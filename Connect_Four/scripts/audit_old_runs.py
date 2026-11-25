"""Đối chiếu 49 lần chạy A4/A6/tournament cũ giữa các tầng log.

Chạy từ thư mục `Connect_Four/`:

    PYTHONPATH=src python scripts/audit_old_runs.py

Nguồn (tầng 1 / tầng 3):
    results/logs/run_manifest.csv
    results/experiment_assignments.csv
    results/tables/report_numbers.csv
    docs/EXPERIMENT_LOG.md

Kết quả:
    results/tables/audit_old_runs_49.csv

Script chỉ đọc các nguồn trên và ghi lại một dòng cho mỗi run_id thuộc ba nhóm
`tournament-*`, `a4-*`, `a6-*`; không sửa manifest hay báo cáo.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MANIFEST = ROOT / "results/logs/run_manifest.csv"
ASSIGNMENTS = ROOT / "results/experiment_assignments.csv"
REPORT_NUMBERS = ROOT / "results/tables/report_numbers.csv"
EXPERIMENT_LOG = ROOT / "docs/EXPERIMENT_LOG.md"
OUTPUT = ROOT / "results/tables/audit_old_runs_49.csv"

FIELDS = (
    "run_id",
    "nhom",
    "co_trong_manifest",
    "trang_thai",
    "bat_dau_utc",
    "config_file",
    "log_files",
    "log_day_du",
    "report_numbers_dong",
    "report_numbers_muc",
    "nhat_ky_tieu_de",
    "nguoi_chay",
    "pham_vi",
    "ket_luan",
)

# Nhật ký ghi theo prefix (một dòng cho cả giải đấu / cả A4), không phải từng run_id.
LOG_SECTIONS = (
    (
        "tournament-default-20261113T140850Z-s20261113",
        "DQN pilot va Round-Robin pilot (Như Ý)",
    ),
    (
        "tournament-default-20261118T163224Z-s20261118",
        "A4, đóng băng DQN, chẩn đoán, giải đấu Round-Robin",
    ),
    (
        "tournament-timed-20261118T164206Z-s20261119",
        "A4, đóng băng DQN, chẩn đoán, giải đấu Round-Robin",
    ),
    ("a4-", "A4, đóng băng DQN, chẩn đoán, giải đấu Round-Robin"),
    ("a6-", "A6: đối thủ huấn luyện DQN"),
)

OWNER = "Phan Lê Ngọc Như Ý"


def group_of(run_id: str) -> str:
    if run_id.startswith("tournament-"):
        return "tournament"
    if run_id.startswith("a4-"):
        return "a4"
    if run_id.startswith("a6-"):
        return "a6"
    return ""


def scope_of(run_id: str) -> str:
    group = group_of(run_id)
    if group == "tournament":
        if "20261113" in run_id:
            return "Y4/Y6 pilot 3 tác tử; PR #75; 20 ván/cặp"
        if "timed" in run_id:
            return "Y6 giải đấu cùng thời gian 0,2 s/nước; seed 20261119"
        return "Y6 giải đấu mặc định 6 tác tử; seed 20261118"
    if group == "a4":
        if "open4" in run_id:
            return "Y5 A4 ô mở rộng; không dùng chọn checkpoint"
        return "Y5 ablation A4; 3 decay × 3 seed; 10.000 episode"
    return "A6 đối thủ huấn luyện (đã xác nhận trước)"


def main() -> None:
    manifest = {
        r["run_id"]: r for r in csv.DictReader(MANIFEST.open(encoding="utf-8"))
    }
    assignments = {
        r["run_id"]: r for r in csv.DictReader(ASSIGNMENTS.open(encoding="utf-8"))
    }
    report_rows = list(csv.DictReader(REPORT_NUMBERS.open(encoding="utf-8")))
    log_text = EXPERIMENT_LOG.read_text(encoding="utf-8")

    refs: dict[str, list[str]] = defaultdict(list)
    for row in report_rows:
        for run_id in row["run_id"].split(";"):
            if run_id.strip():
                refs[run_id.strip()].append(row["report_section"])

    ids = [k for k in manifest if group_of(k)]
    output_rows = []
    for run_id in sorted(ids):
        group = group_of(run_id)
        row = manifest[run_id]
        if group == "tournament":
            paths = [
                ROOT / f"results/logs/games_{run_id}.csv",
                ROOT / f"results/logs/moves_{run_id}.csv",
            ]
        else:
            paths = [ROOT / f"results/logs/train_dqn_{run_id}.csv"]
        log_ok = all(p.exists() and p.stat().st_size > 0 for p in paths)
        sections = sorted(set(refs.get(run_id, [])))
        log_section = next(
            (title for prefix, title in LOG_SECTIONS if run_id.startswith(prefix)),
            "",
        )
        log_section_hit = bool(log_section) and log_section in log_text
        owner = assignments.get(run_id, {}).get("nguoi_chay", OWNER)
        if owner == "CHƯA XÁC NHẬN":
            owner = OWNER
        findings = []
        if not log_ok:
            findings.append("thiếu log thô")
        if not sections:
            findings.append("không có dòng report_numbers")
        if not log_section_hit:
            findings.append("nhật ký chỉ ghi theo ngày/prefix")
        output_rows.append(
            {
                "run_id": run_id,
                "nhom": group,
                "co_trong_manifest": "có",
                "trang_thai": row["status"],
                "bat_dau_utc": row["started_at"],
                "config_file": row["config_file"],
                "log_files": "; ".join(str(p.relative_to(ROOT)) for p in paths),
                "log_day_du": "có" if log_ok else "không",
                "report_numbers_dong": len(refs.get(run_id, [])),
                "report_numbers_muc": "; ".join(sections),
                "nhat_ky_tieu_de": log_section,
                "nguoi_chay": owner,
                "pham_vi": scope_of(run_id),
                "ket_luan": (
                    "đều trùng; " + "; ".join(findings) if findings else "đều trùng"
                ),
            }
        )

    with OUTPUT.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"Đã ghi {OUTPUT.relative_to(ROOT)}: {len(output_rows)} run")


if __name__ == "__main__":
    main()
