"""Run A1/A2/A5 from Connect_Four; raw logs are never overwritten.

PYTHONPATH=src python scripts/run_search_ablations.py --experiment a1
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from time import perf_counter

import yaml

from connect_four.agents.alphabeta import AlphaBetaAgent
from connect_four.agents.heuristic import HeuristicAgent
from connect_four.agents.mcts import MCTSAgent
from connect_four.evaluation.match import generate_openings, play_game, save_run
from connect_four.evaluation.metrics import bootstrap_ci, mean, p95, score, wilson_interval
from connect_four.evaluation.runlog import (
    ABLATION_FIELDS, append_csv, append_manifest, config_hash, make_manifest_row,
    new_run_id, utc_now, write_csv,
)
from connect_four.game import ConnectFour, ReferenceGame

CONFIGS = {"a1": "ablation_a1_pruning", "a2": "ablation_a2_mcts_budget", "a5": "ablation_a5_depth"}
POSITION_FIELDS = ("run_id", "position_id", "depth", "pruning", "ordering", "repeat",
                   "action", "eval_score", "nodes", "time_ms", "status")


def read_positions(path: str | Path) -> list[tuple[str, ConnectFour]]:
    """Validate positions against both engines before measuring search."""
    with Path(path).open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows or len({r["id"] for r in rows}) != len(rows):
        raise ValueError("Position IDs must be nonempty and unique")
    positions = []
    for row in rows:
        game, reference = ConnectFour(), ReferenceGame()
        for action in map(int, row["moves"].split()):
            game.step(action)
            reference.step(action)
        if (game.board.tolist() != reference.board.tolist()
                or game.current_player != int(row["side_to_move"])
                or game.winner() != reference.winner()):
            raise ValueError(f"Invalid position: {row['id']}")
        positions.append((row["id"], game))
    return positions


def measure_positions(positions, depths, settings, repeats, run_id, raw_path):
    """Measure every repetition; terminal positions are recorded as excluded."""
    rows = []
    expected = {}
    for position_id, game in positions:
        before = (game.key(), list(game.moves_played()))
        for depth in depths:
            for flags in settings:
                for repeat in range(repeats):
                    row = dict(run_id=run_id, position_id=position_id, depth=depth,
                               pruning=flags["pruning"], ordering=flags["ordering"], repeat=repeat)
                    if game.is_terminal():
                        row.update(status="excluded_terminal")
                    else:
                        agent = AlphaBetaAgent(depth=depth, use_pruning=flags["pruning"],
                                               use_ordering=flags["ordering"])
                        start = perf_counter()
                        action = agent.choose(game)
                        elapsed = (perf_counter() - start) * 1000
                        value = agent.last_stats.extra["eval_score"]
                        key = position_id, depth
                        if value != expected.setdefault(key, value):
                            raise AssertionError(f"Search value mismatch: {key}, {flags}")
                        assert action in game.legal_actions()
                        assert before == (game.key(), list(game.moves_played()))
                        row.update(action=action, eval_score=value, nodes=agent.last_stats.nodes,
                                   time_ms=elapsed, status="measured")
                    append_csv(raw_path, POSITION_FIELDS, [row])
                    rows.append(row)
        print(f"{run_id}: position {position_id} complete", flush=True)
    return rows


def match_records(experiment, value, games, seed, opening_plies, run_id):
    """Use paired openings and a fresh, recorded seed rule for every game."""
    if type(games) is not int or games < 2 or games % 2:
        raise ValueError("games must be a positive even count")
    openings = generate_openings(games // 2, opening_plies, seed)
    records = []
    for index in range(games):
        game_seed = seed + index
        if experiment == "a2":
            a = MCTSAgent(simulations=value, seed=game_seed)
            b = AlphaBetaAgent(depth=4)
            name_a, name_b = f"mcts_s{value}", "alphabeta_d4"
        elif experiment == "a5":
            a = AlphaBetaAgent(depth=value)
            b = HeuristicAgent(seed=game_seed)
            name_a, name_b = f"alphabeta_d{value}", "heuristic"
        else:
            raise ValueError(experiment)
        record = play_game(ConnectFour(), a, b, openings[index // 2],
                           a_starts=index % 2 == 0, name_a=name_a, name_b=name_b)
        record.pair = f"{name_a}_vs_{name_b}"
        record.opening_id = index // 2
        record.game_id = f"{record.pair}-g{index:03d}"
        # Replay through the independent engine before accepting a result.
        reference = ReferenceGame()
        for action in record.moves:
            reference.step(action)
        winner = reference.winner()
        expected = None if winner is None else (1 if winner == (1 if record.a_starts else 2) else 2)
        assert reference.is_terminal() and record.winner == expected
        if experiment == "a2":
            assert all(m.simulations == value for m in record.move_logs if m.agent == name_a)
        records.append(record)
        if (index + 1) % 10 == 0:
            print(f"{run_id}: {index + 1}/{games} games", flush=True)
    return records


def summarize_match(records, seed):
    """Pool individual moves; bootstrap paired-opening scores, not independent games."""
    if not records or len(records) % 2:
        raise ValueError("Need complete opening pairs")
    for a, b in zip(records[::2], records[1::2]):
        if a.opening_id != b.opening_id or not a.a_starts or b.a_starts:
            raise ValueError("Records must be ordered in balanced opening pairs")
    wins = sum(r.winner == 1 for r in records)
    draws = sum(r.winner is None for r in records)
    values = [1 if r.winner == 1 else .5 if r.winner is None else 0 for r in records]
    pair_scores = [(a + b) / 2 for a, b in zip(values[::2], values[1::2])]
    lo, hi = bootstrap_ci(pair_scores, seed=seed)
    wlo, whi = wilson_interval(wins, len(records))
    times = [t for r in records for t in r.times_ms_a]
    return dict(games=len(records), wins=wins, draws=draws, losses=len(records)-wins-draws,
                win_rate=wins/len(records), score=score(wins, draws, len(records)),
                score_ci_low=lo, score_ci_high=hi, win_wilson_low=wlo, win_wilson_high=whi,
                mean_ms=mean(times), p95_ms=p95(times),
                mean_nodes=sum(r.nodes_a for r in records)/len(times),
                mean_simulations=sum(r.simulations_a for r in records)/len(times),
                wins_as_first=sum(r.winner == 1 for r in records if r.a_starts),
                wins_as_second=sum(r.winner == 1 for r in records if not r.a_starts))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", choices=CONFIGS, required=True)
    args = parser.parse_args()
    exp = args.experiment
    config_path = Path(f"configs/{CONFIGS[exp]}.yaml")
    config = yaml.safe_load(config_path.read_text())
    if exp in ("a2", "a5") and config["opponent"] != {"a2": "alphabeta_depth4", "a5": "heuristic"}[exp]:
        raise ValueError("Unsupported opponent for this experiment")
    seed = config["seed"]
    run_id = new_run_id(f"ablation-{exp}", seed)
    started = utc_now()
    raw_path = Path(f"results/logs/positions_{run_id}.csv")
    metrics_path = Path(f"results/logs/ablation_{run_id}.csv")
    summary_path = Path(f"results/tables/{run_id}.csv")
    if any(p.exists() for p in (raw_path, metrics_path, summary_path)):
        raise FileExistsError(run_id)
    command = f"PYTHONPATH=src python scripts/run_search_ablations.py --experiment {exp}"
    manifest = make_manifest_row(run_id, config_file=config_path, command=command,
                                 seed=seed, started_at=started)
    summaries = []
    print(f"START {run_id}", flush=True)
    try:
        if exp in ("a1", "a5"):
            settings = config.get("configs", [{"pruning": True, "ordering": True}])
            rows = measure_positions(read_positions(config["positions"]), config["depths"],
                                     settings, config.get("repeat", config.get("repeat_per_position")),
                                     run_id, raw_path)
            for depth in config["depths"]:
                for flags in settings:
                    subset = [r for r in rows if r["depth"] == depth and r["status"] == "measured"
                              and r["pruning"] == flags["pruning"] and r["ordering"] == flags["ordering"]]
                    summaries.append(dict(run_id=run_id, phase="positions", depth=depth,
                        pruning=int(flags["pruning"]), ordering=int(flags["ordering"]),
                        measurements=len(subset), positions=len({r["position_id"] for r in subset}),
                        mean_nodes=mean([r["nodes"] for r in subset]),
                        mean_ms=mean([r["time_ms"] for r in subset]), p95_ms=p95([r["time_ms"] for r in subset]),
                        raw_log_path=str(raw_path)))
        if exp in ("a2", "a5"):
            param = "simulations" if exp == "a2" else "depth"
            for value in config["simulations" if exp == "a2" else "depths"]:
                subrun = f"{run_id}-{param}{value}"
                records = match_records(exp, value, config["games_per_budget" if exp == "a2" else "games_per_depth"],
                                        seed, config["opening_plies"], subrun)
                games_path, moves_path = save_run(records, run_id=subrun)
                summaries.append(dict(run_id=run_id, match_run_id=subrun, phase="games", **{param: value},
                                      **summarize_match(records, seed),
                                      raw_log_path=str(games_path), moves_log_path=str(moves_path)))
                fields = tuple(dict.fromkeys(k for row in summaries for k in row))
                write_csv(summary_path, fields, summaries)
        fields = tuple(dict.fromkeys(k for row in summaries for k in row))
        write_csv(summary_path, fields, summaries)
        write_csv(config["output"], fields, summaries)
        metrics = []
        for row in summaries:
            cid = f"{row['phase']}-" + "-".join(f"{k}{row[k]}" for k in ("depth", "simulations", "pruning", "ordering") if k in row)
            for metric in ("mean_nodes", "mean_ms", "p95_ms", "win_rate", "score", "score_ci_low", "score_ci_high"):
                if metric in row:
                    metrics.append(dict(run_id=run_id, experiment=exp.upper(), config_id=cid,
                        seed=seed, param_name="simulations" if exp == "a2" else "depth",
                        param_value=row.get("simulations", row.get("depth")), metric=metric,
                        value=row[metric], raw_log_path=row["raw_log_path"]))
        write_csv(metrics_path, ABLATION_FIELDS, metrics)
        manifest["status"] = "completed"
    except BaseException:
        manifest["status"] = "failed"
        raise
    finally:
        manifest["finished_at"] = utc_now()
        manifest["notes"] = (f"K4 {exp.upper()}; sequential CPU; per-game RNG seed=seed+game index; "
                              f"paired openings; {summary_path}; "
                              f"positions_hash={config_hash(config['positions']) if 'positions' in config else 'n/a'}")
        append_manifest("results/logs/run_manifest.csv", manifest)
    print(json.dumps(summaries, indent=2), flush=True)


if __name__ == "__main__":
    main()
