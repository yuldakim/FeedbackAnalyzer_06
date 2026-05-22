# -*- coding: utf-8 -*-
"""pytest path setup and shared fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def _purge_shadow_entity_modules() -> None:
    """tests/entity·tests/control 수집 시 최상위 entity/control 섀도잉 방지."""
    for key in list(sys.modules):
        if key in ("entity", "control") or key.startswith(("entity.", "control.")):
            mod = sys.modules[key]
            mod_file = getattr(mod, "__file__", "") or ""
            if mod_file and "tests" in mod_file.replace("\\", "/"):
                del sys.modules[key]


ANCHOR_TEXT = "배송이 너무 늦어요. 화가 납니다."


def pytest_configure(config) -> None:
    _purge_shadow_entity_modules()
    import importlib

    importlib.import_module("entity")
    importlib.import_module("control")


@pytest.fixture
def client():
    from app import app

    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_session_and_globals():
    import app as app_module
    from session import Session
    from text_analyzer import TextAnalyzer

    Session.current_feedbacks = []
    app_module.fil_data = []
    TextAnalyzer.global_sent = {}
    TextAnalyzer.global_kw = {}
    yield
    Session.current_feedbacks = []
    app_module.fil_data = []
    TextAnalyzer.global_sent = {}
    TextAnalyzer.global_kw = {}
