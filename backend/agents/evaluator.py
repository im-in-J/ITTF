"""Evaluation Agent — 3단계 선별 (규칙 기반 → AI 추론 → 팀 선호도)"""

import json
from datetime import datetime, timezone, timedelta
from backend.agents.base import run_agent_loop
from backend.tools.db_tools import (
    get_raw_articles, update_article_evaluation, get_historical_ratings,
)
from backend.config import (
    KEYWORDS, COMPANIES, CRAWL_SOURCES, MAX_ARTICLES_PER_RUN,
    RULE_BASED_TOP_N, SONNET_MODEL,
)


# === 1단계: 규칙 기반 점수화 (AI 없이 즉시) ===

def calculate_rule_score(article: dict) -> dict:
    """규칙 기반으로 기사 점수를 계산한다.

    점수 항목:
    - 출처 점수 (최대 3점)
    - 키워드 점수 (중복 합산)
    - 기업 관련성 점수 (최대 2점)
    - 최신성 점수 (최대 2점)
    """
    score = 0
    breakdown = {}

    title = (article.get("title") or "").lower()
    summary = (article.get("summary") or "").lower()
    text = f"{title} {summary}"

    # A. 출처 점수
    source_name = article.get("source_name", "")
    source_score = 0
    for src in CRAWL_SOURCES:
        if src["name"] == source_name:
            source_score = src["source_score"]
            break
    score += source_score
    breakdown["source"] = source_score

    # B. 키워드 점수
    keyword_score = 0
    matched_keywords = []
    for level, config in KEYWORDS.items():
        for kw in config["keywords"]:
            if kw.lower() in text:
                keyword_score += config["score"]
                matched_keywords.append(f"{kw}(+{config['score']})")
    score += keyword_score
    breakdown["keywords"] = keyword_score
    breakdown["matched_keywords"] = matched_keywords

    # C. 기업 관련성 점수
    company_tags = article.get("company_tags", [])
    company_score = 0
    for company in company_tags:
        if company in COMPANIES:
            company_score = max(company_score, COMPANIES[company]["weight"])
    score += company_score
    breakdown["company"] = company_score

    # D. 최신성 점수
    recency_score = 0
    published = article.get("published_at")
    if published:
        try:
            if isinstance(published, str):
                pub_dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
            else:
                pub_dt = published
            now = datetime.now(timezone.utc)
            hours_ago = (now - pub_dt).total_seconds() / 3600
            if hours_ago <= 24:
                recency_score = 2
            elif hours_ago <= 48:
                recency_score = 1
        except (ValueError, TypeError):
            pass
    score += recency_score
    breakdown["recency"] = recency_score

    return {
        **article,
        "rule_score": score,
        "score_breakdown": breakdown,
    }


def run_rule_based_filter(articles: list[dict], top_n: int = RULE_BASED_TOP_N) -> list[dict]:
    """1단계: 규칙 기반 점수화 → 상위 N개 추림."""
    scored = [calculate_rule_score(a) for a in articles]
    scored.sort(key=lambda x: x["rule_score"], reverse=True)
    return scored[:top_n]


# === 2단계: Claude AI 중요도 추론 ===

EVAL_TOOLS = [
    {
        "name": "score_articles",
        "description": "기사들의 중요도 평가 결과를 저장합니다. 각 기사에 1~5점 중요도와 선정 사유를 부여하세요.",
        "input_schema": {
            "type": "object",
            "properties": {
                "evaluations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "article_id": {"type": "string"},
                            "importance_score": {"type": "integer", "minimum": 1, "maximum": 5},
                            "reason": {"type": "string", "description": "선정/탈락 사유 (한국어)"},
                            "categories": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "카테고리 태그 (예: AI Model, Physical AI, Partnership 등)",
                            },
                        },
                        "required": ["article_id", "importance_score", "reason"],
                    },
                },
            },
            "required": ["evaluations"],
        },
    },
    {
        "name": "get_team_history",
        "description": "최근 4주간 팀원들의 스크랩/댓글 패턴을 조회합니다.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
]

EVAL_SYSTEM_PROMPT = """당신은 AI 테크 기업 파트너십 팀의 기사 심사위원입니다.

## 임무
주어진 기사들을 분석하여 팀에게 가장 가치 있는 기사를 선별하세요.

## 평가 기준
- **5점**: 제품 런칭, M&A, 대형 발표, 주요 규제 변화. 파트너십 업무에 직접 영향.
- **4점**: 기능 업데이트, 투자 유치, CEO 발언, 전략 변화.
- **3점**: 기술 블로그, 업계 리포트, 연구 결과.
- **2점**: 일반 뉴스, 간접적 관련.
- **1점**: 관련성 낮음.

## 관점
- AI 테크 기업 파트너십 팀: OpenAI, Anthropic, Google, Microsoft, Nvidia에 특히 주목
- 파트너십 계약, API 가격, 경쟁 구도 변화에 민감
- Physical AI/로보틱스 분야도 관심 대상

## 출력
score_articles 도구를 호출하여 모든 기사의 평가 결과를 저장하세요.
선정 사유는 반드시 한국어로 작성하세요."""


async def run_ai_evaluation(session, articles: list[dict]) -> dict:
    """2~3단계: Claude AI 중요도 평가 + 팀 선호도 반영."""
    evaluations_result = {"evaluations": []}

    async def tool_executor(tool_name: str, tool_input: dict) -> str:
        if tool_name == "score_articles":
            evaluations_result["evaluations"] = tool_input["evaluations"]
            # DB에 저장
            for ev in tool_input["evaluations"]:
                await update_article_evaluation(
                    session,
                    article_id=ev["article_id"],
                    importance_score=ev["importance_score"],
                    evaluation_reason=ev["reason"],
                    category_tags=ev.get("categories"),
                )
            return json.dumps({"saved": len(tool_input["evaluations"])})
        elif tool_name == "get_team_history":
            history = await get_historical_ratings(session)
            return json.dumps(history, ensure_ascii=False)
        return json.dumps({"error": "unknown tool"})

    # 기사 목록 텍스트 구성
    articles_text = ""
    for i, a in enumerate(articles, 1):
        companies = ", ".join(a.get("company_tags", [])) or "미디어"
        articles_text += f"\n[{i}] ID: {a['id']}\n"
        articles_text += f"    제목: {a['title']}\n"
        articles_text += f"    소스: {a['source_name']} | 기업: {companies}\n"
        articles_text += f"    요약: {a['summary'][:200]}\n"
        articles_text += f"    규칙점수: {a.get('rule_score', 'N/A')}\n"

    user_prompt = f"""다음 {len(articles)}개 기사를 평가해주세요.
먼저 get_team_history를 호출하여 팀 선호도를 확인한 후, 각 기사에 1~5점 중요도를 부여하세요.

{articles_text}

score_articles 도구로 모든 기사의 평가 결과를 한번에 저장해주세요."""

    result = await run_agent_loop(
        system_prompt=EVAL_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        tools=EVAL_TOOLS,
        tool_executor=tool_executor,
        model=SONNET_MODEL,
        max_turns=5,
    )

    result["evaluations"] = evaluations_result["evaluations"]
    return result


# === 규칙 기반 평가 (AI 없이) ===

async def run_rule_based_evaluation(session, articles: list[dict]) -> list[dict]:
    """AI 없이 규칙 기반으로만 평가하고 DB에 저장한다. (API 크레딧 없을 때 대체용)"""
    scored = run_rule_based_filter(articles, top_n=MAX_ARTICLES_PER_RUN)

    for a in scored:
        # 규칙 점수를 1~5 스케일로 변환
        rule_score = a["rule_score"]
        if rule_score >= 8:
            importance = 5
        elif rule_score >= 6:
            importance = 4
        elif rule_score >= 4:
            importance = 3
        elif rule_score >= 2:
            importance = 2
        else:
            importance = 1

        keywords = ", ".join(a["score_breakdown"].get("matched_keywords", []))
        reason = f"규칙 기반 평가 (점수 {rule_score}): {keywords}" if keywords else f"규칙 기반 평가 (점수 {rule_score})"

        await update_article_evaluation(
            session,
            article_id=a["id"],
            importance_score=importance,
            evaluation_reason=reason,
        )
        a["importance_score"] = importance
        a["evaluation_reason"] = reason

    return scored


# === 통합 실행 ===

async def run_evaluation_agent(session, run_id: str | None = None, use_ai: bool = True) -> dict:
    """Evaluation Agent 실행.

    Args:
        session: DB 세션
        run_id: 파이프라인 실행 ID
        use_ai: True면 Claude AI 평가, False면 규칙 기반만
    """
    # 1단계: 미평가 기사 로드
    raw_articles = await get_raw_articles(session, run_id)
    if not raw_articles:
        return {"selected": [], "total_evaluated": 0, "message": "평가할 기사가 없습니다."}

    # 규칙 기반 필터링
    top_articles = run_rule_based_filter(raw_articles, top_n=RULE_BASED_TOP_N)

    if use_ai:
        # 2~3단계: AI 평가
        result = await run_ai_evaluation(session, top_articles)
        selected = [
            e for e in result.get("evaluations", [])
            if e["importance_score"] >= 3
        ][:MAX_ARTICLES_PER_RUN]
        return {
            "selected": selected,
            "total_evaluated": len(top_articles),
            "tokens_input": result.get("tokens_input", 0),
            "tokens_output": result.get("tokens_output", 0),
        }
    else:
        # 규칙 기반만
        selected = await run_rule_based_evaluation(session, top_articles)
        return {
            "selected": [
                {"article_id": a["id"], "importance_score": a["importance_score"], "reason": a["evaluation_reason"]}
                for a in selected
            ],
            "total_evaluated": len(raw_articles),
            "tokens_input": 0,
            "tokens_output": 0,
        }
