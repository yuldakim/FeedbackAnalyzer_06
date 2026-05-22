# -*- coding: utf-8 -*-
"""In-memory FilteredResultStorePort (replaces fil_data global)."""

from __future__ import annotations

from typing import List

from feedback import Feedback


class MemoryFilteredResultStore:
    def __init__(self) -> None:
        self._snapshot: List[Feedback] = []

    def save(self, snapshot: List[Feedback]) -> None:
        self._snapshot = list(snapshot)

    def load(self) -> List[Feedback]:
        return list(self._snapshot)

    def has_snapshot(self) -> bool:
        return bool(self._snapshot)

    def clear(self) -> None:
        self._snapshot.clear()
