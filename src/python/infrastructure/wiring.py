# -*- coding: utf-8 -*-
"""Application-scoped Port instances (composition root)."""

from __future__ import annotations

from pathlib import Path

from infrastructure.file_handler import FileHandler
from infrastructure.keyword_rule_repository import FileKeywordRuleRepository
from infrastructure.memory_feedback_repository import MemoryFeedbackRepository
from infrastructure.memory_filtered_store import MemoryFilteredResultStore
from infrastructure.page_log_sink import PageLogSink

_data_dir = Path(__file__).resolve().parent.parent / "data"

feedback_repository = MemoryFeedbackRepository()
filtered_store = MemoryFilteredResultStore()
file_handler = FileHandler()
export_dir = _data_dir / "exports"
keyword_rule_repository = FileKeywordRuleRepository(_data_dir / "feedback_rules.json")
page_log_sink = PageLogSink()
trend_csv_path = _data_dir / "test_feedback_trend.csv"


def reset_state() -> None:
    feedback_repository.clear()
    filtered_store.clear()
    keyword_rule_repository.reset()
    page_log_sink.reset()
