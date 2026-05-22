# -*- coding: utf-8 -*-
"""In-memory fakes (test-only)."""

from __future__ import annotations

from typing import List

from feedback import Feedback


class InMemoryFeedbackRepository:
    def __init__(self) -> None:
        self._feedbacks: List[Feedback] = []

    def add_text(self, text: str) -> None:
        stripped = text.strip()
        if stripped:
            self._feedbacks.append(Feedback(stripped))

    def all(self) -> List[Feedback]:
        return list(self._feedbacks)

    def clear(self) -> None:
        self._feedbacks.clear()
