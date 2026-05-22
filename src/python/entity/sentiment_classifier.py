# -*- coding: utf-8 -*-
"""SentimentClassifier — 단일 감정 분류 허브 (INV-SENT-001, INV-SENT-002)."""

from __future__ import annotations

from typing import Dict, List

from constants import SENTIMENT_KEYWORDS
from feedback import Feedback


class SentimentClassifier:
    """긍정 → 부정 → 중립 (INV-SENT-001). Analyze·Filter 동일 규칙 (INV-SENT-002)."""

    @staticmethod
    def _contains_any(text: str, keywords: List[str]) -> bool:
        return any(kw in text for kw in keywords)

    def classify(self, text: str) -> str:
        if self._contains_any(text, SENTIMENT_KEYWORDS["긍정"]):
            return "긍정"
        if self._contains_any(text, SENTIMENT_KEYWORDS["부정"]):
            return "부정"
        return "중립"

    def aggregate(self, feedbacks: List[Feedback]) -> Dict[str, int]:
        res: Dict[str, int] = {"긍정": 0, "중립": 0, "부정": 0}
        for fb in feedbacks:
            res[self.classify(fb.text)] += 1
        return res
