"""APScheduler 설정 — 월·목 07:00 KST 자동 실행"""

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from backend.config import CRAWL_SCHEDULE


scheduler = AsyncIOScheduler()


async def scheduled_pipeline():
    """스케줄에 의해 자동 실행되는 파이프라인."""
    from backend.agents.orchestrator import run_pipeline
    print("\n[스케줄러] 정기 크롤링 시작")
    result = await run_pipeline(trigger_type="scheduled", use_ai=True)
    print(f"[스케줄러] 정기 크롤링 완료: {result['status']}")


def setup_scheduler():
    """스케줄러를 설정한다. FastAPI 시작 시 호출."""
    scheduler.add_job(
        scheduled_pipeline,
        trigger=CronTrigger(
            day_of_week=CRAWL_SCHEDULE["day_of_week"],
            hour=CRAWL_SCHEDULE["hour"],
            minute=CRAWL_SCHEDULE["minute"],
            timezone=CRAWL_SCHEDULE["timezone"],
        ),
        id="crawl_pipeline",
        name="정기 크롤링 파이프라인",
        replace_existing=True,
    )
    scheduler.start()
    print(f"[스케줄러] 설정 완료 — {CRAWL_SCHEDULE['day_of_week']} {CRAWL_SCHEDULE['hour']:02d}:{CRAWL_SCHEDULE['minute']:02d} KST")


def shutdown_scheduler():
    """스케줄러를 종료한다. FastAPI 종료 시 호출."""
    if scheduler.running:
        scheduler.shutdown()
