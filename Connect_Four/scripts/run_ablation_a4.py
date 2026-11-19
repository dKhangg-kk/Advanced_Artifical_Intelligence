#!/usr/bin/env python3
"""Chay ablation A4: anh huong cua epsilon decay va so episode len DQN (Y5).

Moi o thi nghiem = (muc decay, seed). Script huan luyen DQN gap Heuristic,
luu checkpoint o cac moc trong ``configs/ablation_a4_dqn_training.yaml``, roi
danh gia tung moc bang vong choi rieng (khong dung giai dau cuoi):

* 100 van voi Random, seed validation 20261102 (50 khai cuoc x 2 ben);
* 100 van voi Heuristic, seed validation 20261103.

Hai seed validation khac seed giai dau chinh thuc (20261118, 20261119), nen
viec chon moc checkpoint khong nhin thay van danh gia cuoi.

Chay tu ``Connect_Four/``:

    # mot o (de chay song song nhieu tien trinh)
    PYTHONPATH=src python scripts/run_ablation_a4.py --decay default_decay --seed 0
    # o mo rong sau chan doan (huan luyen voi 4 nuoc khai cuoc ngau nhien, KHONG nam trong A4 goc)
    PYTHONPATH=src python scripts/run_ablation_a4.py --decay default_decay --seed 0 --opening-plies 4
    # gop moi o da chay thanh bang tong hop
    PYTHONPATH=src python scripts/run_ablation_a4.py --merge
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from connect_four.evaluation.match import MatchConfig, play_match  # noqa: E402
from connect_four.evaluation.metrics import wilson_interval  # noqa: E402
from connect_four.evaluation.runlog import (  # noqa: E402
    ABLATION_FIELDS,
    append_manifest,
    make_manifest_row,
    write_csv,
)

CONFIG = Path("configs/ablation_a4_dqn_training.yaml")
VALIDATION_SEEDS = {"random": 20261102, "heuristic": 20261103}
CELL_DIR = Path("results/logs")
TABLE_PATH = Path("results/tables/ablation_a4_results.csv")
TABLE_FIELDS = (
    "run_id",
    "config_id",
    "decay",
    "opening_plies",
    "seed",
    "episode",
    "epsilon_at_milestone",
    "train_mean_reward_last500",
    "train_win_rate_last500",
    "train_mean_loss_last500",
    "optimizer_updates",
    "training_elapsed_seconds",
    "opponent",
    "games",
    "wins",
    "draws",
    "losses",
    "score",
    "score_ci95_low",
    "score_ci95_high",
    "validation_seed",
    "checkpoint_json",
    "training_log",
)


def _load_config() -> dict[str, Any]:
    import yaml

    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def _training_window(log_path: Path, episode: int, window: int = 500) -> dict[str, float]:
    rows = []
    with log_path.open(encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            ep = int(row["episode"])
            if episode - window < ep <= episode:
                rows.append(row)
    n = len(rows)
    rewards = [float(r["reward"]) for r in rows]
    losses = [float(r["mean_loss"]) for r in rows]
    return {
        "train_mean_reward_last500": sum(rewards) / n,
        "train_win_rate_last500": sum(r > 0 for r in rewards) / n,
        "train_mean_loss_last500": sum(losses) / n,
    }


def _evaluate(checkpoint: Path, opponent: str, games: int) -> dict[str, Any]:
    from connect_four.agents import make_agent

    seed = VALIDATION_SEEDS[opponent]
    dqn = make_agent("dqn", checkpoint=checkpoint, epsilon=0.0, seed=seed)
    opp = make_agent(opponent, seed=seed + 1)
    records = play_match(
        dqn, opp, MatchConfig(games_per_pair=games, openings=(games + 1) // 2, seed=seed),
        name_a="dqn", name_b=opponent,
    )
    wins = sum(r.winner == 1 for r in records)
    draws = sum(r.winner is None for r in records)
    losses = sum(r.winner == 2 for r in records)
    low, high = wilson_interval(wins + 0.5 * draws, games)
    low, high = max(0.0, low), min(1.0, high)
    return {
        "opponent": opponent,
        "games": games,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "score": (wins + 0.5 * draws) / games,
        "score_ci95_low": low,
        "score_ci95_high": high,
        "validation_seed": seed,
    }


def run_cell(decay_name: str, seed: int, opening_plies: int = 0) -> Path:
    import torch

    torch.set_num_threads(1)
    from connect_four.training.train_dqn import train_dqn

    cfg = _load_config()
    decays = {item["name"]: item for item in cfg["epsilon_decay_configs"]}
    if decay_name not in decays:
        raise SystemExit(f"Khong co muc decay {decay_name!r}; co {sorted(decays)}")
    if seed not in cfg["seeds"]:
        raise SystemExit(f"Seed {seed} khong nam trong {cfg['seeds']}")
    decay = decays[decay_name]
    milestones = list(cfg["milestones"])
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    config_id = decay_name + (f"_open{opening_plies}" if opening_plies else "")
    run_id = f"a4-{config_id}-s{seed}-{stamp}"
    out_dir = Path("checkpoints/level6_dqn/a4") / f"{config_id}_s{seed}"
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    train_dqn(
        episodes=max(milestones),
        opponent="heuristic",
        lr=1e-3,
        gamma=0.99,
        epsilon_start=1.0,
        epsilon_min=float(decay["eps_min"]),
        epsilon_decay=float(decay["decay"]),
        buffer_size=100_000,
        batch_size=64,
        target_update_freq=500,
        checkpoint_milestones=milestones,
        out_dir=out_dir,
        log_dir="results/logs",
        seed=seed,
        device="cpu",
        run_id=run_id,
        opening_plies=opening_plies,
    )
    log_path = Path("results/logs") / f"train_dqn_{run_id}.csv"

    table_rows: list[dict[str, Any]] = []
    long_rows: list[dict[str, Any]] = []
    games = int(cfg["eval_games_per_milestone"])
    for episode in milestones:
        ckpt = out_dir / f"dqn_model_ep{episode:06d}.pt"
        meta = json.loads(ckpt.with_suffix(".json").read_text(encoding="utf-8"))
        window = _training_window(log_path, episode)
        for opponent in cfg["opponents"]:
            result = _evaluate(ckpt, opponent, games)
            row = {
                "run_id": run_id,
                "config_id": config_id,
                "decay": decay["decay"],
                "opening_plies": opening_plies,
                "seed": seed,
                "episode": episode,
                "epsilon_at_milestone": meta["epsilon"],
                "optimizer_updates": meta["optimizer_updates"],
                "training_elapsed_seconds": meta["training_elapsed_seconds"],
                "checkpoint_json": str(ckpt.with_suffix(".json")),
                "training_log": str(log_path),
                **window,
                **result,
            }
            table_rows.append(row)
            for metric in ("score", "wins", "draws", "losses", "score_ci95_low", "score_ci95_high"):
                long_rows.append(
                    {
                        "run_id": run_id,
                        "experiment": "A4",
                        "config_id": f"{config_id}@ep{episode}",
                        "seed": seed,
                        "param_name": "epsilon_decay",
                        "param_value": decay["decay"],
                        "metric": f"val_{opponent}_{metric}",
                        "value": result[metric],
                        "raw_log_path": str(log_path),
                    }
                )
            print(
                f"{config_id} s{seed} ep{episode} vs {opponent}: "
                f"{result['wins']}-{result['draws']}-{result['losses']} score={result['score']:.3f}",
                flush=True,
            )
        for metric in ("train_mean_reward_last500", "train_win_rate_last500", "train_mean_loss_last500"):
            long_rows.append(
                {
                    "run_id": run_id,
                    "experiment": "A4",
                    "config_id": f"{config_id}@ep{episode}",
                    "seed": seed,
                    "param_name": "epsilon_decay",
                    "param_value": decay["decay"],
                    "metric": metric,
                    "value": window[metric],
                    "raw_log_path": str(log_path),
                }
            )

    cell_table = CELL_DIR / f"ablation_a4_cell_{run_id}.csv"
    write_csv(cell_table, TABLE_FIELDS, table_rows)
    long_path = CELL_DIR / f"ablation_{run_id}.csv"
    write_csv(long_path, ABLATION_FIELDS, long_rows)
    append_manifest(
        CELL_DIR / "run_manifest.csv",
        make_manifest_row(
            run_id,
            config_file=CONFIG,
            command=(f"PYTHONPATH=src python scripts/run_ablation_a4.py --decay {decay_name} --seed {seed}"
                     + (f" --opening-plies {opening_plies}" if opening_plies else "")),
            seed=seed,
            status="completed",
            notes=(
                f"{'A4-ext (sau chan doan, KHONG thuoc A4 goc)' if opening_plies else 'A4'} DQN; decay={decay['decay']}; "
                f"opening_plies={opening_plies}; episodes={max(milestones)} vs heuristic; "
                f"validation seeds random={VALIDATION_SEEDS['random']}, heuristic={VALIDATION_SEEDS['heuristic']}; "
                f"{games} games/opponent/milestone; train_log={log_path}; ablation_log={long_path}"
            ),
            started_at=started_at,
            finished_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            cwd=Path.cwd(),
        ),
    )
    return cell_table


def merge() -> Path:
    cells = sorted(CELL_DIR.glob("ablation_a4_cell_*.csv"))
    rows: list[dict[str, str]] = []
    for path in cells:
        with path.open(encoding="utf-8") as stream:
            rows.extend(csv.DictReader(stream))
    order = {"fast_decay": 0, "default_decay": 1, "slow_decay": 2, "default_decay_open4": 3}
    for r in rows:
        r.setdefault("opening_plies", "0")  # cac o A4 goc chay truoc khi co tham so nay
    rows.sort(key=lambda r: (order.get(r["config_id"], 9), int(r["seed"]), int(r["episode"]), r["opponent"]))
    write_csv(TABLE_PATH, TABLE_FIELDS, rows)
    print(f"merged {len(cells)} cells, {len(rows)} rows -> {TABLE_PATH}")
    return TABLE_PATH


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--decay", help="fast_decay | default_decay | slow_decay")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--opening-plies", type=int, default=0,
                        help="so nuoc ngau nhien dat truoc moi episode luc huan luyen (mo rong sau chan doan)")
    parser.add_argument("--merge", action="store_true")
    args = parser.parse_args(argv)
    if args.merge:
        merge()
        return 0
    if args.decay is None or args.seed is None:
        parser.error("can --decay va --seed, hoac --merge")
    started = time.perf_counter()
    path = run_cell(args.decay, args.seed, args.opening_plies)
    print(f"cell done in {time.perf_counter() - started:.0f}s -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
