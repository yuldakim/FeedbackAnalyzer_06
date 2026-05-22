# -*- coding: utf-8 -*-
"""Port interfaces — implemented in infrastructure/ (M2+)."""

from __future__ import annotations

from typing import Dict, List, Protocol

from feedback import Feedback


class FeedbackRepositoryPort(Protocol):
    def all(self) -> List[Feedback]: ...

    def add_text(self, text: str) -> None: ...

    def clear(self) -> None: ...


class FilteredResultStorePort(Protocol):
    def save(self, snapshot: List[Feedback]) -> None: ...

    def load(self) -> List[Feedback]: ...

    def has_snapshot(self) -> bool: ...


class KeywordRuleRepositoryPort(Protocol):
    """F-08 — category + sentiment keyword rules (File DB / dynamic register)."""

    def category_keywords(self) -> Dict[str, dict]: ...

    def sentiment_keywords(self) -> Dict[str, List[str]]: ...

    def sentiment_weights(self) -> Dict[str, Dict[str, float]]: ...

    def register_category_keywords(
        self, category: str, keywords: List[str]
    ) -> None: ...

    def list_categories(self) -> List[str]: ...

    def reset(self) -> None: ...
