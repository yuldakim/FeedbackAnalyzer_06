# -*- coding: utf-8 -*-
"""PageLogSink level display (F-14)."""

from __future__ import annotations

from infrastructure import wiring


def test_page_log_sink_hides_warning_on_page(client):
    wiring.page_log_sink.set_levels(warning=False, error=True)
    resp = client.post("/filter", data={"sentiment": "전체", "keyword": "전체"})
    html = resp.data.decode("utf-8")
    assert 'class="alert alert-warning"' not in html
    assert "분석할 피드백이 없습니다" not in html
