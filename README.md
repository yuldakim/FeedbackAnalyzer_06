# Feedback Analyzer (Python/Flask)

키워드 기반으로 고객 피드백을 감정·카테고리 분류하고, 웹 대시보드에서 집계·필터·CSV 다운로드를 제공하며, **계약(Invariant)·pytest·Boundary→Control→Entity** 로 레거시 코드를 개선하는 **리팩토링·TDD 학습** 프로젝트입니다.

> 상세 요구사항: [`doc/PRD.md`](doc/PRD.md) · 학습 로드맵: [`project_purpose.md`](project_purpose.md) · AI/개발 규칙: [`.cursorrules`](.cursorrules)

---

## 목차

- [개요 (Overview)](#개요-overview)
- [빠른 시작 (Quick Start)](#빠른-시작-quick-start)
- [지원 감정·카테고리 및 키워드 기준](#지원-감정카테고리-및-키워드-기준)
- [입력 형식 계약](#입력-형식-계약)
- [아키텍처](#아키텍처)
- [테스트 실행](#테스트-실행)
- [RED 단계 To-Do 리스트](#red-단계-to-do-리스트)
- [REFACTOR 단계 To-Do 리스트](#refactor-단계-to-do-리스트)
- [Golden Master 회귀 안전장치](#golden-master-회귀-안전장치)
- [설정 파일 (KeywordRule)](#설정-파일-keywordrule-file-db--jsonyaml)
- [출력 포맷](#출력-포맷)
- [생성형 AI 활용 Activities](#생성형-ai-활용-activities)
- [기여 가이드](#기여-가이드)
- [라이선스](#라이선스)
- [관련 문서](#관련-문서)
- [TO-DO LIST](#to-do-list)

---

## 개요 (Overview)

### 이 프로젝트가 해결하는 문제 (학습용 AS-IS → REFACTOR 완료)

| 문제 | 레거시 증상 (학습 전) | REFACTOR 후 (현재) |
|------|----------------------|-------------------|
| God Function | `app.py`에 라우팅·HTML·흐름 혼재 | `boundary/routes.py` + `boundary/presenter.py`, thin `app.py` |
| 이중 감정 규칙 | `SENTIMENT_KEYWORDS` ≠ `S_KEYWORDS` | `entity.SentimentClassifier` 단일 (**RR-3**) |
| 전역 상태 | `fil_data`, `global_sent`, `global_kw` | `infrastructure` Port (**RR-4**) |
| 세션 설계 | `Session` 클래스 변수 | `MemoryFeedbackRepository` |
| 중립 필터 | 규칙 불일치 | `FeedbackFilter` + **INV-SENT-003** |

자세한 배경: [`doc/PRD.md` §1.2](doc/PRD.md) · 실행 기록: [`doc/refactoring_plan.md`](doc/refactoring_plan.md).

### 측정 목표 ([`doc/PRD.md` §1.3](doc/PRD.md))

| ID | 요약 | 목표값 |
|----|------|--------|
| G-1 | entity·control 커버리지 | ≥ 90% |
| G-2 | Analyze = Filter 감정 | **INV-SENT-002** |
| G-3 | 중립 필터 | **INV-SENT-003** |
| G-4 | 감정 건수 합 | **INV-COUNT-002** |
| G-5 | 입·출력 계약 | 공백-only·원문·0건·CSV 스냅샷 |

### 비목표 ([`doc/PRD.md` §1.4](doc/PRD.md))

| ID | 제외 |
|----|------|
| NG-1 | 딥러닝·LLM 감정 분석 |
| NG-2 | `Cursor AI_퀴즈 - 문제.docx` 반영 |
| NG-3 | 프로덕션 배포·인증·다국어 UI |

### 사용자 Journey ([`doc/PRD.md` §2.2](doc/PRD.md))

| ID | 흐름 |
|----|------|
| SCN-A | 접속 → `POST /analyze` → 집계 |
| SCN-B | `POST /upload` (CSV) → N건 적재 |
| SCN-C | `POST /filter` → `GET /download` |

### 주요 학습 목표

| 목표 | 측정·산출 |
|------|-----------|
| **SRP / OCP** | HTML·분류·상태·키워드 저장 책임 분리; KeywordRule Repository 확장 |
| **Dual-Track + BCE** | Boundary → Control → Entity 의존 방향 |
| **TDD** | RED(Gherkin·INV) → GREEN(최소 통과) → REFACTOR(구조만) |
| **pytest-cov** | `entity`·`control` **≥ 90%** (G-1) |
| **계약 통일** | Phase 4 Gherkin · [`doc/PRD.md` §7](doc/PRD.md) · 본 README Invariant 동일 표기 |

### 현재 코드의 문제점과 개선 방향

```text
[레거시 AS-IS]                  [현재 런타임 TO-BE — M2 완료]
app.py (God Function)    →      app.py (composition root) + boundary/
text_analyzer + filters  →      entity/ (삭제됨: text_analyzer, filters, session)
Session, fil_data, ...   →      infrastructure/ Repository + Store
constants (카테고리)      →      CategoryClassifier ← constants (F-08·File DB는 🟢 선택)
```

### 용어·계약 통일 (Invariant)

다음 ID는 **`doc/PRD.md` · Phase 4 Gherkin · 본 README** 에서 **동일한 의미**로 씁니다.

| ID | 의미 |
|----|------|
| **INV-SENT-002** | Analyze 직후 감정 집계 = Filter(`전체`,`전체`) 재집계 (동일 분류 규칙) |
| **INV-SENT-003** | Filter(`중립`,…) 결과에 중립만 포함 |
| **INV-COUNT-002** | 긍정 + 중립 + 부정 건수 = 분석 대상 피드백 수 |
| **INV-CSV-OUT-003** | 다운로드 CSV 행·순서 = 마지막 필터 스냅샷 |
| **INV-SENT-001** | 긍·부 미매칭 → 중립 |
| **INV-INPUT-001** | 공백-only 미추가 |
| **INV-TEXT-001** | 원문 보존 (escape만) |
| **INV-SESSION-001** | 업로드 실패 시 세션 불변 |
| **INV-EMPTY-001** | 0건 filter·download → warning |
| **INV-RULE-002** | 동적 KeywordRule 등록 후 분류·원문 불변 |
| **INV-JSON-001** | JSON API 스키마 (선택 F-13, PRD §6.5) |

전체 정의: [`doc/PRD.md` §8 Glossary](doc/PRD.md). 인수 체크리스트: [§7.1](doc/PRD.md).

### 문서 범위 안내

**`Cursor AI_퀴즈 - 문제.docx` 내용은 README·PRD·학습 미션에 인용·반영하지 않습니다.** (저장소 분석·AI 컨텍스트 제외)

---

## 빠른 시작 (Quick Start)

### 사전 조건

| 항목 | 요구 |
|------|------|
| Python | **3.11+** ([`doc/PRD.md` §4.1](doc/PRD.md) 기준). 레거시 환경 3.9+ 는 보장하지 않음 |
| pip | 최신 권장 |
| 가상환경 | `src/python/.venv` (로컬 전용, 커밋하지 않음) |

### 저장소 클론

```bash
git clone [repository-url]
cd FeedbackAnalyzer_06
```

### 빌드 & 실행

```bash
cd src/python
python -m venv .venv
```

**Windows (PowerShell)**

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

**macOS / Linux**

```bash
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

브라우저: **http://localhost:8080**

가상환경 종료: `deactivate`

### 예시 입출력 (1분 데모)

| 단계 | 사용자 행위 | 기대 결과 |
|------|-------------|-----------|
| 1 | 접속 `http://localhost:8080` | 대시보드, 시작 `success` 메시지 |
| 2 | 텍스트 `배송이 너무 늦어요. 화가 납니다.` 입력 → **입력하기** (`POST /analyze`) | `success`: N건 입력; 감정 **부정** 집계; 카테고리 **배송** 등 집계 |
| 3 | 감정 `부정`, 카테고리 `배송` → **분석** (`POST /filter`) | 필터된 목록·집계 |
| 4 | **결과 다운로드** (`GET /download`) | `filtered_feedback.csv` (BOM + `text` 헤더) |

### HTTP 엔드포인트

| 메서드 | 경로 | 용도 |
|--------|------|------|
| GET | `/` | 대시보드 |
| POST | `/analyze` | 수동 피드백 추가·분석 |
| POST | `/upload` | CSV 업로드 |
| POST | `/filter` | 감정·카테고리 필터 |
| GET | `/download` | 필터 스냅샷 CSV |

### CSV 입력 형식 (요약)

- UTF-8 (BOM 허용)
- 첫 행: 헤더 `text`
- 이후 행: 피드백 원문 1열
- 빈 행 무시

---

## 지원 감정·카테고리 및 키워드 기준

출처: [`src/python/constants.py`](src/python/constants.py)

### 감정 (Sentiment)

| 구분 | 식별자 | 키워드 출처 | 비고 |
|------|--------|-------------|------|
| 긍정 | `긍정` | `SENTIMENT_KEYWORDS["긍정"]` | 부분 문자열 매칭 (예: 만족, 감사, 최고) |
| 부정 | `부정` | `SENTIMENT_KEYWORDS["부정"]` | 부분 문자열 매칭 (예: 불만, 화남, 최악) |
| 중립 | `중립` | (별도 목록 없음) | 긍·부 **모두** 미매칭 시 중립 (**INV-SENT-001**) |
| 필터 전체 | `전체` | — | 감정 조건 없음 |

> **개선 목표:** `filters.S_KEYWORDS` 와 **단일** `SentimentClassifier` 로 통합 (**INV-SENT-002**).

### 카테고리 (Category)

| 구분 | 식별자 | 키워드 출처 | 비고 |
|------|--------|-------------|------|
| 배송 | `배송` | `CATEGORY_KEYWORDS["배송"]` | `main`: 배송, 택배, … / `sub`: time, type, status |
| 품질 | `품질` | `CATEGORY_KEYWORDS["품질"]` | `main` + sub(physical, state, content) |
| 가격 | `가격` | `CATEGORY_KEYWORDS["가격"]` | `main` + sub(amount, discount, evaluation) |
| 서비스 | `서비스` | `CATEGORY_KEYWORDS["서비스"]` | `main` + sub(interaction, quality, type_) |
| 사용성 | `사용성` | `CATEGORY_KEYWORDS["사용성"]` | `main` + sub(ease, guide, action) |
| UI 목록 | `CATEGORIES` | 동일 5종 배열 | 필터 드롭다운; **Repository 등록 목록과 동일 집합** |
| 필터 전체 | `전체` | — | 카테고리 조건 없음 |

**카테고리 필터 정책 ([`doc/PRD.md` §5.1](doc/PRD.md)):** UI·필터는 **main + sub** 키워드와 일치한다. `entity/category_classifier.py` · `FeedbackFilter` 가 동일 정책 사용 (TC-B-11).

**카테고리 집계:** 복수 카테고리 매칭 시 건수 합 ≤ 분석 대상 피드백 수 ([`doc/PRD.md` §6.4](doc/PRD.md)).

---

## 입력 형식 계약

Phase 4 Gherkin Background 및 [`doc/PRD.md` §3.3](doc/PRD.md) 와 동일합니다.

### 정상 입력 예시 (3)

**1) 수동 텍스트 (단일 건)**

```http
POST /analyze
Content-Type: application/x-www-form-urlencoded

text=배송이 너무 늦어요. 화가 납니다.
```

→ 1건 추가, 감정·카테고리 집계 갱신.

**2) 멀티라인 (1건으로 보존)**

```http
POST /analyze

text=첫 줄 피드백
둘째 줄도 같은 건입니다.
```

→ 줄바꿈 포함 **원문 1건** (**INV-TEXT-001**).

**3) CSV 업로드**

```csv
text
배송이 빨라서 좋아요
품질이 별로예요
```

```http
POST /upload
(multipart file, UTF-8 BOM 허용)
```

→ `success`: `2개의 피드백이 입력되었습니다.` (예시 문구).

### 비정상 입력 예시 (3) + 메시지

| # | 입력 | 기대 메시지·동작 | Invariant |
|---|------|------------------|-----------|
| 1 | `text=   ` (공백만) | 추가 없음; 기존 건수·원문 유지 | **INV-INPUT-001** |
| 2 | 깨진/빈 CSV 업로드 | `error`: 업로드 오류; **세션 목록 불변** | **INV-SESSION-001** |
| 3 | 피드백 0건 상태에서 Filter | `warning`: 분석할 피드백 없음; 집계 미표시 | **INV-EMPTY-001** |
| 4 | `sentiment`/`keyword` **미지원 값** | `error` 또는 문서화된 fallback + 사용자 메시지 (**C-09**) | PRD §3.2 F-03 |

추가 비정상:

| 입력 | 기대 |
|------|------|
| Filter 결과 0건 | `warning`: 필터링 결과가 없습니다. |
| 0건 또는 스냅샷 없음 Download | `warning` 또는 다운로드 미제공 (**INV-EMPTY-001**) |

**Filter 성공 시:** 결과는 **FilteredResultStore** 스냅샷에 저장 후 집계·`GET /download` 가 동일 스냅샷을 참조 ([`doc/PRD.md` §3.2 F-03](doc/PRD.md)).

---

## 아키텍처

### 목표 레이어 (Dual-Track + BCE)

```mermaid
flowchart TB
    subgraph Boundary["Boundary (Track A)"]
        R[Flask Routes]
        P[HTML Presenter]
        IO[CSV Upload / Download]
    end
    subgraph Control["Control (BCE)"]
        UC[Use Cases]
    end
    subgraph Entity["Entity (BCE)"]
        FB[Feedback]
        SC[SentimentClassifier]
        FF[FeedbackFilter]
        PORT[Ports]
    end
    subgraph Infra["Infrastructure"]
        REP[FeedbackRepository]
        STORE[FilteredResultStore]
        KR[KeywordRuleRepository]
    end
    R --> UC
    P --> UC
    IO --> UC
    UC --> SC
    UC --> FF
    UC --> PORT
    REP -.-> PORT
    STORE -.-> PORT
    KR -.-> PORT
```

### 의존성 방향

```text
boundary  →  control  →  entity
                ↑
         infrastructure (Port 구현만)
```

| 규칙 | 설명 |
|------|------|
| 허용 | `boundary` → `control` → `entity` |
| 허용 | `infrastructure` → `entity` (Port 구현) |
| **금지** | `entity` 가 `flask`, `boundary`, `control` import |

### 디렉터리 (REFACTOR 완료, 2026-05-22)

| 경로 | 역할 |
|------|------|
| `app.py` | Flask composition root (~20줄) |
| `boundary/routes.py`, `boundary/presenter.py` | HTTP · HTML (F-10) |
| `control/*_use_case.py` | 유스케이스 오케스트레이션 |
| `entity/` | `SentimentClassifier`, `CategoryClassifier`, `FeedbackFilter`, `ports.py` |
| `infrastructure/` | `MemoryFeedbackRepository`, `MemoryFilteredResultStore`, `wiring.py` |
| `tests/boundary`, `tests/entity`, `tests/control`, `tests/tobe` | 회귀 (tobe = TO-BE 병렬 검증) |

**삭제됨:** `text_analyzer.py`, `filters.py`, `session.py`, `file_handler.py`

### 새 카테고리·키워드 추가 방법 (OCP)

| 단계 | 담당 레이어 | 작업 |
|------|-------------|------|
| 1 | **계약** | Gherkin·INV-* · PRD §5.3 에 등록 시나리오 추가 |
| 2 | **RED** | `tests/entity` 에 분류·필터 실패 테스트 |
| 3 | **KeywordRule** | `KeywordRuleRepository` 에 `category` + `keywords[]` 등록 (mission7 File DB/JSON) |
| 4 | **GREEN** | Repository 로드만 변경; **SentimentClassifier core 무변경** |
| 5 | **UI** | `CATEGORIES` / 필터 옵션을 Repository와 동기화 |
| 6 | **REFACTOR** | `constants.py` 는 bootstrap 또는 fallback 으로만 유지 |

**금지:** `filters.py` 에 별도 `S_KEYWORDS` 표를 다시 두는 것 (**INV-SENT-002** 위반).

---

## 테스트 실행

### 사전 설치 (개발)

```bash
cd src/python
.venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
pip install pytest pytest-cov   # PRD 권장; requirements에 없을 수 있음
```

### 실행

```bash
cd src/python
pytest -v tests/
```

| 범위 | 경로 | 비중 |
|------|------|------|
| Entity | `tests/entity/` | 커버리지 **주력** |
| Control | `tests/control/` | 커버리지 **주력** |
| Boundary | `tests/boundary/` | Flask client **소수** |
| Mission 7 | `@pytest.mark.mission7` | Trend·File DB (선택) |

### 커버리지

```bash
pytest --cov=entity --cov=control --cov-report=term-missing tests/
```

**통과 기준:** entity·control 합산 **≥ 90%** ([`doc/PRD.md` G-1](doc/PRD.md)).

### `.cursorrules` TDD 단계 ↔ 미션 매핑

| TDD 단계 | 활동 | 산출물 | 연계 미션 (`project_purpose.md` §6.1) |
|----------|------|--------|--------------------------------------|
| **RED** | 실패 pytest 작성; docstring에 **INV-\*** | Gherkin 8 Scenario 대응 테스트 | **미션 2** (coverage 준비) |
| **GREEN** | 최소 구현으로 통과; `app.py` 에 비즈니스 로직 추가 금지 | **INV-SENT-003** 등 버그 수정 | **미션 3** |
| **REFACTOR** | 전 테스트 green 유지; 구조·이름만 | boundary/control/entity 분리 | **미션 4, 5, 6** |
| **GREEN (mission7)** | Trend·KeywordRule DB | `test_feedback_trend.csv`, File DB | **미션 7** |

**패턴:** Arrange–Act–Assert (AAA). 각 테스트 docstring에 **INV-\*** 1줄 ([`doc/PRD.md` §4.3](doc/PRD.md)).

**회귀 게이트 (RR-5):** main/PR 병합 전 **전체 pytest 0 실패**; mission7은 `-m mission7` 분리 가능.

---

## RED 단계 To-Do 리스트

> 이 체크리스트는 [`doc/test_plan.md`](doc/test_plan.md) 기반으로 생성되었습니다.  
> **RED** 작성 완료 후 **GREEN** 통과(2026-05-22, 52 passed) — 항목 메모는 `GREEN 통과` 기준.

### Track A — UI / Boundary 테스트 (`tests/boundary/`)

- [x] TC-A-01: `POST /analyze` 앵커 `text=배송이 너무 늦어요. 화가 납니다.` → 200, `success`, 부정·배송 집계·원문 표시 (SCN-A Happy Path, TP-10) — GREEN 통과 (X-09 RR-1 **B** `화가` 키워드)
- [x] TC-A-02: `POST /analyze` `text=   ` → 피드백 미추가, 건수·원문 불변 (B-IN-02, **INV-INPUT-001**) — GREEN 통과
- [x] TC-A-03: 피드백 0건 `POST /filter` → `warning`「분석할 피드백 없음」(B-EMP-01, **INV-EMPTY-001**) — GREEN 통과
- [x] TC-A-04: 앵커 적재 → `POST /filter` (`부정`,`배송`) → `GET /download` BOM + `text` 헤더 + 원문 1행 (B-EMP-04, **INV-CSV-OUT-003**) — GREEN 통과
- [x] TC-A-05: `POST /upload` 깨진/빈 CSV → `error`, 기존 세션 건수·원문 불변 (B-UPL-02~03, **INV-SESSION-001**) — GREEN 통과
- [x] TC-A-06: `POST /analyze` 멀티라인 `첫 줄\n둘째 줄` → HTML에 줄바꿈 포함 원문 1건 (B-IN-05, **INV-TEXT-001**) — GREEN 통과
- [x] TC-A-07: `POST /filter` `sentiment=알수없음` → `error` 또는 문서화된 fallback + 메시지 (B-FLT-01, PRD C-09) — GREEN 통과

### Track B — Domain / Logic 테스트 (`tests/entity/`, `tests/control/`)

- [x] TC-B-01: 앵커 문장 분류 → 감정 `부정`, 카테고리 `배송` ≥ 1, `긍정+중립+부정=1` (B-SEN-03, B-CAT-01, **INV-COUNT-002**, TP-01) — GREEN 통과 (X-09)
- [x] TC-B-02: `오늘은 특별한 일이 없었습니다.` → `중립` (**INV-SENT-001**, B-SEN-01) — GREEN 통과
- [x] TC-B-03: `만족스럽지만 별로예요...` → 긍·부 키워드 동시 시 **긍정** (긍→부→중립 순, B-SEN-02) — GREEN 통과
- [x] TC-B-04: Analyze 직후 감정 집계 = `Filter(전체,전체)` 재집계 (**INV-SENT-002**, TP-05, X-01) — GREEN 통과 (04a·04b)
- [x] TC-B-05: `Filter(중립,전체)` 결과에 중립 라벨만 (**INV-SENT-003**, X-02) — GREEN 통과
- [x] TC-B-06: N건 혼합 입력 후 `긍정+중립+부정 == len(feedbacks)` (**INV-COUNT-002**, B-SEN-05, X-03) — GREEN 통과
- [x] TC-B-07: `text=""` / trim 후 공백-only → append 없음 (**INV-INPUT-001**, B-IN-01~03) — GREEN 통과
- [x] TC-B-08: `UploadCsvUseCase` 빈·깨진 파일 → `error` + Repository 건수·원문 불변 (**INV-SESSION-001**, B-UPL-04) — GREEN 통과 (2함수)
- [x] TC-B-09: Filter 스냅샷 행·순서 = Download CSV 본문 (**INV-CSV-OUT-003**, X-04) — GREEN 통과
- [x] TC-B-10: 10_000자 장문 입력 → 원문 equality·분류 완료 (**INV-TEXT-001**, B-IN-04) — GREEN 통과
- [x] TC-B-11: `keyword=배송` 필터 + 앵커(main 매칭) → 1건 반환 (TO-BE main+sub, X-05) — GREEN 통과
- [x] TC-B-12: `SENTIMENT_KEYWORDS` 부분 문자열 매칭 단위 검증 (`constants.py` 기준) — GREEN 통과

### 커버리지 목표 (GREEN 단계 전 RED 골격)

- [x] Entity + Control: **≥ 90%** — `pytest --cov=entity --cov=control tests/` (**100%**, `test_coverage_g1.py` 포함)
- [x] Boundary (`app.py`): **≥ 85%** — `pytest --cov=app tests/boundary/` (**100%**, `test_coverage_boundary.py` 포함)
- [x] 회귀 게이트: `pytest -v tests/` **0 failed** (RR-5) — **52 passed** (2026-05-22, Golden 5건 포함)

### 결함 목록 연결

- [x] [`doc/defect_list.md`](doc/defect_list.md) 생성 및 RED 중 발견 결함 기록 (재현: **X-01**, **X-02**, **X-09**)
- [x] 앵커 `화가` vs `화남` 키워드 정합(X-09) — **RR-1 (B)** `SENTIMENT_KEYWORDS`에 `화가` 추가 · README 앵커 문장 유지
- [x] 결함 **X-01·X-02·X-09** GREEN 수정 후 pytest·**INV-SENT-002/003·INV-COUNT-002** 회귀 통과 (52/52)

---

## REFACTOR 단계 To-Do 리스트

> 기준: [`doc/refactoring_plan.md`](doc/refactoring_plan.md) · 커밋 **C-01~C-14** (`refactoring` 브랜치, 2026-05-22)  
> **범위:** M2 Architecture — **🟢 선택(mission7·JSON API·Trend) 제외**

### Phase 0~5 (M2 핵심)

- [x] C-01~C-02: `FeedbackRepositoryPort` · `FilteredResultStorePort` + `infrastructure/`
- [x] C-03: `fil_data` 제거 → `wiring.filtered_store`
- [x] C-04~C-06: `FeedbackFilter` · `SentimentClassifier` 단일화 · `legacy_labels` 정합
- [x] C-07~C-10: 라우트 4개 → `Analyze` / `Upload` / `Filter` / `Download` Use Case
- [x] C-11~C-12: `boundary/presenter.py` · `boundary/routes.py` · thin `app.py`
- [x] C-13~C-14: `text_analyzer` · `filters` · `session` · `file_handler` 삭제
- [x] 회귀: `pytest -v tests/` **52 passed** (REFACTOR 후)

### REFACTOR 잔여 (비선택·문서)

- [x] Gherkin GH-01 추적 문서 ([`doc/gherkin_gh01.md`](doc/gherkin_gh01.md)) — RR-1 **(B)** `화가`·M2 아키텍처 반영
- [ ] `KeywordRuleRepository` (F-08, ST-06) — **🟢/mission7** 범위
- [ ] `tests/tobe/` → `tests/entity|control` 통합 (Phase 5 선택)
- [ ] 네이밍 `fil`/`sent`/`kw` (M4)

---

## Golden Master 회귀 안전장치

> **Approval / Golden Master** — HTTP·HTML·CSV 계약 고정 (`stdout`·`redirect_stdout` 금지).  
> 기준: [`src/python/tests/golden/`](src/python/tests/golden/) · 실행: `tests/boundary/test_golden_master.py`  
> **전제:** 레거시 RED 출력을 golden으로 고정하지 않음. **GREEN baseline** + **RR-1(X-09, 앵커 부정)** 반영 후 기준 승인.

### 기준 파일·도구 (`src/python/tests/golden/`)

- [x] `feedback_golden_master.txt` GREEN baseline (S1~S4, `[S1: …]` 섹션) — `tests/golden/`, GM-TC 5/5 PASS
- [x] `download_filtered_anchor.csv` GREEN baseline (S5, BOM+`text`+앵커 행) — **INV-CSV-OUT-001~003**
- [x] `normalize.py` — 타임스탬프 `[TIMESTAMP]`, 집계·원문 canonical 추출
- [x] `helpers.py` — `load_section`, `load_csv_golden`, `assert_golden_*`, `difflib.unified_diff` FAIL
- [x] `tests/golden/README.md` — 시나리오·재생성·`APPROVE_GOLDEN` 정책

### Golden Master 테스트 (`tests/boundary/test_golden_master.py`)

| GM ID | 시나리오 | 흐름 | INV / 계약 |
|-------|----------|------|------------|
| GM-TC-01 | **S1** | `POST /analyze` 앵커 `text=배송이 너무 늦어요. 화가 납니다.` | success, 부정·배송 집계, 원문 1건 (**INV-COUNT-002**, X-09) |
| GM-TC-02 | **S2** | `POST /analyze` `text=배송이 빨라서 좋아요` | 긍정·배송 집계 (권장) |
| GM-TC-03 | **S3** | 앵커 적재 후 `POST /analyze` `text=   ` | **INV-INPUT-001** |
| GM-TC-04 | **S4** | 0건 `POST /filter` | **INV-EMPTY-001** |
| GM-TC-05 | **S5** | S1 → `POST /filter`(부정,배송) → `GET /download` | **INV-CSV-OUT-003** |

- [x] GM-TC-01: S1 앵커 analyze — `assert_golden_text` vs `[S1: SCN-A anchor POST /analyze]`
- [x] GM-TC-02: S2 긍정·배송 analyze
- [x] GM-TC-03: S3 공백-only 건수·원문 불변
- [x] GM-TC-04: S4 0건 filter `warning`
- [x] GM-TC-05: S5 CSV 바이트 비교 (`load_csv_golden` / `assert_golden_csv`)

### 회귀 실행·승인 (RR-5 보조)

```bash
cd src/python
pytest -v tests/boundary/test_golden_master.py
pytest -v tests/    # 전체 회귀에 포함 (현재 52건+)
```

| 단계 | 명령 | 비고 |
|------|------|------|
| enforce | `pytest -v tests/boundary/test_golden_master.py` | 기준 있을 때 `actual == expected` |
| 1회 승인 | `APPROVE_GOLDEN=1 pytest …` (PowerShell: `$env:APPROVE_GOLDEN="1"`) | 기준 없음/불일치 시 저장 후 **skip** — baseline 확정 후 계약 변경 시에만 |

- [x] RR-1(X-09) 앵커 부정·`화가` 키워드 README/계약 정합 — Gherkin 선행 갱신은 M2 추적
- [x] Golden pytest 5건 (`test_golden_master.py`) — Approval 회귀 포함
- [x] Golden baseline `tests/golden/` 커밋·`regenerate.py` 운영 — 계약 변경 시 diff 리뷰 (**RR-1**)

---

## 설정 파일 (KeywordRule File DB / JSON·YAML)

**상태:** mission7 **선택** 기능 — 구현 전에는 [`constants.py`](src/python/constants.py) 가 기본값.

### 권장 위치 (목표)

```text
src/python/
  config/
    keyword_rules.json    # 또는 keyword_rules.yaml
  data/
    test_feedback_trend.csv
```

### JSON 예시 (`keyword_rules.json`)

```json
{
  "version": 1,
  "categories": {
    "배송": {
      "main": ["배송", "택배", "배달"],
      "sub": {
        "time": ["배송지연", "배송시간"]
      }
    },
    "프로모션": {
      "main": ["이벤트-프로모션", "할인행사"]
    }
  }
}
```

> **주의:** 감정 키워드는 **SentimentClassifier** / `constants.SENTIMENT_KEYWORDS` 가 단일 허브이다. 위 JSON 예시는 **카테고리(KeywordRule)만** 외부화하는 것을 권장하며, `sentiment` 블록을 넣을 경우 ST-05·**INV-SENT-002** 와 동기화해야 한다.

### 동적 키워드 등록 계약 ([`doc/PRD.md` §5.3](doc/PRD.md))

| 필드 | 값 |
|------|-----|
| `category` | `배송` \| `품질` \| `가격` \| `서비스` \| `사용성` 또는 신규명 |
| `keywords` | `["이벤트-프로모션", ...]` |
| 검증 문장 | `이번 이벤트-프로모션 정말 좋았어요` → 해당 카테고리 매칭, 원문 불변 (**INV-RULE-002**) |

### 로드 실패 시 (ST-05)

| 정책 | 동작 |
|------|------|
| **B (PRD 기본)** | `constants.py` fallback + `warning` |
| A (대안) | 이전 유효 규칙 유지 + `error` 로그 — 채택 시 PRD §5.2·본 절 동시 개정 |

---

## 출력 포맷

### 웹 페이지

**원문 + 집계 예시**

```text
[success] 2026-05-21 10:00:00 : 1개의 피드백이 입력되었습니다.

감정 분포
  긍정: 0    중립: 0    부정: 1

키워드 분포
  배송: 1    품질: 0    ...

(표시 원문) 배송이 너무 늦어요. 화가 납니다.
```

**메시지 스키마**

| 필드 | CSS 클래스(현재) | 용도 |
|------|------------------|------|
| `success` | `alert-success` | 입력·분석 성공 |
| `warning` | `alert-warning` | 0건·무결과 (**PageLogSink** level에 warning 포함 시) |
| `error` | `alert-danger` | 업로드·처리 오류 |

### CSV 다운로드 (`filtered_feedback.csv`)

```csv
text
배송이 너무 늦어요. 화가 납니다.
```

| 규칙 | Invariant |
|------|-----------|
| 파일 선두 UTF-8 BOM | INV-CSV-OUT-001 |
| 1행 헤더 `text` | INV-CSV-OUT-002 |
| 2행~ = 필터 스냅샷 순서 | **INV-CSV-OUT-003** |

### PageLogSink (목표, 미션 3)

```yaml
# 예: config/log_display.yaml (목표)
levels:
  success: true
  warning: true
  error: true
```

`warning: false` 이면 warning 배너 HTML 미렌더.

### 집계 (INV-COUNT-002)

```text
긍정 건수 + 중립 건수 + 부정 건수 = 분석 대상 피드백 총건수
```

---

## 생성형 AI 활용 Activities

총 **약 13시간** — [`project_purpose.md` §6.1](project_purpose.md) · [`doc/PRD.md`](doc/PRD.md) 정합.

| 미션 | 시간 | 산출물 | TDD 단계 |
|------|------|--------|----------|
| 1 개요·실습 준비 | 1h | 환경·미션 로드맵·본 README 숙지 | — |
| 2 테스트 구조·case | 2h | `tests/` 골격, **coverage ≥ 90%** 목표, INV-* RED | **RED** |
| 3 버그(중립 필터·multiline·PageLogSink) | 1.5h | **INV-SENT-003** 등 GREEN | **GREEN** |
| 4 네이밍·매직넘버·전역 | 1h | Repository/Store 도입 설계 | REFACTOR 준비 |
| 5 긴 함수·중복 제거 | 1.5h | Presenter·UseCase 분리 | **REFACTOR** |
| 6 리팩터 1건 추가 | 1h | BCE 디렉터리 정리 | **REFACTOR** |
| 7 Trend·File DB | 3h | `test_feedback_trend.csv`, KeywordRule DB | **GREEN** (mission7) |
| 8 팀 리뷰·발표 | 2h | Before/After·장단점 | — |

### AI 사용 시 권장 프롬프트 맥락

- 현재 TDD 단계: **REFACTOR (M2 완료)** — 신규 동작은 RED부터
- 준수 Invariant: 예) `INV-SENT-002`
- 레이어: 변경 허용 경로만 명시 (`entity/…`)

---

## 기여 가이드

1. **계약 변경 순서:** [`doc/PRD.md`](doc/PRD.md) → Phase 4 Gherkin → README → 코드 (**RR-1**).
2. **이중 감정 규칙**(`constants` vs `filters.S_KEYWORDS`) 재도입 PR 금지 (**RR-3**).
3. `fil_data`·`global_sent`·`Session` 클래스 변수 재도입 금지 (**RR-4**).
4. `entity` 레이어에 Flask·HTML·`print` 디버그 금지 ([`.cursorrules`](.cursorrules)).
5. 포맷: `black`, `isort` (line-length 88), **타입 힌트 필수**.
6. 커밋·push는 메인테이너 요청 시; `src/python/.venv` 커밋 금지.
7. **RR-5:** 병합 전 전체 pytest 0 실패.
8. `Cursor AI_퀴즈 - 문제.docx` 를 이슈·PR·README에 링크하지 않음 (**NG-2**).

---

## 라이선스

MIT License — 자유 이용·수정·배포 가능. 상세 전문은 저장소 `LICENSE` 파일이 추가되면 그 내용을 따릅니다.

---

## 관련 문서

| 문서 | 설명 |
|------|------|
| [`doc/PRD.md`](doc/PRD.md) | 제품 요구사항 (**Phase 4** Epic/Story/Gherkin 기준, v1.1) |
| [`project_purpose.md`](project_purpose.md) | 리팩토링 챌린지 목적·코드 스멜·미션 |
| [`.cursorrules`](.cursorrules) | TDD·아키텍처·forbidden 규칙 |
| [`doc/refactoring_plan.md`](doc/refactoring_plan.md) | M2 REFACTOR 실행 계획·C-01~C-14 완료 기록 |
| [`doc/gherkin_gh01.md`](doc/gherkin_gh01.md) | Phase 4 Gherkin GH-01 추적 (RR-1·pytest 매핑) |
| [`doc/OLD_README.md`](doc/OLD_README.md) | 이전 간단 README 보관 |

---

## TO-DO LIST

> **기준:** [`doc/PRD.md`](doc/PRD.md) §7 · Phase 4 Gherkin · `.cursorrules`  
> **Story:** Phase 4 공식 **ST-01~06** ([`doc/PRD.md` 부록 C](doc/PRD.md)). ST-07~10 은 구현·미션 추적용 파생 ID.  
> **INV:** PRD §7.1·§8 · Gherkin · `.cursorrules` 동일 표기.  
> **우선순위:** M1 = INV·pytest 통과(동작, F-01~06). M2 = BCE·전역·Presenter(`[M2]`).  
> **완료:** 레거시 UI는 미검증. `[x]` = §7.1 해당 항목·pytest·Gherkin 통과 후.

### 🔴 필수 (Must-Have) — v1.0 차단 항목 (M1)

- [x] 피드백 입력 검증 (trim, 공백-only 미추가, **멀티라인 1건**) | ST-01, F-01 | INV-INPUT-001, INV-TEXT-001 — TC-A-02·06, TC-B-07
- [x] SentimentClassifier 단일 허브 (긍정→부정→중립, Analyze=Filter 동일) | ST-02 | INV-SENT-002 — `entity/sentiment_classifier.py`, TC-B-04
- [x] 중립 감정 필터 ("중립" 선택 시 중립만 반환) | ST-02 | INV-SENT-003 — TC-B-05
- [x] 수동·CSV 피드백 수집 (UTF-8 BOM, 헤더 text, 빈 행 스킵) | ST-01 | INV-SESSION-001 — TC-A-05, TC-B-08, `control/upload_csv.py`
- [x] 감정·카테고리 집계 (긍정+중립+부정 합=대상 건수) | ST-03 | INV-COUNT-002 — TC-B-01·06
- [x] 필터·다운로드 계약 (POST /filter, GET /download, BOM+text) | ST-04 | INV-CSV-OUT-003 — TC-A-04, TC-B-09, GM-TC-05
- [x] 피드백 원문 보존 (표·export 입력 문자열 그대로) | ST-04 | TC-B-10, TC-A-06, `HtmlPresenter` 원문

### 🟡 권장 (Should-Have) — M2

- [x] Dual-Track BCE 분리 (boundary/control/entity, app.py thin) [M2] | ST-05 | `boundary/`, `entity` Flask import 없음
- [ ] KeywordRuleRepository(Port) + OCP [M2] | ST-06 | **🟢/mission7 범위** — 현재 `constants.CATEGORY_KEYWORDS`
- [x] FilteredResultStore·FeedbackRepository (fil_data·Session 제거) [M2] | ST-05 | `infrastructure/`, `tests/support/port_fakes.py`
- [ ] 동적 키워드 등록 (카테고리명 + 키워드 목록) | ST-06 | **🟢/mission7** — F-08 선행
- [ ] PageLogSink level별 페이지 표시 (warning/error) | ST-07, F-14 | **선택(미션3)** — 현재 `Logger` print
- [x] pytest-cov entity·control ≥90% | ST-08 | G-1 달성 (`tests/control/test_coverage_g1.py`)

### 🟢 선택 (Nice-to-Have) — v2.0 / M3

- [ ] Trend 시각화 (test_feedback_trend.csv) | ST-09 | @pytest.mark.mission7
- [ ] 감정·키워드 File DB 관리 | ST-09 | KeywordRule 영속화
- [ ] 멀티라인 텍스트 입력 UI (폼 UX) | — | 계약은 F-01·INV-TEXT-001 (🔴과 중복 시 UI만 🟢)
- [ ] JSON API 응답 (집계·필터 결과) | ST-10, F-13 | **INV-JSON-001**, PRD §6.5

### 🔵 기술 부채 — M2~M4 (동작 변경 시 RED부터 재시작)

- [x] app.py `render_page`·라우트 God Function 분리 [M2] | `boundary/presenter.py`, `boundary/routes.py`
- [x] `text_analyzer`·`filters`·`S_KEYWORDS` 제거 [M2] | **RR-3** — 파일 삭제 완료
- [x] 이중 감정 규칙 제거 [M2] | `SentimentClassifier` 단일; 카테고리는 `constants` 유지 (F-08은 미착수)
- [x] `fil_data`·`global_sent`·`Session` 전역 제거 [M2] | **RR-4** — `infrastructure/wiring.py`
- [x] `file_handler.py` Lava Flow [M4] | 삭제 완료 (C-14)
- [ ] 네이밍 fil/sent/kw/fil_data [M4] | 도메인 용어 rename | 미션4

### ✅ 완료 항목

- [x] 테스트 계획서 [`doc/test_plan.md`](doc/test_plan.md) v1.0 | 2026-05-22 | TC-A/B·INV 매핑
- [x] RED pytest 골격 (`tests/entity`, `control`, `boundary`, `tobe`) | 2026-05-22 | TC-A-01~07, TC-B-01~12, docstring **INV-\***
- [x] 결함 목록 [`doc/defect_list.md`](doc/defect_list.md) | 2026-05-22 | X-01, X-02, X-09 재현
- [x] TO-BE `entity/`, `control/` 런타임 연동 + `tests/tobe/` | 2026-05-22 | RED 13건 → REFACTOR 후 52 passed
- [x] RED 부분 통과 (레거시·계약 일치 구간) | 2026-05-22 | **INV-INPUT-001**, **INV-SESSION-001**, **INV-EMPTY-001**, **INV-SENT-001**(TC-B-02), TC-B-03·07·08·09·10·12
- [x] GREEN M1 (TC-A/B·tobe·Golden) | 2026-05-22 | **52 passed**, X-01·X-02·X-09 수정, §7.1 핵심 INV
- [x] Golden Master baseline·GM-TC-01~05 | 2026-05-22 | `tests/golden/`, `test_golden_master.py`
- [x] PRD G-1 커버리지 entity·control ≥90% | 2026-05-22 | **100%** (`test_coverage_g1.py`, `test_coverage_boundary.py`)
- [x] REFACTOR M2 (C-01~C-14) | 2026-05-22 | [`doc/refactoring_plan.md`](doc/refactoring_plan.md) · `origin/refactoring`

<!-- [x] 항목 | 완료일 | 통과 INV/pytest/Gherkin — 🔴 Must-Have·M2는 GREEN·§7.1 전체 통과 후 [x] -->

### 📋 회귀 방지 체크리스트

- [x] INV-SENT-002 · INV-SENT-003 · INV-COUNT-002 — TC-B-04·05·06, TC-B-01
- [x] INV-CSV-OUT-003 — TC-A-04, TC-B-09, GM-TC-05
- [x] INV-INPUT-001 · INV-SESSION-001 · INV-EMPTY-001 — TC-A-02·03·05, TC-B-07·08
- [x] INV-TEXT-001 — TC-B-10, TC-A-06
- [x] PRD §7.1 ↔ Gherkin ↔ README INV 용어 동일 (**RR-1**) — X-09 **(B)** `화가`; [`doc/gherkin_gh01.md`](doc/gherkin_gh01.md)
- [x] RR-3 `S_KEYWORDS` 제거 · RR-4 `fil_data`/Session 전역 제거 — REFACTOR C-01~C-14 (2026-05-22)
- [x] RR-5 전체 pytest 0 실패 — **52 passed** / 0 failed (2026-05-22)
- [x] Cursor AI_퀴즈 - 문제.docx 미반영 (**NG-2**)

### 🗓️ 마일스톤

| 마일스톤 | 범위 | 차단 TO-DO |
|----------|------|------------|
| M1 v1.0 Domain | ST-01~04, 🔴 전부 | INV·Gherkin·핵심 pytest |
| M2 v1.1 Architecture | ST-05~08, 🟡·🔵 [M2] | **핵심 완료** (F-08·ST-06·PageLogSink·🟢 제외) |
| M3 v2.0 Extension | ST-09~10, 🟢 | mission7·Trend·File DB |
| M4 Debt sweep | 🔵 [M4] | 리팩터 only |
