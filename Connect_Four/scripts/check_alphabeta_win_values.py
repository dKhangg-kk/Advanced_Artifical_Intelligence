#!/usr/bin/env python3
"""Kiem tra gia tri goc cua Alpha-Beta (do sau 5, khong cat tia) tren cac vi tri thang ngay.

Muc dich phan tich loi (Y6): tai cac vi tri co nuoc thang ngay, in gia tri chinh xac
cua tung nuoc o do sau 5 de xem nuoc thang ngay co bi nuoc khac vuot diem hay khong.
Chi DOC mat Alpha-Beta/Heuristic cua Khang, khong sua. Ghi ``results/tables/y6_alphabeta_root_values.csv``.

    PYTHONPATH=src python scripts/check_alphabeta_win_values.py
"""
from __future__ import annotations

import csv
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from connect_four.agents.alphabeta import AlphaBetaAgent  # noqa: E402
from connect_four.game.engine import ConnectFour  # noqa: E402

OUT = Path("results/tables/y6_alphabeta_root_values.csv")


def main() -> int:
    with Path("tests/data/positions.csv").open(encoding="utf-8", newline="") as stream:
        positions = list(csv.DictReader(stream))
    rows = []
    for pos in positions:
        wins = [] if pos["winning_moves"] == "-" else [int(x) for x in pos["winning_moves"].split()]
        if not wins:
            continue
        game = ConnectFour()
        for column in pos["moves"].split():
            game.step(int(column))
        me = game.current_player
        exact = AlphaBetaAgent(depth=5, use_pruning=False, use_ordering=False, seed=0)
        values = {a: -exact._negamax(game.clone_after(a), 4, -float("inf"), float("inf"), me, -1)
                  for a in game.legal_actions()}
        chosen = AlphaBetaAgent(depth=5).choose(game.clone())  # cau hinh mac dinh: co cat tia, co sap xep
        best_win_value = max(values[w] for w in wins)
        best_other = max((v for a, v in values.items() if a not in wins), default=float("-inf"))
        rows.append({
            "position_id": pos["id"], "winning_columns": " ".join(map(str, wins)), "chosen_default": chosen,
            "chosen_is_winning": chosen in wins, "best_winning_move_value": best_win_value,
            "best_non_winning_value": best_other, "non_winning_exceeds": best_other > best_win_value,
            "values_by_column": " ".join(f"{a}:{v:.0f}" for a, v in sorted(values.items())),
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    missed = [r for r in rows if not r["chosen_is_winning"]]
    print(f"{len(rows)} vi tri thang ngay; Alpha-Beta mac dinh bo lo {len(missed)}; "
          f"{sum(r['non_winning_exceeds'] for r in rows)} vi tri co nuoc khong thang ngay vuot diem nuoc thang")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
