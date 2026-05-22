# -*- coding: utf-8 -*-
"""DownloadFilteredUseCase — CSV export from filter snapshot (INV-CSV-OUT-003)."""

from __future__ import annotations

from entity.ports import FilteredResultStorePort
from control.dto import DownloadViewModel


class DownloadFilteredUseCase:
    def __init__(self, store: FilteredResultStorePort) -> None:
        self._store = store

    def execute(self) -> DownloadViewModel:
        snapshot = self._store.load()
        lines = ["\ufeff", "text\n"] + [fb.text + "\n" for fb in snapshot]
        return DownloadViewModel(body="".join(lines))
