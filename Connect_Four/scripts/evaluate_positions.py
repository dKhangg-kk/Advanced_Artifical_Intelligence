#!/usr/bin/env python3
"""Do do dung cua 6 tac tu tren bo vi tri kiem thu ``tests/data/positions.csv`` (Y6).

Moi vi tri duoc phat lai tren engine, roi tung tac tu (cau hinh mac dinh trong
``configs/agents_y6.yaml``, checkpoint da dong bang) chon mot nuoc:

* ``win_now``      - vi tri co nuoc thang ngay: dung neu chon mot cot thang;
* ``block``        - khong thang ngay nhung doi thu co nuoc thang: dung neu chan duoc
                     (``double_threat`` la tap con co doi thu ca hai nuoc thang);
* ``quiet``        - khong co nuoc chien thuat: chi kiem tra nuoc hop le.

Tac tu co ngau nhien (random, heuristic, alphabeta, mcts) duoc chay lap voi nhieu
seed va bao cao ty le chon dung; nn va dqn la xac dinh (argmax) nen chay mot lan.
Vi tri da ket thuc (``draw-full-board``) khong co nuoc de chon nen bi bo qua.

    PYTHONPATH=src python scripts/evaluate_positions.py
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from connect_four.evaluation.config import build_agent, load_agent_config  # noqa: E402
from connect_four.evaluation.metrics import wilson_interval  # noqa: E402
from connect_four.game.engine import ConnectFour  # noqa: E402

AGENTS = ["random", "heuristic", "alphabeta", "mcts", "nn", "dqn"]
REPEATS = {"random": 200, "heuristic": 20, "alphabeta": 10, "mcts": 20, "nn": 1, "dqn": 1}
POSITIONS = Path("tests/data/positions.csv")


def _cols(value: str) -> list[int]:
    return [] if value == "-" else [int(x) for x in value.split()]


def situation_of(position: dict[str, str]) -> str:
    if _cols(position["winning_moves"]):
        return "win_now"
    if _cols(position["blocking_moves"]):
        return "block"
    return "quiet"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--agent-config", default="configs/agents_y6.yaml")
    parser.add_argument("--out-prefix", default="results/tables/y6_position")
    parser.add_argument("--seed", type=int, default=20261118)
    args = parser.parse_args(argv)

    settings = load_agent_config(args.agent_config)
    with POSITIONS.open(encoding="utf-8", newline="") as stream:
        positions = list(csv.DictReader(stream))

    choice_rows: list[dict[str, object]] = []
    for agent_name in AGENTS:
        for position in positions:
            game = ConnectFour()
            for column in (int(x) for x in position["moves"].split()):
                game.step(column)
            if game.is_terminal():
                continue
            assert game.current_player == int(position["side_to_move"]), position["id"]
            legal = game.legal_actions()
            wins, blocks = _cols(position["winning_moves"]), _cols(position["blocking_moves"])
            situation = situation_of(position)
            target = wins if situation == "win_now" else blocks if situation == "block" else legal
            counts: Counter[int] = Counter()
            for rep in range(REPEATS[agent_name]):
                agent = build_agent(agent_name, settings, seed=args.seed + rep)
                action = agent.choose(game.clone())
                assert action in legal, (agent_name, position["id"], action)
                counts[action] += 1
            total = sum(counts.values())
            hits = sum(counts[c] for c in target)
            choice_rows.append(
                {
                    "agent": agent_name,
                    "position_id": position["id"],
                    "situation": situation,
                    "double_threat": position["id"].startswith("double-threat"),
                    "target_columns": " ".join(map(str, target)) if situation != "quiet" else "legal",
                    "repeats": total,
                    "hits": hits,
                    "hit_rate": hits / total,
                    "modal_action": counts.most_common(1)[0][0],
                    "action_counts": " ".join(f"{c}:{n}" for c, n in sorted(counts.items())),
                }
            )

    out_choices = Path(f"{args.out_prefix}_choices.csv")
    out_summary = Path(f"{args.out_prefix}_accuracy.csv")
    out_choices.parent.mkdir(parents=True, exist_ok=True)
    with out_choices.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(choice_rows[0]))
        writer.writeheader()
        for r in choice_rows:
            writer.writerow({k: (f"{v:.6f}" if isinstance(v, float) else v) for k, v in r.items()})

    groups = [("win_now", lambda r: r["situation"] == "win_now"),
              ("block", lambda r: r["situation"] == "block"),
              ("double_threat", lambda r: r["double_threat"]),
              ("quiet_legal", lambda r: r["situation"] == "quiet")]
    summary_rows = []
    for agent_name in AGENTS:
        for label, pick in groups:
            sel = [r for r in choice_rows if r["agent"] == agent_name and pick(r)]
            attempts = sum(r["repeats"] for r in sel)
            hits = sum(r["hits"] for r in sel)
            low, high = wilson_interval(hits, attempts)
            summary_rows.append(
                {
                    "agent": agent_name, "situation": label, "positions": len(sel), "attempts": attempts,
                    "hits": hits, "accuracy": hits / attempts,
                    "wilson95_low": max(0.0, low), "wilson95_high": min(1.0, high),
                    "note": "n_attempts = positions x repeats; cac lan lap cua cung mot vi tri khong doc lap"
                            if REPEATS[agent_name] > 1 else "xac dinh: 1 lan/vi tri",
                }
            )
    with out_summary.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summary_rows[0]))
        writer.writeheader()
        for r in summary_rows:
            writer.writerow({k: (f"{v:.6f}" if isinstance(v, float) else v) for k, v in r.items()})

    print(f"{'agent':<10}" + "".join(f"{label:>15}" for label, _ in groups))
    for agent_name in AGENTS:
        cells = [next(r for r in summary_rows if r["agent"] == agent_name and r["situation"] == label)
                 for label, _ in groups]
        print(f"{agent_name:<10}" + "".join(f"{c['accuracy']:>15.3f}" for c in cells))
    print(out_choices, out_summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
