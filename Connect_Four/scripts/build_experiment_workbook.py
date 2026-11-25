"""Sinh file Excel duy nhất chua phan cong va bang chung thuc nghiem.

Chay tu thu muc `Connect_Four/`:

    PYTHONPATH=src python scripts/build_experiment_workbook.py

Nguon:
    results/logs/run_manifest.csv        - thoi gian that cua moi lan chay
    results/experiment_assignments.csv   - run_id -> nguoi chay (do thanh vien xac nhan)
    results/experiment_plan.csv          - bang phan cong cac nhiem vu

Ket qua:
    results/experiment_schedule.xlsx     - 3 sheet: Phan cong, Thuc nghiem, Minh chung

Khong su dung pandas/ofert de ghi file: mo va doc bang openpyxl, co the tai ve tu
GitHub va gui rieng cho giang vien.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo

    VIETNAM = ZoneInfo("Asia/Ho_Chi_Minh")
except Exception:  # pragma: no cover - fallback neu thieu tzdata
    VIETNAM = timezone(timedelta(hours=7))

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "results/logs/run_manifest.csv"
ASSIGNMENTS = ROOT / "results/experiment_assignments.csv"
PLAN = ROOT / "results/experiment_plan.csv"
DEFAULT_OUTPUT = ROOT / "results/experiment_schedule.xlsx"

UNKNOWN = "CHƯA XÁC NHẬN"

PLAN_HEADERS = {
    "stt": "STT",
    "thanh_vien": "Thành viên",
    "mssv": "MSSV",
    "pham_vi": "Phạm việc",
    "nhiem_vu": "Nhiệm vụ",
    "so_run": "Số run dự kiến",
    "lenh_chay": "Lệnh chạy",
    "san_pham": "Sản phẩm",
    "trang_thai": "Trạng thái",
    "ngay_giao": "Ngày giao",
    "ngay_xong": "Ngày xong",
    "ghi_chu": "Ghi chú",
}

EVIDENCE_HEADERS = [
    "STT",
    "run_id",
    "Người thực hiện",
    "Bắt đầu (UTC+7)",
    "Kết thúc (UTC+7)",
    "Loại",
    "Mục tiêu/Ghi chú",
    "Lệnh chạy",
    "Commit",
    "Config",
    "Seed",
    "Trạng thái",
    "Log thô",
    "Bảng kết quả",
]

SUMMARY_HEADERS = [
    "Thành viên",
    "Số lần chạy",
    "Run đầu tiên",
    "Run gần nhất",
    "Phạm việc",
    "Hồ sơ đóng góp",
    "Ghi chú",
]

PROFILES = {
    "Bùi Anh Đức": "docs/contributions/duc.md",
    "Phạm Thái Duy Khang": "docs/contributions/pham-thai-duy-khang.md",
    "Phan Lê Ngọc Như Ý": "docs/contributions/phan-le-ngoc-nhu-y.md",
    "Bùi Quyền Kiệt": "docs/contributions/kiet.md",
}

TYPE_RULES = (
    ("K1 - Heuristic/Random", lambda rid: rid.startswith("k1-")),
    ("K3 - MCTS", lambda rid: rid.startswith("k3-")),
    ("A1/A2/A5 - tìm kiếm", lambda rid: rid.startswith(("ablation-a1-", "ablation-a2-", "ablation-a5-"))),
    ("A3 - CNN", lambda rid: "a3" in rid),
    ("A4 - DQN", lambda rid: "a4" in rid),
    ("A6 - DQN", lambda rid: "a6" in rid),
    ("Giải đấu", lambda rid: rid.startswith("tournament")),
    ("Train CNN/DQN", lambda rid: rid.startswith(("train_cnn", "train_dqn", "2026"))),
)


def format_vn(value: str) -> str:
    """ISO timestamp (UTC) -> dd/mm/yyyy hh:mm theo giờ Viet Nam."""
    raw = (value or "").strip().replace("Z", "+00:00")
    if not raw:
        return ""
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(VIETNAM).strftime("%d/%m/%Y %H:%M")



def classify(run_id: str) -> str:
    if run_id in {
        "alphabeta-vs-mcts-20261125T162305Z-s20261119",
        "alphabeta-vs-mcts-20261125T163120Z-s20261120",
    }:
        return "RQ1 – Độ nhạy theo seed"

    if "heuristic-vs-random" in run_id:
        return "Giải đấu - K1 đối chiếu"
    for label, matches in TYPE_RULES:
        if matches(run_id):
            return label
    return "Khác"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_owners(path: Path, run_ids: list[str]) -> dict[str, tuple[str, str]]:
    owners: dict[str, tuple[str, str]] = {}
    for row in read_csv(path):
        rid = row["run_id"].strip()
        if rid in owners:
            raise ValueError(f"run_id bị trùng trong file phân công: {rid}")
        owners[rid] = (row["nguoi_chay"].strip() or UNKNOWN, row["pham_vi"].strip())
    missing = [rid for rid in run_ids if rid not in owners]
    if missing:
        raise ValueError("Thiếu người chạy cho các run_id: " + ", ".join(missing))
    return owners


def _paths(notes: str, pattern: str) -> str:
    return "; ".join(dict.fromkeys(re.findall(pattern, notes or "")))


def _style(ws, widths: dict[str, int], wrap_cols: set[str] | None = None) -> None:
    from openpyxl.styles import Alignment, Font

    wrap_cols = wrap_cols or set()
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for col, width in widths.items():
        ws.column_dimensions[col].width = width
    if wrap_cols:
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                if cell.column_letter in wrap_cols:
                    cell.alignment = Alignment(vertical="top", wrap_text=True)


def build_workbook(output: Path) -> None:
    """Doc cac CSV nguon va ghi file .xlsx. Goi lai se ghi de (idempotent)."""
    from openpyxl import Workbook

    manifest = read_csv(MANIFEST)
    plan = read_csv(PLAN)
    run_ids = [row["run_id"].strip() for row in manifest]
    owners = load_owners(ASSIGNMENTS, run_ids)

    wb = Workbook()

    # --- Sheet 1: bang phan cong -------------------------------------------------
    ws = wb.active
    ws.title = "Phan cong"
    ws.append([PLAN_HEADERS[key] for key in PLAN_HEADERS])
    for row in plan:
        ws.append([row.get(key, "") for key in PLAN_HEADERS])
    _style(
        ws,
        {"A": 6, "B": 24, "C": 13, "D": 18, "E": 36, "F": 12, "G": 62, "H": 42, "I": 15, "J": 13, "K": 13, "L": 30},
        {"E", "G", "H", "L"},
    )

    # --- Sheet 2: bang chung thuc nghiem -----------------------------------------
    ws = wb.create_sheet("Thuc nghiem")
    ws.append(EVIDENCE_HEADERS)
    for i, row in enumerate(sorted(manifest, key=lambda r: r["started_at"]), start=1):
        rid = row["run_id"].strip()
        notes = row.get("notes", "")
        person, scope = owners[rid]
        if person != UNKNOWN and scope:
            person = f"{person} ({scope})"
        ws.append(
            [
                i,
                rid,
                person,
                format_vn(row["started_at"]),
                format_vn(row["finished_at"]),
                classify(rid),
                notes,
                row.get("command", ""),
                row.get("git_commit", ""),
                row.get("config_file", ""),
                row.get("seed", ""),
                row.get("status", ""),
                _paths(notes, r"(?:results|checkpoints)/logs/[\w.\-]+\.csv"),
                _paths(notes, r"results/tables/[\w.\-]+\.csv")]
        )
    _style(
        ws,
        {"A": 6, "B": 52, "C": 30, "D": 19, "E": 19, "F": 24, "G": 65, "H": 50,
         "I": 12, "J": 36, "K": 12, "L": 13, "M": 55, "N": 40},
        {"B", "C", "G", "H", "J", "M", "N"},
    )

    # --- Sheet 3: minh chung / huong dan kiem tra ---------------------------------
    ws = wb.create_sheet("Minh chung")
    ws.append(SUMMARY_HEADERS)
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in sorted(manifest, key=lambda r: r["started_at"]):
        grouped[owners[row["run_id"].strip()][0]].append(row)
    for person in sorted(grouped, key=lambda p: (p == UNKNOWN, p)):
        runs = grouped[person]
        note = ""
        if person == UNKNOWN:
            note = "Can thanh vien xac nhan nguoi chay truoc khi nop."
        elif person in PROFILES:
            note = "Da xac nhan bang hoso dong gop."
        ws.append(
            [
                person,
                len(runs),
                format_vn(runs[0]["started_at"]),
                format_vn(runs[-1]["finished_at"]),
                "; ".join(sorted({owners[r["run_id"].strip()][1] for r in runs if owners[r["run_id"].strip()][1]})),
                PROFILES.get(person, ""),
                note,
            ]
        )
    _style(ws, {"A": 26, "B": 13, "C": 19, "D": 19, "E": 30, "F": 48, "G": 42}, {"E", "G"})

    guide_row = ws.max_row + 3
    guide = [
        ("Huong dan kiem tra (gio da doi tu UTC sang UTC+7)", ""),
        ("1. Mo sheet 'Phan cong'de xem moi nguoi duoc giao viec gi.", ""),
        ("2. Mo sheet 'Thuc nghiem', chon run_id bat ky.", ""),
        ("3. Mo file log o cot 'Log thô' de doi chieu so lieu trong bao cao.", ""),
        ("File nay nam tai Connect_Four/results/experiment_schedule.xlsx tren GitHub; co the tai ve gui rieng.", ""),
    ]
    for offset, (text, _) in enumerate(guide):
        ws.cell(row=guide_row + offset, column=1, value=text)

    output.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output)
    print(f"Da ghi {output} ({len(manifest)} lan chay, {len(plan)} nhiem vu, {len(grouped)} nhom nguoi).")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Duong dan file .xlsx can ghi")
    args = parser.parse_args()
    build_workbook(args.output)


if __name__ == "__main__":
    main()
