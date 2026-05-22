# -*- coding: utf-8 -*-
"""TrendAnalysisUseCase — read test_feedback_trend.csv (F-11, ST-09)."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class TrendPoint:
    date: str
    count: int
    positive: int
    negative: int
    neutral: int


class TrendAnalysisUseCase:
    def __init__(self, csv_path: Path) -> None:
        self._path = csv_path

    def execute(self) -> List[TrendPoint]:
        if not self._path.is_file():
            return []
        points: List[TrendPoint] = []
        with self._path.open(encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                points.append(
                    TrendPoint(
                        date=row["date"],
                        count=int(row["count"]),
                        positive=int(row["sentiment_positive"]),
                        negative=int(row["sentiment_negative"]),
                        neutral=int(row["sentiment_neutral"]),
                    )
                )
        return points
