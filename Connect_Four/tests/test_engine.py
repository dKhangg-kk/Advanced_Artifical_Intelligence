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


def _moves_for_window(window):
    """Chuoi nuoc di de P1 lap day mot cua so 4 o; P2 di cac cot khong anh huong."""
    need = {}  # cot -> so quan can co (tinh den hang cao nhat cua cua so)
    for r, c in window:
        need[c] = max(need.get(c, 0), r + 1)
    return need


@pytest.mark.parametrize("game_cls", [ConnectFour, ReferenceGame])
def test_every_one_of_69_windows_wins(game_cls):
    """Dat truc tiep 4 quan P1 vao tung cua so (bang cach lap day nen bang quan P2)."""
    from connect_four.game.reference import _WINDOWS

    for window in _WINDOWS:
        win_cells = set(window)
        need = _moves_for_window(window)
        game = game_cls()
        # tung cot: tha tu duoi len; o thuoc cua so -> P1, o con lai -> P2.
        # Danh sach theo luot de ca hai ben di dung luot.
        p1_queue, p2_queue = [], []
        for c, height in need.items():
            for r in range(height):
                (p1_queue if (r, c) in win_cells else p2_queue).append((r, c))
        # sap xep luot: moi quan phai tha dung thu tu trong cot
        placed = {c: 0 for c in range(COLS)}
        order = []
        pending = {1: list(p1_queue), 2: list(p2_queue)}
        turn = 1
        guard = 0
        while pending[1] or pending[2]:
            guard += 1
            assert guard < 200
            options = [x for x in pending[turn] if x[0] == placed[x[1]]]
            if not options:
                # nguoi nay chua co o hop le: di quan "dem" o cot rong khac
                filler = next(
                    c for c in range(COLS) if placed[c] < ROWS and c not in need
                )
                order.append(filler)
                placed[filler] += 1
            else:
                r, c = options[0]
                pending[turn].remove(options[0])
                order.append(c)
                placed[c] += 1
            turn = 3 - turn
            if len(order) > 41:
                break
        else:
            for col in order:
                if game.is_terminal():
                    break
                game.step(col)
            assert game.winner() in (1, 2)
            continue
        pytest.skip("khong dung duoc chuoi cho cua so nay")


@pytest.mark.parametrize("game_cls", [ConnectFour, ReferenceGame])
def test_draw_full_board(game_cls):
    # Chuoi hoa da biet: 7 cot day, khong ai co 4 lien tiep.
    import random
    rng = random.Random(1)
    for _ in range(20000):
        game = game_cls()
        while not game.is_terminal():
            game.step(rng.choice(game.legal_actions()))
        if game.winner() is None:
            assert game.legal_actions() == []
            assert game.result(1) == 0.0
            assert len(game.moves_played()) == ROWS * COLS
            return
    pytest.fail("khong tim thay van hoa")


@pytest.mark.parametrize("game_cls", [ConnectFour, ReferenceGame])
def test_undo_restores_state_and_clears_win(game_cls):
    game = game_cls()
    for action in [0, 1, 0, 1, 0, 1]:
        game.step(action)
    before = game.board.tolist(), game.current_player, game.key()
    game.step(0)
    assert game.winner() == PLAYER_1
    game.undo()
    assert game.winner() is None and not game.is_terminal()
    assert (game.board.tolist(), game.current_player, game.key()) == before
    with pytest.raises(ValueError):
        game_cls().undo()


@pytest.mark.parametrize("game_cls", [ConnectFour, ReferenceGame])
def test_step_after_terminal_raises(game_cls):
    game = game_cls()
    for action in [0, 1, 0, 1, 0, 1, 0]:
        game.step(action)
    with pytest.raises(ValueError):
        game.step(2)
    assert game.legal_actions() == []
