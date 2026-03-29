# 빅테크 트렌드 크롤링 & 팀 공유 플랫폼 기획서 (Claude 에이전트 아키텍처)

**문서 버전:** v2.1 (Claude API 기반 에이전트)
**작성일:** 2026년 3월 29일
**이전 버전:** v2.0 (Ollama + LangGraph) → v2.1 (Claude API + Anthropic Agent SDK)
**작성 목적:** 해외 AI/빅테크 파트너십 팀을 위한 **Claude 기반 자율 에이전트** 트렌드 수집 및 내부 공유 시스템 구축

---

## 1. 프로젝트 개요

### 배경 및 목적

해외 AI 테크 기업들과의 파트너십 업무 특성상, 각 기업의 최신 기술 동향·제품 발표·전략 변화를 빠르게 파악하는 것이 핵심 역량임. 현재는 팀원 개개인이 수동으로 뉴스를 검색하는 방식으로, 정보 수집의 일관성과 효율이 떨어짐.

**→ 목표:** 주요 빅테크 11개사의 AI 트렌드를 **Claude 기반 자율 에이전트 시스템**이 자동 수집·지능형 선별·번역·인사이트화하여 팀 전용 플랫폼에서 공유하고, 팀원 간 논의 및 개인 스크랩이 가능한 환경 구축.

### v2.0(Ollama) → v2.1(Claude) 전환 핵심 이유

| 항목 | v2.0 (Ollama 로컬) | v2.1 (Claude API) |
|------|-------------------|-------------------|
| 추론 품질 | 로컬 8b~12b 수준 (★★★☆☆) | Claude Sonnet/Haiku (★★★★★) |
| 한국어 번역 | 어색한 직역 빈번 | 자연스러운 의역, 맥락 이해 |
| 교차 분석 | 단순 패턴 매칭 수준 | 깊은 맥락 이해 기반 분석 |
| 에이전트 도구 사용 | LangGraph 래퍼 필요 | **네이티브 Tool Use** (Claude 내장) |
| 에이전트 프레임워크 | LangGraph (서드파티) | **Anthropic Agent SDK** (공식) |
| RAM 부담 | 5~17GB 점유 | 없음 (API 호출) |
| 월 비용 | $0 | **$8~30** (모델 조합에 따라) |
| 설치 | Ollama + 모델 다운로드 필요 | API 키 발급만 필요 |

### 왜 "에이전트"인가? (단순 LLM vs 에이전트)

| 구분 | 단순 API 호출 | 에이전트 시스템 |
|------|-------------|---------------|
| 실행 흐름 | 개발자가 코드로 순서를 고정 | 에이전트가 상황을 판단하고 다음 행동을 결정 |
| 오류 처리 | `try/except`로 개발자가 미리 작성 | 에이전트가 오류 원인을 분석하고 대안 전략 수립 |
| 도구 사용 | 없음 (텍스트 입출력만) | DB 조회, 웹 요청, 파싱, 검색 등 도구를 자율적으로 호출 |
| 멀티스텝 추론 | 단일 호출 후 종료 | 목표 달성까지 여러 단계를 자율 수행 |
| 메모리 | 매 호출이 독립적 | 이전 작업 결과를 기억하고 활용 |
| 협업 | 불가 | 에이전트 간 결과 전달, 역할 위임 |
| 학습 | 없음 | 팀원 반응(스크랩/댓글) 데이터로 선별 정확도 향상 |

**에이전트 행동 예시 (Claude의 Tool Use 활용):**

```
[상황] Google Blog 크롤링 403 에러 발생

Claude 에이전트의 사고 과정:
1. fetch_url("https://blog.google/technology/ai") → 403 Forbidden
2. "HTML 직접 접근이 차단됐다. RSS 피드를 시도해보자."
   → parse_rss("https://blog.google/technology/ai/rss/") → 성공, 12개 기사 수집
3. "성공했다. 이 전략 변경을 기록해두자."
   → save_source_stats("google_ai", strategy="rss", success=true)
4. "다음 실행부터 Google은 RSS 우선으로 전환."
   → update_source_config("google_ai", primary_strategy="rss")
5. "관리자에게도 알려주자."
   → send_admin_alert("Google AI Blog: HTML→RSS 전략 자동 전환됨")
```

### 대상 사용자

- 총 **7명** (관리자 1명 + 팀원 6명)
- 관리자: 시스템 설정·팀원 초대·소스 관리·에이전트 상태 모니터링 담당
- 팀원: 기사 열람·댓글·반응·개인 스크랩 기능 사용

### 운영 환경

- **개인 노트북 로컬 운영** (별도 서버 없음)
- **월 운영 비용: $8~30** (Claude API 종량제)
- 노트북이 켜져 있어야 에이전트 실행 및 사이트 운영 가능 (월·목 07:00 필수)

---

## 2. 모니터링 대상 기업 & 소스

### 모니터링 기업 (11개사)

| # | 기업 | 카테고리 |
|---|------|----------|
| 1 | Microsoft | Cloud, AI, Enterprise |
| 2 | Google | Search, AI, Cloud |
| 3 | Apple | Device, OS, AI |
| 4 | Meta | SNS, AR/VR, AI |
| 5 | Nvidia | GPU, AI Infra, Robotics |
| 6 | OpenAI | AI Model, Product |
| 7 | Tesla | EV, Robotics, Physical AI |
| 8 | Anthropic | AI Model, Safety |
| 9 | Mistral AI | Open-source LLM |
| 10 | Perplexity | AI Search |
| 11 | Amazon | Cloud, AI, Commerce |

### 크롤링 소스

**기업 공식 AI 블로그 (1차 소스)**

| 기업 | URL | 비고 |
|------|-----|------|
| Microsoft | microsoft.com/en-us/ai + azure.microsoft.com/en-us/blog | Azure AI 블로그 병행 수집 |
| Google | blog.google/technology/ai | AI 카테고리 전용 |
| Apple | machinelearning.apple.com/research | Apple ML Research 전용 |
| Meta | ai.meta.com/blog | Meta AI 공식 블로그 |
| Nvidia | blogs.nvidia.com/blog/category/generative-ai | Generative AI 카테고리 |
| OpenAI | openai.com/news | 전체가 AI 관련 |
| Tesla | tesla.com/blog | AI·Robotics 태그 필터링 |
| Anthropic | anthropic.com/news | 전체가 AI 관련 |
| Mistral AI | mistral.ai/news | 전체가 AI 관련 |
| Perplexity | blog.perplexity.ai | 전체가 AI 관련 |
| Amazon | aws.amazon.com/blogs/machine-learning | ML 카테고리 전용 |

> **수집 원칙:** AI·ML·모델·제품·로보틱스 관련 카테고리 태그가 달린 글만 수집. 인사, 재무, CSR 관련 포스트는 자동 제외.

**신뢰 미디어 (2차 소스)**

| 미디어 | 특징 |
|--------|------|
| The Verge | 빅테크 제품·전략 심층 보도 |
| TechCrunch | 스타트업·투자·신제품 속보 |
| Wired | 기술 트렌드 심층 분석 |
| Ars Technica | 기술적 깊이 있는 보도 |

> **우선순위:** 공식 AI 블로그 > The Verge > TechCrunch > Wired > Ars Technica

---

## 3. 에이전트 아키텍처 설계

### 전체 에이전트 구조도

```
                        ┌───────────────────────────┐
                        │    Orchestrator Agent      │
                        │ (지휘자 — Claude Sonnet)    │
                        │ Anthropic Agent SDK 기반    │
                        └────────────┬──────────────┘
                                     │
            ┌────────────────────────┼────────────────────────┐
            │                        │                        │
            ▼                        ▼                        ▼
    ┌───────────────┐     ┌──────────────────┐     ┌──────────────────┐
    │ Crawling Agent │     │ Evaluation Agent │     │ Newsletter Agent │
    │ (수집가)        │     │ (심사위원)        │     │ (편집장)          │
    │ Tool Use 전용   │     │ Claude Sonnet    │     │ Claude Haiku     │
    └───────┬───────┘     └────────┬─────────┘     └──────────────────┘
            │                      │                        ▲
            │                      ▼                        │
            │             ┌──────────────────┐              │
            │             │ Translation Agent│              │
            │             │ (번역가)          │              │
            │             │ Claude Sonnet    │              │
            │             └────────┬─────────┘              │
            │                      │                        │
            │                      ▼                        │
            │             ┌──────────────────┐              │
            └────────────►│  Insight Agent   │──────────────┘
                          │  (분석가)         │
                          │  Claude Sonnet   │
                          └──────────────────┘
```

### Claude 네이티브 Tool Use — 핵심 설계 원리

Claude API는 **Tool Use(도구 사용)**를 네이티브로 지원한다. 별도의 에이전트 프레임워크 없이도 Claude가 도구를 선택·호출·결과 해석을 자율적으로 수행한다.

```python
# Anthropic Agent SDK 기반 에이전트 정의 예시
import anthropic
from anthropic_agent_sdk import Agent, tool

class CrawlingAgent(Agent):
    model = "claude-sonnet-4-6"

    system_prompt = """당신은 빅테크 AI 블로그 크롤링 전문 에이전트입니다.
    11개 소스에서 AI 관련 기사를 수집하세요.
    소스별로 최적의 전략(HTML 파싱, RSS, Playwright)을 판단하여 사용하세요.
    실패 시 대안 전략으로 전환하고, 결과를 기록하세요."""

    @tool
    def fetch_url(self, url: str, headers: dict = None) -> str:
        """URL에서 HTML을 가져옵니다."""
        ...

    @tool
    def parse_rss(self, feed_url: str) -> list[dict]:
        """RSS 피드를 파싱하여 기사 목록을 반환합니다."""
        ...

    @tool
    def save_raw_article(self, article: dict) -> str:
        """수집된 기사를 DB에 저장합니다."""
        ...
```

**LangGraph(v2.0) vs Anthropic Agent SDK(v2.1) 비교:**

| 항목 | LangGraph (v2.0) | Anthropic Agent SDK (v2.1) |
|------|------------------|---------------------------|
| Tool Use | LangChain 래퍼 필요 | **Claude 네이티브** (내장) |
| 상태 관리 | StateGraph로 명시적 관리 | **에이전트 컨텍스트**로 자연스럽게 |
| 조건부 라우팅 | 개발자가 함수로 정의 | **Claude가 자율 판단** |
| 에이전트 간 통신 | 상태 객체 전달 | **핸드오프(handoff)** 패턴 |
| 체크포인팅 | SQLite 체크포인터 | 실행 로그 DB 저장으로 대체 |
| 학습 곡선 | 높음 (그래프 개념) | **낮음** (Python 클래스 정의) |
| Claude 최적화 | 간접 연동 | **직접 최적화** |

### 에이전트 워크플로우 (Anthropic Agent SDK 기반)

```
APScheduler (월·목 07:00 KST)
       │
       ▼
  Orchestrator Agent (Claude Sonnet)
  "오늘 크롤링을 시작합니다. 각 에이전트를 순차 실행합니다."
       │
       ├──► Crawling Agent (Claude Sonnet + Tool Use)
       │       ├─ fetch_url() / parse_rss() / render_page() 도구 자율 선택
       │       ├─ 소스별 최적 전략 판단 → 실패 시 대안 자동 전환
       │       ├─ detect_duplicate() → 중복 제거
       │       └─ 결과: raw_articles (100~200개) → DB 저장
       │
       │    [Orchestrator 자율 판단]
       │    Claude가 수집 결과를 보고 다음 행동 결정:
       │    "143개 수집 완료. Tesla만 실패했지만 다른 소스로 충분. 선별 단계로 진행."
       │
       ├──► Evaluation Agent (Claude Sonnet + Tool Use)
       │       ├─ get_raw_articles() → 제목+요약 일괄 로드
       │       ├─ Claude의 추론으로 산업 영향력·기술 혁신성 평가
       │       ├─ get_historical_ratings() → 팀 선호도 패턴 반영
       │       └─ 결과: 30개 선별 + 각 기사 선정 사유 → DB 저장
       │
       ├──► Translation Agent (Claude Sonnet + Tool Use)
       │       ├─ get_glossary() → 기존 용어 사전 로드
       │       ├─ Claude의 고품질 한국어 번역 (맥락 이해 기반)
       │       ├─ 자체 품질 검증: 원문 대조 → 누락/오역 감지 → 재번역
       │       ├─ 신규 용어 발견 시 update_glossary() 자동 호출
       │       └─ 결과: 30개 번역본 + 품질 점수 → DB 저장
       │
       ├──► Insight Agent (Claude Sonnet + Tool Use)
       │       ├─ 30개 기사 클러스터링 → 주제별 그룹화
       │       ├─ get_past_insights(weeks=4) → 과거 트렌드 대비 분석
       │       ├─ get_company_timeline() → 기업별 동향 맥락 파악
       │       ├─ 기사 간 교차 분석 (Claude의 깊은 맥락 이해)
       │       └─ 결과: 기사별 인사이트 + 주간 트렌드 리포트 → DB 저장
       │
       └──► Newsletter Agent (Claude Haiku + Tool Use)
              ├─ get_team_preferences() → 팀원별 관심 분야 조회
              ├─ 팀원별 기사 순서 개인화
              ├─ 뉴스레터 제목 자동 생성
              ├─ render_newsletter_html() → send_email()
              └─ 결과: 7명 발송 완료

  ~07:50  전체 파이프라인 완료 (Claude API는 로컬 Ollama 대비 5~10배 빠름)
  08:00   팀원 7명에게 이메일 도착 + 사이트 업데이트
```

**v2.0(Ollama) 대비 속도 개선:**

| 단계 | v2.0 (Ollama 로컬) | v2.1 (Claude API) |
|------|-------------------|-------------------|
| 번역 30개 | 20~30분 | **2~3분** |
| 인사이트 30개 | 10~15분 | **1~2분** |
| 전체 파이프라인 | 40~60분 | **10~15분** |

---

## 4. 에이전트 상세 명세

### Agent 1: Orchestrator (지휘자) — Claude Sonnet

**역할:** 전체 파이프라인의 실행을 조율한다. 각 에이전트의 결과를 받아 다음 행동을 **자율적으로 판단**한다.

**모델:** `claude-sonnet-4-6` (판단·분기 결정에 적합)

**부여 도구(Tools):**

| 도구명 | 기능 |
|--------|------|
| `get_pipeline_status(run_id)` | 현재 파이프라인 진행 상태 조회 |
| `run_crawling_agent(sources)` | Crawling Agent 실행 |
| `run_evaluation_agent(run_id)` | Evaluation Agent 실행 |
| `run_translation_agent(run_id)` | Translation Agent 실행 |
| `run_insight_agent(run_id)` | Insight Agent 실행 |
| `run_newsletter_agent(run_id)` | Newsletter Agent 실행 |
| `send_admin_alert(message)` | 관리자에게 알림 발송 |
| `query_db(sql)` | DB 상태 조회 (읽기 전용) |

**Anthropic Agent SDK 핸드오프 패턴:**

```python
from anthropic_agent_sdk import Agent, tool, handoff

class OrchestratorAgent(Agent):
    model = "claude-sonnet-4-6"

    system_prompt = """당신은 빅테크 트렌드 수집 파이프라인의 지휘자입니다.
    다음 순서로 에이전트를 실행하세요:
    1. Crawling → 2. Evaluation → 3. Translation → 4. Insight → 5. Newsletter

    각 단계 완료 후 결과를 확인하고:
    - 수집 수가 20개 미만이면 소스를 확장하거나 관리자에게 알리세요.
    - 번역 품질이 낮으면 해당 기사만 재번역을 지시하세요.
    - 문제가 3회 이상 반복되면 관리자에게 긴급 알림을 보내세요."""

    # 하위 에이전트로 핸드오프
    handoffs = [
        handoff(CrawlingAgent, "기사 수집이 필요할 때"),
        handoff(EvaluationAgent, "수집된 기사 선별이 필요할 때"),
        handoff(TranslationAgent, "선별된 기사 번역이 필요할 때"),
        handoff(InsightAgent, "인사이트 생성이 필요할 때"),
        handoff(NewsletterAgent, "뉴스레터 발송이 필요할 때"),
    ]
```

---

### Agent 2: Crawling Agent (수집가) — Claude Sonnet + Tool Use

**역할:** 15개 소스(11개 공식 블로그 + 4개 미디어)에서 기사를 수집한다. Claude의 추론 능력으로 소스별 최적 전략을 **자율적으로 판단**하고, 실패 시 대안을 **스스로 찾아** 실행한다.

**모델:** `claude-sonnet-4-6` (전략 판단이 필요하므로 Sonnet)

**부여 도구(Tools):**

| 도구명 | 기능 |
|--------|------|
| `fetch_url(url, headers)` | HTTP GET 요청 |
| `parse_html(html, selector)` | CSS 셀렉터로 HTML 파싱 |
| `parse_rss(feed_url)` | RSS/Atom 피드 파싱 |
| `render_page(url)` | Playwright로 JS 렌더링 후 HTML 반환 |
| `detect_duplicate(url)` | URL 기반 중복 기사 확인 |
| `save_raw_article(article_data)` | 원문 기사 DB 저장 |
| `get_source_config(source_name)` | 소스별 설정 조회 |
| `update_source_config(source, config)` | 소스 설정 업데이트 (전략 변경 등) |
| `get_last_crawl_result(source)` | 이전 크롤링 결과 조회 |
| `save_source_stats(source, stats)` | 소스별 통계 저장 |

**Claude가 자율적으로 수행하는 행동:**

1. **전략 선택**: 소스별 설정을 읽고, 이전 성공/실패 이력을 참고하여 최적 전략 결정
2. **적응적 파싱**: HTML 구조가 변경되면 페이지를 분석하여 새 셀렉터를 추론
3. **수집량 검증**: "이 소스에서 평소 15개인데 2개만 수집됨 → 셀렉터 문제 가능성 → 대안 시도"
4. **중복 필터링**: 매 기사마다 `detect_duplicate()` 호출하여 이미 수집된 기사 건너뜀
5. **결과 보고**: 수집 완료 후 소스별 성공/실패/수집 수를 구조화하여 Orchestrator에 보고

**수집 필터링 키워드:**

| 키워드 군 | 키워드 목록 |
|-----------|-------------|
| AI 모델·기술 | `AI`, `model`, `API`, `LLM`, `multimodal` |
| 제품·전략 | `launch`, `release`, `partnership`, `acquisition`, `funding` |
| 시장·규제 | `regulation`, `product`, `competition` |
| Physical AI·로보틱스 | `Physical AI`, `robot`, `robotics`, `humanoid`, `embodied AI`, `autonomous`, `self-driving`, `dexterous`, `manipulation` |

- 광고성 콘텐츠, 채용 공고, 인사·재무·CSR 관련 글 제외
- 최소 본문 길이: 200단어 이상

---

### Agent 3: Evaluation Agent (심사위원) — Claude Sonnet

**역할:** 수집된 전체 기사(100~200개)에서 팀에게 가장 가치 있는 30개를 선별한다. Claude Sonnet의 뛰어난 추론 능력으로 **산업 맥락을 이해**하고, 팀원 반응 데이터를 참고하여 시간이 갈수록 선별이 정교해진다.

**모델:** `claude-sonnet-4-6` (복잡한 중요도 판단에 Sonnet 필수)

**부여 도구(Tools):**

| 도구명 | 기능 |
|--------|------|
| `get_raw_articles(run_id)` | 수집된 원문 기사 목록 (제목 + 첫 단락) |
| `check_keyword_match(article, keywords)` | 키워드 매칭 점수 |
| `calculate_source_score(source_type)` | 출처 점수 계산 |
| `get_company_weight(company)` | 기업별 가중치 조회 |
| `calculate_recency_score(published_date)` | 최신성 점수 계산 |
| `get_historical_ratings()` | 과거 팀원 반응 통계 (스크랩 수, 댓글 수, 이모지) |
| `get_team_interests()` | 팀원별 관심 분야 |
| `save_evaluation_result(article_id, score, reason)` | 평가 결과 저장 |

**3단계 선별 프로세스:**

```
전체 수집 기사 (100~200개)
        │
        ▼
  1단계: 규칙 기반 점수화 (도구 사용, Claude 추론 없이)
  ├─ check_keyword_match() → 키워드 점수
  ├─ calculate_source_score() → 출처 점수
  ├─ get_company_weight() → 기업 가중치
  └─ calculate_recency_score() → 최신성 점수
        │
        ▼
  상위 50개 추림
        │
        ▼
  2단계: Claude 추론 기반 중요도 평가
  ├─ 50개 기사의 제목+요약을 Claude Sonnet이 분석
  ├─ 산업 영향력·기술 혁신성·파트너십 관련성 종합 판단
  ├─ 1~5점 중요도 + 판단 사유 생성
  └─ (Claude의 깊은 맥락 이해 → 로컬 LLM 대비 정확도 대폭 향상)
        │
        ▼
  상위 40개
        │
        ▼
  3단계: 팀 선호도 반영 (도구 + Claude 추론) ★ 학습하는 시스템
  ├─ get_historical_ratings() → 팀원 스크랩/댓글 패턴 분석
  ├─ get_team_interests() → 현재 팀 관심사 반영
  ├─ Claude가 패턴을 종합 분석하여 최종 30개 확정
  └─ 각 기사에 "왜 선정했는가" 사유 첨부
        │
        ▼
  최종 30개 (선정 사유 포함)
```

**점수화 기준 (1단계):**

A. 출처 점수 (최대 3점)

| 출처 | 점수 |
|------|------|
| 기업 공식 AI 블로그 | 3점 |
| The Verge / TechCrunch | 2점 |
| Wired / Ars Technica | 1점 |

B. 키워드 점수 (중복 합산)

| 키워드 군 | 키워드 | 점수 |
|-----------|--------|------|
| 초고중요 | `launch`, `announce`, `release`, `partnership`, `acquisition`, `funding`, `humanoid`, `Physical AI` | +3점 |
| 고중요 | `model`, `API`, `robot`, `autonomous`, `regulation` | +2점 |
| 일반 | `AI`, `update`, `feature` | +1점 |

C. 기업 관련성 점수 (관리자 페이지에서 수정 가능)

| 기업 그룹 | 기본 점수 |
|-----------|----------|
| OpenAI, Anthropic, Google, Microsoft, Nvidia | +2점 |
| Meta, Amazon, Apple | +1점 |
| Tesla, Mistral AI, Perplexity | +0점 |

D. 최신성 점수

| 발행 시점 | 점수 |
|-----------|------|
| 24시간 이내 | +2점 |
| 24~48시간 | +1점 |
| 48시간 이상 | +0점 |

---

### Agent 4: Translation Agent (번역가) — Claude Sonnet

**역할:** 선별된 30개 기사를 한국어로 번역한다. Claude Sonnet의 **뛰어난 한국어 능력**으로 자연스러운 의역을 수행하고, 자체 품질 검증 루프와 용어 사전을 자율 관리한다.

**모델:** `claude-sonnet-4-6` (한국어 번역 품질 최우선)

**부여 도구(Tools):**

| 도구명 | 기능 |
|--------|------|
| `get_articles_to_translate(run_id)` | 번역 대상 기사 조회 |
| `get_glossary()` | 기술 용어 사전 조회 |
| `update_glossary(term_en, term_ko)` | 용어 사전 업데이트 |
| `get_previous_translation(term)` | 동일 용어의 과거 번역 조회 |
| `save_translation(article_id, title_ko, body_ko, quality_score)` | 번역 결과 저장 |

**자체 품질 검증 루프:**

```
기사 원문 로드
    │
    ▼
용어 사전 로드 → 기존 용어 확인
    │
    ▼
Claude Sonnet 번역 수행
(맥락 이해 기반 자연스러운 의역)
    │
    ▼
자체 검증 (Claude가 스스로 판단)
├─ "핵심 수치(매출, 성능 지표)가 원문과 일치하는가?"
├─ "고유명사(GPT-5, Gemini Pro)가 정확하게 표기되었는가?"
├─ "번역 누락이 없는가? (원문 문단 수 ≈ 번역 문단 수)"
├─ "기술 용어가 glossary와 일치하는가?"
├─ "자연스러운 한국어인가? (번역투가 아닌가?)"
    │
    ├─ 품질 0.8 이상 → 저장
    └─ 품질 미달 → 문제 부분만 재번역 → 재검증
    │
    ▼
신규 기술 용어 발견 시
    → update_glossary() 자동 호출
    → "이후 모든 기사에서 동일하게 번역"
```

**번역 기준:**

| 항목 | 내용 |
|------|------|
| 번역 범위 | 제목 + 본문 전체 |
| 원문 보존 | 원문과 번역본 모두 저장 및 노출 |
| 품질 기준 | 자연스러운 의역, 번역투 최소화 |
| 고유명사 | 기업명·제품명·기술 용어는 원어 병기 |
| 예시 | "GPT-5 model weights" → "GPT-5 모델 가중치(model weights)" |

**Claude 번역 품질 vs Ollama 비교:**

| 항목 | Ollama (llama3.1:8b) | Claude Sonnet |
|------|---------------------|---------------|
| 자연스러움 | 번역투 빈번, 어색한 조사 사용 | 원어민 수준의 자연스러운 한국어 |
| 맥락 이해 | 문장 단위 직역 경향 | 문단 전체 맥락 이해 후 의역 |
| 기술 용어 | 일관성 없음 | 용어 사전 기반 일관된 번역 |
| 고유명사 | 임의 번역 가능성 | 원어 유지 원칙 준수 |

---

### Agent 5: Insight Agent (분석가) — Claude Sonnet

**역할:** 번역된 기사들을 **교차 분석**하여 단순 요약을 넘어선 트렌드 인사이트를 생성한다. Claude Sonnet의 깊은 맥락 이해로 기사 간 관계, 산업 흐름, 과거 대비 변화를 도출한다.

**모델:** `claude-sonnet-4-6` (교차 분석에 높은 추론 능력 필수)

**부여 도구(Tools):**

| 도구명 | 기능 |
|--------|------|
| `get_translated_articles(run_id)` | 번역 완료된 기사 조회 |
| `get_past_insights(weeks=4)` | 최근 4주간 인사이트 조회 |
| `search_related_articles(keyword)` | 과거 기사에서 관련 기사 검색 |
| `get_company_timeline(company)` | 특정 기업의 최근 동향 타임라인 |
| `save_insight(article_id, insight_data)` | 기사별 인사이트 저장 |
| `save_weekly_report(report_data)` | 주간 트렌드 리포트 저장 |

**생성하는 결과물:**

**A. 기사별 인사이트 (30개)**

| 항목 | 설명 | 예시 |
|------|------|------|
| 핵심 요약 | 기사의 핵심을 2~3문장으로 압축 | "OpenAI가 GPT-5를 발표하며 멀티모달 처리 속도를 3배 향상시켰다." |
| 파트너십 관련성 | 우리 팀 업무와의 직접적 연관성 | "API 파트너사에 새로운 가격 정책 적용 예정 — 계약 재검토 필요" |
| 경쟁사 영향 | 타 기업에 미치는 영향 분석 | "Google Gemini와의 성능 비교에서 우위 주장 → 경쟁 구도 변화" |
| 시장 시그널 | 업계 트렌드 방향성 | "에지 AI 시장 확대 신호 — 온디바이스 모델 수요 증가 예상" |
| 현실 세계 적용 가능성 | *(Physical AI 기사만)* | "Optimus Gen-3 공개 — 산업 현장 도입 2027년으로 앞당겨질 가능성" |
| 액션 아이템 | *(선택)* 팀 차원 검토 사항 | "Anthropic 새 약관 검토 후 파트너십 계약 반영 여부 확인 필요" |

**B. 주간 트렌드 리포트 (1개) ★ 에이전트 핵심 기능**

Claude Sonnet의 멀티스텝 추론:
```
1. 30개 기사를 읽고 주제별 클러스터링
2. get_past_insights(weeks=4) → 지난 4주 트렌드와 비교
3. "에이전트 AI" 언급이 지난주 3건 → 이번 주 8건 = 급증 트렌드
4. get_company_timeline("OpenAI") → 최근 3주간 연속 에이전트 관련 발표
5. search_related_articles("pricing") → 과거 가격 변경 기사와 연결
6. 교차 분석: "Google과 OpenAI가 같은 주에 에이전트 기능을 발표한 것은 직접 경쟁 신호"
7. 최종 주간 트렌드 리포트 구성
```

**주간 리포트 구조:**
```json
{
  "week": "2026-W13",
  "top_trends": [
    {
      "trend": "에이전트형 AI 경쟁 본격화",
      "description": "OpenAI, Google, Anthropic 3사가 동시에 에이전트 기능 강화...",
      "related_articles": ["article_id_1", "article_id_5", "article_id_12"],
      "vs_last_week": "신규 부상",
      "impact_level": "높음"
    }
  ],
  "cross_analysis": [
    "Google의 Gemini 2.0 발표와 OpenAI의 GPT-5 발표가 같은 주에 이루어진 것은 직접적 경쟁 신호"
  ],
  "keyword_delta": {
    "에이전트 AI": "+167%",
    "온디바이스 모델": "신규 등장",
    "Physical AI": "+23% (3주 연속 상승)"
  }
}
```

**AI 응답 스키마 (기사별):**
```json
{
  "title_ko": "번역된 제목",
  "body_ko": "번역된 본문 전체",
  "importance_score": 4,
  "evaluation_reason": "선정 사유",
  "insights": {
    "summary": "핵심 요약 2~3문장",
    "partnership_relevance": "파트너십 관련성",
    "competitor_impact": "경쟁사 영향",
    "market_signal": "시장 시그널",
    "physical_ai_applicability": "현실 세계 적용 가능성 (해당 시만)",
    "action_item": "액션 아이템 (해당 시만)"
  }
}
```

---

### Agent 6: Newsletter Agent (편집장) — Claude Haiku

**역할:** 최종 뉴스레터를 구성하고 팀원에게 발송한다. 비용 효율을 위해 **Claude Haiku**를 사용한다 (구성·포맷팅은 고급 추론이 불필요).

**모델:** `claude-haiku-4-5` (비용 절감, 단순 구성 작업에 충분)

**부여 도구(Tools):**

| 도구명 | 기능 |
|--------|------|
| `get_insights(run_id)` | 인사이트 조회 |
| `get_translated_articles(run_id)` | 번역된 기사 조회 |
| `get_weekly_report(run_id)` | 주간 리포트 조회 |
| `get_team_preferences()` | 팀원별 관심 분야/이메일 수신 설정 |
| `render_newsletter_html(data)` | HTML 뉴스레터 렌더링 |
| `send_email(to, subject, html_body)` | Gmail SMTP 이메일 발송 |

**뉴스레터 구성:**

| 항목 | 내용 |
|------|------|
| 발송 시각 | 매주 **월·목 오전 8시** |
| 제목 | 이번 주 핵심 키워드 자동 생성 (예: "[ITTF] 에이전트 AI 경쟁·Physical AI 투자 — 3/29") |
| 내용 | 주간 트렌드 요약 / 중요도 5점 하이라이트 / 30개 기사 목록 / 사이트 바로가기 |
| 개인화 | 팀원별 관심 분야 기사를 상단 배치 |
| 수신 설정 | 개인별 이메일 수신 ON/OFF 가능 |
| 발송 방식 | Gmail SMTP (무료, 일 500통) |

---

## 5. 팀 공유 플랫폼 (프라이빗 사이트)

### F3-1. 접근 제어 (보안)

| 항목 | 내용 |
|------|------|
| 로그인 방식 | **Google 계정 로그인만 지원** |
| 초대 방식 | 관리자가 Google 계정 이메일로 초대 → 수락 시 접근 가능 |
| 외부 노출 | 완전 비공개, 검색엔진 미노출 |

**Google OAuth 인증 플로우:**
```
1. 사용자가 [Google로 로그인] 클릭
2. Google OAuth 2.0 동의 화면으로 리다이렉트
3. Google → NextAuth 콜백 URL로 authorization code 전달
4. NextAuth → Google에서 access_token + 사용자 정보 수령
5. NextAuth → 해당 이메일이 users 테이블에 있는지 확인
   ├── 있음 (is_active=true): 로그인 허용, JWT 세션 발급
   ├── 있음 (is_active=false): 접근 차단 페이지
   └── 없음: "초대받지 않은 계정입니다" 페이지
6. 이후 모든 API 요청 시 JWT 토큰을 Authorization 헤더에 포함
```

### F3-2. 메인 피드 (홈 화면)

- **최신순 / 중요도순** 정렬 토글
- 기업별 필터, 카테고리 필터, 소스별 필터
- 읽음/안읽음 표시
- 각 카드: 기업 로고 + 기업명, 한국어 제목, 카테고리 태그, 수집일, 중요도, 댓글 수, 출처

### F3-3. 기사 상세 페이지

```
┌─────────────────────────────────────────┐
│ [기업 로고] OpenAI | techcrunch.com      │
│ 발행: 2026.03.19 | 수집: 2026.03.29     │
│ 태그: #AI모델 #제품런칭                  │
├─────────────────────────────────────────┤
│ 제목 (한국어 번역)                       │
│ 제목 (원문 영어)          [📌 스크랩]    │
├─────────────────────────────────────────┤
│ 🤖 왜 이 기사가 선정되었나?              │
│ "파트너십 가격 정책 변경은 팀 업무에     │
│  직접적 영향. 최근 팀원 관심도 높음."    │
├─────────────────────────────────────────┤
│ ⭐ AI 인사이트                           │
│ • 핵심 요약: ...                         │
│ • 파트너십 관련성: ...                   │
│ • 경쟁사 영향: ...                       │
│ • 시장 시그널: ...                       │
│ • 현실 세계 적용 가능성: ...             │
├─────────────────────────────────────────┤
│ [원문 보기] [번역본 보기] 탭 전환         │
│ 본문 내용...                             │
├─────────────────────────────────────────┤
│ 원문 링크: [바로가기 →]                  │
├─────────────────────────────────────────┤
│ 💬 팀 댓글 (3)                          │
│ 홍길동: "파트너십 계약에 영향 있을 듯"   │
│ [댓글 작성창]                            │
└─────────────────────────────────────────┘
```

### F3-4. 댓글 기능

| 기능 | 상세 |
|------|------|
| 댓글 작성 | 로그인한 팀원 누구나 가능 |
| 대댓글 | 1단계 답글 |
| 멘션 | `@이름` 호출 |
| 이모지 반응 | 👍 📌 🔥 💡 ❗ |
| 수정/삭제 | 본인 댓글만 |
| 알림 | 답글/멘션 시 이메일 알림 |

### F3-5. 개인 스크랩 공간

| 기능 | 상세 |
|------|------|
| 스크랩 추가 | [📌 스크랩] 버튼 |
| 스크랩 목록 | 본인만 볼 수 있는 개인 페이지 |
| 메모 | 스크랩 시 메모 작성/수정 가능 |
| 정렬·필터 | 날짜순 / 기업별 / 카테고리별 |
| 보관 예외 | **3개월 자동 삭제에서 제외** — 영구 보존 |

### F3-6. 주간 트렌드 리포트 페이지

```
┌─────────────────────────────────────────┐
│ 📊 주간 트렌드 리포트 — 2026년 13주차    │
├─────────────────────────────────────────┤
│ 🔥 이번 주 핵심 트렌드                   │
│                                         │
│ 1. 에이전트형 AI 경쟁 본격화 [신규 부상]  │
│    OpenAI, Google, Anthropic 3사가...    │
│    관련 기사: (3개 링크)                  │
│                                         │
│ 2. Physical AI 투자 급증 [3주 연속 지속]  │
│    Nvidia와 Tesla의 로보틱스 투자가...    │
│    관련 기사: (2개 링크)                  │
│                                         │
│ 📈 키워드 변화                           │
│ • "에이전트 AI" +167%                    │
│ • "온디바이스 모델" 신규 등장             │
│ • "Physical AI" +23% (3주 연속 상승)     │
├─────────────────────────────────────────┤
│ 🔗 교차 분석                             │
│ "Google의 Gemini 2.0과 OpenAI의 GPT-5   │
│  발표가 같은 주 — 직접적 경쟁 신호"      │
└─────────────────────────────────────────┘
```

### F3-7. 관리자 기능

| 기능 | 상세 |
|------|------|
| 팀원 관리 | Google 계정 초대(최대 6명), 권한 설정, 비활성화 |
| 수동 크롤링 | 즉시 에이전트 파이프라인 실행 |
| 기사 관리 | 삭제, 중요도 수동 수정 |
| 소스 관리 | 크롤링 소스 URL 추가/제거 |
| 키워드 관리 | 필터링 키워드 추가/제거 |
| 기업 가중치 | 우선순위 점수 기업별 가중치 조정 |
| **에이전트 대시보드** | 각 에이전트 실행 상태, 소요 시간, 에러 로그 |
| **파이프라인 이력** | 최근 10회 실행 이력, 소스별 성공/실패 통계 |
| **용어 사전 관리** | Translation Agent 자동 추가 용어 확인/수정/삭제 |
| **API 사용량 모니터링** | Claude API 토큰 사용량, 비용 추적 |

**에이전트 대시보드 화면:**
```
┌─────────────────────────────────────────┐
│ 🤖 에이전트 파이프라인 상태              │
│ 실행 ID: run_20260329_0700              │
│ 시작: 07:00 | 현재: 07:08               │
├─────────────────────────────────────────┤
│ ✅ Crawling Agent     07:00~07:04  완료  │
│    수집: 143개 / 실패: Tesla (→RSS 전환) │
│    Sonnet 토큰: 입력 8K / 출력 2K        │
│                                         │
│ ✅ Evaluation Agent   07:04~07:06  완료  │
│    선별: 30개 / 탈락: 113개              │
│    Sonnet 토큰: 입력 12K / 출력 3K       │
│                                         │
│ 🔄 Translation Agent  07:06~      진행중 │
│    완료: 22/30개 (73%)                   │
│    Sonnet 토큰: 입력 82K / 출력 78K      │
│                                         │
│ ⏳ Insight Agent      대기중              │
│ ⏳ Newsletter Agent   대기중              │
├─────────────────────────────────────────┤
│ 예상 완료: 07:12 (08:00 발송 예정)       │
│ 이번 실행 예상 비용: ~$3.80              │
└─────────────────────────────────────────┘
```

---

## 6. 기술 스택 상세 명세

### 전체 아키텍처 구조

```
[팀원 브라우저] ── 인터넷 ──▶ Cloudflare Tunnel (무료)
                                      │
                          [본인 노트북 (월·목 07:00 켜둠)]
                                      │
               ┌──────────────────────┼──────────────────────┐
               │                      │                      │
         Next.js (프론트)       FastAPI (백엔드)      Claude API ☁️
         TypeScript              Python 3.11+         (Anthropic 클라우드)
         Tailwind CSS                 │
         shadcn/ui               ┌────┴────┐
                                 │         │
                             SQLite    Anthropic
                             (DB)      Agent SDK
                                           │
                              ┌────────────┼────────────┐
                              │            │            │
                         Orchestrator  Crawling    Evaluation
                         (Sonnet)     (Sonnet)    (Sonnet)
                              │            │            │
                              │       Translation   Insight
                              │       (Sonnet)     (Sonnet)
                              │            │            │
                              └────────Newsletter──────┘
                                      (Haiku)
```

### 프론트엔드

| 항목 | 선택 | 이유 |
|------|------|------|
| 프레임워크 | **Next.js 14 (App Router)** | SSR, 빠른 초기 로딩 |
| 언어 | **TypeScript** | 타입 안정성 |
| 스타일링 | **Tailwind CSS** | 빠른 UI 개발, 반응형 |
| 상태 관리 | **Zustand** | 가볍고 간단 |
| 서버 상태 | **TanStack Query** | API 캐싱, 리패칭 |
| 인증 | **NextAuth.js v5** | Google OAuth 2.0 |
| 컴포넌트 | **shadcn/ui** | Tailwind 기반 |
| 아이콘 | **Lucide React** | shadcn/ui 통일성 |

**페이지 라우팅:**
```
app/
├── (auth)/
│   └── login/                → Google 로그인
├── (main)/
│   ├── page.tsx              → 메인 피드 (홈)
│   ├── articles/
│   │   └── [id]/page.tsx     → 기사 상세
│   ├── trends/
│   │   └── page.tsx          → 주간 트렌드 리포트
│   ├── scrapbook/
│   │   └── page.tsx          → 개인 스크랩
│   └── admin/
│       ├── page.tsx          → 관리자
│       ├── agents/page.tsx   → 에이전트 모니터링
│       └── glossary/page.tsx → 용어 사전
└── api/
    └── auth/[...nextauth]/   → NextAuth 핸들러
```

### 백엔드

| 항목 | 선택 | 이유 |
|------|------|------|
| 프레임워크 | **FastAPI (Python 3.11+)** | 비동기, Swagger 자동 문서화 |
| **에이전트 SDK** | **Anthropic Agent SDK (`claude-agent-sdk`)** | Claude 공식 에이전트 프레임워크, 네이티브 Tool Use |
| **Claude API** | **`anthropic` Python SDK** | Claude Sonnet/Haiku 호출 |
| 인증 | **Google OAuth 2.0 + JWT** | NextAuth 토큰 검증 |
| ORM | **SQLAlchemy 2.0 (async)** | 비동기 DB 쿼리 |
| DB 마이그레이션 | **Alembic** | 스키마 버전 관리 |
| 이메일 | **Gmail SMTP** (smtplib) | 무료 |
| 스케줄러 | **APScheduler** | Orchestrator 트리거 |
| 크롤링 (정적) | **httpx + BeautifulSoup4** | 가볍고 빠름 |
| 크롤링 (동적) | **Playwright (async)** | JS 렌더링 필요 시 |
| 환경변수 | **python-dotenv** | 환경별 설정 분리 |

**핵심 패키지:**
```
# requirements.txt
anthropic>=0.40.0          # Claude API SDK
claude-agent-sdk>=0.1.0    # Anthropic Agent SDK (에이전트 프레임워크)
fastapi>=0.110.0
uvicorn>=0.29.0
sqlalchemy[asyncio]>=2.0.0
aiosqlite>=0.20.0
alembic>=1.13.0
apscheduler>=3.10.0
httpx>=0.27.0
beautifulsoup4>=4.12.0
playwright>=1.43.0
python-dotenv>=1.0.0
python-jose[cryptography]  # JWT
```

**API 엔드포인트:**
```
# 기사
GET    /api/articles               → 기사 목록
GET    /api/articles/{id}          → 기사 상세
GET    /api/articles/{id}/comments → 댓글 목록

# 댓글
POST   /api/articles/{id}/comments → 댓글 작성
PATCH  /api/comments/{id}          → 수정
DELETE /api/comments/{id}          → 삭제
POST   /api/comments/{id}/reaction → 이모지 반응

# 스크랩
GET    /api/scrapbook               → 내 스크랩 목록
POST   /api/scrapbook               → 스크랩 추가
PATCH  /api/scrapbook/{id}          → 메모 수정
DELETE /api/scrapbook/{id}          → 스크랩 해제

# 주간 트렌드
GET    /api/trends/weekly           → 최신 주간 리포트
GET    /api/trends/weekly/{week}    → 특정 주차 리포트

# 관리자
POST   /api/admin/crawl             → 수동 파이프라인 실행
GET    /api/admin/users             → 팀원 목록
POST   /api/admin/invite            → 초대
DELETE /api/admin/users/{id}        → 차단
PATCH  /api/admin/articles/{id}     → 중요도 수정
DELETE /api/admin/articles/{id}     → 기사 삭제

# 에이전트 모니터링
GET    /api/admin/pipeline/status   → 현재 실행 상태
GET    /api/admin/pipeline/history  → 최근 10회 이력
GET    /api/admin/agents/{name}/logs → 에이전트별 로그
GET    /api/admin/api-usage         → Claude API 사용량/비용

# 용어 사전
GET    /api/admin/glossary          → 용어 목록
PATCH  /api/admin/glossary/{id}     → 수정
DELETE /api/admin/glossary/{id}     → 삭제
```

### 데이터베이스

| 항목 | 선택 | 이유 |
|------|------|------|
| DB | **SQLite** | 설치 불필요, 7명 소규모에 충분 |

**테이블 스키마:**

```sql
-- ============================================
-- 핵심 테이블
-- ============================================

CREATE TABLE users (
  id            TEXT PRIMARY KEY,
  email         TEXT UNIQUE,
  name          TEXT,
  profile_image TEXT,
  role          TEXT DEFAULT 'member',
  is_active     INTEGER DEFAULT 1,
  email_notify  INTEGER DEFAULT 1,
  created_at    TEXT
);

CREATE TABLE articles (
  id               TEXT PRIMARY KEY,
  title_en         TEXT,
  title_ko         TEXT,
  body_en          TEXT,
  body_ko          TEXT,
  url              TEXT UNIQUE,
  source_name      TEXT,
  source_type      TEXT,
  company_tags     TEXT,              -- JSON
  category_tags    TEXT,              -- JSON
  importance_score INTEGER,
  evaluation_reason TEXT,             -- 에이전트 선정 사유
  insights         TEXT,              -- JSON
  published_at     TEXT,
  crawled_at       TEXT,
  expires_at       TEXT
);

CREATE TABLE comments (
  id         TEXT PRIMARY KEY,
  article_id TEXT REFERENCES articles,
  user_id    TEXT REFERENCES users,
  parent_id  TEXT REFERENCES comments,
  body       TEXT,
  created_at TEXT,
  updated_at TEXT
);

CREATE TABLE reactions (
  id         TEXT PRIMARY KEY,
  comment_id TEXT REFERENCES comments,
  user_id    TEXT REFERENCES users,
  emoji      TEXT,
  UNIQUE(comment_id, user_id, emoji)
);

CREATE TABLE scrapbook (
  id         TEXT PRIMARY KEY,
  user_id    TEXT REFERENCES users,
  article_id TEXT REFERENCES articles,
  memo       TEXT,
  created_at TEXT,
  UNIQUE(user_id, article_id)
);

-- ============================================
-- 에이전트 관련 테이블
-- ============================================

CREATE TABLE pipeline_runs (
  id               TEXT PRIMARY KEY,
  triggered_at     TEXT,
  trigger_type     TEXT,              -- 'scheduled' | 'manual'
  status           TEXT,              -- 'running' | 'completed' | 'failed'
  total_crawled    INTEGER,
  total_selected   INTEGER,
  total_translated INTEGER,
  errors           TEXT,              -- JSON
  completed_at     TEXT,
  elapsed_seconds  REAL,
  api_tokens_input  INTEGER,          -- Claude API 입력 토큰 합계
  api_tokens_output INTEGER,          -- Claude API 출력 토큰 합계
  api_cost_usd     REAL              -- 예상 비용 ($)
);

CREATE TABLE agent_logs (
  id           TEXT PRIMARY KEY,
  run_id       TEXT REFERENCES pipeline_runs,
  agent_name   TEXT,
  model_used   TEXT,                  -- 'claude-sonnet-4-6' | 'claude-haiku-4-5'
  status       TEXT,
  started_at   TEXT,
  completed_at TEXT,
  input_count  INTEGER,
  output_count INTEGER,
  retries      INTEGER DEFAULT 0,
  tokens_input  INTEGER,
  tokens_output INTEGER,
  error_detail TEXT,
  metadata     TEXT                   -- JSON
);

CREATE TABLE glossary (
  id             TEXT PRIMARY KEY,
  term_en        TEXT UNIQUE,
  term_ko        TEXT,
  added_by       TEXT,                -- 'agent' | 'admin'
  first_seen_in  TEXT REFERENCES articles,
  created_at     TEXT,
  updated_at     TEXT
);

CREATE TABLE weekly_reports (
  id          TEXT PRIMARY KEY,
  run_id      TEXT REFERENCES pipeline_runs,
  week_label  TEXT,
  report_data TEXT,                   -- JSON
  created_at  TEXT
);

CREATE TABLE source_stats (
  id              TEXT PRIMARY KEY,
  source_name     TEXT,
  run_id          TEXT REFERENCES pipeline_runs,
  strategy_used   TEXT,
  success         INTEGER,
  articles_found  INTEGER,
  error_detail    TEXT,
  elapsed_seconds REAL,
  crawled_at      TEXT
);

-- API 사용량 추적
CREATE TABLE api_usage (
  id             TEXT PRIMARY KEY,
  run_id         TEXT REFERENCES pipeline_runs,
  agent_name     TEXT,
  model          TEXT,
  tokens_input   INTEGER,
  tokens_output  INTEGER,
  cost_usd       REAL,
  recorded_at    TEXT
);
```

### 기사 보관 정책

| 항목 | 내용 |
|------|------|
| 보관 기간 | **3개월** |
| 초기화 | 3개월 경과 시 자동 삭제 (스크랩 기사는 예외 보존) |
| 초기화 주기 | 분기 1회 (1월·4월·7월·10월 1일) |

### 외부 접속 & 이메일

| 항목 | 내용 |
|------|------|
| 외부 접속 | **Cloudflare Tunnel** (무료) |
| 이메일 | **Gmail SMTP** (무료, 일 500통) |

---

## 7. 비용 분석

### Claude API 모델별 가격 (2026년 3월 기준)

| 모델 | 입력 ($/1M 토큰) | 출력 ($/1M 토큰) | 용도 |
|------|-----------------|-----------------|------|
| Claude Sonnet 4.6 | $3 | $15 | Evaluation, Translation, Insight |
| Claude Haiku 4.5 | $0.80 | $4 | Newsletter, 단순 작업 |

### 회당 토큰 사용량 예측 (30개 기사)

| 에이전트 | 모델 | 입력 토큰 | 출력 토큰 | 회당 비용 |
|---------|------|----------|----------|----------|
| Crawling | Sonnet | ~8K | ~2K | $0.05 |
| Evaluation | Sonnet | ~12K | ~3K | $0.08 |
| Translation (번역) | Sonnet | ~105K | ~105K | $1.89 |
| Translation (검증) | Sonnet | ~210K | ~15K | $0.86 |
| Insight (기사별) | Sonnet | ~120K | ~24K | $0.72 |
| Insight (주간 리포트) | Sonnet | ~34K | ~3K | $0.15 |
| Newsletter | Haiku | ~10K | ~5K | $0.03 |
| **회당 합계** | | **~499K** | **~157K** | **$3.78** |

### 월간 비용 예측 (8회 실행)

| 항목 | 월 토큰 | 월 비용 |
|------|---------|---------|
| 입력 (Sonnet 위주) | ~3.9M | $11.7 |
| 출력 (Sonnet 위주) | ~1.2M | $18.0 |
| Newsletter (Haiku) | ~120K | $0.24 |
| **월 합계** | **~5.2M** | **~$30** |

### 비용 최적화 옵션

**옵션 A: 전부 Sonnet — 최고 품질**
- 월 **~$30**
- 모든 에이전트가 최고 품질로 동작

**옵션 B: 번역을 Haiku로 전환 — 균형**
- 월 **~$16**
- 번역 품질 다소 하락하나 여전히 Ollama 대비 우수
- Evaluation/Insight만 Sonnet 유지

**옵션 C: 번역+인사이트를 Haiku로 — 최저 비용**
- 월 **~$8**
- 핵심 판단(Evaluation)만 Sonnet
- 번역·인사이트 품질이 Sonnet 대비 하락

**권장: 옵션 A ($30/월)**
- Claude Pro 구독($20) + API $30 = 월 $50 이하로 최고 품질의 에이전트 시스템 운영 가능
- 참고: Claude Pro 구독은 이 시스템에 필수가 아님 (API만 있으면 됨)

### 비용 절감 팁

1. **Prompt Caching**: 반복 사용되는 시스템 프롬프트를 캐싱하면 입력 토큰 최대 90% 절감
2. **Batch API**: 실시간이 아닌 배치 처리이므로 Batch API 사용 시 50% 할인
3. **적용 시 예상**: $30 → Batch API 적용 → **~$15/월**

---

## 8. 프로젝트 디렉토리 구조

```
ITTF/
├── backend/
│   ├── main.py                        # FastAPI 엔트리포인트
│   ├── config.py                      # 설정 (소스, 스케줄, API 키 등)
│   ├── requirements.txt
│   │
│   ├── database/
│   │   ├── connection.py              # SQLite 연결
│   │   ├── models.py                  # SQLAlchemy 모델
│   │   └── migrations/                # Alembic
│   │
│   ├── agents/                        # ★ 에이전트 핵심
│   │   ├── __init__.py
│   │   ├── base.py                    # 에이전트 공통 베이스 (Anthropic SDK 래퍼)
│   │   ├── orchestrator.py            # Orchestrator Agent (Sonnet)
│   │   ├── crawler.py                 # Crawling Agent (Sonnet + Tools)
│   │   ├── evaluator.py              # Evaluation Agent (Sonnet)
│   │   ├── translator.py             # Translation Agent (Sonnet)
│   │   ├── insight_generator.py      # Insight Agent (Sonnet)
│   │   └── newsletter.py             # Newsletter Agent (Haiku)
│   │
│   ├── tools/                         # ★ 에이전트 도구
│   │   ├── __init__.py
│   │   ├── web_tools.py              # fetch_url, parse_html, parse_rss, render_page
│   │   ├── db_tools.py               # DB CRUD
│   │   ├── email_tools.py            # Gmail SMTP
│   │   ├── glossary_tools.py         # 용어 사전
│   │   └── search_tools.py           # 기사 검색, 중복 감지
│   │
│   ├── scheduler/
│   │   └── jobs.py                   # APScheduler (월·목 07:00)
│   │
│   └── api/
│       ├── deps.py
│       └── routes/
│           ├── articles.py
│           ├── comments.py
│           ├── scraps.py
│           ├── trends.py
│           ├── admin.py
│           ├── pipeline.py           # 에이전트 모니터링
│           ├── glossary.py           # 용어 사전
│           └── api_usage.py          # API 사용량 추적
│
├── frontend/
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── app/
│       ├── components/
│       │   ├── ui/                   # shadcn/ui
│       │   ├── feed/
│       │   ├── article/
│       │   ├── trends/
│       │   ├── admin/
│       │   └── agents/              # 에이전트 모니터링 UI
│       └── lib/
│           ├── api.ts
│           ├── auth.ts
│           └── store.ts
│
├── data/
│   └── ittf.db                       # SQLite
│
├── .env.example                      # ANTHROPIC_API_KEY, Google OAuth 등
├── CLAUDE.md
└── README.md
```

---

## 9. 사용자 시나리오

### 시나리오 A: 정기 수집 (에이전트 파이프라인)

```
월·목 07:00  APScheduler → Orchestrator Agent 실행
             ├─ Crawling Agent (Sonnet): 15개 소스 수집 → 143개 기사 (2분)
             │  └─ Tesla Blog 403 → RSS 자동 전환 → 성공
             ├─ Evaluation Agent (Sonnet): 143→30개 선별 (1분)
             │  └─ 팀 스크랩 패턴 반영 → Physical AI 가중치 상향
             ├─ Translation Agent (Sonnet): 30개 고품질 번역 (3분)
             │  └─ 자체 검증 통과, "agentic AI" 용어 사전 추가
             ├─ Insight Agent (Sonnet): 인사이트 + 주간 리포트 (2분)
             │  └─ "에이전트 AI 경쟁 본격화" 신규 트렌드 감지
             └─ Newsletter Agent (Haiku): 개인화 뉴스레터 (1분)

07:12  전체 완료 (총 ~10분, API 비용 ~$3.80)
08:00  팀원 7명 이메일 수신
```

### 시나리오 B: 관리자 API 비용 모니터링

```
관리자  에이전트 대시보드 → API 사용량 탭
       이번 달 현재: $22.40 / 예상 월말: $28.50
       에이전트별 비용: Translation $15.20 (54%) > Insight $5.80 > Evaluation $3.10
       "번역이 비용의 절반. 필요시 Haiku로 전환 가능."
```

---

## 10. 개발 우선순위

### Phase 1 — Claude 에이전트 기반 MVP

- [ ] Anthropic Agent SDK 설치 및 Claude API 연동 확인
- [ ] 에이전트 공통 베이스 구현 (`agents/base.py`)
- [ ] Crawling Agent 구현 (15개 소스, Tool Use 기반 적응적 크롤링)
- [ ] Evaluation Agent 구현 (3단계 선별)
- [ ] Translation Agent 구현 (자체 검증 + 용어 사전)
- [ ] Orchestrator Agent 구현 (핸드오프 패턴, 에러 복구)
- [ ] SQLite DB 스키마 생성 (핵심 + 에이전트 테이블)
- [ ] Google 로그인 연동 (NextAuth + Google OAuth 2.0)
- [ ] 기본 피드 페이지 (목록 + 상세, 선정 사유)
- [ ] APScheduler → Orchestrator 트리거 (월·목 07:00)
- [ ] Cloudflare Tunnel 설정

### Phase 2 — 고급 에이전트 기능

- [ ] Insight Agent 구현 (교차 분석 + 주간 리포트)
- [ ] Newsletter Agent 구현 (Haiku, 개인화)
- [ ] 주간 트렌드 리포트 페이지
- [ ] 에이전트 대시보드 (실행 상태, 로그)
- [ ] API 사용량/비용 모니터링
- [ ] 용어 사전 관리 페이지
- [ ] Prompt Caching 적용 (비용 절감)

### Phase 3 — 팀 협업 기능

- [ ] 개인 스크랩 공간
- [ ] 댓글 + 대댓글 + 멘션 + 이모지
- [ ] 기업/카테고리/소스 필터 + 읽음/안읽음
- [ ] 관리자 페이지 (소스·키워드·가중치·팀원 관리)
- [ ] Gmail 이메일 알림

### Phase 4 — 최적화 & 확장

- [ ] Batch API 적용 (비용 50% 절감)
- [ ] Evaluation Agent 팀 선호도 학습 고도화
- [ ] 기사 3개월 자동 삭제 (스크랩 예외)
- [ ] SQLite 자동 백업
- [ ] 모델 전환 옵션 (Sonnet ↔ Haiku 에이전트별 선택)

---

## 11. 로컬 운영 주의사항

| 항목 | 내용 |
|------|------|
| **노트북 상시 가동** | 월·목 오전 7시에 켜져 있어야 에이전트 파이프라인 실행 |
| **인터넷 필수** | Claude API 호출에 인터넷 연결 필요 (Ollama와 다른 점) |
| **API 키 보안** | `.env` 파일에 `ANTHROPIC_API_KEY` 저장, `.gitignore`에 반드시 추가 |
| **처리 속도** | 전체 파이프라인 ~10분 (Ollama 40~60분 대비 5배 빠름) |
| **RAM 부담** | Ollama 대비 경미 (API 호출이므로 모델 로딩 없음) |
| **비용 관리** | 관리자 대시보드에서 API 사용량/비용 추적 가능 |
| **사이트 접속** | 노트북 꺼지면 팀원 접속 불가 (Cloudflare Tunnel 끊김) |
| **데이터 백업** | `data/ittf.db` 주기적 백업 권장 |

---

## 12. v1.4 → v2.0 → v2.1 변경 이력 요약

| 항목 | v1.4 (단순 LLM) | v2.0 (Ollama 에이전트) | v2.1 (Claude 에이전트) |
|------|-----------------|---------------------|---------------------|
| AI 엔진 | Ollama 단순 호출 | Ollama + LangGraph | **Claude API + Agent SDK** |
| 추론 품질 | ★★★☆☆ | ★★★☆☆ | **★★★★★** |
| 한국어 번역 | 어색한 직역 | 어색한 직역 | **자연스러운 의역** |
| 에이전트 프레임워크 | 없음 | LangGraph | **Anthropic Agent SDK** |
| 처리 속도 | 40~60분 | 40~60분 | **~10분** |
| RAM 사용 | 5~17GB | 5~17GB | **경미** |
| 월 비용 | $0 | $0 | **$8~30** |
| 설치 복잡도 | Ollama + 모델 다운 | Ollama + LangGraph | **API 키만 발급** |
