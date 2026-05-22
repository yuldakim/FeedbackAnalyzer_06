# -*- coding: utf-8 -*-
"""Test-only mirrors of legacy Session/analyze/upload behavior (read app.py)."""

from __future__ import annotations

import csv
import io
from typing import List, Tuple

from feedback import Feedback


def mirror_analyze_append(feedbacks: List[Feedback], text: str) -> List[Feedback]:
    stripped = text.strip()
    if stripped:
        feedbacks.append(Feedback(stripped))
    return feedbacks


def mirror_upload_csv(
    feedbacks: List[Feedback], raw: bytes
) -> Tuple[str, bool]:
    """Returns (level, mutated). level: success|error; mutated True if rows appended."""
    try:
        content = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return "error", False

    reader = csv.reader(io.StringIO(content))
    first_line = True
    appended = False
    for row in reader:
        if first_line:
            first_line = False
            continue
        if row and row[0].strip():
            feedbacks.append(Feedback(row[0].strip()))
            appended = True
    return "success", appended


def build_download_body(snapshot: List[Feedback]) -> str:
    """Same shape as app.download (INV-CSV-OUT-001~002)."""
    lines = ["\ufeff", "text\n"]
    for fb in snapshot:
        lines.append(fb.text + "\n")
    return "".join(lines)
