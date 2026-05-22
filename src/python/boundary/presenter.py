# -*- coding: utf-8 -*-
"""HTML presenter (F-10) — escape and page layout only."""

from __future__ import annotations

from datetime import datetime
from html import escape
from typing import List, Optional

from constants import CATEGORIES
from control.dto import AnalysisViewModel
from feedback import Feedback


def _current_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class HtmlPresenter:
    def render_page(
        self,
        success: str = "",
        warning: str = "",
        error: str = "",
        sentiment_results: Optional[dict] = None,
        keyword_results: Optional[dict] = None,
        feedbacks: Optional[list] = None,
    ) -> str:
        if sentiment_results is None:
            sentiment_results = {}
        if keyword_results is None:
            keyword_results = {}
        if feedbacks is None:
            feedbacks = []

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Feedback Analyzer</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; text-align: center; margin-bottom: 30px; }}
        .section {{ margin-bottom: 30px; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
        .form-group {{ margin-bottom: 15px; }}
        label {{ display: block; margin-bottom: 5px; font-weight: bold; color: #555; }}
        input[type="text"], textarea, select {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; box-sizing: border-box; }}
        textarea {{ height: 100px; resize: vertical; }}
        button {{ background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; margin-right: 10px; }}
        button:hover {{ background-color: #0056b3; }}
        .btn-success {{ background-color: #28a745; }}
        .btn-success:hover {{ background-color: #1e7e34; }}
        .alert-success {{ background-color: #d4edda; border-color: #c3e6cb; color: #155724; padding: 10px; border-radius: 4px; }}
        .alert-warning {{ background-color: #fff3cd; border-color: #ffeaa7; color: #856404; padding: 10px; border-radius: 4px; }}
        .alert-danger {{ background-color: #f8d7da; border-color: #f5c6cb; color: #721c24; padding: 10px; border-radius: 4px; }}
        .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .stat-item {{ text-align: center; padding: 15px; background-color: #f8f9fa; border-radius: 5px; flex: 1; margin: 0 10px; }}
        .stat-number {{ font-size: 24px; font-weight: bold; color: #007bff; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
    </style>
</head>
<body>
<div class="container">
    <h1>Feedback Analyzer</h1>
    <p style="text-align: center; color: #666;">고객 피드백 분석 시스템</p>"""

        if success:
            html += (
                f'<p class="alert alert-success">{_current_timestamp()} : '
                f"{escape(success)}</p>"
            )

        html += """
    <div class="section">
        <h3>피드백 입력</h3>
        <form action="/analyze" method="post">
            <div class="form-group">
                <label for="text">피드백 텍스트:</label>
                <textarea id="text" name="text" placeholder="피드백을 입력하세요..."></textarea>
            </div>
            <button type="submit">입력하기</button>
        </form>
    </div>"""

        html += """
    <div class="section">
        <h3>CSV 파일 업로드 (선택사항)</h3>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <div class="form-group">
                <label for="file">CSV 파일 선택:</label>
                <input type="file" id="file" name="file" accept=".csv">
            </div>
            <button type="submit">업로드</button>
        </form>
    </div>"""

        cat_options = "".join(
            f'<option value="{cat}">{cat}</option>' for cat in CATEGORIES
        )
        html += f"""
    <div class="section">
        <h3>피드백 분석</h3>
        <form action="/filter" method="post">
            <div class="form-group">
                <label for="sentiment">감정 필터:</label>
                <select id="sentiment" name="sentiment">
                    <option value="전체">전체</option>
                    <option value="긍정">긍정</option>
                    <option value="중립">중립</option>
                    <option value="부정">부정</option>
                </select>
            </div>
            <div class="form-group">
                <label for="keyword">키워드 필터:</label>
                <select id="keyword" name="keyword">
                    <option value="전체">전체</option>
                    {cat_options}
                </select>
            </div>
            <button type="submit">분  석</button>
        </form>
    </div>"""

        if warning:
            html += f'<p class="alert alert-warning">{escape(warning)}</p>'

        if sentiment_results or keyword_results:
            html += '<div class="section"><h3>분석 결과</h3>'
            if sentiment_results:
                html += '<h4>감정 분포</h4><div class="stats">'
                for label, count in sentiment_results.items():
                    html += (
                        f'<div class="stat-item">'
                        f'<div class="stat-number">{count}</div>'
                        f'<div class="stat-label">{label}</div></div>'
                    )
                html += "</div>"
            if keyword_results:
                html += '<h4>키워드 분포</h4><div class="stats">'
                for label, count in keyword_results.items():
                    html += (
                        f'<div class="stat-item">'
                        f'<div class="stat-number">{count}</div>'
                        f'<div class="stat-label">{label}</div></div>'
                    )
                html += "</div>"
            html += (
                '<a href="/download"><button class="btn-success">'
                "결과 다운로드</button></a></div>"
            )

        if error:
            html += f'<p class="alert alert-danger">{escape(error)}</p>'

        if feedbacks:
            html += '<div class="section"><h3>피드백 원문</h3><ul>'
            for fb in feedbacks:
                html += f"<li>{escape(fb.text)}</li>"
            html += "</ul></div>"

        html += "</div></body></html>"
        return html

    def render_vm(
        self, vm: AnalysisViewModel, feedbacks: Optional[List[Feedback]] = None
    ) -> str:
        if feedbacks is None:
            feedbacks = (
                [Feedback(t) for t in vm.feedback_texts]
                if vm.feedback_texts
                else []
            )
        sentiment_results = vm.sentiment_results
        keyword_results = vm.keyword_results
        if vm.warning or vm.error:
            sentiment_results = {}
            keyword_results = {}
        return self.render_page(
            success=vm.success or "",
            warning=vm.warning or "",
            error=vm.error or "",
            sentiment_results=sentiment_results,
            keyword_results=keyword_results,
            feedbacks=feedbacks,
        )


presenter = HtmlPresenter()
