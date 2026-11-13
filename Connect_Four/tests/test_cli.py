"""Kiem thu doc cau hinh va CLI giai dau cua Như Ý."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from connect_four.evaluation.cli import main
from connect_four.evaluation.config import (
    build_agent,
    load_agent_config,
    load_tournament_config,
)


def test_load_agent_config_contains_registered_agents() -> None:
    settings = load_agent_config("configs/agents.yaml")
    assert {"random", "heuristic", "alphabeta", "mcts", "nn", "dqn"}.issubset(settings)


def test_build_agent_reads_configured_search_budget() -> None:
    settings = load_agent_config("configs/agents.yaml")
    agent = build_agent("alphabeta", settings, seed=9, depth=4)
    assert agent.name == "alphabeta"
    assert agent.budget.depth == 4


def test_timed_tournament_requires_positive_time(tmp_path: Path) -> None:
    agent_config = tmp_path / "agents.yaml"
    agent_config.write_text("random:\n  level: 1\nheuristic:\n  level: 2\n", encoding="utf-8")
    config = tmp_path / "timed.yaml"
    config.write_text(
        "mode: timed\ngames_per_pair: 2\nopenings: 1\nseed: 2\n"
        "agents: [random, heuristic]\ntime_per_move_s: 0\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="time_per_move_s"):
        load_tournament_config(config, agent_config_path=agent_config)


def test_pair_cli_runs_and_writes_game_move_and_manifest_logs(tmp_path: Path) -> None:
    output = tmp_path / "logs"
    summary = tmp_path / "pair.csv"
    result = main([
        "--a", "random", "--b", "heuristic", "--openings", "1",
        "--games-per-pair", "2", "--seed", "8", "--out-dir", str(output),
        "--out", str(summary),
    ])
    assert result == 0
    game_logs = list(output.glob("games_*.csv"))
    move_logs = list(output.glob("moves_*.csv"))
    assert len(game_logs) == len(move_logs) == 1
    with game_logs[0].open(newline="", encoding="utf-8") as stream:
        assert len(list(csv.DictReader(stream))) == 2
    with move_logs[0].open(newline="", encoding="utf-8") as stream:
        assert len(list(csv.DictReader(stream))) > 0
    with (output / "run_manifest.csv").open(newline="", encoding="utf-8") as stream:
        manifest = list(csv.DictReader(stream))
    assert len(manifest) == 1
    assert manifest[0]["status"] == "completed"
    assert summary.is_file()


def test_round_robin_config_saves_each_pair_before_finishing(tmp_path: Path) -> None:
    agent_config = tmp_path / "agents.yaml"
    agent_config.write_text(
        "random:\n  level: 1\nheuristic:\n  level: 2\n",
        encoding="utf-8",
    )
    config = tmp_path / "tournament.yaml"
    config.write_text(
        "mode: default\ngames_per_pair: 2\nopenings: 1\nseed: 5\n"
        "agents: [random, heuristic]\n"
        f"output_dir: {tmp_path / 'logs'}\n"
        f"tables_dir: {tmp_path / 'tables'}\n",
        encoding="utf-8",
    )
    result = main(["--config", str(config), "--agent-config", str(agent_config)])
    assert result == 0
    assert len(list((tmp_path / "logs").glob("games_*.csv"))) == 1
    assert len(list((tmp_path / "logs").glob("moves_*.csv"))) == 1
    assert len(list((tmp_path / "tables").glob("*_summary.csv"))) == 1


def test_build_agent_applies_shared_time_budget() -> None:
    settings = load_agent_config("configs/agents.yaml")
    agent = build_agent("alphabeta", settings, seed=1, time_budget_s=0.2)
    assert agent.budget.time_s == pytest.approx(0.2)
