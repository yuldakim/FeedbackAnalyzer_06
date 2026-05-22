# -*- coding: utf-8 -*-
"""View models for control layer (TO-BE)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AnalysisViewModel:
    success: Optional[str] = None
    warning: Optional[str] = None
    error: Optional[str] = None
    sentiment_results: Dict[str, int] = field(
        default_factory=lambda: {"긍정": 0, "중립": 0, "부정": 0}
    )
    keyword_results: Dict[str, int] = field(default_factory=dict)
    feedback_texts: List[str] = field(default_factory=list)


@dataclass
class DownloadViewModel:
    body: str = ""
    warning: Optional[str] = None
    error: Optional[str] = None
