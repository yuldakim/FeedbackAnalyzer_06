# -*- coding: utf-8 -*-
"""Session facade — delegates to infrastructure.feedback_repository (M2 migration)."""

from __future__ import annotations

from typing import List

from feedback import Feedback
from infrastructure import wiring


class Session:
    @classmethod
    def init_session(cls) -> None:
        pass

    @classmethod
    def get_current_feedbacks(cls) -> List[Feedback]:
        return wiring.feedback_repository.all()

    @classmethod
    def update_current_feedbacks(cls, feedbacks: List[Feedback]) -> None:
        wiring.feedback_repository.replace_all(feedbacks)


Session.current_feedbacks = property(  # type: ignore[misc]
    fget=lambda cls: wiring.feedback_repository.all(),
    fset=lambda cls, val: wiring.feedback_repository.replace_all(val),
)
