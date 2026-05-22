# 신규 기능 확장 — 가중치 감성 · FileHandler · 명명 규칙 (M4)

| 항목 | 값 |
|------|-----|
| 문서 버전 | 1.0 |
| 반영일 | 2026-05-22 |
| 코드 기준 | `refactoring` 브랜치 · `SentimentClassifier` 가중치 · `FileHandler` · `FeedbackAnalyzer` |
| 테스트 | **62 passed** (M3 Extension + M4 `TEST_F` 포함) |
| 참조 | [`PRD.md`](PRD.md), [`test_plan.md`](test_plan.md), [`README.md`](../README.md) |

---

## 1. 개요

| 기능 ID | 이름 | 요약 |
|---------|------|------|
| **F-15** | 가중치 감성 분석 | 키워드 **가중 합** 비교; 혼합 텍스트 정확도 개선 |
| **F-16** | FileHandler CSV 저장 | 세션 피드백·분석 결과를 UTF-8 BOM CSV로 영속화 |
| **M4-N** | C++ 스타일 명명 | `analyzeSentiment`, `analyzeKeywords`, `filter`→`FilterResult`, `getCurrentFeedbacks` |

---

## 2. F-15 — 가중치 감성 분석

### 2.1 레거시(개선 전) 문제

| 문제 | 설명 |
|------|------|
| 첫 매칭 우선 | `긍정` 키워드가 먼저 매칭되면 `부정` 키워드를 검사하지 않음 |
| 혼합 오분류 | 긍·부가 공존하는 문장에서 순서에 따라 라벨이 왜곡됨 |
| 중립 fallback | 긍·부 미매칭이 아닌 경우에도 `else`로 중립 처리되는 경로 존재 |

### 2.2 TO-BE 알고리즘

구현: [`src/python/entity/sentiment_classifier.py`](../src/python/entity/sentiment_classifier.py)

1. 텍스트에서 `SENTIMENT_KEYWORDS["긍정"]`·`["부정"]` 각 키워드 **부분 문자열 매칭** 목록 수집
2. `SENTIMENT_KEYWORD_WEIGHTS` 로 키워드별 가중치 합산 (`constants.py`, 미지정 시 **1.0**)
3. `scoreSentiment(text)` → `{"긍정": float, "부정": float}`
4. `analyzeSentiment(text)` / `classify(text)`:
   - `긍정 점수 > 부정 점수` → **긍정**
   - `부정 점수 > 긍정 점수` → **부정**
   - **양쪽 0** → **중립** (**INV-SENT-001**: 긍·부 미매칭)
   - **동점·양수** → `MIXED_SENTIMENT_TIE_BREAKER` (기본 **부정**)

### 2.3 계약·INV 정합

| INV | 가중치 적용 후 |
|-----|----------------|
| **INV-SENT-001** | 키워드 미매칭 시에만 중립 |
| **INV-SENT-002** | Analyze·Filter 동일 `SentimentClassifier` |
| **INV-SENT-003** | 중립 필터 = 계약상 중립 라벨만 |
| **INV-COUNT-002** | `aggregate()` 합 = 피드백 수 |

**회귀:** 앵커 `화가` → **부정** 유지 (Golden S1·TC-B-01).  
**혼합 예:** `만족스럽지만 별로예요…` → 긍정 가중 합 > 부정 → **긍정** (TC-B-03).

### 2.4 설정

```python
# constants.py
SENTIMENT_KEYWORD_WEIGHTS = {
    "긍정": {"만족": 1.0, "만족스럽": 1.2, ...},
    "부정": {"별로": 1.2, "화가": 1.5, ...},
}
MIXED_SENTIMENT_TIE_BREAKER = "부정"
```

---

## 3. F-16 — FileHandler CSV 저장

### 3.1 구현

| 파일 | API |
|------|-----|
| [`infrastructure/file_handler.py`](../src/python/infrastructure/file_handler.py) | `saveFeedbacksCsv(path, feedbacks)` |
| 동일 | `saveAnalysisCsv(path, feedbacks, sentiment_results, keyword_results)` |

### 3.2 런타임 연동

| 시점 | 동작 |
|------|------|
| `POST /analyze` 성공·피드백 1건 이상 | `data/exports/session_feedbacks.csv` 저장 |
| wiring | `wiring.file_handler`, `wiring.export_dir` |

**형식:** UTF-8 BOM, 헤더 `text`, 데이터 행 = 피드백 원문 (**INV-TEXT-001**).

**분석 CSV:** `text,sentiment_label` 행 + `# sentiment_aggregate` / `# keyword_aggregate` 섹션.

> **주의:** HTTP `GET /download` 계약(**INV-CSV-OUT-003**)은 기존 Filter 스냅샷용이며, FileHandler export와 별도이다.

---

## 4. M4 — C++ 스타일 명명

파사드: [`entity/feedback_analyzer.py`](../src/python/entity/feedback_analyzer.py)

| 레거시 (학습용 AS-IS) | 신규 API | 반환/비고 |
|----------------------|----------|-----------|
| `sent()` | `analyzeSentiment(text)` | `str` — 긍정/부정/중립 |
| `kw()` | `analyzeKeywords(feedbacks)` | `Dict[str, int]` |
| `fil()` | `filter(sentiment, keyword)` | **`FilterResult`** |
| `fil_data` (전역) | `FilterResult.feedbacks` + `FilteredResultStore` | 전역 mutable 금지 (**RR-4**) |
| `getOldDataFromSession()` | `getCurrentFeedbacks()` | `List[Feedback]` |

### 4.1 FilterResult

[`entity/filter_result.py`](../src/python/entity/filter_result.py)

```python
@dataclass
class FilterResult:
    feedbacks: List[Feedback]
    sentiment_results: Dict[str, int]
    keyword_results: Dict[str, int]
```

`CategoryClassifier.analyzeKeywords()` — `aggregate()` 별칭.

---

## 5. TEST_F — 독립 검증

마커: `pytest.mark.TEST_F` ([`tests/conftest.py`](../src/python/tests/conftest.py))

| 파일 | ID | 검증 |
|------|-----|------|
| `tests/entity/test_f_weighted_sentiment.py` | F-01~06 | 순수 긍/부, tie-breaker, 가중 혼합, 중립, 집계 |
| `tests/infrastructure/test_f_file_handler.py` | F-07~08 | CSV·분석 CSV |
| `tests/entity/test_f_feedback_analyzer_naming.py` | F-09~12 | 명명·FilterResult·persist |

```bash
cd src/python
pytest -v -m TEST_F tests/
pytest -v tests/    # 전체 62건 + Golden
```

---

## 6. 품질 지표 (2026-05-22)

| 항목 | 결과 |
|------|------|
| `pytest tests/` | **62 passed** |
| Golden GM-TC-01~05 | **5/5 PASS** |
| entity+control cov | **≥ 99%** |
| 전 레이어 cov | **94%** (653 stmts, M3·M4) |
| `file_handler.py` | **100%** |

---

## 8. M3 Extension (README TO-DO 완료)

| 기능 | 구현 | 테스트 |
|------|------|--------|
| F-08 KeywordRuleRepository | `FileKeywordRuleRepository`, `data/feedback_rules.json` | `test_keyword_rule_repository.py` |
| ST-06 동적 키워드 | `POST /keywords/register` | `test_register_keyword.py` |
| F-14 PageLogSink | `PageLogSink`, `POST /settings/log-levels` | `test_page_log_sink.py` |
| F-11 Trend | `test_feedback_trend.csv`, index 테이블 | `test_trend_mission7.py` |
| F-13 JSON API | `/api/session`, `/api/analyze`, `/api/filter` | `test_json_api.py` |
| 멀티라인 UI | `textarea rows="6"` | `test_multiline_ui.py` |
| tests/tobe 통합 | `tests/integration/test_tobe_parity.py` | 3건 parity |

**회귀:** 62 passed · Golden 5/5 PASS

---

## 9. 문서 이력

| 버전 | 일자 | 변경 |
|------|------|------|
| 1.0 | 2026-05-22 | F-15·F-16·M4 명명·TEST_F 초안 |
| 1.1 | 2026-05-22 | M3 F-08~F-14·ST-06~10·tobe 통합 |
