from __future__ import annotations

import pytest

from connect_four.game import ConnectFour, ReferenceGame
from connect_four.solver import ExactSolver


@pytest.fixture(params=[ConnectFour, ReferenceGame])
def game(request):
    return request.param()


def test_solver_finds_forced_immediate_win_on_both_engines(game):
    for move in [0, 1, 0, 1, 0, 2]:
        game.step(move)
    solver = ExactSolver()
    assert solver.solve(game) == 1
    assert solver.best_moves(game) == [0]
    assert solver.choose(game) == 0


def test_solver_handles_terminal_loss_from_current_perspective(game):
    for move in [0, 1, 0, 1, 0, 1, 0]:
        game.step(move)
    assert game.is_terminal()
    assert ExactSolver().solve(game) == -1


def test_solver_does_not_mutate_game(game):
    for move in [0, 1, 0, 1, 0, 2]:
        game.step(move)
    before = (game.board.tolist(), game.current_player, game.moves_played())
    ExactSolver().best_moves(game)
    assert (game.board.tolist(), game.current_player, game.moves_played()) == before
