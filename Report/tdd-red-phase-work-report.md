# Feedback Analyzer — TDD RED 단계 작업 보고서

| 항목 | 내용 |
|------|------|
| 프로젝트 | `c:\DEV_BR\FeedbackAnalyzer_06` |
| 작성일 | 2026-05-22 |
| 단계 | **TDD RED** (GREEN·REFACTOR 미착수) |
| 엔트리포인트 | `src/python/app.py` (Flask, 포트 8080) |
| 참조 문서 | [`doc/PRD.md`](../doc/PRD.md), [`doc/test_plan.md`](../doc/test_plan.md), [`doc/defect_list.md`](../doc/defect_list.md), [`README.md`](../README.md) |

---

## 1. 작업 목적

Feedback Analyzer 레거시 코드를 **계약(Invariant)·pytest·Dual-Track(Boundary / Control / Entity)** 기준으로 개선하기 위한 학습 프로젝트이다. 본 보고서는 **RED 단계**에서 수행한 문서화·테스트 설계·pytest 추가·결함 분석·TO-BE 스켈레톤 정의까지의 산출물을 정리한다.

**비목표:** GREEN 구현, REFACTOR, 프로덕션 비즈니스 로직 수정, git 커밋.

---

## 2. 작업 일람 (시간순)

| 순서 | 작업 | 산출물 |
|------|------|--------|
| 1 | 테스트 플랜 샘플 예제 선정 | 앵커: `POST /analyze`, `text=배송이 너무 늦어요. 화가 납니다.` |
| 2 | 테스트 계획서 작성 | [`doc/test_plan.md`](../doc/test_plan.md) v1.0 |
| 3 | README RED To-Do 리스트 섹션 추가 | [`README.md`](../README.md) §「RED 단계 To-Do 리스트」 |
| 4 | 1차 RED pytest (TC-B-01, 04, 05) | `tests/entity/`, `tests/control/`, `tests/support/` |
| 5 | pytest 실행·결함 분석 | [`doc/defect_list.md`](../doc/defect_list.md) v1.0 |
| 6 | README 결함 목록 연결 체크박스 갱신 | `defect_list.md` 생성 [x], X-09 합의 [ ] 유지 |
| 7 | 전체 TC-A/B RED pytest 확장 | `tests/boundary/`, 레거시 entity/control 테스트 추가 |
| 8 | TO-BE 스켈레톤 + `tests/tobe/` RED | `src/python/entity/`, `src/python/control/` |
| 9 | pytest 패키지 충돌 해소 | `tests/conftest.py`, `tests/entity|control/__init__.py` 제거 |

---

## 3. 앵커 시나리오 (기준 예제)

| 항목 | 내용 |
|------|------|
| 입력 | `POST /analyze`, `Content-Type: application/x-www-form-urlencoded`, `text=배송이 너무 늦어요. 화가 납니다.` |
| TO-BE 기대 | `success`; `sentiment_results` 긍0·중0·**부1**; `keyword_results` **배송** ≥ 1; **INV-COUNT-002** (합=1) |
| Journey | SCN-A → (확장) SCN-C Filter·Download |
| 관련 INV | INV-SENT-001~003, INV-COUNT-002, INV-TEXT-001, INV-INPUT-001 |

---

## 4. 문서 산출물

### 4.1 [`doc/test_plan.md`](../doc/test_plan.md)

- pytest 범위·우선순위: **P0** `tests/entity/`, **P1** `tests/control/`, **P2** `tests/boundary/`
- 경계값 B-IN ~ B-FLT, 회귀 X-01 ~ X-09
- 커버리지 목표: entity+control **≥ 90%** (G-1)
- pytest-cov 측정 전략

### 4.2 [`doc/defect_list.md`](../doc/defect_list.md)

- 1차 RED 실행(4 tests): **failed 3 / passed 1**
- 재현 결함: **X-01**, **X-02**, **X-09** (Critical)
- RR-1 합의 대기: 앵커 `화가` vs 키워드 `화남`

### 4.3 [`README.md`](../README.md) 갱신

- 「RED 단계 To-Do 리스트」: Track A (TC-A-01~07), Track B (TC-B-01~12)
- 「결함 목록 연결」: `defect_list.md` 기록 [x], GREEN 회귀 [ ] 유지

---

## 5. 테스트 산출물 구조

### 5.1 레거시 기반 RED (`tests/` — AS-IS 대상)

| 경로 | 역할 | 대표 TC |
|------|------|---------|
| `tests/entity/` | `TextAnalyzer`, `filter_feedbacks` 직접 검증 | TC-B-01, 02, 03, 05, 10, 12 |
| `tests/control/` | Use Case 미러·Port fake·집계 | TC-B-04, 06, 07, 08, 09, 11 |
| `tests/boundary/` | Flask `test_client` 스모크 | TC-A-01 ~ 07 |
| `tests/support/` | `contract.py`, `legacy_labels.py`, `fakes.py`, `legacy_session.py` | TO-BE assert 허브 |

**규칙:** assert = PRD/README TO-BE; `skip`/`xfail`/assert 완화 없음; `filters.S_KEYWORDS` 불일치를 정답으로 고정하지 않음.

### 5.2 TO-BE 스켈레톤 RED (`tests/tobe/` — 미구현 계층)

| 경로 | 역할 |
|------|------|
| `tests/tobe/test_entity_red.py` | `entity.SentimentClassifier`, `FeedbackFilter`, `CategoryClassifier` |
| `tests/tobe/test_control_red.py` | `control.*UseCase` + `port_fakes` |

**의도:** import Error 방지용 STUB 반환 → `pytest.fail("RED: …")` 또는 assert Failure.

### 5.3 TO-BE 스켈레톤 프로덕션 패키지 (STUB only)

```
src/python/
  entity/
    sentiment_classifier.py   # classify → "중립", aggregate → 0
    category_classifier.py    # aggregate 전부 0
    feedback_filter.py        # filter_neutral → 전체 반환, filter_category → []
    ports.py
  control/
    analyze_feedback.py
    filter_feedbacks.py
    upload_csv.py
    download_filtered.py
    dto.py
```

> **주의:** 레거시 `text_analyzer.py`, `filters.py`, `app.py`는 RED 규칙상 **수정하지 않음**.

---

## 6. pytest 실행 결과 (최종 스냅샷)

**명령**

```bash
cd src/python
.venv\Scripts\python.exe -m pytest tests/ --tb=no -q
```

**결과 (2026-05-22 기준)**

| 구분 | 건수 |
|------|------|
| **총 테스트** | 34 |
| **passed (GREEN)** | 12 |
| **failed (RED)** | 22 |
| **ERROR (수집 실패)** | 0 |

### 6.1 passed — 조기 GREEN (레거시·정책 일치)

| TC | 함수 | 비고 |
|----|------|------|
| TC-A-02 | `test_tc_a_02_post_analyze_whitespace_only_unchanged_count` | INV-INPUT-001 |
| TC-A-03 | `test_tc_a_03_post_filter_empty_session_warning` | INV-EMPTY-001 |
| TC-A-05 | `test_tc_a_05_post_upload_broken_csv_error_session_unchanged` | INV-SESSION-001 (Session 검증) |
| TC-B-02 | `test_tc_b_02_neutral_only_sentence_classified_as_neutral` | INV-SENT-001 |
| TC-B-03 | `test_tc_b_03_positive_wins_when_positive_and_negative_keywords_present` | 긍→부 우선 |
| TC-B-04a | `test_tc_b_04_analyze_aggregate_equals_filter_whole_recount` | 집계만 동일·이중 규칙 미노출 |
| TC-B-07 | `test_tc_b_07_empty_and_whitespace_only_do_not_append_to_repository` | |
| TC-B-08 | `test_tc_b_08_*` (2건) | mirror upload |
| TC-B-09 | `test_tc_b_09_filter_snapshot_row_order_matches_download_body` | BOM 파싱 |
| TC-B-10 | `test_tc_b_10_long_text_original_equality_and_classification_complete` | `화남` suffix |
| TC-B-12 | `test_tc_b_12_sentiment_keyword_partial_substring_match` | |

### 6.2 failed — RED 확정 (요약)

| 영역 | 대표 실패 원인 | 결함 ID |
|------|----------------|---------|
| Entity 레거시 | 앵커 부정 기대 → 실제 중립 | X-09 |
| Control 레거시 | Analyze≠Filter 라벨 (`빠르` 키워드) | X-01 |
| Entity 레거시 | 중립 필터에 앵커 포함 | X-02 |
| Boundary | 부정 stat=1·원문 HTML 미표시·filter+download 0건 | X-05, X-09, UI |
| TO-BE entity/control | STUB 미구현 | GREEN 대상 |

전체 failed 목록은 pytest `-v` 로 확인.

---

## 7. 주요 결함 요약

| ID | Severity | 요약 | GREEN 방향 |
|----|----------|------|------------|
| **X-09** | Critical | `화가` ≠ `화남` — README 부정 vs 키워드·분류 중립 | RR-1 합의 후 단일 Classifier |
| **X-01** | Critical | `SENTIMENT_KEYWORDS` vs `S_KEYWORDS` 이중 규칙 | `SentimentClassifier` 단일 허브 (**INV-SENT-002**) |
| **X-02** | Critical | 중립 필터가 `S_KEYWORDS["중립"]`+else 사용 | 긍·부 미매칭만 (**INV-SENT-003**) |
| **X-05** | Major | `filters.py` 카테고리 필터 `main` 스킵 | main+sub 정책 (**TC-B-11**) |
| X-03~X-08 | open | CSV·Session·Upload 등 — 추가 TC로 추적 | test_plan §3.1 |

상세: [`doc/defect_list.md`](../doc/defect_list.md)

---

## 8. 인프라·기술 이슈 및 조치

### 8.1 pytest 패키지 이름 충돌

**현상:** `tests/entity/` 가 pytest import 시 최상위 패키지 `entity`로 로드되어, 도메인 `src/python/entity/` 와 충돌 → `ModuleNotFoundError: entity.category_classifier`.

**조치**

- `tests/entity/__init__.py`, `tests/control/__init__.py` **삭제**
- `tests/conftest.py`에 `pytest_configure`에서 도메인 `entity`·`control` 선로드
- TO-BE RED는 **`tests/tobe/`** 에만 배치 (레거시 테스트 파일 본문은 미수정)

### 8.2 TO-BE vs 레거시 이중 트랙

| 트랙 | 테스트 위치 | 대상 코드 |
|------|-------------|-----------|
| 레거시 RED | `tests/entity|control|boundary/` | `text_analyzer`, `filters`, `app` |
| TO-BE RED | `tests/tobe/` | `entity/`, `control/` STUB |

GREEN 단계에서 레거시 로직을 **Entity·Control로 이전** 후 TO-BE 테스트를 통과시키는 순서를 권장한다.

---

## 9. AS-IS 코드 상태 (변경 없음)

| 파일 | 문제 (PRD/README) |
|------|-------------------|
| `app.py` | God Function, `render_page`에 원문 목록 미렌더 |
| `text_analyzer.py` | `SENTIMENT_KEYWORDS`, 전역 `global_sent` |
| `filters.py` | `S_KEYWORDS` 이중 규칙, `main` 스킵 |
| `session.py` | `Session.current_feedbacks` 클래스 변수 |
| 전역 | `fil_data` |

---

## 10. 다음 단계 (GREEN 권장 순서)

1. **RR-1:** 앵커 문장·키워드 정합 (X-09) — PRD → Gherkin → README
2. **GREEN-1:** `entity.SentimentClassifier` 실구현 + `filters` 감정 로직 제거 (X-01, X-02)
3. **GREEN-2:** `FeedbackFilter` main+sub (X-05), `FilteredResultStore` Port (X-04)
4. **GREEN-3:** Control Use Case 연결, `app.py` thin boundary
5. **회귀:** 전체 pytest 0 failed, entity+control cov ≥ 90%

---

## 11. 관련 파일 인덱스

### 문서

- [`doc/test_plan.md`](../doc/test_plan.md)
- [`doc/defect_list.md`](../doc/defect_list.md)
- [`doc/PRD.md`](../doc/PRD.md)
- [`README.md`](../README.md)
- [`Report/spec-documentation-work-report.md`](../Report/spec-documentation-work-report.md) (이전 스펙 문서 작업)

### 테스트 (신규·주요)

- `src/python/tests/boundary/test_tc_a_boundary_red.py`
- `src/python/tests/entity/test_anchor_tc_b_01.py` 외
- `src/python/tests/control/test_inv_sent_002_tc_b_04.py` 외
- `src/python/tests/tobe/test_entity_red.py`
- `src/python/tests/tobe/test_control_red.py`
- `src/python/tests/support/contract.py`

### TO-BE 스켈레톤

- `src/python/entity/*.py`
- `src/python/control/*.py`

---

## 12. 문서 이력

| 버전 | 일자 | 변경 |
|------|------|------|
| 1.0 | 2026-05-22 | RED 단계 작업 통합 보고서 초안 |
