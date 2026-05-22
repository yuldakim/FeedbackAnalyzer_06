# -*- coding: utf-8 -*-
"""Multiline textarea UI (F-01 UX)."""

from __future__ import annotations


def test_index_has_multiline_textarea(client):
    html = client.get("/").data.decode("utf-8")
    assert 'textarea' in html
    assert 'rows="6"' in html
    assert "멀티라인" in html
