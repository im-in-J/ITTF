"""DB 도구 — 기사 CRUD, 중복 체크, 통계 조회"""

import json
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models import (
    Article, PipelineRun, AgentLog, SourceStat, ApiUsage, Scrapbook, gen_id,
)


async def detect_duplicate(session: AsyncSession, url: str) -> bool:
    """URL 기반으로 중복 기사인지 확인한다."""
    result = await session.execute(
        select(Article.id).where(Article.url == url).limit(1)
    )
    return result.scalar_one_or_none() is not None


async def save_raw_article(
    session: AsyncSession,
    title: str,
    url: str,
    summary: str,
    source_name: str,
    source_type: str,
    company: str | None = None,
    published_at: datetime | None = None,
) -> str | None:
    """원문 기사를 DB에 저장한다. 중복이면 None 반환."""
    if await detect_duplicate(session, url):
        return None

    article_id = gen_id()
    expires_at = datetime.now(timezone.utc) + timedelta(days=90)
    company_tags = json.dumps([company]) if company else None

    article = Article(
        id=article_id,
        title_en=title,
        body_en=summary,
        url=url,
        source_name=source_name,
        source_type=source_type,
        company_tags=company_tags,
        published_at=published_at,
        expires_at=expires_at,
    )
    session.add(article)
    await session.commit()
    return article_id


async def get_raw_articles(session: AsyncSession, run_id: str | None = None) -> list[dict]:
    """번역되지 않은 기사 목록을 가져온다."""
    stmt = select(Article).where(Article.importance_score.is_(None))
    if run_id:
        # run_id에 해당하는 시간 범위의 기사만
        run = await session.get(PipelineRun, run_id)
        if run:
            stmt = stmt.where(Article.crawled_at >= run.triggered_at)
    result = await session.execute(stmt)
    articles = result.scalars().all()
    return [
        {
            "id": a.id,
            "title": a.title_en,
            "summary": (a.body_en or "")[:500],
            "url": a.url,
            "source_name": a.source_name,
            "source_type": a.source_type,
            "company_tags": json.loads(a.company_tags) if a.company_tags else [],
            "published_at": a.published_at.isoformat() if a.published_at else None,
            "crawled_at": a.crawled_at.isoformat() if a.crawled_at else None,
        }
        for a in articles
    ]


async def update_article_evaluation(
    session: AsyncSession,
    article_id: str,
    importance_score: int,
    evaluation_reason: str,
    category_tags: list[str] | None = None,
) -> bool:
    """기사의 평가 결과를 업데이트한다."""
    article = await session.get(Article, article_id)
    if not article:
        return False
    article.importance_score = importance_score
    article.evaluation_reason = evaluation_reason
    if category_tags:
        article.category_tags = json.dumps(category_tags)
    await session.commit()
    return True


async def update_article_translation(
    session: AsyncSession,
    article_id: str,
    title_ko: str,
    body_ko: str,
    insights: dict | None = None,
) -> bool:
    """기사의 번역 결과를 업데이트한다."""
    article = await session.get(Article, article_id)
    if not article:
        return False
    article.title_ko = title_ko
    article.body_ko = body_ko
    if insights:
        article.insights = json.dumps(insights, ensure_ascii=False)
    await session.commit()
    return True


async def get_selected_articles(session: AsyncSession, min_score: int = 1) -> list[dict]:
    """선별된 기사(importance_score가 있는) 목록을 가져온다."""
    stmt = (
        select(Article)
        .where(Article.importance_score >= min_score)
        .order_by(Article.importance_score.desc())
    )
    result = await session.execute(stmt)
    articles = result.scalars().all()
    return [
        {
            "id": a.id,
            "title_en": a.title_en,
            "title_ko": a.title_ko,
            "body_en": a.body_en,
            "url": a.url,
            "source_name": a.source_name,
            "company_tags": json.loads(a.company_tags) if a.company_tags else [],
            "importance_score": a.importance_score,
            "evaluation_reason": a.evaluation_reason,
        }
        for a in articles
    ]


async def get_historical_ratings(session: AsyncSession, weeks: int = 4) -> dict:
    """과거 N주간 팀원 반응 통계 (스크랩 수, 댓글 수)."""
    since = datetime.now(timezone.utc) - timedelta(weeks=weeks)
    # 스크랩이 많은 기사의 company_tags, category_tags 패턴
    stmt = (
        select(
            Article.company_tags,
            Article.category_tags,
            func.count(Scrapbook.id).label("scrap_count"),
        )
        .join(Scrapbook, Scrapbook.article_id == Article.id)
        .where(Scrapbook.created_at >= since)
        .group_by(Article.company_tags, Article.category_tags)
        .order_by(func.count(Scrapbook.id).desc())
        .limit(20)
    )
    result = await session.execute(stmt)
    rows = result.all()
    return {
        "popular_patterns": [
            {
                "company_tags": json.loads(r.company_tags) if r.company_tags else [],
                "category_tags": json.loads(r.category_tags) if r.category_tags else [],
                "scrap_count": r.scrap_count,
            }
            for r in rows
        ],
    }


# === 파이프라인 로그 ===

async def create_pipeline_run(session: AsyncSession, trigger_type: str = "manual") -> str:
    """새 파이프라인 실행 기록을 생성한다."""
    run = PipelineRun(id=gen_id(), trigger_type=trigger_type)
    session.add(run)
    await session.commit()
    return run.id


async def update_pipeline_run(session: AsyncSession, run_id: str, **kwargs) -> None:
    """파이프라인 실행 기록을 업데이트한다."""
    run = await session.get(PipelineRun, run_id)
    if run:
        for key, value in kwargs.items():
            if hasattr(run, key):
                setattr(run, key, value)
        await session.commit()


async def create_agent_log(
    session: AsyncSession,
    run_id: str,
    agent_name: str,
    model_used: str | None = None,
) -> str:
    """에이전트 실행 로그를 생성한다."""
    log = AgentLog(id=gen_id(), run_id=run_id, agent_name=agent_name, model_used=model_used)
    session.add(log)
    await session.commit()
    return log.id


async def update_agent_log(session: AsyncSession, log_id: str, **kwargs) -> None:
    """에이전트 로그를 업데이트한다."""
    log = await session.get(AgentLog, log_id)
    if log:
        for key, value in kwargs.items():
            if hasattr(log, key):
                setattr(log, key, value)
        await session.commit()


async def save_source_stat(
    session: AsyncSession,
    source_name: str,
    run_id: str,
    strategy_used: str,
    success: bool,
    articles_found: int,
    elapsed_seconds: float | None = None,
    error_detail: str | None = None,
) -> None:
    """소스별 크롤링 통계를 저장한다."""
    stat = SourceStat(
        id=gen_id(),
        source_name=source_name,
        run_id=run_id,
        strategy_used=strategy_used,
        success=success,
        articles_found=articles_found,
        elapsed_seconds=elapsed_seconds,
        error_detail=error_detail,
    )
    session.add(stat)
    await session.commit()


async def save_api_usage(
    session: AsyncSession,
    run_id: str | None,
    agent_name: str,
    model: str,
    tokens_input: int,
    tokens_output: int,
    cost_usd: float,
) -> None:
    """API 사용량을 기록한다."""
    usage = ApiUsage(
        id=gen_id(),
        run_id=run_id,
        agent_name=agent_name,
        model=model,
        tokens_input=tokens_input,
        tokens_output=tokens_output,
        cost_usd=cost_usd,
    )
    session.add(usage)
    await session.commit()
