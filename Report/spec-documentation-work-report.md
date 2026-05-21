# Feedback Analyzer — spec 브랜치 문서화 작업 보고서

| 항목 | 내용 |
|------|------|
| 작성일 | 2026-05-21 |
| 워크스페이스 | `c:\DEV_BR\FeedbackAnalyzer_06` |
| Git 브랜치 | **spec** (기존 브랜치 확인·작업; `origin/spec` 추적) |
| 보고 범위 | Phase 4/5 산출물 정리, PRD·README·TO-DO, 문서 정합, AI 프롬프트 설계 (코드 구현 없음) |

---

## 1. Executive Summary

본 작업은 **UnitConverter_Python** 등 타 프로젝트용 BDD·PRD·README·TO-DO 프롬프트 포맷을 **Feedback Analyzer** 도메인에 맞게 이식하고, 저장소에 **제품 계약(PRD)** 과 **운영·학습 문서(README)** 를 분리·정합한 것이다. **애플리케이션 코드(`src/python`) 비즈니스 로직 변경은 범위 외**이며, 문서·규칙·체크리스트 중심이다.

| 성과 | 상태 |
|------|------|
| `doc/PRD.md` v1.1 (Phase 4 기준) | 신규·정합 완료 |
| `README.md` 확장 (Quick Start, 계약, 아키텍처, TO-DO) | 대폭 보강 (+585/-62 lines vs main 계열) |
| PRD ↔ README 불일치 분석·수정 | 완료 |
| `.cursorrules` | 워크스페이스에 존재 (untracked) |
| Gherkin 8 Scenario 본문 | **프롬프트만** 설계 (`.feature` 파일 미생성) |

---

## 2. Git · 브랜치

### 2.1 spec 브랜치

- 현재 체크아웃: **`spec`** (`Your branch is up to date with 'origin/spec'`)
- 별도 `git checkout -b spec` 불필요 — 이미 spec에서 문서 작업 수행
- 최근 커밋(참고): `579a698` main 브랜치 초기 설정

### 2.2 작업 트리 스냅샷 (보고서 작성 시점)

| 상태 | 경로 |
|------|------|
| 수정됨 (staged 아님) | `README.md` |
| 미추적 (신규) | `doc/` (`PRD.md`, `OLD_README.md`) |
| 미추적 | `.cursorrules` |
| 미추적 | `Report/` (본 보고서) |
| 제외 대상 | `src/python/.venv/`, `__pycache__/`, `Cursor AI_퀴즈 - 문제.docx` |

> **권장:** spec에 커밋 시 `doc/`, `README.md`, `.cursorrules`, `Report/` 만 추가하고 `.venv`·`__pycache__`·퀴즈 docx는 `.gitignore` 반영.

---

## 3. 산출물 목록

### 3.1 신규·갱신 파일

| 파일 | 버전·규모 | 역할 |
|------|-----------|------|
| `doc/PRD.md` | v1.1, Phase 4 기준 | 기능 F-01~14, INV, §3.2 I/O 계약, §7 인수, RR-1~5, 부록 A/C |
| `README.md` | ~632 lines | Quick Start, Mermaid BCE, 입력/출력 예시, Activities, **TO-DO LIST** |
| `doc/OLD_README.md` | 보관 | 이전 간단 README |
| `.cursorrules` | 191 lines | TDD RED/GREEN/REFACTOR, BCE, pytest-cov 90% |
| `Report/spec-documentation-work-report.md` | 본 문서 | 작업 이력·정합 보고 |

### 3.2 설계만 수행 (저장소 미포함)

| 산출물 | 설명 |
|--------|------|
| Phase 4 Gherkin 작성 프롬프트 | 8 Scenario, INV, 공백-only·원문보존·동적 KeywordRule 테마 |
| Phase 5 PRD 작성 프롬프트 | UnitConverter PRD 포맷 → Feedback Analyzer 매핑 |
| README 확장 프롬프트 | Phase 5 PRD 기반 README 섹션 |
| TO-DO LIST 프롬프트 | M1~M4, ST-01~10, 회귀 체크리스트 |

---

## 4. 문서 역할 분담 (정합 후)

```text
doc/PRD.md          → 계약·INV·인수·회귀·Story ST-01~06 (진실원천)
        ↓ RR-1
Phase 4 Gherkin     → 8 Scenario (별도 파일화 예정)
        ↓
README.md           → 실행·학습·TO-DO·예시 I/O
project_purpose.md  → 리팩토링 챌린지 교육 맥락
.cursorrules        → AI·개발 TDD/아키텍처 규칙
```

### 4.1 PRD v1.1 주요 추가·수정

- **문서 역할** 표: PRD vs README vs `project_purpose.md`
- **§6.5** JSON API (`INV-JSON-001`, F-13)
- **§5.2** KeywordRule 로드 실패 **기본 정책 B** (`constants` fallback + `warning`)
- **부록 C:** README TO-DO의 ST-07~10 = 구현 추적용 파생 ID
- Python **3.11+** 기준 명시

### 4.2 README 주요 보강

- G-1~G-5, NG-1~3, SCN-A/B/C 요약
- Invariant 전체 링크 (§7.1, §8)
- C-09 미지원 필터, FilteredResultStore, main+sub 카테고리 정책
- AAA, RR-5, 기여 가이드 RR-1~5
- TO-DO: Phase 4, ST 매핑, 멀티라인 F-01 필수, F-14/PageLogSink 선택
- `keyword_rules.json` 예시에서 **sentiment 블록 제거** (SentimentClassifier 단일 허브)

---

## 5. PRD vs README 정합 작업 (2026-05-21)

초기 비교에서 발견된 불일치를 역할에 맞게 수정했다.

| 이슈 | 조치 |
|------|------|
| Phase 5 vs Phase 4 명칭 | README → Phase 4 PRD v1.1로 통일 |
| ST-01~10 vs ST-01~06 | PRD 부록 C + README TO-DO 메타 |
| JSON → PRD §6.2 오참조 | PRD §6.5 신설, README ST-10 수정 |
| INV 출처 (Gherkin만) | README·TO-DO → PRD §7.1 포함 |
| 멀티라인 우선순위 | F-01 필수(🔴), UI만 🟢 |
| PageLogSink | F-14 선택 명시 |
| 미지원 필터 C-09 | README 비정상 예시 #4 |
| RR-5, AAA | README 테스트·기여 섹션 |
| KeywordRule 로드 | 정책 B PRD 고정, README 동기화 |

---

## 6. TO-DO LIST (README 하단)

구현 추적용 체크리스트. **코드 미구현** — 레거시 UI는「미검증」.

| 마일스톤 | 범위 |
|----------|------|
| **M1** | 🔴 ST-01~04, INV·Gherkin·핵심 pytest |
| **M2** | 🟡 BCE·Repository·90% cov, 🔵 [M2] 기술 부채 |
| **M3** | 🟢 Trend·File DB·JSON API |
| **M4** | 🔵 Lava Flow·네이밍 |

차단 항목 예: INV-SENT-002/003, INV-COUNT-002, INV-CSV-OUT-003, 공백-only, 세션 불변.

---

## 7. 도메인·레거시 코드 현황 (참고)

문서가 전제하는 **현재** `src/python` 상태 (구현 변경 없음):

| 항목 | AS-IS |
|------|--------|
| 엔트리 | `app.py` God Function, port 8080 |
| 감정 | `text_analyzer` vs `filters.S_KEYWORDS` **이중 규칙** |
| 상태 | `fil_data`, `global_sent`, `Session` 클래스 변수 |
| 카테고리 필터 | `filters.py`가 sub만 순회, `main` 스킵 (PRD 정책과 불일치) |
| 테스트 | `tests/` 디렉터리 **미존재** (README·PRD 목표는 ≥90% cov) |

---

## 8. AI 프롬프트 자산 (재사용)

대화에서 작성·정제한 프롬프트 템플릿 (저장소 별도 경로 없음, 본 보고서에 요약):

1. **Gherkin 8개** — README/constants/.cursorrules 전제, Given-When-Then 영어
2. **PRD** — §1~8 + doc/PRD.md 저장
3. **README** — Overview~License + Activities
4. **TO-DO** — Must/Should/Nice/Debt + M1~M4 (보완판)

**주의:** TO-DO·PRD·README 작성 프롬프트에 `⚠️ 코드 작성 금지` 포함 → Agent가 문서만 생성하는 것이 **정상 동작**.

---

## 9. 미완료·후속 작업

| ID | 항목 | 권장 담당 |
|----|------|----------|
| N-1 | `doc/spec/stories.yaml` 또는 Phase 4 Story 공식 목록 | PM/Spec |
| N-2 | Gherkin `GH-01` `.feature` 파일 8 Scenario | Spec → RED pytest |
| N-3 | `tests/entity`, `tests/control` 골격 | Dev (RED) |
| N-4 | spec 브랜치 커밋·push (`doc/`, README, Report, .cursorrules) | DevOps |
| N-5 | `.gitignore` (.venv, __pycache__, 퀴즈 docx) | Dev |
| N-6 | M1 🔴 항목 구현 (SentimentClassifier 단일화 등) | Dev TDD |

---

## 10. 변경 이력 (본 보고서)

| 버전 | 일자 | 내용 |
|------|------|------|
| 1.0 | 2026-05-21 | spec 브랜치 문서화 작업 종합 보고 초안 |

---

## 11. 참조 경로

| 문서 | 경로 |
|------|------|
| PRD | `doc/PRD.md` |
| README | `README.md` |
| 프로젝트 목적 | `project_purpose.md` |
| AI 규칙 | `.cursorrules` |
| 본 보고서 | `Report/spec-documentation-work-report.md` |
