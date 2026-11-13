from __future__ import annotations

import csv
from pathlib import Path

import pytest

from connect_four.game import ConnectFour, ReferenceGame


POSITIONS_PATH = Path(__file__).parent / "data" / "positions.csv"
EXPECTED_COLUMNS = [
    "id",
    "moves",
    "side_to_move",
    "winning_moves",
    "blocking_moves",
    "note",
]


def _read_positions() -> list[dict[str, str]]:
    with POSITIONS_PATH.open(encoding="utf-8", newline="") as positions_file:
        reader = csv.DictReader(positions_file)
        assert reader.fieldnames == EXPECTED_COLUMNS
        return list(reader)


POSITIONS = _read_positions()


def _parse_columns(value: str) -> list[int]:
    return [] if value == "-" else [int(column) for column in value.split()]


def _play_position(game, position: dict[str, str]) -> None:
    for ply, column in enumerate(position["moves"].split(), start=1):
        assert not game.is_terminal(), (
            f"{position['id']}: game ended before move {ply}"
        )
        game.step(int(column))

    player = int(position["side_to_move"])
    assert game.current_player == player, position["id"]
    assert game.winning_moves(player) == _parse_columns(
        position["winning_moves"]
    ), position["id"]
    assert game.winning_moves(3 - player) == _parse_columns(
        position["blocking_moves"]
    ), position["id"]


def test_position_set_covers_required_cases():
    position_ids = [position["id"] for position in POSITIONS]
    assert len(POSITIONS) >= 30
    assert len(position_ids) == len(set(position_ids))
    for prefix in (
        "win-vertical-",
        "win-horizontal-",
        "win-diagonal-up-",
        "win-diagonal-down-",
        "block-",
        "double-threat-",
        "quiet-",
    ):
        assert any(position_id.startswith(prefix) for position_id in position_ids)
    for prefix in (
        "win-vertical-",
        "win-horizontal-",
        "win-diagonal-up-",
        "win-diagonal-down-",
    ):
        assert all(
            _parse_columns(position["winning_moves"])
            for position in POSITIONS
            if position["id"].startswith(prefix)
        )
    assert all(
        len(_parse_columns(position["blocking_moves"])) >= 2
        for position in POSITIONS
        if position["id"].startswith("double-threat-")
    )
    assert "draw-full-board" in position_ids
    assert "full-column" in position_ids


@pytest.mark.parametrize("game_cls", [ConnectFour, ReferenceGame])
@pytest.mark.parametrize("position", POSITIONS, ids=lambda position: position["id"])
def test_winning_moves_matches_position(game_cls, position):
    game = game_cls()
    _play_position(game, position)

    if position["id"] == "draw-full-board":
        assert game.is_terminal()
        assert game.winner() is None
    else:
        assert not game.is_terminal()

    if position["id"] == "full-column":
        assert not game.is_legal(0)
