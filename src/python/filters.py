# -*- coding: utf-8 -*-
"""Legacy filter shim — delegates to entity.FeedbackFilter (INV-SENT-002/003)."""

from __future__ import annotations

from typing import List

from entity.feedback_filter import FeedbackFilter
from entity.sentiment_classifier import SentimentClassifier
from feedback import Feedback

_filter = FeedbackFilter()
_classifier = SentimentClassifier()


def _label_sentiment(text: str) -> str:
    return _classifier.classify(text)


def filter_feedbacks(
    data_list: List[Feedback],
    sentiment_filter: str,
    keyword_filter: str,
) -> List[Feedback]:
    result = _filter.filter(data_list, sentiment_filter, keyword_filter)
    for fb in result:
        print(fb.text)
    return result
