# -*- coding: utf-8 -*-
"""Application-scoped Port instances (composition root)."""

from __future__ import annotations

from infrastructure.memory_feedback_repository import MemoryFeedbackRepository

feedback_repository = MemoryFeedbackRepository()


def reset_state() -> None:
    feedback_repository.clear()
