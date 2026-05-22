# -*- coding: utf-8 -*-
"""RegisterKeywordUseCase — dynamic category keywords (ST-06, INV-RULE-002)."""

from __future__ import annotations

from typing import List

from entity.ports import KeywordRuleRepositoryPort
from control.dto import AnalysisViewModel


class RegisterKeywordUseCase:
    def __init__(self, rule_repo: KeywordRuleRepositoryPort) -> None:
        self._rule_repo = rule_repo

    def execute(self, category: str, keywords: List[str]) -> AnalysisViewModel:
        category = category.strip()
        if not category:
            return AnalysisViewModel(error="카테고리명이 필요합니다.")
        if not keywords:
            return AnalysisViewModel(error="키워드 목록이 비어 있습니다.")
        self._rule_repo.register_category_keywords(category, keywords)
        return AnalysisViewModel(
            success=f"카테고리 '{category}' 에 키워드 {len(keywords)}개가 등록되었습니다."
        )
