"""Orchestrator Agent — 전체 파이프라인 조율, 에러 복구, 상태 관리"""

import time
import json
from datetime import datetime, timezone
from backend.database.connection import async_session
from backend.tools.db_tools import (
    create_pipeline_run, update_pipeline_run,
    create_agent_log, update_agent_log, save_api_usage,
)
from backend.agents.crawler import run_crawling_agent
from backend.agents.evaluator import run_evaluation_agent
from backend.agents.translator import run_translation_agent
from backend.config import CRAWL_SOURCES, SONNET_MODEL, HAIKU_MODEL


async def run_pipeline(trigger_type: str = "manual", use_ai: bool = True) -> dict:
    """전체 에이전트 파이프라인을 실행한다.

    실행 순서: Crawling → Evaluation → Translation
    (Insight, Newsletter는 Phase 2에서 추가)

    Args:
        trigger_type: "manual" 또는 "scheduled"
        use_ai: True면 Claude API 사용, False면 규칙 기반 + 직접 크롤링

    Returns:
        파이프라인 실행 결과 요약
    """
    pipeline_start = time.time()
    total_tokens_in = 0
    total_tokens_out = 0
    errors = []
    results = {}

    async with async_session() as session:
        # 파이프라인 실행 기록 생성
        run_id = await create_pipeline_run(session, trigger_type)
        print(f"[Orchestrator] 파이프라인 시작 (ID: {run_id[:8]}...)")
        print(f"[Orchestrator] AI 모드: {'Claude API' if use_ai else '규칙 기반'}")
        print("=" * 60)

        # ── 1. Crawling Agent ──
        print("\n[1/3] Crawling Agent 실행 중...")
        crawl_log_id = await create_agent_log(session, run_id, "crawling", SONNET_MODEL if use_ai else None)
        crawl_start = time.time()

        try:
            if use_ai:
                crawl_result = await run_crawling_agent(session, run_id)
            else:
                crawl_result = await _run_direct_crawling(session, run_id)

            crawl_elapsed = time.time() - crawl_start
            crawl_tokens_in = crawl_result.get("tokens_input", 0)
            crawl_tokens_out = crawl_result.get("tokens_output", 0)
            total_tokens_in += crawl_tokens_in
            total_tokens_out += crawl_tokens_out

            # 수집된 기사 수 계산
            source_stats = crawl_result.get("source_stats", [])
            total_crawled = sum(s.get("articles_found", 0) for s in source_stats)
            failed_sources = [s["source_name"] for s in source_stats if not s.get("success", True)]

            await update_agent_log(session, crawl_log_id,
                status="completed",
                completed_at=datetime.now(timezone.utc),
                output_count=total_crawled,
                tokens_input=crawl_tokens_in,
                tokens_output=crawl_tokens_out,
            )
            await update_pipeline_run(session, run_id, total_crawled=total_crawled)

            print(f"  ✅ 수집 완료: {total_crawled}개 기사 ({crawl_elapsed:.1f}초)")
            if failed_sources:
                print(f"  ⚠️  실패 소스: {', '.join(failed_sources)}")

            results["crawling"] = {
                "total_crawled": total_crawled,
                "failed_sources": failed_sources,
                "elapsed": crawl_elapsed,
            }

            # 판단: 수집 수가 너무 적으면 경고
            if total_crawled < 10:
                msg = f"수집 기사가 {total_crawled}개로 매우 적습니다."
                errors.append(msg)
                print(f"  ⚠️  {msg}")

        except Exception as e:
            crawl_elapsed = time.time() - crawl_start
            error_msg = f"Crawling Agent 실패: {str(e)}"
            errors.append(error_msg)
            await update_agent_log(session, crawl_log_id,
                status="failed", error_detail=str(e),
                completed_at=datetime.now(timezone.utc),
            )
            print(f"  ❌ {error_msg}")
            results["crawling"] = {"error": str(e)}

        # ── 2. Evaluation Agent ──
        print("\n[2/3] Evaluation Agent 실행 중...")
        eval_log_id = await create_agent_log(session, run_id, "evaluation", SONNET_MODEL if use_ai else None)
        eval_start = time.time()

        try:
            eval_result = await run_evaluation_agent(session, run_id, use_ai=use_ai)
            eval_elapsed = time.time() - eval_start
            eval_tokens_in = eval_result.get("tokens_input", 0)
            eval_tokens_out = eval_result.get("tokens_output", 0)
            total_tokens_in += eval_tokens_in
            total_tokens_out += eval_tokens_out

            total_selected = len(eval_result.get("selected", []))

            await update_agent_log(session, eval_log_id,
                status="completed",
                completed_at=datetime.now(timezone.utc),
                input_count=eval_result.get("total_evaluated", 0),
                output_count=total_selected,
                tokens_input=eval_tokens_in,
                tokens_output=eval_tokens_out,
            )
            await update_pipeline_run(session, run_id, total_selected=total_selected)

            print(f"  ✅ 선별 완료: {eval_result.get('total_evaluated', 0)}개 → {total_selected}개 ({eval_elapsed:.1f}초)")

            results["evaluation"] = {
                "total_evaluated": eval_result.get("total_evaluated", 0),
                "total_selected": total_selected,
                "elapsed": eval_elapsed,
            }

        except Exception as e:
            eval_elapsed = time.time() - eval_start
            error_msg = f"Evaluation Agent 실패: {str(e)}"
            errors.append(error_msg)
            await update_agent_log(session, eval_log_id,
                status="failed", error_detail=str(e),
                completed_at=datetime.now(timezone.utc),
            )
            print(f"  ❌ {error_msg}")
            results["evaluation"] = {"error": str(e)}

        # ── 3. Translation Agent ──
        print("\n[3/3] Translation Agent 실행 중...")
        trans_log_id = await create_agent_log(session, run_id, "translation", SONNET_MODEL if use_ai else None)
        trans_start = time.time()

        try:
            if use_ai:
                trans_result = await run_translation_agent(session, run_id)
            else:
                trans_result = {"translated": 0, "message": "AI 모드 비활성 — 번역 건너뜀", "tokens_input": 0, "tokens_output": 0}

            trans_elapsed = time.time() - trans_start
            trans_tokens_in = trans_result.get("tokens_input", 0)
            trans_tokens_out = trans_result.get("tokens_output", 0)
            total_tokens_in += trans_tokens_in
            total_tokens_out += trans_tokens_out

            total_translated = trans_result.get("translated", 0)

            await update_agent_log(session, trans_log_id,
                status="completed",
                completed_at=datetime.now(timezone.utc),
                output_count=total_translated,
                tokens_input=trans_tokens_in,
                tokens_output=trans_tokens_out,
            )
            await update_pipeline_run(session, run_id, total_translated=total_translated)

            print(f"  ✅ 번역 완료: {total_translated}개 ({trans_elapsed:.1f}초)")
            if trans_result.get("message"):
                print(f"     {trans_result['message']}")

            results["translation"] = {
                "total_translated": total_translated,
                "elapsed": trans_elapsed,
            }

        except Exception as e:
            trans_elapsed = time.time() - trans_start
            error_msg = f"Translation Agent 실패: {str(e)}"
            errors.append(error_msg)
            await update_agent_log(session, trans_log_id,
                status="failed", error_detail=str(e),
                completed_at=datetime.now(timezone.utc),
            )
            print(f"  ❌ {error_msg}")
            results["translation"] = {"error": str(e)}

        # ── 파이프라인 완료 ──
        pipeline_elapsed = time.time() - pipeline_start
        pipeline_status = "failed" if errors else "completed"

        # 비용 계산 (Sonnet 기준)
        cost_input = total_tokens_in / 1_000_000 * 3    # $3/MTok
        cost_output = total_tokens_out / 1_000_000 * 15  # $15/MTok
        total_cost = cost_input + cost_output

        await update_pipeline_run(session, run_id,
            status=pipeline_status,
            completed_at=datetime.now(timezone.utc),
            elapsed_seconds=pipeline_elapsed,
            api_tokens_input=total_tokens_in,
            api_tokens_output=total_tokens_out,
            api_cost_usd=total_cost,
            errors=json.dumps(errors, ensure_ascii=False) if errors else None,
        )

        if total_tokens_in > 0 or total_tokens_out > 0:
            await save_api_usage(session, run_id, "pipeline_total", SONNET_MODEL,
                total_tokens_in, total_tokens_out, total_cost)

        print("\n" + "=" * 60)
        print(f"[Orchestrator] 파이프라인 {'완료' if not errors else '완료 (에러 있음)'}")
        print(f"  소요 시간: {pipeline_elapsed:.1f}초")
        print(f"  API 토큰: 입력 {total_tokens_in:,} / 출력 {total_tokens_out:,}")
        print(f"  예상 비용: ${total_cost:.4f}")
        if errors:
            print(f"  에러: {len(errors)}건")
            for e in errors:
                print(f"    - {e}")

        return {
            "run_id": run_id,
            "status": pipeline_status,
            "elapsed_seconds": pipeline_elapsed,
            "total_crawled": results.get("crawling", {}).get("total_crawled", 0),
            "total_selected": results.get("evaluation", {}).get("total_selected", 0),
            "total_translated": results.get("translation", {}).get("total_translated", 0),
            "tokens_input": total_tokens_in,
            "tokens_output": total_tokens_out,
            "cost_usd": total_cost,
            "errors": errors,
            "details": results,
        }


async def _run_direct_crawling(session, run_id: str) -> dict:
    """AI 없이 직접 크롤링 (도구만 사용)."""
    from backend.tools.web_tools import fetch_url, parse_html, parse_rss
    from backend.tools.db_tools import save_raw_article, save_source_stat
    from bs4 import BeautifulSoup

    source_stats = []

    for source in CRAWL_SOURCES:
        name = source["name"]
        count = 0
        strategy = "html_parse"

        for url in source["urls"]:
            # RSS 시도
            for rss_suffix in ["/feed/", "/rss/", "/atom.xml", "/feed"]:
                rss_url = url.rstrip("/") + rss_suffix
                result = await fetch_url(rss_url)
                if result["success"] and ("<?xml" in result["html"][:200].lower() or "<rss" in result["html"][:500].lower() or "<feed" in result["html"][:500].lower()):
                    articles = parse_rss(result["html"])
                    strategy = "rss"
                    for a in articles:
                        if a["url"].startswith("http"):
                            saved = await save_raw_article(
                                session, a["title"], a["url"], a.get("summary", ""),
                                name, source["source_type"], source.get("company"),
                            )
                            if saved:
                                count += 1
                    if articles:
                        break

            # RSS 실패 시 HTML 파싱
            if count == 0:
                strategy = "html_parse"
                result = await fetch_url(url)
                if result["success"]:
                    articles = parse_html(result["html"])
                    if len(articles) < 2:
                        soup = BeautifulSoup(result["html"], "lxml")
                        domain = "/".join(url.split("/")[:3])
                        for a_tag in soup.find_all("a", href=True):
                            href = a_tag["href"]
                            text = a_tag.get_text(strip=True)
                            if 20 < len(text) < 200 and any(p in href for p in ["/blog/", "/news/", "/research/", "/post/"]):
                                if not href.startswith("http"):
                                    href = domain + href
                                articles.append({"title": text, "url": href, "summary": ""})
                        seen = set()
                        articles = [a for a in articles if a["url"] not in seen and not seen.add(a["url"])]

                    for a in articles:
                        if a["url"].startswith("http"):
                            saved = await save_raw_article(
                                session, a["title"], a["url"], a.get("summary", ""),
                                name, source["source_type"], source.get("company"),
                            )
                            if saved:
                                count += 1

        stat = {
            "source_name": name,
            "strategy_used": strategy,
            "success": True,  # 크롤링 시도 자체는 성공 (에러 발생 시 except에서 처리)
            "articles_found": count,
        }
        source_stats.append(stat)
        await save_source_stat(session, name, run_id, strategy, True, count)

    return {
        "source_stats": source_stats,
        "tokens_input": 0,
        "tokens_output": 0,
    }
