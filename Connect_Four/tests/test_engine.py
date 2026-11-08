from __future__ import annotations

import pytest

from connect_four.game import ConnectFour, ReferenceGame
from connect_four.game.constants import COLS, PLAYER_1, ROWS


@pytest.mark.parametrize("game_cls", [ConnectFour, ReferenceGame])
def test_drop_and_full_column(game_cls):
    game = game_cls()
    for _ in range(ROWS):
        game.step(0)
    assert game.board[:, 0].tolist() == [1, 2, 1, 2, 1, 2]
    assert not game.is_legal(0)
    with pytest.raises(ValueError):
        game.step(0)


@pytest.mark.parametrize("game_cls", [ConnectFour, ReferenceGame])
@pytest.mark.parametrize(
    "moves",
    [
        [0, 0, 1, 1, 2, 2, 3],
        [0, 1, 0, 1, 0, 1, 0],
        [3, 4, 4, 0, 0, 4, 1, 4, 2, 1, 2, 0, 1, 2, 2, 1, 3, 6, 4, 5, 2, 4, 6, 5, 0],
        [3, 2, 2, 1, 1, 0, 1, 0, 0, 4, 0],
    ],
)
def test_four_directions(game_cls, moves):
    game = game_cls()
    for action in moves:
        game.step(action)
    assert game.is_terminal()
    assert game.winner() == PLAYER_1


@pytest.mark.parametrize("game_cls", [ConnectFour, ReferenceGame])
def test_invalid_input_and_terminal_action(game_cls):
    game = game_cls()
    for action in (-1, COLS, 1.5, True, "2"):
        assert not game.is_legal(action)
        with pytest.raises(ValueError):
            game.step(action)


@pytest.mark.parametrize("game_cls", [ConnectFour, ReferenceGame])
def test_undo_clone_and_winning_moves(game_cls):
    game = game_cls()
    for action in [3, 2, 3, 2, 3, 2]:
        game.step(action)
    clone = game.clone()
    assert clone.board.tolist() == game.board.tolist()
    assert game.winning_moves(PLAYER_1) == [3]
    game.undo()
    assert game.moves_played() == (3, 2, 3, 2, 3)
    clone.step(4)
    assert clone.board.tolist() != game.board.tolist()


def test_reference_enumerates_69_winning_windows():
    from connect_four.game.reference import _WINDOWS

    assert len(_WINDOWS) == 69
