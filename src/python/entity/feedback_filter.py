# -*- coding: utf-8 -*-
"""FeedbackFilter — SentimentClassifier·CategoryClassifier 기반 필터."""

from __future__ import annotations

from typing import List

from entity.category_classifier import CategoryClassifier
from entity.sentiment_classifier import SentimentClassifier
from feedback import Feedback


class FeedbackFilter:
    def __init__(
        self,
        classifier: SentimentClassifier | None = None,
        category_classifier: CategoryClassifier | None = None,
    ) -> None:
        self._classifier = classifier or SentimentClassifier()
        self._category = category_classifier or CategoryClassifier()

    def filter(
        self,
        feedbacks: List[Feedback],
        sentiment: str = "전체",
        keyword: str = "전체",
    ) -> List[Feedback]:
        result = list(feedbacks)
        if sentiment != "전체":
            result = [
                fb
                for fb in result
                if self._classifier.classify(fb.text) == sentiment
            ]
        if keyword != "전체":
            result = [
                fb
                for fb in result
                if keyword in self._category.match_categories(fb.text)
            ]
        return result

    def filter_neutral_only(self, feedbacks: List[Feedback]) -> List[Feedback]:
        return self.filter(feedbacks, sentiment="중립", keyword="전체")

    def filter_category(
        self, feedbacks: List[Feedback], category: str
    ) -> List[Feedback]:
        return self.filter(feedbacks, sentiment="전체", keyword=category)
