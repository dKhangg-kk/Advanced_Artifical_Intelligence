"""Run DQN vs Heuristic and audit Như Ý's historical experiment evidence."""
from __future__ import annotations

import csv
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
except Exception:
    VN_TZ = timezone(timedelta(hours=7))

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "results/logs/run_manifest.csv"
ASSIGNMENTS = ROOT / "results/experiment_assignments.csv"
PLAN = ROOT / "results/experiment_plan.csv"
REPORT_NUMBERS = ROOT / "results/tables/report_numbers.csv"
EXPERIMENT_LOG = ROOT / "docs/EXPERIMENT_LOG.md"
CONTRIBUTION = ROOT / "docs/contributions/phan-le-ngoc-nhu-y.md"
AUDIT_REPORT = ROOT / "results/audit_nhu_y_runs.md"

OWNER = "Phan Lê Ngọc Như Ý"
UNKNOWN = "CHƯA XÁC NHẬN"
TICK = chr(96)
COMMAND = [
    sys.executable, "-m", "connect_four.evaluation.cli",
    "--a", "dqn", "--b", "heuristic", "--openings", "5", "--seed", "2026",
    "--checkpoint-a", "checkpoints/level6_dqn/final.pt",
]


def code(value: str) -> str:
    return TICK + str(value) + TICK


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def matches_assigned_command(row: dict[str, str]) -> bool:
    command = " ".join(row.get("command", "").split())
    return (
        "--a dqn --b heuristic" in command
        and "--openings 5" in command
        and "--seed 2026" in command
        and "--checkpoint-a checkpoints/level6_dqn/final.pt" in command
        and row.get("status") == "completed"
    )


def ensure_experiment() -> dict[str, str]:
    existing = [row for row in read_csv(MANIFEST) if matches_assigned_command(row)]
    if existing:
        if len(existing) != 1:
            raise RuntimeError("Có nhiều hơn một run đã hoàn tất cùng cấu hình DQN–Heuristic.")
        print("Dùng lại run đã hoàn tất:", existing[0]["run_id"])
        return existing[0]

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    print("Chạy thí nghiệm:", " ".join(COMMAND), flush=True)
    subprocess.run(COMMAND, cwd=ROOT, env=env, check=True)
    completed = [row for row in read_csv(MANIFEST) if matches_assigned_command(row)]
    if len(completed) != 1:
        raise RuntimeError(f"Không xác định được duy nhất run mới: {len(completed)}")
    return completed[0]


def note_path(notes: str, key: str) -> Path | None:
    match = re.search(r"(?:^|;\s*)" + re.escape(key) + r"=([^;]+)", notes or "")
    if not match:
        return None
    path = Path(match.group(1).strip())
    return path if path.is_absolute() else ROOT / path


def require_file(path: Path | None, label: str, run_id: str) -> None:
    if path is None or not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"{run_id}: thiếu bằng chứng {label}: {path}")


def validate_old_run(row: dict[str, str]) -> None:
    rid = row["run_id"]
    if row.get("status") != "completed":
        raise RuntimeError(f"{rid}: trạng thái manifest không phải completed")
    notes = row.get("notes", "")
    if rid.startswith("tournament-"):
        keys = ("games_log", "moves_log")
    elif rid.startswith(("a4-", "a6-")):
        keys = ("train_log", "ablation_log")
    else:
        raise RuntimeError(f"Run ngoài phạm vi audit: {rid}")
    for key in keys:
        require_file(note_path(notes, key), key, rid)


def game_summary(run_row: dict[str, str]) -> tuple[int, int, int, float, str, str]:
    games_path = note_path(run_row.get("notes", ""), "games_log")
    moves_path = note_path(run_row.get("notes", ""), "moves_log")
    require_file(games_path, "games_log", run_row["run_id"])
    require_file(moves_path, "moves_log", run_row["run_id"])
    games = read_csv(games_path)
    if len(games) != 10:
        raise RuntimeError(f"Cần đúng 10 ván từ 5 khai cuộc; nhận được {len(games)}.")
    wins = draws = losses = 0
    for game in games:
        winner = (game.get("winner") or "").strip().lower()
        if winner in {"a", "agent_a", "dqn"}:
            wins += 1
        elif winner in {"b", "agent_b", "heuristic"}:
            losses += 1
        elif winner in {"", "draw", "d", "none", "0"}:
            draws += 1
        else:
            raise RuntimeError("Không nhận diện được winner trong games log: " + winner)
    if wins + draws + losses != 10:
        raise RuntimeError("W-D-L không đủ 10 ván.")
    score = (wins + 0.5 * draws) / 10
    return wins, draws, losses, score, str(games_path.relative_to(ROOT)), str(moves_path.relative_to(ROOT))


def update_assignments(manifest: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = read_csv(ASSIGNMENTS)
    fields = list(rows[0].keys()) if rows else ["run_id", "nguoi_chay", "pham_vi"]
    by_id: dict[str, dict[str, str]] = {}
    for row in rows:
        rid = row["run_id"].strip()
        if rid in by_id:
            raise RuntimeError("run_id trùng trong assignments: " + rid)
        by_id[rid] = row

    manifest_ids = [row["run_id"].strip() for row in manifest]
    if len(manifest_ids) != len(set(manifest_ids)):
        raise RuntimeError("run_manifest.csv có run_id trùng.")
    if set(by_id) - set(manifest_ids):
        raise RuntimeError("Assignments chứa run_id không tồn tại trong manifest.")
    missing = [rid for rid in manifest_ids if rid not in by_id]
    unresolved = [row for row in rows if row["nguoi_chay"].strip() == UNKNOWN]
    if unresolved and len(unresolved) != 43:
        raise RuntimeError(f"Số dòng CHƯA XÁC NHẬN bất thường: {len(unresolved)} (dự kiến 43).")

    for row in unresolved:
        rid = row["run_id"].strip()
        if rid.startswith("tournament-"):
            row["nguoi_chay"] = OWNER
            row["pham_vi"] = "Y6 - Giải đấu 6 tác tử"
        elif rid.startswith("a4-"):
            row["nguoi_chay"] = OWNER
            row["pham_vi"] = "Y5 - Ablation A4 DQN"
        else:
            raise RuntimeError("Không thể xác minh người chạy cho run: " + rid)

    for rid in missing:
        source = next(row for row in manifest if row["run_id"].strip() == rid)
        if not matches_assigned_command(source):
            raise RuntimeError("Có run chưa được phân công ngoài nhiệm vụ DQN–Heuristic: " + rid)
        rows.append({
            "run_id": rid,
            "nguoi_chay": OWNER,
            "pham_vi": "DQN cấp 6 vs Heuristic - 5 khai cuộc / 10 ván",
        })

    write_csv(ASSIGNMENTS, rows, fields)
    return rows


def update_plan(run_row: dict[str, str], wdl: tuple[int, int, int, float, str, str], counts: dict[str, int]) -> None:
    rows = read_csv(PLAN)
    fields = list(rows[0].keys())
    date = datetime.now(VN_TZ).strftime("%d/%m/%Y")
    wins, draws, losses, score, games_path, _ = wdl
    for row in rows:
        if row["stt"] == "9":
            row["trang_thai"] = "Đã chạy"
            row["ngay_xong"] = date
            row["ghi_chu"] = (
                f"run_id={run_row['run_id']}; 5 khai cuộc/10 ván; W-D-L={wins}-{draws}-{losses}; "
                f"score_DQN={score:.3f}; log={games_path}"
            )
        elif row["stt"] == "10":
            row["trang_thai"] = "Đã đối chiếu"
            row["ngay_xong"] = date
            row["ghi_chu"] = (
                f"Đối chiếu {counts['total']} run: {counts['tournament']} tournament + "
                f"{counts['a4']} A4 + {counts['a6']} A6; cập nhật 43 người chạy trước đây "
                "CHƯA XÁC NHẬN; file log thô tồn tại; "
                f"{counts['report_missing']} run A4 không có run_id riêng trong report_numbers "
                "(metric đã được tổng hợp ở bảng A4)."
            )
    write_csv(PLAN, rows, fields)


def append_contribution(run_row: dict[str, str], wdl: tuple[int, int, int, float, str, str]) -> None:
    text = CONTRIBUTION.read_text(encoding="utf-8")
    if run_row["run_id"] in text:
        return
    lines = text.splitlines()
    header = next((i for i, line in enumerate(lines) if line.startswith("| Ngày | Việc đã làm")), None)
    if header is None:
        raise RuntimeError("Không tìm thấy bảng Nhật ký trong hồ sơ đóng góp.")
    insert_at = header + 2
    while insert_at < len(lines) and lines[insert_at].startswith("|"):
        insert_at += 1
    wins, draws, losses, score, games_path, _ = wdl
    date = datetime.now(VN_TZ).strftime("%d/%m/%Y")
    lines.insert(insert_at, (
        f"| {date} | Chạy DQN cấp 6 đối đầu Heuristic (5 khai cuộc, 10 ván, seed 2026); "
        "rà soát 49 run A4/A6/giải đấu và hoàn thiện phân công | "
        f"{code(run_row['run_id'])}; {code('results/audit_nhu_y_runs.md')}; "
        f"{code(games_path)} | Chưa ghi nhận |"
    ))
    CONTRIBUTION.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_audit(
    manifest: list[dict[str, str]], assignments: list[dict[str, str]],
    tournament: list[dict[str, str]], a4: list[dict[str, str]], a6: list[dict[str, str]],
    run_row: dict[str, str], wdl: tuple[int, int, int, float, str, str],
    report_missing: list[str],
) -> dict[str, int]:
    counts = {
        "tournament": len(tournament), "a4": len(a4), "a6": len(a6),
        "total": len(tournament) + len(a4) + len(a6),
        "report_missing": len(report_missing),
        "report_linked": 49 - len(report_missing),
    }
    wins, draws, losses, score, games_path, moves_path = wdl
    owner_counts = Counter(row["nguoi_chay"] for row in assignments)
    date = datetime.now(VN_TZ).strftime("%d/%m/%Y")
    lines = [
        "# Biên bản chạy DQN–Heuristic và rà soát bằng chứng của Như Ý", "",
        f"- Ngày kiểm tra: {date} (UTC+7).",
        "- Repository: dKhangg-kk/Advanced_Artifical_Intelligence.",
        "",
        "## 1. Run DQN cấp 6 đối đầu Heuristic", "",
        f"- run_id: {code(run_row['run_id'])}.",
        "- Lệnh: " + code("python -m connect_four.evaluation.cli --a dqn --b heuristic --openings 5 --seed 2026 --checkpoint-a checkpoints/level6_dqn/final.pt") + ".",
        "- Checkpoint: " + code("checkpoints/level6_dqn/final.pt") + ".",
        "- Seed: 2026; 5 khai cuộc × 2 lượt đổi bên = 10 ván.",
        f"- Kết quả DQN: **{wins} thắng – {draws} hòa – {losses} thua**, score = **{score:.3f}**.",
        f"- Log ván: {code(games_path)}.",
        f"- Log nước đi: {code(moves_path)}.",
        "",
        "## 2. Kết quả audit 49 run cũ", "",
        "| Nhóm | Số run | Kiểm tra bằng chứng |",
        "|---|---:|---|",
        f"| Tournament | {counts['tournament']} | Games log và moves log tồn tại; manifest completed |",
        f"| A4 DQN | {counts['a4']} | Train log và ablation log tồn tại; manifest completed |",
        f"| A6 DQN | {counts['a6']} | Train log và ablation log tồn tại; manifest completed |",
        f"| **Tổng** | **{counts['total']}** | **Đã kiểm tra** |",
        "",
        "- Đã gán người thực hiện cho 43/43 dòng CHƯA XÁC NHẬN: 33 tournament và 10 A4.",
        "- Sáu run A6 đã có tên Như Ý từ trước và được giữ nguyên.",
        f"- Tổng manifest sau run mới: {len(manifest)}; tổng assignments: {len(assignments)}.",
        f"- Dòng assignments theo người thực hiện: {dict(owner_counts)}.",
        "- Đối chiếu ID: manifest và assignments khớp một-một; không có ID trùng, thiếu hoặc mồ côi.",
        "",
        "## 3. Đối chiếu report_numbers", "",
        f"- Có {counts['report_linked']}/49 run được dẫn trực tiếp bằng run_id trong results/tables/report_numbers.csv.",
        f"- {len(report_missing)} run A4 không có dòng run_id riêng; log thô vẫn tồn tại và metric A4 được tổng hợp ở bảng kết quả A4.",
        "- Không tự tạo số liệu report_numbers cho run không có dòng nguồn trực tiếp.",
        "",
        "Các run A4 không có run_id riêng trong report_numbers:",
    ]
    lines.extend(f"- {code(rid)}" for rid in report_missing)
    lines.extend(["", "## 4. Danh sách 49 run đã audit", "", "### Tournament (33)"])
    lines.extend(f"- {code(row['run_id'])}" for row in tournament)
    lines.extend(["", "### A4 DQN (10)"])
    lines.extend(f"- {code(row['run_id'])}" for row in a4)
    lines.extend(["", "### A6 DQN (6)"])
    lines.extend(f"- {code(row['run_id'])}" for row in a6)
    lines.extend([
        "", "## 5. Kết luận", "",
        "- Run mới có games log, moves log và manifest; số W-D-L được tính trực tiếp từ games log.",
        "- 49 run cũ trong phạm vi Như Ý đã được kiểm tra file bằng chứng; 43 dòng chưa xác nhận được cập nhật phân công.",
        "- Không chạy lại A4/A6, không sửa checkpoint đã đóng băng và không tạo số liệu báo cáo thay cho nguồn thiếu.",
        "- File Excel được dựng lại từ manifest, assignments và plan bằng scripts/build_experiment_workbook.py.", "",
    ])
    AUDIT_REPORT.write_text("\n".join(lines), encoding="utf-8")

    log = EXPERIMENT_LOG.read_text(encoding="utf-8")
    if run_row["run_id"] not in log:
        wins, draws, losses, score, games_path, moves_path = wdl
        section = f"""

## {run_row['run_id']} — DQN cấp 6 đối đầu Heuristic

- **Ngày:** {date}, giờ Việt Nam (UTC+7).
- **Người thực hiện:** {OWNER} / 3124720079.
- **Loại và mục tiêu:** tournament đối kháng; kiểm chứng checkpoint DQN cấp 6 đã đóng băng khi gặp Heuristic.
- **Lệnh chạy:** {code("python -m connect_four.evaluation.cli --a dqn --b heuristic --openings 5 --seed 2026 --checkpoint-a checkpoints/level6_dqn/final.pt")}.
- **Seed:** 2026; 5 khai cuộc, mỗi khai cuộc đổi bên một lần, tổng cộng 10 ván.
- **Checkpoint:** {code("checkpoints/level6_dqn/final.pt")}.
- **Trạng thái:** completed.
- **Kết quả:** DQN W-D-L = {wins}-{draws}-{losses}; score_A = (W + 0,5 × D) / 10 = {score:.3f}.
- **Log ván:** {code(games_path)}.
- **Log nước đi:** {code(moves_path)}.
- **Run manifest:** {code(run_row['run_id'])}.

## Rà soát phân công 49 run A4/A6/giải đấu — {date}

- Đối chiếu run_manifest.csv với experiment_assignments.csv: run_id khớp một-một; không có ID trùng, thiếu hoặc mồ côi.
- Kiểm tra 49 run thuộc phần DQN/giải đấu của Như Ý: 33 tournament, 10 A4 và 6 A6; tất cả có trạng thái completed và file log thô được tham chiếu đều tồn tại.
- Điền người thực hiện cho 43 dòng trước đó là CHƯA XÁC NHẬN: 33 tournament và 10 A4. Sáu run A6 đã được gán từ trước.
- Đối chiếu report_numbers.csv: {counts['report_linked']} run có run_id được dẫn trực tiếp; {counts['report_missing']} run A4 không có dòng riêng vì metric được tổng hợp ở bảng kết quả A4.
- Biên bản chi tiết: {code("results/audit_nhu_y_runs.md")}.
"""
        EXPERIMENT_LOG.write_text(log.rstrip() + section + "\n", encoding="utf-8")

    return counts


def main() -> None:
    if not MANIFEST.is_file() or not ASSIGNMENTS.is_file():
        raise FileNotFoundError("Thiếu run_manifest.csv hoặc experiment_assignments.csv.")

    run_row = ensure_experiment()
    manifest = read_csv(MANIFEST)
    matching = [row for row in manifest if row["run_id"] == run_row["run_id"]]
    if len(matching) != 1:
        raise RuntimeError("Run mới không xuất hiện duy nhất một lần trong manifest.")
    run_row = matching[0]
    wdl = game_summary(run_row)

    tournament = [r for r in manifest if r["run_id"].startswith("tournament-")]
    a4 = [r for r in manifest if r["run_id"].startswith("a4-")]
    a6 = [r for r in manifest if r["run_id"].startswith("a6-")]
    if (len(tournament), len(a4), len(a6)) != (33, 10, 6):
        raise RuntimeError(f"Phân bố run cũ thay đổi: tournament={len(tournament)}, A4={len(a4)}, A6={len(a6)}")
    for row in tournament + a4 + a6:
        validate_old_run(row)

    assignments = update_assignments(manifest)
    owner_by_id = {row["run_id"]: row["nguoi_chay"] for row in assignments}
    audited = tournament + a4 + a6
    if any(owner_by_id.get(row["run_id"]) != OWNER for row in audited):
        raise RuntimeError("Sau audit vẫn còn run trong nhóm 49 chưa được gán cho Như Ý.")
    if owner_by_id.get(run_row["run_id"]) != OWNER:
        raise RuntimeError("Run mới chưa được gán cho Như Ý.")

    report_ids = {row.get("run_id", "").strip() for row in read_csv(REPORT_NUMBERS)}
    report_missing = sorted(row["run_id"] for row in audited if row["run_id"] not in report_ids)
    if any(not rid.startswith("a4-") for rid in report_missing):
        raise RuntimeError("Có tournament/A6 thiếu liên kết report_numbers: " + ", ".join(report_missing))

    counts = write_audit(manifest, assignments, tournament, a4, a6, run_row, wdl, report_missing)
    update_plan(run_row, wdl, counts)
    append_contribution(run_row, wdl)

    print(
        f"AUDIT_OK run={run_row['run_id']} W-D-L={wdl[0]}-{wdl[1]}-{wdl[2]} "
        f"score={wdl[3]:.3f}; old_runs=49; assigned_rows=43; "
        f"report_numbers_missing_a4={len(report_missing)}",
        flush=True,
    )


if __name__ == "__main__":
    main()
