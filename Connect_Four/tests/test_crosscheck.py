from __future__ import annotations

import random

from connect_four.game import ConnectFour, ReferenceGame


def test_bitboard_matches_reference_on_random_sequences():
    rng = random.Random(100)
    for _ in range(1000):
        fast = ConnectFour()
        reference = ReferenceGame()
        while not fast.is_terminal():
            legal = fast.legal_actions()
            action = rng.choice(legal)
            fast.step(action)
            reference.step(action)
            assert fast.board.tolist() == reference.board.tolist()
            assert fast.current_player == reference.current_player
            assert fast.winner() == reference.winner()
            assert fast.legal_actions() == reference.legal_actions()



def test_bitboard_matches_reference_extended_api():
    """Doi chieu them is_terminal, winning_moves, result, to_array, moves_played."""
    from connect_four.game.constants import PLAYERS

    rng = random.Random(2026)
    for _ in range(1000):
        fast, ref = ConnectFour(), ReferenceGame()
        while True:
            assert fast.is_terminal() == ref.is_terminal()
            assert fast.moves_played() == ref.moves_played()
            assert fast.to_array().tolist() == ref.to_array().tolist()
            for p in PLAYERS:
                assert fast.winning_moves(p) == ref.winning_moves(p)
            if fast.is_terminal():
                for p in PLAYERS:
                    assert fast.result(p) == ref.result(p)
                break
            action = rng.choice(fast.legal_actions())
            fast.step(action)
            ref.step(action)


def test_bitboard_undo_matches_reference():
    rng = random.Random(7)
    for _ in range(300):
        fast, ref = ConnectFour(), ReferenceGame()
        for _ in range(rng.randint(1, 42)):
            if fast.is_terminal():
                break
            a = rng.choice(fast.legal_actions())
            fast.step(a)
            ref.step(a)
        for _ in range(rng.randint(0, len(fast.moves_played()))):
            fast.undo()
            ref.undo()
            assert fast.board.tolist() == ref.board.tolist()
            assert fast.current_player == ref.current_player
            assert fast.winner() is None and ref.winner() is None


def test_no_wraparound_between_columns():
    """Bit dem chan 'cuon': 3 o tren cung cot c + o duoi cung cot c+1 khong tao day 4 doc."""
    from connect_four.game.engine import _has_four

    col0_top3 = (1 << 3) | (1 << 4) | (1 << 5)
    assert not _has_four(col0_top3 | (1 << 7))      # hang 0 cot 1 ngay sau bit dem
    assert _has_four(col0_top3 | (1 << 2))          # that su 4 quan doc

def test_key_unique_per_position():
    rng = random.Random(3)
    seen: dict[int, list] = {}
    for _ in range(300):
        g = ConnectFour()
        while not g.is_terminal():
            g.step(rng.choice(g.legal_actions()))
            board = g.board.tolist() + [g.current_player]
            assert seen.setdefault(g.key(), board) == board

