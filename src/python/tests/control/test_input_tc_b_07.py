# -*- coding: utf-8 -*-

from __future__ import annotations

from tests.conftest import ANCHOR_TEXT
from tests.support.fakes import InMemoryFeedbackRepository
from tests.support.legacy_session import mirror_analyze_append


def test_tc_b_07_empty_and_whitespace_only_do_not_append_to_repository():
    """INV-INPUT-001: trim 후 공백-only → no Feedback append (F-01 policy)."""
    # Arrange
    repo = InMemoryFeedbackRepository()
    mirror_analyze_append(repo._feedbacks, ANCHOR_TEXT)
    count_before = len(repo.all())

    # Act — TO-BE analyze append policy
    for candidate in ("", "   \t\n  "):
        mirror_analyze_append(repo._feedbacks, candidate)

    # Then
    assert len(repo.all()) == count_before == 1
    assert repo.all()[0].text == ANCHOR_TEXT
