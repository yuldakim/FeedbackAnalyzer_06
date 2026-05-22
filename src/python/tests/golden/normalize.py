# -*- coding: utf-8 -*-
"""Golden Master capture — HTTP/HTML/CSV 정규화 (동적 타임스탬프·집계 추출)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from html import unescape
from typing import Dict, List, Optional

TIMESTAMP_PATTERN = re.compile(
    r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\s*:\s*"
)
SUCCESS_MSG_PATTERN = re.compile(
    r"(\d+)개의 피드백이 입력되었습니다\."
)
STAT_PATTERN = re.compile(
    r'<div class="stat-number">(\d+)</div>\s*'
    r'<div class="stat-label">([^<]+)</div>'
)
ORIGINAL_ITEM_PATTERN = re.compile(
    r"<li>([^<]*(?:<(?!/li>)[^<]*)*)</li>",
    re.DOTALL,
)

SENTIMENT_LABELS = ("긍정", "중립", "부정")
CATEGORY_LABELS = ("배송", "품질", "가격", "서비스", "사용성")


@dataclass
class PageSnapshot:
    """정규화된 페이지 계약 스냅샷."""

    scenario_id: str
    level: str  # success | warning | error | none
    message: str = ""
    expected_count: Optional[int] = None
    sentiment: Dict[str, int] = field(default_factory=dict)
    keyword: Dict[str, int] = field(default_factory=dict)
    originals: List[str] = field(default_factory=list)

    def to_canonical_block(self, *, include_legacy_header: bool = False) -> str:
        lines: List[str] = []
        if include_legacy_header:
            lines.append(f"=== {self.scenario_id} ===")
        lines.extend(
            [
            f"level: {self.level}",
            ]
        )
        if self.message:
            lines.append(f"message: {self.message}")
        if self.expected_count is not None:
            lines.append(f"expected_count: {self.expected_count}")
        if self.sentiment:
            lines.append("sentiment:")
            for label in SENTIMENT_LABELS:
                if label in self.sentiment:
                    lines.append(f"  {label}: {self.sentiment[label]}")
        if self.keyword:
            lines.append("keyword:")
            for label in CATEGORY_LABELS:
                if label in self.keyword:
                    lines.append(f"  {label}: {self.keyword[label]}")
        if self.originals:
            lines.append("originals:")
            for text in self.originals:
                lines.append(f"  - {text}")
        return "\n".join(lines) + "\n"


def normalize_timestamp(text: str) -> str:
    return TIMESTAMP_PATTERN.sub("[TIMESTAMP] ", text)


def normalize_success_count(text: str, expected_count: int) -> str:
    return SUCCESS_MSG_PATTERN.sub(
        f"{expected_count}개의 피드백이 입력되었습니다.", text
    )


def _extract_alert_level(html: str) -> str:
    """`<p class="alert …">` 만 검사 (CSS `.alert-success` 오탐 방지)."""
    for css, level in (
        ("alert-warning", "warning"),
        ("alert-danger", "error"),
        ("alert-success", "success"),
    ):
        if re.search(rf'<p class="alert {css}">', html):
            return level
    return "none"


def _extract_alert_message(html: str) -> str:
    for css in ("alert-success", "alert-warning", "alert-danger"):
        match = re.search(
            rf'<p class="alert {css}">([^<]+)</p>',
            html,
        )
        if match:
            raw = unescape(match.group(1).strip())
            raw = normalize_timestamp(raw)
            return raw
    return ""


def _extract_stats(html: str) -> tuple[Dict[str, int], Dict[str, int]]:
    sentiment: Dict[str, int] = {}
    keyword: Dict[str, int] = {}
    for number, label in STAT_PATTERN.findall(html):
        label = label.strip()
        value = int(number)
        if label in SENTIMENT_LABELS:
            sentiment[label] = value
        elif label in CATEGORY_LABELS:
            keyword[label] = value
    return sentiment, keyword


def _extract_originals(html: str) -> List[str]:
    section = re.search(
        r"<h3>피드백 원문</h3>\s*<ul>(.*?)</ul>",
        html,
        re.DOTALL,
    )
    if not section:
        return []
    items = ORIGINAL_ITEM_PATTERN.findall(section.group(1))
    return [unescape(item.strip()) for item in items if item.strip()]


def snapshot_from_html(
    scenario_id: str,
    html: str,
    *,
    expected_count: Optional[int] = None,
) -> PageSnapshot:
    level = _extract_alert_level(html)
    message = _extract_alert_message(html)
    if expected_count is not None and message:
        message = normalize_success_count(message, expected_count)
    sentiment, keyword = _extract_stats(html)
    originals = _extract_originals(html)
    return PageSnapshot(
        scenario_id=scenario_id,
        level=level,
        message=message,
        expected_count=expected_count,
        sentiment=sentiment,
        keyword=keyword,
        originals=originals,
    )


def parse_golden_master_file(content: str) -> Dict[str, str]:
    """feedback_golden_master.txt → {scenario_id: block_text}."""
    blocks: Dict[str, str] = {}
    current_id: Optional[str] = None
    current_lines: List[str] = []

    for line in content.splitlines():
        if line.startswith("=== ") and line.endswith(" ==="):
            if current_id is not None:
                blocks[current_id] = "\n".join(current_lines) + "\n"
            current_id = line[4:-4].strip()
            current_lines = [line]
        elif current_id is not None:
            current_lines.append(line)

    if current_id is not None:
        blocks[current_id] = "\n".join(current_lines).rstrip() + "\n"
    return blocks


def normalize_csv_body(raw: bytes) -> bytes:
    """Golden CSV 비교용 — BOM 유지, trailing newline 정규화."""
    if not raw.startswith(b"\xef\xbb\xbf"):
        raw = b"\xef\xbb\xbf" + raw.lstrip(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    lines = text.splitlines()
    return ("\n".join(lines) + "\n").encode("utf-8")
