"""기사 API — 목록, 상세, 검색"""

import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.connection import get_db
from backend.database.models import Article, Comment, User

router = APIRouter(prefix="/api/articles", tags=["기사"])


@router.get("")
async def list_articles(
    sort: str = Query("latest", description="정렬: latest(최신순) 또는 importance(중요도순)"),
    company: str | None = Query(None, description="기업 필터 (예: OpenAI)"),
    source_type: str | None = Query(None, description="소스 유형: official_blog 또는 media"),
    min_score: int = Query(1, description="최소 중요도"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """기사 목록 조회 (필터·정렬·페이지네이션)"""
    stmt = select(Article).where(Article.importance_score >= min_score)

    if company:
        stmt = stmt.where(Article.company_tags.contains(f'"{company}"'))
    if source_type:
        stmt = stmt.where(Article.source_type == source_type)

    if sort == "importance":
        stmt = stmt.order_by(desc(Article.importance_score), desc(Article.crawled_at))
    else:
        stmt = stmt.order_by(desc(Article.crawled_at))

    # 총 개수
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    # 페이지네이션
    stmt = stmt.offset((page - 1) * size).limit(size)
    result = await db.execute(stmt)
    articles = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "size": size,
        "articles": [_article_to_dict(a) for a in articles],
    }


@router.get("/{article_id}")
async def get_article(article_id: str, db: AsyncSession = Depends(get_db)):
    """기사 상세 조회"""
    article = await db.get(Article, article_id)
    if not article:
        return {"error": "기사를 찾을 수 없습니다."}
    return _article_to_dict(article, include_body=True)


@router.get("/{article_id}/comments")
async def get_comments(article_id: str, db: AsyncSession = Depends(get_db)):
    """기사 댓글 목록"""
    stmt = (
        select(Comment)
        .where(Comment.article_id == article_id, Comment.parent_id.is_(None))
        .order_by(asc(Comment.created_at))
    )
    result = await db.execute(stmt)
    comments = result.scalars().all()

    items = []
    for c in comments:
        # 대댓글 조회
        replies_stmt = (
            select(Comment)
            .where(Comment.parent_id == c.id)
            .order_by(asc(Comment.created_at))
        )
        replies_result = await db.execute(replies_stmt)
        replies = replies_result.scalars().all()

        items.append({
            "id": c.id,
            "user_id": c.user_id,
            "body": c.body,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "replies": [
                {
                    "id": r.id,
                    "user_id": r.user_id,
                    "body": r.body,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in replies
            ],
        })

    return {"article_id": article_id, "comments": items}


def _article_to_dict(article: Article, include_body: bool = False) -> dict:
    """Article 모델을 딕셔너리로 변환한다."""
    data = {
        "id": article.id,
        "title_en": article.title_en,
        "title_ko": article.title_ko,
        "url": article.url,
        "source_name": article.source_name,
        "source_type": article.source_type,
        "company_tags": json.loads(article.company_tags) if article.company_tags else [],
        "category_tags": json.loads(article.category_tags) if article.category_tags else [],
        "importance_score": article.importance_score,
        "evaluation_reason": article.evaluation_reason,
        "insights": json.loads(article.insights) if article.insights else None,
        "published_at": article.published_at.isoformat() if article.published_at else None,
        "crawled_at": article.crawled_at.isoformat() if article.crawled_at else None,
    }
    if include_body:
        data["body_en"] = article.body_en
        data["body_ko"] = article.body_ko
    return data
