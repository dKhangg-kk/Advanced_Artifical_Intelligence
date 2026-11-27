"""Sinh các hình bàn cờ dùng trong bộ slide Connect Four (Nhóm 26).

Chạy từ thư mục Connect_Four:
    .venv/bin/python docs/slides/build_assets.py

Ảnh được ghi vào docs/slides/assets/. Không phụ thuộc dữ liệu thí nghiệm;
đây là hình minh họa luật chơi và ván cờ, không phải log thực nghiệm.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

ASSETS = Path(__file__).resolve().parent / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

INK = "#0B242B"
TEAL = "#2E7D8C"
BOARD = "#1F5C8B"
BOARD_DARK = "#123B5C"
CREAM = "#F7F1E3"
RED = "#D64545"
RED_DARK = "#9E2B2B"
YELLOW = "#F2C14E"
YELLOW_DARK = "#B8862B"
GOLD = "#FFD166"
MUTED = "#8AA4AB"


def _disc(ax, x: float, y: float, color: str, radius: float = 0.40, glow: bool = False) -> None:
    if glow:
        ax.add_patch(Circle((x, y), radius * 1.22, facecolor=GOLD, edgecolor="none", alpha=0.28, zorder=4))
    ax.add_patch(Circle((x, y), radius, facecolor=color, edgecolor="white", linewidth=1.6, zorder=5))
    ax.add_patch(
        Circle(
            (x - radius * 0.28, y + radius * 0.28),
            radius * 0.30,
            facecolor="white",
            edgecolor="none",
            alpha=0.16,
            zorder=6,
        )
    )


def draw_board(
    ax,
    stacks: list[str],
    highlight: set[tuple[int, int]] | None = None,
    *,
    show_coords: bool = True,
    glow: bool = False,
    board_color: str = BOARD,
    edge_color: str = BOARD_DARK,
) -> None:
    """Vẽ bàn 7x6. stacks[c] là chuỗi quân từ đáy lên ('R' đỏ, 'Y' vàng)."""
    ax.set_xlim(-0.65, 6.65)
    ax.set_ylim(-0.65, 5.65)
    ax.set_aspect("equal")
    ax.axis("off")

    ax.add_patch(
        FancyBboxPatch(
            (-0.58, -0.58),
            7.16,
            6.16,
            boxstyle="round,pad=0.02,rounding_size=0.22",
            facecolor=board_color,
            edgecolor=edge_color,
            linewidth=3.0,
            zorder=1,
        )
    )
    # subtle inner frame
    ax.add_patch(
        FancyBboxPatch(
            (-0.46, -0.46),
            6.92,
            5.92,
            boxstyle="round,pad=0.01,rounding_size=0.18",
            facecolor="none",
            edgecolor="white",
            linewidth=0.8,
            alpha=0.18,
            zorder=2,
        )
    )

    highlight = highlight or set()
    for c in range(7):
        for r in range(6):
            # hole shadow
            ax.add_patch(Circle((c, r), 0.455, facecolor=BOARD_DARK, edgecolor="none", zorder=3))
            ax.add_patch(Circle((c, r), 0.425, facecolor=CREAM, edgecolor="none", zorder=3))
            if r < len(stacks[c]):
                ch = stacks[c][r]
                color = RED if ch == "R" else YELLOW
                _disc(ax, c, r, color, glow=glow and (c, r) in highlight)

    if show_coords:
        for c in range(7):
            ax.text(c, -0.56, str(c), ha="center", va="center", fontsize=9, color="white", alpha=0.75)
        for r in range(6):
            ax.text(-0.56, r, str(r), ha="center", va="center", fontsize=9, color="white", alpha=0.75)


def save(fig, name: str) -> None:
    path = ASSETS / name
    fig.savefig(path, dpi=220, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    print("wrote", path)


def hero() -> None:
    fig = plt.figure(figsize=(13.333, 7.5), dpi=200)
    fig.patch.set_facecolor(INK)
    ax_bg = fig.add_axes([0, 0, 1, 1])
    ax_bg.set_xlim(0, 1)
    ax_bg.set_ylim(0, 1)
    ax_bg.axis("off")

    # gradient background
    grad = plt.cm.colors.LinearSegmentedColormap.from_list("hero", ["#08191E", "#0F3540", "#15505C"])
    for i in range(120):
        y = i / 120
        ax_bg.add_patch(
            Rectangle((0, y), 1, 1 / 120 + 0.002, facecolor=grad(y), edgecolor="none", zorder=0)
        )

    # decorative discs
    for x, y, color, alpha, r in [
        (0.86, 0.86, RED, 0.10, 0.16),
        (0.93, 0.72, YELLOW, 0.08, 0.10),
        (0.10, 0.12, YELLOW, 0.06, 0.13),
        (0.16, 0.20, RED, 0.05, 0.07),
    ]:
        ax_bg.add_patch(Circle((x, y), r, facecolor=color, edgecolor="none", alpha=alpha, zorder=1))

    ax = fig.add_axes([0.47, 0.10, 0.51, 0.80])
    stacks = ["Y", "RY", "RY", "RY", "R", "", "R"]
    draw_board(
        ax,
        stacks,
        highlight={(1, 0), (2, 0), (3, 0), (4, 0)},
        show_coords=False,
        glow=True,
        board_color="#1B547F",
        edge_color="#0A2A45",
    )
    save(fig, "hero_board.png")


def rules() -> None:
    fig = plt.figure(figsize=(9.2, 6.4), dpi=220)
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    stacks = ["Y", "RY", "RY", "RY", "R", "", "R"]
    draw_board(
        ax,
        stacks,
        highlight={(1, 0), (2, 0), (3, 0), (4, 0)},
        glow=True,
        show_coords=False,
    )
    ax.set_ylim(-1.05, 5.65)
    ax.text(2.5, -0.72, "4 quân liên tiếp", ha="center", va="top", fontsize=15, color="#B8862B", fontweight="bold")
    save(fig, "rules_board.png")


def loss_boards() -> None:
    # Trước nước đi sai của MCTS: Random (đỏ) có 3 quân ở đáy c1-c3, MCTS (vàng) ở c1/c6.
    before = ["", "RY", "R", "R", "", "", "Y"]
    fig = plt.figure(figsize=(7.0, 5.4), dpi=220)
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    draw_board(ax, before, highlight={(1, 0), (2, 0), (3, 0)}, glow=True)
    ax.annotate(
        "Random đe dọa cột 4",
        xy=(3.42, 0.10),
        xytext=(4.35, 1.65),
        fontsize=11,
        ha="center",
        color=RED_DARK,
        fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=RED_DARK, lw=2, connectionstyle="arc3,rad=0.25"),
        zorder=12,
    )
    save(fig, "mcts_loss_before.png")

    # Sau khi MCTS chọn c0, Random thả c4 và thắng ngang c1-c4.
    after = ["Y", "RY", "R", "R", "R", "", "Y"]
    fig = plt.figure(figsize=(7.0, 5.4), dpi=220)
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    draw_board(ax, after, highlight={(1, 0), (2, 0), (3, 0), (4, 0)}, glow=True)
    ax.annotate(
        "Random thắng",
        xy=(4.0, 0.12),
        xytext=(4.55, 1.65),
        fontsize=11,
        ha="center",
        color=RED_DARK,
        fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=RED_DARK, lw=2, connectionstyle="arc3,rad=0.2"),
        zorder=12,
    )
    save(fig, "mcts_loss_after.png")


def state_tensor() -> None:
    """Hai kênh đầu vào 2x6x7 của CNN/DQN."""
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.5), dpi=220)
    fig.patch.set_facecolor("white")
    stacks = ["Y", "RY", "RY", "RY", "R", "", "R"]
    grids = []
    for channel in (0, 1):
        grid = [[0] * 7 for _ in range(6)]
        for c, stack in enumerate(stacks):
            for r, ch in enumerate(stack):
                if (ch == "R" and channel == 0) or (ch == "Y" and channel == 1):
                    grid[r][c] = 1
        grids.append(grid)

    titles = ["Kênh 0 — quân của bên đang đi", "Kênh 1 — quân đối thủ"]
    for ax, grid, title in zip(axes, grids, titles):
        ax.imshow(grid, cmap=matplotlib.colors.ListedColormap(["#EEF3F4", TEAL]), vmin=0, vmax=1)
        ax.set_xticks(range(7))
        ax.set_yticks(range(6))
        ax.set_xticklabels(range(7), fontsize=8)
        ax.set_yticklabels(range(6), fontsize=8)
        ax.set_title(title, fontsize=10, color=INK)
        ax.set_xticks([x - 0.5 for x in range(1, 7)], minor=True)
        ax.set_yticks([y - 0.5 for y in range(1, 6)], minor=True)
        ax.grid(which="minor", color="white", linewidth=2)
        ax.tick_params(which="both", length=0)
        for spine in ax.spines.values():
            spine.set_color("#D5E2E4")
    fig.text(0.5, -0.02, "Tensor 2 × 6 × 7", ha="center", fontsize=12, color=INK, fontweight="bold")
    fig.tight_layout()
    save(fig, "state_tensor.png")




def architecture() -> None:
    """Sơ đồ kiến trúc hệ thống, chữ Việt có dấu, tông màu của bộ slide."""
    fig = plt.figure(figsize=(11.4, 5.6), dpi=220)
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 11.4)
    ax.set_ylim(0, 5.6)
    ax.axis("off")

    def box(x, y, w, h, title, body, color, text_color="white"):
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                w,
                h,
                boxstyle="round,pad=0.02,rounding_size=0.12",
                facecolor=color,
                edgecolor="none",
                zorder=2,
            )
        )
        ax.text(x + w / 2, y + h - 0.30, title, ha="center", va="center", fontsize=12.5, fontweight="bold", color=text_color, zorder=3)
        ax.text(x + w / 2, y + h / 2 - 0.14, body, ha="center", va="center", fontsize=10.2, color=text_color, linespacing=1.45, zorder=3)

    def arrow(x1, y1, x2, y2, rad=0.0):
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(arrowstyle="-|>", color="#5E8A93", lw=2.0, shrinkA=3, shrinkB=5, connectionstyle=f"arc3,rad={rad}"),
            zorder=1,
        )

    box(0.30, 3.28, 2.45, 1.42, "GIAO DIỆN", "Terminal (play.py)\nPygame (ui/gui.py)", "#8AA4AB")
    box(3.30, 3.20, 4.55, 1.60, "SÁU TÁC TỬ", "Random · Heuristic · Alpha-Beta\nMCTS · CNN Policy · DQN", "#2E7D8C")
    box(8.45, 3.28, 2.65, 1.42, "GAME ENGINE", "Bitboard 49-bit\n+ ReferenceGame", "#12343B")

    box(2.05, 0.55, 3.45, 1.50, "HUẤN LUYỆN", "CNN: học có giám sát\nDQN: học tăng cường", "#E07A2F")
    box(6.55, 0.55, 3.55, 1.50, "ĐÁNH GIÁ", "15 cặp · 4.500 ván\nCSV · manifest · hình", "#5C7A3A")

    arrow(2.78, 3.99, 3.24, 3.99)
    arrow(7.88, 3.99, 8.39, 3.99)
    arrow(8.95, 3.22, 5.05, 2.12)
    arrow(5.55, 2.10, 5.55, 3.14)
    arrow(9.55, 3.22, 8.65, 2.12)
    arrow(5.55, 1.30, 6.49, 1.30)

    ax.text(6.85, 2.82, "ván + nhãn", ha="center", va="bottom", fontsize=8.8, color="#4E6B70")
    ax.text(5.72, 2.62, "checkpoint", ha="left", va="center", fontsize=8.8, color="#4E6B70")
    ax.text(9.38, 2.74, "log ván", ha="center", va="bottom", fontsize=8.8, color="#4E6B70")

    ax.text(0.30, 5.22, "Một hợp đồng chung cho engine, tác tử và đánh giá", fontsize=13.5, fontweight="bold", color=INK)
    ax.text(0.30, 0.16, "Agent.choose(game.clone()) không sửa bàn thật; mọi con số truy về CSV thô và report_numbers.csv.", fontsize=9.6, color="#5E7A80")
    save(fig, "deck_architecture.png")


if __name__ == "__main__":
    hero()
    rules()
    loss_boards()
    state_tensor()
    architecture()
