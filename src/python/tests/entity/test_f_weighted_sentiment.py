# -*- coding: utf-8 -*-
"""TEST_F — weighted sentiment analysis (independent feature cases)."""

from __future__ import annotations

import pytest

from entity.sentiment_classifier import SentimentClassifier
from feedback import Feedback

pytestmark = pytest.mark.TEST_F


@pytest.fixture
def classifier() -> SentimentClassifier:
    return SentimentClassifier()


def test_f_01_pure_positive_high_score(classifier: SentimentClassifier):
    """TEST_F-01: only positive keywords → 긍정."""
    text = "정말 좋아요. 최고입니다. 감사합니다."
    scores = classifier.scoreSentiment(text)
    assert scores["긍정"] > scores["부정"]
    assert classifier.analyzeSentiment(text) == "긍정"


def test_f_02_pure_negative_high_score(classifier: SentimentClassifier):
    """TEST_F-02: only negative keywords → 부정."""
    text = "배송이 너무 늦어요. 화가 납니다."
    scores = classifier.scoreSentiment(text)
    assert scores["부정"] > scores["긍정"]
    assert classifier.analyzeSentiment(text) == "부정"


def test_f_03_mixed_equal_single_hit_tie_breaker_negative(
    classifier: SentimentClassifier,
):
    """TEST_F-03: one positive + one negative hit, equal weight → tie-breaker 부정."""
    text = "좋아요 but 별로"
    scores = classifier.scoreSentiment(text)
    assert scores["긍정"] >= 1.0
    assert scores["부정"] >= 1.0
    assert classifier.analyzeSentiment(text) == "부정"


def test_f_04_mixed_weighted_positive_wins(classifier: SentimentClassifier):
    """TEST_F-04: multiple positive weights beat single negative."""
    text = "만족스럽지만 별로예요. 다시는 안 삽니다."
    scores = classifier.scoreSentiment(text)
    assert scores["긍정"] > scores["부정"]
    assert classifier.analyzeSentiment(text) == "긍정"


def test_f_05_neutral_only_when_no_keyword_hits(classifier: SentimentClassifier):
    """TEST_F-05: no hits → 중립 (not else-fallback on unrelated text)."""
    text = "오늘은 특별한 일이 없었습니다."
    scores = classifier.scoreSentiment(text)
    assert scores["긍정"] == 0.0 and scores["부정"] == 0.0
    assert classifier.analyzeSentiment(text) == "중립"


def test_f_06_aggregate_inv_count_002(classifier: SentimentClassifier):
    """TEST_F-06: aggregate sum equals feedback count."""
    feedbacks = [
        Feedback("좋아요"),
        Feedback("오늘은 특별한 일이 없었습니다."),
        Feedback("화가 납니다"),
    ]
    counts = classifier.aggregate(feedbacks)
    assert sum(counts.values()) == len(feedbacks)
