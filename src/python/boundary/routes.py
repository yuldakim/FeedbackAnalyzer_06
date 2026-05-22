# -*- coding: utf-8 -*-
"""Flask routes — delegate to control use cases (thin boundary)."""

from __future__ import annotations

from flask import Blueprint, Response, request

from boundary.presenter import presenter
from control.analyze_feedback import AnalyzeFeedbackUseCase
from control.download_filtered import DownloadFilteredUseCase
from control.filter_feedbacks import FilterFeedbacksUseCase
from control.upload_csv import UploadCsvUseCase
from infrastructure import wiring
from logger import Logger

bp = Blueprint("feedback", __name__)


@bp.route("/", methods=["GET"])
def index():
    feedbacks = wiring.feedback_repository.all()
    return presenter.render_page(
        success="피드백 분석기 시작", feedbacks=feedbacks
    )


@bp.route("/analyze", methods=["POST"])
def analyze():
    try:
        vm = AnalyzeFeedbackUseCase(wiring.feedback_repository).execute(
            request.form.get("text", "")
        )
        feedbacks = wiring.feedback_repository.all()
        for fb in feedbacks:
            Logger.log_info(fb.text)
        if feedbacks:
            Logger.log_info(f"현재 {len(feedbacks)}개의 피드백이 입력되었습니다.")
            Logger.log_info("감성 분석 완료")
            Logger.log_info("키워드 분석 완료")
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
        return presenter.render_vm(vm)
    except Exception as e:
        Logger.log_error(f"파일 업로드 오류: {e}")
        return presenter.render_page(error="파일 업로드 중 오류가 발생했습니다.")


@bp.route("/filter", methods=["POST"])
def filter_route():
    try:
        vm = FilterFeedbacksUseCase(
            wiring.feedback_repository, wiring.filtered_store
        ).execute(
            request.form.get("sentiment", "전체"),
            request.form.get("keyword", "전체"),
        )
        if vm.error:
            return presenter.render_vm(vm)
        if vm.warning:
            Logger.log_warning(vm.warning)
            return presenter.render_vm(vm)
        filtered = wiring.filtered_store.load()
        Logger.log_info(f"필터링 결과: {len(filtered)}개의 피드백")
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
