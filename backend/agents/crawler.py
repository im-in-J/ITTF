"""Crawling Agent — Claude Sonnet + Tool Use 기반 적응적 크롤링"""

import json
import time
from backend.agents.base import run_agent_loop
from backend.tools.web_tools import fetch_url, parse_html, parse_rss
from backend.tools.db_tools import (
    save_raw_article, detect_duplicate, save_source_stat,
)
from backend.config import CRAWL_SOURCES, EXCLUDE_KEYWORDS, SONNET_MODEL

# === Claude에게 부여할 도구 정의 ===

CRAWLER_TOOLS = [
    {
        "name": "fetch_url",
        "description": "URL에서 HTML 콘텐츠를 가져옵니다. 성공 시 HTML 문자열, 실패 시 에러 메시지를 반환합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "가져올 URL"},
            },
            "required": ["url"],
        },
    },
    {
        "name": "parse_html",
        "description": "HTML에서 기사 목록을 파싱합니다. 각 기사의 title, url, summary를 추출합니다. container 셀렉터를 지정하면 해당 요소 내에서만 추출합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "html": {"type": "string", "description": "파싱할 HTML 문자열"},
                "container_selector": {"type": "string", "description": "(선택) 기사를 감싸는 컨테이너의 CSS 셀렉터"},
                "title_selector": {"type": "string", "description": "(선택) 제목 요소의 CSS 셀렉터"},
                "link_selector": {"type": "string", "description": "(선택) 링크 요소의 CSS 셀렉터"},
                "summary_selector": {"type": "string", "description": "(선택) 요약 요소의 CSS 셀렉터"},
            },
            "required": ["html"],
        },
    },
    {
        "name": "parse_rss",
        "description": "RSS/Atom XML을 파싱하여 기사 목록을 반환합니다. 각 기사의 title, url, summary, published를 추출합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "xml_text": {"type": "string", "description": "RSS/Atom XML 문자열"},
            },
            "required": ["xml_text"],
        },
    },
    {
        "name": "check_duplicate",
        "description": "URL이 이미 DB에 저장된 기사인지 확인합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "확인할 기사 URL"},
            },
            "required": ["url"],
        },
    },
    {
        "name": "save_article",
        "description": "수집한 기사를 DB에 저장합니다. 중복이면 저장하지 않고 null을 반환합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "기사 제목 (영어 원문)"},
                "url": {"type": "string", "description": "기사 URL (전체 경로)"},
                "summary": {"type": "string", "description": "기사 요약 또는 첫 단락"},
                "source_name": {"type": "string", "description": "소스 이름 (예: openai_news)"},
                "source_type": {"type": "string", "description": "소스 유형: official_blog 또는 media"},
                "company": {"type": "string", "description": "관련 기업명 (예: OpenAI). 미디어 소스면 빈 문자열."},
            },
            "required": ["title", "url", "summary", "source_name", "source_type"],
        },
    },
    {
        "name": "report_source_result",
        "description": "소스 하나의 크롤링 결과를 보고합니다. 모든 소스 처리 후 반드시 호출하세요.",
        "input_schema": {
            "type": "object",
            "properties": {
                "source_name": {"type": "string"},
                "strategy_used": {"type": "string", "description": "사용한 전략: html_parse, rss, 또는 둘 다"},
                "success": {"type": "boolean"},
                "articles_found": {"type": "integer"},
                "error_detail": {"type": "string", "description": "실패 시 에러 내용"},
            },
            "required": ["source_name", "strategy_used", "success", "articles_found"],
        },
    },
]


# === 도구 실행기 ===

# 세션과 run_id를 클로저로 캡처
def make_tool_executor(session, run_id: str):
    source_stats = []

    async def executor(tool_name: str, tool_input: dict) -> str:
        try:
            if tool_name == "fetch_url":
                result = await fetch_url(tool_input["url"])
                if result["success"]:
                    # HTML이 너무 길면 앞부분만 전달 (토큰 절약)
                    html = result["html"]
                    if len(html) > 50000:
                        html = html[:50000] + "\n... (HTML 50000자로 잘림)"
                    return json.dumps({"success": True, "status_code": result["status_code"], "html": html}, ensure_ascii=False)
                else:
                    return json.dumps({"success": False, "error": result["error"]}, ensure_ascii=False)

            elif tool_name == "parse_html":
                selectors = {}
                if tool_input.get("container_selector"):
                    selectors["container"] = tool_input["container_selector"]
                if tool_input.get("title_selector"):
                    selectors["title"] = tool_input["title_selector"]
                if tool_input.get("link_selector"):
                    selectors["link"] = tool_input["link_selector"]
                if tool_input.get("summary_selector"):
                    selectors["summary"] = tool_input["summary_selector"]
                articles = parse_html(tool_input["html"], selectors or None)
                return json.dumps({"articles": articles[:30], "total": len(articles)}, ensure_ascii=False)

            elif tool_name == "parse_rss":
                articles = parse_rss(tool_input["xml_text"])
                return json.dumps({"articles": articles[:30], "total": len(articles)}, ensure_ascii=False)

            elif tool_name == "check_duplicate":
                is_dup = await detect_duplicate(session, tool_input["url"])
                return json.dumps({"is_duplicate": is_dup})

            elif tool_name == "save_article":
                article_id = await save_raw_article(
                    session,
                    title=tool_input["title"],
                    url=tool_input["url"],
                    summary=tool_input.get("summary", ""),
                    source_name=tool_input["source_name"],
                    source_type=tool_input["source_type"],
                    company=tool_input.get("company") or None,
                )
                if article_id:
                    return json.dumps({"saved": True, "article_id": article_id})
                else:
                    return json.dumps({"saved": False, "reason": "duplicate"})

            elif tool_name == "report_source_result":
                stat = tool_input
                source_stats.append(stat)
                await save_source_stat(
                    session,
                    source_name=stat["source_name"],
                    run_id=run_id,
                    strategy_used=stat["strategy_used"],
                    success=stat["success"],
                    articles_found=stat["articles_found"],
                    error_detail=stat.get("error_detail"),
                )
                return json.dumps({"recorded": True})

            else:
                return json.dumps({"error": f"알 수 없는 도구: {tool_name}"})

        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    executor.source_stats = source_stats
    return executor


# === Crawling Agent 실행 ===

SYSTEM_PROMPT = """당신은 빅테크 AI 블로그 크롤링 전문 에이전트입니다.

## 임무
주어진 소스 목록에서 AI 관련 기사를 수집하세요.

## 수집 규칙
1. 각 소스 URL에서 기사를 수집합니다.
2. 먼저 fetch_url로 페이지를 가져온 후, HTML 구조를 분석하여 적절한 셀렉터로 parse_html을 호출하세요.
3. HTML 파싱이 잘 안 되면 RSS 피드를 시도하세요 (URL 뒤에 /feed/, /rss/, /atom.xml 등 시도).
4. 기사 URL이 상대경로이면 소스 도메인을 붙여 절대경로로 변환하세요.
5. 각 기사마다 save_article로 DB에 저장하세요.
6. 각 소스 처리 완료 후 report_source_result로 결과를 보고하세요.

## 제외 기준
다음 키워드가 제목에 포함된 기사는 저장하지 마세요: """ + ", ".join(EXCLUDE_KEYWORDS) + """

## 중요
- 가능한 한 많은 기사를 수집하되, AI/ML/기술 관련 기사만 수집하세요.
- 소스 하나가 실패해도 다른 소스는 계속 진행하세요.
- 모든 소스를 처리한 후, 전체 수집 결과를 텍스트로 요약해주세요.
"""


async def run_crawling_agent(session, run_id: str, sources: list[dict] | None = None) -> dict:
    """Crawling Agent를 실행한다.

    Args:
        session: DB 세션
        run_id: 파이프라인 실행 ID
        sources: 크롤링할 소스 목록 (None이면 전체)

    Returns:
        {"result": str, "tokens_input": int, "tokens_output": int, "turns": int, "source_stats": list}
    """
    if sources is None:
        sources = CRAWL_SOURCES

    source_list = "\n".join([
        f"- {s['name']}: {', '.join(s['urls'])} (기업: {s.get('company', '미디어')}, 유형: {s['source_type']})"
        for s in sources
    ])

    user_prompt = f"""다음 소스들에서 AI 관련 기사를 수집해주세요:

{source_list}

각 소스에서 기사를 수집하고 DB에 저장한 후, 소스별 결과를 report_source_result로 보고해주세요.
모든 소스를 처리한 후 전체 결과를 요약해주세요."""

    executor = make_tool_executor(session, run_id)

    result = await run_agent_loop(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        tools=CRAWLER_TOOLS,
        tool_executor=executor,
        model=SONNET_MODEL,
        max_turns=50,  # 크롤링은 턴이 많을 수 있음
    )

    result["source_stats"] = executor.source_stats
    return result
