# -*- coding: utf-8 -*-
"""In-memory Port implementations for TO-BE control RED tests."""

from __future__ import annotations

from typing import List

from feedback import Feedback


class InMemoryFeedbackRepositoryPort:
    def __init__(self) -> None:
        self._feedbacks: List[Feedback] = []

    def all(self) -> List[Feedback]:
        return list(self._feedbacks)

    def add_text(self, text: str) -> None:
        stripped = text.strip()
        if stripped:
            self._feedbacks.append(Feedback(stripped))

    def clear(self) -> None:
        self._feedbacks.clear()


class InMemoryFilteredResultStorePort:
    def __init__(self) -> None:
        self._snapshot: List[Feedback] = []

    def save(self, snapshot: List[Feedback]) -> None:
        self._snapshot = list(snapshot)

    def load(self) -> List[Feedback]:
        return list(self._snapshot)

    def has_snapshot(self) -> bool:
        return bool(self._snapshot)
