from __future__ import annotations

from connect_four.agents.base import Agent
from connect_four.evaluation.match import MatchConfig, play_game, play_match
from connect_four.game.engine import ConnectFour


class FirstLegalAgent(Agent):
    name = "first"

    def choose(self, game):
        legal = game.legal_actions()
        if not legal:
            raise ValueError("no legal move")
        return legal[0]


def test_play_game_records_moves_and_swaps_players():
    record = play_game(ConnectFour(), FirstLegalAgent(), FirstLegalAgent())
    assert record.moves
    assert record.winner in (None, 1, 2)
    assert len(record.move_logs) == len(record.moves)
    assert record.move_logs[-1].is_terminal


def test_play_match_uses_each_opening_twice():
    config = MatchConfig(games_per_pair=2, openings=1, opening_plies=2, seed=7)
    records = play_match(FirstLegalAgent(), FirstLegalAgent(), config)
    assert len(records) == 2
    assert records[0].opening_id == records[1].opening_id == 0
    assert records[0].a_starts is True
    assert records[1].a_starts is False
