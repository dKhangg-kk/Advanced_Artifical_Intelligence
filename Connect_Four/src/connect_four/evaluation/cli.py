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


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Chay giai dau Connect Four giua hai tac tu")
    p.add_argument("--a", required=True, help="Ten tac tu A (xem agents.AGENTS)")
    p.add_argument("--b", required=True, help="Ten tac tu B")
    p.add_argument("--openings", type=int, default=100, help="So khai cuoc (moi khai cuoc choi 2 van)")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--depth-a", type=int, default=None)
    p.add_argument("--depth-b", type=int, default=None)
    p.add_argument("--sims-b", type=int, default=None)
    p.add_argument("--time-a", type=float, default=None, help="Giay moi nuoc cua A")
    p.add_argument("--time-b", type=float, default=None, help="Giay moi nuoc cua B")
    p.add_argument("--checkpoint-a", default=None)
    p.add_argument("--checkpoint-b", default=None)
    p.add_argument("--out", default=None, help="Duong dan CSV ket qua")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    raise NotImplementedError(
        f"TODO: dung make_agent() cho {args.a!r} va {args.b!r}, roi goi play_match()"
    )


if __name__ == "__main__":
    raise SystemExit(main())
