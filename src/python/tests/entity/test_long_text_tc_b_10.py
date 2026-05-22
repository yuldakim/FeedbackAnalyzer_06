# -*- coding: utf-8 -*-

from __future__ import annotations

from feedback import Feedback
from text_analyzer import TextAnalyzer

from tests.support.contract import assert_inv_count_002, classify_sentiment_contract

ANCHOR_PREFIX = "배송"
ANCHOR_SUFFIX = "화남"


def test_tc_b_10_long_text_original_equality_and_classification_complete():
    """INV-TEXT-001: ~10k chars preserved; classification completes; INV-COUNT-002."""
    # Arrange
    long_text = ANCHOR_PREFIX + ("x" * 9996) + ANCHOR_SUFFIX
    assert len(long_text) >= 10_000
    feedbacks = [Feedback(long_text)]
    analyzer = TextAnalyzer()

    # Act
    sentiment_results = analyzer.sent(feedbacks)
    keyword_results = analyzer.kw(feedbacks)

    # Then — TO-BE
    assert feedbacks[0].text == long_text
    assert classify_sentiment_contract(long_text) == "부정"
    assert sentiment_results == {"긍정": 0, "중립": 0, "부정": 1}
    assert keyword_results.get("배송", 0) >= 1
    assert_inv_count_002(sentiment_results, 1)
