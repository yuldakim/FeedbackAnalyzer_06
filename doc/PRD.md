# PRD — Feedback Analyzer (Phase 4 기준)

| 항목 | 값 |
|------|-----|
| 문서 버전 | 1.1 |
| 워크스페이스 | `c:\DEV_BR\FeedbackAnalyzer_06` |
| 기준 산출물 | Phase 4 Epic (EP-01), User Journey (UJ-01), User Story (ST-01~06), Gherkin (GH-01, 8 Scenarios) |
| 참조 | `README.md`, `project_purpose.md`, `.cursorrules`, `src/python/constants.py` |
| 엔트리포인트 | `src/python/app.py` (포트 8080) |

### 문서 역할 (단일 진실원천 분담)

| 문서 | 역할 | 이 PRD에 두지 않는 내용 |
|------|------|-------------------------|
| **본 PRD** | 기능·계약·INV·인수·회귀·Phase 4 추적 | 설치 스크립트, 13h 미션 표, 일일 TO-DO 체크 |
| **README.md** | Quick Start, 예시 I/O, 아키텍처 다이어그램, Activities, **구현 TO-DO** | 계약 변경(→ 본 PRD 선행) |
| **project_purpose.md** | 리팩토링 챌린지·코드 스멜 교육 맥락 | — |

구현 진행·마일스톤 체크는 README **TO-DO LIST** 를 따르되, 계약·INV 변경은 **본 PRD → Gherkin → README** 순으로만 갱신한다 (**RR-1**).

---

# 1. 프로젝트 개요

## 1.1 한 줄 목적문 (What / Who / Why)

**What:** 키워드 기반으로 고객 피드백을 감정·카테고리 분류하고, 웹 대시보드에서 집계·필터·CSV 다운로드를 제공한다.  
**Who:** 중급 Python 개발자·리팩토링·TDD·클린 아키텍처 실습자.  
**Why:** 의도적 레거시 코드를 **계약(Invariant)·pytest·Boundary→Control→Entity 레이어 분리**로 개선하는 학습 목적을 달성한다.

## 1.2 배경 및 문제 정의

| 문제 | 현재 코드·문서 근거 | 사용자·학습 영향 |
|------|---------------------|------------------|
| God Function | `app.py`에 Flask 라우팅·HTML 렌더링·흐름 제어 혼재 | 변경 시 회귀 범위 불명확 |
| 이중 감정 규칙 | `constants.SENTIMENT_KEYWORDS` vs `filters.S_KEYWORDS` | Analyze 집계와 Filter 결과 불일치 (**INV-SENT-002** 위반) |
| 전역 상태 | `fil_data`, `TextAnalyzer.global_sent` / `global_kw` | 다운로드·집계가 요청 간 숨은 결합 |
| 세션 설계 | `Session.current_feedbacks` 클래스 변수 | 다중 사용자·테스트 격리 불가 |
| 중립 필터 결함 | 필터·분석 규칙 불일치 (미션 3) | 「중립」 선택 시 기대와 다른 목록 (**INV-SENT-003**) |

Phase 4 Gherkin Background는 위 문제를 **정책·계약**으로 고정하고, 구현은 단일 `SentimentClassifier` 허브와 Repository/Store로 수렴하는 것을 전제로 한다.

## 1.3 목표 (측정 가능)

| ID | 목표 | 측정 방법 | 목표값 |
|----|------|-----------|--------|
| G-1 | Domain·Control 테스트 커버리지 | `pytest-cov` (entity·control) | **≥ 90%** |
| G-2 | Analyze·Filter 감정 일치 | pytest + GH-01 Scn6 | **INV-SENT-002** 100% 통과 |
| G-3 | 중립 필터 정확성 | pytest + GH-01 Scn5 | **INV-SENT-003** 100% 통과 |
| G-4 | 감정 건수 합 정합 | pytest + GH-01 Scn7 | **INV-COUNT-002** (긍+중+부 = 대상 건수) |
| G-5 | 입력·출력 계약 | GH-01 Scn2·3·8, Background | 공백-only 미추가, 원문 보존, 0건 warning, CSV 스냅샷 일치 |

## 1.4 비목표

| ID | 비목표 | 제외 사유 |
|----|--------|-----------|
| NG-1 | 딥러닝·LLM 기반 감정 분석 | 키워드 규칙·계약 학습이 범위; `constants.py` 키워드 모델 유지 |
| NG-2 | `Cursor AI_퀴즈 - 문제.docx` 요구 반영 | 저장소·`.cursorrules` exclude; 피드백 분석과 무관 |
| NG-3 | 프로덕션 배포·인증·다국어 UI | 로컬 Flask 학습·리팩토링 챌린지 범위 외 |

---

# 2. 사용자 및 이해관계자

## 2.1 타깃 사용자 (페르소나 1명)

| 항목 | 내용 |
|------|------|
| 이름(가칭) | 김리팩 — 중급 Python 개발자 |
| 역량 | Flask 기초, pytest 경험, Clean Code·리팩토링 교재 학습 중 |
| 목표 | God Function·전역 상태를 제거하고 **테스트로 보호되는** 구조로 전환 |
| 성공 정의 | Level 5 체크리스트·Gherkin 8 Scenario·커버리지 90% 달성 |

## 2.2 주요 시나리오 (Phase 4 Journey UJ-01 기반)

| ID | 시나리오 | Journey 단계 | 관련 Story·Gherkin |
|----|----------|--------------|-------------------|
| SCN-A | 대시보드 접속 → 피드백 텍스트 입력 → **POST /analyze** → 감정·카테고리 집계 확인 | Entry → Action | ST-01, ST-02 / GH Scn2,6,7 |
| SCN-B | **POST /upload** (UTF-8 CSV) → N건 적재 메시지 → 전체 분석·집계 | Action | ST-01 / GH Scn1, Background |
| SCN-C | **POST /filter** (감정·카테고리) → 결과 확인 → **GET /download** (`filtered_feedback.csv`) | Validation → Outcome | ST-02, ST-04 / GH Scn3,5,8 |

---

# 3. 기능 요구사항

## 3.1 기능 목록

| 우선순위 | 기능 ID | 기능명 | 설명 |
|----------|---------|--------|------|
| **필수** | F-01 | 피드백 입력 검증 | trim 후 공백-only 미추가; 멀티라인 1건 보존 |
| **필수** | F-02 | SentimentClassifier 단일 허브 | 긍정/부정/중립 분류; Analyze·Filter 동일 규칙 |
| **필수** | F-03 | 카테고리 키워드 분류 | `CATEGORIES` 5종; `CATEGORY_KEYWORDS` 정책 |
| **필수** | F-04 | 웹 대시보드 | GET `/`, POST `/analyze`, `/upload`, `/filter`, GET `/download` |
| **필수** | F-05 | 감정·카테고리 집계 표시 | 건수 기반 stat; **INV-COUNT-002** |
| **필수** | F-06 | 필터·경고 | 0건·무결과 시 warning; 미지원 값 처리 정책 고정 |
| **권장** | F-07 | Dual-Track BCE | Boundary→Control→Entity 의존 방향 |
| **권장** | F-08 | KeywordRuleRepository (Port) | OCP; 키워드 변경 시 분류기 core 무변경 |
| **권장** | F-09 | FeedbackRepository·FilteredResultStore | `Session`·`fil_data`·`global_sent` 제거 |
| **권장** | F-10 | Presenter 분리 | HTML·escape; 비즈니스 로직 비포함 |
| **선택** | F-11 | Trend 시각화 | `test_feedback_trend.csv`; `@pytest.mark.mission7` |
| **선택** | F-12 | File DB 키워드 관리 | mission7; 손상 JSON fallback (ST-05) |
| **선택** | F-13 | JSON API 응답 | `AnalysisResult` JSON 직렬화 (**INV-JSON-001**; 스키마는 §6.5) |
| **선택** | F-14 | PageLogSink level 외부화 | warning/error 페이지 노출 on/off (미션 3) |

## 3.2 기능별 입출력 계약 (문자열·필드 수준)

### F-01 / POST `/analyze`

| 방향 | 계약 |
|------|------|
| 입력 | `text`: string (form); 앞뒤 trim 적용 |
| 처리 | trim 후 길이 0 → 피드백 **추가하지 않음**; 길이 > 0 → Feedback 1건 append 후 전체 재분석 |
| 출력 | `success`: string (예: `"N개의 피드백이 입력되었습니다."`); `sentiment_results`: `{"긍정": int, "중립": int, "부정": int}`; `keyword_results`: `{카테고리명: int}`; 피드백 **원문** 목록(표시 시 escape) |
| 오류 | 처리 예외 시 `error`: string; 기존 목록 불변 |

### F-02 / POST `/upload`

| 방향 | 계약 |
|------|------|
| 입력 | `file`: CSV, UTF-8 (BOM 허용) |
| 처리 | 1행 헤더 스킵; 데이터 행 1열을 피드백 텍스트; 빈 행 무시; 행별 trim 후 공백-only 무시 |
| 출력 | `success`: string (적재 후 총 건수); 실패 시 `error`: string |
| 불변 | 업로드 실패 시 **기존 세션 피드백 건수·원문 불변** (**INV-SESSION-001**, GH Scn1) |

### F-03 / POST `/filter`

| 방향 | 계약 |
|------|------|
| 입력 | `sentiment`: `전체` \| `긍정` \| `부정` \| `중립`; `keyword`: `전체` \| `배송` \| `품질` \| `가격` \| `서비스` \| `사용성` |
| 처리 | 저장된 피드백 목록에 감정·카테고리 조건 적용; **SentimentClassifier와 동일 규칙**; 결과를 FilteredResultStore에 스냅샷 저장 |
| 출력 (성공) | 필터된 목록; `sentiment_results`·`keyword_results` (**부분집합** 재집계) |
| 출력 (0건·무피드백) | `warning`: string (예: 분석할 피드백 없음 / 필터링 결과 없음) |
| 출력 (미지원 값) | `error` 또는 정의된 safe fallback + 사용자 메시지 (GH Scn unknown filter 정책과 동일 문구) |

### F-04 / GET `/download`

| 방향 | 계약 |
|------|------|
| 입력 | 없음 (마지막 필터 스냅샷 참조) |
| 출력 | `Content-Disposition: attachment; filename=filtered_feedback.csv`; body: UTF-8 **BOM** + 헤더 `text` + 스냅샷 각 행 원문 1줄 |
| 불변 | 스냅샷 **행 개수·순서** = 필터 직후 목록 (**INV-CSV-OUT-003**) |
| 0건 | 스냅샷 없음 → warning 또는 다운로드 미제공 (**INV-EMPTY-001**, GH Scn8) |

### F-05 동적 KeywordRule (선택, ST-06 / GH Scn4)

| 방향 | 계약 |
|------|------|
| 입력 | 카테고리명(기존 또는 신규) + 키워드 목록(예: `"이벤트-프로모션"`) |
| 처리 | Repository 저장 후 분류·필터에 반영 |
| 출력 | 해당 키워드 포함 텍스트가 **등록 카테고리**로 분류; 원문 불변 (**INV-RULE-002**) |

## 3.3 제약 사항 (Phase 4 Gherkin Background Given과 일치)

| ID | 제약 | 규칙 |
|----|------|------|
| C-01 | CSV | UTF-8; BOM 허용; **첫 행 헤더(`text`) 스킵**; 빈 행 무시 |
| C-02 | 수동 입력 | **공백-only 미추가**; 원문은 숫자·특수문자 포함 **변형 없이 보존** (**INV-TEXT-001**) |
| C-03 | 허용 감정 | `긍정`, `부정`, `중립`, `전체` (필터); 분류 결과는 3감정 중 1 |
| C-04 | 허용 카테고리 | `배송`, `품질`, `가격`, `서비스`, `사용성`, `전체` (필터) |
| C-05 | 감정 분류 단일성 | **Analyze와 Filter는 동일 감정 분류 규칙** (**INV-SENT-002**) |
| C-06 | 중립 정의 | 긍·부 키워드 미매칭 → `중립`; 중립 필터는 중립 라벨만 (**INV-SENT-003**) |
| C-07 | 업로드 실패 | 오류 메시지; **세션 피드백 목록·원문 불변** |
| C-08 | 0건 | 피드백 0건 시 filter·download → **warning**; 집계·다운로드 미제공 (**INV-EMPTY-001**) |
| C-09 | 미지원 필터 값 | `error` 또는 문서화된 fallback; 사용자에게 표시 가능한 메시지 |

---

# 4. 비기능 요구사항

## 4.1 기술 스택

| 구분 | 기술 | 버전·비고 |
|------|------|-----------|
| 언어 | Python | **3.11+** (`.cursorrules` 기준). README Quick Start는 3.9+ 레거시 호환 **참고**만 |
| 웹 | Flask | 3.x (`requirements.txt`) |
| 테스트 | pytest, pytest-cov | entity·control 커버리지 |
| 포맷 | black, isort | line-length 88 (`.cursorrules`) |
| 타입 | typing | public API·메서드 **타입 힌트 필수** |

## 4.2 아키텍처 원칙

| 원칙 | 요구 |
|------|------|
| SRP | HTML·HTTP·분류·상태·키워드 저장 책임 분리 |
| OCP | 새 카테고리·키워드는 KeywordRule·Repository 확장; SentimentClassifier core 무변경 |
| Dual-Track | **Boundary** (Flask, Presenter, CSV I/O) / **Entity** (모델, 분류, 필터, Port) |
| BCE | **Control**: Use Case 조율; **Entity**: 규칙·불변식 |
| 의존성 | `boundary → control → entity`; `infrastructure`는 Port 구현만 |
| 금지 | **entity**가 `flask`, `boundary`, `control` import 금지 |

## 4.3 테스트·커버리지

| 항목 | 요구 |
|------|------|
| 커버리지 | entity·control **≥ 90%** |
| boundary | Flask client 통합 **소수** |
| 패턴 | AAA (Arrange–Act–Assert) |
| 문서화 | 각 테스트 docstring에 **INV-\*** 1줄 |
| 마커 | mission7: Trend·File DB (선택) |

## 4.4 확장성

| 변경 유형 | 확장 지점 | 금지 |
|-----------|-----------|------|
| 새 카테고리·키워드 | KeywordRuleRepository | `filters.S_KEYWORDS` vs `constants` **이중 규칙 재도입** |
| 새 출력 포맷 | Boundary Presenter / Serializer | Entity에 HTML·CSV 문자열 |
| 새 감정 규칙 | SentimentClassifier 단일 모듈 | Filter 전용 별도 키워드表 |

---

# 5. 데이터 요구사항

## 5.1 분류 기준 상수 (`constants.py` 기준)

### SENTIMENT_KEYWORDS

| 감정 | 매칭 방식 | 비고 |
|------|-----------|------|
| 긍정 | 목록 중 **부분 문자열 포함** 시 긍정 | 목록: `constants.py` L4–8 |
| 부정 | 목록 중 부분 문자열 포함 시 부정 | 목록: L9–13 |
| 중립 | 긍·부 모두 미매칭 시 중립 | 별도 키워드表 없음 (**INV-SENT-001**) |

### CATEGORY_KEYWORDS · CATEGORIES

| 카테고리 | main 키워드 (예) | sub 키 (구조) |
|----------|------------------|---------------|
| 배송 | 배송, 택배, 배달, … | time, type, status |
| 품질 | 품질, 재질, … | physical, state, content |
| 가격 | 가격, 비용, … | amount, discount, evaluation |
| 서비스 | 서비스, 응대, … | interaction, quality, type_ |
| 사용성 | 사용, 편리, … | ease, guide, action |

**필터 UI 정책 (PRD 고정):** 카테고리 필터는 문서화된 **main + sub** 정책과 일치해야 하며, UI 라벨 `CATEGORIES`와 Repository 등록 목록이 동일 집합이어야 한다.

## 5.2 설정 외부화 (권장·선택, mission7)

| 항목 | 방식 |
|------|------|
| KeywordRule | File DB 또는 JSON/YAML 파일; Port 경유 로드 |
| 로드 실패 | **기본 정책(고정):** `constants.py` fallback + `warning` (정책 B). 팀이 ST-05에서 A(이전 규칙 유지)로 변경 시 본 절·README 동시 개정 |
| Trend | `test_feedback_trend.csv`; 시간·건수 컬럼 계약은 mission7 스펙에서 정의 |

## 5.3 동적 키워드 등록 계약 (GH Scn4 = ST-06)

| 필드 | 계약 |
|------|------|
| 등록 요청 | `category`: `배송`\|`품질`\|`가격`\|`서비스`\|`사용성` 또는 신규 카테고리명; `keywords`: string[] |
| 예시 | 카테고리 `프로모션`(또는 기존 카테고리) + `"이벤트-프로모션"` |
| 검증 | 등록 후 `"이번 이벤트-프로모션 정말 좋았어요"` → 해당 카테고리 매칭; 원문 동일 |
| 회귀 | **INV-SENT-002**, **INV-SENT-003**, **INV-COUNT-002** 테스트 유지 |

---

# 6. 출력 요구사항

## 6.1 웹 기본 포맷

| 요소 | 계약 |
|------|------|
| 피드백 원문 | 사용자 입력 문자열 **그대로** 표시(HTML escape만 적용) |
| 감정 표기 | 집계: 긍정/중립/부정 **건수**; 개별 행 감정 라벨은 필터·분석 결과와 일치 |
| 예시 | 원문 `"2.5일 만에 배송 완료! (만족)"` 유지; 집계에 긍정 1건 반영 |

## 6.2 페이지 메시지 스키마

| 필드 | 타입 | 노출 조건 |
|------|------|-----------|
| `success` | string | 성공·적재·분석 완료; 타임스탬프 접두 가능 |
| `warning` | string | 0건·무결과·다운로드 불가; **PageLogSink level에 warning 포함 시만** (선택 F-14) |
| `error` | string | 업로드·처리·미지원 필터; **level에 error 포함 시만** |

## 6.3 CSV 출력 스키마 (`filtered_feedback.csv`)

| 순서 | 내용 |
|------|------|
| 1 | UTF-8 BOM (`\ufeff`) |
| 2 | 헤더 행: `text` |
| 3..N | 스냅샷 피드백 원문 1행 1건; **순서 = 필터 결과 순서** (**INV-CSV-OUT-001~003**) |

## 6.4 집계 표시 스키마

| 블록 | 필드 | 규칙 |
|------|------|------|
| 감정 분포 | `긍정`, `중립`, `부정` | int ≥ 0; **합 = 분석 대상 피드백 수** (**INV-COUNT-002**) |
| 카테고리 분포 | `배송`…`사용성` | 각 int ≥ 0; 1 피드백이 복수 카테고리 매칭 시 **건수 합 ≤ 분석 대상 피드백 수** (복수 main 매칭 허용, 이중 카운트는 README·테스트에 예시 고정) |

## 6.5 JSON API 스키마 (선택 F-13, **INV-JSON-001**)

| 필드 | 타입 | 설명 |
|------|------|------|
| `feedbacks` | `{ "text": string, "sentiment": string, "categories": string[] }[]` | 원문·분류 결과 |
| `sentiment_results` | `{ "긍정": int, "중립": int, "부정": int }` | §6.4와 동일 |
| `keyword_results` | `{ [category: string]: int }` | §6.4와 동일 |
| `message` | `success` \| `warning` \| `error` | string, §6.2와 동일 의미 |

---

# 7. 성공 지표

## 7.1 인수 기준 (테스트·데모 가능)

- [ ] **INV-SENT-002:** 동일 세션에서 Analyze 직후 감정 건수 = Filter(`전체`,`전체`) 재집계 감정 건수
- [ ] **INV-SENT-003:** Filter(`중립`,`전체`) 결과에 중립 라벨만 존재; 긍·부 샘플 제외
- [ ] **INV-INPUT-001:** POST `/analyze` with `"   "` → 건수 불변
- [ ] **INV-SESSION-001:** 깨진/빈 CSV 업로드 → `error` + 기존 피드백 원문·건수 불변
- [ ] **INV-CSV-OUT-003:** Filter 후 download CSV 행·순서 = 필터 목록
- [ ] **INV-COUNT-002:** 긍정+중립+부정 = 전체 피드백 수
- [ ] **INV-EMPTY-001:** 0건 시 filter·download → warning, 집계/파일 미제공
- [x] **G-1:** pytest-cov entity·control ≥ 90% (`tests/control/test_coverage_g1.py` 포함, 2026-05-22)

## 7.2 회귀 보호 규칙

| 규칙 ID | 내용 |
|---------|------|
| RR-1 | Phase 4 Gherkin 8 Scenario + Background 3정책 **문자열·행위 변경 시** Story·AC·PRD 동시 개정 |
| RR-2 | **INV-\*** ID 삭제·의미 변경 금지; 변경 시 RED 테스트 선행 |
| RR-3 | `constants.SENTIMENT_KEYWORDS` vs `filters.S_KEYWORDS` **이중 감정表 재도입 금지** |
| RR-4 | `fil_data`·`global_sent`·`global_kw`·`Session` 클래스 변수 **재도입 금지** (Repository/Store 사용) |
| RR-5 | main 브랜치(또는 PR) **전체 pytest 0 실패**; mission7 마커 분리 실행 |

---

# 8. 용어 정의 (Glossary)

| 용어 | 정의 |
|------|------|
| **Feedback** | 사용자 피드백 원문 1건; 필수 속성 `text`(string); 분석·필터·CSV의 최소 단위 |
| **SentimentClassifier** | 긍정/부정/중립을 판정하는 **단일 허브** Domain 서비스; Analyze·Filter가 동일 인스턴스·규칙 사용 |
| **KeywordRule** | 카테고리별 키워드 집합; 동적 등록·File DB의 기본 단위 (OCP) |
| **Boundary** | Flask 라우트, HTML Presenter, CSV 업로드/다운로드 I/O; 비즈니스 규칙 없음 |
| **Control** | Use Case; Command 수신·Entity 호출·`success`/`warning`/`error` ViewModel 조립 |
| **Entity** | Feedback 모델, SentimentClassifier, FeedbackFilter, Port 인터페이스, Invariant |
| **INV-\*** | 불변식 ID; pytest·Gherkin Scenario 제목에 추적 (예: INV-SENT-002) |
| **FilteredResultStore** | 마지막 필터 결과 스냅샷 Port; GET `/download` 입력 |
| **FeedbackRepository** | 세션 피드백 목록 CRUD Port; `Session.current_feedbacks` 대체 |
| **PageLogSink** | warning/error/success의 **페이지 노출 여부**를 level 설정으로 제어 (선택) |
| **Phase 4** | Epic EP-01, Journey UJ-01, Story ST-01~06, Gherkin GH-01(8 Scenarios) 산출물 집합 |

---

## 부록 A — Phase 4 추적 매트릭스

| PRD 절 | Epic | Journey | Story | Gherkin |
|--------|------|---------|-------|---------|
| §3.2 analyze | SC-2 | 4–5 | ST-01,02 | Scn2,6,7 |
| §3.2 upload | SC-5 | 5 | ST-01,05 | Scn1 |
| §3.2 filter | SC-2 | 5 | ST-02 | Scn5,6 |
| §3.2 download | SC-5 | 6 | ST-04 | Scn3,8 |
| §5.3 동적 규칙 | SC-3 | 7 | ST-06 | Scn4 |
| §7.1 인수 | SC-1~5 | 7 | ST-01~06 | Scn1~8 |

---

## 부록 B — 문서 이력

| 버전 | 일자 | 변경 |
|------|------|------|
| 1.0 | 2026-05-21 | Phase 4 기준 초안; `doc/PRD.md` 생성 |
| 1.1 | 2026-05-21 | README 정합: 문서 역할, §6.5 JSON, ST-07~10 부록 C, KeywordRule 로드 기본 정책 B |

---

## 부록 C — README TO-DO 와 Story ID (구현 추적)

Phase 4 공식 Story는 **ST-01~06** 이다. README TO-DO 의 ST-07~10 은 **구현·미션 추적용 파생 ID**이며 Epic 범위를 바꾸지 않는다.

| README ST | 대응 PRD | 비고 |
|-----------|----------|------|
| ST-01 | ST-01, F-01 | 입력·CSV |
| ST-02 | ST-02, F-02 | SentimentClassifier·필터 |
| ST-03 | ST-02, F-05 | INV-COUNT-002 |
| ST-04 | ST-04, F-04 | CSV 다운로드 |
| ST-05 | ST-05, F-07~F-10 | BCE·Repository (M2) |
| ST-06 | ST-06, F-08·§5.3 | 동적 KeywordRule |
| ST-07 | F-14 | PageLogSink (선택) |
| ST-08 | G-1, §4.3 | pytest-cov ≥90% |
| ST-09 | F-11, F-12 | mission7 Trend·File DB |
| ST-10 | F-13, §6.5 | JSON API (**INV-JSON-001**) |
