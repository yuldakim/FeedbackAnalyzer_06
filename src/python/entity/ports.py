# -*- coding: utf-8 -*-
"""Port interfaces — implemented in infrastructure/ (M2)."""

from __future__ import annotations

from typing import List, Protocol

from feedback import Feedback


class FeedbackRepositoryPort(Protocol):
    def all(self) -> List[Feedback]: ...

    def add_text(self, text: str) -> None: ...

    def clear(self) -> None: ...


class FilteredResultStorePort(Protocol):
    def save(self, snapshot: List[Feedback]) -> None: ...

    def load(self) -> List[Feedback]: ...

    def has_snapshot(self) -> bool: ...
