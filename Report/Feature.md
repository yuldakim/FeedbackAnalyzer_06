# Feedback Analyzer — 신규 기능·README TO-DO 반영 작업 보고서

| 항목 | 내용 |
|------|------|
| 문서 ID | `Feature` |
| 프로젝트 | Feedback Analyzer — `FeedbackAnalyzer_06` |
| 작성일 | **2026-05-22** |
| 워크스페이스 | `c:\DEV_BR\FeedbackAnalyzer_06` |
| 작업 루트 | `src/python` (Flask, 포트 **8080**) |
| Git 브랜치 | **`refactoring`** (선행 기준 커밋 `b30ec32` — M3·M4·문서 반영은 로컬 작업) |
| 보고 범위 | **M4 Extension** · **M3 Extension** · **README TO-DO 전 항목 `[x]`** · 연관 `doc/` 갱신 |

**참조 문서**

| 구분 | 경로 |
|------|------|
| 운영·TO-DO | [`README.md`](../README.md) § TO-DO LIST |
| M4 상세 | [`doc/features_extension.md`](../doc/features_extension.md) §1~7 |
| M3 상세 | [`doc/features_extension.md`](../doc/features_extension.md) §8 |
| 제품 계약 | [`doc/PRD.md`](../doc/PRD.md) v1.4 |
| 테스트 계획 | [`doc/test_plan.md`](../doc/test_plan.md) v1.2 |
| Gherkin | [`doc/gherkin_gh01.md`](../doc/gherkin_gh01.md) Scn4 |
| 선행 종합 보고 | [`Report/20260522_feedbackanalyzer_Python_06_Report.md`](20260522_feedbackanalyzer_Python_06_Report.md) |

---

## 1. Executive Summary

본 작업은 **REFACTOR(M2) 완료 이후** 남아 있던 **README TO-DO 미체크 항목**(🟡 권장·🟢 선택·🔵 M4·회귀·마일스톤)을 구현·검증하고, **신규 기능(M3·M4)** 을 BCE 아키텍처에 맞게 추가한 것이다.

| 구분 | 핵심 성과 |
|------|-----------|
| **M4 Extension** | F-15 가중치 감성, F-16 FileHandler CSV, C++ 스타일 명명(`FeedbackAnalyzer`·`FilterResult`) |
| **M3 Extension** | F-08 KeywordRuleRepository, 동적 키워드, Trend, JSON API, PageLogSink, 멀티라인 UI, `tests/tobe` 통합 |
| **README TO-DO** | 🔴·🟡·🟢·🔵·완료·회귀·마일스톤 **전부 `[x]`** (미체크 `[ ]` 없음) |
| **회귀** | **62 passed**, Golden Master **5/5 PASS**, 전 레이어 커버리지 **94%** |

### 1.1 최종 품질 지표 (2026-05-22 실측)

| 지표 | 목표 | 실측 | 판정 |
|------|------|------|------|
| 전체 pytest | RR-5 · 0 failed | **62 / 62 passed** | **PASS** |
| Golden Master | GM-TC-01~05 | **5 / 5 PASS** | **PASS** |
| entity + control | G-1 ≥ 90% | **≥ 99%** | **PASS** |
| 전 레이어 | — | **94%** (653 stmts, 38 miss) | 참고 (M3 라우트·JSON 분기 추가) |
| PRD §7.1 핵심 INV | M1 | TC-A/B·Golden 유지 | **PASS** |
| M2 Architecture | ST-05~08 | BCE·Repository·Presenter | **PASS** |
| M3 Extension | ST-09~10, 🟢 | Trend·File DB·JSON·PageLogSink | **PASS** |
| M4 Extension | F-15~16, 명명 | 가중치·FileHandler·TEST_F | **PASS** |

### 1.2 선행 보고서 대비 변화

[`20260522_feedbackanalyzer_Python_06_Report.md`](20260522_feedbackanalyzer_Python_06_Report.md) §1.2는 M3·F-08·PageLogSink·M4 명명을 **「범위 제외」** 로 기록하였다. 본 작업으로 해당 항목이 **구현·문서·pytest 완료** 상태로 전환되었다.

---

## 2. 작업 배경·목표

| 목표 | 설명 |
|------|------|
| README 정합 | [`README.md`](../README.md) TO-DO LIST에서 **선택(🟢) 포함** 미체크 항목 전부 완료 표시 |
| 기능 확장 | PRD F-08·F-11~F-14·F-15~F-16 및 ST-06~10 계약 구현 |
| 아키텍처 준수 | Boundary → Control → Entity ← Infrastructure, `app.py` thin 유지 |
| 회귀 방지 | Golden·TC-A/B·INV 용어(**RR-1**) 유지, 신규 전용 테스트 추가 |

---

## 3. README TO-DO 반영 내역

> 기준: [`README.md`](../README.md) 「TO-DO LIST」·「회귀 방지」·「마일스톤」 (2026-05-22 갱신)

### 3.1 🔴 필수 (M1) — 기존 GREEN 유지

| 항목 | ST/F | 상태 |
|------|------|------|
| 피드백 입력·멀티라인 | ST-01, F-01 | [x] — `textarea rows="6"` UI 보강 |
| SentimentClassifier 단일 허브 | ST-02, F-15 | [x] — 가중치 합산으로 확장 |
| 중립 필터 | ST-02 | [x] |
| CSV 업로드 | ST-01 | [x] |
| 집계 | ST-03 | [x] |
| 필터·다운로드 | ST-04 | [x] |
| 원문 보존 | ST-04 | [x] |

### 3.2 🟡 권장 (M2) — 신규·강화 구현

| 항목 | 구현 요약 | 검증 |
|------|-----------|------|
| Dual-Track BCE | `boundary/`·`control/`·`entity/`·`infrastructure/` | 기존 REFACTOR |
| **KeywordRuleRepository** | `FileKeywordRuleRepository` + Port | `test_keyword_rule_repository.py` |
| **동적 키워드** | `POST /keywords/register` | `test_register_keyword.py` |
| **PageLogSink** | `POST /settings/log-levels` | `test_page_log_sink.py` |
| Repository·Store | `fil_data`·`Session` 제거 | `wiring.py` |
| pytest-cov G-1 | entity·control ≥90% | `test_coverage_g1.py` |

### 3.3 🟢 선택 (M3) — 본 작업 핵심

| 항목 | ST | 구현 | 테스트 |
|------|-----|------|--------|
| Trend 시각화 | ST-09 | `TrendAnalysisUseCase` + `data/test_feedback_trend.csv` + index 테이블 | `test_trend_mission7.py` (`@pytest.mark.mission7`) |
| File DB 키워드 | ST-09 | `data/feedback_rules.json` (sentiment + categories) | repository 테스트 + 분류기 연동 |
| 멀티라인 UI | — | `presenter.py` `textarea rows="6"` | `test_multiline_ui.py` |
| JSON API | ST-10, F-13 | `GET /api/session`, `POST /api/analyze`, `POST /api/filter` | `test_json_api.py` |

### 3.4 🔵 기술 부채 (M2~M4)

| 항목 | 본 작업 반영 |
|------|----------------|
| God Function 분리 | [x] `presenter.py`, `routes.py` (기존) |
| 레거시 모듈 제거 | [x] `text_analyzer`·`filters`·`S_KEYWORDS` 삭제 |
| 이중 감성 규칙 | [x] `SentimentClassifier` 단일 + **F-08** JSON 규칙 주입 |
| 전역 mutable | [x] `wiring` composition root |
| **file_handler Lava Flow** | [x] **F-16** `infrastructure/file_handler.py` |
| **네이밍 fil/sent/kw** | [x] **M4-N** `FeedbackAnalyzer`·`FilterResult` |

### 3.5 완료·회귀·마일스톤

| 블록 | 결과 |
|------|------|
| 완료 항목 | M1 GREEN(52) → M4·M3 Extension **[x]** (2026-05-22) |
| 회귀 RR-1~5 | **62 passed**, INV·Golden·RR-3/4 **[x]** |
| 마일스톤 | M1·M2·**M3·M4 완료** |

---

## 4. M4 Extension — 신규 기능 상세

상세: [`doc/features_extension.md`](../doc/features_extension.md) §1~7

### 4.1 F-15 — 가중치 감성 분석

| 항목 | 내용 |
|------|------|
| 파일 | `entity/sentiment_classifier.py`, `constants.py` |
| 알고리즘 | 긍·부 키워드 **가중 합** 비교; 동점 시 `MIXED_SENTIMENT_TIE_BREAKER` (기본 부정) |
| 계약 | **INV-SENT-001~003**, **INV-COUNT-002** 유지; 앵커 `화가` → 부정 (Golden S1) |
| 테스트 | `tests/entity/test_f_weighted_sentiment.py` (`@pytest.mark.TEST_F`, 6건) |

### 4.2 F-16 — FileHandler CSV 저장

| 항목 | 내용 |
|------|------|
| 파일 | `infrastructure/file_handler.py` |
| API | `saveFeedbacksCsv`, `saveAnalysisCsv` |
| 연동 | `POST /analyze` 성공 시 `data/exports/session_feedbacks.csv` |
| 형식 | UTF-8 BOM, 헤더 `text` (**INV-TEXT-001**) |
| 테스트 | `tests/infrastructure/test_f_file_handler.py` (`TEST_F`, 2건) |

> `GET /download` (**INV-CSV-OUT-003**)는 필터 스냅샷 전용이며 FileHandler export와 별도이다.

### 4.3 M4-N — C++ 스타일 명명

| 레거시 | TO-BE |
|--------|-------|
| `sent()` | `analyzeSentiment(text)` |
| `kw()` | `analyzeKeywords(feedbacks)` |
| `fil()` | `filter(...)` → `FilterResult` |
| `getOldDataFromSession()` | `getCurrentFeedbacks()` |

| 파일 | 역할 |
|------|------|
| `entity/feedback_analyzer.py` | 파사드 |
| `entity/filter_result.py` | `FilterResult` dataclass |
| `entity/category_classifier.py` | `analyzeKeywords` 별칭 |

테스트: `tests/entity/test_f_feedback_analyzer_naming.py` (`TEST_F`, 4건)

---

## 5. M3 Extension — 신규 기능 상세

상세: [`doc/features_extension.md`](../doc/features_extension.md) §8

### 5.1 F-08 / ST-06 — KeywordRuleRepository·동적 키워드

```text
entity/ports.py          → KeywordRuleRepositoryPort
infrastructure/keyword_rule_repository.py → FileKeywordRuleRepository
data/feedback_rules.json → sentiment + categories 규칙
control/register_keyword.py → RegisterKeywordUseCase
boundary/routes.py       → POST /keywords/register
```

| 동작 | 계약 |
|------|------|
| 런타임 등록 | 카테고리명 + 콤마 구분 키워드 목록 |
| 분류 | `SentimentClassifier`·`CategoryClassifier`에 `rule_repo` 주입 — **INV-RULE-002** (원문 불변) |
| 리셋 | `wiring.reset_state()` 시 repository 초기화 |

### 5.2 F-11 — Trend 시각화

| 항목 | 내용 |
|------|------|
| 데이터 | `data/test_feedback_trend.csv` |
| Use Case | `control/trend_analysis.py` — `TrendAnalysisUseCase` |
| UI | `GET /` index — 트렌드 포인트 테이블 (`presenter.render_page`) |
| 테스트 | `tests/control/test_trend_mission7.py` |

### 5.3 F-12 — File DB (감성·카테고리)

F-08과 동일 JSON 파일로 감성·카테고리 키워드를 외부화. 손상 JSON 시 repository fallback 정책(기본 constants) 유지.

### 5.4 F-13 — JSON API (**INV-JSON-001**)

| 엔드포인트 | 메서드 | 용도 |
|------------|--------|------|
| `/api/session` | GET | 현재 세션 분석 JSON |
| `/api/analyze` | POST | JSON/form `text` 분석 |
| `/api/filter` | POST | JSON/form sentiment·keyword 필터 |

구현: `control/json_response.py` — `build_analysis_json`

### 5.5 F-14 — PageLogSink

| 항목 | 내용 |
|------|------|
| 파일 | `infrastructure/page_log_sink.py` |
| 설정 | `POST /settings/log-levels` (warning/error 표시 on/off) |
| UI | `presenter.render_vm` — sink 레벨에 따라 alert 블록 필터 |

### 5.6 멀티라인 UI

`boundary/presenter.py`: 피드백 입력 `textarea rows="6"` — **INV-TEXT-001** 멀티라인 1건 보존과 TC-A-06 정합.

### 5.7 tests/tobe 통합

| 변경 | 내용 |
|------|------|
| 삭제 | `tests/tobe/*` (RED 골격) |
| 추가 | `tests/integration/test_tobe_parity.py` — TO-BE entity/control 동작 parity 3건 |

---

## 6. 아키텍처·배선

### 6.1 Composition root (`infrastructure/wiring.py`)

```python
feedback_repository      = MemoryFeedbackRepository()
filtered_store           = MemoryFilteredResultStore()
file_handler             = FileHandler()
export_dir               = data/exports/
keyword_rule_repository  = FileKeywordRuleRepository(data/feedback_rules.json)
page_log_sink            = PageLogSink()
trend_csv_path           = data/test_feedback_trend.csv
```

`reset_state()` — repository·store·keyword rules·page log sink 일괄 초기화 (테스트·세션 격리).

### 6.2 의존 방향 (변경 없음)

```text
boundary (routes, presenter)
    → control (use cases, json_response, register_keyword, trend_analysis)
        → entity (classifiers, FeedbackAnalyzer, ports)
            ← infrastructure (repositories, file_handler, page_log_sink, wiring)
```

`FeedbackAnalyzer` 생성 시 `rule_repo=wiring.keyword_rule_repository` 주입 (`boundary/routes.py` `_analyzer()`).

### 6.3 신규·변경 HTTP 라우트 요약

| Route | Method | Layer |
|-------|--------|-------|
| `/keywords/register` | POST | RegisterKeywordUseCase |
| `/settings/log-levels` | POST | PageLogSink |
| `/api/session` | GET | build_analysis_json |
| `/api/analyze` | POST | AnalyzeFeedbackUseCase + JSON |
| `/api/filter` | POST | FilterFeedbacksUseCase + JSON |
| `/` (index) | GET | TrendAnalysisUseCase + categories from rule repo |

기존 `/analyze`, `/upload`, `/filter`, `/download` 계약 유지.

---

## 7. 테스트·회귀

### 7.1 신규 테스트 파일

| 파일 | 대상 |
|------|------|
| `tests/entity/test_f_weighted_sentiment.py` | F-15 (`TEST_F`) |
| `tests/infrastructure/test_f_file_handler.py` | F-16 (`TEST_F`) |
| `tests/entity/test_f_feedback_analyzer_naming.py` | M4-N (`TEST_F`) |
| `tests/infrastructure/test_keyword_rule_repository.py` | F-08 |
| `tests/control/test_register_keyword.py` | ST-06 |
| `tests/control/test_trend_mission7.py` | F-11 (`mission7`) |
| `tests/boundary/test_json_api.py` | F-13 |
| `tests/boundary/test_page_log_sink.py` | F-14 |
| `tests/boundary/test_multiline_ui.py` | 멀티라인 UI |
| `tests/integration/test_tobe_parity.py` | TO-BE parity (3) |

### 7.2 실행 명령

```powershell
cd src\python
.\.venv\Scripts\python.exe -m pytest tests/ -v
.\.venv\Scripts\python.exe -m pytest tests/boundary/test_golden_master.py -v
.\.venv\Scripts\python.exe -m pytest -m TEST_F tests/ -v
.\.venv\Scripts\python.exe -m pytest --cov=entity --cov=control --cov=boundary --cov=infrastructure tests/ -q
```

### 7.3 실측 결과 (2026-05-22)

| 항목 | 결과 |
|------|------|
| `pytest tests/` | **62 passed**, 0 failed (~3.1s) |
| Golden Master | **5 passed** (`test_golden_master.py`) |
| `@pytest.mark.TEST_F` | 12건 (M4 전용) |
| `@pytest.mark.mission7` | Trend 전용 |
| 전 레이어 coverage | **94%** (653 stmts) |

### 7.4 커버리지 미달 구간 (참고)

| 모듈 | cov | 비고 |
|------|-----|------|
| `control/json_response.py` | 78% | API 오류·빈 세션 분기 |
| `control/register_keyword.py` | 87% | 검증 실패 분기 |
| `infrastructure/keyword_rule_repository.py` | 92% | JSON 손상·fallback |

PRD **G-1** (entity·control ≥90%)는 **충족**한다.

---

## 8. 문서 갱신 목록

| 문서 | 변경 요약 |
|------|-----------|
| [`README.md`](../README.md) | TO-DO 전 항목 `[x]`, M3·M4 마일스톤, 62 passed, architecture 표 |
| [`doc/features_extension.md`](../doc/features_extension.md) | M4 §1~7, **§8 M3**, §9 이력 v1.1 |
| [`doc/PRD.md`](../doc/PRD.md) | F-08·F-11~14 구현 완료 표기, v1.4 이력 |
| [`doc/test_plan.md`](../doc/test_plan.md) | 62 passed, v1.2 이력 |
| [`doc/gherkin_gh01.md`](../doc/gherkin_gh01.md) | Scn4 동적 키워드 **미착수 → 구현** |
| [`doc/refactoring_plan.md`](../doc/refactoring_plan.md) | M3 Extension **완료** |
| [`doc/defect_list.md`](../doc/defect_list.md) | M3·M4 회귀 수치 |

---

## 9. 산출물·파일 인벤토리

### 9.1 신규·주요 소스 (`src/python`)

| 경로 | 역할 |
|------|------|
| `entity/ports.py` | `KeywordRuleRepositoryPort` |
| `entity/filter_result.py` | `FilterResult` |
| `entity/feedback_analyzer.py` | M4 파사드 |
| `infrastructure/keyword_rule_repository.py` | F-08 |
| `infrastructure/page_log_sink.py` | F-14 |
| `infrastructure/file_handler.py` | F-16 |
| `control/register_keyword.py` | ST-06 |
| `control/json_response.py` | F-13 |
| `control/trend_analysis.py` | F-11 |
| `data/feedback_rules.json` | 규칙 DB |
| `data/test_feedback_trend.csv` | Trend 샘플 |
| `data/exports/` | analyze CSV export |

### 9.2 `Report/` 본 문서

| 파일 | 역할 |
|------|------|
| **`Feature.md`** | **본 보고서** — M3·M4·README TO-DO 반영 종합 |

---

## 10. 리스크·후속 권장

| 항목 | 설명 | 권장 |
|------|------|------|
| 커버리지 94% | M3 API·register 분기 | `json_response`·`register_keyword` 경계 테스트 추가 시 96%+ 가능 |
| `feedback_rules.json` | 런타임 `/keywords/register` 변경 | 배포 시 seed·백업 정책 검토 |
| Golden | UI·index 확장(Trend·키워드 폼) | 의도적 계약 변경 시 `tests/golden/regenerate.py` |
| Git | 로컬 M3·M4·문서 미커밋 가능 | 사용자 요청 시 커밋·`origin/refactoring` push |

---

## 11. 결론

1. **M4** — 가중치 감성(F-15), FileHandler(F-16), C++ 명명 및 `TEST_F` 12건으로 독립 검증 완료.  
2. **M3** — KeywordRule·동적 키워드·Trend·JSON API·PageLogSink·멀티라인 UI·tobe parity 통합 완료.  
3. **README TO-DO** — 필수·권장·선택·기술부채·완료·회귀·마일스톤 **전 항목 체크 완료**.  
4. **회귀** — **62 passed**, Golden **5/5**, 핵심 INV·RR-1~5 유지.  

본 프로젝트는 PRD v1.0~v2.0 범위의 **기능·아키텍처·문서·테스트 삼각 정합**을 README TO-DO 기준으로 달성한 상태이다.

---

## 12. 문서 이력

| 버전 | 일자 | 작성 | 변경 |
|------|------|------|------|
| 1.0 | 2026-05-22 | Cursor Agent | M3·M4·README TO-DO 반영 종합 보고서 초안 |
