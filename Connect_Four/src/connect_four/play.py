"""Choi trong terminal: nguoi vs may, hoac may vs may.

Vi du:
    python -m connect_four.play --opponent heuristic
    python -m connect_four.play --a alphabeta --b mcts --auto
"""

from __future__ import annotations

import argparse

from connect_four.agents import make_agent
from connect_four.game.constants import PLAYER_1, PLAYER_2
from connect_four.game.engine import ConnectFour


def _make_agent(name: str, args: argparse.Namespace, seed: int):
    """Tao agent theo tham so CLI, giu checkpoint la tuy chon."""
    kwargs: dict[str, object] = {"seed": seed}
    if name == "alphabeta" and args.depth is not None:
        kwargs["depth"] = args.depth
    if name == "mcts" and args.simulations is not None:
        kwargs["simulations"] = args.simulations
    if name in {"nn", "dqn"} and args.checkpoint:
        kwargs["checkpoint"] = args.checkpoint
    return make_agent(name, **kwargs)


def _print_board(game: ConnectFour) -> None:
    print(game.render())
    print()


def _read_human_action(game: ConnectFour) -> int:
    while True:
        raw = input("Chon cot 0-6 (q de thoat): ").strip().lower()
        if raw == "q":
            raise KeyboardInterrupt
        try:
            action = int(raw)
        except ValueError:
            print("Vui long nhap mot so tu 0 den 6.")
            continue
        if game.is_legal(action):
            return action
        print(f"Cot khong hop le. Cac cot con trong: {game.legal_actions()}")


def _play_interactive(args: argparse.Namespace) -> int:
    game = ConnectFour()
    opponent = _make_agent(args.opponent, args, args.seed + 1)
    print("Connect Four 7x6. Ban la X va di truoc.")
    _print_board(game)
    while not game.is_terminal():
        if game.current_player == PLAYER_1:
            action = _read_human_action(game)
        else:
            action = opponent.choose(game.clone())
            print(f"{args.opponent} chon cot {action}.")
        game.step(action)
        _print_board(game)
    winner = game.winner()
    print("Hoa!" if winner is None else ("Ban thang!" if winner == PLAYER_1 else f"{args.opponent} thang!"))
    return 0


def _play_auto(args: argparse.Namespace) -> int:
    if not args.a or not args.b:
        raise SystemExit("Che do --auto can ca --a va --b.")
    game = ConnectFour()
    agent_a = _make_agent(args.a, args, args.seed)
    agent_b = _make_agent(args.b, args, args.seed + 1)
    print(f"May vs may: {args.a} (X) - {args.b} (O)")
    _print_board(game)
    while not game.is_terminal():
        agent = agent_a if game.current_player == PLAYER_1 else agent_b
        action = agent.choose(game.clone())
        print(f"{agent.name} chon cot {action}.")
        game.step(action)
        _print_board(game)
    winner = game.winner()
    print("Hoa!" if winner is None else f"{args.a if winner == PLAYER_1 else args.b} thang!")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Choi Connect Four trong terminal")
    p.add_argument("--opponent", default="random", help="Tac tu cua may khi choi nguoi-may")
    p.add_argument("--a", default=None, help="Tac tu A khi choi may-may")
    p.add_argument("--b", default=None, help="Tac tu B khi choi may-may")
    p.add_argument("--auto", action="store_true", help="Che do may vs may")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--depth", type=int, default=None, help="Do sau cho Alpha-Beta")
    p.add_argument("--simulations", type=int, default=None, help="So mo phong cho MCTS")
    p.add_argument("--checkpoint", default=None, help="Checkpoint cho nn/dqn")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return _play_auto(args) if args.auto else _play_interactive(args)
    except KeyboardInterrupt:
        print("\nDa thoat van.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
