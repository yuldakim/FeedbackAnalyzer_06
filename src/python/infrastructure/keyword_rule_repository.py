# -*- coding: utf-8 -*-
"""File-backed KeywordRuleRepository (F-08, ST-06) with constants fallback."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Dict, List

from constants import (
    CATEGORY_KEYWORDS,
    SENTIMENT_KEYWORDS,
    SENTIMENT_KEYWORD_WEIGHTS,
)


class FileKeywordRuleRepository:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._category: Dict[str, dict] = copy.deepcopy(CATEGORY_KEYWORDS)
        self._sentiment: Dict[str, List[str]] = {
            k: list(v) for k, v in SENTIMENT_KEYWORDS.items()
        }
        self._weights: Dict[str, Dict[str, float]] = copy.deepcopy(
            SENTIMENT_KEYWORD_WEIGHTS
        )
        self._extra_categories: Dict[str, List[str]] = {}
        self._load_file()

    def _load_file(self) -> None:
        if not self._path.is_file():
            return
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        if "categories" in raw:
            self._category = raw["categories"]
        if "sentiment" in raw:
            self._sentiment = {
                k: list(v) for k, v in raw["sentiment"].items()
            }
        if "sentiment_weights" in raw:
            self._weights = raw["sentiment_weights"]

    def _persist(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "sentiment": self._sentiment,
            "sentiment_weights": self._weights,
            "categories": self._category,
        }
        self._path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def category_keywords(self) -> Dict[str, dict]:
        merged = copy.deepcopy(self._category)
        for cat, kws in self._extra_categories.items():
            if cat not in merged:
                merged[cat] = {"main": list(kws)}
            else:
                main = merged[cat].setdefault("main", [])
                for kw in kws:
                    if kw not in main:
                        main.append(kw)
        return merged

    def sentiment_keywords(self) -> Dict[str, List[str]]:
        return {k: list(v) for k, v in self._sentiment.items()}

    def sentiment_weights(self) -> Dict[str, Dict[str, float]]:
        return copy.deepcopy(self._weights)

    def register_category_keywords(
        self, category: str, keywords: List[str]
    ) -> None:
        cleaned = [k.strip() for k in keywords if k.strip()]
        if not cleaned:
            return
        self._extra_categories[category] = cleaned
        if category not in self._category:
            self._category[category] = {"main": list(cleaned)}
        self._persist()

    def list_categories(self) -> List[str]:
        keys = set(self._category) | set(self._extra_categories)
        return sorted(keys)

    def reset(self) -> None:
        self._category = copy.deepcopy(CATEGORY_KEYWORDS)
        self._sentiment = {k: list(v) for k, v in SENTIMENT_KEYWORDS.items()}
        self._weights = copy.deepcopy(SENTIMENT_KEYWORD_WEIGHTS)
        self._extra_categories.clear()
