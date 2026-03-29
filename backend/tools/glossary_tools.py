"""용어 사전 도구 — 기술 용어 일관 번역 관리"""

from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models import Glossary, gen_id


async def get_glossary(session: AsyncSession) -> dict[str, str]:
    """전체 용어 사전을 {영어: 한국어} 딕셔너리로 반환한다."""
    result = await session.execute(select(Glossary))
    entries = result.scalars().all()
    return {e.term_en: e.term_ko for e in entries}


async def get_glossary_list(session: AsyncSession) -> list[dict]:
    """용어 사전 전체를 리스트로 반환한다."""
    result = await session.execute(select(Glossary).order_by(Glossary.term_en))
    entries = result.scalars().all()
    return [
        {
            "id": e.id,
            "term_en": e.term_en,
            "term_ko": e.term_ko,
            "added_by": e.added_by,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in entries
    ]


async def update_glossary(
    session: AsyncSession,
    term_en: str,
    term_ko: str,
    added_by: str = "agent",
    article_id: str | None = None,
) -> str:
    """용어를 추가하거나 업데이트한다. 용어 ID를 반환."""
    result = await session.execute(
        select(Glossary).where(Glossary.term_en == term_en)
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.term_ko = term_ko
        existing.updated_at = datetime.now(timezone.utc)
        await session.commit()
        return existing.id
    else:
        entry = Glossary(
            id=gen_id(),
            term_en=term_en,
            term_ko=term_ko,
            added_by=added_by,
            first_seen_in=article_id,
        )
        session.add(entry)
        await session.commit()
        return entry.id


async def get_previous_translation(session: AsyncSession, term_en: str) -> str | None:
    """특정 용어의 기존 번역을 조회한다."""
    result = await session.execute(
        select(Glossary.term_ko).where(Glossary.term_en == term_en)
    )
    return result.scalar_one_or_none()
