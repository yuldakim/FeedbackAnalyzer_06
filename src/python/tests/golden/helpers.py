# -*- coding: utf-8 -*-
"""
Golden Master load / approve / diff helpers.

환경 변수:
  APPROVE_GOLDEN=1  — 기준 없거나 불일치 시 현재 캡처로 파일 갱신 후 pytest.skip (1회 승인)
"""

from __future__ import annotations

import difflib
import os
import re
from pathlib import Path
from typing import Dict, Optional

import pytest

from tests.golden.normalize import normalize_csv_body

GOLDEN_DIR = Path(__file__).resolve().parent
MASTER_PATH = GOLDEN_DIR / "feedback_golden_master.txt"
CSV_GOLDEN_PATH = GOLDEN_DIR / "download_filtered_anchor.csv"

# 섹션 ID → 파일 내 헤더 라인 (load_section 인자로 ID 또는 헤더 전체 허용)
SECTION_HEADERS: Dict[str, str] = {
    "S1": "[S1: SCN-A anchor POST /analyze]",
    "S2": "[S2: positive delivery POST /analyze]",
    "S3": "[S3: whitespace-only INV-INPUT-001]",
    "S4": "[S4: zero feedback filter INV-EMPTY-001]",
}

_HEADER_LINE_RE = re.compile(r"^\[(S\d+):[^\]]+\]\s*$|^\=== (S\d+) ===\s*$")


def approve_golden_enabled() -> bool:
    return os.environ.get("APPROVE_GOLDEN", "").strip() in ("1", "true", "yes")


def _resolve_section_key(section: str) -> str:
    """'S1' 또는 '[S1: …]' → 'S1'."""
    section = section.strip()
    match = _HEADER_LINE_RE.match(section)
    if match:
        return match.group(1) or match.group(2)
    if section in SECTION_HEADERS:
        return section
    for key, header in SECTION_HEADERS.items():
        if section == header:
            return key
    raise KeyError(f"Unknown golden section: {section!r}")


def _parse_master_sections(content: str) -> Dict[str, str]:
    """Parse feedback_golden_master.txt → {S1: block_body}."""
    sections: Dict[str, str] = {}
    current_key: Optional[str] = None
    current_lines: list[str] = []

    for line in content.splitlines():
        if line.startswith("#"):
            continue
        header_match = _HEADER_LINE_RE.match(line)
        if header_match:
            if current_key is not None:
                sections[current_key] = _finalize_block(current_lines)
            current_key = header_match.group(1) or header_match.group(2)
            current_lines = []
            continue
        if current_key is not None:
            current_lines.append(line)

    if current_key is not None:
        sections[current_key] = _finalize_block(current_lines)
    return sections


def _finalize_block(lines: list[str]) -> str:
    body = "\n".join(lines).strip()
    return (body + "\n") if body else ""


def _read_master_file() -> str:
    if not MASTER_PATH.is_file():
        return ""
    return MASTER_PATH.read_text(encoding="utf-8")


def _write_master_sections(sections: Dict[str, str]) -> None:
    header_comment = (
        "# Feedback Analyzer — Golden Master (HTML/메시지 정규화)\n"
        "# GREEN baseline · X-09 RR-1(앵커 부정) 반영 후 approve\n"
        "# 재생성: APPROVE_GOLDEN=1 pytest … 또는 python tests/golden/regenerate.py\n\n"
    )
    order = ("S1", "S2", "S3", "S4")
    parts = [header_comment]
    for key in order:
        if key not in sections:
            continue
        parts.append(SECTION_HEADERS[key])
        body = sections[key].rstrip()
        if body:
            parts.append(body)
        parts.append("")
    MASTER_PATH.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")


def load_section(section: str) -> Optional[str]:
    """
    기준 블록 로드.

    Args:
        section: ``S1`` 또는 ``[S1: SCN-A anchor POST /analyze]``

    Returns:
        정규화된 본문(헤더 제외). 파일·섹션 없으면 ``None``.
    """
    key = _resolve_section_key(section)
    content = _read_master_file()
    if not content:
        return None
    return _parse_master_sections(content).get(key)


def load_csv_golden() -> Optional[bytes]:
    """S5 CSV golden (BOM 유지, 줄바꿈 정규화). 없으면 None."""
    if not CSV_GOLDEN_PATH.is_file():
        return None
    return normalize_csv_body(CSV_GOLDEN_PATH.read_bytes())


def save_section(section: str, body: str) -> None:
    """단일 섹션 저장(merge)."""
    key = _resolve_section_key(section)
    sections = _parse_master_sections(_read_master_file()) if MASTER_PATH.is_file() else {}
    sections[key] = body.rstrip() + "\n"
    _write_master_sections(sections)


def save_csv_golden(raw: bytes) -> None:
    CSV_GOLDEN_PATH.write_bytes(normalize_csv_body(raw))


def _format_unified_diff(
    expected: str,
    actual: str,
    *,
    label: str,
) -> str:
    expected_lines = expected.rstrip().splitlines(keepends=True)
    actual_lines = actual.rstrip().splitlines(keepends=True)
    if expected_lines and not expected_lines[-1].endswith("\n"):
        expected_lines[-1] += "\n"
    if actual_lines and not actual_lines[-1].endswith("\n"):
        actual_lines[-1] += "\n"
    diff = difflib.unified_diff(
        expected_lines,
        actual_lines,
        fromfile=f"expected ({label})",
        tofile="actual",
        lineterm="",
    )
    return "\n".join(diff)


def assert_golden_text(
    actual: str,
    section: str,
    *,
    status_code: int = 200,
) -> None:
    """
    S1~S4 HTML 정규화 블록 Approval.

    - 기준 없음 + ``APPROVE_GOLDEN=1`` → 저장 후 skip
    - 불일치 → unified diff 출력 후 FAIL
    """
    key = _resolve_section_key(section)
    label = f"tests/golden/feedback_golden_master.txt [{SECTION_HEADERS[key]}]"
    expected = load_section(key)

    if status_code != 200:
        pytest.fail(f"[{key}] expected HTTP 200, got {status_code}")

    actual_norm = actual.rstrip() + "\n"

    if expected is None:
        if approve_golden_enabled():
            save_section(key, actual_norm)
            pytest.skip(
                f"Golden approved: wrote {label}. "
                "Re-run without APPROVE_GOLDEN to enforce."
            )
        pytest.fail(
            f"Missing golden section {SECTION_HEADERS[key]}. "
            "Set APPROVE_GOLDEN=1 to capture GREEN baseline."
        )

    expected_norm = expected.rstrip() + "\n"
    if actual_norm == expected_norm:
        return

    if approve_golden_enabled():
        save_section(key, actual_norm)
        pytest.skip(
            f"Golden updated: {label}. Re-run without APPROVE_GOLDEN to enforce."
        )

    diff_text = _format_unified_diff(expected_norm, actual_norm, label=label)
    pytest.fail(
        f"Golden Master mismatch [{SECTION_HEADERS[key]}]\n"
        f"{diff_text or '(no diff lines)'}"
    )


def assert_golden_csv(actual: bytes) -> None:
    """S5 CSV Approval (바이트 비교, BOM 유지)."""
    label = "tests/golden/download_filtered_anchor.csv"
    expected = load_csv_golden()
    actual_norm = normalize_csv_body(actual)

    if expected is None:
        if approve_golden_enabled():
            save_csv_golden(actual_norm)
            pytest.skip(
                f"Golden approved: wrote {label}. "
                "Re-run without APPROVE_GOLDEN to enforce."
            )
        pytest.fail(
            f"Missing {label}. Set APPROVE_GOLDEN=1 to capture GREEN baseline."
        )

    if actual_norm == expected:
        return

    if approve_golden_enabled():
        save_csv_golden(actual_norm)
        pytest.skip(f"Golden updated: {label}. Re-run without APPROVE_GOLDEN to enforce.")

    exp_text = expected.decode("utf-8-sig")
    act_text = actual_norm.decode("utf-8-sig")
    diff_text = _format_unified_diff(exp_text, act_text, label=label)
    pytest.fail(f"Golden CSV mismatch\n{diff_text or '(no diff lines)'}")
