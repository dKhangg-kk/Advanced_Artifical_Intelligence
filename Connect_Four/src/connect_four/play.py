"""Choi trong terminal: nguoi vs may, hoac may vs may.

Vi du:
    python -m connect_four.play --opponent heuristic
    python -m connect_four.play --a alphabeta --b mcts --auto
"""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Choi Connect Four trong terminal")
    p.add_argument("--opponent", default="heuristic", help="Tac tu cua may khi choi nguoi-may")
    p.add_argument("--a", default=None, help="Tac tu A khi choi may-may")
    p.add_argument("--b", default=None, help="Tac tu B khi choi may-may")
    p.add_argument("--auto", action="store_true", help="Che do may vs may")
    p.add_argument("--seed", type=int, default=0)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    raise NotImplementedError(
        f"TODO: tao engine + make_agent({args.opponent!r}), vong lap nhap cot tu ban phim"
    )


if __name__ == "__main__":
    raise SystemExit(main())
