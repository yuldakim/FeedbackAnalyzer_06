# -*- coding: utf-8 -*-
"""
TO-BE control layer RED (tests/tobe — no package name clash with domain entity).

기존 tests/control/test_*.py (레거시) 는 수정하지 않음.
"""

from __future__ import annotations

import pytest

from control.analyze_feedback import AnalyzeFeedbackUseCase
from control.download_filtered import DownloadFilteredUseCase
from control.filter_feedbacks import FilterFeedbacksUseCase
from control.upload_csv import UploadCsvUseCase
from entity.sentiment_classifier import SentimentClassifier
from tests.conftest import ANCHOR_TEXT
from tests.support.contract import classify_sentiment_contract
from tests.support.legacy_labels import (
    label_sentiment_analyze_path,
    label_sentiment_filter_path,
)
from tests.support.port_fakes import (
    InMemoryFeedbackRepositoryPort,
    InMemoryFilteredResultStorePort,
)

_DIVERGENT_TEXT = "택배가 빠르게 왔어요. 친절했습니다."


def test_tobe_tc_b_04_inv_sent_002_single_classifier_labels():
    """INV-SENT-002: TO-BE SentimentClassifier used for both analyze and filter paths."""
    # Arrange
    classifier = SentimentClassifier()
    texts = [ANCHOR_TEXT, _DIVERGENT_TEXT]

    # Act
    analyze_labels = [classifier.classify(t) for t in texts]
    filter_labels = [classifier.classify(t) for t in texts]

    # Assert — 동일 인스턴스·규칙이면 라벨 일치
    assert analyze_labels == filter_labels
    assert analyze_labels[1] == label_sentiment_analyze_path(_DIVERGENT_TEXT)


def test_tobe_tc_b_04b_tobe_label_matches_contract():
    """INV-SENT-002: TO-BE classifier aligns with contract keywords."""
    # Arrange
    classifier = SentimentClassifier()
    text = _DIVERGENT_TEXT
    expected = classify_sentiment_contract(text)

    # Act
    tobe_label = classifier.classify(text)

    # Assert
    assert tobe_label == expected


def test_tobe_tc_b_06_analyze_use_case_mixed_sentiment_counts():
    """INV-COUNT-002: AnalyzeFeedbackUseCase aggregate sum equals feedback count."""
    # Arrange
    repo = InMemoryFeedbackRepositoryPort()
    uc = AnalyzeFeedbackUseCase(repo)
    for text in (
        ANCHOR_TEXT,
        "배송이 빨라서 좋아요",
        "오늘은 특별한 일이 없었습니다.",
    ):
        uc.execute(text)

    # Act
    vm = uc.execute("")

    # Assert
    s = vm.sentiment_results
    assert sum(s.values()) == 3
    assert s == {"긍정": 1, "중립": 1, "부정": 1}


def test_tobe_tc_b_07_analyze_use_case_whitespace_only_no_append():
    """INV-INPUT-001: whitespace-only does not increase repository size."""
    # Arrange
    repo = InMemoryFeedbackRepositoryPort()
    uc = AnalyzeFeedbackUseCase(repo)
    uc.execute(ANCHOR_TEXT)

    # Act
    uc.execute("   \t\n  ")

    # Assert
    assert len(repo.all()) == 1


def test_tobe_tc_b_08_upload_use_case_broken_csv_error():
    """INV-SESSION-001: broken CSV must error and not mutate repository."""
    # Arrange
    repo = InMemoryFeedbackRepositoryPort()
    repo.add_text(ANCHOR_TEXT)
    before = [fb.text for fb in repo.all()]
    uc = UploadCsvUseCase(repo)

    # Act
    vm = uc.execute(b"\xff\xfe invalid")

    # Assert
    assert vm.error is not None
    assert [fb.text for fb in repo.all()] == before


def test_tobe_tc_b_09_download_use_case_snapshot_csv_body():
    """INV-CSV-OUT-003: download body rows match filter snapshot order."""
    # Arrange
    repo = InMemoryFeedbackRepositoryPort()
    store = InMemoryFilteredResultStorePort()
    repo.add_text(ANCHOR_TEXT)
    repo.add_text("배송이 빨라서 좋아요")
    filter_uc = FilterFeedbacksUseCase(repo, store)
    filter_uc.execute("전체", "전체")
    download_uc = DownloadFilteredUseCase(store)

    # Act
    vm = download_uc.execute()

    # Assert
    text = vm.body.lstrip("\ufeff")
    lines = text.splitlines()
    assert lines[0] == "text"
    assert lines[1:] == [fb.text for fb in store.load()]
    assert len(lines[1:]) == 2


def test_tobe_filter_use_case_unknown_sentiment_c09():
    """PRD C-09: unsupported sentiment → error on FilterFeedbacksUseCase."""
    # Arrange
    repo = InMemoryFeedbackRepositoryPort()
    repo.add_text(ANCHOR_TEXT)
    store = InMemoryFilteredResultStorePort()
    uc = FilterFeedbacksUseCase(repo, store)

    # Act
    vm = uc.execute("알수없음", "전체")

    # Assert
    assert vm.error is not None
