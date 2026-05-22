# -*- coding: utf-8 -*-
"""Trend CSV visualization data (F-11, ST-09)."""

from __future__ import annotations

import pytest

from control.trend_analysis import TrendAnalysisUseCase
from infrastructure import wiring

pytestmark = pytest.mark.mission7


def test_trend_csv_loads_points():
    points = TrendAnalysisUseCase(wiring.trend_csv_path).execute()
    assert len(points) >= 3
    assert points[0].count > 0


def test_index_includes_trend_table(client):
    resp = client.get("/")
    html = resp.data.decode("utf-8")
    assert "피드백 트렌드" in html
    assert "2026-05" in html
