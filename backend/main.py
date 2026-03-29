"""ITTF 백엔드 — FastAPI 메인 앱"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.config import ANTHROPIC_API_KEY
from backend.database.connection import init_db
import backend.database.models  # 모델 로드
from backend.api.routes import articles, pipeline, admin
from backend.scheduler.jobs import setup_scheduler, shutdown_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행"""
    await init_db()
    setup_scheduler()
    print("[ITTF] 서버 시작 완료")
    yield
    shutdown_scheduler()
    print("[ITTF] 서버 종료")


app = FastAPI(
    title="ITTF — 빅테크 트렌드 크롤링 플랫폼",
    description="Claude 에이전트 기반 AI 트렌드 자동 수집·선별·번역·인사이트 시스템",
    version="0.1.0",
    lifespan=lifespan,
)

# 라우터 등록
app.include_router(articles.router)
app.include_router(pipeline.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    return {
        "project": "ITTF",
        "version": "0.1.0",
        "status": "running",
        "api_key_configured": bool(ANTHROPIC_API_KEY),
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
