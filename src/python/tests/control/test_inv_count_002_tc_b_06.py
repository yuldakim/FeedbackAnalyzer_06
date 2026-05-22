# -*- coding: utf-8 -*-

from __future__ import annotations

from feedback import Feedback
from entity.sentiment_classifier import SentimentClassifier

from tests.support.contract import assert_inv_count_002, classify_sentiment_contract
from tests.support.fakes import InMemoryFeedbackRepository

ANCHOR_TEXT = "배송이 너무 늦어요. 화가 납니다."
_POSITIVE_TEXT = "배송이 빨라서 좋아요"
_NEUTRAL_TEXT = "오늘은 특별한 일이 없었습니다."


def test_tc_b_06_mixed_feedbacks_sentiment_sum_equals_total_count():
    """INV-COUNT-002: 긍정+중립+부정 equals number of analyzed feedbacks."""
    # Arrange
    repo = InMemoryFeedbackRepository()
    for text in (ANCHOR_TEXT, _POSITIVE_TEXT, _NEUTRAL_TEXT):
        repo.add_text(text)
    feedbacks = repo.all()
    sentiment = SentimentClassifier()

    # Act
    sentiment_results = sentiment.aggregate(feedbacks)

    # Then — TO-BE (README: anchor 부정; sum = 3)
    assert len(feedbacks) == 3
    assert_inv_count_002(sentiment_results, len(feedbacks))
    expected = {
        "긍정": sum(
            1 for fb in feedbacks if classify_sentiment_contract(fb.text) == "긍정"
        ),
        "중립": sum(
            1 for fb in feedbacks if classify_sentiment_contract(fb.text) == "중립"
        ),
        "부정": sum(
            1 for fb in feedbacks if classify_sentiment_contract(fb.text) == "부정"
        ),
    }
    # README anchor 부정 — contract helper may differ; assert analyzer matches TO-BE dict
    assert sentiment_results["긍정"] + sentiment_results["중립"] + sentiment_results[
        "부정"
    ] == 3
    assert sentiment_results == {
        "긍정": 1,
        "중립": 1,
        "부정": 1,
    }
