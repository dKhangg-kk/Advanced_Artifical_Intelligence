#!/usr/bin/env python3
"""Them cac dong cua Y (Y5, Y6) vao ``results/tables/report_numbers.csv``.

Moi con so Chuong 4 do Y viet (4.1-4.5 va so lieu loi the di truoc cho 4.7) co mot
dong truy nguoc ve file log/bang nguon va ``run_id``. Script chi doc cac bang va
log da sinh ra tu log tho (``summarize_tournament.py``, ``summarize_a4.py``,
``run_ablation_a4.py``, ``freeze_dqn_checkpoint.py``); khong tu tinh lai ket
qua thi dau.

Chay lai nhieu lan an toan: cac dong thuoc nhom ``report_section`` do script nay
quan ly se bi thay moi, moi dong khac (cua Duc, Khang, Kiet) giu nguyen.

    PYTHONPATH=src python scripts/build_report_numbers_y.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
import re
import statistics
import sys

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from connect_four.evaluation.runlog import REPORT_NUMBER_FIELDS  # noqa: E402

REPORT = Path("results/tables/report_numbers.csv")
TABLES = Path("results/tables")
LOGS = Path("results/logs")
MODES = {"default": "mặc định", "timed": "cùng thời gian 0,2 giây/nước"}
OWNED_PREFIXES = (
    "4.1 environment-y6",
    "4.2 tournament-",
    "4.3 latency-",
    "4.4 dqn",
    "4.5 a4-dqn",
    "4.7 first-move-",
)


def fmt(value: float | int | str, digits: int = 4) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, int):
        return str(value)
    return f"{value:.{digits}f}".rstrip("0").rstrip(".") if value != int(value) else str(int(value))


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def row(section, metric, value, unit, typ, source_type, source_path, source_filter, formula, run_id):
    return {
        "report_section": section, "metric": metric, "value": fmt(value), "unit": unit, "type": typ,
        "source_type": source_type, "source_path": str(source_path), "source_filter": source_filter,
        "formula": formula, "run_id": run_id,
    }


def prefix_of(run_id: str) -> str:
    match = re.match(r"(tournament-(?:default|timed)-\d{8}T\d{6}Z-s\d+)-", run_id)
    if not match:
        raise ValueError(f"run_id giai dau khong dung mau: {run_id}")
    return match.group(1)


def tournament_rows(mode: str) -> list[dict[str, str]]:
    pairs = read(TABLES / f"y6_{mode}_pair_summary.csv")
    agents = read(TABLES / f"y6_{mode}_agent_summary.csv")
    firsts = read(TABLES / f"y6_{mode}_first_move.csv")
    prefix = prefix_of(pairs[0]["run_id"])
    out: list[dict[str, str]] = []
    sec_pair, sec_lat, sec_first = f"4.2 tournament-{mode}", f"4.3 latency-{mode}", f"4.7 first-move-{mode}"
    for p in pairs:
        a, b, n = p["agent_a"], p["agent_b"], int(p["games"])
        src, rid, flt = p["source_games"], p["run_id"], f"pair={a}_vs_{b}"
        out += [
            row(sec_pair, f"{a}_wins_vs_{b}", int(p["wins_a"]), "games", "measured", "games_log", src, f"{flt}; winner=a", "count(winner=a)", rid),
            row(sec_pair, f"draws_{a}_vs_{b}", int(p["draws"]), "games", "measured", "games_log", src, f"{flt}; winner=draw", "count(winner=draw)", rid),
            row(sec_pair, f"{b}_wins_vs_{a}", int(p["wins_b"]), "games", "measured", "games_log", src, f"{flt}; winner=b", "count(winner=b)", rid),
            row(sec_pair, f"score_{a}_vs_{b}", float(p["score_a"]), "ratio", "derived", "games_log", src, f"{flt}; n={n}", "(W + 0.5*D) / N", rid),
            row(sec_pair, f"wilson95_low_{a}_vs_{b}", float(p["score_ci95_low"]), "ratio", "derived", "games_log", src, f"{flt}; n={n}", "Wilson 95% (z=1.96) tren W+0.5D, cat vao [0,1]", rid),
            row(sec_pair, f"wilson95_high_{a}_vs_{b}", float(p["score_ci95_high"]), "ratio", "derived", "games_log", src, f"{flt}; n={n}", "Wilson 95% (z=1.96) tren W+0.5D, cat vao [0,1]", rid),
        ]
    for ag in agents:
        name = ag["agent"]
        src = str(TABLES / f"y6_{mode}_agent_summary.csv")
        flt = f"agent={name}; gop moi cap trong giai dau {mode}"
        out += [
            row(sec_lat, f"{name}_mean_ms_per_move", float(ag["mean_ms_per_move"]), "ms", "derived", "table", src, flt, "mean(time_ms) tren moi nuoc cua tac tu (moves_<run_id>.csv)", prefix),
            row(sec_lat, f"{name}_p95_ms_per_move", float(ag["p95_ms_per_move"]), "ms", "derived", "table", src, flt, "percentile95(time_ms)", prefix),
            row(sec_lat, f"{name}_max_ms_per_move", float(ag["max_ms_per_move"]), "ms", "derived", "table", src, flt, "max(time_ms)", prefix),
            row(sec_lat, f"{name}_mean_nodes_per_move", float(ag["mean_nodes_per_move"]), "nodes", "derived", "table", src, flt, "mean(nodes)", prefix),
            row(sec_lat, f"{name}_mean_simulations_per_move", float(ag["mean_simulations_per_move"]), "simulations", "derived", "table", src, flt, "mean(simulations)", prefix),
            row(sec_lat, f"{name}_games_with_over_budget_move", int(ag["over_budget_games"]), "games", "derived", "table", src, flt, "sum(over_budget_<side>) tren cac van", prefix),
            row(sec_lat, f"{name}_overall_score", float(ag["score"]), "ratio", "derived", "table", src, f"{flt}; N={ag['games']}", "(W + 0.5*D) / N", prefix),
        ]
    for fm in firsts:
        tag = "ALL" if fm["agent_a"] == "ALL" else f"{fm['agent_a']}_vs_{fm['agent_b']}"
        src = str(TABLES / f"y6_{mode}_first_move.csv")
        rid = prefix if fm["agent_a"] == "ALL" else fm["run_id"]
        flt = f"pair={tag}; n={fm['games']}"
        out += [
            row(sec_first, f"first_player_wins_{tag}", int(fm["first_player_wins"]), "games", "derived", "table", src, flt, "count(winner == ben di truoc), ben di truoc theo a_starts", rid),
            row(sec_first, f"second_player_wins_{tag}", int(fm["second_player_wins"]), "games", "derived", "table", src, flt, "count(winner == ben di sau)", rid),
            row(sec_first, f"first_player_score_{tag}", float(fm["first_player_score"]), "ratio", "derived", "table", src, flt, "(W_first + 0.5*D) / N", rid),
            row(sec_first, f"first_player_wilson95_low_{tag}", float(fm["first_player_score_ci95_low"]), "ratio", "derived", "table", src, flt, "Wilson 95%", rid),
            row(sec_first, f"first_player_wilson95_high_{tag}", float(fm["first_player_score_ci95_high"]), "ratio", "derived", "table", src, flt, "Wilson 95%", rid),
        ]
    # Phan cung va cau hinh cua lan chay (4.1): doc tu run_manifest.csv.
    manifest = [r for r in read(LOGS / "run_manifest.csv") if r["run_id"].startswith(prefix)]
    if manifest:
        m = manifest[0]
        for key, unit in (("cpu", "text"), ("ram_gb", "GB"), ("os", "text"), ("python_version", "text"),
                          ("torch_version", "text"), ("git_commit", "text")):
            out.append(row("4.1 environment-y6", f"{mode}_{key}", m[key] or "khong ghi", unit, "observed",
                           "manifest", LOGS / "run_manifest.csv", f"run_id={m['run_id']}", f"cot {key}", m["run_id"]))
        out.append(row("4.1 environment-y6", f"{mode}_pairs", len(pairs), "pairs", "measured", "table",
                       TABLES / f"y6_{mode}_pair_summary.csv", "so dong", "count(cap)", prefix))
        out.append(row("4.1 environment-y6", f"{mode}_total_games", sum(int(p['games']) for p in pairs), "games",
                       "measured", "table", TABLES / f"y6_{mode}_pair_summary.csv", "tat ca cap", "sum(games)", prefix))
        out.append(row("4.1 environment-y6", f"{mode}_games_per_pair", int(pairs[0]["games"]), "games", "measured",
                       "table", TABLES / f"y6_{mode}_pair_summary.csv", "moi cap", "games", prefix))
    return out


def dqn_rows() -> list[dict[str, str]]:
    meta = json.loads(Path("checkpoints/level6_dqn/final.json").read_text(encoding="utf-8"))
    run_id = meta["run_id"]
    train_path = Path(meta["training_log"])
    train = read(train_path)
    out: list[dict[str, str]] = []
    sec = "4.4 dqn"
    src = str(train_path)
    wins = sum(r["result"] == "win" for r in train)
    draws = sum(r["result"] == "draw" for r in train)
    losses = sum(r["result"] == "loss" for r in train)
    out += [
        row(sec, "main_run_episodes", len(train), "episode", "measured", "training_log", src, "all rows", "count(episode)", run_id),
        row(sec, "main_run_wins", wins, "games", "measured", "training_log", src, "result == win", "count(result=win)", run_id),
        row(sec, "main_run_draws", draws, "games", "measured", "training_log", src, "result == draw", "count(result=draw)", run_id),
        row(sec, "main_run_losses", losses, "games", "measured", "training_log", src, "result == loss", "count(result=loss)", run_id),
        row(sec, "main_run_mean_reward", statistics.fmean(float(r["reward"]) for r in train), "reward/episode", "derived", "training_log", src, "all rows", "mean(reward)", run_id),
        row(sec, "main_run_final_epsilon_logged", float(train[-1]["epsilon"]), "epsilon", "measured", "training_log", src, f"episode={train[-1]['episode']}", "epsilon", run_id),
        row(sec, "main_run_optimizer_updates", int(train[-1]["optimizer_updates"]), "update", "measured", "training_log", src, f"episode={train[-1]['episode']}", "optimizer_updates", run_id),
        row(sec, "main_run_training_seconds", sum(float(r["elapsed_seconds"]) for r in train), "seconds", "derived", "training_log", src, "all rows", "sum(elapsed_seconds)", run_id),
    ]
    for lo in range(0, len(train), 1000):
        chunk = train[lo:lo + 1000]
        if len(chunk) < 1000:
            continue
        label = f"episodes_{lo + 1}_{lo + 1000}"
        out += [
            row(sec, f"win_rate_training_{label}", sum(r["result"] == "win" for r in chunk) / len(chunk), "ratio", "derived", "training_log", src, label, "count(result=win)/1000 (doi thu Heuristic, epsilon-greedy)", run_id),
            row(sec, f"mean_reward_training_{label}", statistics.fmean(float(r["reward"]) for r in chunk), "reward/episode", "derived", "training_log", src, label, "mean(reward)", run_id),
            row(sec, f"mean_loss_training_{label}", statistics.fmean(float(r["mean_loss"]) for r in chunk), "loss", "derived", "training_log", src, label, "mean(mean_loss)", run_id),
        ]
    cell = Path(meta["ablation_cell_table"])
    for r in read(cell):
        tag = f"ep{int(r['episode'])}_vs_{r['opponent']}"
        flt = f"episode={r['episode']}; opponent={r['opponent']}; validation seed={r['validation_seed']}"
        out += [
            row(sec, f"validation_wins_{tag}", int(r["wins"]), "games", "measured", "table", cell, flt, "count(winner=dqn) tren 100 van", run_id),
            row(sec, f"validation_draws_{tag}", int(r["draws"]), "games", "measured", "table", cell, flt, "count(draw)", run_id),
            row(sec, f"validation_losses_{tag}", int(r["losses"]), "games", "measured", "table", cell, flt, "count(winner=" + r["opponent"] + ")", run_id),
            row(sec, f"validation_score_{tag}", float(r["score"]), "ratio", "derived", "table", cell, flt, "(W + 0.5*D) / N", run_id),
            row(sec, f"validation_wilson95_low_{tag}", float(r["score_ci95_low"]), "ratio", "derived", "table", cell, flt, "Wilson 95%", run_id),
            row(sec, f"validation_wilson95_high_{tag}", float(r["score_ci95_high"]), "ratio", "derived", "table", cell, flt, "Wilson 95%", run_id),
        ]
    for item in meta["validation"]:
        out.append(row(sec, f"validation_mean_score_ep{item['episode']}", item["mean_validation_score"], "ratio", "derived",
                       "checkpoint_metadata", "checkpoints/level6_dqn/final.json", f"episode={item['episode']}",
                       "(score_vs_random + score_vs_heuristic) / 2", run_id))
    out += [
        row(sec, "selected_episode", meta["selected_episode"], "episode", "derived", "checkpoint_metadata", "checkpoints/level6_dqn/final.json", "selection_rule", meta["selection_rule"], run_id),
        row(sec, "frozen_checkpoint_size", meta["size_bytes"] / 1e6, "MB", "measured", "checkpoint_metadata", "checkpoints/level6_dqn/final.json", "size_bytes", "size_bytes / 1e6", run_id),
        row(sec, "frozen_checkpoint_training_seconds", meta["training_elapsed_seconds_at_checkpoint"], "seconds", "measured", "checkpoint_metadata", "checkpoints/level6_dqn/final.json", "training_elapsed_seconds_at_checkpoint", "thoi gian tu luc bat dau huan luyen den moc duoc chon", run_id),
        row(sec, "frozen_checkpoint_optimizer_updates", meta["optimizer_updates_at_checkpoint"], "update", "measured", "checkpoint_metadata", "checkpoints/level6_dqn/final.json", "optimizer_updates_at_checkpoint", "optimizer_updates", run_id),
    ]
    return out


def a4_rows() -> list[dict[str, str]]:
    summary = read(TABLES / "ablation_a4_summary.csv")
    results = read(TABLES / "ablation_a4_results.csv")
    runs: dict[str, list[str]] = {}
    for r in results:
        runs.setdefault(r["config_id"], [])
        if r["run_id"] not in runs[r["config_id"]]:
            runs[r["config_id"]].append(r["run_id"])
    out: list[dict[str, str]] = []
    sec = "4.5 a4-dqn"
    src = str(TABLES / "ablation_a4_summary.csv")
    for s in summary:
        tag = f"{s['config_id']}_ep{s['episode']}_vs_{s['opponent']}"
        flt = f"config={s['config_id']}; decay={s['decay']}; episode={s['episode']}; opponent={s['opponent']}; seeds={s['seeds']}"
        rid = ";".join(runs[s["config_id"]])
        out += [
            row(sec, f"score_mean_{tag}", float(s["score_mean"]), "ratio", "derived", "table", src, flt, "mean(score) tren cac seed", rid),
            row(sec, f"score_sd_{tag}", float(s["score_sd"]), "ratio", "derived", "table", src, flt, "do lech chuan mau cua score giua cac seed", rid),
            row(sec, f"score_min_{tag}", float(s["score_min"]), "ratio", "derived", "table", src, flt, "min(score) tren cac seed", rid),
            row(sec, f"score_max_{tag}", float(s["score_max"]), "ratio", "derived", "table", src, flt, "max(score) tren cac seed", rid),
        ]
    # Thong ke huan luyen theo cau hinh o moc cuoi (10.000) - khong phu thuoc doi thu.
    seen: set[tuple[str, str]] = set()
    for s in summary:
        key = (s["config_id"], s["episode"])
        if key in seen:
            continue
        seen.add(key)
        flt = f"config={s['config_id']}; episode={s['episode']}; seeds={s['seeds']}"
        rid = ";".join(runs[s["config_id"]])
        out += [
            row(sec, f"epsilon_at_{s['config_id']}_ep{s['episode']}", float(s["epsilon_at_milestone"]), "epsilon", "derived", "table", src, flt, "mean(epsilon_at_milestone)", rid),
            row(sec, f"train_win_rate_last500_{s['config_id']}_ep{s['episode']}", float(s["train_win_rate_last500"]), "ratio", "derived", "table", src, flt, "ty le thang trong 500 episode huan luyen cuoi (epsilon-greedy, doi thu Heuristic), trung binh seed", rid),
            row(sec, f"train_mean_reward_last500_{s['config_id']}_ep{s['episode']}", float(s["train_mean_reward_last500"]), "reward/episode", "derived", "table", src, flt, "mean(reward) 500 episode cuoi, trung binh seed", rid),
            row(sec, f"training_seconds_{s['config_id']}_ep{s['episode']}", float(s["training_elapsed_seconds_mean"]), "seconds", "derived", "table", src, flt, "mean(training_elapsed_seconds) tren cac seed", rid),
        ]
    return out


def main() -> int:
    rows = list(csv.DictReader(REPORT.open(encoding="utf-8")))
    kept = [r for r in rows if not r["report_section"].startswith(OWNED_PREFIXES)]
    new: list[dict[str, str]] = []
    for mode in MODES:
        if (TABLES / f"y6_{mode}_pair_summary.csv").exists():
            new += tournament_rows(mode)
    if Path("checkpoints/level6_dqn/final.json").exists():
        new += dqn_rows()
    if (TABLES / "ablation_a4_summary.csv").exists():
        new += a4_rows()
    with REPORT.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(REPORT_NUMBER_FIELDS), lineterminator="\n")
        writer.writeheader()
        writer.writerows(kept + new)
    print(f"giu {len(kept)} dong cu, them {len(new)} dong moi -> {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
