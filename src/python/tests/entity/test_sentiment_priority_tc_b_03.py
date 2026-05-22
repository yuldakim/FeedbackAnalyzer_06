# -*- coding: utf-8 -*-

from __future__ import annotations

from feedback import Feedback
from text_analyzer import TextAnalyzer

from tests.support.contract import classify_sentiment_contract

_BOTH_POLARITY_TEXT = "만족스럽지만 별로예요. 다시는 안 삽니다."


def test_tc_b_03_positive_wins_when_positive_and_negative_keywords_present():
    """INV-SENT-001 order: positive before negative → label 긍정."""
    # Arrange
    feedbacks = [Feedback(_BOTH_POLARITY_TEXT)]
    analyzer = TextAnalyzer()

    # Act
    sentiment_results = analyzer.sent(feedbacks)

    # Then — TO-BE (긍→부→중립)
    assert classify_sentiment_contract(_BOTH_POLARITY_TEXT) == "긍정"
    assert sentiment_results["긍정"] == 1
    assert sentiment_results["부정"] == 0
