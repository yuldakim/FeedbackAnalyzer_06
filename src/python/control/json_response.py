# -*- coding: utf-8 -*-
"""JSON API response builder (F-13, INV-JSON-001)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from entity.feedback_analyzer import FeedbackAnalyzer
from feedback import Feedback


def build_analysis_json(
    analyzer: FeedbackAnalyzer,
    *,
    success: Optional[str] = None,
    warning: Optional[str] = None,
    error: Optional[str] = None,
    feedbacks: Optional[List[Feedback]] = None,
) -> Dict[str, Any]:
    items = feedbacks if feedbacks is not None else analyzer.getCurrentFeedbacks()
    feedback_rows = []
    for fb in items:
        feedback_rows.append(
            {
                "text": fb.text,
                "sentiment": analyzer.analyzeSentiment(fb.text),
                "categories": analyzer.matchCategories(fb.text),
            }
        )
    message_type = "success"
    message_text = success or ""
    if error:
        message_type = "error"
        message_text = error
    elif warning:
        message_type = "warning"
        message_text = warning

    return {
        "feedbacks": feedback_rows,
        "sentiment_results": analyzer.aggregateSentiment(items),
        "keyword_results": analyzer.analyzeKeywords(items),
        "message": {"type": message_type, "text": message_text},
    }
