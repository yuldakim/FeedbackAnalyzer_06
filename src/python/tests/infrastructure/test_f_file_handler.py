# -*- coding: utf-8 -*-
"""TEST_F — FileHandler CSV persistence."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from feedback import Feedback
from infrastructure.file_handler import FileHandler

pytestmark = pytest.mark.TEST_F


def test_f_07_file_handler_save_feedbacks_csv(tmp_path: Path):
    """TEST_F-07: saveFeedbacksCsv writes BOM + text header + rows."""
    path = tmp_path / "out.csv"
    feedbacks = [
        Feedback("첫 줄"),
        Feedback("배송이 너무 늦어요. 화가 납니다."),
    ]
    FileHandler().saveFeedbacksCsv(path, feedbacks)
    raw = path.read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    assert rows[0] == ["text"]
    assert rows[1][0] == "첫 줄"
    assert rows[2][0] == "배송이 너무 늦어요. 화가 납니다."


def test_f_08_file_handler_save_analysis_csv(tmp_path: Path):
    """TEST_F-08: saveAnalysisCsv includes labels and aggregate sections."""
    path = tmp_path / "analysis.csv"
    feedbacks = [Feedback("좋아요")]
    handler = FileHandler()
    handler.saveAnalysisCsv(
        path,
        feedbacks,
        {"긍정": 1, "중립": 0, "부정": 0},
        {"배송": 0, "품질": 0, "가격": 0, "서비스": 0, "사용성": 0},
    )
    text = path.read_text(encoding="utf-8-sig")
    assert "text,sentiment_label" in text
    assert "좋아요,긍정" in text
    assert "# sentiment_aggregate" in text
