# Golden Master (Approval Regression)

Feedback Analyzer의 **HTTP 응답·CSV 파일 계약**을 고정하는 회귀 기준입니다.  
`print`/stdout Golden은 사용하지 않습니다 (PRD §6, README 「출력 포맷」).

## 파일

| 파일 | 시나리오 | 내용 |
|------|----------|------|
| `feedback_golden_master.txt` | **S1~S4** | `[S1: …]` 섹션별 정규화 블록 |
| `download_filtered_anchor.csv` | **S5** | `GET /download` CSV 본문 (UTF-8 BOM + `text` + 앵커 행) |
| `normalize.py` | — | HTML → `PageSnapshot`, CSV BOM 정규화 |
| `helpers.py` | — | `load_section`, `load_csv_golden`, `assert_golden_*`, `APPROVE_GOLDEN` |
| `regenerate.py` | — | GREEN baseline 일괄 재생성 |

## 시나리오 매핑

| ID | Journey | 입력 | INV |
|----|---------|------|-----|
| **S1** | SCN-A | `POST /analyze` 앵커 문장 | INV-COUNT-002, INV-TEXT-001 |
| **S2** | SCN-A | `POST /analyze` 긍정·배송 문장 | 집계 다양성 (권장) |
| **S3** | SCN-A | 앵커 적재 후 `text=   ` | **INV-INPUT-001** |
| **S4** | SCN-C | 0건 `POST /filter` | **INV-EMPTY-001** |
| **S5** | SCN-C | S1 → filter(부정,배송) → download | **INV-CSV-OUT-001~003** |

pytest: `tests/boundary/test_golden_master.py`

## Approval API (`helpers.py`)

```python
from tests.golden.helpers import load_section, load_csv_golden, assert_golden_text

expected = load_section("S1")  # 또는 load_section("[S1: SCN-A anchor POST /analyze]")
assert_golden_text(actual_block, "S1", status_code=200)
```

| `APPROVE_GOLDEN=1` | 동작 |
|--------------------|------|
| 기준 섹션/CSV **없음** | 현재 캡처 저장 → **pytest.skip** (1회 승인) |
| 기준 **불일치** | 갱신 저장 → **skip** (재실행 시 enforce) |
| 기준 **일치** | PASS |

불일치 시 `difflib.unified_diff` 형식으로 FAIL:

```text
--- expected (tests/golden/feedback_golden_master.txt [S1: ...])
+++ actual
@@ ...
```

**금지:** `redirect_stdout` / stdout Golden (출력은 HTTP·HTML·CSV).

## 정규화 규칙

| 동적 요소 | 처리 |
|-----------|------|
| `YYYY-MM-DD HH:MM:SS :` | `[TIMESTAMP]` |
| `N개의 피드백이 입력되었습니다` | 시나리오 `expected_count`로 N 고정 |
| HTML | `stat-number`/`stat-label`, `alert-*`, `<li>` 원문만 추출 |
| CSV | BOM 유지, 줄바꿈 `\n`으로 통일 |

## 실행

```bash
cd src/python
.venv\Scripts\Activate.ps1
pytest -v tests/boundary/test_golden_master.py
```

전체 회귀에 포함:

```bash
pytest -v tests/
```

## 기준 파일 재생성 (GREEN baseline · 계약 변경 시만)

1. **RR-1:** `doc/PRD.md` → Gherkin → README (X-09 앵커 부정 반영)  
2. **GREEN** 통과 후:

```bash
cd src/python
python tests/golden/regenerate.py
# 또는 1회 승인:
# set APPROVE_GOLDEN=1  (PowerShell)
pytest tests/boundary/test_golden_master.py -v
```

3. `git diff tests/golden/` 검토 후 커밋  
4. `APPROVE_GOLDEN` 없이 `pytest` → 0 failed enforce

## 버전 관리

- Golden 파일은 **소스와 동일 브랜치**에 커밋 (`.gitignore` 제외)  
- 의도적 출력 변경 = 계약 변경 + Golden diff가 PR 리뷰 증거  
- `htmlcov/`, `.coverage`는 Golden에 포함하지 않음

## 참조

- [`doc/PRD.md`](../../../doc/PRD.md) §6.1~6.3, G-2~G-5  
- [`doc/test_plan.md`](../../../doc/test_plan.md) §6.3  
- README 「예시 입출력」「출력 포맷」
