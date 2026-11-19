#!/usr/bin/env python3
"""Tong hop ablation A4 (epsilon decay x moc episode x seed) cho muc 4.5 (Y5).

Doc ``results/tables/ablation_a4_results.csv`` (do ``run_ablation_a4.py --merge``
tao tu cac o da chay) va ghi:

* ``results/tables/ablation_a4_summary.csv``: moi (decay, moc, doi thu): so seed,
  trung binh, do lech chuan mau, min, max cua score validation, cung trung binh
  cac chi so huan luyen 500 episode cuoi;
* ``results/figures/ablation_a4_score_vs_episode.png``.

Khong dung van giai dau. Chay tu ``Connect_Four/``:

    PYTHONPATH=src python scripts/summarize_a4.py
"""

from __future__ import annotations

import csv
from pathlib import Path
import statistics
import sys

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

TABLE = Path("results/tables/ablation_a4_results.csv")
SUMMARY = Path("results/tables/ablation_a4_summary.csv")
FIGURE = Path("results/figures/ablation_a4_score_vs_episode.png")
ORDER = ["fast_decay", "default_decay", "slow_decay", "default_decay_open4"]
LABEL = {"fast_decay": "decay 0.9990 (nhanh)", "default_decay": "decay 0.9995 (mặc định)",
         "slow_decay": "decay 0.9998 (chậm)",
         "default_decay_open4": "mở rộng: decay 0.9995 + 4 nước khai cuộc ngẫu nhiên khi huấn luyện"}
COLOR = {"fast_decay": "#C44E52", "default_decay": "#4C72B0", "slow_decay": "#55A868",
         "default_decay_open4": "#DD8452"}


def _f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def load() -> list[dict[str, str]]:
    with TABLE.open(encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def summarize(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    groups: dict[tuple[str, int, str], list[dict[str, str]]] = {}
    for row in rows:
        groups.setdefault((row["config_id"], int(row["episode"]), row["opponent"]), []).append(row)
    out = []
    for (config, episode, opponent), items in sorted(
        groups.items(), key=lambda kv: (ORDER.index(kv[0][0]) if kv[0][0] in ORDER else 9, kv[0][1], kv[0][2])
    ):
        scores = [_f(r, "score") for r in items]
        out.append(
            {
                "config_id": config,
                "decay": items[0]["decay"],
                "episode": episode,
                "opponent": opponent,
                "n_seeds": len(items),
                "seeds": " ".join(sorted(r["seed"] for r in items)),
                "games_per_seed": items[0]["games"],
                "score_mean": statistics.fmean(scores),
                "score_sd": statistics.stdev(scores) if len(scores) > 1 else 0.0,
                "score_min": min(scores),
                "score_max": max(scores),
                "epsilon_at_milestone": statistics.fmean(_f(r, "epsilon_at_milestone") for r in items),
                "train_mean_reward_last500": statistics.fmean(_f(r, "train_mean_reward_last500") for r in items),
                "train_win_rate_last500": statistics.fmean(_f(r, "train_win_rate_last500") for r in items),
                "train_mean_loss_last500": statistics.fmean(_f(r, "train_mean_loss_last500") for r in items),
                "training_elapsed_seconds_mean": statistics.fmean(_f(r, "training_elapsed_seconds") for r in items),
            }
        )
    return out


def write_summary(summary: list[dict[str, object]]) -> None:
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    with SUMMARY.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summary[0]))
        writer.writeheader()
        for row in summary:
            writer.writerow({k: (f"{v:.6f}" if isinstance(v, float) else v) for k, v in row.items()})


def plot(rows: list[dict[str, str]]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    episodes = sorted({int(r["episode"]) for r in rows})
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    for ax, opponent, title in zip(axes, ("random", "heuristic"), ("Validation vs Random", "Validation vs Heuristic")):
        for config in ORDER:
            sel = [r for r in rows if r["config_id"] == config and r["opponent"] == opponent]
            if not sel:
                continue
            means, lows, highs = [], [], []
            for ep in episodes:
                vals = [_f(r, "score") for r in sel if int(r["episode"]) == ep]
                means.append(statistics.fmean(vals) if vals else float("nan"))
                lows.append(min(vals) if vals else float("nan"))
                highs.append(max(vals) if vals else float("nan"))
            n_seeds = len({r["seed"] for r in sel})
            ax.plot(episodes, means, marker="o", color=COLOR[config], ls="--" if config.endswith("open4") else "-",
                    label=f"{LABEL[config]} (n={n_seeds} seed)")
            ax.fill_between(episodes, lows, highs, color=COLOR[config], alpha=0.15)
        ax.set_xscale("log")
        ax.set_xticks(episodes, [f"{e:,}".replace(",", ".") for e in episodes])
        ax.set_xlabel("Số episode huấn luyện")
        ax.set_title(title)
        ax.axhline(0.5, color="#888888", lw=0.8, ls=":")
        ax.set_ylim(-0.02, 1.02)
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("score = (W + 0.5D) / N (đường: trung bình seed; vùng: min–max)")
    axes[0].legend(fontsize=8, loc="lower right")
    fig.suptitle("Ablation A4: epsilon decay và số episode huấn luyện DQN (100 ván mỗi điểm, seed validation cố định)")
    fig.tight_layout()
    FIGURE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE, dpi=150)
    plt.close(fig)


def main() -> int:
    rows = load()
    summary = summarize(rows)
    write_summary(summary)
    plot(rows)
    print(f"{len(rows)} dong -> {SUMMARY} ({len(summary)} nhom), {FIGURE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
