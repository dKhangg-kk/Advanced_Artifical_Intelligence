"""Test cho cac script tong hop cua Y5/Y6 (freeze, summarize_tournament, summarize_a4, report_numbers).

Cac script nam trong ``scripts/`` (khong phai package) nen duoc nap bang importlib.
Du lieu la log gia lap nho, khong can PyTorch.
"""

from __future__ import annotations

import csv
import importlib.util
from pathlib import Path
import sys

import pytest

from connect_four.evaluation.runlog import GAME_FIELDS, MOVE_FIELDS

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"_y_script_{name}", SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write(path: Path, fields, rows) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(fields))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})


@pytest.fixture()
def tournament_logs(tmp_path: Path):
    """Mot cap alphabeta-mcts, 4 van: a thang 2, hoa 1, b thang 1."""
    run_id = "tournament-default-20261118T000000Z-s1-alphabeta-vs-mcts"
    winners = ["a", "b", "draw", "a"]
    a_starts = [1, 0, 1, 0]
    games = [
        {"run_id": run_id, "game_id": f"g{i}", "pair": "alphabeta_vs_mcts", "agent_a": "alphabeta",
         "agent_b": "mcts", "a_starts": a_starts[i], "winner": winners[i], "n_moves": 10 + i,
         "over_budget_a": 1 if i == 0 else 0, "over_budget_b": 0}
        for i in range(4)
    ]
    moves = []
    for i, (agent, ms, nodes, sims) in enumerate(
        [("alphabeta", 10.0, 100, 0), ("alphabeta", 20.0, 300, 0), ("alphabeta", 60.0, 500, 0),
         ("mcts", 5.0, 0, 1000), ("mcts", 15.0, 0, 1000)]
    ):
        moves.append({"run_id": run_id, "game_id": "g0", "ply": i, "agent": agent, "time_ms": ms,
                      "nodes": nodes, "simulations": sims})
    _write(tmp_path / f"games_{run_id}.csv", GAME_FIELDS, games)
    _write(tmp_path / f"moves_{run_id}.csv", MOVE_FIELDS, moves)
    return tmp_path, run_id


def test_pair_agent_and_first_move_summaries(tournament_logs, monkeypatch) -> None:
    folder, run_id = tournament_logs
    mod = _load("summarize_tournament")
    monkeypatch.setattr(mod, "LOG_DIR", folder)
    pairs = mod.load_pairs("tournament-default-20261118T000000Z-s1")
    assert len(pairs) == 1 and pairs[0]["run_id"] == run_id

    (pair,) = mod.pair_summary(pairs)
    assert (pair["wins_a"], pair["draws"], pair["wins_b"]) == (2, 1, 1)
    assert pair["score_a"] == pytest.approx(0.625)
    assert 0.0 <= pair["score_ci95_low"] < pair["score_a"] < pair["score_ci95_high"] <= 1.0
    assert (pair["a_starts"], pair["b_starts"]) == (2, 2)
    assert pair["over_budget_games_a"] == 1 and pair["over_budget_games_b"] == 0
    assert pair["mean_ms_a_per_move"] == pytest.approx(30.0)
    assert pair["mean_nodes_a_per_move"] == pytest.approx(300.0)
    assert pair["mean_simulations_b_per_move"] == pytest.approx(1000.0)

    agents = {row["agent"]: row for row in mod.agent_summary(pairs)}
    assert agents["alphabeta"]["wins"] == 2 and agents["alphabeta"]["losses"] == 1
    assert agents["mcts"]["wins"] == 1 and agents["mcts"]["losses"] == 2
    assert agents["alphabeta"]["max_ms_per_move"] == pytest.approx(60.0)
    assert agents["alphabeta"]["over_budget_games"] == 1

    names, cells = mod.score_matrix([pair])
    assert names == ["alphabeta", "mcts"]
    assert cells[("alphabeta", "mcts")]["score"] == pytest.approx(0.625)
    assert cells[("mcts", "alphabeta")]["score"] == pytest.approx(0.375)
    assert cells[("mcts", "alphabeta")]["w"] == 1 and cells[("mcts", "alphabeta")]["l"] == 2

    first = {(r["agent_a"], r["agent_b"]): r for r in mod.first_move(pairs)}
    row = first[("alphabeta", "mcts")]
    # van 0: a di truoc, a thang; van 1: b di truoc, b thang; van 2: hoa; van 3: b di truoc, a thang
    assert (row["first_player_wins"], row["second_player_wins"], row["draws"]) == (2, 1, 1)
    assert row["first_player_score"] == pytest.approx(0.625)
    assert first[("ALL", "ALL")]["games"] == 4


def test_load_pairs_reports_missing_logs(tmp_path: Path, monkeypatch) -> None:
    mod = _load("summarize_tournament")
    monkeypatch.setattr(mod, "LOG_DIR", tmp_path)
    with pytest.raises(SystemExit):
        mod.load_pairs("khong-ton-tai")


def test_freeze_selection_rule_prefers_mean_score_then_smaller_episode() -> None:
    mod = _load("freeze_dqn_checkpoint")

    def rows(spec):
        out = []
        for episode, score_random, score_heuristic in spec:
            for opponent, score in (("random", score_random), ("heuristic", score_heuristic)):
                out.append({"episode": str(episode), "opponent": opponent, "score": str(score),
                            "wins": "0", "draws": "0", "losses": "0"})
        return out

    best = mod.choose(mod.milestone_table(rows([(1000, 0.6, 0.0), (2500, 0.5, 0.2), (5000, 0.7, 0.1)])))
    assert best["episode"] == 5000 and best["mean_validation_score"] == pytest.approx(0.4)
    # bang diem: chon moc episode nho hon
    tie = mod.choose(mod.milestone_table(rows([(1000, 0.5, 0.1), (10000, 0.4, 0.2)])))
    assert tie["episode"] == 1000


def test_a4_summary_aggregates_over_seeds(tmp_path: Path, monkeypatch) -> None:
    mod = _load("summarize_a4")
    rows = []
    for seed, score in (("0", 0.5), ("42", 0.7), ("2026", 0.9)):
        rows.append({"config_id": "default_decay", "decay": "0.9995", "episode": "1000", "opponent": "random",
                     "seed": seed, "games": "100", "score": str(score), "epsilon_at_milestone": "0.6",
                     "train_mean_reward_last500": "-0.5", "train_win_rate_last500": "0.2",
                     "train_mean_loss_last500": "0.01", "training_elapsed_seconds": "100"})
    (item,) = mod.summarize(rows)
    assert item["n_seeds"] == 3 and item["seeds"] == "0 2026 42"
    assert item["score_mean"] == pytest.approx(0.7)
    assert item["score_sd"] == pytest.approx(0.2)
    assert (item["score_min"], item["score_max"]) == (0.5, 0.9)
    monkeypatch.setattr(mod, "SUMMARY", tmp_path / "summary.csv")
    mod.write_summary([item])
    assert (tmp_path / "summary.csv").read_text(encoding="utf-8").startswith("config_id,decay,episode,opponent")


def test_report_numbers_helpers() -> None:
    mod = _load("build_report_numbers_y")
    assert mod.fmt(0.123456) == "0.1235"
    assert mod.fmt(3.0) == "3" and mod.fmt(7) == "7" and mod.fmt("abc") == "abc"
    assert mod.prefix_of("tournament-timed-20261118T163224Z-s20261119-mcts-vs-nn") == \
        "tournament-timed-20261118T163224Z-s20261119"
    with pytest.raises(ValueError):
        mod.prefix_of("k1-heuristic-random-20261109T060914Z-s0")
    assert mod.OWNED_PREFIXES  # nhom section do script quan ly khong rong
