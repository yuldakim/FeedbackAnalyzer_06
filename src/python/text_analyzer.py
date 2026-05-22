# -*- coding: utf-8 -*-
"""Legacy analyze shim — delegates to entity classifiers (INV-SENT-002)."""

from __future__ import annotations

from typing import Dict, List

from entity.category_classifier import CategoryClassifier
from entity.sentiment_classifier import SentimentClassifier
from feedback import Feedback


class TextAnalyzer:
    def __init__(self) -> None:
        self._sentiment = SentimentClassifier()
        self._category = CategoryClassifier()

    def sent(self, feedbacks: List[Feedback]) -> Dict[str, int]:
        return self._sentiment.aggregate(feedbacks)

    def kw(self, feedbacks: List[Feedback]) -> Dict[str, int]:
        return self._category.aggregate(feedbacks)
