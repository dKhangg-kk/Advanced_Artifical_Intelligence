"""Sinh va chia tap du lieu policy duoc gan nhan boi Alpha-Beta."""

from __future__ import annotations

import json
import math
import random
from contextlib import ExitStack
from pathlib import Path
from typing import Any, TextIO

from connect_four.agents.alphabeta import AlphaBetaAgent
from connect_four.game import ConnectFour
from connect_four.game.constants import COLS, ROWS

DEFAULT_GAMES = 5000
DEFAULT_DEPTH = 4
DEFAULT_MIN_RANDOM_OPENING_PLIES = 6
DEFAULT_RANDOM_OPENING_PLIES = 8
DEFAULT_MAIN_MODEL_GAMES = 3000
DEFAULT_SPLIT_RATIOS = (0.70, 0.15, 0.15)
_SPLITS = ("train", "val", "test")


def _validate_ratios(ratios: tuple[float, float, float]) -> None:
    if len(ratios) != 3 or any(
        not math.isfinite(ratio) or ratio <= 0 for ratio in ratios
    ):
        raise ValueError("Ratios must contain three finite positive values.")
    if not math.isclose(sum(ratios), 1.0, rel_tol=0.0, abs_tol=1e-9):
        raise ValueError("Split ratios must sum to 1.")


def _split_counts(size: int, ratios: tuple[float, float, float]) -> tuple[int, ...]:
    exact = [size * ratio for ratio in ratios]
    counts = [math.floor(value) for value in exact]
    for index in sorted(
        range(len(ratios)),
        key=lambda item: exact[item] - counts[item],
        reverse=True,
    )[: size - sum(counts)]:
        counts[index] += 1
    for empty_index in (index for index, count in enumerate(counts) if count == 0):
        donors = [index for index, count in enumerate(counts) if count > 1]
        if not donors:
            raise ValueError("At least three unique games are required to split data.")
        donor = max(donors, key=lambda index: counts[index] - exact[index])
        counts[donor] -= 1
        counts[empty_index] = 1
    return tuple(counts)


def _canonical_state(state: Any) -> bytes:
    if (
        not isinstance(state, list)
        or len(state) != 2
        or any(not isinstance(channel, list) or len(channel) != ROWS for channel in state)
    ):
        raise ValueError("Each state must have shape (2, 6, 7).")

    flattened = bytearray()
    for channel in state:
        for row in channel:
            if not isinstance(row, list) or len(row) != COLS:
                raise ValueError("Each state must have shape (2, 6, 7).")
            for value in row:
                if isinstance(value, bool) or value not in (0, 0.0, 1, 1.0):
                    raise ValueError("State entries must be binary.")
                flattened.append(int(value))
    return bytes(flattened)


def _mirror_state(state: list[list[list[int | float]]]) -> list[list[list[int | float]]]:
    return [[list(reversed(row)) for row in channel] for channel in state]


def _state_key(state: list[list[list[int | float]]]) -> bytes:
    original = _canonical_state(state)
    mirrored = _canonical_state(_mirror_state(state))
    return min(original, mirrored)


def _read_game_index(
    games_path: Path,
) -> tuple[list[dict[str, Any]], int, int, int]:
    games: list[dict[str, Any]] = []
    game_ids: set[int] = set()
    game_sequences: set[tuple[int, ...]] = set()
    generated_count = 0
    duplicate_count = 0
    raw_example_count = 0
    with games_path.open(encoding="utf-8") as games_file:
        line_number = 0
        while True:
            offset = games_file.tell()
            line = games_file.readline()
            if not line.strip():
                if not line:
                    break
                line_number += 1
                continue
            line_number += 1
            generated_count += 1
            game = json.loads(line)
            if (
                not isinstance(game, dict)
                or type(game.get("game_id")) is not int
                or type(game.get("depth")) is not int
                or game["depth"] < 1
                or not isinstance(game.get("moves"), list)
                or not isinstance(game.get("examples"), list)
            ):
                raise ValueError(f"{games_path}:{line_number}: invalid game record.")
            game_id = game["game_id"]
            if game_id in game_ids:
                raise ValueError(f"{games_path}:{line_number}: duplicate game_id.")
            game_ids.add(game_id)
            moves = game["moves"]
            if any(type(move) is not int or not 0 <= move < COLS for move in moves):
                raise ValueError(f"Game {game_id} has an invalid move.")
            raw_example_count += len(game["examples"])
            signature = tuple(moves)
            if signature in game_sequences:
                duplicate_count += 1
                continue
            game_sequences.add(signature)
            games.append(
                {
                    "game_id": game_id,
                    "moves": signature,
                    "offset": offset,
                    "depth": game.get("depth"),
                    "planned_use": game.get("planned_use"),
                    "example_count": len(game["examples"]),
                }
            )
    if not generated_count:
        raise ValueError(f"No games found in {games_path}.")
    return games, generated_count, duplicate_count, raw_example_count


def _write_example(output: TextIO, example: dict[str, Any]) -> None:
    output.write(json.dumps(example, separators=(",", ":"), allow_nan=False))
    output.write("\n")


def generate_dataset(
    n_games: int = DEFAULT_GAMES,
    depth: int = DEFAULT_DEPTH,
    max_plies_random: int = DEFAULT_RANDOM_OPENING_PLIES,
    out_dir: str | Path = "data/generated",
    seed: int = 0,
    main_model_games: int | None = None,
    min_plies_random: int = DEFAULT_MIN_RANDOM_OPENING_PLIES,
) -> Path:
    """Sinh ván Alpha-Beta sau khai cuộc ngẫu nhiên va tao cac tap du lieu.

    Mỗi dòng `games.jsonl` lưu một ván cùng các trạng thái trước nước đi được
    gán nhãn bởi Alpha-Beta. Hàm cũng chia tập theo ván, loại trạng thái trùng
    (kể cả trạng thái đối xứng) và chỉ lật gương dữ liệu train.
    """
    if type(n_games) is not int or n_games < 3:
        raise ValueError("n_games must be an integer >= 3.")
    if type(depth) is not int or depth < 1:
        raise ValueError("depth must be an integer >= 1.")
    if type(max_plies_random) is not int or max_plies_random < 0:
        raise ValueError("max_plies_random must be an integer >= 0.")
    if (
        type(min_plies_random) is not int
        or min_plies_random < 0
        or min_plies_random > max_plies_random
    ):
        raise ValueError("min_plies_random must be between 0 and max_plies_random.")
    if type(seed) is not int:
        raise ValueError("seed must be an integer.")
    if main_model_games is None:
        main_model_games = min(n_games, DEFAULT_MAIN_MODEL_GAMES)
    if type(main_model_games) is not int or not 0 <= main_model_games <= n_games:
        raise ValueError("main_model_games must be an integer between 0 and n_games.")

    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    agent = AlphaBetaAgent(depth=depth)
    games_path = output_dir / "games.jsonl"
    seen_games: set[tuple[int, ...]] = set()
    generation_attempts = 0
    duplicate_games_rejected = 0
    terminal_openings_rejected = 0
    max_attempts = n_games * 20

    with games_path.open("w", encoding="utf-8", newline="\n") as games_file:
        while len(seen_games) < n_games:
            if generation_attempts >= max_attempts:
                raise RuntimeError(
                    f"Generated only {len(seen_games)} unique games after "
                    f"{generation_attempts} attempts."
                )
            generation_attempts += 1
            game_id = len(seen_games)
            game = ConnectFour()
            opening: list[int] = []
            opening_length = rng.randint(min_plies_random, max_plies_random)
            for _ in range(opening_length):
                legal = game.legal_actions()
                if not legal or game.is_terminal():
                    break
                action = rng.choice(legal)
                opening.append(action)
                game.step(action)
            if game.is_terminal():
                terminal_openings_rejected += 1
                continue

            examples: list[dict[str, Any]] = []
            while not game.is_terminal():
                action = agent.choose(game)
                examples.append(
                    {
                        "ply": len(game.moves_played()),
                        "state": game.to_array().tolist(),
                        "action": action,
                    }
                )
                game.step(action)

            game_sequence = tuple(game.moves_played())
            if game_sequence in seen_games:
                duplicate_games_rejected += 1
                continue
            seen_games.add(game_sequence)
            game_record = {
                "game_id": game_id,
                "depth": depth,
                "planned_use": "main_model" if game_id < main_model_games else "a3",
                "opening_moves": opening,
                "moves": list(game.moves_played()),
                "winner": game.winner(),
                "examples": examples,
            }
            games_file.write(
                json.dumps(game_record, separators=(",", ":"), allow_nan=False)
            )
            games_file.write("\n")

    split_by_game(
        output_dir,
        seed=seed,
        generation_metadata={
            "attempts": generation_attempts,
            "duplicate_games_rejected": duplicate_games_rejected,
            "terminal_openings_rejected": terminal_openings_rejected,
            "min_random_opening_plies": min_plies_random,
            "max_random_opening_plies": max_plies_random,
        },
    )
    return output_dir


def split_by_game(
    dataset_dir: str | Path,
    ratios: tuple[float, float, float] = DEFAULT_SPLIT_RATIOS,
    seed: int = 0,
    generation_metadata: dict[str, int] | None = None,
) -> tuple[list[int], list[int], list[int]]:
    """Chia games.jsonl theo ván, lọc trạng thái trùng và ghi ba split.

    Danh sách game ID được trả theo thứ tự train, val, test. Trạng thái lặp
    hoặc đối xứng với trạng thái đã giữ ở split trước bị loại để tránh rò rỉ.
    Các ví dụ train được bổ sung ảnh gương, trừ trạng thái đối xứng chính nó.
    `manifest.json` ghi số lượng và tỷ lệ thực tế trước/sau lọc.
    """
    _validate_ratios(ratios)
    dataset_path = Path(dataset_dir)
    games_path = dataset_path if dataset_path.is_file() else dataset_path / "games.jsonl"
    unique_games, generated_count, duplicate_games_removed, raw_example_count = (
        _read_game_index(games_path)
    )

    if len(unique_games) < 3:
        raise ValueError("At least three unique games are required to split data.")
    if len({game["depth"] for game in unique_games}) != 1:
        raise ValueError("All games in a dataset must use the same Alpha-Beta depth.")

    shuffled = [game["game_id"] for game in unique_games]
    random.Random(seed).shuffle(shuffled)
    counts = _split_counts(len(shuffled), ratios)
    assignments: dict[str, list[int]] = {}
    offset = 0
    for split, count in zip(_SPLITS, counts, strict=True):
        assignments[split] = shuffled[offset : offset + count]
        offset += count
    if any(not assignments[split] for split in _SPLITS):
        raise ValueError("Each split must contain at least one unique game.")

    games_by_id = {game["game_id"]: game for game in unique_games}
    seen_states: set[bytes] = set()
    retained_counts = {split: 0 for split in _SPLITS}
    written_counts = {split: 0 for split in _SPLITS}
    retained_games: dict[str, set[int]] = {split: set() for split in _SPLITS}
    duplicates_removed = 0
    mirror_count = 0
    split_dir = games_path.parent / "splits"
    split_dir.mkdir(parents=True, exist_ok=True)
    with games_path.open(encoding="utf-8") as games_file, ExitStack() as stack:
        outputs = {
            split: stack.enter_context(
                (split_dir / f"{split}.jsonl").open(
                    "w", encoding="utf-8", newline="\n"
                )
            )
            for split in _SPLITS
        }
        for split in _SPLITS:
            for game_id in assignments[split]:
                game_index = games_by_id[game_id]
                games_file.seek(game_index["offset"])
                game = json.loads(games_file.readline())
                for example in game["examples"]:
                    if (
                        not isinstance(example, dict)
                        or type(example.get("action")) is not int
                    ):
                        raise ValueError(f"Game {game_id} has an invalid example.")
                    action = example["action"]
                    if not 0 <= action < COLS:
                        raise ValueError(f"Game {game_id} has an invalid action label.")
                    state = example.get("state")
                    state_key = _state_key(state)
                    if state_key in seen_states:
                        duplicates_removed += 1
                        continue
                    seen_states.add(state_key)
                    row = {
                        "game_id": game_id,
                        "planned_use": game_index.get("planned_use"),
                        "ply": example.get("ply"),
                        "state": state,
                        "action": action,
                        "augmentation": "original",
                    }
                    _write_example(outputs[split], row)
                    retained_counts[split] += 1
                    written_counts[split] += 1
                    retained_games[split].add(game_id)

                    if split == "train":
                        mirrored_state = _mirror_state(state)
                        if _canonical_state(mirrored_state) != _canonical_state(state):
                            _write_example(
                                outputs[split],
                                {
                                    **row,
                                    "state": mirrored_state,
                                    "action": COLS - 1 - action,
                                    "augmentation": "mirror",
                                },
                            )
                            mirror_count += 1
                            written_counts[split] += 1

    if any(count == 0 for count in retained_counts.values()):
        raise ValueError("A split has no unique labeled states after deduplication.")

    game_counts = {split: len(assignments[split]) for split in _SPLITS}
    planned_use_counts = {
        purpose: sum(game.get("planned_use") == purpose for game in unique_games)
        for purpose in ("main_model", "a3")
    }
    split_planned_use_counts = {
        split: {
            purpose: sum(
                games_by_id[game_id].get("planned_use") == purpose
                for game_id in assignments[split]
            )
            for purpose in ("main_model", "a3")
        }
        for split in _SPLITS
    }
    retained_total = sum(retained_counts.values())
    manifest = {
        "format_version": 1,
        "label_source": "AlphaBetaAgent",
        "depth": sorted({game.get("depth") for game in unique_games}),
        "seed": seed,
        "target_ratios": dict(zip(_SPLITS, ratios, strict=True)),
        "generated_games": generated_count,
        "unique_games": len(unique_games),
        "generation": generation_metadata or {},
        "duplicate_games_removed": (
            duplicate_games_removed
            + (generation_metadata or {}).get("duplicate_games_rejected", 0)
        ),
        "planned_use_games": planned_use_counts,
        "game_counts": game_counts,
        "split_game_ids": assignments,
        "games_without_unique_examples": {
            split: game_counts[split] - len(retained_games[split])
            for split in _SPLITS
        },
        "split_planned_use_game_counts": split_planned_use_counts,
        "actual_game_ratios": {
            split: game_counts[split] / len(unique_games) for split in _SPLITS
        },
        "raw_examples": raw_example_count,
        "duplicate_examples_removed": duplicates_removed,
        "retained_examples": retained_counts,
        "actual_example_ratios": {
            split: (
                retained_counts[split] / retained_total if retained_total else 0.0
            )
            for split in _SPLITS
        },
        "mirror_examples_added_to_train": mirror_count,
        "written_examples": written_counts,
    }
    with (split_dir / "manifest.json").open(
        "w", encoding="utf-8", newline="\n"
    ) as manifest_file:
        json.dump(manifest, manifest_file, indent=2, allow_nan=False)
        manifest_file.write("\n")

    return assignments["train"], assignments["val"], assignments["test"]
