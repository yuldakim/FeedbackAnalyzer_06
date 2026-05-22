# -*- coding: utf-8 -*-
"""CategoryClassifier — main+sub 키워드 정책 (PRD §5.1, F-03)."""

from __future__ import annotations

from typing import Dict, List

from constants import CATEGORY_KEYWORDS
from feedback import Feedback


class CategoryClassifier:
    @staticmethod
    def _contains_any(text: str, keywords: List[str]) -> bool:
        return any(kw in text for kw in keywords)

    def match_categories(self, text: str) -> List[str]:
        matched: List[str] = []
        for cat, sub_map in CATEGORY_KEYWORDS.items():
            main_keywords = sub_map.get("main", [])
            if self._contains_any(text, main_keywords):
                matched.append(cat)
                continue
            for bucket, sub_keywords in sub_map.items():
                if bucket == "main":
                    continue
                if self._contains_any(text, sub_keywords):
                    matched.append(cat)
                    break
        return matched

    def aggregate(self, feedbacks: List[Feedback]) -> Dict[str, int]:
        res = {cat: 0 for cat in CATEGORY_KEYWORDS}
        for fb in feedbacks:
            for cat in self.match_categories(fb.text):
                res[cat] += 1
        return res
