# GH-01 — Phase 4 Gherkin (8 Scenarios)

| 항목 | 값 |
|------|-----|
| 문서 | GH-01 추적본 (저장소 내 선행 갱신) |
| 기준일 | 2026-05-22 |
| RR-1 | 앵커 `배송이 너무 늦어요. 화가 납니다.` · `SENTIMENT_KEYWORDS["부정"]`에 **`화가`** 포함 **(B)** |
| 아키텍처 | M2 — `boundary` → `control` → `entity` ← `infrastructure` |
| pytest 대응 | [`doc/test_plan.md`](test_plan.md) TC-A/B · Golden GM-TC-01~05 |

> 외부 Phase 4 원본과 문구가 다를 수 있으나, **INV·행위·앵커**는 본 문서·PRD·README와 동일합니다.

---

## Background

```gherkin
Given the Feedback Analyzer app is running with M2 architecture
And sentiment classification uses a single SentimentClassifier (INV-SENT-002)
And neutral filter means no positive/negative keyword match (INV-SENT-003)
And the demo anchor text is "배송이 너무 늦어요. 화가 납니다." with negative sentiment (RR-1 B: keyword "화가")
```

---

## Scenarios

### Scn1 — CSV upload (ST-01, ST-05)

```gherkin
Scenario: Upload valid UTF-8 CSV with text column
  Given the feedback repository is empty
  When I POST /upload with a valid CSV (BOM, header "text", one data row)
  Then the response shows success
  And the repository contains the uploaded row unchanged (INV-SESSION-001 on failure paths)
```

**pytest:** TC-A-05, TC-B-08

---

### Scn2 — Analyze anchor (ST-02, ST-03)

```gherkin
Scenario: Analyze anchor feedback — negative sentiment and delivery category
  When I POST /analyze with text "배송이 너무 늦어요. 화가 납니다."
  Then sentiment_results show negative count 1 (INV-COUNT-002)
  And keyword_results include delivery category count >= 1
  And the page lists the original text escaped (INV-TEXT-001)
```

**pytest:** TC-A-01, TC-B-01, GM-TC-01

---

### Scn3 — Download after filter (ST-04)

```gherkin
Scenario: Download CSV matches last filter snapshot
  Given anchor feedback was analyzed and stored
  When I POST /filter with sentiment "부정" and keyword "배송"
  And I GET /download
  Then the CSV has UTF-8 BOM, header "text", and one data row equal to the anchor (INV-CSV-OUT-003)
```

**pytest:** TC-A-04, TC-B-09, GM-TC-05

---

### Scn4 — Dynamic keyword rule (ST-06, F-08) — **미착수 (🟢/mission7)**

```gherkin
Scenario: Register category keywords at runtime
  Given KeywordRuleRepository is available
  When I register new keywords for a category
  Then classification uses the updated rules without changing stored feedback text (INV-RULE-002)
```

**상태:** 선택 범위 — 현재 `constants.CATEGORY_KEYWORDS` 고정.

---

### Scn5 — Neutral filter only (ST-02)

```gherkin
Scenario: Filter neutral returns only neutral-labeled items
  Given multiple feedbacks with known sentiment labels under contract rules
  When I POST /filter with sentiment "중립" and keyword "전체"
  Then every returned item is neutral by SentimentClassifier (INV-SENT-003)
  And the anchor negative example is not included when labeled negative
```

**pytest:** TC-B-05

---

### Scn6 — Analyze equals filter recount (ST-02)

```gherkin
Scenario: Analyze aggregate matches filter whole-session recount
  Given a session with mixed feedback texts
  When I analyze all feedbacks
  And I filter with sentiment "전체" and keyword "전체"
  Then per-item sentiment labels from analyze match filter labels (INV-SENT-002)
```

**pytest:** TC-B-04a, TC-B-04b

---

### Scn7 — Sentiment count sum (ST-03)

```gherkin
Scenario: Sentiment counts sum to feedback count
  Given N feedbacks in the repository
  When sentiment is aggregated for all feedbacks
  Then positive + neutral + negative equals N (INV-COUNT-002)
```

**pytest:** TC-B-06

---

### Scn8 — Empty session filter warning (ST-04)

```gherkin
Scenario: Filter with zero feedbacks shows warning
  Given no feedbacks in the repository
  When I POST /filter
  Then the response contains warning for empty analysis (INV-EMPTY-001)
```

**pytest:** TC-A-03, GM-TC-04

---

## 문서 이력

| 일자 | 변경 |
|------|------|
| 2026-05-22 | 초안 — M2·RR-1 (B)·pytest 매핑; Scn4는 🟢 미착수 명시 |
