# -*- coding: utf-8 -*-
"""FileHandler — CSV persistence (replaces legacy Lava Flow stub)."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List

from feedback import Feedback


class FileHandler:
    """Save feedback texts and optional analysis summary to UTF-8 BOM CSV."""

    def saveFeedbacksCsv(self, path: str | Path, feedbacks: List[Feedback]) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["text"])
            for fb in feedbacks:
                writer.writerow([fb.text])

    def saveAnalysisCsv(
        self,
        path: str | Path,
        feedbacks: List[Feedback],
        sentiment_results: Dict[str, int],
        keyword_results: Dict[str, int],
    ) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["text", "sentiment_label"])
            from entity.sentiment_classifier import SentimentClassifier

            clf = SentimentClassifier()
            for fb in feedbacks:
                writer.writerow([fb.text, clf.analyzeSentiment(fb.text)])
            writer.writerow([])
            writer.writerow(["# sentiment_aggregate"])
            for key in ("긍정", "중립", "부정"):
                writer.writerow([key, sentiment_results.get(key, 0)])
            writer.writerow([])
            writer.writerow(["# keyword_aggregate"])
            for cat, count in keyword_results.items():
                writer.writerow([cat, count])
