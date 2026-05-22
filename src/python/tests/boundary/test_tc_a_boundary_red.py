# -*- coding: utf-8 -*-
"""Track A — UI / Boundary RED (Flask test_client)."""

from __future__ import annotations

import io
import re

from tests.conftest import ANCHOR_TEXT


def test_tc_a_01_post_analyze_anchor_success_negative_delivery_original(client):
    """INV-COUNT-002: POST /analyze anchor returns success, negative count, delivery, original text."""
    # Given: empty session
    # When
    response = client.post("/analyze", data={"text": ANCHOR_TEXT})

    # Then — TO-BE (README 1분 데모)
    assert response.status_code == 200
    body = response.data.decode("utf-8")
    assert "alert-success" in body or "피드백이 입력되었습니다" in body
    assert "부정" in body
    assert "배송" in body
    negative_count = re.search(
        r'<div class="stat-number">(\d+)</div>\s*<div class="stat-label">부정</div>',
        body,
    )
    assert negative_count and negative_count.group(1) == "1"


def test_tc_a_02_post_analyze_whitespace_only_unchanged_count(client):
    """INV-INPUT-001: whitespace-only POST /analyze does not add feedback."""
    # Given
    client.post("/analyze", data={"text": ANCHOR_TEXT})

    # When
    response = client.post("/analyze", data={"text": "   \t\n  "})

    # Then
    body = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "1개의 피드백이 입력되었습니다" in body
    assert "2개의 피드백" not in body


def test_tc_a_03_post_filter_empty_session_warning(client):
    """INV-EMPTY-001: zero feedbacks → filter warning."""
    # Given: empty session
    # When
    response = client.post(
        "/filter", data={"sentiment": "전체", "keyword": "전체"}
    )

    # Then
    assert response.status_code == 200
    body = response.data.decode("utf-8")
    assert "alert-warning" in body
    assert "분석할 피드백이 없습니다" in body


def test_tc_a_04_filter_negative_delivery_download_csv_anchor(client):
    """INV-CSV-OUT-003: filter snapshot → download BOM, text header, anchor row."""
    # Given
    client.post("/analyze", data={"text": ANCHOR_TEXT})

    # When
    filter_resp = client.post(
        "/filter", data={"sentiment": "부정", "keyword": "배송"}
    )
    download_resp = client.get("/download")

    # Then — TO-BE: 1 filtered row, CSV matches anchor
    assert filter_resp.status_code == 200
    assert download_resp.status_code == 200
    assert (
        download_resp.headers.get("Content-Disposition", "")
        == "attachment; filename=filtered_feedback.csv"
    )
    raw = download_resp.data
    assert raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    lines = [ln for ln in text.splitlines() if ln]
    assert lines[0] == "text"
    assert lines[1] == ANCHOR_TEXT
    filter_body = filter_resp.data.decode("utf-8")
    assert ANCHOR_TEXT in filter_body


def test_tc_a_05_post_upload_broken_csv_error_session_unchanged(client):
    """INV-SESSION-001: broken CSV upload → error, session count unchanged."""
    # Given
    client.post("/analyze", data={"text": ANCHOR_TEXT})
    broken = io.BytesIO(b"\xff\xfe not-valid-utf8")

    # When
    response = client.post(
        "/upload",
        data={"file": (broken, "bad.csv")},
        content_type="multipart/form-data",
    )

    # Then
    assert response.status_code == 200
    body = response.data.decode("utf-8")
    from infrastructure import wiring

    assert "alert-danger" in body or "오류" in body

    assert len(wiring.feedback_repository.all()) == 1
    assert wiring.feedback_repository.all()[0].text == ANCHOR_TEXT


def test_tc_a_06_post_analyze_multiline_original_preserved_in_html(client):
    """INV-TEXT-001: multiline text preserved as single feedback in HTML."""
    multiline = "첫 줄 피드백\n둘째 줄도 같은 건입니다."

    # When
    response = client.post("/analyze", data={"text": multiline})

    # Then
    body = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "첫 줄 피드백" in body
    assert "둘째 줄도 같은 건입니다." in body
    assert "1개의 피드백이 입력되었습니다" in body


def test_tc_a_07_post_filter_unknown_sentiment_error_or_fallback(client):
    """PRD C-09: unsupported sentiment filter → error or documented fallback message."""
    # Given
    client.post("/analyze", data={"text": ANCHOR_TEXT})

    # When
    response = client.post(
        "/filter", data={"sentiment": "알수없음", "keyword": "전체"}
    )

    # Then — TO-BE: error (not silent empty-filter warning only)
    body = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "alert-danger" in body or "error" in body.lower()
    assert "알수없음" in body or "지원" in body or "유효" in body
