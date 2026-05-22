# -*- coding: utf-8 -*-

from __future__ import annotations

from feedback import Feedback
from entity.feedback_filter import FeedbackFilter

from constants import CATEGORY_KEYWORDS

# main "품질" only — sub buckets omit standalone "품질" (legacy skips main)
_QUALITY_MAIN_ONLY_TEXT = "품질이 기대에 못 미쳐요"


def test_tc_b_11_category_filter_matches_main_keywords_not_sub_only():
    """F-03 / PRD §5.1: category filter must match main + sub; legacy skips main."""
    # Arrange
    feedbacks = [Feedback(_QUALITY_MAIN_ONLY_TEXT)]
    assert any(
        kw in _QUALITY_MAIN_ONLY_TEXT
        for kw in CATEGORY_KEYWORDS["품질"]["main"]
    )

    # Act
    filtered = FeedbackFilter().filter(feedbacks, "전체", "품질")

    # Then — TO-BE: 1 row; AS-IS filters.py continues sub only → 0
    assert len(filtered) == 1
    assert filtered[0].text == _QUALITY_MAIN_ONLY_TEXT
