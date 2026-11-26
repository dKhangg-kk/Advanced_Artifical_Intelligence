#!/usr/bin/env python3
"""Đối chiếu số liệu CNN (mục 4.4/4.5) với bộ đóng băng 19/11/2026.

Chạy từ thư mục ``Connect_Four/``::

    PYTHONPATH=src python scripts/verify_frozen_cnn_numbers.py

Mặc định so với commit ``2521b36`` (19/11/2026 22:57 UTC+7), bản được Issue #41
gọi là bộ số đóng băng 19/11 22:00. Script chỉ kiểm tra các dòng thuộc mục
4.4/4.5 đã có trong bản đóng băng; các dòng thêm sau đó (ví dụ A6) được phép
xuất hiện và không làm sai đối chiếu.
"""

from __future__ import annotations

import argparse
import csv
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_NUMBERS = "results/tables/report_numbers.csv"
DEFAULT_COMMIT = "2521b36"
SECTIONS = ("4.4", "4.4 dqn", "4.5", "4.5 a4-dqn")
FIGURES = (
    "results/figures/cnn_main_learning_curve.png",
    "results/figures/ablation_a3_learning_curves.png",
    "results/figures/ablation_a3_accuracy.png",
)


def _from_git(commit: str, rel: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{commit}:Connect_Four/{rel}"], cwd=ROOT.parent
    )


def _rows(data: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(data.decode("utf-8").splitlines()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", default=DEFAULT_COMMIT)
    args = parser.parse_args()

    current_rows = _rows((ROOT / REPORT_NUMBERS).read_bytes())
    frozen_rows = [
        row
        for row in _rows(_from_git(args.commit, REPORT_NUMBERS))
        if row["report_section"] in SECTIONS
    ]
    current_by_key = {
        (row["report_section"], row["metric"]): row for row in current_rows
    }
    missing = []
    changed = []
    for row in frozen_rows:
        key = (row["report_section"], row["metric"])
        now = current_by_key.get(key)
        if now is None:
            missing.append(key)
        elif now != row:
            changed.append(key)
    print(
        f"report_numbers: {len(frozen_rows)} dong dong bang, "
        f"{len(missing)} thieu, {len(changed)} khac"
    )

    sources = sorted(
        {row["source_path"] for row in frozen_rows if row["source_type"] in {"log", "table", "checkpoint_metadata"}}
    )
    bad_sources = []
    for rel in sources:
        try:
            frozen = _from_git(args.commit, rel)
        except subprocess.CalledProcessError:
            bad_sources.append(f"{rel} (khong co trong ban dong bang)")
            continue
        if not (ROOT / rel).exists() or (ROOT / rel).read_bytes() != frozen:
            bad_sources.append(rel)
    print(f"log/bang/metadata nguon: {len(sources)} kiem tra, {len(bad_sources)} khac")

    bad_figures = []
    for rel in FIGURES:
        if (ROOT / rel).read_bytes() != _from_git(args.commit, rel):
            bad_figures.append(rel)
    print(f"hinh: {len(FIGURES)} kiem tra, {len(bad_figures)} khac")

    problems = missing + changed + bad_sources + bad_figures
    if problems:
        print("KHONG KHOP:", *problems, sep="\n  - ")
        return 1
    print(f"DAT: du lieu hien tai khop toan bo ban dong bang {args.commit}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
