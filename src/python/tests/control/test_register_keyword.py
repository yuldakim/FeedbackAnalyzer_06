# -*- coding: utf-8 -*-
"""Dynamic keyword registration (ST-06, INV-RULE-002)."""

from __future__ import annotations

from entity.category_classifier import CategoryClassifier
from infrastructure.keyword_rule_repository import FileKeywordRuleRepository

from control.register_keyword import RegisterKeywordUseCase


def test_register_keyword_then_classify(tmp_path):
    repo = FileKeywordRuleRepository(tmp_path / "r.json")
    vm = RegisterKeywordUseCase(repo).execute(
        "프로모션", ["이벤트-프로모션"]
    )
    assert vm.success
    clf = CategoryClassifier(repo)
    cats = clf.match_categories("이번 이벤트-프로모션 정말 좋았어요")
    assert "프로모션" in cats
