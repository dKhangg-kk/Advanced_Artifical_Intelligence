"""Negamax, cat tia va hop dong khong sua ban co."""

import pytest

from connect_four.agents.alphabeta import AlphaBetaAgent
from connect_four.agents.base import Budget
from connect_four.agents.heuristic import HeuristicAgent
from connect_four.game import ConnectFour, ReferenceGame


@pytest.fixture(params=[ConnectFour, ReferenceGame])
def game(request):
    return request.param()


def snapshot(game):
    return (game.board.tolist(), game.current_player, game.moves_played(),
            game.key(), game.winner(), game.legal_actions())


def minimax(game, depth, root_player, heuristic):
    if depth <= 0 or game.is_terminal():
        return heuristic.score(game, root_player)
    scores = [minimax(game.clone_after(c), depth - 1, root_player, heuristic)
              for c in game.legal_actions()]
    return max(scores) if game.current_player == root_player else min(scores)


@pytest.mark.parametrize("depth", [1, 2, 3, 4])
@pytest.mark.parametrize("ordering", [False, True])
@pytest.mark.parametrize("moves", [[3, 2, 3, 4, 1], [0, 6, 1, 6, 2, 5]])
def test_matches_minimax_and_pruning_reduces_nodes(game, depth, ordering, moves):
    for move in moves:
        game.step(move)
    before = snapshot(game)
    heuristic = HeuristicAgent()
    scores = {c: minimax(game.clone_after(c), depth - 1, game.current_player, heuristic)
              for c in game.legal_actions()}
    expected = max(scores.values())
    counts = []
    for pruning in [False, True]:
        agent = AlphaBetaAgent(depth=depth, use_pruning=pruning, use_ordering=ordering)
        action = agent.choose(game)
        assert scores[action] == agent.last_stats.extra["eval_score"] == expected
        assert agent.last_stats.depth_reached == depth
        assert agent.last_stats.time_ms >= 0
        counts.append(agent.last_stats.nodes)
        assert snapshot(game) == before
        assert agent.negamax(game, depth, -float("inf"), float("inf")) == expected
        assert snapshot(game) == before
    assert counts[1] <= counts[0]
    if depth >= 3:
        assert counts[1] < counts[0]


@pytest.mark.parametrize("moves, expected", [
    ([0, 6, 0, 6, 0, 5], 0),
    ([6, 0, 6, 0, 5, 0], 0),
    ([6, 0, 6, 0, 5, 0, 5], 0),
])
@pytest.mark.parametrize("depth", [2, 3])
def test_wins_and_blocks_for_both_players(game, moves, expected, depth):
    for move in moves:
        game.step(move)
    assert AlphaBetaAgent(depth=depth).choose(game) == expected


def test_depth_one_takes_immediate_win(game):
    for move in [0, 6, 0, 6, 0, 5]:
        game.step(move)
    assert AlphaBetaAgent(depth=1).choose(game) == 0


def test_full_column_budget_and_stats_reset(game):
    for move in [3] * 6:
        game.step(move)
    before = snapshot(game)
    agent = AlphaBetaAgent(budget=Budget(depth=1))
    assert agent.choose(game) in game.legal_actions()
    assert agent.last_stats.nodes == 7
    assert agent.last_stats.depth_reached == 1
    agent.choose(game)
    assert agent.last_stats.nodes == 7
    assert snapshot(game) == before


@pytest.mark.parametrize("terminal", [False, True])
def test_leaf_score_uses_current_player(game, terminal):
    for move in [0, 6, 0, 6, 0, 5]:
        game.step(move)
    if terminal:
        game.step(0)
    agent = AlphaBetaAgent()
    before = snapshot(game)
    for depth in ([0, -1] if not terminal else [0, 4]):
        assert agent.negamax(game, depth, -float("inf"), float("inf")) == (
            HeuristicAgent().score(game, game.current_player))
    assert snapshot(game) == before
    if terminal:
        with pytest.raises(ValueError, match="hop le"):
            agent.choose(game)


def test_draw(game):
    moves = [4, 3, 2, 1, 2, 2, 3, 3, 5, 6, 3, 1, 1, 3, 4, 2, 1, 1, 6, 1, 6,
             0, 3, 4, 2, 2, 0, 0, 0, 0, 4, 6, 6, 4, 0, 5, 6, 4, 5, 5, 5, 5]
    for move in moves:
        game.step(move)
    agent = AlphaBetaAgent()
    assert agent.negamax(game, 4, -float("inf"), float("inf")) == 0
    with pytest.raises(ValueError, match="hop le"):
        agent.choose(game)


@pytest.mark.parametrize("depth", [0, -1])
def test_rejects_nonpositive_search_depth(depth):
    with pytest.raises(ValueError):
        AlphaBetaAgent(depth=depth)
