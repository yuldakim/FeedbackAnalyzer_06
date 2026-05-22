# -*- coding: utf-8 -*-
"""AnalyzeFeedbackUseCase — STUB / RED phase."""

from __future__ import annotations

from entity.category_classifier import CategoryClassifier
from entity.sentiment_classifier import SentimentClassifier
from entity.ports import FeedbackRepositoryPort
from control.dto import AnalysisViewModel


class AnalyzeFeedbackUseCase:
    def __init__(
        self,
        repository: FeedbackRepositoryPort,
        sentiment: SentimentClassifier | None = None,
        category: CategoryClassifier | None = None,
    ) -> None:
        self._repository = repository
        self._sentiment = sentiment or SentimentClassifier()
        self._category = category or CategoryClassifier()

    def execute(self, text: str) -> AnalysisViewModel:
        # STUB: trim·append 정책 미구현; 집계 스텁 반환
        stripped = text.strip()
        if stripped:
            self._repository.add_text(stripped)
        feedbacks = self._repository.all()
        return AnalysisViewModel(
            success=f"{len(feedbacks)}개의 피드백이 입력되었습니다.",
            sentiment_results=self._sentiment.aggregate(feedbacks),
            keyword_results=self._category.aggregate(feedbacks),
            feedback_texts=[fb.text for fb in feedbacks],
        )
