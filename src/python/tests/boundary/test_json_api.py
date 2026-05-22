# -*- coding: utf-8 -*-
"""JSON API (F-13, INV-JSON-001)."""

from __future__ import annotations

from tests.conftest import ANCHOR_TEXT


def test_api_analyze_returns_json_contract(client):
    resp = client.post(
        "/api/analyze",
        json={"text": ANCHOR_TEXT},
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "feedbacks" in data
    assert "sentiment_results" in data
    assert "keyword_results" in data
    assert data["message"]["type"] in ("success", "warning", "error")
    assert data["sentiment_results"]["부정"] >= 1


def test_api_session_get(client):
    client.post("/api/analyze", json={"text": ANCHOR_TEXT})
    resp = client.get("/api/session")
    assert resp.status_code == 200
    body = resp.get_json()
    assert len(body["feedbacks"]) >= 1
