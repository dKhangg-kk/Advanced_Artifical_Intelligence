#!/usr/bin/env python3
"""Chay thi nghiem A6 (mo rong cho RQ3): doi thu huan luyen cua DQN (Y5).

Cau hoi: DQN co tu hoc duoc qua tu choi (self-play) khong, va doi thu huan luyen
(Heuristic co dinh, Random co dinh, tu choi) anh huong the nao den nang luc tren
khai cuoc ngau nhien?

* ``random`` va ``selfplay``: moi o = (doi thu, seed), 10.000 episode, cung sieu
  tham so voi o A4 ``default_decay`` (decay 0,9995). Tu choi dung tap 5 ban sao
  dong bang gan nhat cua chinh mang, chep ban moi moi 500 episode.
* ``heuristic``: KHONG chay lai; ``--merge`` dung lai 3 o A4 ``default_decay``.

Danh gia giong het A4 (ham ``_evaluate`` cua ``run_ablation_a4.py``): 4 moc,
100 van voi Random (seed 20261102) va 100 van voi Heuristic (seed 20261103). Them
o moc 10.000: 100 van doi dau truc tiep voi checkpoint giai dau da dong bang
``checkpoints/level6_dqn/final.pt`` (seed 20261104) va do dung tren bo vi tri
``tests/data/positions.csv``.

A6 chay ngay 20/11/2026, SAU khi checkpoint giai dau dong bang (18/11) va sau khi
giai dau chay xong; vi vay A6 khong duoc dung de chon checkpoint hay sua ket qua
muc 4.1-4.3.

Chay tu ``Connect_Four/``:

    PYTHONPATH=src python scripts/run_ablation_a6.py --opponent selfplay --seed 0
    PYTHONPATH=src python scripts/run_ablation_a6.py --opponent random --seed 42
    PYTHONPATH=src python scripts/run_ablation_a6.py --merge
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
for _path in (_ROOT / "src", _ROOT / "scripts"):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from run_ablation_a4 import (  # noqa: E402
    TABLE_FIELDS as A4_TABLE_FIELDS,
    TABLE_PATH as A4_TABLE_PATH,
    VALIDATION_SEEDS,
    _evaluate,
    _training_window,
)

from connect_four.evaluation.match import MatchConfig, play_match  # noqa: E402
from connect_four.evaluation.metrics import wilson_interval  # noqa: E402
from connect_four.evaluation.runlog import (  # noqa: E402
    ABLATION_FIELDS,
    append_manifest,
    make_manifest_row,
    write_csv,
)

CONFIG = Path("configs/ablation_a6_dqn_opponent.yaml")
CELL_DIR = Path("results/logs")
TABLE_PATH = Path("results/tables/ablation_a6_results.csv")
H2H_PATH = Path("results/tables/ablation_a6_head_to_head.csv")
POS_PATH = Path("results/tables/ablation_a6_positions.csv")
POSITIONS = Path("tests/data/positions.csv")
TABLE_FIELDS = ("train_opponent",) + tuple(A4_TABLE_FIELDS)
H2H_FIELDS = (
    "run_id", "train_opponent", "seed", "episode", "opponent_checkpoint", "games",
    "wins", "draws", "losses", "score", "score_ci95_low", "score_ci95_high", "match_seed",
)
POS_FIELDS = ("train_opponent", "seed", "checkpoint", "situation", "positions", "hits", "accuracy")


def _load_config() -> dict[str, Any]:
    import yaml

    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def _head_to_head(checkpoint: Path, cfg: dict[str, Any]) -> dict[str, Any]:
    """100 van DQN(A6) gap DQN dong bang; doi ben moi khai cuoc, khai cuoc ngau nhien."""
    from connect_four.agents import make_agent

    spec = cfg["head_to_head"]
    seed, games = int(spec["seed"]), int(spec["games"])
    learner = make_agent("dqn", checkpoint=checkpoint, epsilon=0.0, seed=seed)
    frozen = make_agent("dqn", checkpoint=Path(spec["checkpoint"]), epsilon=0.0, seed=seed + 1)
    records = play_match(
        learner, frozen, MatchConfig(games_per_pair=games, openings=(games + 1) // 2, seed=seed),
        name_a="dqn_a6", name_b="dqn_frozen",
    )
    wins = sum(r.winner == 1 for r in records)
    draws = sum(r.winner is None for r in records)
    losses = sum(r.winner == 2 for r in records)
    low, high = wilson_interval(wins + 0.5 * draws, games)
    return {
        "opponent_checkpoint": str(spec["checkpoint"]), "games": games, "wins": wins, "draws": draws,
        "losses": losses, "score": (wins + 0.5 * draws) / games,
        "score_ci95_low": max(0.0, low), "score_ci95_high": min(1.0, high), "match_seed": seed,
    }


def _cols(value: str) -> list[int]:
    return [] if value == "-" else [int(x) for x in value.split()]


def position_accuracy(checkpoint: Path) -> dict[str, tuple[int, int]]:
    """So vi tri dung / tong theo loai the (DQN greedy la xac dinh nen chay 1 lan)."""
    from connect_four.agents import make_agent
    from connect_four.game.engine import ConnectFour

    agent = make_agent("dqn", checkpoint=checkpoint, epsilon=0.0, seed=0)
    totals: dict[str, list[int]] = {k: [0, 0] for k in ("win_now", "block", "double_threat", "quiet_legal")}
    with POSITIONS.open(encoding="utf-8", newline="") as stream:
        for position in csv.DictReader(stream):
            game = ConnectFour()
            for column in (int(x) for x in position["moves"].split()):
                game.step(column)
            if game.is_terminal():
                continue
            wins, blocks = _cols(position["winning_moves"]), _cols(position["blocking_moves"])
            action = agent.choose(game.clone())
            if wins:
                key, hit = "win_now", action in wins
            elif blocks:
                key, hit = "block", action in blocks
            else:
                key, hit = "quiet_legal", action in game.legal_actions()
            totals[key][0] += int(hit)
            totals[key][1] += 1
            if position["id"].startswith("double-threat"):
                totals["double_threat"][0] += int(hit)
                totals["double_threat"][1] += 1
    return {k: (v[0], v[1]) for k, v in totals.items()}


def run_cell(train_opponent: str, seed: int) -> Path:
    import torch

    torch.set_num_threads(1)
    from connect_four.training.train_dqn import train_dqn

    cfg = _load_config()
    specs = {item["name"]: item for item in cfg["training_opponents"]}
    if train_opponent not in specs:
        raise SystemExit(f"Khong co doi thu {train_opponent!r}; co {sorted(specs)}")
    if seed not in cfg["seeds"]:
        raise SystemExit(f"Seed {seed} khong nam trong {cfg['seeds']}")
    spec, hp = specs[train_opponent], cfg["hyperparameters"]
    milestones = list(cfg["milestones"])
    config_id = f"opp_{train_opponent}"
    out_dir = Path("checkpoints/level6_dqn/a6") / f"{config_id}_s{seed}"
    run_file = out_dir / "run_in_progress.json"
    previous = json.loads(run_file.read_text(encoding="utf-8")) if run_file.is_file() else None
    final_meta = out_dir / "dqn_model.json"
    training_done = bool(
        previous and final_meta.is_file()
        and json.loads(final_meta.read_text(encoding="utf-8")).get("run_id") == previous["run_id"]
    )
    if previous and (training_done or (out_dir / "resume_state.pt").is_file()):
        # May bi khoi dong lai giua chung: dung lai run_id cu (tiep tuc huan luyen hoac chi danh gia lai).
        run_id, started_at = previous["run_id"], previous["started_at"]
        print(f"tiep tuc {run_id} (huan luyen da xong: {training_done})", flush=True)
    else:
        training_done = False
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_id = f"a6-{config_id}-s{seed}-{stamp}"
        started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        out_dir.mkdir(parents=True, exist_ok=True)
        run_file.write_text(json.dumps({"run_id": run_id, "started_at": started_at}) + "\n", encoding="utf-8")

    extra: dict[str, Any] = {}
    if train_opponent == "selfplay":
        extra = {"selfplay_snapshot_every": int(spec["snapshot_every"]),
                 "selfplay_pool_size": int(spec["pool_size"])}
    if not training_done:
        train_dqn(
            episodes=max(milestones), opponent=train_opponent, lr=float(hp["lr"]), gamma=float(hp["gamma"]),
            epsilon_start=float(hp["epsilon_start"]), epsilon_min=float(hp["epsilon_min"]),
            epsilon_decay=float(hp["epsilon_decay"]), buffer_size=int(hp["buffer_size"]),
            batch_size=int(hp["batch_size"]), target_update_freq=int(hp["target_update_freq"]),
            checkpoint_milestones=milestones, out_dir=out_dir, log_dir="results/logs", seed=seed,
            device="cpu", run_id=run_id, resume_every=250, **extra,
        )
    log_path = Path("results/logs") / f"train_dqn_{run_id}.csv"

    table_rows: list[dict[str, Any]] = []
    long_rows: list[dict[str, Any]] = []
    games = int(cfg["eval_games_per_milestone"])
    for episode in milestones:
        ckpt = out_dir / f"dqn_model_ep{episode:06d}.pt"
        meta = json.loads(ckpt.with_suffix(".json").read_text(encoding="utf-8"))
        window = _training_window(log_path, episode)
        for opponent in cfg["eval_opponents"]:
            result = _evaluate(ckpt, opponent, games)
            table_rows.append({
                "train_opponent": train_opponent, "run_id": run_id, "config_id": config_id,
                "decay": hp["epsilon_decay"], "opening_plies": 0, "seed": seed, "episode": episode,
                "epsilon_at_milestone": meta["epsilon"], "optimizer_updates": meta["optimizer_updates"],
                "training_elapsed_seconds": meta["training_elapsed_seconds"],
                "checkpoint_json": str(ckpt.with_suffix(".json")), "training_log": str(log_path),
                **window, **result,
            })
            for metric in ("score", "wins", "draws", "losses", "score_ci95_low", "score_ci95_high"):
                long_rows.append({
                    "run_id": run_id, "experiment": "A6", "config_id": f"{config_id}@ep{episode}",
                    "seed": seed, "param_name": "train_opponent", "param_value": train_opponent,
                    "metric": f"val_{opponent}_{metric}", "value": result[metric],
                    "raw_log_path": str(log_path),
                })
            print(f"{config_id} s{seed} ep{episode} vs {opponent}: "
                  f"{result['wins']}-{result['draws']}-{result['losses']} score={result['score']:.3f}", flush=True)
        for metric in ("train_mean_reward_last500", "train_win_rate_last500", "train_mean_loss_last500"):
            long_rows.append({
                "run_id": run_id, "experiment": "A6", "config_id": f"{config_id}@ep{episode}", "seed": seed,
                "param_name": "train_opponent", "param_value": train_opponent, "metric": metric,
                "value": window[metric], "raw_log_path": str(log_path),
            })

    last = out_dir / f"dqn_model_ep{max(milestones):06d}.pt"
    h2h = _head_to_head(last, cfg)
    h2h_row = {"run_id": run_id, "train_opponent": train_opponent, "seed": seed,
               "episode": max(milestones), **h2h}
    print(f"{config_id} s{seed} head-to-head vs frozen: {h2h['wins']}-{h2h['draws']}-{h2h['losses']} "
          f"score={h2h['score']:.3f}", flush=True)
    for metric in ("score", "wins", "draws", "losses", "score_ci95_low", "score_ci95_high"):
        long_rows.append({
            "run_id": run_id, "experiment": "A6", "config_id": f"{config_id}@ep{max(milestones)}",
            "seed": seed, "param_name": "train_opponent", "param_value": train_opponent,
            "metric": f"h2h_frozen_{metric}", "value": h2h[metric], "raw_log_path": str(log_path),
        })

    run_file.unlink(missing_ok=True)
    cell_table = CELL_DIR / f"ablation_a6_cell_{run_id}.csv"
    write_csv(cell_table, TABLE_FIELDS, table_rows)
    write_csv(CELL_DIR / f"ablation_a6_h2h_{run_id}.csv", H2H_FIELDS, [h2h_row])
    long_path = CELL_DIR / f"ablation_{run_id}.csv"
    write_csv(long_path, ABLATION_FIELDS, long_rows)
    append_manifest(
        CELL_DIR / "run_manifest.csv",
        make_manifest_row(
            run_id, config_file=CONFIG,
            command=f"PYTHONPATH=src python scripts/run_ablation_a6.py --opponent {train_opponent} --seed {seed}",
            seed=seed, status="completed",
            notes=(f"A6 (mo rong RQ3, sau khi dong bang checkpoint giai dau) DQN; train_opponent={train_opponent}; "
                   f"decay={hp['epsilon_decay']}; episodes={max(milestones)}; validation seeds "
                   f"random={VALIDATION_SEEDS['random']}, heuristic={VALIDATION_SEEDS['heuristic']}; "
                   f"{games} games/opponent/milestone; h2h vs final.pt seed={cfg['head_to_head']['seed']}; "
                   f"train_log={log_path}; ablation_log={long_path}"),
            started_at=started_at, finished_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            cwd=Path.cwd(),
        ),
    )
    return cell_table


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def merge() -> Path:
    """Gop o A6 voi 3 o A4 default_decay (doi thu Heuristic); them H2H va do dung vi tri."""
    cfg = _load_config()
    rows: list[dict[str, Any]] = []
    for row in _read(A4_TABLE_PATH):
        if row["config_id"] == "default_decay":
            rows.append({"train_opponent": "heuristic", **row})
    cells = sorted(CELL_DIR.glob("ablation_a6_cell_*.csv"))
    for path in cells:
        rows.extend(_read(path))
    order = {"heuristic": 0, "random": 1, "selfplay": 2}
    rows.sort(key=lambda r: (order[r["train_opponent"]], int(r["seed"]), int(r["episode"]), r["opponent"]))
    write_csv(TABLE_PATH, TABLE_FIELDS, rows)

    h2h_rows: list[dict[str, Any]] = []
    for path in sorted(CELL_DIR.glob("ablation_a6_h2h_*.csv")):
        h2h_rows.extend(_read(path))
    # Doi chung: o A4 default_decay seed 42 va 2026 (cung doi thu Heuristic) gap final.pt (= seed 0),
    # chi khi file .pt con tren may (cac .pt cua A4 khong commit, chi co JSON).
    last = max(cfg["milestones"])
    for seed in cfg["seeds"]:
        if seed == 0:
            continue  # seed 0 chinh la final.pt, tu dau voi chinh no khong co nghia
        ckpt = Path("checkpoints/level6_dqn/a4") / f"default_decay_s{seed}" / f"dqn_model_ep{last:06d}.pt"
        if not ckpt.is_file():
            print(f"bo qua H2H heuristic s{seed}: khong co {ckpt} (.pt khong commit)")
            continue
        existing = [r for r in h2h_rows if r["train_opponent"] == "heuristic" and int(r["seed"]) == seed]
        if existing:
            continue
        a4_run = next(r["run_id"] for r in rows if r["train_opponent"] == "heuristic" and int(r["seed"]) == seed)
        h2h_rows.append({"run_id": a4_run, "train_opponent": "heuristic", "seed": seed, "episode": last,
                         **_head_to_head(ckpt, cfg)})
    h2h_rows.sort(key=lambda r: (order[r["train_opponent"]], int(r["seed"])))
    write_csv(H2H_PATH, H2H_FIELDS, h2h_rows)

    pos_rows: list[dict[str, Any]] = []
    for row in rows:
        if int(row["episode"]) != last or row["opponent"] != "random":
            continue
        ckpt = Path(row["checkpoint_json"]).with_suffix(".pt")
        if not ckpt.is_file() and row["train_opponent"] == "heuristic" and int(row["seed"]) == 0:
            ckpt = Path("checkpoints/level6_dqn/final.pt")  # cung trong so, da bo optimizer state
        if not ckpt.is_file():
            print(f"bo qua do dung vi tri: khong co {ckpt}")
            continue
        for situation, (hits, total) in position_accuracy(ckpt).items():
            pos_rows.append({"train_opponent": row["train_opponent"], "seed": row["seed"], "checkpoint": str(ckpt),
                             "situation": situation, "positions": total, "hits": hits,
                             "accuracy": hits / total if total else 0.0})
    write_csv(POS_PATH, POS_FIELDS, pos_rows)
    print(f"merged {len(cells)} A6 cells + A4 default_decay -> {TABLE_PATH}, {H2H_PATH}, {POS_PATH}")
    return TABLE_PATH


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--opponent", help="random | selfplay")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--merge", action="store_true")
    args = parser.parse_args(argv)
    if args.merge:
        merge()
        return 0
    if args.opponent is None or args.seed is None:
        parser.error("can --opponent va --seed, hoac --merge")
    started = time.perf_counter()
    path = run_cell(args.opponent, args.seed)
    print(f"cell done in {time.perf_counter() - started:.0f}s -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
