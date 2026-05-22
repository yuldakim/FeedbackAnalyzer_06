# -*- coding: utf-8 -*-

from __future__ import annotations

from feedback import Feedback

from tests.support.fakes import InMemoryFeedbackRepository
from tests.support.legacy_labels import (
    analyze_sentiment_counts,
    filter_all_sentiment_counts,
    label_sentiment_analyze_path,
    label_sentiment_filter_path,
)

ANCHOR_TEXT = "배송이 너무 늦어요. 화가 납니다."
# Analyze(SENTIMENT_KEYWORDS) vs Filter(S_KEYWORDS) 라벨이 갈라지는 문장
_DIVERGENT_TEXT = "택배가 빠르게 왔어요. 친절했습니다."
_NEUTRAL_TEXT = "오늘은 특별한 일이 없었습니다."


def test_tc_b_04_analyze_aggregate_equals_filter_whole_recount():
    """INV-SENT-002: Analyze sentiment counts equal Filter(전체, 전체) recount."""
    # Arrange
    repo = InMemoryFeedbackRepository()
    repo.add_text(ANCHOR_TEXT)
    repo.add_text(_DIVERGENT_TEXT)
    repo.add_text(_NEUTRAL_TEXT)
    feedbacks = repo.all()

    # Act
    analyze_counts = analyze_sentiment_counts(feedbacks)
    filter_counts = filter_all_sentiment_counts(feedbacks)

    # Assert — 동일 규칙이면 집계 일치 (불일치를 정답으로 두지 않음)
    assert analyze_counts == filter_counts


def test_tc_b_04_per_item_sentiment_label_analyze_matches_filter():
    """INV-SENT-002: each feedback gets the same sentiment label on Analyze and Filter paths."""
    # Arrange
    texts = [ANCHOR_TEXT, _DIVERGENT_TEXT, _NEUTRAL_TEXT]

    # Act & Assert
    for text in texts:
        analyze_label = label_sentiment_analyze_path(text)
        filter_label = label_sentiment_filter_path(text)
        assert analyze_label == filter_label, (
            f"sentiment label mismatch for {text!r}: "
            f"analyze={analyze_label}, filter={filter_label}"
        )
