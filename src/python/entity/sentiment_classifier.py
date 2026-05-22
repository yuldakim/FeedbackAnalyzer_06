# -*- coding: utf-8 -*-
"""SentimentClassifier — weighted keyword scoring (INV-SENT-001~003, INV-SENT-002)."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from constants import (
    MIXED_SENTIMENT_TIE_BREAKER,
    SENTIMENT_KEYWORDS,
    SENTIMENT_KEYWORD_WEIGHTS,
)
from entity.ports import KeywordRuleRepositoryPort
from feedback import Feedback


class SentimentClassifier:
    """가중치 감성 분석 — File DB(KeywordRuleRepository) 또는 constants."""

    def __init__(self, rule_repo: Optional[KeywordRuleRepositoryPort] = None) -> None:
        if rule_repo is not None:
            self._keywords = rule_repo.sentiment_keywords()
            self._weights = rule_repo.sentiment_weights()
        else:
            self._keywords = SENTIMENT_KEYWORDS
            self._weights = SENTIMENT_KEYWORD_WEIGHTS

    @staticmethod
    def _keyword_hits(text: str, keywords: List[str]) -> List[str]:
        return [kw for kw in keywords if kw in text]

    def scoreSentiment(self, text: str) -> Dict[str, float]:
        pos_hits = self._keyword_hits(text, self._keywords["긍정"])
        neg_hits = self._keyword_hits(text, self._keywords["부정"])
        pos_w = self._weights.get("긍정", {})
        neg_w = self._weights.get("부정", {})
        return {
            "긍정": sum(pos_w.get(kw, 1.0) for kw in pos_hits),
            "부정": sum(neg_w.get(kw, 1.0) for kw in neg_hits),
        }

    def analyzeSentiment(self, text: str) -> str:
        return self.classify(text)

    def classify(self, text: str) -> str:
        pos_score, neg_score = self._polarity_totals(text)
        if pos_score > neg_score:
            return "긍정"
        if neg_score > pos_score:
            return "부정"
        if pos_score == 0.0 and neg_score == 0.0:
            return "중립"
        return MIXED_SENTIMENT_TIE_BREAKER

    def _polarity_totals(self, text: str) -> Tuple[float, float]:
        scores = self.scoreSentiment(text)
        return scores["긍정"], scores["부정"]

    def aggregate(self, feedbacks: List[Feedback]) -> Dict[str, int]:
        res: Dict[str, int] = {"긍정": 0, "중립": 0, "부정": 0}
        for fb in feedbacks:
            res[self.classify(fb.text)] += 1
        return res
