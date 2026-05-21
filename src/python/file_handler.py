# -*- coding: utf-8 -*-
from typing import List
from feedback import Feedback


class FileHandler:
    """Dead code - kept for parity with original C++ project."""

    def save_result(self, data: List[Feedback]):
        print(f"saveResult{len(data)}")
        for fb in data:
            print(fb.text)

    def save(self, data: List[Feedback]):
        self.save_result(data)
