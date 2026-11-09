"""Hop dong chung cua hai tac tu K1 tren ca hai engine."""

import pytest

from connect_four.agents.heuristic import HeuristicAgent
from connect_four.agents.random_agent import RandomAgent
from connect_four.game import ConnectFour, ReferenceGame


@pytest.mark.parametrize("game_cls", [ConnectFour, ReferenceGame])
@pytest.mark.parametrize("agent_cls", [RandomAgent, HeuristicAgent])
def test_legal_seeded_choices_preserve_game(game_cls, agent_cls):
    game = game_cls()
    for move in [0] * 6:
        game.step(move)
    before = (game.board.tolist(), game.current_player, game.moves_played(), game.key())
    first, second = agent_cls(seed=12), agent_cls(seed=12)
    choices = [first.choose(game) for _ in range(20)]
    assert choices == [second.choose(game) for _ in range(20)]
    assert all(c in game.legal_actions() and c != 0 for c in choices)
    assert before == (game.board.tolist(), game.current_player, game.moves_played(), game.key())
    assert first.last_stats.simulations == 0
    first.reset()
    assert first.last_stats.nodes == 0
    assert first.last_stats.extra == {}


@pytest.mark.parametrize("game_cls", [ConnectFour, ReferenceGame])
@pytest.mark.parametrize("agent_cls", [RandomAgent, HeuristicAgent])
def test_finished_game_rejects_choice(game_cls, agent_cls):
    game = game_cls()
    for move in [0, 1, 0, 1, 0, 1, 0]:
        game.step(move)
    with pytest.raises(ValueError, match="hop le"):
        agent_cls(seed=0).choose(game)
