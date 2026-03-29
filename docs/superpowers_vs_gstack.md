# gstack vs Superpowers 비교 분석

## 기본 개요

| | **gstack** | **Superpowers** |
|---|---|---|
| 제작자 | Garry Tan (YC 대표) | Jesse Vincent (Prime Radiant) |
| 라이선스 | MIT | MIT |
| 지원 플랫폼 | Claude Code, Codex, Gemini CLI, Cursor | Claude Code, Codex, Cursor, OpenCode |
| 설치 방식 | `git clone` → `./setup` (Bun 필요) | `/plugin install` (마켓플레이스) 또는 git clone |
| 스킬 수 | 28개 | ~12개 |
| 핵심 철학 | "1인 = 20인 팀" 소프트웨어 팩토리 | TDD 기반 체계적 개발 워크플로우 |

---

## 사용법 차이

### gstack
```
/office-hours          → 제품 아이디어 검증
/plan-ceo-review       → CEO 관점 리뷰
/plan-eng-review       → 엔지니어링 아키텍처 리뷰
/review                → 코드 리뷰 + 자동 수정
/qa https://staging.com → 실제 브라우저 QA
/ship                  → 테스트 → PR 생성
/cso                   → 보안 감사
```
- **역할 기반**: 각 명령어가 "CEO", "엔지니어 매니저", "QA 리드" 등 특정 역할을 수행
- **순차 스프린트**: Think → Plan → Build → Review → Test → Ship → Reflect
- Bun으로 컴파일된 바이너리(브라우저, 디자인 도구) 포함

### Superpowers
```
(대화 시작)            → 자동으로 요구사항 인터뷰
(설계 제시)            → 단계별 설계안 자동 생성
(구현 계획)            → TDD 기반 작업 분해
(실행)                → 서브에이전트가 자동 개발
```
- **프로세스 기반**: 대화 시작 시 자동으로 워크플로우 진입
- **Git Worktree 활용**: 격리된 브랜치에서 개발 → 리뷰 → 머지
- 서브에이전트 자동 배포로 병렬 작업 수행

---

## 상대적 우위/열위

### gstack이 우위인 부분

| 영역 | 설명 |
|------|------|
| **브라우저 통합** | Playwright 기반 실제 Chromium 제어, 스크린샷, 쿠키 임포트까지 가능. Superpowers에는 이 기능 없음 |
| **디자인 도구** | `/design-consultation`, `/design-shotgun`, `/design-review` 등 디자인 전용 스킬이 풍부 |
| **보안 감사** | `/cso`로 OWASP Top 10 + STRIDE 위협 모델링. 17개 오탐 필터, 8/10 신뢰도 게이트 |
| **배포 파이프라인** | `/ship` → `/land-and-deploy` → `/canary` 까지 배포 후 모니터링 체계 완비 |
| **스킬 수와 세분화** | 28개 스킬로 역할이 세분화됨. 상황별 정확한 도구 선택 가능 |
| **멀티 AI 지원** | `/codex`로 OpenAI Codex에게 세컨드 오피니언 요청 가능 |
| **회고 시스템** | `/retro`로 주간 회고 + 프로젝트 간 교차 분석 |
| **안전 장치** | `/careful`, `/freeze`, `/guard`로 파괴적 명령어 방지 |

### Superpowers가 우위인 부분

| 영역 | 설명 |
|------|------|
| **설치 편의성** | `/plugin install` 한 줄로 설치 완료. gstack은 Bun 설치 + git clone + setup 필요 |
| **TDD 강제화** | RED-GREEN-REFACTOR를 워크플로우에 강제 적용. gstack은 테스트를 권장하지만 강제하지 않음 |
| **자동 워크플로우** | 대화 시작 시 자동으로 인터뷰 → 설계 → 계획 → 실행 흐름 진입. gstack은 수동으로 `/명령어` 입력 필요 |
| **서브에이전트 병렬 실행** | 계획 단계에서 2~5분 단위 작업으로 분해 후 서브에이전트가 병렬 실행. gstack은 한 번에 하나씩 |
| **Git Worktree 네이티브** | 기능 브랜치를 자동으로 worktree에서 격리 개발. 실패 시 깔끔한 롤백 |
| **진입 장벽** | 명령어를 몰라도 자연어 대화만으로 워크플로우 진행 가능. gstack은 28개 명령어 학습 필요 |
| **경량성** | 순수 마크다운 스킬만 사용. gstack은 Bun 바이너리(~58MB), Playwright, Chromium 등 의존성이 무거움 |

### 동등한 부분

| 영역 | 설명 |
|------|------|
| 코드 리뷰 | 둘 다 자동 코드 리뷰 + 버그 탐지 제공 |
| 계획 수립 | 둘 다 구현 전 설계/계획 단계를 강조 |
| MIT 라이선스 | 둘 다 무료, 오픈소스 |
| 멀티 플랫폼 | 둘 다 Claude Code, Codex, Cursor 지원 |

---

## ITTF 프로젝트 적용 추천

| 상황 | 추천 |
|------|------|
| **1인 개발 + 빠른 배포 중심** | gstack (풀스택 팩토리) |
| **TDD 중심 + 코드 품질 우선** | Superpowers (프로세스 강제) |
| **QA/디자인/보안이 중요** | gstack (브라우저 + 디자인 + CSO) |
| **처음 에이전트 코딩 시작** | Superpowers (자동 가이드) |
| **팀 공유 + 일관된 프로세스** | Superpowers (자동 워크플로우) |
| **복잡한 제품 + 다양한 역할 필요** | gstack (28개 전문 역할) |

ITTF 프로젝트의 경우 **gstack이 더 적합** — 브라우저 QA(`/qa`), 보안 감사(`/cso`), 배포 자동화(`/ship`)가 프론트엔드+백엔드 풀스택 개발에 실질적으로 유용하기 때문. 필요 시 Superpowers를 추가 설치하여 계획 수립 단계에서 보조적으로 사용 가능 (둘은 충돌 없이 공존 가능).
