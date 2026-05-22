# -*- coding: utf-8 -*-
"""Flask routes — delegate to control use cases (thin boundary)."""

from __future__ import annotations

from flask import Blueprint, Response, jsonify, request

from boundary.presenter import presenter
from control.analyze_feedback import AnalyzeFeedbackUseCase
from control.download_filtered import DownloadFilteredUseCase
from control.filter_feedbacks import FilterFeedbacksUseCase
from control.json_response import build_analysis_json
from control.register_keyword import RegisterKeywordUseCase
from control.trend_analysis import TrendAnalysisUseCase
from control.upload_csv import UploadCsvUseCase
from entity.feedback_analyzer import FeedbackAnalyzer
from infrastructure import wiring
from logger import Logger

bp = Blueprint("feedback", __name__)


def _analyzer() -> FeedbackAnalyzer:
    return FeedbackAnalyzer(
        wiring.feedback_repository,
        store=wiring.filtered_store,
        file_handler=wiring.file_handler,
        rule_repo=wiring.keyword_rule_repository,
    )


@bp.route("/", methods=["GET"])
def index():
    feedbacks = wiring.feedback_repository.all()
    trend = TrendAnalysisUseCase(wiring.trend_csv_path).execute()
    return presenter.render_page(
        success="피드백 분석기 시작",
        feedbacks=feedbacks,
        categories=wiring.keyword_rule_repository.list_categories(),
        trend_points=trend,
    )


@bp.route("/analyze", methods=["POST"])
def analyze():
    try:
        export_path = str(wiring.export_dir / "session_feedbacks.csv")
        vm = AnalyzeFeedbackUseCase(
            wiring.feedback_repository,
            file_handler=wiring.file_handler,
            export_path=export_path,
            rule_repo=wiring.keyword_rule_repository,
        ).execute(request.form.get("text", ""))
        feedbacks = wiring.feedback_repository.all()
        for fb in feedbacks:
            Logger.log_info(fb.text)
        if feedbacks:
            Logger.log_info(f"현재 {len(feedbacks)}개의 피드백이 입력되었습니다.")
        return presenter.render_vm(vm, feedbacks=feedbacks)
    except Exception as e:
        Logger.log_error(f"오류 발생: {e}")
        return presenter.render_page(error="처리 중 오류가 발생했습니다.")


@bp.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files.get("file")
        raw = file.read() if file and file.filename else b""
        vm = UploadCsvUseCase(wiring.feedback_repository).execute(raw)
        if file and file.filename and vm.success:
            Logger.log_info("파일이 성공적으로 업로드되었습니다.")
        return presenter.render_vm(vm, feedbacks=wiring.feedback_repository.all())
    except Exception as e:
        Logger.log_error(f"파일 업로드 오류: {e}")
        return presenter.render_page(error="파일 업로드 중 오류가 발생했습니다.")


@bp.route("/filter", methods=["POST"])
def filter_route():
    try:
        vm = FilterFeedbacksUseCase(
            wiring.feedback_repository,
            wiring.filtered_store,
            rule_repo=wiring.keyword_rule_repository,
        ).execute(
            request.form.get("sentiment", "전체"),
            request.form.get("keyword", "전체"),
        )
        repo_feedbacks = wiring.feedback_repository.all()
        if vm.error:
            return presenter.render_vm(vm, feedbacks=repo_feedbacks)
        if vm.warning:
            Logger.log_warning(vm.warning)
            return presenter.render_vm(vm, feedbacks=repo_feedbacks)
        filtered = wiring.filtered_store.load()
        return presenter.render_vm(vm, feedbacks=filtered)
    except Exception as e:
        Logger.log_error(f"오류 발생: {e}")
        return presenter.render_page(error="처리 중 오류가 발생했습니다.")


@bp.route("/download", methods=["GET"])
def download():
    vm = DownloadFilteredUseCase(wiring.filtered_store).execute()
    return Response(
        vm.body,
        mimetype="text/csv; charset=UTF-8",
        headers={
            "Content-Disposition": "attachment; filename=filtered_feedback.csv"
        },
    )


@bp.route("/keywords/register", methods=["POST"])
def register_keywords():
    raw = request.form.get("keywords", "")
    keywords = [k.strip() for k in raw.split(",") if k.strip()]
    vm = RegisterKeywordUseCase(wiring.keyword_rule_repository).execute(
        request.form.get("category", ""), keywords
    )
    return presenter.render_vm(vm, feedbacks=wiring.feedback_repository.all())


@bp.route("/settings/log-levels", methods=["POST"])
def log_levels():
    wiring.page_log_sink.set_levels(
        warning="show_warning" in request.form,
        error="show_error" in request.form,
    )
    return presenter.render_page(success="PageLogSink 설정이 적용되었습니다.")


@bp.route("/api/session", methods=["GET"])
def api_session():
    """INV-JSON-001 — current session analysis JSON."""
    analyzer = _analyzer()
    return jsonify(build_analysis_json(analyzer, success="ok"))


@bp.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.get_json(silent=True) or {}
    text = data.get("text", request.form.get("text", ""))
    vm = AnalyzeFeedbackUseCase(
        wiring.feedback_repository,
        rule_repo=wiring.keyword_rule_repository,
    ).execute(text)
    analyzer = _analyzer()
    return jsonify(
        build_analysis_json(
            analyzer,
            success=vm.success,
            warning=vm.warning,
            error=vm.error,
        )
    )


@bp.route("/api/filter", methods=["POST"])
def api_filter():
    data = request.get_json(silent=True) or {}
    sentiment = data.get("sentiment", request.form.get("sentiment", "전체"))
    keyword = data.get("keyword", request.form.get("keyword", "전체"))
    vm = FilterFeedbacksUseCase(
        wiring.feedback_repository,
        wiring.filtered_store,
        rule_repo=wiring.keyword_rule_repository,
    ).execute(sentiment, keyword)
    analyzer = _analyzer()
    feedbacks = (
        wiring.filtered_store.load()
        if not vm.error and not vm.warning
        else wiring.feedback_repository.all()
    )
    return jsonify(
        build_analysis_json(
            analyzer,
            success=vm.success,
            warning=vm.warning,
            error=vm.error,
            feedbacks=feedbacks,
        )
    )
