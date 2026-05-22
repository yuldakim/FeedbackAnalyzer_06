# -*- coding: utf-8 -*-
"""AnalyzeFeedbackUseCase — trim, append, aggregate (F-01, INV-COUNT-002)."""

from __future__ import annotations

from entity.feedback_analyzer import FeedbackAnalyzer
from entity.ports import FeedbackRepositoryPort, KeywordRuleRepositoryPort
from control.dto import AnalysisViewModel
from infrastructure.file_handler import FileHandler


class AnalyzeFeedbackUseCase:
    def __init__(
        self,
        repository: FeedbackRepositoryPort,
        analyzer: FeedbackAnalyzer | None = None,
        file_handler: FileHandler | None = None,
        export_path: str | None = None,
        rule_repo: KeywordRuleRepositoryPort | None = None,
    ) -> None:
        self._repository = repository
        self._analyzer = analyzer or FeedbackAnalyzer(
            repository,
            file_handler=file_handler,
            rule_repo=rule_repo,
        )
        self._export_path = export_path

    def execute(self, text: str) -> AnalysisViewModel:
        stripped = text.strip()
        if stripped:
            self._repository.add_text(stripped)
        feedbacks = self._analyzer.getCurrentFeedbacks()
        if self._export_path and feedbacks:
            self._analyzer.persistFeedbacksToCsv(self._export_path)
        return AnalysisViewModel(
            success=f"{len(feedbacks)}개의 피드백이 입력되었습니다.",
            sentiment_results=self._analyzer.aggregateSentiment(feedbacks),
            keyword_results=self._analyzer.analyzeKeywords(feedbacks),
            feedback_texts=[fb.text for fb in feedbacks],
        )
