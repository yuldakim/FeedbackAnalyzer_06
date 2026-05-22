# -*- coding: utf-8 -*-
"""Flask composition root — thin entry (F-07)."""

from flask import Flask

from boundary.routes import bp
from control.analyze_feedback import AnalyzeFeedbackUseCase
from control.filter_feedbacks import FilterFeedbacksUseCase
from logger import Logger

app = Flask(__name__)
app.register_blueprint(bp)

# Re-export for tests that patch app.* use cases
__all__ = ["app", "AnalyzeFeedbackUseCase", "FilterFeedbacksUseCase"]


if __name__ == "__main__":  # pragma: no cover
    Logger.log_info("서버가 http://localhost:8080 에서 시작됩니다.")
    app.run(host="0.0.0.0", port=8080)
