# -*- coding: utf-8 -*-
"""
TO-BE entity layer RED (tests/tobe — avoids tests/entity vs domain entity name clash).

기존 tests/entity/test_*.py (레거시) 는 수정하지 않음.
"""

from __future__ import annotations

import pytest

from entity.category_classifier import CategoryClassifier
from entity.feedback_filter import FeedbackFilter
from entity.sentiment_classifier import SentimentClassifier
from feedback import Feedback
from tests.support.contract import classify_sentiment_contract

ANCHOR_TEXT = "배송이 너무 늦어요. 화가 납니다."
_NEUTRAL_TEXT = "오늘은 특별한 일이 없었습니다."
_BOTH_POLARITY_TEXT = "만족스럽지만 별로예요. 다시는 안 삽니다."
_QUALITY_MAIN_ONLY = "품질이 기대에 못 미쳐요"


def test_tobe_tc_b_01_sentiment_classifier_anchor_negative():
    """INV-COUNT-002 / README 앵커: SentimentClassifier → 부정."""
    # Arrange
    classifier = SentimentClassifier()

    # Act
    label = classifier.classify(ANCHOR_TEXT)
    counts = classifier.aggregate([Feedback(ANCHOR_TEXT)])

    # Assert — TO-BE (스켈레톤은 중립/0 반환 → RED)
    assert label == "부정", f"Expected 부정, got {label!r} (STUB)"
    assert counts == {"긍정": 0, "중립": 0, "부정": 1}


def test_tobe_tc_b_02_sentiment_classifier_neutral_only():
    """INV-SENT-001: 긍·부 미매칭 → 중립."""
    # Arrange
    classifier = SentimentClassifier()

    # Act
    label = classifier.classify(_NEUTRAL_TEXT)

    # Assert
    assert classify_sentiment_contract(_NEUTRAL_TEXT) == "중립"
    assert label == "중립"
    assert classifier.classify(ANCHOR_TEXT) == "부정"


def test_tobe_tc_b_03_sentiment_classifier_positive_priority():
    """INV-SENT-001 order: 긍정 → 부정 → 중립."""
    # Arrange
    classifier = SentimentClassifier()

    # Act
    label = classifier.classify(_BOTH_POLARITY_TEXT)

    # Assert
    assert label == "긍정"


def test_tobe_tc_b_05_feedback_filter_neutral_excludes_anchor():
    """INV-SENT-003: Filter neutral-only excludes README negative anchor."""
    # Arrange
    feedbacks = [
        Feedback(_NEUTRAL_TEXT),
        Feedback("배송이 빨라서 좋아요"),
        Feedback(ANCHOR_TEXT),
    ]
    flt = FeedbackFilter()

    # Act
    filtered = flt.filter_neutral_only(feedbacks)

    # Assert — TO-BE
    assert all(classify_sentiment_contract(fb.text) == "중립" for fb in filtered)
    assert not any(fb.text == ANCHOR_TEXT for fb in filtered)


def test_tobe_tc_b_11_category_classifier_main_match_quality():
    """F-03 / X-05: category filter matches main keywords."""
    # Arrange
    flt = FeedbackFilter()
    feedbacks = [Feedback(_QUALITY_MAIN_ONLY)]

    # Act
    filtered = flt.filter_category(feedbacks, "품질")

    # Assert
    assert len(filtered) == 1
    assert filtered[0].text == _QUALITY_MAIN_ONLY


def test_tobe_tc_b_12_category_classifier_aggregate_delivery():
    """CategoryClassifier detects 배송 on anchor."""
    # Arrange
    classifier = CategoryClassifier()
    feedbacks = [Feedback(ANCHOR_TEXT)]

    # Act
    counts = classifier.aggregate(feedbacks)

    # Assert
    assert counts.get("배송", 0) >= 1
