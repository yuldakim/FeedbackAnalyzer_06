# -*- coding: utf-8 -*-
"""Application-scoped Port instances (composition root)."""

from __future__ import annotations

from infrastructure.memory_feedback_repository import MemoryFeedbackRepository
from infrastructure.memory_filtered_store import MemoryFilteredResultStore

feedback_repository = MemoryFeedbackRepository()
filtered_store = MemoryFilteredResultStore()


def reset_state() -> None:
    feedback_repository.clear()
    filtered_store.clear()
