"""ITTF 프로젝트 설정 — 크롤링 소스, 키워드, 기업 가중치"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# === Anthropic API ===
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
SONNET_MODEL = "claude-sonnet-4-6"
HAIKU_MODEL = "claude-haiku-4-5-20251001"

# === 데이터베이스 ===
_db_path = PROJECT_ROOT / "data" / "ittf.db"
_db_path.parent.mkdir(parents=True, exist_ok=True)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{_db_path}")

# === 크롤링 스케줄 ===
CRAWL_SCHEDULE = {
    "day_of_week": "mon,thu",  # 월, 목
    "hour": 7,
    "minute": 0,
    "timezone": "Asia/Seoul",
}
EMAIL_SEND_HOUR = 8  # 오전 8시 발송

# === 모니터링 기업 (11개사) ===
COMPANIES = {
    "Microsoft": {"category": "Cloud, AI, Enterprise", "weight": 2},
    "Google": {"category": "Search, AI, Cloud", "weight": 2},
    "Apple": {"category": "Device, OS, AI", "weight": 1},
    "Meta": {"category": "SNS, AR/VR, AI", "weight": 1},
    "Nvidia": {"category": "GPU, AI Infra, Robotics", "weight": 2},
    "OpenAI": {"category": "AI Model, Product", "weight": 2},
    "Tesla": {"category": "EV, Robotics, Physical AI", "weight": 0},
    "Anthropic": {"category": "AI Model, Safety", "weight": 2},
    "Mistral AI": {"category": "Open-source LLM", "weight": 0},
    "Perplexity": {"category": "AI Search", "weight": 0},
    "Amazon": {"category": "Cloud, AI, Commerce", "weight": 1},
}

# === 크롤링 소스 ===
CRAWL_SOURCES = [
    # 기업 공식 AI 블로그 (1차 소스, 출처 점수 3점)
    {
        "name": "microsoft_ai",
        "urls": [
            "https://www.microsoft.com/en-us/ai",
            "https://azure.microsoft.com/en-us/blog/",
        ],
        "company": "Microsoft",
        "source_type": "official_blog",
        "source_score": 3,
    },
    {
        "name": "google_ai",
        "urls": ["https://blog.google/technology/ai/"],
        "company": "Google",
        "source_type": "official_blog",
        "source_score": 3,
    },
    {
        "name": "apple_ml",
        "urls": ["https://machinelearning.apple.com/research"],
        "company": "Apple",
        "source_type": "official_blog",
        "source_score": 3,
    },
    {
        "name": "meta_ai",
        "urls": ["https://ai.meta.com/blog/"],
        "company": "Meta",
        "source_type": "official_blog",
        "source_score": 3,
    },
    {
        "name": "nvidia_ai",
        "urls": ["https://blogs.nvidia.com/blog/category/generative-ai/"],
        "company": "Nvidia",
        "source_type": "official_blog",
        "source_score": 3,
    },
    {
        "name": "openai_news",
        "urls": ["https://openai.com/news/"],
        "company": "OpenAI",
        "source_type": "official_blog",
        "source_score": 3,
    },
    {
        "name": "tesla_blog",
        "urls": ["https://www.tesla.com/blog"],
        "company": "Tesla",
        "source_type": "official_blog",
        "source_score": 3,
    },
    {
        "name": "anthropic_news",
        "urls": ["https://www.anthropic.com/news"],
        "company": "Anthropic",
        "source_type": "official_blog",
        "source_score": 3,
    },
    {
        "name": "mistral_news",
        "urls": ["https://mistral.ai/news/"],
        "company": "Mistral AI",
        "source_type": "official_blog",
        "source_score": 3,
    },
    {
        "name": "perplexity_blog",
        "urls": ["https://blog.perplexity.ai/"],
        "company": "Perplexity",
        "source_type": "official_blog",
        "source_score": 3,
    },
    {
        "name": "amazon_ml",
        "urls": ["https://aws.amazon.com/blogs/machine-learning/"],
        "company": "Amazon",
        "source_type": "official_blog",
        "source_score": 3,
    },
    # 신뢰 미디어 (2차 소스)
    {
        "name": "the_verge",
        "urls": ["https://www.theverge.com/ai-artificial-intelligence"],
        "company": None,
        "source_type": "media",
        "source_score": 2,
    },
    {
        "name": "techcrunch",
        "urls": ["https://techcrunch.com/category/artificial-intelligence/"],
        "company": None,
        "source_type": "media",
        "source_score": 2,
    },
    {
        "name": "wired",
        "urls": ["https://www.wired.com/tag/artificial-intelligence/"],
        "company": None,
        "source_type": "media",
        "source_score": 1,
    },
    {
        "name": "ars_technica",
        "urls": ["https://arstechnica.com/ai/"],
        "company": None,
        "source_type": "media",
        "source_score": 1,
    },
]

# === 필터링 키워드 ===
KEYWORDS = {
    "critical": {  # +3점
        "keywords": [
            "launch", "announce", "release", "partnership",
            "acquisition", "funding", "humanoid", "Physical AI",
        ],
        "score": 3,
    },
    "high": {  # +2점
        "keywords": [
            "model", "API", "robot", "autonomous", "regulation",
        ],
        "score": 2,
    },
    "normal": {  # +1점
        "keywords": [
            "AI", "update", "feature",
        ],
        "score": 1,
    },
}

# === 제외 키워드 (수집 제외) ===
EXCLUDE_KEYWORDS = [
    "careers", "hiring", "job", "recruit",
    "CSR", "diversity", "sustainability",
    "earnings", "quarterly results", "revenue report",
]

# === 선별 설정 ===
MAX_ARTICLES_PER_RUN = 30  # 회당 최종 선별 수
RULE_BASED_TOP_N = 50  # 1단계 규칙 기반 상위 N개
MIN_BODY_LENGTH = 200  # 최소 본문 길이 (단어)

# === 기사 보관 ===
ARTICLE_RETENTION_DAYS = 90  # 3개월
