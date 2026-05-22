# -*- coding: utf-8 -*-
"""
Approval / Golden Master — HTTP·CSV 계약 (stdout 금지).

기준: tests/golden/feedback_golden_master.txt (S1~S4), download_filtered_anchor.csv (S5)
승인: APPROVE_GOLDEN=1 pytest tests/boundary/test_golden_master.py -v
"""

from __future__ import annotations

from tests.conftest import ANCHOR_TEXT
from tests.golden.helpers import assert_golden_csv, assert_golden_text
from tests.golden.normalize import snapshot_from_html

_POSITIVE_TEXT = "배송이 빨라서 좋아요"


def test_golden_s1_analyze_anchor(client):
    """S1 / SCN-A: 앵커 부정·배송·원문 (X-09 RR-1, INV-COUNT-002)."""
    response = client.post("/analyze", data={"text": ANCHOR_TEXT})
    body = snapshot_from_html(
        "S1", response.data.decode("utf-8"), expected_count=1
    ).to_canonical_block()
    assert_golden_text(body, "S1", status_code=response.status_code)


def test_golden_s2_analyze_positive_delivery(client):
    """S2: 긍정·배송 집계."""
    response = client.post("/analyze", data={"text": _POSITIVE_TEXT})
    body = snapshot_from_html(
        "S2", response.data.decode("utf-8"), expected_count=1
    ).to_canonical_block()
    assert_golden_text(body, "[S2: positive delivery POST /analyze]", status_code=response.status_code)


def test_golden_s3_whitespace_only_unchanged(client):
    """S3 / INV-INPUT-001: 공백-only → 건수·원문 불변."""
    client.post("/analyze", data={"text": ANCHOR_TEXT})
    response = client.post("/analyze", data={"text": "   \t\n  "})
    body = snapshot_from_html(
        "S3", response.data.decode("utf-8"), expected_count=1
    ).to_canonical_block()
    assert_golden_text(body, "S3", status_code=response.status_code)


def test_golden_s4_filter_empty_session(client):
    """S4 / INV-EMPTY-001: 0건 filter → warning."""
    response = client.post(
        "/filter", data={"sentiment": "전체", "keyword": "전체"}
    )
    body = snapshot_from_html("S4", response.data.decode("utf-8")).to_canonical_block()
    assert_golden_text(body, "S4", status_code=response.status_code)


def test_golden_s5_filter_download_csv(client):
    """S5 / INV-CSV-OUT-001~003: BOM + text + 앵커 행."""
    client.post("/analyze", data={"text": ANCHOR_TEXT})
    client.post("/filter", data={"sentiment": "부정", "keyword": "배송"})
    response = client.get("/download")
    assert response.status_code == 200
    assert (
        response.headers.get("Content-Disposition", "")
        == "attachment; filename=filtered_feedback.csv"
    )
    assert_golden_csv(response.data)
