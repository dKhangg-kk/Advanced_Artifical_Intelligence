"""Thu tu luat, ham diem dung chung va cac the co bien cua K1."""

import pytest

from connect_four.agents.heuristic import HeuristicAgent
from connect_four.game import ConnectFour, ReferenceGame


@pytest.fixture(params=[ConnectFour, ReferenceGame])
def game(request):
    return request.param()


@pytest.mark.parametrize("moves, expected", [
    ([0, 6, 0, 6, 0, 6], 0),  # Thang truoc khi chan doi thu o cot 6.
    ([6, 0, 6, 0, 5, 0], 0),
    ([6, 0, 6, 0, 5, 0, 5], 0),  # Cung quy tac khi nguoi 2 den luot.
    ([], 3),
])
def test_priority(game, moves, expected):
    for move in moves:
        game.step(move)
    assert HeuristicAgent(seed=0).choose(game) == expected


def test_avoid_supporting_opponent_win(game):
    moves = [1, 3, 6, 2, 4, 6, 2, 4, 3, 2, 0, 5, 6, 0, 4, 4, 6, 4, 5, 6, 2]
    for move in moves:
        game.step(move)
    opponent = 3 - game.current_player
    assert not game.winning_moves(1) and not game.winning_moves(2)
    assert game.clone_after(3).winning_moves(opponent)
    agent = HeuristicAgent(seed=0)
    # Diem vi tri khong duoc vuot qua quy tac an toan.
    agent.weights["center_bonus"] = 1_000_000
    action = agent.choose(game)
    assert action != 3
    assert not game.clone_after(action).winning_moves(opponent)


def test_unavoidable_double_threat_is_not_reported_as_defended(game):
    for move in [6, 1, 6, 2, 5, 3]:
        game.step(move)
    assert game.winning_moves(2) == [0, 4]
    agent = HeuristicAgent(seed=0)
    action = agent.choose(game)
    assert action in game.legal_actions()
    assert agent.last_stats.extra["unavoidable_double_threat"] == 1.0


def test_tied_wins_are_seeded_and_not_always_leftmost(game):
    for move in [1, 6, 2, 6, 3, 5]:
        game.step(move)
    assert game.winning_moves(1) == [0, 4]
    a, b = HeuristicAgent(seed=12), HeuristicAgent(seed=12)
    actions = [a.choose(game) for _ in range(20)]
    assert actions == [b.choose(game) for _ in range(20)]
    assert set(actions) == {0, 4}


def test_tied_position_scores_use_seed(game):
    agent = HeuristicAgent(seed=1)
    agent.weights = dict.fromkeys(agent.weights, 0.0)
    actions = [agent.choose(game) for _ in range(30)]
    again = HeuristicAgent(weights=agent.weights, seed=1)
    assert actions == [again.choose(game) for _ in range(30)]
    assert len(set(actions)) > 1


def test_score_perspective_position_and_terminal(game):
    agent = HeuristicAgent(seed=0)
    assert agent.score(game) == 0
    game.step(3)
    assert agent.score(game, 1) == 18
    assert agent.score(game) == agent.score(game, 2) == -18
    for move in [0, 3, 0, 3, 0]:
        game.step(move)
    assert agent.score(game, 1) > 0
    game.step(3)
    assert agent.score(game, 1) == agent.weights["win"]
    assert agent.score(game) == -agent.weights["win"]
    with pytest.raises(ValueError):
        agent.score(game, 3)


@pytest.mark.parametrize("moves", [
    [0, 6, 1, 6, 2, 5],
    [0, 6, 0, 6, 0, 5],
    [3, 2, 2, 1, 1, 0, 1, 0, 0, 4],
    [3, 4, 4, 5, 5, 6, 5, 6, 6, 2],
])
def test_score_counts_unblocked_threes_in_all_directions(game, moves):
    for move in moves:
        game.step(move)
    agent = HeuristicAgent()
    agent.weights = dict.fromkeys(agent.weights, 0.0)
    agent.weights["own_three"] = 100
    assert agent.score(game, 1) >= 100


def test_draw_scores_zero_and_has_no_choice(game):
    moves = [4, 3, 2, 1, 2, 2, 3, 3, 5, 6, 3, 1, 1, 3, 4, 2, 1, 1, 6, 1, 6,
             0, 3, 4, 2, 2, 0, 0, 0, 0, 4, 6, 6, 4, 0, 5, 6, 4, 5, 5, 5, 5]
    for move in moves:
        game.step(move)
    assert game.is_terminal() and game.winner() is None
    agent = HeuristicAgent()
    assert agent.score(game, 1) == agent.score(game, 2) == 0
    with pytest.raises(ValueError):
        agent.choose(game)


def test_stats_are_reset_for_immediate_win(game):
    agent = HeuristicAgent(seed=0)
    agent.choose(game)
    assert agent.last_stats.nodes == 7
    for move in [0, 6, 0, 6, 0, 6]:
        game.step(move)
    assert agent.choose(game) == 0
    assert agent.last_stats.nodes == 0
    assert agent.last_stats.depth_reached == 0
    assert agent.last_stats.extra["eval_score"] == agent.weights["win"]
