# -*- coding: utf-8 -*-

from __future__ import annotations

from entity.sentiment_classifier import SentimentClassifier
from feedback import Feedback

from tests.support.contract import classify_sentiment_contract

_NEUTRAL_TEXT = "오늘은 특별한 일이 없었습니다."


def test_tc_b_02_neutral_only_sentence_classified_as_neutral():
    """INV-SENT-001: no positive/negative keywords → neutral sentiment."""
    # Arrange
    feedbacks = [Feedback(_NEUTRAL_TEXT)]
    sentiment = SentimentClassifier()

    # Act
    sentiment_results = sentiment.aggregate(feedbacks)

    # Then — TO-BE
    assert classify_sentiment_contract(_NEUTRAL_TEXT) == "중립"
    assert sentiment_results == {"긍정": 0, "중립": 1, "부정": 0}
