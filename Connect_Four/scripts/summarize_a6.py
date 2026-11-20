#!/usr/bin/env python3
"""Tong hop thi nghiem A6 (doi thu huan luyen DQN: Heuristic / Random / tu choi) cho muc 4.5 (Y5).

Doc ``results/tables/ablation_a6_results.csv``, ``ablation_a6_head_to_head.csv``,
``ablation_a6_positions.csv`` (do ``run_ablation_a6.py --merge`` tao) va ghi:

* ``results/tables/ablation_a6_summary.csv``: moi (doi thu huan luyen, moc, doi thu danh
  gia): so seed, trung binh, do lech chuan mau, min, max cua score validation;
* ``results/figures/ablation_a6_score_vs_episode.png``: score validation theo moc;
* ``results/figures/ablation_a6_training_curves.png``: ty le thang khi huan luyen
  (cua so truot 500 episode) va epsilon theo episode.

Chay tu ``Connect_Four/``:

    PYTHONPATH=src python scripts/summarize_a6.py
"""

from __future__ import annotations

import csv
from pathlib import Path
import statistics

TABLE = Path("results/tables/ablation_a6_results.csv")
SUMMARY = Path("results/tables/ablation_a6_summary.csv")
POOLED = Path("results/tables/ablation_a6_pooled.csv")
H2H = Path("results/tables/ablation_a6_head_to_head.csv")
FIGURE = Path("results/figures/ablation_a6_score_vs_episode.png")
CURVES = Path("results/figures/ablation_a6_training_curves.png")
ORDER = ["heuristic", "random", "selfplay"]
LABEL = {"heuristic": "đối thủ Heuristic (A4 default_decay)", "random": "đối thủ Random",
         "selfplay": "tự chơi (5 bản sao gần nhất)"}
COLOR = {"heuristic": "#4C72B0", "random": "#55A868", "selfplay": "#C44E52"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def summarize(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    groups: dict[tuple[str, int, str], list[dict[str, str]]] = {}
    for row in rows:
        groups.setdefault((row["train_opponent"], int(row["episode"]), row["opponent"]), []).append(row)
    out = []
    for (train, episode, opponent), items in sorted(groups.items(), key=lambda kv: (ORDER.index(kv[0][0]), kv[0][1], kv[0][2])):
        scores = [float(r["score"]) for r in items]
        out.append({
            "train_opponent": train, "episode": episode, "opponent": opponent, "n_seeds": len(items),
            "seeds": " ".join(sorted((r["seed"] for r in items), key=int)), "games_per_seed": items[0]["games"],
            "score_mean": statistics.fmean(scores),
            "score_sd": statistics.stdev(scores) if len(scores) > 1 else 0.0,
            "score_min": min(scores), "score_max": max(scores),
            "wins_total": sum(int(r["wins"]) for r in items), "draws_total": sum(int(r["draws"]) for r in items),
            "losses_total": sum(int(r["losses"]) for r in items),
            "train_win_rate_last500": statistics.fmean(float(r["train_win_rate_last500"]) for r in items),
            "train_mean_reward_last500": statistics.fmean(float(r["train_mean_reward_last500"]) for r in items),
            "training_elapsed_seconds_mean": statistics.fmean(float(r["training_elapsed_seconds"]) for r in items),
            "run_ids": ";".join(sorted({r["run_id"] for r in items})),
        })
    return out


def pooled(rows: list[dict[str, str]], h2h: list[dict[str, str]], episode: int = 10000) -> list[dict[str, object]]:
    """Gop 3 seed o moc cuoi: W/D/L cong don va khoang Wilson tren 300 van.

    Cac seed la cac mo hinh khac nhau nen day la uoc luong cho 'mot mo hinh ngau nhien cua
    cau hinh nay'; khoang Wilson coi 300 van doc lap, bo qua bien thien giua seed (ghi ro trong bao cao).
    """
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from connect_four.evaluation.metrics import wilson_interval

    out = []
    sources = [(r["train_opponent"], r["opponent"], r) for r in rows if int(r["episode"]) == episode]
    sources += [(h["train_opponent"], "final_pt", h) for h in h2h]
    for train in ORDER:
        for opponent in ("random", "heuristic", "final_pt"):
            items = [r for t, o, r in sources if t == train and o == opponent]
            if not items:
                continue
            w = sum(int(r["wins"]) for r in items)
            d = sum(int(r["draws"]) for r in items)
            l_ = sum(int(r["losses"]) for r in items)
            n = w + d + l_
            low, high = wilson_interval(w + 0.5 * d, n)
            out.append({"train_opponent": train, "episode": episode, "opponent": opponent, "n_seeds": len(items),
                        "seeds": " ".join(sorted((r["seed"] for r in items), key=int)), "games": n, "wins": w,
                        "draws": d, "losses": l_, "score": (w + 0.5 * d) / n,
                        "score_ci95_low": max(0.0, low), "score_ci95_high": min(1.0, high),
                        "run_ids": ";".join(sorted({r["run_id"] for r in items}))})
    return out


def write(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (f"{v:.6f}" if isinstance(v, float) else v) for k, v in row.items()})


def plot_scores(rows: list[dict[str, str]]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    episodes = sorted({int(r["episode"]) for r in rows})
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    for ax, opponent, title in zip(axes, ("random", "heuristic"), ("Validation gặp Random", "Validation gặp Heuristic")):
        for train in ORDER:
            sel = [r for r in rows if r["train_opponent"] == train and r["opponent"] == opponent]
            if not sel:
                continue
            means, lows, highs = [], [], []
            for ep in episodes:
                vals = [float(r["score"]) for r in sel if int(r["episode"]) == ep]
                means.append(statistics.fmean(vals))
                lows.append(min(vals))
                highs.append(max(vals))
            n = len({r["seed"] for r in sel})
            ax.plot(episodes, means, marker="o", color=COLOR[train], label=f"{LABEL[train]} (n={n} seed)")
            ax.fill_between(episodes, lows, highs, color=COLOR[train], alpha=0.15)
        ax.set_xscale("log")
        ax.set_xticks(episodes, [f"{e:,}".replace(",", ".") for e in episodes])
        ax.set_xlabel("Số episode huấn luyện")
        ax.set_title(title)
        ax.axhline(0.5, color="#888888", lw=0.8, ls=":")
        ax.set_ylim(-0.02, 1.02)
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("score (đường: trung bình seed; vùng: min–max)")
    axes[0].legend(fontsize=8, loc="lower right")
    fig.suptitle("A6: đối thủ huấn luyện DQN (100 ván mỗi điểm, seed validation 20261102/20261103)")
    fig.tight_layout()
    FIGURE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE, dpi=150)
    plt.close(fig)


def plot_curves(rows: list[dict[str, str]], window: int = 500) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    logs = sorted({(r["train_opponent"], int(r["seed"]), r["training_log"]) for r in rows},
                  key=lambda t: (ORDER.index(t[0]), t[1]))
    fig, ax = plt.subplots(figsize=(10, 4.2))
    for train, seed, log in logs:
        path = Path(log)
        if not path.is_file():
            continue
        data = read(path)
        wins = [1.0 if d["result"] == "win" else 0.0 for d in data]
        xs, ys, acc = [], [], 0.0
        for i, w in enumerate(wins):
            acc += w
            if i >= window:
                acc -= wins[i - window]
            if i + 1 >= window:
                xs.append(i + 1)
                ys.append(acc / window)
        ax.plot(xs, ys, color=COLOR[train], alpha=0.85, lw=1.1,
                ls={0: "-", 42: "--", 2026: ":"}.get(seed, "-"), label=f"{LABEL[train]}, seed {seed}")
    ax.set_xlabel("Episode")
    ax.set_ylabel(f"Tỷ lệ thắng khi huấn luyện (trượt {window} episode)")
    ax.set_title("Tỷ lệ thắng trong lúc huấn luyện (ε-greedy) — mỗi đường đo trên đối thủ huấn luyện của chính nó")
    ax.set_ylim(-0.02, 1.02)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7, ncol=3, loc="lower right")
    fig.tight_layout()
    fig.savefig(CURVES, dpi=150)
    plt.close(fig)


def main() -> int:
    rows = read(TABLE)
    summary = summarize(rows)
    write(SUMMARY, summary)
    write(POOLED, pooled(rows, read(H2H)))
    plot_scores(rows)
    plot_curves(rows)
    print(f"{len(rows)} dong -> {SUMMARY} ({len(summary)} nhom), {FIGURE}, {CURVES}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
