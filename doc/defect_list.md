# 결함 목록 — Feedback Analyzer

| 항목 | 값 |
|------|-----|
| 문서 버전 | 1.2 (REFACTOR 클로저) |
| RED 기록일 | 2026-05-22 |
| GREEN 확인일 | 2026-05-22 |
| pytest 명령 | `cd src/python` → `.venv\Scripts\python.exe -m pytest -v --tb=short tests/entity/test_anchor_tc_b_01.py tests/control/test_inv_sent_002_tc_b_04.py tests/entity/test_inv_sent_003_tc_b_05.py` |
| assert 기준 | TO-BE — [`doc/PRD.md`](PRD.md), [`README.md`](../README.md), `tests/support/contract.py` |
| 참조 | [`doc/test_plan.md`](test_plan.md) §5, §5.1 · PRD §7.1 |

---

## 1. 요약

| 구분 | 건수 | 비고 |
|------|------|------|
| **RED failed (기록)** | 3 | X-01, X-02, X-09 — TC-B-01, TC-B-04b, TC-B-05 |
| **GREEN closed** | 3 | 2026-05-22 — 전체 `pytest tests/` **52 passed** |
| **REFACTOR closed** | X-06, X-07 | Session → Repository; Upload 정책 문서화 |
| **open (선택)** | X-08 일부 | download 헤더-only — boundary cov로 mitigated |

**M1 GREEN:** TC-A-01~07, TC-B-01~12, `tests/tobe/`, Golden GM-TC-01~05

---

## 2. pytest 실행 로그 요약

| TC | pytest 함수 | 결과 | assert 한 줄 (요약) | INV |
|----|-------------|------|---------------------|-----|
| TC-B-01 | `test_tc_b_01_anchor_negative_sentiment_and_delivery_category` | **FAILED** | `sentiment_results` 부정1 기대 → 실제 중립1 | INV-COUNT-002, (문서) 부정 분류 |
| TC-B-04a | `test_tc_b_04_analyze_aggregate_equals_filter_whole_recount` | **PASSED** (조기 GREEN) | Analyze 집계 == Filter(전체,전체) 재집계 | INV-SENT-002 |
| TC-B-04b | `test_tc_b_04_per_item_sentiment_label_analyze_matches_filter` | **FAILED** | `택배가 빠르게…` analyze=중립 vs filter=긍정 | INV-SENT-002 |
| TC-B-05 | `test_tc_b_05_neutral_filter_returns_only_contract_neutral_items` | **FAILED** | 앵커 문장이 `Filter(중립,전체)` 결과에 포함 | INV-SENT-003 |

### 2.1 진단 스냅샷 (실행일 1회 출력)

**앵커** `배송이 너무 늦어요. 화가 납니다.`

| 경로 | 값 |
|------|-----|
| `classify_sentiment_contract` | `중립` (`화남` 부분매칭 없음) |
| `TextAnalyzer().sent` | `{'긍정': 0, '중립': 1, '부정': 0}` |
| `TextAnalyzer().kw['배송']` | `1` |
| `label_sentiment_analyze_path` | `중립` |
| `label_sentiment_filter_path` | `중립` |

**TC-B-04 혼합 3건** (`ANCHOR`, `택배가 빠르게 왔어요. 친절했습니다.`, `오늘은 특별한 일이 없었습니다.`)

| 항목 | 값 |
|------|-----|
| `analyze_sentiment_counts` | `{'긍정': 0, '중립': 3, '부정': 0}` |
| `filter_all_sentiment_counts` | `{'긍정': 0, '중립': 3, '부정': 0}` (동일 → TC-B-04a PASS) |
| 불일치 문장 | `택배가 빠르게…` — analyze=`중립`, filter=`긍정` (`빠르` ∈ `S_KEYWORDS["긍정"]`) |

**TC-B-05** `Filter(중립, 전체)`

| 항목 | 값 |
|------|-----|
| `filter_feedbacks` 반환 text | `오늘은 특별한 일이 없었습니다.`, `배송이 너무 늦어요. 화가 납니다.` |
| contract 라벨 (3건) | 중립, **긍정**, 중립 |
| README 기대 | 앵커(부정 예시)는 중립 필터 결과에 **미포함** |

---

## 3. 결함 표

> **상태 (v1.1):** **X-01·X-02·X-09** → **closed (GREEN)** — §5 클로저. 아래 표는 RED 재현 시점 스냅샷.

| ID | Severity | 결함 유형 | 재현 절차 | 기대값 | 실제값 | 근본 원인 | 수정 요약 |
|----|----------|-----------|-----------|--------|--------|-----------|-----------|
| **X-09** | Critical | 감정 분류(Analyze)·키워드 정합(앵커) | `pytest tests/entity/test_anchor_tc_b_01.py::test_tc_b_01_anchor_negative_sentiment_and_delivery_category`; `POST /analyze` `text=배송이 너무 늦어요. 화가 납니다.` | PRD/README: `sentiment_results` 긍0/중0/부1; TO-BE 테스트 assert 부정 1건 | `TextAnalyzer.sent`: 긍0/중1/부0; `classify_sentiment_contract`도 `중립` (현 키워드表) | `constants.SENTIMENT_KEYWORDS["부정"]`에 `화남`만 등록; 입력 `화가`는 부분매칭 실패. README 데모는 부정·PRD §6.1 예시와 문장·키워드 불일치 | **RR-1** 합의: (A) 문장을 `화남` 포함으로 정합 **또는** (B) 키워드 확장. 이후 **단일 SentimentClassifier**로 Analyze·Filter 통일 |
| **X-01** | Critical | Analyze≠Filter | `pytest tests/control/test_inv_sent_002_tc_b_04.py::test_tc_b_04_per_item_sentiment_label_analyze_matches_filter`; 3건 혼합 피드백 | 문장별 Analyze 라벨 == Filter 라벨; 동일 규칙이면 집계도 일치 (**INV-SENT-002**) | `택배가 빠르게 왔어요. 친절했습니다.`: analyze=`중립`, filter=`긍정` | `text_analyzer.py` → `SENTIMENT_KEYWORDS`; `filters.py` → `S_KEYWORDS` 이중 표 (**RR-3** 위반) | `SentimentClassifier` 단일 허브; `filter_feedbacks` 감정 판정도 동일 목록·순서(긍→부→중립) 사용 |
| **X-02** | Critical | 중립 필터 | `pytest tests/entity/test_inv_sent_003_tc_b_05.py::test_tc_b_05_neutral_filter_returns_only_contract_neutral_items`; `Filter(중립, 전체)` | README/PRD: 계약 **부정** 앵커는 중립 필터 결과에 없음; contract 중립(긍·부 미매칭)만 | 반환: `오늘은…`, **앵커** 포함; `배송이 빨라서 좋아요`는 제외됨 | `filters.filter_feedbacks`가 `S_KEYWORDS["중립"]` 목록 + `else: 중립` 사용 (**INV-SENT-001** 정의와 다름). 앵커는 filter 경로에서 `else` 중립으로 통과 | 중립 필터 = **긍·부 키워드 미매칭**만 (**INV-SENT-003**); `S_KEYWORDS["중립"]` 제거·SentimentClassifier와 동일 판정 |

### 3.1 미재현·open (이번 RED 범위 외)

| ID | 상태 | 비고 |
|----|------|------|
| X-03 | closed (M1) | TC-B-06 — N건 혼합 **INV-COUNT-002** |
| X-04 | closed (M1) | TC-B-09, TC-A-04, GM-TC-05 — **INV-CSV-OUT-003** |
| X-05 | closed (M1) | TC-B-11 — main+sub 카테고리 필터 |
| X-06 | **closed (REFACTOR)** | `Session` 제거 → `MemoryFeedbackRepository` + `wiring` (C-01, C-13) |
| X-07 | **closed (policy)** | Upload 후 자동 재분석 없음 — ADR-03·`UploadCsvUseCase` append only; TC-B-08·boundary cov |
| X-08 | mitigated | TC-A-03, GM-TC-04 — 0건 filter warning; download 헤더-only는 `test_coverage_boundary` |

### 3.2 조기 GREEN 메모 (결함 아님·테스트 보강)

| 항목 | 설명 |
|------|------|
| TC-B-04a PASS | `Filter(전체,전체)` 후에도 동일 `Feedback` 목록에 `TextAnalyzer.sent`만 재호출 → 집계 일치. **문장별 라벨 불일치(X-01)는 가려짐.** TC-B-04b가 INV-SENT-002의 실질 RED 담당 |

---

## 4. TC ↔ 결함 ↔ INV 매트릭스

| TC | 결과 | 결함 ID | INV |
|----|------|---------|-----|
| TC-B-01 | FAILED | X-09 | INV-COUNT-002 (부정 1건 전제), 문서 부정 분류 |
| TC-B-04a | PASSED (조기 GREEN) | — (X-01 은 TC-B-04b에서 재현) | INV-SENT-002 |
| TC-B-04b | FAILED | X-01 | INV-SENT-002 |
| TC-B-05 | FAILED | X-02, X-09 (앵커 부정 기대 시) | INV-SENT-003, INV-SENT-001 |

---

## 5. GREEN 클로저 (2026-05-22)

| ID | 조치 | 검증 |
|----|------|------|
| **X-09** | **RR-1 (B)** — `constants.SENTIMENT_KEYWORDS["부정"]`에 `화가` 추가; README 앵커 문장 유지 | TC-B-01, TC-A-01, GM-TC-01 |
| **X-01** | `filters._label_sentiment` + `entity/sentiment_classifier.py`; Analyze·Filter 동일 규칙 | TC-B-04b, INV-SENT-002 |
| **X-02** | 중립 필터 = 긍·부 미매칭만; `S_KEYWORDS["중립"]` 목록 경로 제거 | TC-B-05, INV-SENT-003 |

**회귀:** `cd src/python` → `pytest -v tests/` → **52 passed**, 0 failed.

---

## 6. RR-1 결정 기록 (X-09)

| 항목 | 결정 |
|------|------|
| **선택** | **(B)** `화가` 키워드 추가 — 데모 문장 `배송이 너무 늦어요. 화가 납니다.` 유지 |
| **문서** | README RED To-Do·Golden·[`doc/PRD.md`](PRD.md) §7.1 INV `[x]` 반영 |
| **문서** | [`doc/gherkin_gh01.md`](gherkin_gh01.md) — GH-01 추적본 (RR-1·M2) |

---

## 7. 문서 이력

| 버전 | 일자 | 변경 |
|------|------|------|
| 1.0 | 2026-05-22 | RED pytest 4건 실행; X-01, X-02, X-09 재현 기록 |
| 1.1 | 2026-05-22 | GREEN 클로저; RR-1 **(B)**; 52 passed 스냅샷 |
| 1.2 | 2026-05-22 | REFACTOR: X-06·X-07 closed; Gherkin 추적 문서; CategoryClassifier main+sub |
