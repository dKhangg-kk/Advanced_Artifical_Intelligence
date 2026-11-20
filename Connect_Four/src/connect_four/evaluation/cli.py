"""CLI chay mot cap tac tu hoac giai dau Round-Robin tu YAML.

Chay mot cap:
    python -m connect_four.evaluation.cli --a alphabeta --b mcts --openings 10

Chay giai dau:
    python -m connect_four.evaluation.cli --config configs/tournament_default.yaml
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import time
from itertools import combinations
from pathlib import Path
import sys
from typing import Sequence

from connect_four.agents import AGENTS
from connect_four.evaluation.config import (
    build_agent,
    load_agent_config,
    load_tournament_config,
)
from connect_four.evaluation.match import (
    MatchConfig,
    generate_openings,
    play_match,
    save_records,
    save_run,
)
from connect_four.evaluation.runlog import (
    RUN_MANIFEST_FIELDS,
    make_manifest_row,
    new_run_id,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Chay giai dau Connect Four")
    parser.add_argument("--config", default=None, help="YAML giai dau Round-Robin (neu bo qua thi dung --a/--b)")
    parser.add_argument("--agent-config", default="configs/agents.yaml", help="YAML tham so tac tu")
    parser.add_argument("--a", choices=sorted(AGENTS), help="Tac tu A khi chay mot cap")
    parser.add_argument("--b", choices=sorted(AGENTS), help="Tac tu B khi chay mot cap")
    parser.add_argument("--openings", type=int, default=100, help="So khai cuoc (moi khai cuoc choi hai van)")
    parser.add_argument("--games-per-pair", type=int, default=None, help="So van trong mot cap; mac dinh 2 x openings")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--depth-a", type=int, default=None)
    parser.add_argument("--depth-b", type=int, default=None)
    parser.add_argument("--sims-a", type=int, default=None)
    parser.add_argument("--sims-b", type=int, default=None)
    parser.add_argument("--time-a", type=float, default=None, help="Ngan sach giay moi nuoc cua A")
    parser.add_argument("--time-b", type=float, default=None, help="Ngan sach giay moi nuoc cua B")
    parser.add_argument("--checkpoint-a", default=None)
    parser.add_argument("--checkpoint-b", default=None)
    parser.add_argument("--out", default=None, help="CSV tong hop van dau (tuong thich CLI cu)")
    parser.add_argument("--out-dir", default="results/logs", help="Thu muc luu games/moves/manifest")
    return parser


def _append_manifest(path: Path, row: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists() and path.stat().st_size > 0
    with path.open("a", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=RUN_MANIFEST_FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def _print_summary(records, name_a: str, name_b: str) -> None:
    wins = sum(record.winner == 1 for record in records)
    losses = sum(record.winner == 2 for record in records)
    draws = sum(record.winner is None for record in records)
    total = len(records)
    score = (wins + 0.5 * draws) / total if total else 0.0
    print(f"{name_a} vs {name_b}: {total} games | W-D-L = {wins}-{draws}-{losses} | score_A={score:.3f}")


def _run_pair(args: argparse.Namespace) -> int:
    if not args.a or not args.b:
        raise ValueError("Can truyen ca --a va --b khi khong dung --config.")
    if args.a == args.b:
        raise ValueError("Hai tac tu trong mot cap phai khac nhau.")
    if args.openings <= 0:
        raise ValueError("--openings phai la so nguyen duong.")
    games = args.games_per_pair if args.games_per_pair is not None else 2 * args.openings
    if games <= 0 or (games + 1) // 2 > args.openings:
        raise ValueError("games-per-pair phai > 0 va can khong qua 2 x openings.")
    for value, label in ((args.time_a, "time-a"), (args.time_b, "time-b")):
        if value is not None and value <= 0:
            raise ValueError(f"--{label} phai > 0.")

    if args.time_a is not None and args.time_b is not None and args.time_a != args.time_b:
        raise ValueError("match.py chi ghi mot nguong over_budget chung; time-a va time-b phai bang nhau.")

    settings = load_agent_config(args.agent_config)
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    agent_a = build_agent(
        args.a, settings, seed=args.seed, time_budget_s=args.time_a,
        depth=args.depth_a, simulations=args.sims_a, checkpoint=args.checkpoint_a,
    )
    agent_b = build_agent(
        args.b, settings, seed=args.seed + 1, time_budget_s=args.time_b,
        depth=args.depth_b, simulations=args.sims_b, checkpoint=args.checkpoint_b,
    )
    config = MatchConfig(
        games_per_pair=games,
        openings=args.openings,
        seed=args.seed,
        time_per_move_s=args.time_a if args.time_a is not None else args.time_b,
    )
    records = play_match(agent_a, agent_b, config, name_a=args.a, name_b=args.b)
    run_id = new_run_id(f"{args.a}-vs-{args.b}", args.seed)
    out_dir = Path(args.out_dir)
    games_path, moves_path = save_run(records, out_dir, run_id)
    if args.out:
        save_records(records, args.out)
    row = make_manifest_row(
        run_id,
        config_file=args.agent_config,
        command="python -m connect_four.evaluation.cli " + " ".join(sys.argv[1:]),
        seed=args.seed,
        status="completed",
        notes=f"pair={args.a}_vs_{args.b}; games={games}; games_log={games_path}; moves_log={moves_path}",
        started_at=started_at,
        finished_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        cwd=Path.cwd(),
    )
    _append_manifest(out_dir / "run_manifest.csv", row)
    _print_summary(records, args.a, args.b)
    print(f"games_log={games_path}\nmoves_log={moves_path}")
    if args.out:
        print(f"summary_csv={args.out}")
    return 0


def _run_round_robin(args: argparse.Namespace) -> int:
    config_path = Path(args.config)
    tournament = load_tournament_config(config_path, agent_config_path=args.agent_config)
    agent_settings = load_agent_config(tournament.agent_config)
    match_config = tournament.match_config()
    openings = generate_openings(
        (match_config.games_per_pair + 1) // 2,
        seed=match_config.seed,
    )
    run_prefix = new_run_id(f"tournament-{tournament.mode}", tournament.seed)
    all_summaries: list[tuple[str, str, int, int, int, float]] = []

    # Luu tung cap ngay sau khi ket thuc de giam rui ro mat ca giai neu bi dung dot ngot.
    for index, (name_a, name_b) in enumerate(combinations(tournament.agents, 2)):
        pair_started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        agent_a = build_agent(
            name_a, agent_settings, seed=tournament.seed + index * 2,
            time_budget_s=tournament.time_per_move_s,
        )
        agent_b = build_agent(
            name_b, agent_settings, seed=tournament.seed + index * 2 + 1,
            time_budget_s=tournament.time_per_move_s,
        )
        records = play_match(
            agent_a, agent_b, match_config, openings=openings,
            name_a=name_a, name_b=name_b,
        )
        pair_run_id = f"{run_prefix}-{name_a}-vs-{name_b}"
        games_path, moves_path = save_run(records, tournament.output_dir, pair_run_id)
        manifest = make_manifest_row(
            pair_run_id,
            config_file=config_path,
            command=f"python -m connect_four.evaluation.cli --config {config_path}",
            seed=tournament.seed,
            status="completed",
            notes=(f"mode={tournament.mode}; pair={name_a}_vs_{name_b}; games={len(records)}; "
                   f"games_log={games_path}; moves_log={moves_path}"),
            started_at=pair_started_at,
            finished_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            cwd=Path.cwd(),
        )
        _append_manifest(tournament.output_dir / "run_manifest.csv", manifest)
        wins = sum(record.winner == 1 for record in records)
        losses = sum(record.winner == 2 for record in records)
        draws = sum(record.winner is None for record in records)
        score = (wins + 0.5 * draws) / len(records)
        all_summaries.append((name_a, name_b, wins, draws, losses, score))
        _print_summary(records, name_a, name_b)

    summary_path = tournament.tables_dir / f"{run_prefix}_summary.csv"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with summary_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["agent_a", "agent_b", "wins_a", "draws", "wins_b", "score_a"])
        writer.writerows(all_summaries)
    print(f"Round-Robin complete: {len(all_summaries)} pairs; summary={summary_path}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.config:
        return _run_round_robin(args)
    return _run_pair(args)


if __name__ == "__main__":
    raise SystemExit(main())
