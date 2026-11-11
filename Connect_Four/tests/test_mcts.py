from __future__ import annotations

import pytest

from connect_four.agents.base import Budget
from connect_four.agents.mcts import MCTSAgent
from connect_four.game import ConnectFour


def _snapshot(game: ConnectFour) -> tuple[object, int, tuple[int, ...], int]:
    return game.board.tolist(), game.current_player, game.moves_played(), game.key()


def test_mcts_returns_legal_move_without_mutating_game() -> None:
    game = ConnectFour()
    for action in [3, 2, 3, 2]:
        game.step(action)
    before = _snapshot(game)

    agent = MCTSAgent(simulations=40, seed=7)
    action = agent.choose(game)

    assert action in game.legal_actions()
    assert _snapshot(game) == before
    assert agent.last_stats.simulations == 40
    assert agent.last_stats.nodes > 0


def test_mcts_seed_reproduces_choice_and_stats() -> None:
    game = ConnectFour()
    first = MCTSAgent(simulations=50, seed=11)
    second = MCTSAgent(simulations=50, seed=11)

    assert first.choose(game) == second.choose(game)
    assert first.last_stats.simulations == second.last_stats.simulations == 50


def test_mcts_takes_immediate_win() -> None:
    game = ConnectFour()
    for action in [0, 1, 0, 1, 0, 2]:
        game.step(action)

    agent = MCTSAgent(simulations=50, seed=7)

    assert agent.choose(game) == 0


def test_mcts_supports_simulation_budget_object() -> None:
    agent = MCTSAgent(budget=Budget(simulations=12), seed=3)

    action = agent.choose(ConnectFour())

    assert action in range(7)
    assert agent.last_stats.simulations == 12


def test_mcts_rejects_finished_game() -> None:
    game = ConnectFour()
    for action in [0, 1, 0, 1, 0, 1, 0]:
        game.step(action)

    with pytest.raises(ValueError, match="hop le"):
        MCTSAgent(simulations=10, seed=0).choose(game)
