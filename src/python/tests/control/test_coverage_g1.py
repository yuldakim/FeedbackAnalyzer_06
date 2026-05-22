# -*- coding: utf-8 -*-
"""PRD G-1: entity·control coverage — UploadCsv success, filter/download branches."""

from __future__ import annotations

import csv
from unittest.mock import patch

from control.download_filtered import DownloadFilteredUseCase
from control.filter_feedbacks import FilterFeedbacksUseCase
from control.upload_csv import UploadCsvUseCase
from tests.conftest import ANCHOR_TEXT
from tests.support.port_fakes import (
    InMemoryFeedbackRepositoryPort,
    InMemoryFilteredResultStorePort,
)

_VALID_CSV = (
    "text\n"
    "배송이 빨라서 좋아요\n"
    "오늘은 특별한 일이 없었습니다.\n"
).encode("utf-8-sig")


def test_upload_csv_use_case_valid_utf8_csv_appends_rows():
    """PRD F-01 / ST-01: UTF-8 BOM CSV with text header appends feedback rows."""
    repo = InMemoryFeedbackRepositoryPort()
    uc = UploadCsvUseCase(repo)

    vm = uc.execute(_VALID_CSV)

    assert vm.error is None
    assert vm.success is not None
    assert "2개의 피드백" in vm.success
    texts = [fb.text for fb in repo.all()]
    assert "배송이 빨라서 좋아요" in texts
    assert "오늘은 특별한 일이 없었습니다." in texts


def test_upload_csv_use_case_utf16_bom_rejected():
    """B-UPL-02: UTF-16 BOM prefix → error; repository unchanged (INV-SESSION-001)."""
    repo = InMemoryFeedbackRepositoryPort()
    repo.add_text(ANCHOR_TEXT)
    before = [fb.text for fb in repo.all()]
    uc = UploadCsvUseCase(repo)

    vm = uc.execute(b"\xff\xfe\xdd\xdd")

    assert vm.error is not None
    assert [fb.text for fb in repo.all()] == before


def test_upload_csv_use_case_invalid_utf8_decode_error():
    """B-UPL-03: invalid UTF-8 byte sequence → UnicodeDecodeError path."""
    repo = InMemoryFeedbackRepositoryPort()
    repo.add_text(ANCHOR_TEXT)
    before = [fb.text for fb in repo.all()]
    uc = UploadCsvUseCase(repo)

    vm = uc.execute(b"\x80\x81\x82")

    assert vm.error is not None
    assert [fb.text for fb in repo.all()] == before


def test_upload_csv_use_case_csv_reader_error():
    """B-UPL-05: csv.reader raises csv.Error → error; INV-SESSION-001."""
    repo = InMemoryFeedbackRepositoryPort()
    repo.add_text(ANCHOR_TEXT)
    before = [fb.text for fb in repo.all()]
    uc = UploadCsvUseCase(repo)
    valid_body = b"text\nok\n"

    with patch(
        "control.upload_csv.csv.reader",
        side_effect=csv.Error("malformed csv"),
    ):
        vm = uc.execute(valid_body)

    assert vm.error is not None
    assert [fb.text for fb in repo.all()] == before


def test_filter_use_case_empty_repository_warning():
    """INV-EMPTY-001: no feedbacks → warning before filter runs."""
    repo = InMemoryFeedbackRepositoryPort()
    store = InMemoryFilteredResultStorePort()
    uc = FilterFeedbacksUseCase(repo, store)

    vm = uc.execute("전체", "전체")

    assert vm.warning == "분석할 피드백이 없습니다."
    assert not store.has_snapshot()


def test_filter_use_case_no_matching_results_warning():
    """Filter yields zero rows → warning; snapshot not saved."""
    repo = InMemoryFeedbackRepositoryPort()
    store = InMemoryFilteredResultStorePort()
    repo.add_text(ANCHOR_TEXT)
    uc = FilterFeedbacksUseCase(repo, store)

    vm = uc.execute("긍정", "전체")

    assert vm.warning == "필터링 결과가 없습니다."
    assert not store.has_snapshot()


def test_download_use_case_no_snapshot_warning():
    """INV-EMPTY-001: download without prior filter snapshot → warning."""
    store = InMemoryFilteredResultStorePort()
    uc = DownloadFilteredUseCase(store)

    vm = uc.execute()

    assert vm.warning == "다운로드할 결과가 없습니다."
    assert vm.body == ""
