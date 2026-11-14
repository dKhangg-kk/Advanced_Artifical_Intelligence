"""Tests for tactical situation classification used by ablation A3 (RQ2)."""

from __future__ import annotations

import numpy as np
import pytest

from connect_four.evaluation.situations import (
    CENTER_COLUMN,
    SITUATION_NAMES,
    classify_position,
    situation_hit,
    situation_metrics,
)
from connect_four.game import ConnectFour


def _state_after(moves: list[int]) -> np.ndarray:
    game = ConnectFour()
    for move in moves:
        game.step(move)
    return game.to_array()


def test_empty_board_is_center_control() -> None:
    situation = classify_position(_state_after([]))

    assert situation.name == "center_control"
    assert situation.center_available is True
    assert situation.winning_moves == ()
    assert situation.blocking_moves == ()
    assert CENTER_COLUMN in situation.legal_actions


def test_immediate_win_has_priority_over_block() -> None:
    # Player 1 has 0,1,2 on the bottom row; player 2 also threatens 3.
    situation = classify_position(_state_after([0, 0, 1, 1, 2, 2]))

    assert situation.name == "win_now"
    assert situation.winning_moves == (3,)
    assert situation.blocking_moves == ()
    assert situation_hit(situation, 3, 3)
    assert not situation_hit(situation, 2, 3)


def test_block_situation_detects_opponent_winning_column() -> None:
    # Player 2 has 3,4,5 on the bottom row and wins at column 2.
    situation = classify_position(_state_after([0, 3, 1, 4, 6, 5]))

    assert situation.name == "block"
    assert situation.winning_moves == ()
    assert situation.blocking_moves == (2,)
    assert situation_hit(situation, 2, 2)
    assert not situation_hit(situation, 3, 2)


def test_center_control_requires_center_move() -> None:
    situation = classify_position(_state_after([]))

    assert situation_hit(situation, CENTER_COLUMN, 0)
    assert not situation_hit(situation, 0, 0)


def test_situation_metrics_reports_counts_and_accuracy() -> None:
    states = np.stack(
        [
            _state_after([]),
            _state_after([0, 3, 1, 4, 6, 5]),
            _state_after([0, 0, 1, 1, 2, 2]),
        ]
    )
    labels = np.asarray([0, 2, 3], dtype=np.int64)
    predictions = np.asarray([3, 2, 0], dtype=np.int64)

    metrics = situation_metrics(states, labels, predictions)

    assert set(metrics) == {
        f"{name}_{metric}"
        for name in SITUATION_NAMES
        for metric in ("n", "top1_accuracy", "situation_accuracy")
    }
    assert metrics["center_control_n"] == 1.0
    assert metrics["center_control_situation_accuracy"] == 1.0
    assert metrics["block_n"] == 1.0
    assert metrics["block_situation_accuracy"] == 1.0
    assert metrics["win_now_n"] == 1.0
    assert metrics["win_now_situation_accuracy"] == 0.0
    assert metrics["other_n"] == 0.0
    assert sum(metrics[f"{name}_n"] for name in SITUATION_NAMES) == 3.0


def test_situation_metrics_rejects_shape_mismatch() -> None:
    with pytest.raises(ValueError, match="states phai co shape"):
        situation_metrics(
            np.zeros((2, 2, 6, 6)),
            np.asarray([0, 1]),
            np.asarray([0, 1]),
        )
