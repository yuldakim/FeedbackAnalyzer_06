# -*- coding: utf-8 -*-

from __future__ import annotations

from feedback import Feedback
from text_analyzer import TextAnalyzer

from tests.support.contract import (
    assert_inv_count_002,
    classify_sentiment_contract,
    count_categories_contract,
    count_sentiments_contract,
)

ANCHOR_TEXT = "배송이 너무 늦어요. 화가 납니다."


def test_tc_b_01_anchor_negative_sentiment_and_delivery_category():
    """INV-COUNT-002: anchor analyze yields negative sentiment, delivery category, sum equals 1."""
    # Arrange
    feedbacks = [Feedback(ANCHOR_TEXT)]
    analyzer = TextAnalyzer()

    # Act
    sentiment_results = analyzer.sent(feedbacks)
    keyword_results = analyzer.kw(feedbacks)

    # Assert — TO-BE contract (PRD/README 앵커)
    assert sentiment_results == {"긍정": 0, "중립": 0, "부정": 1}
    assert keyword_results.get("배송", 0) >= 1
    assert_inv_count_002(sentiment_results, len(feedbacks))
    assert classify_sentiment_contract(ANCHOR_TEXT) == "부정"
    assert count_sentiments_contract(feedbacks) == sentiment_results
    assert count_categories_contract(feedbacks)["배송"] >= 1
