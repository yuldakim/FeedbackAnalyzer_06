# -*- coding: utf-8 -*-
"""Read-only mirrors of analyze vs filter sentiment labeling (test-only)."""

from __future__ import annotations

from typing import List

from entity.feedback_filter import FeedbackFilter
from entity.sentiment_classifier import SentimentClassifier
from feedback import Feedback

_classifier = SentimentClassifier()
_filter = FeedbackFilter()


def label_sentiment_analyze_path(text: str) -> str:
    return _classifier.classify(text)


def label_sentiment_filter_path(text: str) -> str:
    return _classifier.classify(text)


def analyze_sentiment_counts(feedbacks: List[Feedback]) -> dict[str, int]:
    return _classifier.aggregate(feedbacks)


def filter_all_sentiment_counts(feedbacks: List[Feedback]) -> dict[str, int]:
    filtered = _filter.filter(feedbacks, "전체", "전체")
    return _classifier.aggregate(filtered)
