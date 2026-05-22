# -*- coding: utf-8 -*-
"""Read-only mirrors of legacy analyze vs filter sentiment labeling (test-only)."""

from __future__ import annotations

from typing import List

from constants import SENTIMENT_KEYWORDS
from feedback import Feedback
from filters import _label_sentiment, filter_feedbacks
from text_analyzer import TextAnalyzer


def _contains_any(text: str, keywords: List[str]) -> bool:
    return any(kw in text for kw in keywords)


def label_sentiment_analyze_path(text: str) -> str:
    if _contains_any(text, SENTIMENT_KEYWORDS["긍정"]):
        return "긍정"
    if _contains_any(text, SENTIMENT_KEYWORDS["부정"]):
        return "부정"
    return "중립"


def label_sentiment_filter_path(text: str) -> str:
    return _label_sentiment(text)


def analyze_sentiment_counts(feedbacks: List[Feedback]) -> dict[str, int]:
    return TextAnalyzer().sent(feedbacks)


def filter_all_sentiment_counts(feedbacks: List[Feedback]) -> dict[str, int]:
    filtered = filter_feedbacks(feedbacks, "전체", "전체")
    return TextAnalyzer().sent(filtered)
