from __future__ import annotations

import json
from pathlib import Path

import pytest

from connect_four.agents.alphabeta import AlphaBetaAgent
from connect_four.game import ConnectFour
from connect_four.training.gen_data import (
    DEFAULT_DEPTH,
    DEFAULT_GAMES,
    DEFAULT_MAIN_MODEL_GAMES,
    generate_dataset,
    split_by_game,
)


def test_default_generation_plan_matches_issue_scope():
    assert DEFAULT_GAMES == 5000
    assert DEFAULT_MAIN_MODEL_GAMES == 3000
    assert DEFAULT_DEPTH == 4


def _state(index: int) -> list[list[list[int]]]:
    state = [[[0 for _ in range(7)] for _ in range(6)] for _ in range(2)]
    state[1][5][3] = 1
    for bit in range(5):
        if index & (1 << bit):
            state[0][bit][0] = 1
    return state


def _write_games(path: Path, count: int = 20) -> None:
    path.mkdir(parents=True, exist_ok=True)
    with (path / "games.jsonl").open("w", encoding="utf-8") as games_file:
        for game_id in range(count):
            state = _state(game_id)
            action = 2
            if game_id == 1:
                state = [
                    [list(reversed(row)) for row in channel]
                    for channel in _state(0)
                ]
                action = 4
            game = {
                "game_id": game_id,
                "depth": 4,
                "moves": [game_id % 7, game_id // 7],
                "examples": [{"ply": 2, "state": state, "action": action}],
            }
            games_file.write(json.dumps(game) + "\n")


def _read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as data_file:
        return [json.loads(line) for line in data_file]


def _canonical(state: list[list[list[int]]]) -> tuple[int, ...]:
    mirrored = [[list(reversed(row)) for row in channel] for channel in state]
    original_flat = tuple(value for channel in state for row in channel for value in row)
    mirrored_flat = tuple(value for channel in mirrored for row in channel for value in row)
    return min(original_flat, mirrored_flat)


def test_split_is_by_game_and_preserves_no_duplicate_states(tmp_path):
    _write_games(tmp_path)

    train_ids, val_ids, test_ids = split_by_game(tmp_path, seed=13)

    assert (len(train_ids), len(val_ids), len(test_ids)) == (14, 3, 3)
    assert not (set(train_ids) & set(val_ids))
    assert not (set(train_ids) & set(test_ids))
    assert not (set(val_ids) & set(test_ids))
    assert set(train_ids) | set(val_ids) | set(test_ids) == set(range(20))

    splits_dir = tmp_path / "splits"
    train = _read_jsonl(splits_dir / "train.jsonl")
    val = _read_jsonl(splits_dir / "val.jsonl")
    test = _read_jsonl(splits_dir / "test.jsonl")
    original_examples = [
        row
        for row in train + val + test
        if row["augmentation"] == "original"
    ]
    canonical_states = [_canonical(row["state"]) for row in original_examples]
    assert len(canonical_states) == len(set(canonical_states))
    assert {row["game_id"] for row in train} <= set(train_ids)
    assert {row["game_id"] for row in val} <= set(val_ids)
    assert {row["game_id"] for row in test} <= set(test_ids)

    manifest = json.loads((splits_dir / "manifest.json").read_text())
    assert manifest["target_ratios"] == {"train": 0.7, "val": 0.15, "test": 0.15}
    assert manifest["duplicate_examples_removed"] == 1
    assert sum(manifest["actual_game_ratios"].values()) == pytest.approx(1.0)
    assert sum(manifest["actual_example_ratios"].values()) == pytest.approx(1.0)


def test_mirror_augmentation_is_only_in_train_and_flips_action(tmp_path):
    _write_games(tmp_path)
    split_by_game(tmp_path, seed=13)
    splits_dir = tmp_path / "splits"
    train = _read_jsonl(splits_dir / "train.jsonl")
    val = _read_jsonl(splits_dir / "val.jsonl")
    test = _read_jsonl(splits_dir / "test.jsonl")

    originals = {row["game_id"]: row for row in train if row["augmentation"] == "original"}
    mirrors = [row for row in train if row["augmentation"] == "mirror"]
    assert mirrors
    assert all(row["augmentation"] == "original" for row in val + test)
    for mirror in mirrors:
        original = originals[mirror["game_id"]]
        assert mirror["state"] == [
            [list(reversed(row)) for row in channel]
            for channel in original["state"]
        ]
        assert mirror["action"] == 6 - original["action"]

    manifest = json.loads((splits_dir / "manifest.json").read_text())
    assert manifest["mirror_examples_added_to_train"] == len(mirrors)
    assert manifest["written_examples"]["train"] == len(train)


def test_split_is_reproducible(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    _write_games(first)
    _write_games(second)

    first_ids = split_by_game(first, seed=7)
    second_ids = split_by_game(second, seed=7)

    assert first_ids == second_ids
    for split in ("train", "val", "test"):
        assert (first / "splits" / f"{split}.jsonl").read_bytes() == (
            second / "splits" / f"{split}.jsonl"
        ).read_bytes()


def test_split_deduplicates_identical_games_and_reports_them(tmp_path):
    _write_games(tmp_path)
    games_path = tmp_path / "games.jsonl"
    games = _read_jsonl(games_path)
    duplicate = {**games[0], "game_id": 20}
    with games_path.open("a", encoding="utf-8") as games_file:
        games_file.write(json.dumps(duplicate) + "\n")

    train_ids, val_ids, test_ids = split_by_game(tmp_path, seed=13)

    assert 20 not in train_ids + val_ids + test_ids
    manifest = json.loads((tmp_path / "splits" / "manifest.json").read_text())
    assert manifest["generated_games"] == 21
    assert manifest["unique_games"] == 20
    assert manifest["duplicate_games_removed"] == 1


@pytest.mark.parametrize(
    "ratios",
    [
        (0.7, 0.2, 0.2),
        (0.7, 0.3, 0.0),
        (float("nan"), 0.15, 0.85),
    ],
)
def test_split_rejects_invalid_ratios(tmp_path, ratios):
    _write_games(tmp_path)
    with pytest.raises(ValueError):
        split_by_game(tmp_path, ratios=ratios)


def test_generate_dataset_records_fixed_depth_and_ab_labels(tmp_path):
    output_dir = generate_dataset(
        n_games=8,
        depth=1,
        max_plies_random=3,
        out_dir=tmp_path / "dataset",
        seed=17,
    )
    games = _read_jsonl(output_dir / "games.jsonl")
    assert len(games) == 8
    assert {game["depth"] for game in games} == {1}
    assert len({tuple(game["opening_moves"]) for game in games}) > 1

    agent = AlphaBetaAgent(depth=1)
    for record in games:
        game = ConnectFour()
        for action in record["opening_moves"]:
            game.step(action)
        examples = iter(record["examples"])
        while not game.is_terminal():
            example = next(examples)
            assert example["state"] == game.to_array().tolist()
            label = agent.choose(game)
            assert example["action"] == label
            game.step(label)
        assert list(examples) == []
        assert list(game.moves_played()) == record["moves"]

    manifest = json.loads(
        (output_dir / "splits" / "manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["depth"] == [1]
    assert manifest["generated_games"] == 8
    assert manifest["planned_use_games"] == {"main_model": 8, "a3": 0}


def test_generate_dataset_rejects_invalid_parameters(tmp_path):
    with pytest.raises(ValueError):
        generate_dataset(n_games=2, out_dir=tmp_path / "too-few-games")
    with pytest.raises(ValueError):
        generate_dataset(n_games=3, depth=0, out_dir=tmp_path / "invalid-depth")
