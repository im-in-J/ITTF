"""ITTF 백엔드 — FastAPI 메인 앱"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.config import ANTHROPIC_API_KEY
from backend.database.connection import init_db
import backend.database.models  # 모델 로드
from backend.api.routes import articles, pipeline, admin
from backend.scheduler.jobs import setup_scheduler, shutdown_scheduler

# 관리자 API 키 (.env에 ADMIN_API_KEY 설정, 미설정 시 인증 비활성)
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행"""
    await init_db()
    setup_scheduler()
    print("[ITTF] 서버 시작 완료")
    if not ADMIN_API_KEY:
        print("[ITTF] ⚠️  ADMIN_API_KEY 미설정 — 관리자 API 인증 비활성화 상태")
    yield
    shutdown_scheduler()
    print("[ITTF] 서버 종료")


app = FastAPI(
    title="ITTF — 빅테크 트렌드 크롤링 플랫폼",
    description="Claude 에이전트 기반 AI 트렌드 자동 수집·선별·번역·인사이트 시스템",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def admin_auth_middleware(request: Request, call_next):
    """관리자 API 엔드포인트에 API Key 인증 적용"""
    if request.url.path.startswith("/api/admin") and ADMIN_API_KEY:
        api_key = request.headers.get("X-Admin-Key", "")
        if api_key != ADMIN_API_KEY:
            raise HTTPException(status_code=403, detail="관리자 인증 실패")
    return await call_next(request)


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
