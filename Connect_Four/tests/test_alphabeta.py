"""Negamax, cat tia va hop dong khong sua ban co."""

from itertools import count
from time import perf_counter

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


@pytest.mark.parametrize("ordering, expected", [(False, 0), (True, 3)])
def test_ordering_changes_tie_break_only(game, ordering, expected):
    agent = AlphaBetaAgent(depth=1, use_ordering=ordering)
    agent._heuristic.weights = dict.fromkeys(agent._heuristic.weights, 0.0)
    assert agent.choose(game) == expected
    assert agent.last_stats.extra["eval_score"] == 0


def test_budget_depth_overrides_default_and_counts_all_nodes(game):
    agent = AlphaBetaAgent(budget=Budget(depth=2), depth=1, use_pruning=False)
    agent.choose(game)
    assert agent.last_stats.depth_reached == 2
    assert agent.last_stats.nodes == 1 + 7 + 7 * 7


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


@pytest.mark.parametrize("depth", [0, -1, 1.5, True])
def test_rejects_nonpositive_search_depth(depth):
    with pytest.raises(ValueError):
        AlphaBetaAgent(depth=depth)


@pytest.mark.parametrize("budget", [Budget(depth=0), Budget(depth=1.5),
                                   Budget(simulations=10), Budget(time_s=-1),
                                   Budget(time_s=float("nan")), Budget(time_s=float("inf"))])
def test_rejects_invalid_budgets(budget):
    with pytest.raises(ValueError):
        AlphaBetaAgent(budget=budget)


def test_zero_time_returns_fallback_and_resets_stats(game):
    agent = AlphaBetaAgent(budget=Budget(time_s=0))
    agent.last_stats.nodes = 100
    agent.last_stats.extra["eval_score"] = 123
    before = snapshot(game)
    assert agent.choose(game) in game.legal_actions()
    assert snapshot(game) == before
    assert agent.last_stats.nodes == agent.last_stats.depth_reached == 0
    assert agent.last_stats.extra == {}
    assert agent._deadline is None
    assert agent.negamax(game, 0, -float("inf"), float("inf")) == 0


@pytest.mark.parametrize("pruning", [False, True])
@pytest.mark.parametrize("ordering", [False, True])
def test_timeout_keeps_completed_iteration(game, monkeypatch, pruning, ordering):
    ticks = count()
    monkeypatch.setattr("connect_four.agents.alphabeta.perf_counter",
                        lambda: next(ticks) * 0.001)
    agent = AlphaBetaAgent(budget=Budget(time_s=0.04),
                          use_pruning=pruning, use_ordering=ordering)
    before = snapshot(game)
    action = agent.choose(game)
    assert agent.last_stats.depth_reached == 1
    reference = AlphaBetaAgent(depth=1, use_pruning=pruning, use_ordering=ordering)
    assert action == reference.choose(game)
    assert agent.last_stats.extra == reference.last_stats.extra
    assert agent.last_stats.nodes > reference.last_stats.nodes
    assert snapshot(game) == before
    assert agent._deadline is None
    agent.reset()
    assert agent.last_stats.nodes == agent.last_stats.depth_reached == 0
    assert agent.last_stats.extra == {}


def test_timed_search_is_not_capped_by_default_depth(game, monkeypatch):
    moves = [4, 3, 2, 1, 2, 2, 3, 3, 5, 6, 3, 1, 1, 3, 4, 2, 1, 1, 6, 1, 6,
             0, 3, 4, 2, 2, 0, 0, 0, 0, 4, 6, 6, 4, 0, 5, 6, 4, 5, 5]
    for move in moves:
        game.step(move)
    monkeypatch.setattr("connect_four.agents.alphabeta.perf_counter", lambda: 0.0)
    agent = AlphaBetaAgent(budget=Budget(time_s=1), depth=1)
    before = snapshot(game)
    assert agent.choose(game) in game.legal_actions()
    assert agent.last_stats.depth_reached == 2
    assert agent.last_stats.extra["eval_score"] == 0
    assert snapshot(game) == before


def test_real_time_budget_returns_promptly(game):
    agent = AlphaBetaAgent(budget=Budget(time_s=0.01))
    before = snapshot(game)
    start = perf_counter()
    assert agent.choose(game) in game.legal_actions()
    assert perf_counter() - start < 1.0
    assert snapshot(game) == before
    assert agent.last_stats.time_ms >= 0
