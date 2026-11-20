#!/usr/bin/env python3
"""Chan doan DQN: dieu kien khoi dau luc huan luyen khac luc danh gia (Y5/Y6).

Luc huan luyen (``train_dqn.py``) moi van bat dau tu ban trong, ben di truoc luan
phien, doi thu Heuristic duoc tao moi voi seed = seed + episode. Luc validation
va giai dau (``play_match``) moi van bat dau sau 4 nuoc khai cuoc ngau nhien.

Script do cung mot checkpoint (mac dinh la ``final.pt``) o cac do dai khai cuoc
ngau nhien 0, 2, 4 nuoc, voi hai doi thu Heuristic va Random, va dem so van khac
nhau (chuoi nuoc di) de biet DQN co lap lai mot so duong choi hay khong.

    PYTHONPATH=src python scripts/diagnose_dqn_openings.py
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from connect_four.agents import make_agent  # noqa: E402
from connect_four.evaluation.match import generate_openings, play_game  # noqa: E402
from connect_four.evaluation.metrics import wilson_interval  # noqa: E402
from connect_four.game.engine import ConnectFour  # noqa: E402

OUT = Path("results/tables/dqn_opening_diagnostic.csv")


def run(checkpoint: Path, opponent: str, plies: int, games: int, seed: int) -> dict[str, object]:
    if plies == 0:
        openings = [[] for _ in range(games // 2)]
    else:
        openings = generate_openings(games // 2, plies=plies, seed=seed)
    dqn = make_agent("dqn", checkpoint=checkpoint, epsilon=0.0, seed=0)
    wins = draws = losses = 0
    sequences: set[tuple[int, ...]] = set()
    plies_total = 0
    for g in range(games):
        opp = make_agent(opponent, seed=seed + 1 + g)  # seed moi van, giong luc huan luyen
        record = play_game(
            ConnectFour(), dqn, opp, openings[g // 2], a_starts=(g % 2 == 0),
            name_a="dqn", name_b=opponent,
        )
        wins += record.winner == 1
        losses += record.winner == 2
        draws += record.winner is None
        sequences.add(tuple(record.moves))
        plies_total += len(record.moves)
    low, high = wilson_interval(wins + 0.5 * draws, games)
    return {
        "opponent": opponent, "opening_plies": plies, "games": games, "unique_openings": len(openings),
        "wins": wins, "draws": draws, "losses": losses, "score": (wins + 0.5 * draws) / games,
        "wilson95_low": max(0.0, low), "wilson95_high": min(1.0, high),
        "distinct_games": len(sequences), "mean_plies_per_game": plies_total / games,
        "seed": seed,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--checkpoint", default="checkpoints/level6_dqn/final.pt")
    parser.add_argument("--games", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20261120)
    args = parser.parse_args(argv)

    rows = []
    for opponent in ("heuristic", "random"):
        for plies in (0, 2, 4):
            games = args.games if plies != 2 else 80  # chi co 49 khai cuoc 2 nuoc khac nhau
            row = run(Path(args.checkpoint), opponent, plies, games, args.seed)
            row["checkpoint"] = args.checkpoint
            rows.append(row)
            print(f"{opponent:<10} plies={plies} {row['wins']}-{row['draws']}-{row['losses']} "
                  f"score={row['score']:.3f} distinct={row['distinct_games']}/{games}", flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        for r in rows:
            writer.writerow({k: (f"{v:.6f}" if isinstance(v, float) else v) for k, v in r.items()})
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
