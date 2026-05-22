# -*- coding: utf-8 -*-
"""In-memory FeedbackRepositoryPort (replaces Session class variable)."""

from __future__ import annotations

from typing import List

from feedback import Feedback


class MemoryFeedbackRepository:
    def __init__(self) -> None:
        self._feedbacks: List[Feedback] = []

    def all(self) -> List[Feedback]:
        return self._feedbacks

    def add_text(self, text: str) -> None:
        stripped = text.strip()
        if stripped:
            self._feedbacks.append(Feedback(stripped))

    def clear(self) -> None:
        self._feedbacks.clear()

    def replace_all(self, feedbacks: List[Feedback]) -> None:
        self._feedbacks.clear()
        self._feedbacks.extend(feedbacks)
