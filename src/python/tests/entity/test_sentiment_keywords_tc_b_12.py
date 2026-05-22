# -*- coding: utf-8 -*-

from __future__ import annotations

from constants import SENTIMENT_KEYWORDS

from tests.support.contract import classify_sentiment_contract


def test_tc_b_12_sentiment_keyword_partial_substring_match():
    """INV-SENT-001: SENTIMENT_KEYWORDS partial substring matching."""
    # Arrange — keyword "만족" embedded in longer text
    text = "이번 제품 정말 만족스럽게 썼습니다."

    # Act
    label = classify_sentiment_contract(text)

    # Then — TO-BE
    assert any(kw in text for kw in SENTIMENT_KEYWORDS["긍정"])
    assert label == "긍정"
