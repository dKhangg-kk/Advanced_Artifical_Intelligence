"""Sinh biểu đồ riêng cho bộ slide Connect Four (Nhóm 26).

Chạy từ thư mục Connect_Four:
    .venv/bin/python docs/slides/build_deck_charts.py

Mọi số đọc trực tiếp từ results/tables/*.csv. Ảnh ghi vào docs/slides/assets/.
Bảng màu và cỡ chữ khớp với build_deck.py.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "results" / "tables"
ASSETS = Path(__file__).resolve().parent / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

INK = "#0B242B"
TEAL = "#2E7D8C"
TEAL_DARK = "#12343B"
TEAL_LIGHT = "#8AA4AB"
ORANGE = "#E07A2F"
RED = "#B23A48"
GREEN = "#5C7A3A"
MUTED = "#6B8A90"
GRID = "#DCE7E9"
BG = "#FBFDFD"

AGENTS = ["random", "heuristic", "alphabeta", "mcts", "nn", "dqn"]
LABEL = {
    "random": "Random",
    "heuristic": "Heuristic",
    "alphabeta": "Alpha-Beta",
    "mcts": "MCTS",
    "nn": "CNN Policy",
    "dqn": "DQN",
}

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 12,
        "axes.edgecolor": "#C7D8DB",
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "figure.facecolor": BG,
        "axes.facecolor": BG,
        "savefig.facecolor": BG,
    }
)

VN = FuncFormatter(lambda x, _: f"{x:.1f}".replace(".", ","))


def read(name: str) -> list[dict[str, str]]:
    with (TABLES / name).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def save(fig, name: str) -> None:
    path = ASSETS / name
    fig.savefig(path, dpi=220, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print("wrote", path)


def clean_axes(ax) -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def scores() -> None:
    default = {r["agent"]: float(r["score"]) for r in read("y6_default_agent_summary.csv")}
    timed = {r["agent"]: float(r["score"]) for r in read("y6_timed_agent_summary.csv")}
    order = sorted(AGENTS, key=lambda a: default[a])

    fig, ax = plt.subplots(figsize=(9.8, 4.5))
    y = np.arange(len(order))
    h = 0.36
    b1 = ax.barh(y + h / 2, [default[a] for a in order], h, color=TEAL, label="Mặc định · 200 ván/cặp")
    b2 = ax.barh(y - h / 2, [timed[a] for a in order], h, color=ORANGE, label="Cùng thời gian · 0,2 s/nước")
    for bars, data in ((b1, default), (b2, timed)):
        for bar, agent in zip(bars, order):
            value = data[agent]
            ax.text(
                value + 0.015,
                bar.get_y() + bar.get_height() / 2,
                f"{value:.3f}".replace(".", ","),
                va="center",
                fontsize=10.5,
                color=INK,
            )
    ax.set_yticks(y, [LABEL[a] for a in order], fontsize=12)
    ax.set_xlim(0, 1.02)
    ax.set_xlabel("Score trung bình (thắng = 1, hòa = 0,5)")
    ax.xaxis.set_major_formatter(VN)
    clean_axes(ax)
    ax.legend(loc="lower right", frameon=False, fontsize=10.5)
    save(fig, "deck_scores.png")


def matrix() -> None:
    rows = read("y6_default_score_matrix.csv")
    index = {a: i for i, a in enumerate(AGENTS)}
    grid = np.full((len(AGENTS), len(AGENTS)), np.nan)
    text = [["" for _ in AGENTS] for _ in AGENTS]
    for row in rows:
        a = row["agent"]
        for b in AGENTS:
            cell = row.get(b, "")
            if not cell:
                continue
            grid[index[a], index[b]] = float(cell.split()[0])
            text[index[a]][index[b]] = f"{float(cell.split()[0]):.2f}".replace(".", ",")

    cmap = LinearSegmentedColormap.from_list(
        "deck", ["#FFFFFF", "#DCEBED", "#9CC6CC", "#4E96A2", "#1E5F6C", "#12343B"]
    )
    cmap.set_bad("#FFFFFF")
    fig, ax = plt.subplots(figsize=(7.6, 5.5))
    masked = np.ma.masked_invalid(grid)
    im = ax.imshow(masked, cmap=cmap, vmin=0, vmax=1)
    for i in range(len(AGENTS)):
        for j in range(len(AGENTS)):
            if i == j:
                ax.text(j, i, "—", ha="center", va="center", fontsize=12, color="#9DB3B7")
                continue
            value = grid[i, j]
            ax.text(
                j,
                i,
                text[i][j],
                ha="center",
                va="center",
                fontsize=12,
                color="white" if value >= 0.55 else INK,
                fontweight="bold" if value >= 0.8 or value <= 0.2 else "normal",
            )
    ax.set_xticks(range(len(AGENTS)), [LABEL[a] for a in AGENTS], rotation=28, ha="right")
    ax.set_yticks(range(len(AGENTS)), [LABEL[a] for a in AGENTS])
    ax.set_xlabel("Đối thủ (cột)", labelpad=8)
    ax.set_ylabel("Tác tử (hàng)", labelpad=8)
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0)
    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
    cbar.set_label("Score của hàng khi gặp cột", fontsize=10)
    cbar.outline.set_visible(False)
    save(fig, "deck_matrix.png")


def latency() -> None:
    rows = {r["agent"]: r for r in read("y6_default_agent_summary.csv")}
    order = sorted(AGENTS, key=lambda a: float(rows[a]["mean_ms_per_move"]))
    mean = [float(rows[a]["mean_ms_per_move"]) for a in order]
    p95 = [float(rows[a]["p95_ms_per_move"]) for a in order]

    fig, ax = plt.subplots(figsize=(9.8, 4.4))
    y = np.arange(len(order))
    for yi, m, p in zip(y, mean, p95):
        ax.plot([m, p], [yi, yi], color="#CFE0E3", linewidth=6, solid_capstyle="round", zorder=1)
        ax.scatter([m], [yi], s=110, color=TEAL, zorder=3, label="Trung bình" if yi == y[0] else None)
        ax.scatter([p], [yi], s=110, marker="D", color=ORANGE, zorder=3, label="p95" if yi == y[0] else None)
        label = f"{m:.3f}".replace(".", ",") if m < 1 else f"{m:.1f}".replace(".", ",")
        p_label = f"{p:.3f}" if p < 0.1 else f"{p:.1f}"
        ax.text(p * 1.25, yi, f"{label} ms  ·  p95 {p_label}".replace(".", ","), va="center", fontsize=10)
    ax.set_yticks(y, [LABEL[a] for a in order])
    ax.set_xscale("log")
    ax.set_xlim(0.002, 900)
    ax.set_xlabel("Thời gian suy luận mỗi nước (ms, thang log)")
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.grid(axis="y", visible=False)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(loc="lower right", frameon=False, fontsize=10.5)
    save(fig, "deck_latency.png")


def tactical() -> None:
    rows = read("y6_position_accuracy.csv")
    types = [("win_now", "Thắng ngay"), ("block", "Chặn"), ("double_threat", "Đòn kép")]
    values = {a: {} for a in AGENTS}
    for row in rows:
        values[row["agent"]][row["situation"]] = float(row["accuracy"])

    fig, ax = plt.subplots(figsize=(9.8, 4.7))
    x = np.arange(len(AGENTS))
    width = 0.26
    colors = [TEAL_DARK, TEAL, ORANGE]
    for i, (key, label) in enumerate(types):
        vals = [values[a][key] for a in AGENTS]
        bars = ax.bar(x + (i - 1) * width, vals, width, color=colors[i], label=label)
        for bar, val in zip(bars, vals):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                val + 0.025,
                f"{val:.2f}".replace(".", ","),
                ha="center",
                fontsize=9.5,
                color=INK,
            )
    ax.set_xticks(x, [LABEL[a] for a in AGENTS])
    ax.set_ylim(0, 1.10)
    ax.yaxis.set_major_formatter(VN)
    ax.set_ylabel("Độ chính xác")
    clean_axes(ax)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=3, frameon=False, fontsize=10.5)
    fig.tight_layout()
    save(fig, "deck_tactical.png")


def a3() -> None:
    rows = read("ablation_a3_results.csv")
    rows.sort(key=lambda r: int(r["train_games"]))
    games = [int(r["train_games"]) for r in rows]
    top1 = [float(r["top1_accuracy"]) for r in rows]
    win = [float(r["win_now_situation_accuracy"]) for r in rows]
    block = [float(r["block_situation_accuracy"]) for r in rows]

    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.2), sharex=True)
    ax = axes[0]
    ax.plot(games, top1, "-o", color=TEAL, linewidth=2.6, markersize=7)
    for g, v in zip(games, top1):
        ax.annotate(f"{v * 100:.1f}%".replace(".", ","), (g, v), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=10)
    ax.set_title("Top-1 trên tập test", fontsize=12.5)
    ax.set_ylim(0.40, 0.63)

    ax = axes[1]
    ax.plot(games, win, "-o", color=ORANGE, linewidth=2.4, markersize=6, label="Thắng ngay")
    ax.plot(games, block, "-s", color=TEAL_DARK, linewidth=2.4, markersize=6, label="Chặn")
    for g, v in list(zip(games, win)) + list(zip(games, block)):
        ax.annotate(f"{v * 100:.0f}%", (g, v), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9.5)
    ax.set_title("Tình huống chiến thuật", fontsize=12.5)
    ax.set_ylim(0.33, 0.92)
    ax.legend(frameon=False, fontsize=10, loc="lower right")

    for ax in axes:
        ax.set_xlabel("Số ván huấn luyện")
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v * 100:.0f}%"))
        ax.set_xticks(games)
        clean_axes(ax)
    fig.tight_layout()
    save(fig, "deck_a3.png")


def a4() -> None:
    rows = read("ablation_a4_summary.csv")
    configs = [
        ("fast_decay", "decay 0,9990", RED),
        ("default_decay", "decay 0,9995", TEAL),
        ("slow_decay", "decay 0,9998", GREEN),
        ("default_decay_open4", "0,9995 + 4 nước ngẫu nhiên", ORANGE),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.2), sharey=True)
    for key, label, color in configs:
        for ax, opponent in zip(axes, ("random", "heuristic")):
            subset = [r for r in rows if r["config_id"] == key and r["opponent"] == opponent]
            subset.sort(key=lambda r: int(r["episode"]))
            xs = [int(r["episode"]) for r in subset]
            ys = [float(r["score_mean"]) for r in subset]
            dashed = key == "default_decay_open4"
            ax.plot(
                xs,
                ys,
                "--o" if dashed else "-o",
                color=color,
                linewidth=2.2,
                markersize=5,
                label=label,
                alpha=1.0 if dashed else 0.9,
            )
    axes[0].set_title("Validation gặp Random", fontsize=12.5)
    axes[1].set_title("Validation gặp Heuristic", fontsize=12.5)
    axes[1].annotate(
        "0,425",
        (10000, 0.425),
        textcoords="offset points",
        xytext=(-34, 6),
        fontsize=10,
        color=ORANGE,
        fontweight="bold",
    )
    axes[1].annotate(
        "0,162",
        (10000, 0.1617),
        textcoords="offset points",
        xytext=(-40, 10),
        fontsize=10,
        color=TEAL,
        fontweight="bold",
    )
    for ax in axes:
        ax.set_xlabel("Số episode huấn luyện")
        ax.set_xticks([1000, 2500, 5000, 10000])
        ax.set_xticklabels(["1k", "2,5k", "5k", "10k"])
        ax.set_ylim(0, 0.85)
        ax.yaxis.set_major_formatter(VN)
        clean_axes(ax)
    axes[0].set_ylabel("Score validation")
    axes[0].legend(frameon=False, fontsize=8.8, loc="lower left")
    fig.tight_layout()
    save(fig, "deck_a4.png")


def a6() -> None:
    rows = read("ablation_a6_pooled.csv")
    rows = [r for r in rows if int(r["episode"]) == 10000]
    opponents = [("random", "Gặp Random"), ("heuristic", "Gặp Heuristic")]
    trains = [("heuristic", "Huấn luyện với Heuristic"), ("random", "Huấn luyện với Random"), ("selfplay", "Tự chơi")]
    lookup = {(r["train_opponent"], r["opponent"]): float(r["score"]) for r in rows}

    fig, ax = plt.subplots(figsize=(9.8, 4.3))
    x = np.arange(len(trains))
    width = 0.32
    colors = [TEAL, ORANGE]
    for i, (opp, label) in enumerate(opponents):
        vals = [lookup[(train, opp)] for train, _ in trains]
        bars = ax.bar(x + (i - 0.5) * width, vals, width, color=colors[i], label=label)
        for bar, val in zip(bars, vals):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                val + 0.02,
                f"{val:.3f}".replace(".", ","),
                ha="center",
                fontsize=10,
            )
    ax.set_xticks(x, [label for _, label in trains])
    ax.set_ylim(0, 0.78)
    ax.yaxis.set_major_formatter(VN)
    ax.set_ylabel("Score sau 10.000 episode")
    clean_axes(ax)
    ax.legend(frameon=False, fontsize=10, ncol=2, loc="upper right")
    save(fig, "deck_a6.png")


def search() -> None:
    a2 = read("ablation_a2_results.csv")
    a2.sort(key=lambda r: int(r["simulations"]))
    sims = [int(r["simulations"]) for r in a2]
    a2_score = [float(r["score"]) for r in a2]
    a2_ms = [float(r["mean_ms"]) for r in a2]

    a5 = [r for r in read("ablation_a5_results.csv") if r["phase"] == "games"]
    a5.sort(key=lambda r: int(r["depth"]))
    depths = [int(r["depth"]) for r in a5]
    a5_score = [float(r["score"]) for r in a5]
    a5_ms = [float(r["mean_ms"]) for r in a5]

    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.2))
    ax = axes[0]
    ax.plot(sims, a2_score, "-o", color=TEAL, linewidth=2.6, markersize=6)
    for s, v, ms in zip(sims, a2_score, a2_ms):
        ax.annotate(f"{v:.2f}".replace(".", ","), (s, v), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=9.5)
    ax.set_xlabel("Số mô phỏng mỗi nước")
    ax.set_ylabel("Score trước Alpha-Beta sâu 4")
    ax.set_ylim(0, 0.86)
    ax.yaxis.set_major_formatter(VN)
    ax.set_title("A2 — ngân sách MCTS", fontsize=12.5)
    ax.annotate(
        "100 mô phỏng: 2,5 ms\n5.000 mô phỏng: 126,8 ms",
        xy=(0.03, 0.03),
        xycoords="axes fraction",
        fontsize=9.5,
        color=MUTED,
    )

    ax = axes[1]
    ax.plot(depths, a5_score, "-o", color=ORANGE, linewidth=2.6, markersize=6)
    for d, v, ms in zip(depths, a5_score, a5_ms):
        ax.annotate(f"{v:.2f}".replace(".", ","), (d, v), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=9.5)
        ax.annotate(f"{ms:.1f} ms".replace(".", ","), (d, v), textcoords="offset points", xytext=(0, -22), ha="center", fontsize=8.5, color=MUTED)
    ax.set_xlabel("Độ sâu Alpha-Beta")
    ax.set_ylabel("Score trước Heuristic")
    ax.set_ylim(0.52, 0.90)
    ax.set_xticks(depths)
    ax.yaxis.set_major_formatter(VN)
    ax.set_title("A5 — độ sâu Alpha-Beta", fontsize=12.5)

    for ax in axes:
        clean_axes(ax)
    fig.tight_layout()
    save(fig, "deck_search.png")


def dqn_openings() -> None:
    rows = read("dqn_opening_diagnostic.csv")
    plies = [0, 2, 4]
    series = {"random": ("Gặp Random", TEAL), "heuristic": ("Gặp Heuristic", ORANGE)}
    lookup = {(r["opponent"], int(r["opening_plies"])): float(r["score"]) for r in rows}

    fig, ax = plt.subplots(figsize=(8.4, 4.0))
    x = np.arange(len(plies))
    width = 0.34
    for i, (opp, (label, color)) in enumerate(series.items()):
        vals = [lookup[(opp, p)] for p in plies]
        bars = ax.bar(x + (i - 0.5) * width, vals, width, color=color, label=label)
        for bar, val in zip(bars, vals):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                val + 0.02,
                f"{val:.2f}".replace(".", ","),
                ha="center",
                fontsize=11,
                fontweight="bold",
            )
    ax.set_xticks(x, ["0 nước", "2 nước", "4 nước"])
    ax.set_xlabel("Số nước khai cuộc ngẫu nhiên trước khi DQN vào ván")
    ax.set_ylim(0, 1.1)
    ax.yaxis.set_major_formatter(VN)
    ax.set_ylabel("Score của DQN")
    clean_axes(ax)
    ax.legend(frameon=False, fontsize=10.5)
    save(fig, "deck_dqn_openings.png")


if __name__ == "__main__":
    scores()
    matrix()
    latency()
    tactical()
    a3()
    a4()
    a6()
    search()
    dqn_openings()
