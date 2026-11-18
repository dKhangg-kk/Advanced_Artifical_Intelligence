"""Run the complete A4 DQN ablation (3 epsilon decays x 3 seeds).

Run from Connect_Four/: PYTHONPATH=src python scripts/run_ablation_a4.py --workers 3
"""
from __future__ import annotations

import argparse
import csv
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import statistics
import time
from typing import Any

import yaml

from connect_four.agents.dqn import DQNAgent
from connect_four.agents.heuristic import HeuristicAgent
from connect_four.agents.random_agent import RandomAgent
from connect_four.evaluation.match import MatchConfig, generate_openings, play_match, save_run
from connect_four.evaluation.metrics import p95, score, wilson_interval
from connect_four.evaluation.runlog import ABLATION_FIELDS, append_manifest, make_manifest_row, write_csv
from connect_four.training.train_dqn import train_dqn

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class TrainingJob:
    decay_name: str
    decay: float
    seed: int
    run_id: str
    out_dir: str
    log_dir: str
    config: dict[str, Any]


def _train_one(job: TrainingJob) -> dict[str, Any]:
    import torch
    torch.set_num_threads(1)
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    clock = time.perf_counter()
    cfg = job.config
    checkpoint = train_dqn(
        episodes=cfg["episodes"], opponent=cfg["training_opponent"],
        lr=cfg["lr"], gamma=cfg["gamma"], epsilon_start=cfg["epsilon_start"],
        epsilon_min=cfg["epsilon_min"], epsilon_decay=job.decay,
        buffer_size=cfg["buffer_size"], batch_size=cfg["batch_size"],
        target_update_freq=cfg["target_update_freq"],
        checkpoint_milestones=cfg["milestones"], out_dir=job.out_dir,
        log_dir=job.log_dir, seed=job.seed, device=cfg["device"], run_id=job.run_id,
    )
    return {
        "decay_name": job.decay_name, "decay": job.decay, "seed": job.seed,
        "run_id": job.run_id, "checkpoint": str(checkpoint),
        "started_at": started,
        "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": round(time.perf_counter() - clock, 3),
    }


def _opponent(name: str, seed: int):
    return RandomAgent(seed=seed) if name == "random" else HeuristicAgent(seed=seed)


def _evaluate(checkpoint: Path, *, decay_name: str, decay: float, training_seed: int,
              episode: int, opponent_name: str, validation_seed: int, games: int,
              stamp: str, config_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if games < 2 or games % 2:
        raise ValueError("eval_games_per_milestone must be a positive even number")
    n_openings = games // 2
    records = play_match(
        DQNAgent(checkpoint=checkpoint, epsilon=0.0, seed=training_seed),
        _opponent(opponent_name, validation_seed + 1),
        MatchConfig(games_per_pair=games, openings=n_openings, seed=validation_seed),
        openings=generate_openings(n_openings, seed=validation_seed),
        name_a="dqn", name_b=opponent_name,
    )
    wins = sum(r.winner == 1 for r in records)
    draws = sum(r.winner is None for r in records)
    losses = sum(r.winner == 2 for r in records)
    ci_low, ci_high = wilson_interval(wins, len(records))
    dqn_times = [t for r in records for t in r.times_ms_a]
    opp_times = [t for r in records for t in r.times_ms_b]
    run_id = (f"a4eval-{stamp}-{decay_name}-ep{episode:05d}-s{training_seed}-"
              f"vs-{opponent_name}-v{validation_seed}")
    games_path, moves_path = save_run(records, ROOT / "results/logs", run_id)
    row = {
        "run_id": run_id, "experiment": "a4_dqn_training",
        "config_id": f"{decay_name}_ep{episode:05d}_vs_{opponent_name}",
        "decay_name": decay_name, "epsilon_decay": decay,
        "training_seed": training_seed, "episode": episode,
        "opponent": opponent_name, "validation_seed": validation_seed,
        "games": len(records), "wins": wins, "draws": draws, "losses": losses,
        "score": score(wins, draws, len(records)), "win_rate": wins / len(records),
        "wilson_low": ci_low, "wilson_high": ci_high,
        "dqn_mean_move_ms": statistics.fmean(dqn_times) if dqn_times else 0.0,
        "dqn_p95_move_ms": p95(dqn_times) if dqn_times else 0.0,
        "opponent_mean_move_ms": statistics.fmean(opp_times) if opp_times else 0.0,
        "opponent_p95_move_ms": p95(opp_times) if opp_times else 0.0,
        "games_log": str(games_path.relative_to(ROOT)),
        "moves_log": str(moves_path.relative_to(ROOT)),
        "checkpoint": str(checkpoint.relative_to(ROOT)),
    }
    append_manifest(ROOT / "results/logs/run_manifest.csv", make_manifest_row(
        run_id, config_file=config_path,
        command=(f"PYTHONPATH=src python scripts/run_ablation_a4.py --evaluate {checkpoint} "
                 f"--opponent {opponent_name} --validation-seed {validation_seed}"),
        seed=validation_seed, status="completed",
        notes=(f"A4 validation; decay={decay}; training_seed={training_seed}; episode={episode}; "
               f"opponent={opponent_name}; W-D-L={wins}-{draws}-{losses}; "
               f"games_log={games_path}; moves_log={moves_path}"),
        cwd=ROOT.parent,
    ))
    metrics = []
    for metric, value in (
        ("wins", wins), ("draws", draws), ("losses", losses),
        ("score", row["score"]), ("win_rate", row["win_rate"]),
        ("wilson_low", ci_low), ("wilson_high", ci_high),
        ("dqn_mean_move_ms", row["dqn_mean_move_ms"]),
        ("dqn_p95_move_ms", row["dqn_p95_move_ms"]),
    ):
        metrics.append({
            "run_id": run_id, "experiment": "a4_dqn_training",
            "config_id": row["config_id"], "seed": training_seed,
            "param_name": "epsilon_decay", "param_value": decay,
            "metric": metric, "value": value,
            "raw_log_path": str(games_path.relative_to(ROOT)) if metric in {
                "wins", "draws", "losses", "score", "win_rate", "wilson_low", "wilson_high"
            } else str(moves_path.relative_to(ROOT)),
        })
    return row, metrics


def run_experiment(config_path: str | Path, workers: int = 1) -> tuple[str, list[dict[str, Any]]]:
    config_path = Path(config_path)
    cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(cfg, dict):
        raise ValueError("A4 config must be a YAML mapping")
    episodes = int(cfg.get("episodes", 10_000))
    milestones = [int(v) for v in cfg.get("milestones", [1000, 2500, 5000, 10000])]
    seeds = [int(v) for v in cfg.get("seeds", [0, 42, 2026])]
    decays = cfg.get("epsilon_decay_configs", [])
    games = int(cfg.get("eval_games_per_milestone", 100))
    validation_seeds = cfg.get("validation_seeds", {"random": 20261102, "heuristic": 20261103})
    opponents = cfg.get("opponents", ["random", "heuristic"])
    if episodes != max(milestones) or len(set(milestones)) != len(milestones):
        raise ValueError("episodes must equal the largest unique milestone")
    if {"random", "heuristic"} - set(opponents):
        raise ValueError("A4 must validate against Random and Heuristic")
    if set(validation_seeds) != {"random", "heuristic"}:
        raise ValueError("validation_seeds must contain Random and Heuristic")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    train_cfg = {
        "episodes": episodes, "training_opponent": str(cfg.get("training_opponent", "heuristic")),
        "lr": float(cfg.get("lr", 0.001)), "gamma": float(cfg.get("gamma", 0.99)),
        "epsilon_start": float(cfg.get("epsilon_start", 1.0)),
        "epsilon_min": float(cfg.get("epsilon_min", 0.05)),
        "buffer_size": int(cfg.get("buffer_size", 100000)),
        "batch_size": int(cfg.get("batch_size", 64)),
        "target_update_freq": int(cfg.get("target_update_freq", 500)),
        "milestones": milestones, "device": str(cfg.get("device", "cpu")),
    }
    jobs = []
    for decay_item in decays:
        for seed in seeds:
            name, decay = str(decay_item["name"]), float(decay_item["decay"])
            run_id = f"train-dqn-a4-{name}-{stamp}-s{seed}"
            out_dir = ROOT / "checkpoints/level6_dqn/a4_runs" / run_id
            jobs.append(TrainingJob(name, decay, seed, run_id, str(out_dir),
                                    str(ROOT / "results/logs"), train_cfg))

    trained = []
    worker_count = max(1, min(int(workers), len(jobs)))
    print(f"A4: training {len(jobs)} configurations with {worker_count} worker(s)", flush=True)
    with ProcessPoolExecutor(max_workers=worker_count) as pool:
        futures = {pool.submit(_train_one, job): job for job in jobs}
        for future in as_completed(futures):
            result = future.result()
            trained.append(result)
            append_manifest(ROOT / "results/logs/run_manifest.csv", make_manifest_row(
                result["run_id"], config_file=config_path,
                command=f"PYTHONPATH=src python scripts/run_ablation_a4.py --config {config_path} --workers {workers}",
                seed=result["seed"], status="completed",
                notes=(f"A4 training; decay={result['decay']}; episodes={episodes}; "
                       f"elapsed_seconds={result['elapsed_seconds']}; "
                       f"log=results/logs/train_dqn_{result['run_id']}.csv; "
                       f"checkpoint_dir={Path(result['checkpoint']).parent}"),
                started_at=result["started_at"], finished_at=result["finished_at"], cwd=ROOT.parent,
            ))
            print(f"TRAIN DONE {result['decay_name']} seed={result['seed']} "
                  f"elapsed={result['elapsed_seconds']:.1f}s", flush=True)

    by_key = {(r["decay_name"], r["seed"]): r for r in trained}
    summaries, ablation_rows = [], []
    print("A4: evaluating all milestone checkpoints", flush=True)
    for decay_item in decays:
        name, decay = str(decay_item["name"]), float(decay_item["decay"])
        for seed in seeds:
            run = by_key[(name, seed)]
            for episode in milestones:
                checkpoint = Path(run["checkpoint"]).parent / f"dqn_model_ep{episode:06d}.pt"
                if not checkpoint.is_file():
                    raise FileNotFoundError(checkpoint)
                for opponent in opponents:
                    row, metric_rows = _evaluate(
                        checkpoint, decay_name=name, decay=decay, training_seed=seed,
                        episode=episode, opponent_name=str(opponent),
                        validation_seed=int(validation_seeds[opponent]), games=games,
                        stamp=stamp, config_path=config_path,
                    )
                    summaries.append(row)
                    ablation_rows.extend(metric_rows)
                    print(f"EVAL {name} seed={seed} ep={episode} vs={opponent}: "
                          f"{row['wins']}-{row['draws']}-{row['losses']} score={row['score']:.3f}",
                          flush=True)

    experiment_id = f"ablation-a4-{stamp}-s0-42-2026"
    raw_path = ROOT / "results/logs" / f"ablation_{experiment_id}.csv"
    write_csv(raw_path, ABLATION_FIELDS, ablation_rows)
    table_path = ROOT / "results/tables/ablation_a4_results.csv"
    table_path.parent.mkdir(parents=True, exist_ok=True)
    with table_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summaries[0].keys()))
        writer.writeheader()
        writer.writerows(summaries)

    # Checkpoint selection is based only on predeclared validation games, never final tournament games.
    eligible = [r for r in summaries if r["decay_name"] == "default_decay" and r["training_seed"] == 0]
    grouped: dict[int, dict[str, dict[str, Any]]] = {}
    for row in eligible:
        grouped.setdefault(int(row["episode"]), {})[str(row["opponent"])] = row
    validation = []
    for episode, pair in grouped.items():
        if {"random", "heuristic"} <= set(pair):
            r_score, h_score = float(pair["random"]["score"]), float(pair["heuristic"]["score"])
            validation.append({
                "episode": episode, "random_score": r_score, "heuristic_score": h_score,
                "combined_validation_score": (r_score + h_score) / 2,
            })
    if not validation:
        raise RuntimeError("No complete validation results for default_decay seed 0")
    selected = max(validation, key=lambda r: (
        r["combined_validation_score"], r["heuristic_score"], r["episode"]
    ))
    source_run = by_key[("default_decay", 0)]
    selected_source = Path(source_run["checkpoint"]).parent / f"dqn_model_ep{selected['episode']:06d}.pt"
    frozen = ROOT / "checkpoints/level6_dqn/dqn_model.pt"
    frozen.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(selected_source, frozen)
    metadata = json.loads(selected_source.with_suffix(".json").read_text(encoding="utf-8"))
    metadata.update({
        "checkpoint_file": frozen.name, "status": "frozen",
        "selected_from": str(selected_source.relative_to(ROOT)),
        "selection_rule": "highest mean validation score vs Random and Heuristic; tie-break Heuristic score, then later episode",
        "validation_results": validation, "validation_seeds": validation_seeds,
        "ablation_run_id": experiment_id,
    })
    frozen.with_suffix(".json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (ROOT / "checkpoints/level6_dqn/a4_selection.json").write_text(
        json.dumps({
            "checkpoint": str(frozen.relative_to(ROOT)), "selected": selected,
            "selection_rule": metadata["selection_rule"], "validation_seeds": validation_seeds,
            "experiment_run_id": experiment_id,
        }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"A4 done: {experiment_id}; selected episode={selected['episode']}")
    return experiment_id, summaries


def main() -> int:
    parser = argparse.ArgumentParser(description="Run A4 DQN training ablation")
    parser.add_argument("--config", default="configs/ablation_a4_dqn_training.yaml")
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    run_experiment(args.config, workers=args.workers)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
