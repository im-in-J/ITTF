"""ITTF 전체 DB 모델 — v2.1 기획안 기반"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    String, Text, Integer, Float, Boolean, DateTime, ForeignKey, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database.connection import Base


def gen_id() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ============================================
# 핵심 테이블
# ============================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    profile_image: Mapped[str | None] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(String, default="member")  # 'admin' | 'member'
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    email_notify: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    comments = relationship("Comment", back_populates="user")
    reactions = relationship("Reaction", back_populates="user")
    scraps = relationship("Scrapbook", back_populates="user")


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    title_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    title_ko: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_ko: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    source_name: Mapped[str] = mapped_column(String, nullable=False)
    source_type: Mapped[str] = mapped_column(String, nullable=False)  # 'official_blog' | 'media'
    company_tags: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    category_tags: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    importance_score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1~5
    evaluation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    insights: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    crawled_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    comments = relationship("Comment", back_populates="article")
    scraps = relationship("Scrapbook", back_populates="article")


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    article_id: Mapped[str] = mapped_column(String, ForeignKey("articles.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    parent_id: Mapped[str | None] = mapped_column(String, ForeignKey("comments.id"), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    article = relationship("Article", back_populates="comments")
    user = relationship("User", back_populates="comments")
    reactions = relationship("Reaction", back_populates="comment")
    replies = relationship("Comment", backref="parent", remote_side="Comment.id")


class Reaction(Base):
    __tablename__ = "reactions"
    __table_args__ = (
        UniqueConstraint("comment_id", "user_id", "emoji", name="uq_reaction"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    comment_id: Mapped[str] = mapped_column(String, ForeignKey("comments.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    emoji: Mapped[str] = mapped_column(String, nullable=False)  # 👍📌🔥💡❗

    comment = relationship("Comment", back_populates="reactions")
    user = relationship("User", back_populates="reactions")


class Scrapbook(Base):
    __tablename__ = "scrapbook"
    __table_args__ = (
        UniqueConstraint("user_id", "article_id", name="uq_scrap"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    article_id: Mapped[str] = mapped_column(String, ForeignKey("articles.id"), nullable=False)
    memo: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    user = relationship("User", back_populates="scraps")
    article = relationship("Article", back_populates="scraps")


# ============================================
# 에이전트 관련 테이블
# ============================================

class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    triggered_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    trigger_type: Mapped[str] = mapped_column(String, default="manual")  # 'scheduled' | 'manual'
    status: Mapped[str] = mapped_column(String, default="running")  # 'running' | 'completed' | 'failed'
    total_crawled: Mapped[int] = mapped_column(Integer, default=0)
    total_selected: Mapped[int] = mapped_column(Integer, default=0)
    total_translated: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    elapsed_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    api_tokens_input: Mapped[int] = mapped_column(Integer, default=0)
    api_tokens_output: Mapped[int] = mapped_column(Integer, default=0)
    api_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)

    agent_logs = relationship("AgentLog", back_populates="pipeline_run")
    source_stats = relationship("SourceStat", back_populates="pipeline_run")


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    run_id: Mapped[str] = mapped_column(String, ForeignKey("pipeline_runs.id"), nullable=False)
    agent_name: Mapped[str] = mapped_column(String, nullable=False)
    model_used: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="running")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    input_count: Mapped[int] = mapped_column(Integer, default=0)
    output_count: Mapped[int] = mapped_column(Integer, default=0)
    retries: Mapped[int] = mapped_column(Integer, default=0)
    tokens_input: Mapped[int] = mapped_column(Integer, default=0)
    tokens_output: Mapped[int] = mapped_column(Integer, default=0)
    error_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    pipeline_run = relationship("PipelineRun", back_populates="agent_logs")


class Glossary(Base):
    __tablename__ = "glossary"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    term_en: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    term_ko: Mapped[str] = mapped_column(String, nullable=False)
    added_by: Mapped[str] = mapped_column(String, default="agent")  # 'agent' | 'admin'
    first_seen_in: Mapped[str | None] = mapped_column(String, ForeignKey("articles.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class WeeklyReport(Base):
    __tablename__ = "weekly_reports"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    run_id: Mapped[str | None] = mapped_column(String, ForeignKey("pipeline_runs.id"), nullable=True)
    week_label: Mapped[str] = mapped_column(String, nullable=False)  # '2026-W13'
    report_data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class SourceStat(Base):
    __tablename__ = "source_stats"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    source_name: Mapped[str] = mapped_column(String, nullable=False)
    run_id: Mapped[str] = mapped_column(String, ForeignKey("pipeline_runs.id"), nullable=False)
    strategy_used: Mapped[str] = mapped_column(String, nullable=False)  # 'html_parse' | 'rss' | 'playwright'
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    articles_found: Mapped[int] = mapped_column(Integer, default=0)
    error_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    elapsed_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    crawled_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    pipeline_run = relationship("PipelineRun", back_populates="source_stats")


class ApiUsage(Base):
    __tablename__ = "api_usage"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    run_id: Mapped[str | None] = mapped_column(String, ForeignKey("pipeline_runs.id"), nullable=True)
    agent_name: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False)
    tokens_input: Mapped[int] = mapped_column(Integer, default=0)
    tokens_output: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
