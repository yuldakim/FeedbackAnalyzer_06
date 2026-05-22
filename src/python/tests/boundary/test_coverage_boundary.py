# -*- coding: utf-8 -*-
"""PRD / Boundary: app.py route coverage (index, upload success, filter branches)."""

from __future__ import annotations

import io
from unittest.mock import patch

from tests.conftest import ANCHOR_TEXT


def test_get_index_renders_start_message(client):
    """GET / — dashboard start message (SCN-A entry)."""
    response = client.get("/")

    assert response.status_code == 200
    body = response.data.decode("utf-8")
    assert "피드백 분석기 시작" in body


def test_post_upload_valid_csv_success(client):
    """ST-01: valid UTF-8 CSV upload appends rows and shows success."""
    csv_bytes = (
        "text\n"
        "배송이 빨라서 좋아요\n"
        "품질이 별로예요\n"
    ).encode("utf-8-sig")
    data = {
        "file": (io.BytesIO(csv_bytes), "feedbacks.csv"),
    }

    response = client.post("/upload", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    body = response.data.decode("utf-8")
    assert "alert-success" in body or "피드백이 입력되었습니다" in body
    assert "2개의 피드백" in body


def test_post_filter_no_matching_results_warning(client):
    """Filter with no matching sentiment → warning banner."""
    client.post("/analyze", data={"text": ANCHOR_TEXT})

    response = client.post(
        "/filter", data={"sentiment": "긍정", "keyword": "전체"}
    )

    body = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "alert-warning" in body
    assert "필터링 결과가 없습니다" in body


def test_get_download_without_filter_returns_csv_header_only(client):
    """GET /download with empty fil_data still returns BOM + text header."""
    response = client.get("/download")

    assert response.status_code == 200
    assert response.data.startswith(b"\xef\xbb\xbf")
    text = response.data.decode("utf-8-sig")
    assert text.splitlines()[0] == "text"


def test_post_analyze_exception_returns_error_page(client):
    """Boundary maps unexpected errors to user-facing error message."""
    with patch(
        "app.Session.get_current_feedbacks",
        side_effect=RuntimeError("test failure"),
    ):
        response = client.post("/analyze", data={"text": "테스트"})

    body = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "alert-danger" in body
    assert "처리 중 오류" in body


def test_post_filter_exception_returns_error_page(client):
    """Filter route exception → error page (no uncaught 500)."""
    client.post("/analyze", data={"text": ANCHOR_TEXT})
    with patch(
        "app.filter_feedbacks",
        side_effect=RuntimeError("filter failure"),
    ):
        response = client.post(
            "/filter", data={"sentiment": "전체", "keyword": "전체"}
        )

    body = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "alert-danger" in body
    assert "처리 중 오류" in body
