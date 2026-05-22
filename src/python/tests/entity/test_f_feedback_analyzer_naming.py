# -*- coding: utf-8 -*-
"""TEST_F — C++-style naming (analyzeSentiment, analyzeKeywords, filter, FilterResult)."""

from __future__ import annotations

import pytest

from entity.feedback_analyzer import FeedbackAnalyzer
from entity.filter_result import FilterResult
from infrastructure.memory_feedback_repository import MemoryFeedbackRepository
from infrastructure.memory_filtered_store import MemoryFilteredResultStore
from infrastructure.file_handler import FileHandler
from feedback import Feedback

pytestmark = pytest.mark.TEST_F


def test_f_09_get_current_feedbacks_replaces_session_accessor():
    """TEST_F-09: getCurrentFeedbacks() replaces getOldDataFromSession()."""
    repo = MemoryFeedbackRepository()
    repo.add_text("A")
    analyzer = FeedbackAnalyzer(repo)
    assert [fb.text for fb in analyzer.getCurrentFeedbacks()] == ["A"]


def test_f_10_filter_returns_filter_result_not_global():
    """TEST_F-10: filter() returns FilterResult (not fil_data global)."""
    repo = MemoryFeedbackRepository()
    store = MemoryFilteredResultStore()
    repo.add_text("배송이 너무 늦어요. 화가 납니다.")
    analyzer = FeedbackAnalyzer(repo, store=store)
    result = analyzer.filter("부정", "배송")
    assert isinstance(result, FilterResult)
    assert len(result.feedbacks) == 1
    assert result.sentiment_results["부정"] == 1
    assert store.load() == result.feedbacks


def test_f_11_analyze_sentiment_and_keywords_naming():
    """TEST_F-11: analyzeSentiment / analyzeKeywords naming."""
    repo = MemoryFeedbackRepository()
    repo.add_text("배송이 빨라서 좋아요")
    analyzer = FeedbackAnalyzer(repo)
    fb_list = analyzer.getCurrentFeedbacks()
    assert analyzer.analyzeSentiment(fb_list[0].text) == "긍정"
    keywords = analyzer.analyzeKeywords(fb_list)
    assert keywords.get("배송", 0) >= 1


def test_f_12_persist_feedbacks_via_file_handler(tmp_path):
    """TEST_F-12: persistFeedbacksToCsv delegates to FileHandler."""
    repo = MemoryFeedbackRepository()
    repo.add_text("export me")
    path = tmp_path / "session.csv"
    analyzer = FeedbackAnalyzer(repo, file_handler=FileHandler())
    n = analyzer.persistFeedbacksToCsv(str(path))
    assert n == 1
    assert "export me" in path.read_text(encoding="utf-8-sig")
