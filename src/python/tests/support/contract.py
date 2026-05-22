# -*- coding: utf-8 -*-
"""TO-BE contract helpers (test-only). PRD/README + constants.SENTIMENT_KEYWORDS."""

from __future__ import annotations

from typing import Dict, List

from constants import CATEGORY_KEYWORDS, SENTIMENT_KEYWORDS
from feedback import Feedback


def _contains_any(text: str, keywords: List[str]) -> bool:
    return any(kw in text for kw in keywords)


def classify_sentiment_contract(text: str) -> str:
    """긍정 → 부정 → 중립 (INV-SENT-001)."""
    if _contains_any(text, SENTIMENT_KEYWORDS["긍정"]):
        return "긍정"
    if _contains_any(text, SENTIMENT_KEYWORDS["부정"]):
        return "부정"
    return "중립"


def count_sentiments_contract(feedbacks: List[Feedback]) -> Dict[str, int]:
    res = {"긍정": 0, "중립": 0, "부정": 0}
    for fb in feedbacks:
        res[classify_sentiment_contract(fb.text)] += 1
    return res


def count_categories_contract(feedbacks: List[Feedback]) -> Dict[str, int]:
    res = {cat: 0 for cat in CATEGORY_KEYWORDS}
    for fb in feedbacks:
        txt = fb.text
        for cat, sub_map in CATEGORY_KEYWORDS.items():
            if "main" in sub_map and _contains_any(txt, sub_map["main"]):
                res[cat] += 1
    return res


def assert_inv_count_002(sentiment_counts: Dict[str, int], feedback_count: int) -> None:
    assert sum(sentiment_counts.values()) == feedback_count
