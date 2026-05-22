# -*- coding: utf-8 -*-
"""FilterFeedbacksUseCase — filter snapshot and aggregate (INV-SENT-003, INV-CSV-OUT-003)."""

from __future__ import annotations

from entity.category_classifier import CategoryClassifier
from entity.feedback_filter import FeedbackFilter
from entity.sentiment_classifier import SentimentClassifier
from entity.ports import FeedbackRepositoryPort, FilteredResultStorePort
from control.dto import AnalysisViewModel


class FilterFeedbacksUseCase:
    def __init__(
        self,
        repository: FeedbackRepositoryPort,
        store: FilteredResultStorePort,
        feedback_filter: FeedbackFilter | None = None,
        sentiment: SentimentClassifier | None = None,
        category: CategoryClassifier | None = None,
    ) -> None:
        self._repository = repository
        self._store = store
        self._filter = feedback_filter or FeedbackFilter()
        self._sentiment = sentiment or SentimentClassifier()
        self._category = category or CategoryClassifier()

    def execute(self, sentiment: str, keyword: str) -> AnalysisViewModel:
        feedbacks = self._repository.all()
        if not feedbacks:
            return AnalysisViewModel(warning="분석할 피드백이 없습니다.")

        allowed_sentiments = {"전체", "긍정", "중립", "부정"}
        if sentiment not in allowed_sentiments:
            return AnalysisViewModel(
                error=f"지원하지 않는 감정 필터입니다: {sentiment}"
            )

        filtered = self._filter.filter(feedbacks, sentiment, keyword)
        if not filtered:
            return AnalysisViewModel(warning="필터링 결과가 없습니다.")

        self._store.save(filtered)
        return AnalysisViewModel(
            sentiment_results=self._sentiment.aggregate(filtered),
            keyword_results=self._category.aggregate(filtered),
            feedback_texts=[fb.text for fb in filtered],
        )
