"""Kiem thu khung log thuc nghiem: run_id, manifest, CSV van/nuoc."""

from __future__ import annotations

import csv
from pathlib import Path

from connect_four.evaluation import (
    GameRecord,
    MoveRecord,
    save_run,
)
from connect_four.evaluation.metrics import p95, percentile
from connect_four.evaluation.runlog import (
    ABLATION_FIELDS,
    GAME_FIELDS,
    MOVE_FIELDS,
    REPORT_NUMBER_FIELDS,
    RUN_MANIFEST_FIELDS,
    TRAIN_CNN_FIELDS,
    TRAIN_DQN_FIELDS,
    append_csv,
    append_manifest,
    make_manifest_row,
    new_run_id,
    write_csv,
)


def _header(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8") as fh:
        return next(csv.reader(fh))


def test_template_headers_match_schema() -> None:
    root = Path(__file__).resolve().parents[1]
    pairs = {
        root / "results/logs/templates/games.csv": GAME_FIELDS,
        root / "results/logs/templates/moves.csv": MOVE_FIELDS,
        root / "results/logs/templates/train_cnn.csv": TRAIN_CNN_FIELDS,
        root / "results/logs/templates/train_dqn.csv": TRAIN_DQN_FIELDS,
        root / "results/logs/templates/ablation.csv": ABLATION_FIELDS,
        root / "results/logs/run_manifest.csv": RUN_MANIFEST_FIELDS,
        root / "results/tables/report_numbers.csv": REPORT_NUMBER_FIELDS,
    }
    for path, fields in pairs.items():
        assert _header(path) == list(fields), path


def test_new_run_id_has_prefix_and_seed() -> None:
    run_id = new_run_id("tournament", seed=42)
    assert run_id.startswith("tournament-")
    assert run_id.endswith("-s42")


def test_write_and_append_csv(tmp_path: Path) -> None:
    path = tmp_path / "sample.csv"
    write_csv(path, ("a", "b"), [{"a": 1, "b": [1, 2]}])
    append_csv(path, ("a", "b"), [{"a": 2, "b": None}])

    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    assert rows[0]["b"] == "1 2"
    assert rows[1]["b"] == ""


def test_save_run_writes_games_and_moves(tmp_path: Path) -> None:
    record = GameRecord(
        agent_a="random",
        agent_b="heuristic",
        a_starts=True,
        run_id="run-1",
        game_id="g1",
        moves=[3, 4, 3],
        winner=1,
        times_ms_a=[10.0, 20.0, 30.0],
        times_ms_b=[5.0, 6.0],
        nodes_a=10,
        nodes_b=20,
        simulations_a=0,
        simulations_b=0,
        move_logs=[
            MoveRecord(
                game_id="g1",
                ply=0,
                player=1,
                agent="random",
                action=3,
                run_id="run-1",
                legal_actions=[0, 1, 2, 3, 4, 5, 6],
                time_ms=10.0,
                nodes=1,
            )
        ],
    )

    games_path, moves_path = save_run([record], tmp_path, run_id="run-1")

    with games_path.open(newline="", encoding="utf-8") as fh:
        games = list(csv.DictReader(fh))
    with moves_path.open(newline="", encoding="utf-8") as fh:
        moves = list(csv.DictReader(fh))

    assert games[0]["winner"] == "a"
    assert games[0]["n_moves"] == "3"
    assert games[0]["mean_ms_a"] == "20.0"
    assert games[0]["p95_ms_a"] == "30.0"
    assert moves[0]["game_id"] == "g1"
    assert moves[0]["legal_actions"] == "0 1 2 3 4 5 6"


def test_manifest_row_has_required_fields(tmp_path: Path) -> None:
    config = tmp_path / "config.yaml"
    config.write_text("seed: 1\n", encoding="utf-8")
    manifest = tmp_path / "run_manifest.csv"

    row = make_manifest_row("run-1", config_file=config, seed=7, command="pytest")
    append_manifest(manifest, row)

    with manifest.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    assert rows[0]["run_id"] == "run-1"
    assert rows[0]["seed"] == "7"
    assert rows[0]["status"] == "completed"
    assert len(rows[0]["config_hash"]) == 16


def test_percentile_nearest_rank() -> None:
    assert percentile([1, 2, 3, 4], 50) == 2.0
    assert p95([1, 2, 3, 4, 5]) == 5.0
