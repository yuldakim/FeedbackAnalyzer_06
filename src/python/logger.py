# -*- coding: utf-8 -*-
from datetime import datetime


class Logger:
    debug_mode = True

    @staticmethod
    def _timestamp():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def log_info(cls, message: str):
        print(f"[{cls._timestamp()}] INFO: {message}")

    @classmethod
    def log_warning(cls, message: str):
        print(f"[{cls._timestamp()}] WARNING: {message}")

    @classmethod
    def log_error(cls, message: str):
        import sys
        print(f"[{cls._timestamp()}] ERROR: {message}", file=sys.stderr)

    @classmethod
    def log_debug(cls, message: str):
        if cls.debug_mode:
            print(f"[{cls._timestamp()}] DEBUG: {message}")

    @classmethod
    def set_debug_mode(cls, mode: bool):
        cls.debug_mode = mode
