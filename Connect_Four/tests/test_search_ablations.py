"""Check experimental pairing, independent replay, exclusions and pooled metrics."""
import importlib.util
from pathlib import Path

import pytest
from connect_four.evaluation.match import GameRecord

spec = importlib.util.spec_from_file_location(
    "run_search_ablations", Path(__file__).parents[1] / "scripts/run_search_ablations.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def test_positions_preserve_equal_values_and_exclude_terminal(tmp_path):
    positions = runner.read_positions(Path(__file__).parent / "data/positions.csv")
    chosen = [p for p in positions if p[0] in ("empty-board", "draw-full-board")]
    rows = runner.measure_positions(chosen, [2], [
        {"pruning": p, "ordering": o} for p in (False, True) for o in (False, True)
    ], 2, "test", tmp_path / "positions.csv")
    measured = [r for r in rows if r["status"] == "measured"]
    assert len(measured) == 8
    assert len({r["eval_score"] for r in measured}) == 1
    assert all(r["nodes"] > 0 and r["action"] in range(7) for r in measured)
    assert sum(r["status"] == "excluded_terminal" for r in rows) == 8
    assert (tmp_path / "positions.csv").read_text().count("excluded_terminal") == 8


def test_summary_pools_moves_and_resamples_pairs():
    records = [
        GameRecord("a", "b", True, opening_id=0, winner=1, times_ms_a=[1], nodes_a=2),
        GameRecord("a", "b", False, opening_id=0, winner=2, times_ms_a=[3, 5, 7], nodes_a=6),
        GameRecord("a", "b", True, opening_id=1, winner=None, times_ms_a=[9], nodes_a=2),
        GameRecord("a", "b", False, opening_id=1, winner=None, times_ms_a=[11], nodes_a=2),
    ]
    result = runner.summarize_match(records, 42)
    assert result["wins"] == 1 and result["draws"] == 2 and result["losses"] == 1
    assert result["mean_ms"] == 6 and result["p95_ms"] == 11
    assert result["mean_nodes"] == 2
    assert result["score"] == result["score_ci_low"] == result["score_ci_high"] == .5
    with pytest.raises(ValueError):
        runner.summarize_match(records[::-1], 42)


@pytest.mark.parametrize("experiment,value", [("a2", 2), ("a5", 1)])
def test_matches_are_reproducible_and_balanced(experiment, value):
    a = runner.match_records(experiment, value, 2, 17, 4, "test")
    b = runner.match_records(experiment, value, 2, 17, 4, "test2")
    assert [r.moves for r in a] == [r.moves for r in b]
    assert [r.winner for r in a] == [r.winner for r in b]
    assert [r.a_starts for r in a] == [True, False]
    assert a[0].moves[:4] == a[1].moves[:4]
    assert len({r.game_id for r in a}) == 2
    with pytest.raises(ValueError):
        runner.match_records(experiment, value, 3, 17, 4, "test")


@pytest.mark.parametrize('exp', ['a1', 'a2', 'a5'])
def test_cli_writes_traceable_outputs(exp, tmp_path, monkeypatch):
    import csv
    import sys
    import yaml
    (tmp_path / 'configs').mkdir()
    positions = tmp_path / 'positions.csv'
    positions.write_text('id,moves,side_to_move\nempty,,1\n')
    config = dict(seed=42, depths=[1], simulations=[2], configs=[dict(pruning=True, ordering=True)],
                  positions=str(positions), repeat=1, repeat_per_position=1,
                  games_per_budget=2, games_per_depth=2, opening_plies=4,
                  opponent='alphabeta_depth4' if exp == 'a2' else 'heuristic',
                  output='results/tables/summary.csv')
    (tmp_path / 'configs' / f'{runner.CONFIGS[exp]}.yaml').write_text(yaml.safe_dump(config))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, 'argv', ['run_search_ablations.py', '--experiment', exp])
    runner.main()
    with (tmp_path / 'results/logs/run_manifest.csv').open() as f:
        manifest = list(csv.DictReader(f))
    assert len(manifest) == 1 and manifest[0]['status'] == 'completed'
    assert manifest[0]['config_hash']
    with (tmp_path / 'results/tables/summary.csv').open() as f:
        summary = list(csv.DictReader(f))
    for row in summary:
        assert row['run_id'] == manifest[0]['run_id']
        assert (tmp_path / row['raw_log_path']).is_file()
