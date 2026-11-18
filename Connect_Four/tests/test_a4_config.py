"""Kiem tra cau hinh A4 va hai che do giai dau cua Nhu Y."""

from __future__ import annotations

from pathlib import Path

import yaml

from connect_four.evaluation.config import load_agent_config, load_tournament_config


def test_a4_config_covers_three_decays_seeds_and_milestones() -> None:
    cfg = yaml.safe_load(Path("configs/ablation_a4_dqn_training.yaml").read_text(encoding="utf-8"))
    assert cfg["episodes"] == 10_000
    assert cfg["milestones"] == [1_000, 2_500, 5_000, 10_000]
    assert [x["name"] for x in cfg["epsilon_decay_configs"]] == [
        "fast_decay", "default_decay", "slow_decay"
    ]
    assert cfg["seeds"] == [0, 42, 2026]
    assert cfg["validation_seeds"] == {"random": 20261102, "heuristic": 20261103}
    assert cfg["eval_games_per_milestone"] == 100


def test_tournament_configs_use_own_checkpoint_mapping() -> None:
    settings = load_agent_config("configs/agents_tournament.yaml")
    assert settings["nn"]["checkpoint"] == "checkpoints/level5_cnn/final.pt"
    assert settings["dqn"]["checkpoint"] == "checkpoints/level6_dqn/dqn_model.pt"

    default = load_tournament_config("configs/tournament_default.yaml")
    timed = load_tournament_config("configs/tournament_timed.yaml")
    assert len(default.agents) == 6 and default.games_per_pair == 200
    assert default.mode == "default" and default.time_per_move_s is None
    assert len(timed.agents) == 6 and timed.games_per_pair == 100
    assert timed.mode == "timed" and timed.time_per_move_s == 0.2
    assert timed.seed != 20261102 and timed.seed != 20261103
