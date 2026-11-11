"""K3: hop dong agent, bon buoc UCT va ngan sach."""

import math

import numpy as np
import pytest

from connect_four.agents import Budget, MCTSAgent, make_agent
from connect_four.agents import mcts
from connect_four.game import ConnectFour, ReferenceGame


@pytest.fixture(params=[ConnectFour, ReferenceGame])
def game(request):
    return request.param()


def play(game, moves):
    for action in moves:
        game.step(action)
    return game


@pytest.mark.parametrize('simulations', [0, 1, 7, 25])
def test_budget_stats_and_unchanged_game(game, simulations):
    play(game, [3, 2, 3, 4, 1])
    board, moves, key = game.board.copy(), tuple(game.moves_played()), game.key()
    agent = MCTSAgent(budget=Budget(simulations=simulations), seed=4)
    assert agent.choose(game) in game.legal_actions()
    assert agent.last_stats.simulations == simulations
    assert 1 <= agent.last_stats.nodes <= simulations + 1
    assert agent.last_stats.depth_reached <= simulations
    assert agent.last_stats.time_ms >= 0
    np.testing.assert_array_equal(game.board, board)
    assert tuple(game.moves_played()) == moves and game.key() == key
    assert game.current_player == 2 and game.winner() is None
    # Clone-based search must also preserve the original undo history.
    game.undo()
    assert tuple(game.moves_played()) == moves[:-1]


@pytest.mark.parametrize('moves, expected', [
    ([0, 6, 1, 6, 2, 5], 3),  # win for P1
    ([6, 0, 6, 1, 5, 2, 4], 3),  # win for P2
    ([6, 0, 6, 1, 5, 2], 3),  # block P2
    ([0, 6, 1, 6, 2], 3),  # block P1
])
def test_wins_and_blocks_both_players(game, moves, expected):
    play(game, moves)
    assert MCTSAgent(simulations=500, seed=0).choose(game) == expected


def test_full_column_and_seed(game):
    play(game, [0] * 6)
    a, b = MCTSAgent(30, seed=9), MCTSAgent(30, seed=9)
    for _ in range(2):
        assert a.choose(game) == b.choose(game) != 0
        assert a.last_stats.simulations == b.last_stats.simulations == 30
    a.reset()
    assert a.last_stats.simulations == a.last_stats.nodes == 0


DRAW = [4, 3, 2, 1, 2, 2, 3, 3, 5, 6, 3, 1, 1, 3, 4, 2, 1, 1, 6, 1, 6,
        0, 3, 4, 2, 2, 0, 0, 0, 0, 4, 6, 6, 4, 0, 5, 6, 4, 5, 5, 5, 5]


def test_terminal_and_last_draw_move(game):
    # Reuse the draw sequence from the Alpha-Beta/Heuristic tests.
    play(game, DRAW[:-1])
    assert MCTSAgent(10, seed=0).choose(game) == DRAW[-1]
    game.step(DRAW[-1])
    assert game.is_terminal() and game.winner() is None
    with pytest.raises(ValueError):
        MCTSAgent().choose(game)


def test_won_game_rejected(game):
    play(game, [0, 1, 0, 1, 0, 1, 0])
    with pytest.raises(ValueError):
        MCTSAgent().choose(game)


@pytest.mark.parametrize('budget', [Budget(), Budget(depth=1), Budget(simulations=-1),
    Budget(simulations=1.5), Budget(simulations=True), Budget(time_s=-1),
    Budget(time_s=math.inf), Budget(time_s=math.nan)])
def test_invalid_budget(budget):
    with pytest.raises(ValueError):
        MCTSAgent(budget=budget)


@pytest.mark.parametrize('c', [-1, math.inf, math.nan])
def test_invalid_exploration(c):
    with pytest.raises(ValueError):
        MCTSAgent(c=c)


def test_factory_and_legacy_constructor():
    assert make_agent('mcts', budget=Budget(simulations=3)).budget.simulations == 3
    assert MCTSAgent(5, 0, 42).budget.simulations == 5


def test_zero_time_and_real_clock(game):
    zero = MCTSAgent(budget=Budget(time_s=0), seed=0)
    assert zero.choose(game) in game.legal_actions()
    assert zero.last_stats.simulations == 0
    agent = MCTSAgent(budget=Budget(time_s=.03), seed=0)
    assert agent.choose(game) in game.legal_actions()
    assert agent.last_stats.simulations > 0
    assert agent.last_stats.time_ms < 1000


def test_timeout_mid_rollout_does_not_count_or_mutate(monkeypatch):
    ticks = iter([0, 0, 0, 1, 1])
    monkeypatch.setattr(mcts, 'perf_counter', lambda: next(ticks))
    game = ConnectFour()
    agent = MCTSAgent(budget=Budget(time_s=.5), seed=0)
    assert agent.choose(game) in game.legal_actions()
    assert agent.last_stats.simulations == 0
    assert agent.last_stats.nodes == 2
    assert game.moves_played() == ()


class TrapGame:
    """Root can draw (0), or let the opponent choose loss/win for root (1)."""
    def __init__(self, moves=()):
        self.moves = moves

    @property
    def current_player(self):
        return 1 if len(self.moves) % 2 == 0 else 2

    def clone(self):
        return TrapGame(self.moves)

    def legal_actions(self):
        return [] if self.is_terminal() else [0, 1]

    def step(self, action):
        assert action in self.legal_actions()
        self.moves += (action,)

    def is_terminal(self):
        return self.moves == (0,) or len(self.moves) == 2

    def result(self, player):
        assert self.is_terminal() and player == 1
        return 0. if self.moves == (0,) else (-1. if self.moves[-1] == 0 else 1.)


def test_uct_expansion_backprop_and_adversarial_choice(monkeypatch):
    nodes = []
    original = mcts.MCTSNode

    def capture(*args):
        node = original(*args)
        nodes.append(node)
        return node

    monkeypatch.setattr(mcts, 'MCTSNode', capture)
    agent = MCTSAgent(500, seed=0)
    assert agent.choose(TrapGame()) == 0
    root = nodes[0]
    assert root.visits == sum(n.visits for n in root.children.values()) == 500
    assert root.untried == [] and set(root.children) == {0, 1}
    assert root.children[0].wins == 0
    trap = root.children[1]
    assert trap.children[0].wins == trap.children[0].visits  # opponent's win
    assert trap.children[1].wins == -trap.children[1].visits
    assert trap.children[0].visits > trap.children[1].visits
    assert root.children[0].visits > trap.visits
    assert len(nodes) == agent.last_stats.nodes == 5
    assert agent.last_stats.depth_reached == 2
