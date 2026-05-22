# -*- coding: utf-8 -*-
"""
Integrated TO-BE parity tests (formerly tests/tobe/).

Coverage moved here so entity/control/boundary collect a single suite.
"""

from __future__ import annotations

from entity.feedback_filter import FeedbackFilter
from entity.sentiment_classifier import SentimentClassifier
from feedback import Feedback
from tests.support.contract import classify_sentiment_contract

ANCHOR_TEXT = "배송이 너무 늦어요. 화가 납니다."
_NEUTRAL_TEXT = "오늘은 특별한 일이 없었습니다."
_BOTH_POLARITY_TEXT = "만족스럽지만 별로예요. 다시는 안 삽니다."


def test_integrated_tobe_anchor_negative():
    clf = SentimentClassifier()
    assert clf.classify(ANCHOR_TEXT) == "부정"


def test_integrated_tobe_neutral_filter_excludes_anchor():
    feedbacks = [
        Feedback(_NEUTRAL_TEXT),
        Feedback("배송이 빨라서 좋아요"),
        Feedback(ANCHOR_TEXT),
    ]
    filtered = FeedbackFilter().filter_neutral_only(feedbacks)
    assert all(classify_sentiment_contract(fb.text) == "중립" for fb in filtered)
    assert not any(fb.text == ANCHOR_TEXT for fb in filtered)


def test_integrated_tobe_mixed_weighted_positive():
    assert SentimentClassifier().classify(_BOTH_POLARITY_TEXT) == "긍정"
