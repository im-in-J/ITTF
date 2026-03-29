# 빅테크 트렌드 크롤링 & 팀 공유 플랫폼 기획서 (에이전트 아키텍처)

**문서 버전:** v2.0 (에이전트 전환)
**작성일:** 2026년 3월 29일
**작성 목적:** 해외 AI/빅테크 파트너십 팀을 위한 **자율 에이전트 기반** 트렌드 수집 및 내부 공유 시스템 구축

---

## 1. 프로젝트 개요

### 배경 및 목적

해외 AI 테크 기업들과의 파트너십 업무 특성상, 각 기업의 최신 기술 동향·제품 발표·전략 변화를 빠르게 파악하는 것이 핵심 역량임. 현재는 팀원 개개인이 수동으로 뉴스를 검색하는 방식으로, 정보 수집의 일관성과 효율이 떨어짐.

**→ 목표:** 주요 빅테크 11개사의 AI 트렌드를 **자율 에이전트 시스템**이 자동 수집·지능형 선별·번역·인사이트화하여 팀 전용 플랫폼에서 공유하고, 팀원 간 논의 및 개인 스크랩이 가능한 환경 구축.

### 왜 "에이전트"인가? (단순 LLM vs 에이전트)

| 구분 | 단순 LLM 호출 (v1.4) | 에이전트 시스템 (v2.0) |
|------|----------------------|----------------------|
| 실행 흐름 | 개발자가 코드로 순서를 고정 | 에이전트가 상황을 판단하고 다음 행동을 결정 |
| 오류 처리 | `try/except`로 개발자가 미리 작성 | 에이전트가 오류 원인을 분석하고 대안 전략 수립 |
| 도구 사용 | 없음 (텍스트 입출력만) | DB 조회, 웹 요청, 파싱, 검색 등 도구를 자율적으로 호출 |
| 멀티스텝 추론 | 단일 호출 후 종료 | 목표 달성까지 여러 단계를 자율 수행 |
| 메모리 | 매 호출이 독립적 | 이전 작업 결과를 기억하고 활용 |
| 협업 | 불가 | 에이전트 간 결과 전달, 역할 위임 |
| 학습 | 없음 | 팀원 반응(스크랩/댓글) 데이터로 선별 정확도 향상 |

**핵심 차이 예시:**

```
[단순 LLM] Google Blog 크롤링 403 에러 발생
→ try/except → 3회 재시도 → 실패 → 스킵 → 로그 기록

[에이전트] Google Blog 크롤링 403 에러 발생
→ "Google Blog가 3회 연속 실패했다"
→ 이전 실행 기록 조회 → "지난주에도 실패 이력 있음"
→ 크롤링 전략을 RSS 피드 방식으로 전환 시도
→ RSS로 성공 → 다음부터 RSS 전략 우선 적용
→ 관리자에게 상태 변경 알림 발송
→ 나머지 10개 소스는 병렬 진행 유지
```

### 대상 사용자

- 총 **7명** (관리자 1명 + 팀원 6명)
- 관리자: 시스템 설정·팀원 초대·소스 관리·에이전트 상태 모니터링 담당
- 팀원: 기사 열람·댓글·반응·개인 스크랩 기능 사용

### 운영 환경

- **개인 노트북 로컬 운영** (별도 서버 없음)
- **월 운영 비용: $0** (전면 무료 스택)
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
                        ┌──────────────────────┐
                        │  Orchestrator Agent   │
                        │  (지휘자 — 전체 조율)   │
                        └───────────┬──────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
            ▼                       ▼                       ▼
    ┌───────────────┐     ┌─────────────────┐     ┌─────────────────┐
    │ Crawling Agent │     │ Evaluation Agent│     │ Newsletter Agent│
    │ (수집가)        │     │ (심사위원)       │     │ (편집장)         │
    └───────┬───────┘     └────────┬────────┘     └─────────────────┘
            │                      │                       ▲
            │                      ▼                       │
            │             ┌─────────────────┐              │
            │             │ Translation     │              │
            │             │ Agent (번역가)   │              │
            │             └────────┬────────┘              │
            │                      │                       │
            │                      ▼                       │
            │             ┌─────────────────┐              │
            └────────────►│ Insight Agent   │──────────────┘
                          │ (분석가)         │
                          └─────────────────┘
```

### 에이전트 워크플로우 (LangGraph 기반)

```
APScheduler (월·목 07:00 KST)
       │
       ▼
  Orchestrator Agent ─── 상태 초기화, 실행 계획 수립
       │
       ├──► Crawling Agent (11개 소스 병렬 수집)
       │       ├─ 소스별 최적 전략 선택 (HTML 파싱 / RSS / API)
       │       ├─ 실패 소스 → 전략 변경 후 재시도
       │       ├─ 중복 기사 자동 감지 → 제외
       │       └─ 결과: raw_articles (100~200개)
       │
       │    [Orchestrator 판단]
       │    수집 수가 20개 미만이면? → 소스 확장 or 관리자 알림
       │    전체 실패면? → 재시도 3회 후 관리자 긴급 알림
       │
       ├──► Evaluation Agent (지능형 선별)
       │       ├─ 1단계: 키워드/출처/최신성 규칙 기반 필터 (도구 사용)
       │       ├─ 2단계: AI 중요도 추론 (LLM 멀티스텝)
       │       ├─ 3단계: 팀 선호도 반영 (과거 스크랩/댓글 패턴 분석)
       │       └─ 결과: selected_articles (30개) + 선정 사유
       │
       ├──► Translation Agent (품질 보증 번역)
       │       ├─ 용어 사전(glossary) 로드
       │       ├─ 30개 기사 전문 번역
       │       ├─ 자체 품질 검증 → 오역/누락 감지 시 재번역
       │       ├─ 신규 기술 용어 발견 시 용어 사전 자동 업데이트
       │       └─ 결과: translated_articles (30개) + 품질 점수
       │
       │    [Orchestrator 판단]
       │    저품질 번역이 5개 이상이면? → 해당 기사만 재번역 지시
       │
       ├──► Insight Agent (교차 분석)
       │       ├─ 30개 기사 주제별 클러스터링
       │       ├─ 과거 4주 인사이트와 비교 → 신규/지속 트렌드 분류
       │       ├─ 기업 간 교차 분석 (예: "Google과 OpenAI가 동일 방향")
       │       ├─ 기사별 인사이트 + 주간 트렌드 리포트 생성
       │       └─ 결과: article_insights (30개) + weekly_report (1개)
       │
       └──► Newsletter Agent (개인화 발송)
              ├─ 팀원별 관심 분야 기반 기사 순서 개인화
              ├─ 뉴스레터 제목 = 이번 주 핵심 키워드로 자동 생성
              ├─ HTML 뉴스레터 렌더링
              ├─ Gmail SMTP로 7명에게 발송
              ├─ 발송 실패 시 재시도
              └─ 결과: 발송 완료 상태

  08:00  팀원 7명에게 이메일 도착 + 사이트 업데이트 완료
```

---

## 4. 에이전트 상세 명세

### Agent 1: Orchestrator (지휘자)

**역할:** 전체 파이프라인의 실행 순서를 결정하고, 각 에이전트의 상태를 모니터링하며, 실패 시 복구 전략을 수립한다.

**부여 도구(Tools):**

| 도구명 | 기능 |
|--------|------|
| `get_pipeline_status()` | 현재 파이프라인 진행 상태 조회 |
| `trigger_agent(agent_name, params)` | 하위 에이전트 실행 트리거 |
| `read_agent_result(agent_name, run_id)` | 에이전트 실행 결과 조회 |
| `update_schedule(cron_expr)` | 스케줄 변경 |
| `send_admin_alert(message)` | 관리자에게 알림 발송 |
| `query_db(sql)` | DB 상태 조회 (읽기 전용) |

**조건부 라우팅 로직:**

```python
def route_after_crawling(state: PipelineState) -> str:
    """크롤링 후 분기 결정"""
    if state["crawl_status"] == "failed":
        if state["retry_count"] < 3:
            return "retry_crawling"          # 재시도
        else:
            return "alert_admin"             # 관리자 알림
    if len(state["raw_articles"]) < 20:
        return "expand_sources"              # 소스 확장 시도
    return "evaluate"                        # 정상 → 다음 단계

def route_after_translation(state: PipelineState) -> str:
    """번역 후 품질 기반 분기"""
    low_quality = [t for t in state["translation_quality"] if t["score"] < 0.7]
    if len(low_quality) > 5:
        return "retranslate"                 # 저품질 다수 → 재번역
    return "generate_insights"               # 정상 → 다음 단계

def route_after_insights(state: PipelineState) -> str:
    """인사이트 생성 후 분기"""
    if state["insight_status"] == "done":
        return "send_newsletter"             # 정상 → 발송
    return "retry_insights"                  # 재시도
```

**메모리:** 최근 10회 실행 이력, 각 소스별 성공/실패 통계, 평균 처리 시간

---

### Agent 2: Crawling Agent (수집가)

**역할:** 11개 빅테크 소스 + 4개 미디어에서 기사를 수집한다. 소스별 최적 전략을 자율적으로 판단하고 실행한다.

**부여 도구(Tools):**

| 도구명 | 기능 |
|--------|------|
| `fetch_url(url, method, headers)` | HTTP 요청 |
| `parse_html(html, selector)` | HTML 파싱 (BeautifulSoup 래퍼) |
| `parse_rss(feed_url)` | RSS 피드 파싱 |
| `render_page(url)` | 동적 페이지 렌더링 (Playwright) |
| `check_robots_txt(domain)` | robots.txt 확인 |
| `detect_duplicate(title, url)` | 중복 기사 감지 (DB 조회) |
| `save_raw_article(article_data)` | 원문 DB 저장 |
| `get_last_crawl_result(source)` | 이전 크롤링 결과 조회 |
| `get_source_config(source_name)` | 소스별 설정(셀렉터, 전략) 조회 |

**소스별 크롤링 전략 설정:**

```python
SOURCES = {
    "microsoft_ai": {
        "urls": [
            "https://microsoft.com/en-us/ai",
            "https://azure.microsoft.com/en-us/blog"
        ],
        "primary_strategy": "rss",
        "fallback_strategy": "html_parse",
        "selectors": {"title": "h2.entry-title", "body": "div.entry-content"},
        "company": "Microsoft",
        "source_type": "official_blog",
        "priority_score": 3
    },
    "google_ai": {
        "urls": ["https://blog.google/technology/ai"],
        "primary_strategy": "html_parse",
        "fallback_strategy": "rss",
        "selectors": {"title": "h3.headline", "body": "div.article-body"},
        "company": "Google",
        "source_type": "official_blog",
        "priority_score": 3
    },
    # ... 나머지 13개 소스
}
```

**에이전트적 행동 (핵심 차별점):**

1. **적응적 전략 전환**: HTML 파싱 실패 시 → RSS 시도 → 그래도 실패 시 → Playwright 렌더링 시도
2. **셀렉터 자동 조정**: 페이지 구조 변경 감지 시 대체 셀렉터 탐색
3. **수집량 자체 검증**: 평소 15개인 소스에서 2개만 수집되면 문제를 인식하고 재시도
4. **중복 판단**: `detect_duplicate()` 도구로 DB 조회 → 이미 수집된 기사 제외
5. **병렬 수집**: 독립적인 소스들을 동시에 수집하여 시간 단축

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

### Agent 3: Evaluation Agent (심사위원)

**역할:** 수집된 전체 기사(100~200개)에서 팀에게 가장 가치 있는 30개를 선별한다. 규칙 기반 필터와 AI 추론을 결합하되, **팀원 반응 데이터를 학습**하여 시간이 갈수록 선별 정확도가 향상된다.

**부여 도구(Tools):**

| 도구명 | 기능 |
|--------|------|
| `get_raw_articles(run_id)` | 수집된 원문 기사 목록 조회 |
| `check_keyword_match(article, keywords)` | 키워드 매칭 |
| `calculate_recency_score(published_date)` | 최신성 점수 계산 |
| `get_team_interests()` | 팀원들의 관심 분야/키워드 조회 |
| `get_historical_ratings()` | 과거 기사별 팀원 반응 통계 (스크랩 수, 댓글 수) |
| `get_company_weight(company)` | 기업별 가중치 조회 |
| `save_evaluation_result(article_id, score, reason)` | 평가 결과 저장 |

**3단계 선별 프로세스:**

```
전체 수집 기사 (100~200개, 제목 + 첫 단락)
        │
        ▼
  1단계: 규칙 기반 점수화 (도구 사용, AI 없이 즉시)
  ├─ check_keyword_match() → 키워드 점수
  ├─ calculate_recency_score() → 최신성 점수
  ├─ get_company_weight() → 기업 관련성 점수
  └─ 출처 점수 (공식블로그 3점 / Verge·TC 2점 / Wired·Ars 1점)
        │
        ▼
  상위 50개 추림
        │
        ▼
  2단계: AI 중요도 추론 (LLM 멀티스텝)
  ├─ 제목 + 요약을 분석하여 산업 영향력·기술 혁신성·팀 관련성 평가
  └─ 각 기사에 1~5점 중요도 + 판단 사유 첨부
        │
        ▼
  상위 40개
        │
        ▼
  3단계: 팀 선호도 반영 (도구 + 추론) ★ 에이전트만의 차별점
  ├─ get_historical_ratings() → 팀원들이 과거 높이 평가한 기사 패턴 분석
  ├─ get_team_interests() → 현재 팀 관심사 반영
  └─ 최종 30개 확정 + 선정 사유
        │
        ▼
  최종 30개 (선정 사유 포함)
```

**1단계 규칙 기반 점수화 기준:**

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

| 기업 그룹 | 기본 점수 | 이유 |
|-----------|----------|------|
| OpenAI, Anthropic, Google, Microsoft, Nvidia | +2점 | 파트너십 팀 핵심 관심사 |
| Meta, Amazon, Apple | +1점 | 중간 관심도 |
| Tesla, Mistral AI, Perplexity | +0점 | 참고 수준 |

D. 최신성 점수

| 발행 시점 | 점수 |
|-----------|------|
| 24시간 이내 | +2점 |
| 24~48시간 | +1점 |
| 48시간 이상 | +0점 |

**3단계 팀 선호도 학습 예시:**
```
에이전트 분석: "지난 4주간 팀원 스크랩 패턴 분석 결과:
  - 'partnership', 'pricing' 키워드 기사 스크랩률 78%
  - 'research paper' 키워드 기사 스크랩률 23%
  - Physical AI 카테고리 댓글 참여율이 일반 대비 2.3배
  → 이번 선별에서 파트너십·가격 관련 기사와 Physical AI 기사의 가중치를 상향"
```

**최종 30개 구성 예시:**

| 중요도 | 기사 수 | 해당 기준 |
|--------|---------|-----------|
| 5점 | 5~8개 | 제품 런칭, M&A, 대형 발표, 주요 규제 |
| 4점 | 10~12개 | 기능 업데이트, 투자 유치, CEO 발언 |
| 3점 | 10~13개 | 기술 블로그, 업계 리포트 |

---

### Agent 4: Translation Agent (번역가)

**역할:** 선별된 30개 기사를 한국어로 번역하되, **자체 품질 검증 루프**를 통해 오역·누락을 감지하고, **기술 용어 사전(glossary)**을 자율적으로 관리하여 번역 일관성을 유지한다.

**부여 도구(Tools):**

| 도구명 | 기능 |
|--------|------|
| `get_articles_to_translate(run_id)` | 번역 대상 기사 조회 |
| `get_glossary()` | 기술 용어 사전 조회 |
| `update_glossary(term, translation)` | 용어 사전 업데이트 |
| `get_previous_translation(term)` | 동일 용어의 과거 번역 조회 |
| `save_translation(article_id, title_ko, body_ko, quality_score)` | 번역 결과 저장 |

**자체 품질 검증 루프 (핵심 차별점):**

```
번역 수행
    │
    ▼
원문과 대조 검증
├─ 핵심 숫자/날짜가 누락되지 않았는가?
├─ 고유명사(기업명, 제품명)가 정확한가?
├─ 문장 수가 원문과 크게 다르지 않은가? (누락 감지)
├─ 기술 용어가 glossary와 일치하는가?
    │
    ├─ 문제 없음 → 저장 (품질 점수 부여)
    └─ 문제 발견 → 해당 부분만 재번역 → 재검증
```

**번역 품질 기준:**

| 항목 | 내용 |
|------|------|
| 번역 범위 | 제목 + 본문 전체 |
| 원문 보존 | 원문과 번역본 모두 저장 및 노출 |
| 번역 품질 기준 | 자연스러운 의역 수준 |
| 고유명사 처리 | 기업명·제품명·기술 용어는 원어 유지 또는 병기 |
| 예시 | "GPT-5 model weights" → "GPT-5 모델 가중치(model weights)" |

**용어 사전(glossary) 자동 관리:**
```
에이전트: "이번 기사에서 'agentic AI'라는 용어가 새로 등장했다.
  → get_previous_translation('agentic AI') → 기존 번역 없음
  → 문맥상 '에이전트형 AI'가 적절하다고 판단
  → update_glossary('agentic AI', '에이전트형 AI(agentic AI)')
  → 이후 모든 기사에서 동일하게 번역"
```

---

### Agent 5: Insight Agent (분석가)

**역할:** 번역된 기사들을 **교차 분석**하여 단순 요약을 넘어선 트렌드 인사이트를 생성한다. 기사 간 관계, 산업 흐름, 과거 트렌드 대비 변화를 도출한다.

**부여 도구(Tools):**

| 도구명 | 기능 |
|--------|------|
| `get_translated_articles(run_id)` | 번역 완료된 기사 조회 |
| `get_past_insights(weeks=4)` | 최근 4주간 인사이트 조회 |
| `search_related_articles(keyword)` | 과거 기사에서 관련 기사 검색 |
| `get_company_timeline(company)` | 특정 기업의 최근 동향 타임라인 |
| `save_insight(insight_data)` | 인사이트 저장 |
| `save_weekly_report(report_data)` | 주간 리포트 저장 |

**생성하는 결과물:**

**A. 기사별 인사이트 (30개)**

| 항목 | 설명 | 예시 |
|------|------|------|
| 핵심 요약 | 기사의 핵심을 2~3문장으로 압축 | "OpenAI가 GPT-5를 발표하며 멀티모달 처리 속도를 3배 향상시켰다." |
| 파트너십 관련성 | 우리 팀 업무와의 직접적 연관성 | "API 파트너사에 새로운 가격 정책 적용 예정 — 계약 재검토 필요" |
| 경쟁사 영향 | 타 기업에 미치는 영향 분석 | "Google Gemini와의 성능 비교에서 우위 주장 → 경쟁 구도 변화" |
| 시장 시그널 | 업계 트렌드 방향성 | "에지 AI 시장 확대 신호 — 온디바이스 모델 수요 증가 예상" |
| 현실 세계 적용 가능성 | *(Physical AI 기사만)* 하드웨어·물리 세계 적용 관점 | "Optimus Gen-3 공개 — 산업 현장 도입 2027년으로 앞당겨질 가능성" |
| 액션 아이템 | *(선택)* 팀 차원에서 검토할 사항 | "Anthropic 새 약관 검토 후 파트너십 계약 반영 여부 확인 필요" |

**B. 주간 트렌드 리포트 (1개) ★ 에이전트만의 차별점**

```
에이전트 멀티스텝 추론:
  1. 30개 기사를 읽고 주제별로 클러스터링
  2. 각 클러스터에서 핵심 트렌드 추출
  3. get_past_insights(weeks=4) → 지난 4주 트렌드와 비교
  4. "지난주 대비 새로 부상한 주제"와 "지속 중인 트렌드" 분류
  5. get_company_timeline('OpenAI') → 기업별 동향 맥락 파악
  6. search_related_articles('pricing') → 과거 가격 관련 기사와 연결
  7. 최종 주간 트렌드 리포트 작성
```

**주간 리포트 구조:**
```json
{
  "week": "2026-W13",
  "top_trends": [
    {
      "trend": "에이전트형 AI 경쟁 본격화",
      "description": "OpenAI, Google, Anthropic 3사가 동시에 에이전트 기능을 강화...",
      "related_articles": ["article_id_1", "article_id_5", "article_id_12"],
      "vs_last_week": "신규 부상"
    },
    {
      "trend": "Physical AI 투자 급증",
      "description": "Nvidia와 Tesla의 로보틱스 투자가 지속적으로 확대...",
      "related_articles": ["article_id_3", "article_id_8"],
      "vs_last_week": "3주 연속 지속"
    }
  ],
  "cross_analysis": [
    "Google의 Gemini 2.0 발표와 OpenAI의 GPT-5 발표가 같은 주에 이루어진 것은 직접적 경쟁 신호"
  ]
}
```

**C. 교차 분석 (해당 시)**
- "Google이 발표한 X와 OpenAI의 Y는 동일한 방향을 가리킨다"
- "Nvidia의 칩 발표와 Microsoft의 Azure 업데이트는 연관된 전략"

**AI 응답 스키마:**
```json
{
  "title_ko": "번역된 제목",
  "body_ko": "번역된 본문 전체",
  "importance_score": 4,
  "evaluation_reason": "선정 사유 (에이전트가 생성)",
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

### Agent 6: Newsletter Agent (편집장)

**역할:** 최종 뉴스레터를 구성하고 팀원에게 발송한다. 팀원별 관심 분야에 따라 기사 순서를 **개인화**한다.

**부여 도구(Tools):**

| 도구명 | 기능 |
|--------|------|
| `get_insights(run_id)` | 인사이트 조회 |
| `get_translated_articles(run_id)` | 번역된 기사 조회 |
| `get_weekly_report(run_id)` | 주간 리포트 조회 |
| `get_team_preferences()` | 팀원별 관심 분야/이메일 수신 설정 조회 |
| `render_newsletter_html(template, data)` | HTML 뉴스레터 렌더링 |
| `send_email(to, subject, html_body)` | Gmail SMTP 이메일 발송 |
| `save_newsletter(newsletter_data)` | 뉴스레터 DB 저장 |

**개인화 로직:**
```
에이전트: "팀원 A는 'Physical AI' 카테고리를 많이 스크랩했다.
  → A에게 보내는 뉴스레터에서는 Physical AI 기사를 상단에 배치.
  팀원 B는 'OpenAI', 'Anthropic' 기사에 댓글을 많이 달았다.
  → B에게는 모델/API 관련 기사를 상단에 배치."
```

**뉴스레터 구성:**

| 기능 | 상세 |
|------|------|
| 발송 시각 | 매주 **월·목 오전 8시** |
| 이메일 형식 | 주간 트렌드 리포트 요약 / 중요도 5점 기사 하이라이트 / 전체 30개 기사 목록 / 사이트 바로가기 |
| 제목 | 이번 주 핵심 키워드로 자동 생성 (예: "[ITTF] 에이전트 AI 경쟁·Physical AI 투자 — 3/29") |
| 수신 설정 | 개인별 이메일 수신 ON/OFF 가능 |
| 발송 방식 | Gmail SMTP (무료, 일 500통 한도) |
| 발송 실패 | 재시도 최대 3회, 최종 실패 시 관리자 알림 |

---

## 5. 공유 파이프라인 상태 (PipelineState)

모든 에이전트가 공유하는 상태 스키마 — LangGraph의 핵심 개념:

```python
from typing import TypedDict, List, Optional

class PipelineState(TypedDict):
    # 실행 메타데이터
    run_id: str
    triggered_at: str
    trigger_type: str                    # "scheduled" | "manual"

    # Crawling Agent 결과
    raw_articles: List[dict]             # 수집된 전체 기사
    crawl_errors: List[dict]             # 크롤링 실패 소스 + 사유
    crawl_status: str                    # "pending" | "running" | "done" | "failed"

    # Evaluation Agent 결과
    selected_articles: List[dict]        # 선별된 30개
    evaluation_reasons: List[dict]       # 선정/탈락 사유
    eval_status: str

    # Translation Agent 결과
    translated_articles: List[dict]      # 번역 완료 기사
    translation_quality: List[dict]      # 품질 점수
    glossary_updates: List[dict]         # 신규 추가된 용어
    trans_status: str

    # Insight Agent 결과
    article_insights: List[dict]         # 기사별 인사이트
    weekly_report: Optional[dict]        # 주간 트렌드 리포트
    insight_status: str

    # Newsletter Agent 결과
    newsletter_html: Optional[str]
    send_results: List[dict]             # 팀원별 발송 결과
    newsletter_status: str

    # Orchestrator 메타데이터
    retry_count: int
    error_log: List[str]
    total_elapsed_time: float            # 전체 소요 시간 (초)
```

**체크포인팅:** LangGraph의 SQLite 체크포인터를 사용하여 각 단계 완료 시 상태를 저장한다. 중간에 실패해도 해당 단계부터 재개 가능.

---

## 6. 팀 공유 플랫폼 (프라이빗 사이트)

> 프론트엔드·인증·댓글·스크랩 기능은 v1.4 기획안과 동일. 에이전트 아키텍처 전환으로 **변경·추가된 부분만** 기술.

### F3-1. 접근 제어 (보안) — 변경 없음

| 항목 | 내용 |
|------|------|
| 로그인 방식 | **Google 계정 로그인만 지원** (이메일/비밀번호 없음) |
| 초대 방식 | 관리자가 Google 계정 이메일로 초대 → 수락 시 접근 가능 |
| 외부 노출 | 완전 비공개, 검색엔진 미노출 |

**Google OAuth 인증 플로우:**
```
1. 사용자가 [Google로 로그인] 클릭
2. Google OAuth 2.0 동의 화면으로 리다이렉트
3. Google이 NextAuth 콜백 URL로 authorization code 전달
4. NextAuth가 Google에서 access_token + 사용자 정보 수령
5. NextAuth가 해당 이메일이 users 테이블에 있는지 확인
   ├── 있음 (is_active=true): 로그인 허용, JWT 세션 발급
   ├── 있음 (is_active=false): 접근 차단 페이지로 이동
   └── 없음: "초대받지 않은 계정입니다" 페이지로 이동
6. 이후 모든 API 요청 시 JWT 토큰을 Authorization 헤더에 포함
```

### F3-2. 메인 피드 (홈 화면) — 변경 없음

- **최신순 / 중요도순** 정렬 토글
- 기업별 필터, 카테고리 필터, 소스별 필터
- 읽음/안읽음 표시
- 각 카드에 표시되는 정보: 기업 로고 + 기업명, 기사 제목 (한국어), 카테고리 태그, 수집 날짜, 중요도 점수, 댓글 수, 출처명

### F3-3. 기사 상세 페이지 — **선정 사유 추가**

```
┌─────────────────────────────────────────┐
│ [기업 로고] OpenAI | techcrunch.com      │
│ 발행: 2026.03.19 | 수집: 2026.03.21     │
│ 태그: #AI모델 #제품런칭                  │
├─────────────────────────────────────────┤
│ 제목 (한국어 번역)                       │
│ 제목 (원문 영어)          [📌 스크랩]    │
├─────────────────────────────────────────┤
│ 🤖 왜 이 기사가 선정되었나? ★ NEW       │
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

### F3-4~F3-5. 댓글 & 스크랩 — 변경 없음

(v1.4 기획안과 동일. 댓글/대댓글/멘션/이모지 반응/스크랩/메모 기능 그대로 유지.)

### F3-6. 주간 트렌드 리포트 페이지 ★ NEW

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
│ 📈 지난주 대비 변화                      │
│ • "에이전트 AI" 키워드 언급 +240%        │
│ • "온디바이스 모델" 키워드 신규 등장      │
├─────────────────────────────────────────┤
│ 🔗 교차 분석                             │
│ "Google의 Gemini 2.0과 OpenAI의 GPT-5   │
│  발표가 같은 주에 이루어진 것은 직접적    │
│  경쟁 신호로 해석된다."                  │
└─────────────────────────────────────────┘
```

### F3-7. 관리자 기능 — **에이전트 모니터링 추가**

| 기능 | 상세 |
|------|------|
| 팀원 관리 | Google 계정 초대(최대 6명), 권한 설정, 계정 비활성화 |
| 수동 크롤링 | 즉시 에이전트 파이프라인 실행 버튼 |
| 기사 관리 | 부적절 기사 삭제, 중요도 수동 수정 |
| 소스 관리 | 크롤링 소스 URL 추가/제거 |
| 키워드 관리 | 필터링 키워드 추가/제거 |
| 기업 가중치 설정 | 우선순위 점수화 시 기업별 가중치 조정 |
| **에이전트 상태 대시보드** ★ NEW | 각 에이전트 실행 상태, 소요 시간, 에러 로그 실시간 확인 |
| **파이프라인 이력** ★ NEW | 최근 10회 실행 이력, 소스별 성공/실패 통계 |
| **용어 사전 관리** ★ NEW | Translation Agent가 자동 추가한 용어 확인/수정/삭제 |

**에이전트 상태 대시보드 화면:**
```
┌─────────────────────────────────────────┐
│ 🤖 에이전트 파이프라인 상태              │
│ 실행 ID: run_20260329_0700              │
│ 시작: 07:00 | 현재: 07:35               │
├─────────────────────────────────────────┤
│ ✅ Crawling Agent     07:00~07:12  완료  │
│    수집: 143개 / 실패 소스: 1개 (Tesla)  │
│                                         │
│ ✅ Evaluation Agent   07:12~07:18  완료  │
│    선별: 30개 / 탈락: 113개              │
│                                         │
│ 🔄 Translation Agent  07:18~      진행중 │
│    완료: 18/30개 (60%)                   │
│    재번역: 2개 (품질 미달)                │
│                                         │
│ ⏳ Insight Agent      대기중              │
│ ⏳ Newsletter Agent   대기중              │
├─────────────────────────────────────────┤
│ 예상 완료: 07:48 (08:00 발송 예정)       │
└─────────────────────────────────────────┘
```

---

## 7. 데이터베이스 스키마

> v1.4 기획안의 테이블을 유지하되, 에이전트 관련 테이블을 추가.

```sql
-- ============================================
-- 기존 테이블 (v1.4 유지)
-- ============================================

-- 사용자
CREATE TABLE users (
  id            TEXT PRIMARY KEY,
  email         TEXT UNIQUE,
  name          TEXT,
  profile_image TEXT,
  role          TEXT DEFAULT 'member',    -- 'admin' or 'member'
  is_active     INTEGER DEFAULT 1,
  email_notify  INTEGER DEFAULT 1,
  created_at    TEXT
);

-- 기사
CREATE TABLE articles (
  id               TEXT PRIMARY KEY,
  title_en         TEXT,
  title_ko         TEXT,
  body_en          TEXT,
  body_ko          TEXT,
  url              TEXT UNIQUE,
  source_name      TEXT,
  source_type      TEXT,                  -- 'official_blog' or 'media'
  company_tags     TEXT,                  -- JSON: '["OpenAI","Microsoft"]'
  category_tags    TEXT,                  -- JSON: '["AI Model","Physical AI"]'
  importance_score INTEGER,               -- 1~5
  evaluation_reason TEXT,                 -- ★ NEW: 선정 사유
  insights         TEXT,                  -- JSON 구조화
  published_at     TEXT,
  crawled_at       TEXT,
  expires_at       TEXT
);

-- 댓글
CREATE TABLE comments (
  id         TEXT PRIMARY KEY,
  article_id TEXT REFERENCES articles,
  user_id    TEXT REFERENCES users,
  parent_id  TEXT REFERENCES comments,
  body       TEXT,
  created_at TEXT,
  updated_at TEXT
);

-- 이모지 반응
CREATE TABLE reactions (
  id         TEXT PRIMARY KEY,
  comment_id TEXT REFERENCES comments,
  user_id    TEXT REFERENCES users,
  emoji      TEXT,
  UNIQUE(comment_id, user_id, emoji)
);

-- 스크랩
CREATE TABLE scrapbook (
  id         TEXT PRIMARY KEY,
  user_id    TEXT REFERENCES users,
  article_id TEXT REFERENCES articles,
  memo       TEXT,
  created_at TEXT,
  UNIQUE(user_id, article_id)
);

-- ============================================
-- 에이전트 관련 테이블 (v2.0 신규)
-- ============================================

-- 파이프라인 실행 이력
CREATE TABLE pipeline_runs (
  id               TEXT PRIMARY KEY,
  triggered_at     TEXT,
  trigger_type     TEXT,                  -- 'scheduled' or 'manual'
  status           TEXT,                  -- 'running' | 'completed' | 'failed'
  total_crawled    INTEGER,
  total_selected   INTEGER,
  total_translated INTEGER,
  errors           TEXT,                  -- JSON: 에러 로그
  completed_at     TEXT,
  elapsed_seconds  REAL
);

-- 에이전트별 실행 로그
CREATE TABLE agent_logs (
  id           TEXT PRIMARY KEY,
  run_id       TEXT REFERENCES pipeline_runs,
  agent_name   TEXT,                      -- 'crawling' | 'evaluation' | 'translation' | 'insight' | 'newsletter'
  status       TEXT,                      -- 'running' | 'completed' | 'failed' | 'retrying'
  started_at   TEXT,
  completed_at TEXT,
  input_count  INTEGER,                   -- 입력 기사 수
  output_count INTEGER,                   -- 출력 기사 수
  retries      INTEGER DEFAULT 0,
  error_detail TEXT,
  metadata     TEXT                       -- JSON: 에이전트별 추가 정보
);

-- 기술 용어 사전 (Translation Agent 관리)
CREATE TABLE glossary (
  id             TEXT PRIMARY KEY,
  term_en        TEXT UNIQUE,             -- 원문 용어
  term_ko        TEXT,                    -- 한국어 번역
  added_by       TEXT,                    -- 'agent' or 'admin'
  first_seen_in  TEXT REFERENCES articles,-- 처음 발견된 기사
  created_at     TEXT,
  updated_at     TEXT
);

-- 주간 트렌드 리포트
CREATE TABLE weekly_reports (
  id          TEXT PRIMARY KEY,
  run_id      TEXT REFERENCES pipeline_runs,
  week_label  TEXT,                       -- '2026-W13'
  report_data TEXT,                       -- JSON: 트렌드, 교차분석 등
  created_at  TEXT
);

-- 소스별 크롤링 통계 (Crawling Agent 학습용)
CREATE TABLE source_stats (
  id              TEXT PRIMARY KEY,
  source_name     TEXT,
  run_id          TEXT REFERENCES pipeline_runs,
  strategy_used   TEXT,                   -- 'html_parse' | 'rss' | 'playwright'
  success         INTEGER,                -- 1 or 0
  articles_found  INTEGER,
  error_detail    TEXT,
  elapsed_seconds REAL,
  crawled_at      TEXT
);
```

### 기사 보관 정책 — 변경 없음

| 항목 | 내용 |
|------|------|
| 보관 기간 | **3개월** |
| 초기화 방식 | 3개월 경과 시 자동 삭제 (개인 스크랩 기사는 예외 보존) |
| 초기화 주기 | 분기 1회 (1월·4월·7월·10월 1일) |

---

## 8. 기술 스택 상세 명세

### 전체 아키텍처 구조

```
[팀원 브라우저] ── 인터넷 ──▶ Cloudflare Tunnel (무료)
                                      │
                          [본인 노트북 (월·목 07:00 켜둠)]
                                      │
               ┌──────────────────────┼──────────────────────┐
               │                      │                      │
         Next.js (프론트)       FastAPI (백엔드)        Ollama (AI)
                                      │                 (로컬 LLM)
                                      │
                              ┌───────┴───────┐
                              │               │
                          SQLite (DB)    LangGraph
                                         (에이전트 엔진)
                                              │
                                    ┌─────────┼─────────┐
                                    │         │         │
                               Crawling  Evaluation  Translation
                               Agent     Agent       Agent
                                    │         │         │
                                    └─────────┼─────────┘
                                              │
                                    ┌─────────┼─────────┐
                                    │                   │
                                 Insight           Newsletter
                                 Agent              Agent
```

### 기존 대비 변경 요약

| 항목 | v1.4 (단순 LLM) | v2.0 (에이전트) |
|------|-----------------|----------------|
| AI 처리 | Ollama 단순 호출 | **LangGraph + Ollama** (에이전트 프레임워크) |
| 크롤링 | 하드코딩된 스크립트 | **Crawling Agent** (적응적 전략) |
| 선별 | 규칙함수 + Ollama 호출 | **Evaluation Agent** (팀 선호도 학습) |
| 번역 | Ollama 단순 호출 | **Translation Agent** (자체 검증 + 용어사전) |
| 인사이트 | Ollama 단순 호출 | **Insight Agent** (교차분석 + 주간리포트) |
| 이메일 | 단순 발송 스크립트 | **Newsletter Agent** (개인화) |
| 오류 처리 | try/except | **Orchestrator 조건부 라우팅** (자동 복구) |
| 중간 상태 | 없음 | **LangGraph 체크포인터** (재개 가능) |
| 서버 | 본인 노트북 | 본인 노트북 (변경 없음) |
| DB | SQLite | SQLite + 에이전트 테이블 추가 |
| 비용 | $0 | **$0** (변경 없음) |

### 1. 프론트엔드 — 변경 없음

| 항목 | 선택 | 이유 |
|------|------|------|
| 프레임워크 | **Next.js 14 (App Router)** | SSR로 초기 로딩 빠름 |
| 언어 | **TypeScript** | 타입 안정성 |
| 스타일링 | **Tailwind CSS** | 빠른 UI 개발 |
| 상태 관리 | **Zustand** | 가볍고 간단 |
| 서버 상태 | **TanStack Query** | API 캐싱, 리패칭 자동 처리 |
| 인증 | **NextAuth.js v5** | Google OAuth 2.0 단독 |
| 컴포넌트 | **shadcn/ui** | Tailwind 기반 UI |
| 아이콘 | **Lucide React** | shadcn/ui와 통일성 |

**페이지 라우팅 구조:**
```
app/
├── (auth)/
│   └── login/                → Google 로그인 페이지
├── (main)/
│   ├── page.tsx              → 메인 피드 (홈)
│   ├── articles/
│   │   └── [id]/page.tsx     → 기사 상세
│   ├── trends/
│   │   └── page.tsx          → 주간 트렌드 리포트 ★ NEW
│   ├── scrapbook/
│   │   └── page.tsx          → 개인 스크랩 공간
│   └── admin/
│       ├── page.tsx          → 관리자 페이지
│       ├── agents/
│       │   └── page.tsx      → 에이전트 모니터링 ★ NEW
│       └── glossary/
│           └── page.tsx      → 용어 사전 관리 ★ NEW
└── api/
    └── auth/[...nextauth]/   → NextAuth 핸들러
```

### 2. 백엔드 — **LangGraph 추가**

| 항목 | 선택 | 이유 |
|------|------|------|
| 프레임워크 | **FastAPI (Python 3.11+)** | 비동기 처리, Swagger 자동 문서화 |
| 에이전트 엔진 | **LangGraph** ★ NEW | 상태 그래프 기반 에이전트 오케스트레이션 |
| LLM 연동 | **langchain-ollama (ChatOllama)** ★ NEW | Ollama 로컬 모델과 LangGraph 연결 |
| 인증 | **Google OAuth 2.0 + JWT** | NextAuth 토큰 검증 |
| ORM | **SQLAlchemy 2.0 (async)** | 비동기 DB 쿼리 |
| DB 마이그레이션 | **Alembic** | 스키마 버전 관리 |
| 이메일 | **Gmail SMTP** (smtplib) | 무료 |
| 스케줄러 | **APScheduler** | Orchestrator Agent 트리거 |
| 환경변수 | **python-dotenv** | 환경별 설정 분리 |

**왜 LangGraph인가?**

| 프레임워크 | 장점 | 단점 | 비용 | 판정 |
|-----------|------|------|------|------|
| **LangGraph** | 상태 관리 우수, Ollama 네이티브 지원, 체크포인팅, 조건부 라우팅 | 학습 곡선 | 무료 (OSS) | ✅ 선택 |
| CrewAI | 직관적 API | Ollama 지원 불안정, 상태 관리 약함 | 무료 (OSS) | ❌ |
| Claude Agent SDK | 강력한 도구 사용 | Claude API 필수 (유료) | 유료 | ❌ 비용 제약 |
| AutoGen | 멀티에이전트 대화 | 복잡한 설정, 오버스펙 | 무료 (OSS) | ❌ |

**API 엔드포인트 구조:**
```
# 기사
GET    /api/articles               → 기사 목록 (필터·정렬)
GET    /api/articles/{id}          → 기사 상세
GET    /api/articles/{id}/comments → 기사 댓글 목록

# 댓글
POST   /api/articles/{id}/comments → 댓글 작성
PATCH  /api/comments/{id}          → 댓글 수정
DELETE /api/comments/{id}          → 댓글 삭제
POST   /api/comments/{id}/reaction → 이모지 반응

# 스크랩
GET    /api/scrapbook               → 내 스크랩 목록
POST   /api/scrapbook               → 스크랩 추가
PATCH  /api/scrapbook/{id}          → 메모 수정
DELETE /api/scrapbook/{id}          → 스크랩 해제

# 주간 트렌드 ★ NEW
GET    /api/trends/weekly           → 최신 주간 리포트
GET    /api/trends/weekly/{week}    → 특정 주차 리포트

# 관리자
POST   /api/admin/crawl             → 수동 에이전트 파이프라인 실행
GET    /api/admin/users             → 팀원 목록
POST   /api/admin/invite            → 초대 이메일 발송
DELETE /api/admin/users/{id}        → 팀원 접근 차단
PATCH  /api/admin/articles/{id}     → 중요도 수동 수정
DELETE /api/admin/articles/{id}     → 기사 삭제

# 에이전트 모니터링 ★ NEW
GET    /api/admin/pipeline/status   → 현재 실행 상태
GET    /api/admin/pipeline/history  → 최근 10회 실행 이력
GET    /api/admin/agents/{name}/logs → 에이전트별 실행 로그

# 용어 사전 ★ NEW
GET    /api/admin/glossary          → 용어 사전 목록
PATCH  /api/admin/glossary/{id}     → 용어 수정
DELETE /api/admin/glossary/{id}     → 용어 삭제
```

### 3. AI 처리 (Ollama + LangGraph)

| 항목 | 선택 |
|------|------|
| 엔진 | **Ollama** (로컬 설치, API 비용 없음) |
| 연동 | **ChatOllama** (LangChain 래퍼 → LangGraph에서 사용) |

**노트북 RAM별 추천 모델:**

| 노트북 RAM | 추천 모델 | 용량 | 에이전트 추론 품질 |
|-----------|-----------|------|-------------------|
| 32GB 이상 | **gemma3:27b** | 17GB | ★★★★★ |
| 16GB | **gemma3:12b** | 8GB | ★★★★☆ |
| 8GB | **llama3.1:8b** | 5GB | ★★★☆☆ |

**에이전트별 모델 배정:**

| 에이전트 | 추천 모델 | 이유 |
|----------|-----------|------|
| Orchestrator | llama3.1:8b | 판단·분기 결정에 가벼운 모델 충분 |
| Crawling | (LLM 미사용) | 도구 기반 작업, LLM 추론 불필요 |
| Evaluation | gemma3:12b | 중요도 판단에 높은 추론 능력 필요 |
| Translation | gemma3:12b | 한국어 번역 품질 중시 |
| Insight | gemma3:12b | 교차 분석에 높은 추론 능력 필요 |
| Newsletter | llama3.1:8b | 구성·포맷팅에 가벼운 모델 충분 |

**대안: 무료 클라우드 API (Ollama 품질이 아쉬울 경우)**

| 서비스 | 무료 한도 | 품질 |
|--------|-----------|------|
| **Google Gemini API** | 1일 1,500건 요청 무료 | ★★★★☆ |
| **Groq API** | 분당 30건, 월 수백만 토큰 무료 | ★★★★☆ (속도 매우 빠름) |

> 월·목 주 2회 × 30개 기사 × 에이전트 4~5개 = 월 약 500~600 호출 → 무료 한도 내 충분

### 4. 외부 접속 / 이메일 — 변경 없음

| 항목 | 내용 |
|------|------|
| 외부 접속 | **Cloudflare Tunnel** (`cloudflared`), 완전 무료 |
| 이메일 | **Gmail SMTP** (smtplib), 무료, 하루 500통 한도 |

---

## 9. 프로젝트 디렉토리 구조

```
ITTF/
├── backend/
│   ├── main.py                        # FastAPI 엔트리포인트
│   ├── config.py                      # 설정 (소스 목록, 스케줄, 모델 등)
│   ├── requirements.txt
│   │
│   ├── database/
│   │   ├── connection.py              # SQLite 연결
│   │   ├── models.py                  # SQLAlchemy 모델
│   │   └── migrations/                # Alembic 마이그레이션
│   │
│   ├── agents/                        # ★ 에이전트 핵심 디렉토리
│   │   ├── __init__.py
│   │   ├── state.py                   # PipelineState 정의
│   │   ├── graph.py                   # LangGraph 그래프 정의 (워크플로우 핵심)
│   │   ├── orchestrator.py            # Orchestrator Agent 노드
│   │   ├── crawler.py                 # Crawling Agent 노드
│   │   ├── evaluator.py              # Evaluation Agent 노드
│   │   ├── translator.py             # Translation Agent 노드
│   │   ├── insight_generator.py      # Insight Agent 노드
│   │   └── newsletter.py             # Newsletter Agent 노드
│   │
│   ├── tools/                         # ★ 에이전트 도구 디렉토리
│   │   ├── __init__.py
│   │   ├── web_tools.py              # fetch_url, parse_html, parse_rss, render_page
│   │   ├── db_tools.py               # DB CRUD 도구
│   │   ├── email_tools.py            # Gmail SMTP 발송
│   │   ├── glossary_tools.py         # 용어 사전 관리
│   │   └── search_tools.py           # 기사 검색, 중복 감지
│   │
│   ├── scheduler/
│   │   └── jobs.py                   # APScheduler (월·목 07:00)
│   │
│   └── api/
│       ├── deps.py                   # 의존성 주입
│       └── routes/
│           ├── articles.py
│           ├── comments.py
│           ├── scraps.py
│           ├── trends.py             # ★ NEW: 주간 트렌드
│           ├── admin.py
│           ├── pipeline.py           # ★ NEW: 에이전트 모니터링
│           └── glossary.py           # ★ NEW: 용어 사전
│
├── frontend/
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── app/                      # Next.js App Router
│       ├── components/
│       │   ├── ui/                   # shadcn/ui 컴포넌트
│       │   ├── feed/                 # 메인 피드 컴포넌트
│       │   ├── article/              # 기사 상세 컴포넌트
│       │   ├── trends/               # ★ NEW: 주간 트렌드 컴포넌트
│       │   ├── admin/                # 관리자 컴포넌트
│       │   └── agents/               # ★ NEW: 에이전트 모니터링 컴포넌트
│       └── lib/
│           ├── api.ts                # API 클라이언트
│           ├── auth.ts               # NextAuth 설정
│           └── store.ts              # Zustand 스토어
│
├── data/
│   └── ittf.db                       # SQLite 데이터베이스 파일
│
├── .env.example                      # 환경변수 템플릿
├── docker-compose.yml                # Ollama + backend + frontend
├── CLAUDE.md
└── README.md
```

---

## 10. 사용자 시나리오 (User Flow)

### 시나리오 A: 정기 수집 후 팀원 확인

```
월·목 07:00  Orchestrator Agent 실행
             ├─ Crawling Agent: 15개 소스 병렬 수집 (143개 기사)
             │  └─ Tesla Blog 403 에러 → RSS로 전략 전환 → 성공
             ├─ Evaluation Agent: 143개 → 30개 선별 (선정 사유 포함)
             │  └─ 팀원 스크랩 패턴 분석 → Physical AI 가중치 상향
             ├─ Translation Agent: 30개 번역 + 품질 검증
             │  └─ "agentic AI" 신규 용어 → 용어 사전 자동 추가
             ├─ Insight Agent: 기사별 인사이트 + 주간 트렌드 리포트
             │  └─ "에이전트 AI 경쟁 본격화" 신규 트렌드 감지
             └─ Newsletter Agent: 팀원별 개인화 뉴스레터 구성

08:00  팀원 7명에게 이메일 도착
       └─ 팀원 A는 Physical AI 기사가 상단에, 팀원 B는 모델 기사가 상단에

팀원   이메일 클릭 → Google 로그인 → 메인 피드 진입
       "왜 이 기사가 선정되었나?" 확인 → 인사이트 열람
       주간 트렌드 리포트 페이지 확인
       댓글로 의견 공유 or 📌 스크랩 저장
```

### 시나리오 B: 에이전트 자동 복구

```
07:00  Crawling Agent: Google Blog에서 403 에러 3회
       → Orchestrator 판단: "지난주에도 실패 이력 있음"
       → Crawling Agent에 RSS 전략 전환 지시
       → RSS로 수집 성공
       → source_stats 테이블에 전략 변경 기록
       → 다음 실행부터 Google Blog는 RSS 우선 사용

07:30  Translation Agent: 5개 기사 품질 점수 0.6 미만
       → Orchestrator 판단: "저품질 5개 이상 → 재번역"
       → Translation Agent에 해당 5개만 재번역 지시
       → 재번역 후 품질 0.8 이상 → 정상 진행
```

### 시나리오 C: 관리자 모니터링

```
관리자  관리자 페이지 → 에이전트 상태 대시보드 접속
       현재 실행 상태 확인: Translation Agent 진행중 (60%)
       이전 10회 실행 이력: 평균 소요 48분, 실패 0회
       Tesla Blog 크롤링 통계: 최근 3회 RSS 전략 사용 (HTML 파싱 실패 후 자동 전환)
       용어 사전: 이번 주 자동 추가 3개 → 확인 후 1개 수정
```

---

## 11. 예상 월 운영 비용

| 항목 | 서비스 | 월 비용 |
|------|--------|---------|
| AI 엔진 | Ollama (로컬) + LangGraph (OSS) | **$0** |
| 서버 호스팅 | 본인 노트북 | **$0** |
| 외부 접속 | Cloudflare Tunnel | **$0** |
| 데이터베이스 | SQLite (로컬 파일) | **$0** |
| 이메일 발송 | Gmail SMTP | **$0** |
| 프론트엔드 | Next.js (로컬 실행) | **$0** |
| **월 합계** | | **$0** |

---

## 12. 개발 우선순위 (MVP → Full)

### Phase 1 — 에이전트 기반 구축 (MVP)

- [ ] LangGraph 설치 및 ChatOllama 연동 확인
- [ ] PipelineState 정의, 기본 그래프 구조 생성 (`agents/state.py`, `agents/graph.py`)
- [ ] SQLite DB 스키마 생성 (기존 + 에이전트 테이블)
- [ ] Crawling Agent 구현 (11개 공식 블로그 + 4개 미디어, 적응적 전략)
- [ ] Evaluation Agent 구현 (3단계 선별: 규칙 → AI → 팀 선호도)
- [ ] Translation Agent 구현 (자체 검증 루프 + 용어 사전)
- [ ] Orchestrator Agent 구현 (조건부 라우팅, 에러 복구)
- [ ] Google 로그인 단독 연동 (NextAuth + Google OAuth 2.0)
- [ ] 기본 피드 페이지 (목록 + 상세, 선정 사유 표시)
- [ ] APScheduler → Orchestrator 트리거 (월·목 07:00)
- [ ] Cloudflare Tunnel 설정

### Phase 2 — 고급 에이전트 기능

- [ ] Insight Agent 구현 (교차 분석 + 주간 트렌드 리포트)
- [ ] Newsletter Agent 구현 (팀원별 개인화)
- [ ] 주간 트렌드 리포트 페이지
- [ ] 에이전트 상태 대시보드 (관리자)
- [ ] 용어 사전 관리 페이지 (관리자)
- [ ] LangGraph 체크포인팅 (중간 실패 시 재개)

### Phase 3 — 팀 협업 기능

- [ ] 개인 스크랩 공간 (스크랩 + 메모 + 필터)
- [ ] 댓글 + 대댓글 + 멘션
- [ ] 이모지 반응 (👍 📌 🔥 💡 ❗)
- [ ] 기업 / 카테고리 / 소스별 필터
- [ ] 읽음/안읽음 표시
- [ ] 관리자 페이지 (소스·키워드·기업 가중치·팀원 관리)
- [ ] Gmail SMTP 이메일 알림

### Phase 4 — 확장 & 최적화

- [ ] Evaluation Agent 팀 선호도 학습 고도화 (스크랩/댓글 데이터 축적 후)
- [ ] 기사 3개월 자동 삭제 (스크랩 예외 보존)
- [ ] SQLite 자동 백업 (Google Drive 연동)
- [ ] Ollama → Gemini/Groq API 전환 옵션 (품질 개선 시)
- [ ] 파이프라인 실행 이력 통계 대시보드

---

## 13. 로컬 운영 주의사항

| 항목 | 내용 |
|------|------|
| **노트북 상시 가동** | 월·목 오전 7시에 켜져 있어야 에이전트 파이프라인 실행 (절전 모드 해제 필요) |
| **AI 처리 속도** | 6개 에이전트 순차 실행 시 약 40~60분 소요 예상 (08:00 발송 목표) |
| **에이전트 추론 품질** | 로컬 8b~12b 모델 기준. 복잡한 교차 분석은 클라우드 API 대비 다소 낮을 수 있음 |
| **메모리 사용량** | Ollama 모델 로딩 시 RAM 5~8GB 사용. 최소 16GB RAM 권장 |
| **데이터 백업** | `data/ittf.db` 파일 주기적으로 외장드라이브 또는 Google Drive에 백업 권장 |
| **사이트 접속** | 노트북이 꺼지면 팀원 접속 불가 (Cloudflare Tunnel 끊김) |
| **체크포인팅** | 에이전트 실행 중 노트북이 꺼져도 LangGraph 체크포인터로 재개 가능 |
