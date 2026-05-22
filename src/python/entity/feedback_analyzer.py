# -*- coding: utf-8 -*-
"""FeedbackAnalyzer — C++-style naming facade over domain services."""

from __future__ import annotations

from typing import Dict, List, Optional

from entity.category_classifier import CategoryClassifier
from entity.filter_result import FilterResult
from entity.feedback_filter import FeedbackFilter
from entity.ports import (
    FeedbackRepositoryPort,
    FilteredResultStorePort,
    KeywordRuleRepositoryPort,
)
from entity.sentiment_classifier import SentimentClassifier
from feedback import Feedback
from infrastructure.file_handler import FileHandler


class FeedbackAnalyzer:
    """
    Legacy naming mapping:
      sent()  -> analyzeSentiment()
      kw()    -> analyzeKeywords()
      fil()   -> filter() -> FilterResult
      getOldDataFromSession() -> getCurrentFeedbacks()
    """

    def __init__(
        self,
        repository: FeedbackRepositoryPort,
        store: Optional[FilteredResultStorePort] = None,
        sentiment: SentimentClassifier | None = None,
        category: CategoryClassifier | None = None,
        feedback_filter: FeedbackFilter | None = None,
        file_handler: FileHandler | None = None,
        rule_repo: KeywordRuleRepositoryPort | None = None,
    ) -> None:
        self._repository = repository
        self._store = store
        self._sentiment = sentiment or SentimentClassifier(rule_repo)
        self._category = category or CategoryClassifier(rule_repo)
        self._filter = feedback_filter or FeedbackFilter(
            self._sentiment, self._category
        )
        self._file_handler = file_handler

    def getCurrentFeedbacks(self) -> List[Feedback]:
        return list(self._repository.all())

    def analyzeSentiment(self, text: str) -> str:
        return self._sentiment.analyzeSentiment(text)

    def analyzeSentimentScores(self, text: str) -> Dict[str, float]:
        return self._sentiment.scoreSentiment(text)

    def matchCategories(self, text: str) -> List[str]:
        return self._category.match_categories(text)

    def analyzeKeywords(self, feedbacks: List[Feedback]) -> Dict[str, int]:
        return self._category.analyzeKeywords(feedbacks)

    def aggregateSentiment(self, feedbacks: List[Feedback]) -> Dict[str, int]:
        return self._sentiment.aggregate(feedbacks)

    def filter(self, sentiment: str = "전체", keyword: str = "전체") -> FilterResult:
        feedbacks = self.getCurrentFeedbacks()
        filtered = self._filter.filter(feedbacks, sentiment, keyword)
        result = FilterResult(
            feedbacks=filtered,
            sentiment_results=self._sentiment.aggregate(filtered),
            keyword_results=self._category.aggregate(filtered),
        )
        if self._store is not None and filtered:
            self._store.save(filtered)
        return result

    def persistFeedbacksToCsv(self, path: str) -> int:
        """FileHandler CSV export of current session feedbacks."""
        if self._file_handler is None:
            raise RuntimeError("FileHandler is not configured")
        feedbacks = self.getCurrentFeedbacks()
        self._file_handler.saveFeedbacksCsv(path, feedbacks)
        return len(feedbacks)
