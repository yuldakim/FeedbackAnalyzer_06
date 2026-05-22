# 테스트 계획서 — Feedback Analyzer

| 항목 | 값 |
|------|-----|
| 문서 버전 | 1.0 |
| 작성 관점 | 시니어 QA 리드 |
| 기준 샘플 | `POST /analyze` — 감정·카테고리 분류 및 집계 |
| 앵커 입력 | `text=배송이 너무 늦어요. 화가 납니다.` |
| 참조 | [`README.md`](../README.md), [`doc/PRD.md`](PRD.md), [`.cursorrules`](../.cursorrules) |
| 실행 루트 | `src/python` |
| 스택 | Python 3.11+, Flask 3.x, pytest, pytest-cov |
| 아키텍처 | Dual-Track — `boundary` / `control` / `entity` |

---

## 1. 목적·범위

### 1.1 목적

앵커 예제를 중심으로 **F-01~F-06**(피드백 입력·분류·집계·필터·CSV)과 **INV-\*** 불변식을 pytest로 고정한다. 레거시(`text_analyzer` / `filters.S_KEYWORDS` 이중 규칙, `Session` 클래스 변수, `fil_data` 전역)는 **회귀·특이 케이스**로 명시하고, TO-BE는 **단일 `SentimentClassifier` + Port** 기준으로 검증한다.

### 1.2 In-Scope

| 구분 | 내용 |
|------|------|
| 핵심 Journey | SCN-A (`POST /analyze`) → SCN-C (`POST /filter`, `GET /download`) |
| 계약 | PRD §3.2, §3.3, §6.1~6.4, README 입력·출력 예시 |
| 테스트 레이어 | `tests/entity` (주력), `tests/control`, `tests/boundary` (Flask client 소수) |
| 인수 | PRD §7.1, README TO-DO 🔴, G-1~G-5 |

### 1.3 Out-of-Scope (본 계획서)

| ID | 제외 |
|----|------|
| NG-1 | LLM·딥러닝 감정 분석 |
| NG-2 | `Cursor AI_퀴즈 - 문제.docx` |
| NG-3 | 프로덕션 배포·인증·다국어 |
| M3 | `@pytest.mark.mission7` (Trend, File DB) — 별도 부록만 참조 |

---

## 2. 앵커 시나리오 (기준 예제)

### 2.1 참조

| 문서 | 참조 |
|------|------|
| README | 「예시 입출력 (1분 데모)」2단계; 「입력 형식 계약」정상 예시 1; 「출력 포맷」 |
| PRD | F-01, F-02, F-03, F-05; §3.2 `POST /analyze`; SCN-A; §5.1 `SENTIMENT_KEYWORDS` |
| Story | ST-01, ST-02, ST-03 |
| Gherkin (추적) | GH-01 Scn2, Scn6, Scn7 |

### 2.2 Given / When / Then (계약 기준)

| 단계 | 내용 |
|------|------|
| **Given** | 세션에 피드백 0건(또는 격리된 `FeedbackRepository` fake) |
| **When** | `POST /analyze`, `Content-Type: application/x-www-form-urlencoded`, `text=배송이 너무 늦어요. 화가 납니다.` |
| **Then** | `success`: `1개의 피드백이 입력되었습니다.`(또는 동등 문구); `sentiment_results`: 긍0·중0·부1; `keyword_results`: `배송` ≥ 1; 원문 불변 (**INV-TEXT-001**); **INV-COUNT-002**: 0+0+1 = 1 |

### 2.3 후속 Journey (동일 플랜 내 확장)

```http
POST /filter
sentiment=부정&keyword=배송
```

→ 필터 목록 1건, 부분집계 일치; `GET /download` → BOM + `text` 헤더 + 원문 1행 (**INV-CSV-OUT-003**).

```http
POST /filter
sentiment=전체&keyword=전체
```

→ Analyze 직후 전체 감정·카테고리 집계와 동일 (**INV-SENT-002**).

---

## 3. pytest 범위·우선순위 (Dual-Track)

### 3.1 디렉터리·책임

| 우선순위 | 경로 | 대상 | 비중·역할 |
|:--------:|------|------|-----------|
| **P0** | `tests/entity/` | `SentimentClassifier`, `CategoryClassifier`(또는 KeywordRule 기반 분류), `Feedback`, `FeedbackFilter`, `_contains_any` | **주력** — 도메인 규칙·INV 직접 검증; AAA; docstring에 `INV-*` |
| **P1** | `tests/control/` | Analyze / Upload / Filter / Download Use Case, Port fake | **주력** — 입출력 ViewModel(`success`/`warning`/`error`), 집계 조립, 0건·공백-only 오케스트레이션 |
| **P2** | `tests/boundary/` | Flask `test_client` | **소수** — HTTP form·multipart·CSV 응답 헤더·HTML에 메시지/집계 존재 여부만 스모크 |
| P3 | `tests/infrastructure/` (선택) | Repository·Store 구현 | Port 계약; M2 이후 확대 |

**금지 (`.cursorrules`):** entity가 Flask import; `fil_data`·`global_sent`·`Session` 클래스 변수에만 의존하는 통합-only; 이중 감정 규칙을 “정상”으로 굳히는 테스트.

### 3.2 TDD·실행 순서

| 단계 | 활동 | 산출 |
|------|------|------|
| RED | 앵커 + 경계·INV 실패 테스트 | `tests/entity/test_sentiment_classifier.py` 등 |
| GREEN | `entity/`·`control/` 최소 구현 | `INV-SENT-002/003`, `INV-COUNT-002` 통과 |
| REFACTOR | BCE 분리·중복 제거 | 회귀 전체 pytest 0 실패 (**RR-5**) |

### 3.3 우선순위 매트릭스 (앵커 연관)

| ID | 테스트 제목(요약) | 레이어 | INV / PRD |
|----|-------------------|--------|-----------|
| TP-01 | 앵커 문장 → 부정·배송·집계 1건 | entity | F-02, F-03, INV-COUNT-002 |
| TP-02 | trim·공백-only 미추가 | entity + control | INV-INPUT-001, F-01 |
| TP-03 | 긍·부 없음 → 중립 | entity | INV-SENT-001 |
| TP-04 | 긍+부 동시 → 긍정 우선 | entity | ST-02, §5.1 순서 |
| TP-05 | Analyze 집계 = Filter(전체,전체) | entity + control | INV-SENT-002, G-2 |
| TP-06 | Filter(중립) → 중립만 | entity + control | INV-SENT-003, G-3 |
| TP-07 | 0건 filter / download warning | control + boundary | INV-EMPTY-001 |
| TP-08 | CSV 업로드 실패 세션 불변 | control | INV-SESSION-001 |
| TP-09 | Filter 후 download 행·순서 | control + boundary | INV-CSV-OUT-003 |
| TP-10 | 앵커 E2E 스모크 | boundary | SCN-A, F-04 |

---

## 4. 경계값 케이스 목록

각 케이스는 **Arrange–Act–Assert**로 작성하며, 테스트 docstring 첫 줄에 `INV-*` 또는 `PRD C-09`를 명시한다.

### 4.1 입력 검증 — `POST /analyze` (F-01)

| Case ID | 입력 | 기대 동작 | INV / 비고 | 레이어 |
|---------|------|-----------|------------|--------|
| B-IN-01 | `text=""` | 피드백 미추가; 건수·원문 목록 불변 | INV-INPUT-001 | entity, control |
| B-IN-02 | `text="   \t\n  "` (trim 후 길이 0) | 동일 | INV-INPUT-001 | entity, control |
| B-IN-03 | 앵커 입력 후 B-IN-02 재호출 | 총 건수 1 유지; 원문 앵커만 | INV-INPUT-001 | control |
| B-IN-04 | **매우 긴 문자열** (권장: 10_000자, prefix `배송` + suffix `화남` 포함) | 1 Feedback append; 원문 바이트·길이 동일; 분류·집계 완료; 응답 시간 단일 요청 &lt; 2s (로컬 기준, 성능은 `@pytest.mark.slow` 분리 가능) | INV-TEXT-001 | entity, control, boundary(1) |
| B-IN-05 | 멀티라인 1건: `text=첫 줄\n둘째 줄` | 1건; 줄바꿈 보존; 집계 1 | INV-TEXT-001 | entity, control |

### 4.2 감정 분류 (F-02, §5.1)

| Case ID | 입력 예시 | 기대 감정 | INV / 규칙 | 레이어 |
|---------|-----------|-----------|------------|--------|
| B-SEN-01 | `오늘은 특별한 일이 없었습니다.` | 중립 | INV-SENT-001 (긍·부 키워드 미매칭) | entity |
| B-SEN-02 | `만족스럽지만 별로예요. 다시는 안 삽니다.` | **긍정** (긍→부→중립 순, 긍정 선매칭) | ST-02, §5.1 | entity |
| B-SEN-03 | 앵커 `배송이 너무 늦어요. 화가 납니다.` | **부정** (`SENTIMENT_KEYWORDS["부정"]` 부분 문자열, 예: `화남` 등 계약에 정의된 키워드 매칭) | 앵커, F-02 | entity |
| B-SEN-04 | `배송이 빨라서 좋아요` | 긍정 | F-02 | entity |
| B-SEN-05 | 동일 세션에 B-SEN-01~04 누적 후 집계 | 긍+중+부 = 총 4 (또는 실제 적재 건수) | INV-COUNT-002 | entity, control |

> **QA 메모:** 계약 문서는 앵커를 **부정**으로 정의한다. RED 단계에서 `constants.SENTIMENT_KEYWORDS`만으로 부정이 나오지 않으면 **키워드·문장 정합** 또는 **단일 Classifier** 구현 갭으로 기록하고, 테스트는 **PRD/README 계약**을 기준으로 유지한다 (레거시 통과를 목표로 하지 않음).

### 4.3 카테고리 분류 (F-03)

| Case ID | 입력 | 기대 | 비고 | 레이어 |
|---------|------|------|------|--------|
| B-CAT-01 | 앵커 문장 | `배송` ≥ 1 (`main` 부분 문자열) | TO-BE: main+sub 정책 | entity |
| B-CAT-02 | 카테고리 키워드 없는 중립 문장 | 전 카테고리 0 또는 미매칭 정책 고정 | PRD §6.4 | entity |
| B-CAT-03 | 복수 main 매칭 문장 (설계 시 1문장 고정) | 카테고리 건수 합 ≤ 피드백 수 | PRD §6.4 | entity |

### 4.4 CSV 업로드 — `POST /upload` (F-02, ST-01)

| Case ID | 입력 | 기대 | INV | 레이어 |
|---------|------|------|-----|--------|
| B-UPL-01 | 정상 UTF-8 BOM, 헤더 `text`, 2데이터 행 | `success`, 2건 적재 | SCN-B | control, boundary |
| B-UPL-02 | **빈 파일** / 헤더만 | `error`; 기존 피드백·건수·원문 **불변** | INV-SESSION-001 | control |
| B-UPL-03 | **깨진 인코딩** (invalid UTF-8) | `error`; 세션 불변 | INV-SESSION-001 | control |
| B-UPL-04 | 앵커 1건 적재 후 B-UPL-02 | 여전히 1건·앵커 원문 | INV-SESSION-001 | control |
| B-UPL-05 | `csv.reader` 파싱 예외 (`csv.Error`) | `error`; 세션 불변 | INV-SESSION-001 | control |

### 4.5 0건·필터·다운로드 (F-06, F-04)

| Case ID | 전제 | When | 기대 | INV | 레이어 |
|---------|------|------|------|-----|--------|
| B-EMP-01 | 피드백 0건 | `POST /filter` (전체/전체) | `warning`: 분석할 피드백 없음; 집계 미표시 | INV-EMPTY-001 | control, boundary |
| B-EMP-02 | B-EMP-01 직후 | `GET /download` | `warning` 또는 본문 없음·스냅샷 없음 (정책 고정) | INV-EMPTY-001 | control, boundary |
| B-EMP-03 | 앵커만 있는 상태에서 `sentiment=긍정` | `warning`: 필터링 결과 없음 | F-06 | control |
| B-EMP-04 | Filter 성공 후 | `GET /download` | BOM + `text` + 스냅샷 순서 | INV-CSV-OUT-001~003 | control, boundary |

### 4.6 미지원 필터 값 (PRD C-09, F-03)

| Case ID | 입력 | 기대 | 레이어 |
|---------|------|------|--------|
| B-FLT-01 | `sentiment=알수없음`, `keyword=전체` | `error` 또는 문서화된 safe fallback + 사용자 메시지 | control, boundary |
| B-FLT-02 | `sentiment=전체`, `keyword=프로모션`(미등록) | 동일 | control |
| B-FLT-03 | 빈 문자열 `sentiment=""` | `전체`와 동등 또는 `error` — **팀이 한 가지로 고정** 후 테스트 잠금 | control |

---

## 5. 예외·특이 케이스 목록 (회귀·레거시)

현재 AS-IS(`src/python/`)에서 문서 계약과 어긋날 수 있는 항목이다. TO-BE GREEN 후 **전부 해소**가 인수 조건이다.

| Case ID | 현상·리스크 | 검증 방법 | INV / G |
|---------|-------------|-----------|---------|
| X-01 | **Analyze ≠ Filter 감정**: `text_analyzer`는 `SENTIMENT_KEYWORDS`, `filters`는 `S_KEYWORDS` | 동일 `Feedback` 리스트에 Analyze 집계 vs `filter_feedbacks`+재집계 비교 | **INV-SENT-002**, G-2, GH Scn6 |
| X-02 | **중립 필터 오분류**: Filter만 `S_KEYWORDS["중립"]` 목록 사용 | 중립-only 문장 + 긍·부 샘플 혼합 후 `Filter(중립,전체)` | **INV-SENT-003**, G-3, GH Scn5 |
| X-03 | **집계 합 불일치**: 부분 필터 재집계·이중 카운트 | 임의 N건 입력 후 `긍정+중립+부정 == len(feedbacks)` | **INV-COUNT-002**, G-4, GH Scn7 |
| X-04 | **CSV 스냅샷**: `fil_data` 전역, filter 없이 download | Filter → Download 행 수·순서 = 필터 결과 | **INV-CSV-OUT-003**, GH Scn3,8 |
| X-05 | **카테고리 필터**: legacy `filters`가 `main` 스킵·sub만 순회 | `keyword=배송` + 앵커 문장(main만 매칭) | F-03, PRD §5.1 |
| X-06 | **세션 격리**: `Session.current_feedbacks` 클래스 변수 | 테스트 A/B 순서 바꿔도 목록 오염 없음 (Repository fake) | RR-4 |
| X-07 | **Upload 후 미분석**: upload 라우트가 집계 없이 success만 반환 | 업로드 직후 Analyze/Filter 일관 정책 정의·테스트 | ST-01 |
| X-08 | **Download 0건**: 빈 `fil_data`여도 CSV 헤더만 반환 가능 | B-EMP-02와 연계 | INV-EMPTY-001 |

### 5.1 앵커 특이 분석 (X-09)

| 항목 | 내용 |
|------|------|
| 문장 | `배송이 너무 늦어요. 화가 납니다.` |
| 계약 | 부정 1, 배송 1 |
| 리스크 | `화가` ≠ `화남` 부분 문자열 — RED 시 실패 가능 |
| 조치 | (1) 계약 문장을 키워드와 정합되게 조정 **또는** (2) 키워드 목록에 문서 예시와 일치하는 표현 추가 — **PRD → Gherkin → README 순**(RR-1) |

---

## 6. 테스트 설계 상세 (레이어별)

### 6.1 `tests/entity/` (P0)

| 모듈(목표) | 테스트 클래스·함수 | 앵커·경계 연결 |
|------------|-------------------|----------------|
| `test_sentiment_classifier.py` | `test_anchor_negative_delivery_anger` | B-SEN-03, TP-01 |
| | `test_neutral_when_no_positive_negative_keywords` | B-SEN-01, INV-SENT-001 |
| | `test_positive_wins_when_both_polarity_keywords` | B-SEN-02 |
| | `test_partial_substring_match_from_constants` | §5.1 |
| `test_category_classifier.py` | `test_anchor_matches_delivery_main` | B-CAT-01 |
| `test_feedback_input_policy.py` | `test_strip_rejects_whitespace_only` | B-IN-01~03 |
| | `test_multiline_preserved_as_single_feedback` | B-IN-05 |
| | `test_long_text_roundtrip` | B-IN-04 |
| `test_aggregation_invariant.py` | `test_sentiment_counts_sum_equals_feedback_count` | B-SEN-05, INV-COUNT-002 |

**Fake:** `Feedback(text=...)` 도메인 객체만 사용; Flask·Session 미사용.

### 6.2 `tests/control/` (P1)

| Use Case | 핵심 Assert |
|----------|-------------|
| `AnalyzeFeedbackUseCase` | 공백-only → append 없음; 성공 시 ViewModel `sentiment_results`/`keyword_results` |
| `FilterFeedbacksUseCase` | 0건 warning; 전체/전체 재집계 = Analyze; 중립 필터 |
| `UploadCsvUseCase` | B-UPL-01~05, INV-SESSION-001 |
| `DownloadFilteredUseCase` | 스냅샷 없음 → warning; 있음 → BOM·헤더·행 |

**Port:** `FeedbackRepository`, `FilteredResultStore` in-memory fake.

#### 6.2.1 G-1 커버리지 보강 (`tests/control/test_coverage_g1.py`)

| pytest 함수 | Case ID | Assert 요약 |
|-------------|---------|-------------|
| `test_upload_csv_use_case_valid_utf8_csv_appends_rows` | B-UPL-01 | 정상 CSV 2건 적재, `success` |
| `test_upload_csv_use_case_utf16_bom_rejected` | B-UPL-02 | UTF-16 BOM → `error`, repo 불변 |
| `test_upload_csv_use_case_invalid_utf8_decode_error` | B-UPL-03 | invalid UTF-8 → `error`, repo 불변 |
| `test_upload_csv_use_case_csv_reader_error` | B-UPL-05 | `csv.Error` mock → `error`, repo 불변 |
| `test_filter_use_case_empty_repository_warning` | B-EMP-01 | 0건 → `warning` |
| `test_filter_use_case_no_matching_results_warning` | B-EMP-03 | 무결과 → `warning` |
| `test_download_use_case_no_snapshot_warning` | B-EMP-02 | 스냅샷 없음 → `warning` |

### 6.3 `tests/boundary/` (P2, 소수)

| 테스트 | Assert 수준 |
|--------|-------------|
| `test_post_analyze_anchor_returns_200_and_success_banner` | status 200, `success`/`alert-success`, 앵커 원문 escape 포함 |
| `test_post_filter_empty_session_warning` | `warning`, `분석할 피드백` |
| `test_get_download_after_filter_has_bom_and_header` | `Content-Disposition`, body starts with BOM, line2 `text` |
| `test_post_upload_broken_csv_error` | `error`, 세션 불변(사전 analyze 후 건수) |

#### 6.3.2 Golden Master / Approval (`tests/golden/`, `test_golden_master.py`)

| 자산 | 시나리오 | 비고 |
|------|----------|------|
| `feedback_golden_master.txt` | S1~S4 | `[S1: …]` 섹션, `load_section` / `assert_golden_text` |
| `download_filtered_anchor.csv` | S5 | `load_csv_golden` / `assert_golden_csv` (**INV-CSV-OUT-003**) |
| `helpers.py` | — | `APPROVE_GOLDEN=1` 승인·`difflib.unified_diff` FAIL |
| `normalize.py` | — | HTTP HTML 정규화 (stdout 금지) |
| `regenerate.py` | — | GREEN baseline 재생성 |

```bash
pytest -v tests/boundary/test_golden_master.py
# 1회 기준 승인: APPROVE_GOLDEN=1 pytest tests/boundary/test_golden_master.py -v
```

#### 6.3.1 Boundary 커버리지 보강 (`tests/boundary/test_coverage_boundary.py`)

| pytest 함수 | Case ID / INV | Assert 요약 |
|-------------|---------------|-------------|
| `test_get_index_renders_start_message` | SCN-A | `GET /`, 시작 메시지 |
| `test_post_upload_valid_csv_success` | B-UPL-01, SCN-B | multipart CSV 2건 `success` |
| `test_post_filter_no_matching_results_warning` | B-EMP-03 | `필터링 결과가 없습니다` |
| `test_get_download_without_filter_returns_csv_header_only` | B-EMP-02, INV-EMPTY-001 | BOM + `text` 헤더만 |
| `test_post_analyze_exception_returns_error_page` | — | analyze 예외 → `error` |
| `test_post_filter_exception_returns_error_page` | — | filter 예외 → `error` |

**격리:** 각 테스트 전 `Session`/Store reset fixture (TO-BE: Repository clear).

---

## 7. 커버리지 목표 (G-1)

| 메트릭 | 목표 | 비고 |
|--------|------|------|
| `entity` + `control` 라인 커버리지 | **≥ 90%** | PRD G-1, README ST-08 |
| `app.py` (boundary 스모크) | **≥ 85%** 권장 | `tests/boundary/` + `test_coverage_boundary.py` |
| `boundary` | HTTP·HTML 스모크 | TC-A + §6.3.1 |

**미커버 허용(예외 기록):** `if __name__ == "__main__"` (`# pragma: no cover`), mission7, 순수 Presenter HTML 템플릿 일부.

**측정 스냅샷 (GREEN+커버리지 보강 후):**

```bash
cd src/python
pytest --cov=entity --cov=control --cov-report=term-missing tests/
pytest --cov=app --cov-report=term-missing tests/boundary/
```

| 메트릭 | 목표 | 달성(참고) |
|--------|------|------------|
| entity+control | ≥ 90% | **100%** (upload_csv 포함) |
| app (boundary only) | ≥ 85% | **100%** |
| 전체 pytest | 0 failed | **52 passed** (boundary·entity·control·tobe·golden) |

---

## 8. pytest-cov 측정 전략

### 8.1 환경

```bash
cd src/python
python -m venv .venv
# Windows
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install pytest pytest-cov
```

### 8.2 일상 실행

```bash
cd src/python
pytest -v tests/
```

| 범위 | 명령 |
|------|------|
| Entity+Control 커버리지 | `pytest --cov=entity --cov=control --cov-report=term-missing tests/` |
| Boundary (`app.py`) | `pytest --cov=app --cov-report=term-missing tests/boundary/` |
| HTML 리포트 | `pytest --cov=entity --cov=control --cov-report=html tests/entity tests/control` → `htmlcov/index.html` |
| Boundary만 | `pytest -v tests/boundary` (cov 선택) |
| mission7 제외 | `pytest -v -m "not mission7" tests/` |

### 8.3 CI·회귀 게이트 (RR-5)

| 게이트 | 조건 |
|--------|------|
| G-0 | `pytest` 전체 0 failed |
| G-1 | `--cov=entity --cov=control` 합산 **≥ 90%** |
| G-2~G-4 | §5 INV-SENT-002/003, INV-COUNT-002 전용 테스트 green |
| G-5 | §4 경계 케이스 B-IN~B-FLT 필수 세트 green |

### 8.4 커버리지 상승 우선순위

1. `SentimentClassifier` 분기(긍/부/중립) — entity  
2. Analyze / Filter / Upload use case — control  
3. 0건·공백-only·CSV 오류 분기 — control  
4. boundary는 **앵커 1 + 0건 warning 1 + download 1** 로 최소 유지  

---

## 9. 추적성 매트릭스 (요약)

| README TO-DO 🔴 | 테스트 Case ID | INV |
|-----------------|----------------|-----|
| 피드백 입력 검증 | B-IN-01~05 | INV-INPUT-001, INV-TEXT-001 |
| SentimentClassifier 단일 허브 | TP-01, B-SEN-01~05, X-01 | INV-SENT-002, INV-SENT-001 |
| 중립 필터 | B-SEN-01 + Filter 중립, X-02 | INV-SENT-003 |
| CSV 수집 | B-UPL-01~04 | INV-SESSION-001 |
| 집계 | B-SEN-05, X-03 | INV-COUNT-002 |
| 필터·다운로드 | B-EMP-03~04, X-04 | INV-CSV-OUT-003 |
| 원문 보존 | B-IN-04~05, 앵커 | INV-TEXT-001 |

| PRD F-ID | Case ID |
|----------|---------|
| F-01 | B-IN-* |
| F-02 | B-SEN-*, TP-05, X-01 |
| F-03 | B-CAT-*, B-FLT-*, X-05 |
| F-04 | B-EMP-*, TP-10 |
| F-05 | B-SEN-05, INV-COUNT-002 |
| F-06 | B-EMP-*, B-FLT-* |

---

## 10. 일정·역할 (권장)

| 단계 | 산출 | 담당 |
|------|------|------|
| Week 1 RED | `tests/entity` 앵커+§4 경계 전부 | Dev + QA 리뷰 INV 태그 |
| Week 2 RED→GREEN | `tests/control` + X-01~05 해소 | Dev — **완료** (2026-05-22, 52 passed) |
| Week 3 | boundary 3~5건, cov ≥ 90% | Dev, QA 인수 §7.1 체크 |

---

## 11. 부록

### 11.1 명명 규칙

- 파일: `test_<domain>_<behavior>.py`
- 함수: `test_<조건>_<기대결과>`
- docstring 1행: `INV-SENT-002: Analyze and Filter share sentiment counts.`

### 11.2 장기 문자열 권장값 (B-IN-04)

```text
"배송" + ("x" * 9990) + "화남"
```

→ 길이 10_000 내외, 배송·부정 키워드 포함, 원문 equality assert.

### 11.3 mission7 (참고만)

Trend CSV, KeywordRule File DB — `@pytest.mark.mission7`, 본 계획서 §1.3 Out-of-Scope.

---

## 12. 문서 이력

| 버전 | 일자 | 변경 |
|------|------|------|
| 1.0 | 2026-05-22 | 앵커 `POST /analyze` 기준 초안 작성 |
