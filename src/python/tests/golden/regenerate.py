# -*- coding: utf-8 -*-
"""
Golden Master 기준 파일 재생성 (GREEN baseline).

Usage (from src/python):
    python tests/golden/regenerate.py

의도적 계약 변경(PRD → README, RR-1) 후에만 실행.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app import app  # noqa: E402
import app as app_module  # noqa: E402
from session import Session  # noqa: E402
from tests.conftest import ANCHOR_TEXT  # noqa: E402
from tests.golden.helpers import (  # noqa: E402
    CSV_GOLDEN_PATH,
    MASTER_PATH,
    SECTION_HEADERS,
    save_csv_golden,
    save_section,
)
from tests.golden.normalize import snapshot_from_html  # noqa: E402

_POSITIVE_TEXT = "배송이 빨라서 좋아요"


def _reset() -> None:
    Session.current_feedbacks = []
    app_module.fil_data = []


def main() -> None:
    app.config["TESTING"] = True
    client = app.test_client()

    _reset()
    r = client.post("/analyze", data={"text": ANCHOR_TEXT})
    save_section(
        "S1",
        snapshot_from_html("S1", r.data.decode("utf-8"), expected_count=1).to_canonical_block(),
    )

    _reset()
    r = client.post("/analyze", data={"text": _POSITIVE_TEXT})
    save_section(
        "S2",
        snapshot_from_html("S2", r.data.decode("utf-8"), expected_count=1).to_canonical_block(),
    )

    _reset()
    client.post("/analyze", data={"text": ANCHOR_TEXT})
    r = client.post("/analyze", data={"text": "   \t\n  "})
    save_section(
        "S3",
        snapshot_from_html("S3", r.data.decode("utf-8"), expected_count=1).to_canonical_block(),
    )

    _reset()
    r = client.post("/filter", data={"sentiment": "전체", "keyword": "전체"})
    save_section("S4", snapshot_from_html("S4", r.data.decode("utf-8")).to_canonical_block())

    _reset()
    client.post("/analyze", data={"text": ANCHOR_TEXT})
    client.post("/filter", data={"sentiment": "부정", "keyword": "배송"})
    r = client.get("/download")
    save_csv_golden(r.data)

    print(f"Wrote {MASTER_PATH}")
    for key, header in SECTION_HEADERS.items():
        print(f"  - {header}")
    print(f"Wrote {CSV_GOLDEN_PATH} ({CSV_GOLDEN_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
