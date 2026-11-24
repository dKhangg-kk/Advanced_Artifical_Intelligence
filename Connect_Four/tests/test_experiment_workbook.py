"""Kiem tra nguon du lieu va file Excel phan cong / bang chung thuc nghiem."""

from __future__ import annotations

import csv
import importlib.util
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_experiment_workbook.py"


def _module():
    spec = importlib.util.spec_from_file_location("build_experiment_workbook", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_format_vn_doi_utc_sang_gio_viet_nam() -> None:
    mod = _module()
    assert mod.format_vn("2026-11-20T09:29:30+00:00") == "20/11/2026 16:29"
    assert mod.format_vn("2026-11-11T15:05:16.898196+00:00") == "11/11/2026 22:05"
    assert mod.format_vn("") == ""


def test_classify_theo_loai_run() -> None:
    mod = _module()
    assert mod.classify("k1-heuristic-random-20261109T061032Z-s0").startswith("K1")
    assert mod.classify("ablation-a6-opp_random-s0-20261120T132502Z") == "A6 - DQN"
    assert mod.classify("tournament-default-20261118T163224Z-s20261118-random-vs-dqn") == "Giải đấu"
    assert mod.classify("heuristic-vs-random-20261120T092931Z-s42").startswith("Giải đấu")


def test_moi_run_id_deu_co_nguoi_chay() -> None:
    mod = _module()
    manifest = _read(mod.MANIFEST)
    assignments = _read(mod.ASSIGNMENTS)
    run_ids = {row["run_id"].strip() for row in manifest}
    assigned = {row["run_id"].strip() for row in assignments}
    assert run_ids <= assigned, f"Thiếu: {sorted(run_ids - assigned)}"
    assert len(assigned) == len(assignments), "run_id bị trùng trong file phân công"


def test_bang_phan_cong_co_bon_thanh_vien() -> None:
    mod = _module()
    plan = _read(mod.PLAN)
    assert len(plan) >= 10
    assert len({row["thanh_vien"] for row in plan}) == 4
    assert {row["so_run"] for row in plan} >= {"0", "1"}


def test_sinh_excel_ba_sheet(tmp_path: Path) -> None:
    openpyxl = pytest.importorskip("openpyxl")
    mod = _module()
    output = tmp_path / "schedule.xlsx"
    mod.build_workbook(output)
    assert output.is_file()

    wb = openpyxl.load_workbook(output)
    assert wb.sheetnames == ["Phan cong", "Thuc nghiem", "Minh chung"]

    evidence = wb["Thuc nghiem"]
    assert evidence.max_row == 1 + len(_read(mod.MANIFEST))
    headers = [cell.value for cell in evidence[1]]
    assert "Bắt đầu (UTC+7)" in headers
    assert "Kết thúc (UTC+7)" in headers
    assert "Người thực hiện" in headers

    first_time = evidence.cell(row=2, column=4).value
    assert re.fullmatch(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}", first_time)
    assert wb["Phan cong"].max_row == 1 + len(_read(mod.PLAN))
