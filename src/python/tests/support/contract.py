# -*- coding: utf-8 -*-
"""TO-BE contract helpers (test-only). Weighted sentiment aligned with SentimentClassifier."""

from __future__ import annotations

from typing import Dict, List

from constants import CATEGORY_KEYWORDS
from entity.sentiment_classifier import SentimentClassifier
from feedback import Feedback

_classifier = SentimentClassifier()


def classify_sentiment_contract(text: str) -> str:
    """Weighted sentiment — same rules as SentimentClassifier (INV-SENT-001~003)."""
    return _classifier.classify(text)


def count_sentiments_contract(feedbacks: List[Feedback]) -> Dict[str, int]:
    return _classifier.aggregate(feedbacks)


def count_categories_contract(feedbacks: List[Feedback]) -> Dict[str, int]:
    from constants import CATEGORY_KEYWORDS as CK

    res = {cat: 0 for cat in CK}
    for fb in feedbacks:
        txt = fb.text
        for cat, sub_map in CK.items():
            main_keywords = sub_map.get("main", [])
            if any(kw in txt for kw in main_keywords):
                res[cat] += 1
                continue
            for bucket, sub_keywords in sub_map.items():
                if bucket == "main":
                    continue
                if any(kw in txt for kw in sub_keywords):
                    res[cat] += 1
                    break
    return res


def assert_inv_count_002(sentiment_counts: Dict[str, int], feedback_count: int) -> None:
    assert sum(sentiment_counts.values()) == feedback_count
