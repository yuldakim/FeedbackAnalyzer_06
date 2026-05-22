# -*- coding: utf-8 -*-

from __future__ import annotations

from feedback import Feedback
from filters import filter_feedbacks

from tests.conftest import ANCHOR_TEXT
from tests.support.legacy_session import build_download_body

_POSITIVE_TEXT = "배송이 빨라서 좋아요"


def test_tc_b_09_filter_snapshot_row_order_matches_download_body():
    """INV-CSV-OUT-003: download CSV rows follow filter snapshot order."""
    # Arrange
    feedbacks = [Feedback(ANCHOR_TEXT), Feedback(_POSITIVE_TEXT)]

    # Act — TO-BE: filter keeps both for 전체/전체; snapshot order preserved
    snapshot = filter_feedbacks(feedbacks, "전체", "전체")
    csv_body = build_download_body(snapshot)

    # Then
    text = csv_body.lstrip("\ufeff")
    lines = text.splitlines()
    assert lines[0] == "text"
    assert lines[1:] == [fb.text for fb in snapshot]
    assert snapshot[0].text == ANCHOR_TEXT
    assert len(snapshot) == 2
