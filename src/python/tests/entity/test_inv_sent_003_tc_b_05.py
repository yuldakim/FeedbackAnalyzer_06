# -*- coding: utf-8 -*-

from __future__ import annotations

from feedback import Feedback
from filters import filter_feedbacks

from tests.support.contract import classify_sentiment_contract

_POSITIVE_TEXT = "배송이 빨라서 좋아요"
_NEUTRAL_TEXT = "오늘은 특별한 일이 없었습니다."
ANCHOR_TEXT = "배송이 너무 늦어요. 화가 납니다."


def test_tc_b_05_neutral_filter_returns_only_contract_neutral_items():
    """INV-SENT-003: Filter(중립, 전체) must return only contract-neutral feedbacks."""
    # Arrange
    feedbacks = [
        Feedback(_NEUTRAL_TEXT),
        Feedback(_POSITIVE_TEXT),
        Feedback(ANCHOR_TEXT),
    ]

    # Act
    filtered = filter_feedbacks(feedbacks, "중립", "전체")

    # Assert — TO-BE: 중립 = 긍·부 키워드 미매칭만
    for fb in filtered:
        assert classify_sentiment_contract(fb.text) == "중립", fb.text

    contract_neutral = [fb for fb in feedbacks if classify_sentiment_contract(fb.text) == "중립"]
    assert {fb.text for fb in filtered} == {fb.text for fb in contract_neutral}

    assert not any(fb.text == _POSITIVE_TEXT for fb in filtered)
    # README/PRD 앵커: 부정 → 중립 필터에 포함되면 INV-SENT-003 위반
    assert not any(fb.text == ANCHOR_TEXT for fb in filtered)
