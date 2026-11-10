"""K1: 200 van Heuristic vs Random, luu log va kiem tra nguong 95%.

Chay tu Connect_Four: PYTHONPATH=src python scripts/evaluate_k1.py
"""

import json
from pathlib import Path

from connect_four.agents.heuristic import HeuristicAgent
from connect_four.agents.random_agent import RandomAgent
from connect_four.evaluation.match import MatchConfig, play_match, save_run
from connect_four.evaluation.runlog import (
    append_manifest, make_manifest_row, new_run_id, utc_now, write_csv,
)
from connect_four.game import ConnectFour


def main() -> None:
    """Chay cau hinh K1 co dinh; luu ca lan khong dat, bao loi neu duoi 95%."""
    config_path = Path("configs/k1_random_heuristic.json")
    config = json.loads(config_path.read_text())
    match = MatchConfig(**config["match"])
    assert match.games_per_pair == 200 and match.openings == 100
    run_id = new_run_id("k1-heuristic-random", match.seed)
    started = utc_now()
    records = play_match(
        HeuristicAgent(**config["heuristic"]), RandomAgent(**config["random"]), match,
    )
    # Doi chieu lai ket qua tung van tu chuoi nuoc truoc khi cong bo so lieu.
    assert len(records) == 200 and sum(r.a_starts for r in records) == 100
    for record in records:
        game = ConnectFour()
        for action in record.moves:
            game.step(action)
        assert game.is_terminal()
        a_player = 1 if record.a_starts else 2
        expected = None if game.winner() is None else (1 if game.winner() == a_player else 2)
        assert record.winner == expected
    games_path, moves_path = save_run(records, run_id=run_id)
    wins = sum(r.winner == 1 for r in records)
    draws = sum(r.winner is None for r in records)
    losses = len(records) - wins - draws
    rate = wins / len(records)
    summary = {"run_id": run_id, "games": len(records), "wins": wins,
               "draws": draws, "losses": losses, "win_rate": rate}
    write_csv(f"results/tables/{run_id}.csv", tuple(summary), [summary])
    row = make_manifest_row(
        run_id, config_file=config_path, seed=match.seed,
        command="PYTHONPATH=src python scripts/evaluate_k1.py",
        started_at=started, finished_at=utc_now(),
        status="completed" if rate >= .95 else "failed",
        notes=(f"Issue #12; {wins}W/{draws}D/{losses}L; "
               f"seeds heuristic={config['heuristic']['seed']}, random={config['random']['seed']}; "
               f"{games_path}; {moves_path}"),
    )
    append_manifest("results/logs/run_manifest.csv", row)
    print(json.dumps(summary))
    assert rate >= .95, f"Heuristic chi thang {wins}/200; can it nhat 190/200"


if __name__ == "__main__":
    main()
