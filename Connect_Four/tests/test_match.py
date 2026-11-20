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


import csv
import time

import pytest

from connect_four.evaluation.match import (
    generate_openings,
    play_round_robin,
    save_run,
)
from connect_four.evaluation.runlog import GAME_FIELDS, MOVE_FIELDS
from connect_four.game.reference import ReferenceGame


class SlowAgent(FirstLegalAgent):
    name = "slow"

    def choose(self, game):
        time.sleep(0.02)
        return super().choose(game)


class LastLegalAgent(FirstLegalAgent):
    name = "last"

    def choose(self, game):
        return game.legal_actions()[-1]


def test_generate_openings_unique_and_reproducible():
    a = generate_openings(30, plies=4, seed=5)
    assert len({tuple(o) for o in a}) == 30
    assert a == generate_openings(30, plies=4, seed=5)
    with pytest.raises(ValueError):
        generate_openings(10**6, plies=1, seed=0)  # khong du khai cuoc khac nhau


def test_play_game_a_starts_swaps_winner_label():
    # FirstLegal (P1) luon thang vi dung cot 0 va 1... doi ben thi nhan A/B phai dao theo.
    r1 = play_game(ConnectFour(), FirstLegalAgent(), LastLegalAgent(), a_starts=True)
    r2 = play_game(ConnectFour(), FirstLegalAgent(), LastLegalAgent(), a_starts=False)
    assert r1.moves != r2.moves
    assert r1.move_logs[0].player == 1 and r2.move_logs[0].player == 1
    assert r1.move_logs[0].agent == "first" and r2.move_logs[0].agent == "last"


def test_over_budget_flag_and_timing():
    rec = play_game(
        ConnectFour(), SlowAgent(), FirstLegalAgent(), time_per_move_s=0.005, max_moves=42
    )
    assert rec.over_budget_a and not rec.over_budget_b
    assert all(t >= 15 for t in rec.times_ms_a)
    ok = play_game(ConnectFour(), SlowAgent(), FirstLegalAgent(), time_per_move_s=5.0)
    assert not ok.over_budget_a


def test_play_game_rejects_illegal_agent_move():
    class Bad(FirstLegalAgent):
        def choose(self, game):
            return 99

    with pytest.raises(ValueError):
        play_game(ConnectFour(), Bad(), FirstLegalAgent())


def test_play_match_same_openings_both_sides_and_ids():
    config = MatchConfig(games_per_pair=6, openings=3, opening_plies=2, seed=1)
    recs = play_match(FirstLegalAgent(), LastLegalAgent(), config)
    assert [r.a_starts for r in recs] == [True, False] * 3
    assert [r.opening_id for r in recs] == [0, 0, 1, 1, 2, 2]
    assert len({r.game_id for r in recs}) == 6
    assert all(m.game_id == r.game_id for r in recs for m in r.move_logs)
    with pytest.raises(ValueError):
        play_match(FirstLegalAgent(), LastLegalAgent(), MatchConfig(games_per_pair=10, openings=2))


def test_round_robin_pairs_and_engine_independence():
    agents = {"first": FirstLegalAgent(), "last": LastLegalAgent(), "slow": FirstLegalAgent()}
    config = MatchConfig(games_per_pair=2, openings=1, opening_plies=2, seed=3)
    fast = play_round_robin(agents, config)
    ref = play_round_robin(agents, config, game_factory=ReferenceGame)
    assert len(fast) == 3 * 2
    assert [(r.moves, r.winner) for r in fast] == [(r.moves, r.winner) for r in ref]


def test_save_run_matches_runlog_schema(tmp_path):
    config = MatchConfig(games_per_pair=2, openings=1, opening_plies=2, seed=2)
    recs = play_match(FirstLegalAgent(), LastLegalAgent(), config)
    games_path, moves_path = save_run(recs, tmp_path, run_id="t-run")
    with games_path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        assert tuple(reader.fieldnames) == GAME_FIELDS
        rows = list(reader)
    assert len(rows) == 2 and rows[0]["run_id"] == "t-run"
    assert rows[0]["winner"] in {"a", "b", "draw"}
    with moves_path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        assert tuple(reader.fieldnames) == MOVE_FIELDS
