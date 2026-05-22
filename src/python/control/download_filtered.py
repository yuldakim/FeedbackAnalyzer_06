# -*- coding: utf-8 -*-
"""DownloadFilteredUseCase — STUB / RED phase."""

from __future__ import annotations

from entity.ports import FilteredResultStorePort
from control.dto import DownloadViewModel


class DownloadFilteredUseCase:
    def __init__(self, store: FilteredResultStorePort) -> None:
        self._store = store

    def execute(self) -> DownloadViewModel:
        # STUB: 스냅샷 없어도 헤더만 반환 (INV-EMPTY-001 / INV-CSV-OUT-003 미구현)
        if not self._store.has_snapshot():
            return DownloadViewModel(warning="다운로드할 결과가 없습니다.")
        snapshot = self._store.load()
        lines = ["\ufeff", "text\n"] + [fb.text + "\n" for fb in snapshot]
        return DownloadViewModel(body="".join(lines))
