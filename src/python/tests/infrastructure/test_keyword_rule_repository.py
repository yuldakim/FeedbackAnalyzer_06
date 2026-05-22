# -*- coding: utf-8 -*-
"""KeywordRuleRepository + File DB (F-08, ST-06)."""

from __future__ import annotations

from pathlib import Path

from infrastructure.keyword_rule_repository import FileKeywordRuleRepository


def test_keyword_rule_repository_loads_file_and_registers(tmp_path: Path):
    path = tmp_path / "rules.json"
    path.write_text(
        '{"categories":{"프로모션":{"main":["이벤트"]}}}',
        encoding="utf-8",
    )
    repo = FileKeywordRuleRepository(path)
    assert "프로모션" in repo.list_categories()
    repo.register_category_keywords("신규", ["키워드A"])
    assert "신규" in repo.list_categories()
    assert "키워드A" in repo.category_keywords()["신규"]["main"]
