# -*- coding: utf-8 -*-
"""UploadCsvUseCase — CSV 업로드 (UTF-8 BOM, INV-SESSION-001)."""

from __future__ import annotations

import csv
import io

from entity.ports import FeedbackRepositoryPort
from feedback import Feedback
from control.dto import AnalysisViewModel


class UploadCsvUseCase:
    def __init__(self, repository: FeedbackRepositoryPort) -> None:
        self._repository = repository

    def execute(self, raw: bytes) -> AnalysisViewModel:
        if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
            return AnalysisViewModel(error="파일 업로드 중 오류가 발생했습니다.")

        try:
            content = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            return AnalysisViewModel(error="파일 업로드 중 오류가 발생했습니다.")

        try:
            reader = csv.reader(io.StringIO(content))
            first_line = True
            added = 0
            for row in reader:
                if first_line:
                    first_line = False
                    continue
                if row and row[0].strip():
                    self._repository.add_text(row[0].strip())
                    added += 1
        except (csv.Error, ValueError):
            return AnalysisViewModel(error="파일 업로드 중 오류가 발생했습니다.")

        total = len(self._repository.all())
        return AnalysisViewModel(success=f"{total}개의 피드백이 입력되었습니다.")
