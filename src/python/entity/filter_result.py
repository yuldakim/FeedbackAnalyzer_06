# -*- coding: utf-8 -*-
"""FilterResult — replaces legacy global fil_data (return value)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from feedback import Feedback


@dataclass
class FilterResult:
    feedbacks: List[Feedback] = field(default_factory=list)
    sentiment_results: Dict[str, int] = field(
        default_factory=lambda: {"긍정": 0, "중립": 0, "부정": 0}
    )
    keyword_results: Dict[str, int] = field(default_factory=dict)
