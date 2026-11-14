"""Tests for CNN training, validation checkpoint selection, and held-out test use."""

from __future__ import annotations

import csv
import json

import numpy as np
import pytest

from connect_four.agents.nn_agent import NNAgent
from connect_four.training.train_supervised import (
    _load_split,
    _load_split_metadata,
    count_cohort_games,
    evaluate_checkpoint,
    train_supervised,
)


def _write_split(path, actions: list[int], cohort: str = "main_model") -> None:
    with path.open("w", encoding="utf-8") as file:
        for action in actions:
            row = {
                "game_id": 1,
                "state": np.zeros((2, 6, 7), dtype=np.float32).tolist(),
                "action": action,
                "augmentation": "original",
                "planned_use": cohort,
            }
            file.write(json.dumps(row) + "\n")


def test_load_split_uses_only_the_requested_game_cohort(tmp_path) -> None:
    _write_split(tmp_path / "train.jsonl", [0], cohort="main_model")
    with (tmp_path / "train.jsonl").open("a", encoding="utf-8") as file:
        row = {
            "state": np.zeros((2, 6, 7), dtype=np.float32).tolist(),
            "action": 1,
            "planned_use": "a3",
        }
        file.write(json.dumps(row) + "\n")

    states, actions = _load_split(tmp_path, "train", cohort="main_model")

    assert states.shape == (1, 2, 6, 7)
    assert actions.tolist() == [0]


def test_load_split_game_limit_keeps_whole_games_and_is_nested(tmp_path) -> None:
    with (tmp_path / "train.jsonl").open("w", encoding="utf-8") as file:
        for game_id in (10, 20, 30):
            for action in (0, 1):
                file.write(
                    json.dumps(
                        {
                            "game_id": game_id,
                            "state": np.zeros((2, 6, 7), dtype=np.float32).tolist(),
                            "action": action,
                            "planned_use": "a3",
                        }
                    )
                    + "\n"
                )

    states_250, actions_250 = _load_split(tmp_path, "train", cohort="a3", game_limit=2)
    states_500, actions_500 = _load_split(tmp_path, "train", cohort="a3", game_limit=3)

    assert states_250.shape == (4, 2, 6, 7)
    assert actions_250.tolist() == [0, 1, 0, 1]
    assert states_500.shape == (6, 2, 6, 7)
    assert actions_500[:4].tolist() == actions_250.tolist()
    assert count_cohort_games(tmp_path, "train", cohort="a3") == 3
    with pytest.raises(ValueError, match="vuot qua so van"):
        _load_split(tmp_path, "train", cohort="a3", game_limit=4)


def test_load_split_metadata_tracks_games_without_a_limit(tmp_path) -> None:
    with (tmp_path / "val.jsonl").open("w", encoding="utf-8") as file:
        for game_id in (10, 20):
            file.write(
                json.dumps(
                    {
                        "game_id": game_id,
                        "state": np.zeros((2, 6, 7), dtype=np.float32).tolist(),
                        "action": 0,
                        "planned_use": "a3",
                    }
                )
                + "\n"
            )

    _, _, games = _load_split_metadata(tmp_path, "val", cohort="a3")

    assert games == (10, 20)


def test_load_split_rejects_a_label_in_a_full_column(tmp_path) -> None:
    state = np.zeros((2, 6, 7), dtype=np.float32)
    state[:, :, 0] = 1
    (tmp_path / "train.jsonl").write_text(
        json.dumps({"state": state.tolist(), "action": 0}) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="cot da day"):
        _load_split(tmp_path, "train")


def test_training_selects_by_validation_and_test_is_consumed_once(tmp_path) -> None:
    torch = pytest.importorskip("torch")
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_split(data_dir / "train.jsonl", [0, 1, 2, 3])
    _write_split(data_dir / "val.jsonl", [3, 3])

    previous_threads = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        checkpoint = train_supervised(
            data_dir,
            out_dir=tmp_path / "output",
            epochs=2,
            batch_size=4,
            lr=1e-3,
            seed=19,
            game_limit=1,
            checkpoint_stem="a3_g1",
            log_dir=tmp_path / "logs",
        )
    finally:
        torch.set_num_threads(previous_threads)

    assert checkpoint.is_file()
    assert checkpoint.name == "a3_g1.pt"
    metadata_path = checkpoint.with_suffix(".json")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["commit"]
    assert metadata["seed"] == 19
    assert metadata["data"]["cohort"] == "main_model"
    assert metadata["data"]["game_limit"] == 1
    assert metadata["data"]["train_games"] == 1
    assert metadata["data"]["val_games"] == 1
    assert metadata["hyperparameters"]["epochs"] == 2
    assert metadata["hardware"]["device"] in {"cpu", "cuda"}
    assert metadata["duration_seconds"] >= 0
    assert metadata["data"]["test_used_during_training"] is False
    assert not (data_dir / "test.jsonl").exists()

    logs = list((tmp_path / "logs").glob("train_cnn_*.csv"))
    assert len(logs) == 1
    with logs[0].open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    assert [int(row["epoch"]) for row in rows] == [1, 2]
    best_row = min(rows, key=lambda row: float(row["val_loss"]))
    assert best_row["best"] == "true"
    assert sum(row["best"] == "true" for row in rows) >= 1
    assert metadata["selection"]["best_epoch"] == int(best_row["epoch"])
    assert metadata["selection"]["best_val_loss"] == pytest.approx(
        float(best_row["val_loss"]), abs=1e-8
    )

    _write_split(data_dir / "test.jsonl", [0, 3])
    metrics = evaluate_checkpoint(checkpoint, data_dir)
    assert {
        "test_loss",
        "top1_accuracy",
        "legal_action_rate",
        "test_examples",
    } <= set(metrics)
    assert metrics["test_examples"] == 2
    assert 0.0 <= metrics["legal_action_rate"] <= 1.0
    situation_count = sum(
        metrics[f"{name}_n"]
        for name in ("win_now", "block", "center_control", "other")
    )
    assert situation_count == metrics["test_examples"]
    (data_dir / "test.jsonl").unlink()
    with pytest.raises(RuntimeError, match="khong duoc danh gia lai"):
        evaluate_checkpoint(checkpoint, data_dir)


def test_nn_agent_masks_every_full_column(tmp_path) -> None:
    torch = pytest.importorskip("torch")
    from connect_four.agents.networks import CNNPolicyNet

    model = CNNPolicyNet(in_channels=2)
    with torch.no_grad():
        for parameter in model.parameters():
            parameter.zero_()
        model.fc[-1].bias.copy_(torch.tensor([10.0, 9.0, 8.0, 7.0, 6.0, 1.0, 5.0]))
    checkpoint = tmp_path / "cnn.pt"
    torch.save({"model_state_dict": model.state_dict()}, checkpoint)

    class OneLegalColumnGame:
        def legal_actions(self) -> list[int]:
            return [5]

        def to_array(self) -> np.ndarray:
            state = np.zeros((2, 6, 7), dtype=np.float32)
            for column in (0, 1, 2, 3, 4, 6):
                state[:, :, column] = 1
            return state

    agent = NNAgent(checkpoint=checkpoint, seed=3)
    assert agent._model is None
    assert agent.choose(OneLegalColumnGame()) == 5  # type: ignore[arg-type]
    assert agent._model is not None
    assert agent.last_stats.extra["legal_actions"] == 1.0


def test_nn_agent_rejects_finished_position() -> None:
    class FinishedGame:
        def legal_actions(self) -> list[int]:
            return []

    with pytest.raises(ValueError, match="Khong con nuoc di"):
        NNAgent().choose(FinishedGame())  # type: ignore[arg-type]
