# -*- coding: utf-8 -*-

from __future__ import annotations

from feedback import Feedback
from infrastructure import wiring

from tests.conftest import ANCHOR_TEXT
from tests.support.legacy_session import mirror_upload_csv


def test_tc_b_08_broken_csv_upload_error_session_unchanged():
    """INV-SESSION-001: invalid UTF-8 CSV → error, feedback list unchanged."""
    # Arrange
    wiring.feedback_repository.replace_all([Feedback(ANCHOR_TEXT)])
    before_texts = [fb.text for fb in wiring.feedback_repository.all()]

    # Act
    level, mutated = mirror_upload_csv(
        wiring.feedback_repository.all(), b"\xff\xfe invalid-bytes"
    )

    # Then — TO-BE
    assert level == "error"
    assert mutated is False
    assert [fb.text for fb in wiring.feedback_repository.all()] == before_texts


def test_tc_b_08_empty_csv_header_only_no_append_session_unchanged():
    """INV-SESSION-001: header-only CSV → no new rows (empty data)."""
    # Arrange
    wiring.feedback_repository.replace_all([Feedback(ANCHOR_TEXT)])
    before_len = len(wiring.feedback_repository.all())

    # Act
    level, mutated = mirror_upload_csv(
        wiring.feedback_repository.all(), b"text\n"
    )

    # Then
    assert level == "success"
    assert mutated is False
    assert len(wiring.feedback_repository.all()) == before_len
