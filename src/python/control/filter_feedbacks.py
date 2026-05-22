# -*- coding: utf-8 -*-
"""FilterFeedbacksUseCase — filter snapshot and aggregate (INV-SENT-003, INV-CSV-OUT-003)."""

from __future__ import annotations

from entity.feedback_analyzer import FeedbackAnalyzer
from entity.ports import (
    FeedbackRepositoryPort,
    FilteredResultStorePort,
    KeywordRuleRepositoryPort,
)
from control.dto import AnalysisViewModel


class FilterFeedbacksUseCase:
    def __init__(
        self,
        repository: FeedbackRepositoryPort,
        store: FilteredResultStorePort,
        analyzer: FeedbackAnalyzer | None = None,
        rule_repo: KeywordRuleRepositoryPort | None = None,
    ) -> None:
        self._analyzer = analyzer or FeedbackAnalyzer(
            repository, store=store, rule_repo=rule_repo
        )

    def execute(self, sentiment: str, keyword: str) -> AnalysisViewModel:
        if not self._analyzer.getCurrentFeedbacks():
            return AnalysisViewModel(warning="분석할 피드백이 없습니다.")

        allowed_sentiments = {"전체", "긍정", "중립", "부정"}
        if sentiment not in allowed_sentiments:
            return AnalysisViewModel(
                error=f"지원하지 않는 감정 필터입니다: {sentiment}"
            )

        filter_result = self._analyzer.filter(sentiment, keyword)
        if not filter_result.feedbacks:
            return AnalysisViewModel(warning="필터링 결과가 없습니다.")

        return AnalysisViewModel(
            sentiment_results=filter_result.sentiment_results,
            keyword_results=filter_result.keyword_results,
            feedback_texts=[fb.text for fb in filter_result.feedbacks],
        )
