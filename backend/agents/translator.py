"""Translation Agent — Claude Sonnet 기반 번역 + 품질 검증 + 용어 사전 관리"""

import json
from backend.agents.base import run_agent_loop
from backend.tools.db_tools import get_selected_articles, update_article_translation
from backend.tools.glossary_tools import get_glossary, update_glossary
from backend.config import SONNET_MODEL


TRANSLATOR_TOOLS = [
    {
        "name": "get_glossary",
        "description": "기존 기술 용어 사전을 조회합니다. {영어: 한국어} 형태로 반환됩니다.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "save_translation",
        "description": "번역 결과를 DB에 저장합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "article_id": {"type": "string"},
                "title_ko": {"type": "string", "description": "번역된 제목"},
                "body_ko": {"type": "string", "description": "번역된 본문"},
                "insights": {
                    "type": "object",
                    "description": "인사이트 JSON",
                    "properties": {
                        "summary": {"type": "string", "description": "핵심 요약 2~3문장"},
                        "partnership_relevance": {"type": "string", "description": "파트너십 관련성"},
                        "competitor_impact": {"type": "string", "description": "경쟁사 영향"},
                        "market_signal": {"type": "string", "description": "시장 시그널"},
                        "physical_ai_applicability": {"type": "string", "description": "현실 세계 적용 가능성 (해당 시만)"},
                        "action_item": {"type": "string", "description": "액션 아이템 (해당 시만)"},
                    },
                    "required": ["summary", "partnership_relevance", "market_signal"],
                },
            },
            "required": ["article_id", "title_ko", "body_ko", "insights"],
        },
    },
    {
        "name": "add_glossary_term",
        "description": "새 기술 용어를 용어 사전에 추가합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "term_en": {"type": "string", "description": "영어 원문 용어"},
                "term_ko": {"type": "string", "description": "한국어 번역 (원어 병기 형태, 예: '에이전트형 AI(agentic AI)')"},
            },
            "required": ["term_en", "term_ko"],
        },
    },
]

TRANSLATOR_SYSTEM_PROMPT = """당신은 AI 테크 기사 전문 번역가입니다.

## 임무
영어 기사를 한국어로 번역하고, 각 기사에 대한 인사이트를 생성하세요.

## 번역 규칙
1. 자연스러운 한국어로 의역하세요. 번역투를 피하세요.
2. 기업명·제품명·기술 용어는 원어를 병기하세요.
   예: "GPT-5 모델 가중치(model weights)"
3. 먼저 get_glossary로 기존 용어 사전을 확인하고, 일관된 번역을 유지하세요.
4. 새로운 기술 용어를 발견하면 add_glossary_term으로 사전에 추가하세요.

## 품질 검증
번역 후 스스로 검증하세요:
- 핵심 수치/날짜가 원문과 일치하는가?
- 고유명사가 정확한가?
- 문장 누락이 없는가?
- 자연스러운 한국어인가?

## 인사이트 생성
각 기사에 대해 다음 인사이트를 생성하세요:
- summary: 핵심 요약 2~3문장
- partnership_relevance: AI 테크 파트너십 팀 관점에서의 관련성
- competitor_impact: 경쟁사에 미치는 영향 (해당 시)
- market_signal: 업계 트렌드 방향성
- physical_ai_applicability: 현실 세계 적용 가능성 (Physical AI 기사만)
- action_item: 팀 차원 검토 사항 (해당 시)

모든 인사이트는 한국어로 작성하세요."""


def make_translator_tool_executor(session):
    """번역 에이전트 도구 실행기를 생성한다."""
    translations_saved = []

    async def executor(tool_name: str, tool_input: dict) -> str:
        try:
            if tool_name == "get_glossary":
                glossary = await get_glossary(session)
                return json.dumps(glossary, ensure_ascii=False)

            elif tool_name == "save_translation":
                ok = await update_article_translation(
                    session,
                    article_id=tool_input["article_id"],
                    title_ko=tool_input["title_ko"],
                    body_ko=tool_input["body_ko"],
                    insights=tool_input.get("insights"),
                )
                if ok:
                    translations_saved.append(tool_input["article_id"])
                return json.dumps({"saved": ok, "total_saved": len(translations_saved)})

            elif tool_name == "add_glossary_term":
                term_id = await update_glossary(
                    session,
                    term_en=tool_input["term_en"],
                    term_ko=tool_input["term_ko"],
                )
                return json.dumps({"added": True, "term_id": term_id})

            return json.dumps({"error": f"알 수 없는 도구: {tool_name}"})
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    executor.translations_saved = translations_saved
    return executor


async def run_translation_agent(session, run_id: str | None = None) -> dict:
    """Translation Agent를 실행한다.

    선별된 기사(importance_score >= 3) 중 아직 번역되지 않은 기사를 번역한다.
    """
    # 번역 대상: 선별됨 + 아직 번역 안 됨
    articles = await get_selected_articles(session, min_score=3)
    untranslated = [a for a in articles if not a.get("title_ko")]

    if not untranslated:
        return {"translated": 0, "message": "번역할 기사가 없습니다."}

    # 기사 목록 구성
    articles_text = ""
    for i, a in enumerate(untranslated, 1):
        companies = ", ".join(a.get("company_tags", [])) or "미디어"
        articles_text += f"\n[{i}] ID: {a['id']}\n"
        articles_text += f"    제목: {a['title_en']}\n"
        articles_text += f"    소스: {a['source_name']} | 기업: {companies}\n"
        articles_text += f"    본문: {a.get('body_en', '')[:500]}\n"

    user_prompt = f"""다음 {len(untranslated)}개 기사를 번역하고 인사이트를 생성해주세요.

먼저 get_glossary를 호출하여 기존 용어 사전을 확인하세요.
그 후 각 기사를 번역하고 save_translation으로 저장하세요.
새 기술 용어를 발견하면 add_glossary_term으로 사전에 추가하세요.

{articles_text}"""

    executor = make_translator_tool_executor(session)

    result = await run_agent_loop(
        system_prompt=TRANSLATOR_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        tools=TRANSLATOR_TOOLS,
        tool_executor=executor,
        model=SONNET_MODEL,
        max_turns=40,
    )

    result["translated"] = len(executor.translations_saved)
    return result
