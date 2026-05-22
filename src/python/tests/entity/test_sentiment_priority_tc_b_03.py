# -*- coding: utf-8 -*-

from __future__ import annotations

from feedback import Feedback
from entity.sentiment_classifier import SentimentClassifier

from tests.support.contract import classify_sentiment_contract

_BOTH_POLARITY_TEXT = "만족스럽지만 별로예요. 다시는 안 삽니다."


def test_tc_b_03_positive_wins_when_positive_and_negative_keywords_present():
    """Weighted sentiment: positive score > negative on mixed text → 긍정."""
    # Arrange
    feedbacks = [Feedback(_BOTH_POLARITY_TEXT)]
    sentiment = SentimentClassifier()

    # Act
    sentiment_results = sentiment.aggregate(feedbacks)

    # Then — TO-BE (긍→부→중립)
    assert classify_sentiment_contract(_BOTH_POLARITY_TEXT) == "긍정"
    assert sentiment_results["긍정"] == 1
    assert sentiment_results["부정"] == 0
