#!/usr/bin/env python3
"""Tong hop A3 nhieu seed va win rate doi khang CNN -> bang + report_numbers.

Chay tu ``Connect_Four/``::

    PYTHONPATH=src python scripts/build_a3_followup_numbers.py

Nguon:
  - ba bang A3 ung voi seed 20261105/06/07;
  - hai log games cua cap CNN(A3 g1332) vs Alpha-Beta va MCTS.

Chi them dong vao report_numbers.csv neu chua co khoa (section, metric), nen
co the chay lai nhieu lan ma khong nhan dong.
"""

from __future__ import annotations

import csv
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results/tables"
REPORT_NUMBERS = TABLES / "report_numbers.csv"
SEED_TABLES = (
    (20261105, "ablation-a3-20261111T150514Z-s20261105", TABLES / "ablation_a3_results.csv"),
    (20261106, "ablation-a3-20261126T155229Z-s20261106", TABLES / "ablation_a3_results_s20261106.csv"),
    (20261107, "ablation-a3-20261126T160159Z-s20261107", TABLES / "ablation_a3_results_s20261107.csv"),
)
METRICS = {
    "top1_accuracy": ("top1", "percent"),
    "test_loss": ("test_loss", "loss"),
    "win_now_situation_accuracy": ("win_now_tactical", "percent"),
    "block_situation_accuracy": ("block_tactical", "percent"),
    "center_control_top1_accuracy": ("center_top1", "percent"),
}
T_CRITICAL_95_DF2 = 4.302652729911275
Z_95 = 1.959963984540054


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def _write(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _mean_ci(values: list[float]) -> tuple[float, float, float]:
    mean = statistics.fmean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    half = T_CRITICAL_95_DF2 * sd / math.sqrt(len(values))
    return mean, sd, half


def _wilson(wins: int, draws: int, total: int) -> tuple[float, float]:
    score = (wins + 0.5 * draws) / total
    denominator = 1 + Z_95**2 / total
    centre = (score + Z_95**2 / (2 * total)) / denominator
    half = (
        Z_95
        * math.sqrt(score * (1 - score) / total + Z_95**2 / (4 * total**2))
        / denominator
    )
    return centre - half, centre + half


def _multiseed() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    by_seed = [
        {int(row["train_games"]): row for row in _read(path)}
        for _, _, path in SEED_TABLES
    ]
    sizes = sorted(by_seed[0])
    summary_rows: list[dict[str, object]] = []
    number_rows: list[dict[str, object]] = []
    run_ids = ";".join(ablation_id for _, ablation_id, _ in SEED_TABLES)
    seeds = ";".join(str(seed) for seed, _, _ in SEED_TABLES)
    sources = ";".join(str(path.relative_to(ROOT)) for _, _, path in SEED_TABLES)
    for size in sizes:
        for column, (prefix, unit) in METRICS.items():
            values = [float(table[size][column]) for table in by_seed]
            scale = 100.0 if unit == "percent" else 1.0
            mean, sd, half = _mean_ci(values)
            summary_rows.append(
                {
                    "train_games": size,
                    "metric": column,
                    "seed_values": ";".join(f"{value * scale:.4f}" for value in values),
                    "mean": f"{mean * scale:.4f}",
                    "sd": f"{sd * scale:.4f}",
                    "ci95_low": f"{(mean - half) * scale:.4f}",
                    "ci95_high": f"{(mean + half) * scale:.4f}",
                    "n_seeds": len(values),
                    "seeds": seeds,
                }
            )
            base = f"a3_multiseed_{prefix}_{size}"
            for suffix, value in (
                ("mean", mean * scale),
                ("sd", sd * scale),
                ("ci95_low", (mean - half) * scale),
                ("ci95_high", (mean + half) * scale),
            ):
                number_rows.append(
                    {
                        "report_section": "4.5 multiseed",
                        "metric": f"{base}_{suffix}",
                        "value": f"{value:.4f}",
                        "unit": unit,
                        "type": "derived",
                        "source_type": "table",
                        "source_path": sources,
                        "source_filter": f"games={size}; seeds={seeds}",
                        "formula": f"mean/sd/t95(CI) over {len(values)} seeds",
                        "run_id": run_ids,
                    }
                )
    # Paired gain 250 -> 1332, one difference per seed.
    for column, (prefix, unit) in METRICS.items():
        gains = [
            (float(table[1332][column]) - float(table[250][column]))
            for table in by_seed
        ]
        scale = 100.0 if unit == "percent" else 1.0
        mean, sd, half = _mean_ci(gains)
        summary_rows.append(
            {
                "train_games": "250->1332",
                "metric": f"gain_{column}",
                "seed_values": ";".join(f"{value * scale:.4f}" for value in gains),
                "mean": f"{mean * scale:.4f}",
                "sd": f"{sd * scale:.4f}",
                "ci95_low": f"{(mean - half) * scale:.4f}",
                "ci95_high": f"{(mean + half) * scale:.4f}",
                "n_seeds": len(gains),
                "seeds": seeds,
            }
        )
        base = f"a3_multiseed_gain_{prefix}_250_1332"
        for suffix, value in (
            ("mean", mean * scale),
            ("ci95_low", (mean - half) * scale),
            ("ci95_high", (mean + half) * scale),
        ):
            number_rows.append(
                {
                    "report_section": "4.5 multiseed",
                    "metric": f"{base}_{suffix}",
                    "value": f"{value:.4f}",
                    "unit": "percentage_points" if unit == "percent" else unit,
                    "type": "derived",
                    "source_type": "table",
                    "source_path": sources,
                    "source_filter": f"games=1332 minus 250; seeds={seeds}",
                    "formula": f"mean/t95(CI) of paired differences over {len(gains)} seeds",
                    "run_id": run_ids,
                }
            )
    return summary_rows, number_rows


def _head_to_head() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    pairs = (
        ("alphabeta", "results/logs/games_nn-vs-alphabeta-20261126T161238Z-s20261105.csv"),
        ("mcts", "results/logs/games_nn-vs-mcts-20261126T161300Z-s20261105.csv"),
    )
    rows: list[dict[str, object]] = []
    numbers: list[dict[str, object]] = []
    for opponent, rel in pairs:
        games = _read(ROOT / rel)
        wins = sum(row["winner"] == "a" for row in games)
        draws = sum(row["winner"] in {"", "draw"} for row in games)
        losses = sum(row["winner"] == "b" for row in games)
        total = len(games)
        score = (wins + 0.5 * draws) / total
        low, high = _wilson(wins, draws, total)
        run_id = Path(rel).stem.removeprefix("games_")
        row = {
            "opponent": opponent,
            "checkpoint_a": "checkpoints/level5_cnn/a3_g1332.pt",
            "settings": "alphabeta depth=5" if opponent == "alphabeta" else "mcts simulations=1000",
            "games": total,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "score_a": f"{score:.4f}",
            "wilson95_low": f"{low:.4f}",
            "wilson95_high": f"{high:.4f}",
            "games_log": rel,
            "run_id": run_id,
        }
        rows.append(row)
        for metric, value in (
            ("wins", wins),
            ("draws", draws),
            ("losses", losses),
            ("score", score),
            ("wilson95_low", low),
            ("wilson95_high", high),
        ):
            numbers.append(
                {
                    "report_section": "4.5 cnn-a3",
                    "metric": f"a3_g1332_vs_{opponent}_{metric}",
                    "value": f"{value:.4f}",
                    "unit": "games" if metric in {"wins", "draws", "losses"} else "ratio",
                    "type": "measured" if metric in {"wins", "draws", "losses"} else "derived",
                    "source_type": "log",
                    "source_path": rel,
                    "source_filter": "all games; CNN=a3_g1332",
                    "formula": "count(winner=A/B/draw)" if metric in {"wins", "draws", "losses"} else ("(W+0.5D)/N" if metric == "score" else "Wilson 95%"),
                    "run_id": run_id,
                }
            )
    return rows, numbers


def _append_numbers(new_rows: list[dict[str, object]]) -> None:
    with REPORT_NUMBERS.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = list(reader.fieldnames or [])
        existing = {(row["report_section"], row["metric"]) for row in reader}
    additions = [
        row
        for row in new_rows
        if (row["report_section"], row["metric"]) not in existing
    ]
    if additions:
        with REPORT_NUMBERS.open("a", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
            writer.writerows(additions)
    print(f"report_numbers: them {len(additions)} dong (bo qua {len(new_rows) - len(additions)} dong co san)")


def main() -> None:
    multiseed, multiseed_numbers = _multiseed()
    h2h, h2h_numbers = _head_to_head()
    _write(
        TABLES / "ablation_a3_multiseed_summary.csv",
        ["train_games", "metric", "seed_values", "mean", "sd", "ci95_low", "ci95_high", "n_seeds", "seeds"],
        multiseed,
    )
    _write(
        TABLES / "cnn_a3_head_to_head.csv",
        ["opponent", "checkpoint_a", "settings", "games", "wins", "draws", "losses", "score_a", "wilson95_low", "wilson95_high", "games_log", "run_id"],
        h2h,
    )
    _append_numbers(multiseed_numbers + h2h_numbers)
    print(f"Da ghi {len(multiseed)} dong nhieu seed va {len(h2h)} dong doi khang.")


if __name__ == "__main__":
    main()
