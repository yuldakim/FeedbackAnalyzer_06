# -*- coding: utf-8 -*-
"""PageLogSink (F-14) — control warning/error visibility on HTML page."""

from __future__ import annotations

from typing import Optional


class PageLogSink:
    def __init__(self) -> None:
        self.show_warning = True
        self.show_error = True

    def filter_warning(self, message: str) -> str:
        if not message or not self.show_warning:
            return ""
        return message

    def filter_error(self, message: str) -> str:
        if not message or not self.show_error:
            return ""
        return message

    def set_levels(self, *, warning: bool, error: bool) -> None:
        self.show_warning = warning
        self.show_error = error

    def reset(self) -> None:
        self.show_warning = True
        self.show_error = True
