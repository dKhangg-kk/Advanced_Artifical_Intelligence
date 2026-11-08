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

