# -*- coding: utf-8 -*-


class Feedback:
    def __init__(self, text: str):
        self._text = text

    @property
    def text(self) -> str:
        return self._text
