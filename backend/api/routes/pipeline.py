"""파이프라인 API — 수동 실행, 상태 조회, 이력"""

import asyncio
import json
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.connection import get_db
from backend.database.models import PipelineRun, AgentLog, SourceStat

router = APIRouter(prefix="/api/admin/pipeline", tags=["파이프라인"])

# 현재 실행 중인 파이프라인 상태
_current_run: dict | None = None


@router.post("/run")
async def trigger_pipeline(
    background_tasks: BackgroundTasks,
    use_ai: bool = False,
):
    """파이프라인 수동 실행 (백그라운드)"""
    global _current_run
    if _current_run and _current_run.get("status") == "running":
        return {"error": "이미 실행 중인 파이프라인이 있습니다.", "run_id": _current_run.get("run_id")}

    _current_run = {"status": "running", "run_id": None}

    async def run_in_background():
        global _current_run
        from backend.agents.orchestrator import run_pipeline
        result = await run_pipeline(trigger_type="manual", use_ai=use_ai)
        _current_run = result

    background_tasks.add_task(run_in_background)
    return {"message": "파이프라인 실행 시작", "use_ai": use_ai}


@router.get("/status")
async def get_pipeline_status():
    """현재 실행 중인 파이프라인 상태"""
    if not _current_run:
        return {"status": "idle", "message": "실행 중인 파이프라인이 없습니다."}
    return _current_run


@router.get("/history")
async def get_pipeline_history(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """최근 파이프라인 실행 이력"""
    stmt = select(PipelineRun).order_by(desc(PipelineRun.triggered_at)).limit(limit)
    result = await db.execute(stmt)
    runs = result.scalars().all()

    return {
        "runs": [
            {
                "id": r.id,
                "triggered_at": r.triggered_at.isoformat() if r.triggered_at else None,
                "trigger_type": r.trigger_type,
                "status": r.status,
                "total_crawled": r.total_crawled,
                "total_selected": r.total_selected,
                "total_translated": r.total_translated,
                "elapsed_seconds": r.elapsed_seconds,
                "api_tokens_input": r.api_tokens_input,
                "api_tokens_output": r.api_tokens_output,
                "api_cost_usd": r.api_cost_usd,
                "errors": json.loads(r.errors) if r.errors else [],
            }
            for r in runs
        ],
    }


@router.get("/runs/{run_id}/agents")
async def get_agent_logs(run_id: str, db: AsyncSession = Depends(get_db)):
    """특정 파이프라인 실행의 에이전트 로그"""
    stmt = select(AgentLog).where(AgentLog.run_id == run_id).order_by(AgentLog.started_at)
    result = await db.execute(stmt)
    logs = result.scalars().all()

    return {
        "run_id": run_id,
        "agents": [
            {
                "agent_name": log.agent_name,
                "model_used": log.model_used,
                "status": log.status,
                "started_at": log.started_at.isoformat() if log.started_at else None,
                "completed_at": log.completed_at.isoformat() if log.completed_at else None,
                "input_count": log.input_count,
                "output_count": log.output_count,
                "retries": log.retries,
                "tokens_input": log.tokens_input,
                "tokens_output": log.tokens_output,
                "error_detail": log.error_detail,
            }
            for log in logs
        ],
    }


@router.get("/runs/{run_id}/sources")
async def get_source_stats(run_id: str, db: AsyncSession = Depends(get_db)):
    """특정 파이프라인 실행의 소스별 크롤링 통계"""
    stmt = select(SourceStat).where(SourceStat.run_id == run_id).order_by(desc(SourceStat.articles_found))
    result = await db.execute(stmt)
    stats = result.scalars().all()

    return {
        "run_id": run_id,
        "sources": [
            {
                "source_name": s.source_name,
                "strategy_used": s.strategy_used,
                "success": s.success,
                "articles_found": s.articles_found,
                "elapsed_seconds": s.elapsed_seconds,
                "error_detail": s.error_detail,
            }
            for s in stats
        ],
    }
