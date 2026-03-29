"""관리자 API — 기사 관리, 용어 사전, API 사용량"""

import json
from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.connection import get_db
from backend.database.models import Article, ApiUsage, Glossary
from backend.tools.glossary_tools import get_glossary_list, update_glossary

router = APIRouter(prefix="/api/admin", tags=["관리자"])


# === 기사 관리 ===

@router.patch("/articles/{article_id}")
async def update_article_score(
    article_id: str,
    importance_score: int = Body(..., ge=1, le=5),
    db: AsyncSession = Depends(get_db),
):
    """기사 중요도 수동 수정"""
    article = await db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="기사를 찾을 수 없습니다.")
    article.importance_score = importance_score
    await db.commit()
    return {"updated": True, "article_id": article_id, "importance_score": importance_score}


@router.delete("/articles/{article_id}")
async def delete_article(article_id: str, db: AsyncSession = Depends(get_db)):
    """기사 삭제"""
    article = await db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="기사를 찾을 수 없습니다.")
    await db.delete(article)
    await db.commit()
    return {"deleted": True, "article_id": article_id}


# === 용어 사전 ===

@router.get("/glossary")
async def list_glossary(db: AsyncSession = Depends(get_db)):
    """용어 사전 목록"""
    entries = await get_glossary_list(db)
    return {"total": len(entries), "glossary": entries}


@router.patch("/glossary/{glossary_id}")
async def update_glossary_term(
    glossary_id: str,
    term_ko: str = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """용어 번역 수정"""
    entry = await db.get(Glossary, glossary_id)
    if not entry:
        raise HTTPException(status_code=404, detail="용어를 찾을 수 없습니다.")
    entry.term_ko = term_ko
    await db.commit()
    return {"updated": True, "term_en": entry.term_en, "term_ko": term_ko}


@router.delete("/glossary/{glossary_id}")
async def delete_glossary_term(glossary_id: str, db: AsyncSession = Depends(get_db)):
    """용어 삭제"""
    entry = await db.get(Glossary, glossary_id)
    if not entry:
        raise HTTPException(status_code=404, detail="용어를 찾을 수 없습니다.")
    await db.delete(entry)
    await db.commit()
    return {"deleted": True, "term_en": entry.term_en}


# === API 사용량 ===

@router.get("/api-usage")
async def get_api_usage(db: AsyncSession = Depends(get_db)):
    """Claude API 사용량 및 비용 요약"""
    # 전체 합산
    stmt = select(
        func.sum(ApiUsage.tokens_input).label("total_input"),
        func.sum(ApiUsage.tokens_output).label("total_output"),
        func.sum(ApiUsage.cost_usd).label("total_cost"),
        func.count(ApiUsage.id).label("total_calls"),
    )
    result = await db.execute(stmt)
    row = result.one()

    # 에이전트별 합산
    agent_stmt = select(
        ApiUsage.agent_name,
        func.sum(ApiUsage.tokens_input).label("tokens_input"),
        func.sum(ApiUsage.tokens_output).label("tokens_output"),
        func.sum(ApiUsage.cost_usd).label("cost_usd"),
    ).group_by(ApiUsage.agent_name)
    agent_result = await db.execute(agent_stmt)

    return {
        "total": {
            "tokens_input": row.total_input or 0,
            "tokens_output": row.total_output or 0,
            "cost_usd": round(row.total_cost or 0, 4),
            "total_calls": row.total_calls or 0,
        },
        "by_agent": [
            {
                "agent_name": r.agent_name,
                "tokens_input": r.tokens_input or 0,
                "tokens_output": r.tokens_output or 0,
                "cost_usd": round(r.cost_usd or 0, 4),
            }
            for r in agent_result.all()
        ],
    }


# === 통계 ===

@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """전체 시스템 통계"""
    total_articles = (await db.execute(select(func.count(Article.id)))).scalar() or 0
    selected_articles = (await db.execute(
        select(func.count(Article.id)).where(Article.importance_score >= 3)
    )).scalar() or 0
    translated_articles = (await db.execute(
        select(func.count(Article.id)).where(Article.title_ko.isnot(None))
    )).scalar() or 0

    # 소스별 기사 수
    source_stats = await db.execute(
        select(Article.source_name, func.count(Article.id))
        .group_by(Article.source_name)
        .order_by(desc(func.count(Article.id)))
    )

    return {
        "total_articles": total_articles,
        "selected_articles": selected_articles,
        "translated_articles": translated_articles,
        "by_source": [
            {"source": name, "count": count}
            for name, count in source_stats.all()
        ],
    }
