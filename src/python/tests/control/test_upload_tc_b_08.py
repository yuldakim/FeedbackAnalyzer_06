# -*- coding: utf-8 -*-

from __future__ import annotations

from feedback import Feedback
from session import Session

from tests.conftest import ANCHOR_TEXT
from tests.support.legacy_session import mirror_upload_csv


def test_tc_b_08_broken_csv_upload_error_session_unchanged():
    """INV-SESSION-001: invalid UTF-8 CSV → error, feedback list unchanged."""
    # Arrange
    Session.current_feedbacks = [Feedback(ANCHOR_TEXT)]
    before_texts = [fb.text for fb in Session.get_current_feedbacks()]

    # Act
    level, mutated = mirror_upload_csv(
        Session.get_current_feedbacks(), b"\xff\xfe invalid-bytes"
    )

    # Then — TO-BE
    assert level == "error"
    assert mutated is False
    assert [fb.text for fb in Session.get_current_feedbacks()] == before_texts


def test_tc_b_08_empty_csv_header_only_no_append_session_unchanged():
    """INV-SESSION-001: header-only CSV → no new rows (empty data)."""
    # Arrange
    Session.current_feedbacks = [Feedback(ANCHOR_TEXT)]
    before_len = len(Session.get_current_feedbacks())

    # Act
    level, mutated = mirror_upload_csv(
        Session.get_current_feedbacks(), b"text\n"
    )

    # Then
    assert level == "success"
    assert mutated is False
    assert len(Session.get_current_feedbacks()) == before_len
