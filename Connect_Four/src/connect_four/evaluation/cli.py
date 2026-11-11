"""CLI chay giai dau tu dong.

Vi du (sau khi cai dat xong match.py):

    python -m connect_four.evaluation.cli \
        --a alphabeta --b mcts --openings 100 --seed 0 \
        --out results/logs/ab_vs_mcts.csv

    # Che do cung thoi gian moi nuoc
    python -m connect_four.evaluation.cli \
        --a alphabeta --b mcts --time-a 0.1 --time-b 0.1 --openings 20
"""

from __future__ import annotations

import argparse
from pathlib import Path

from connect_four.agents import make_agent
from connect_four.agents.base import Budget
from connect_four.evaluation.match import MatchConfig, play_match, save_moves, save_run
from connect_four.evaluation.runlog import new_run_id


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Chay giai dau Connect Four giua hai tac tu")
    p.add_argument("--a", required=True, help="Ten tac tu A (xem agents.AGENTS)")
    p.add_argument("--b", required=True, help="Ten tac tu B")
    p.add_argument("--openings", type=int, default=100, help="So khai cuoc (moi khai cuoc choi 2 van)")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--depth-a", type=int, default=None)
    p.add_argument("--depth-b", type=int, default=None)
    p.add_argument("--sims-a", type=int, default=None)
    p.add_argument("--sims-b", type=int, default=None)
    p.add_argument("--time-a", type=float, default=None, help="Giay moi nuoc cua A")
    p.add_argument("--time-b", type=float, default=None, help="Giay moi nuoc cua B")
    p.add_argument("--checkpoint-a", default=None)
    p.add_argument("--checkpoint-b", default=None)
    p.add_argument("--out", default=None, help="Duong dan CSV ket qua")
    return p


def _make_agent(name: str, *, seed: int, depth: int | None, simulations: int | None,
                time_s: float | None, checkpoint: str | None):
    """Tao agent tu tham so CLI va chon dung loai budget."""
    kwargs: dict[str, object] = {"seed": seed}
    if name == "alphabeta":
        if time_s is not None:
            kwargs["budget"] = Budget(time_s=time_s)
        elif depth is not None:
            kwargs["depth"] = depth
    elif name == "mcts":
        if time_s is not None:
            kwargs["budget"] = Budget(time_s=time_s)
        elif simulations is not None:
            kwargs["simulations"] = simulations
    elif name in {"nn", "dqn"}:
        if checkpoint:
            kwargs["checkpoint"] = checkpoint
        if name == "dqn":
            kwargs["epsilon"] = 0.0
    return make_agent(name, **kwargs)


def _save_cli_records(records, out: str | None, run_id: str) -> tuple[Path, Path]:
    """Luu ca log tran va log nuoc, tuong thich voi --out la CSV hoac thu muc."""
    for record in records:
        record.run_id = run_id

    if out is None:
        return save_run(records, "results/logs", run_id=run_id)

    path = Path(out)
    if path.suffix.lower() == ".csv":
        path.parent.mkdir(parents=True, exist_ok=True)
        generated_games, generated_moves = save_run(records, path.parent, run_id=run_id)
        if generated_games != path:
            generated_games.replace(path)
        moves_path = path.with_name(f"{path.stem}_moves.csv")
        if generated_moves != moves_path:
            generated_moves.replace(moves_path)
        return path, moves_path
    return save_run(records, path, run_id=run_id)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.openings < 1:
        raise SystemExit("--openings phai >= 1")
    if args.time_a is not None and args.time_a <= 0:
        raise SystemExit("--time-a phai > 0")
    if args.time_b is not None and args.time_b <= 0:
        raise SystemExit("--time-b phai > 0")

    agent_a = _make_agent(
        args.a, seed=args.seed, depth=args.depth_a, simulations=args.sims_a,
        time_s=args.time_a, checkpoint=args.checkpoint_a,
    )
    agent_b = _make_agent(
        args.b, seed=args.seed + 1, depth=args.depth_b, simulations=args.sims_b,
        time_s=args.time_b, checkpoint=args.checkpoint_b,
    )
    config = MatchConfig(
        games_per_pair=args.openings * 2,
        openings=args.openings,
        seed=args.seed,
        time_per_move_s=(args.time_a if args.time_a == args.time_b else None),
    )
    records = play_match(agent_a, agent_b, config, name_a=args.a, name_b=args.b)
    run_id = new_run_id("match", args.seed)
    games_path, moves_path = _save_cli_records(records, args.out, run_id)

    wins_a = sum(record.winner == 1 for record in records)
    wins_b = sum(record.winner == 2 for record in records)
    draws = len(records) - wins_a - wins_b
    print(f"{args.a} vs {args.b}: {wins_a} win, {draws} draw, {wins_b} loss (A perspective)")
    print(f"games: {games_path}")
    print(f"moves: {moves_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
