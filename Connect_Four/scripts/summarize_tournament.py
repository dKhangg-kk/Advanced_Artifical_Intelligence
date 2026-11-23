#!/usr/bin/env python3
"""Tong hop log giai dau Round-Robin thanh bang va hinh cho Chuong 4 (Y6).

Chi doc log tho ``results/logs/games_<run_id>.csv`` va ``moves_<run_id>.csv``;
khong sua log. Moi bang ghi lai ``run_id`` va duong dan log nguon de truy nguoc.

Chay tu ``Connect_Four/``:

    PYTHONPATH=src python scripts/summarize_tournament.py \
        --prefix tournament-default-20261118T151500Z-s20261118 --label default

Dau ra (``<label>`` vi du ``default`` hoac ``timed``):

* ``results/tables/y6_<label>_pair_summary.csv``  - moi cap: W/D/L, score, Wilson 95%,
  thoi gian trung binh/p95 moi nuoc, so nut/mo phong, over_budget;
* ``results/tables/y6_<label>_agent_summary.csv`` - gop theo tac tu;
* ``results/tables/y6_<label>_score_matrix.csv``  - ma tran score hang-gap-cot;
* ``results/tables/y6_<label>_first_move.csv``    - loi the di truoc theo cap;
* ``results/figures/y6_<label>_score_matrix.png`` va ``y6_<label>_latency.png``.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from connect_four.evaluation.metrics import mean, p95, wilson_interval  # noqa: E402

AGENT_ORDER = ["random", "heuristic", "alphabeta", "mcts", "nn", "dqn"]
LOG_DIR = Path("results/logs")
TABLE_DIR = Path("results/tables")
FIG_DIR = Path("results/figures")


def _bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes"}


def _ci(points: float, total: int) -> tuple[float, float]:
    low, high = wilson_interval(points, total)
    return max(0.0, low), min(1.0, high)


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def load_pairs(prefix: str) -> list[dict[str, Any]]:
    """Doc moi cap thuoc mot lan chay giai dau."""
    pairs = []
    for games_path in sorted(LOG_DIR.glob(f"games_{prefix}-*-vs-*.csv")):
        run_id = games_path.stem[len("games_"):]
        moves_path = LOG_DIR / f"moves_{run_id}.csv"
        games = _read(games_path)
        moves = _read(moves_path) if moves_path.exists() else []
        pairs.append({"run_id": run_id, "games_path": games_path, "moves_path": moves_path,
                      "games": games, "moves": moves})
    if not pairs:
        raise SystemExit(f"Khong tim thay log games_{prefix}-*-vs-*.csv trong {LOG_DIR}")
    return pairs


def _agent_move_stats(moves: list[dict[str, str]], agent: str) -> dict[str, float]:
    rows = [m for m in moves if m["agent"] == agent]
    times = [float(m["time_ms"]) for m in rows]
    nodes = [float(m["nodes"] or 0) for m in rows]
    sims = [float(m["simulations"] or 0) for m in rows]
    return {
        "decisions": len(rows),
        "times": times,
        "mean_ms": mean(times) if times else 0.0,
        "p95_ms": p95(times) if times else 0.0,
        "mean_nodes": mean(nodes) if nodes else 0.0,
        "mean_sims": mean(sims) if sims else 0.0,
        "nodes": nodes,
        "sims": sims,
    }


def pair_summary(pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for pair in pairs:
        games = pair["games"]
        a, b = games[0]["agent_a"], games[0]["agent_b"]
        n = len(games)
        wins_a = sum(g["winner"] == "a" for g in games)
        wins_b = sum(g["winner"] == "b" for g in games)
        draws = sum(g["winner"] == "draw" for g in games)
        low, high = _ci(wins_a + 0.5 * draws, n)
        sa = _agent_move_stats(pair["moves"], a)
        sb = _agent_move_stats(pair["moves"], b)
        rows.append({
            "agent_a": a, "agent_b": b, "games": n,
            "wins_a": wins_a, "draws": draws, "wins_b": wins_b,
            "score_a": (wins_a + 0.5 * draws) / n,
            "score_ci95_low": low, "score_ci95_high": high,
            "a_starts": sum(_bool(g["a_starts"]) for g in games),
            "b_starts": sum(not _bool(g["a_starts"]) for g in games),
            "mean_moves_per_game": mean([float(g["n_moves"]) for g in games]),
            "mean_ms_a_per_move": sa["mean_ms"], "p95_ms_a_per_move": sa["p95_ms"],
            "mean_ms_b_per_move": sb["mean_ms"], "p95_ms_b_per_move": sb["p95_ms"],
            "mean_nodes_a_per_move": sa["mean_nodes"], "mean_nodes_b_per_move": sb["mean_nodes"],
            "mean_simulations_a_per_move": sa["mean_sims"], "mean_simulations_b_per_move": sb["mean_sims"],
            "over_budget_games_a": sum(_bool(g["over_budget_a"]) for g in games),
            "over_budget_games_b": sum(_bool(g["over_budget_b"]) for g in games),
            "run_id": pair["run_id"], "source_games": str(pair["games_path"]),
        })
    return rows


def agent_summary(pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    acc: dict[str, dict[str, Any]] = {}
    for pair in pairs:
        games = pair["games"]
        a, b = games[0]["agent_a"], games[0]["agent_b"]
        for name, side in ((a, "a"), (b, "b")):
            item = acc.setdefault(name, {"games": 0, "wins": 0, "draws": 0, "losses": 0,
                                         "times": [], "nodes": [], "sims": [], "over": 0})
            other = "b" if side == "a" else "a"
            item["games"] += len(games)
            item["wins"] += sum(g["winner"] == side for g in games)
            item["losses"] += sum(g["winner"] == other for g in games)
            item["draws"] += sum(g["winner"] == "draw" for g in games)
            item["over"] += sum(_bool(g[f"over_budget_{side}"]) for g in games)
            stats = _agent_move_stats(pair["moves"], name)
            item["times"].extend(stats["times"])
            item["nodes"].extend(stats["nodes"])
            item["sims"].extend(stats["sims"])
    rows = []
    for name in [n for n in AGENT_ORDER if n in acc]:
        item = acc[name]
        n = item["games"]
        low, high = _ci(item["wins"] + 0.5 * item["draws"], n)
        rows.append({
            "agent": name, "games": n, "wins": item["wins"], "draws": item["draws"],
            "losses": item["losses"], "score": (item["wins"] + 0.5 * item["draws"]) / n,
            "score_ci95_low": low, "score_ci95_high": high,
            "decisions": len(item["times"]),
            "mean_ms_per_move": mean(item["times"]) if item["times"] else 0.0,
            "p95_ms_per_move": p95(item["times"]) if item["times"] else 0.0,
            "max_ms_per_move": max(item["times"]) if item["times"] else 0.0,
            "mean_nodes_per_move": mean(item["nodes"]) if item["nodes"] else 0.0,
            "mean_simulations_per_move": mean(item["sims"]) if item["sims"] else 0.0,
            "over_budget_games": item["over"],
        })
    return rows


def score_matrix(pair_rows: list[dict[str, Any]]) -> tuple[list[str], dict[tuple[str, str], dict[str, float]]]:
    """matrix[(row, col)] = score cua tac tu hang khi gap tac tu cot."""
    names = [n for n in AGENT_ORDER if any(n in (r["agent_a"], r["agent_b"]) for r in pair_rows)]
    cells: dict[tuple[str, str], dict[str, float]] = {}
    for r in pair_rows:
        a, b, n = r["agent_a"], r["agent_b"], r["games"]
        cells[(a, b)] = {"score": r["score_a"], "low": r["score_ci95_low"], "high": r["score_ci95_high"],
                         "w": r["wins_a"], "d": r["draws"], "l": r["wins_b"], "n": n}
        low_b, high_b = 1 - r["score_ci95_high"], 1 - r["score_ci95_low"]
        cells[(b, a)] = {"score": 1 - r["score_a"], "low": low_b, "high": high_b,
                         "w": r["wins_b"], "d": r["draws"], "l": r["wins_a"], "n": n}
    return names, cells


def first_move(pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    total_games = total_first = total_second = total_draw = 0
    for pair in pairs:
        games = pair["games"]
        a, b = games[0]["agent_a"], games[0]["agent_b"]
        first_wins = second_wins = draws = 0
        for g in games:
            starter = "a" if _bool(g["a_starts"]) else "b"
            if g["winner"] == "draw":
                draws += 1
            elif g["winner"] == starter:
                first_wins += 1
            else:
                second_wins += 1
        n = len(games)
        low, high = _ci(first_wins + 0.5 * draws, n)
        a_first = [g for g in games if _bool(g["a_starts"])]
        b_first = [g for g in games if not _bool(g["a_starts"])]
        rows.append({
            "agent_a": a, "agent_b": b, "games": n,
            "first_player_wins": first_wins, "second_player_wins": second_wins, "draws": draws,
            "first_player_score": (first_wins + 0.5 * draws) / n,
            "first_player_score_ci95_low": low, "first_player_score_ci95_high": high,
            "a_score_when_a_first": _side_score(a_first, "a"),
            "a_score_when_b_first": _side_score(b_first, "a"),
            "run_id": pair["run_id"],
        })
        total_games += n
        total_first += first_wins
        total_second += second_wins
        total_draw += draws
    low, high = _ci(total_first + 0.5 * total_draw, total_games)
    rows.append({
        "agent_a": "ALL", "agent_b": "ALL", "games": total_games,
        "first_player_wins": total_first, "second_player_wins": total_second, "draws": total_draw,
        "first_player_score": (total_first + 0.5 * total_draw) / total_games,
        "first_player_score_ci95_low": low, "first_player_score_ci95_high": high,
        "a_score_when_a_first": "", "a_score_when_b_first": "", "run_id": "all pairs",
    })
    return rows


def _side_score(games: list[dict[str, str]], side: str) -> float:
    if not games:
        return float("nan")
    wins = sum(g["winner"] == side for g in games)
    draws = sum(g["winner"] == "draw" for g in games)
    return (wins + 0.5 * draws) / len(games)


def _write(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (f"{v:.6f}" if isinstance(v, float) else v) for k, v in row.items()})


def plot(label: str, title: str, names: list[str], cells: dict, agents: list[dict[str, Any]]) -> list[Path]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    out = []
    grid = np.full((len(names), len(names)), np.nan)
    for i, r in enumerate(names):
        for j, c in enumerate(names):
            if (r, c) in cells:
                grid[i, j] = cells[(r, c)]["score"]
    fig, ax = plt.subplots(figsize=(7.6, 6.4))
    im = ax.imshow(grid, cmap="RdBu", vmin=0, vmax=1)
    for i, r in enumerate(names):
        for j, c in enumerate(names):
            if (r, c) in cells:
                cell = cells[(r, c)]
                color = "white" if abs(cell["score"] - 0.5) > 0.3 else "black"
                ax.text(j, i, f"{cell['score']:.2f}\n[{cell['low']:.2f}, {cell['high']:.2f}]",
                        ha="center", va="center", fontsize=8, color=color)
            else:
                ax.text(j, i, "—", ha="center", va="center", color="#888888")
    ax.set_xticks(range(len(names)), names)
    ax.set_yticks(range(len(names)), names)
    ax.set_xlabel("Đối thủ (cột)")
    ax.set_ylabel("Tác tử (hàng)")
    ax.set_title(title)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="score = (W + 0.5D) / N")
    fig.tight_layout()
    path = FIG_DIR / f"y6_{label}_score_matrix.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    out.append(path)

    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    x = np.arange(len(agents))
    means = [max(a["mean_ms_per_move"], 1e-3) for a in agents]
    p95s = [max(a["p95_ms_per_move"], 1e-3) for a in agents]
    ax.bar(x - 0.2, means, 0.4, label="trung bình", color="#4C72B0")
    ax.bar(x + 0.2, p95s, 0.4, label="p95", color="#DD8452")
    ax.set_yscale("log")
    ax.set_xticks(x, [a["agent"] for a in agents])
    ax.set_ylabel("ms mỗi nước (thang log)")
    ax.set_title(f"Thời gian mỗi nước — {title}")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    path = FIG_DIR / f"y6_{label}_latency.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    out.append(path)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Tong hop giai dau Round-Robin")
    parser.add_argument("--prefix", required=True, help="run prefix, vi du tournament-default-...-s20261118")
    parser.add_argument("--label", required=True, help="ten ngan cho file dau ra: default | timed")
    parser.add_argument("--title", default=None)
    args = parser.parse_args(argv)

    pairs = load_pairs(args.prefix)
    pair_rows = pair_summary(pairs)
    agent_rows = agent_summary(pairs)
    names, cells = score_matrix(pair_rows)
    matrix_rows = []
    for r in names:
        row: dict[str, Any] = {"agent": r}
        for c in names:
            cell = cells.get((r, c))
            row[c] = "" if cell is None else f"{cell['score']:.3f} [{cell['low']:.3f}, {cell['high']:.3f}] {cell['w']}-{cell['d']}-{cell['l']}"
        matrix_rows.append(row)

    _write(TABLE_DIR / f"y6_{args.label}_pair_summary.csv", pair_rows)
    _write(TABLE_DIR / f"y6_{args.label}_agent_summary.csv", agent_rows)
    _write(TABLE_DIR / f"y6_{args.label}_score_matrix.csv", matrix_rows)
    _write(TABLE_DIR / f"y6_{args.label}_first_move.csv", first_move(pairs))
    figures = plot(args.label, args.title or f"Giải đấu {args.label}", names, cells, agent_rows)
    print(f"{len(pairs)} cap, {sum(r['games'] for r in pair_rows)} van -> results/tables/y6_{args.label}_*.csv")
    for path in figures:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
