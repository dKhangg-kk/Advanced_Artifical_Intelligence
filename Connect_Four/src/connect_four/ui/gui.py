"""Giao dien pygame cho Connect Four.

Chuc nang:
    - Man hinh chon: moi ben (X di truoc, O di sau) la "human" hoac mot trong
      cac tac tu da dang ky (random, heuristic, alphabeta, mcts, nn, dqn).
    - Choi nguoi-may hoac may-may; nguoi choi bang cach bam chuot vao cot.
    - Hien thi ban co, luot di, o vua tha, bon quan thang, ket qua.
    - Hien thi thoi gian suy nghi cua nuoc di gan nhat cua moi ben.

Phim tat trong van: R = van moi, M = ve man hinh chon, Esc = thoat.

Thiet ke: phan luat choi/dieu khien (`GameController`) khong dung pygame nen test
duoc khong can man hinh. `pygame` chi duoc import ben trong `GuiApp` / `run_gui()`
de khong lam hong test/CI khi may chua cai pygame. Tac tu "suy nghi" trong mot
luong rieng de cua so khong bi dung khi tim kiem lau.

Chay:
    python -m connect_four.ui.gui                       # nguoi (X) vs heuristic (O)
    python -m connect_four.ui.gui --a human --b mcts
    python -m connect_four.ui.gui --a alphabeta --b mcts --start
"""

from __future__ import annotations

import argparse
import threading
import time
from typing import Callable

from connect_four.agents import AGENTS, Agent, make_agent
from connect_four.game.base import ConnectFourGame
from connect_four.game.constants import COLS, PLAYER_1, PLAYER_2, ROWS, WIN_LENGTH
from connect_four.game.engine import ConnectFour

HUMAN = "human"
SYMBOL = {PLAYER_1: "X", PLAYER_2: "O"}


def winning_cells(board, player: int) -> list[tuple[int, int]]:
    """Cac o (hang, cot) nam trong mot day `WIN_LENGTH` quan lien tiep cua `player`."""
    cells: set[tuple[int, int]] = set()
    for dr, dc in ((0, 1), (1, 0), (1, 1), (-1, 1)):
        for r in range(ROWS):
            for c in range(COLS):
                line = [(r + dr * k, c + dc * k) for k in range(WIN_LENGTH)]
                if all(
                    0 <= rr < ROWS and 0 <= cc < COLS and board[rr][cc] == player
                    for rr, cc in line
                ):
                    cells.update(line)
    return sorted(cells)


class GameController:
    """Trang thai mot van + dieu phoi luot di giua nguoi va tac tu (khong phu thuoc pygame)."""

    def __init__(
        self,
        names: dict[int, str],
        agent_factory: Callable[..., Agent] | None = None,
        game_factory: Callable[[], ConnectFourGame] = ConnectFour,
        seed: int = 0,
    ) -> None:
        self.names = dict(names)
        self._agent_factory = agent_factory or (lambda name, seed: make_agent(name, seed=seed))
        self._game_factory = game_factory
        self._seed = seed
        self._lock = threading.Lock()
        self.new_game()

    # --- khoi tao van moi -------------------------------------------------
    def new_game(self) -> None:
        self._token = getattr(self, "_token", 0) + 1  # bo qua ket qua cua luong cu
        self._thread: threading.Thread | None = None
        self._result: tuple | None = None
        self.game = self._game_factory()
        self.agents: dict[int, Agent | None] = {PLAYER_1: None, PLAYER_2: None}
        self.last_ms: dict[int, float | None] = {PLAYER_1: None, PLAYER_2: None}
        self.last_col: int | None = None
        self.error: str | None = None
        self.message: str = ""
        self.moved = False  # True ngay sau khi mot nuoc duoc ap dung (de GUI dat nhip)
        for offset, player in enumerate((PLAYER_1, PLAYER_2)):
            name = self.names[player]
            if name == HUMAN:
                continue
            try:
                agent = self._agent_factory(name, seed=self._seed + offset)
                agent.reset()
                self.agents[player] = agent
            except Exception as exc:  # tac tu chua cai dat / thieu checkpoint / thieu torch
                self.error = f"Khong tao duoc tac tu '{name}': {exc}"

    # --- truy van ---------------------------------------------------------
    @property
    def blocked(self) -> bool:
        return self.error is not None

    @property
    def thinking(self) -> bool:
        return self._thread is not None

    def is_human_turn(self) -> bool:
        return not self.game.is_terminal() and self.agents[self.game.current_player] is None and not self.blocked

    def winning_cells(self) -> list[tuple[int, int]]:
        winner = self.game.winner()
        return [] if winner is None else winning_cells(self.game.board, winner)

    def label(self, player: int) -> str:
        name = self.names[player]
        return f"{'Nguoi' if name == HUMAN else name} ({SYMBOL[player]})"

    def status(self) -> str:
        if self.blocked:
            return self.error or ""
        if self.game.is_terminal():
            winner = self.game.winner()
            return "Hoa! Ban co da day." if winner is None else f"{self.label(winner)} thang!"
        who = self.label(self.game.current_player)
        return f"Luot: {who}" + ("  - dang nghi..." if self.thinking else "")

    # --- nuoc di cua nguoi ------------------------------------------------
    def human_move(self, col: int) -> bool:
        if not self.is_human_turn() or self.thinking:
            return False
        if not self.game.is_legal(col):
            self.message = f"Cot {col} da day"
            return False
        self.message = ""
        self.last_col = col
        self.last_ms[self.game.current_player] = None
        self.game.step(col)
        self.moved = True
        return True

    # --- nuoc di cua tac tu -----------------------------------------------
    def update(self, block: bool = False, allow_start: bool = True) -> None:
        """Ap dung nuoc cua tac tu neu da xong; bat dau suy nghi neu den luot tac tu.

        `block=True` (dung trong test): cho luong suy nghi chay xong va ap dung ngay.
        """
        self.moved = False
        for _ in range(2):
            if self._thread is not None:
                if block:
                    self._thread.join()
                if not self._thread.is_alive():
                    self._thread = None
                    self._apply_result()
            if (
                self._thread is None
                and allow_start
                and not self.blocked
                and not self.game.is_terminal()
                and self.agents[self.game.current_player] is not None
            ):
                self._start_thinking()
                if block:
                    continue
            break

    def _start_thinking(self) -> None:
        player = self.game.current_player
        agent = self.agents[player]
        snapshot = self.game.clone()  # tac tu khong duoc sua van that
        token = self._token

        def work() -> None:
            start = time.perf_counter()
            try:
                col = agent.choose(snapshot)
                outcome = (token, player, col, (time.perf_counter() - start) * 1000, None)
            except Exception as exc:  # NotImplementedError, loi checkpoint, ...
                outcome = (token, player, None, 0.0, exc)
            with self._lock:
                self._result = outcome

        self._thread = threading.Thread(target=work, daemon=True)
        self._thread.start()

    def _apply_result(self) -> None:
        with self._lock:
            outcome, self._result = self._result, None
        if outcome is None:
            return
        token, player, col, ms, exc = outcome
        if token != self._token or player != self.game.current_player:
            return  # ket qua cua van cu
        if exc is not None:
            kind = "chua duoc cai dat" if isinstance(exc, NotImplementedError) else f"bi loi: {exc}"
            self.error = f"Tac tu '{self.names[player]}' {kind}"
            return
        if not self.game.is_legal(col):
            self.error = f"Tac tu '{self.names[player]}' tra ve nuoc khong hop le: {col!r}"
            return
        self.last_col = int(col)
        self.last_ms[player] = ms
        self.game.step(int(col))
        self.moved = True


# ======================================================================
# Phan ve (can pygame)
# ======================================================================
CELL = 90
BOARD_X = 20
BOARD_Y = 110
BOARD_W = COLS * CELL
BOARD_H = ROWS * CELL
PANEL_X = BOARD_X + BOARD_W + 30
PANEL_W = 300
WINDOW_W = PANEL_X + PANEL_W + 20
WINDOW_H = BOARD_Y + BOARD_H + 50
AGENT_GAP_S = 0.35  # nhip toi thieu giua hai nuoc de nguoi xem theo doi duoc

BG = (24, 28, 38)
BOARD_COLOR = (36, 78, 168)
HOLE = (20, 24, 34)
COLORS = {PLAYER_1: (235, 64, 52), PLAYER_2: (250, 204, 21)}
TEXT = (230, 232, 238)
MUTED = (150, 156, 170)
GOOD = (80, 200, 120)
BAD = (240, 100, 100)
BUTTON = (52, 62, 90)
BUTTON_HOT = (72, 86, 126)


class GuiApp:
    """Vong lap su kien + ve. Tach rieng `handle_event`/`update`/`draw` de test headless."""

    def __init__(
        self,
        agent_a: str = HUMAN,
        agent_b: str = "heuristic",
        agent_factory: Callable[..., Agent] | None = None,
        seed: int = 0,
    ) -> None:
        import pygame

        self.pg = pygame
        pygame.init()
        pygame.display.set_caption("Connect Four AI - Nhom 100")
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.Font(None, 52)
        self.font = pygame.font.Font(None, 30)
        self.font_small = pygame.font.Font(None, 24)

        self.options = [HUMAN] + sorted(AGENTS)
        for name in (agent_a, agent_b):
            if name not in self.options:
                if agent_factory is None:
                    raise ValueError(f"Tac tu khong hop le: {name!r}. Co san: {self.options}")
                self.options.append(name)  # factory tuy chinh (dung trong test)
        self.choice = {PLAYER_1: agent_a, PLAYER_2: agent_b}
        self.agent_factory = agent_factory
        self.seed = seed
        self.state = "menu"  # "menu" | "game"
        self.controller: GameController | None = None
        self.hover_col: int | None = None
        self.next_agent_time = 0.0
        self.running = True
        self.menu_rects: dict[str, object] = {}
        self.game_rects: dict[str, object] = {}

    # --- dieu khien -------------------------------------------------------
    def start_game(self) -> None:
        self.controller = GameController(
            self.choice, agent_factory=self.agent_factory, seed=self.seed
        )
        self.state = "game"
        self.next_agent_time = time.time() + AGENT_GAP_S

    def cycle(self, player: int, step: int = 1) -> None:
        i = self.options.index(self.choice[player])
        self.choice[player] = self.options[(i + step) % len(self.options)]

    def handle_event(self, event) -> None:
        pg = self.pg
        if event.type == pg.QUIT:
            self.running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.running = False
            elif self.state == "menu" and event.key in (pg.K_RETURN, pg.K_KP_ENTER):
                self.start_game()
            elif self.state == "game" and event.key == pg.K_r:
                self.controller.new_game()
                self.next_agent_time = time.time() + AGENT_GAP_S
            elif self.state == "game" and event.key == pg.K_m:
                self.state = "menu"
        elif event.type == pg.MOUSEMOTION and self.state == "game":
            self.hover_col = self._column_at(event.pos)
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.state == "menu":
                self._menu_click(event.pos)
            else:
                self._game_click(event.pos)

    def _column_at(self, pos: tuple[int, int]) -> int | None:
        x, y = pos
        if BOARD_X <= x < BOARD_X + BOARD_W and 0 <= y < BOARD_Y + BOARD_H:
            return (x - BOARD_X) // CELL
        return None

    def _menu_click(self, pos) -> None:
        for player in (PLAYER_1, PLAYER_2):
            if self.menu_rects.get(f"p{player}") and self.menu_rects[f"p{player}"].collidepoint(pos):
                self.cycle(player)
        if self.menu_rects.get("start") and self.menu_rects["start"].collidepoint(pos):
            self.start_game()

    def _game_click(self, pos) -> None:
        if self.game_rects.get("new") and self.game_rects["new"].collidepoint(pos):
            self.controller.new_game()
            self.next_agent_time = time.time() + AGENT_GAP_S
        elif self.game_rects.get("menu") and self.game_rects["menu"].collidepoint(pos):
            self.state = "menu"
        else:
            col = self._column_at(pos)
            if col is not None and self.controller.human_move(col):
                self.next_agent_time = time.time() + AGENT_GAP_S

    def update(self) -> None:
        if self.state != "game":
            return
        self.controller.update(allow_start=time.time() >= self.next_agent_time)
        if self.controller.moved:
            self.next_agent_time = time.time() + AGENT_GAP_S

    # --- ve ---------------------------------------------------------------
    def _text(self, text: str, pos, font=None, color=TEXT) -> None:
        self.screen.blit((font or self.font).render(text, True, color), pos)

    def _button(self, key: str, store: dict, rect, label: str) -> None:
        pg = self.pg
        rect = pg.Rect(rect)
        store[key] = rect
        hot = rect.collidepoint(pg.mouse.get_pos())
        pg.draw.rect(self.screen, BUTTON_HOT if hot else BUTTON, rect, border_radius=8)
        surf = self.font.render(label, True, TEXT)
        self.screen.blit(surf, surf.get_rect(center=rect.center))

    def draw(self) -> None:
        self.screen.fill(BG)
        if self.state == "menu":
            self._draw_menu()
        else:
            self._draw_game()
        self.pg.display.flip()

    def _draw_menu(self) -> None:
        self._text("Connect Four 7x6", (60, 60), self.font_big)
        self._text("Bam vao o de doi nguoi choi/tac tu cho tung ben.", (60, 120), self.font_small, MUTED)
        for i, player in enumerate((PLAYER_1, PLAYER_2)):
            y = 190 + i * 90
            self.pg.draw.circle(self.screen, COLORS[player], (80, y + 24), 18)
            self._text(f"Ben {SYMBOL[player]} ({'di truoc' if player == PLAYER_1 else 'di sau'})", (115, y + 14))
            self._button(f"p{player}", self.menu_rects, (420, y, 240, 48), self.choice[player])
        self._button("start", self.menu_rects, (60, 410, 240, 54), "Bat dau (Enter)")
        self._text("Trong van: R = van moi, M = ve day, Esc = thoat", (60, 500), self.font_small, MUTED)

    def _draw_game(self) -> None:
        pg, ctl = self.pg, self.controller
        board = ctl.game.board
        win_cells = set(ctl.winning_cells())

        # quan "bay" phia tren khi den luot nguoi
        if self.hover_col is not None and ctl.is_human_turn() and ctl.game.is_legal(self.hover_col):
            cx = BOARD_X + self.hover_col * CELL + CELL // 2
            pg.draw.circle(self.screen, COLORS[ctl.game.current_player], (cx, BOARD_Y - CELL // 2), CELL // 2 - 8)

        pg.draw.rect(self.screen, BOARD_COLOR, (BOARD_X, BOARD_Y, BOARD_W, BOARD_H), border_radius=12)
        last_row = None
        if ctl.last_col is not None:
            heights = [sum(1 for r in range(ROWS) if board[r][c]) for c in range(COLS)]
            last_row = heights[ctl.last_col] - 1
        for r in range(ROWS):
            for c in range(COLS):
                cx = BOARD_X + c * CELL + CELL // 2
                cy = BOARD_Y + (ROWS - 1 - r) * CELL + CELL // 2  # hang 0 o duoi cung
                piece = int(board[r][c])
                pg.draw.circle(self.screen, COLORS.get(piece, HOLE), (cx, cy), CELL // 2 - 8)
                if (r, c) in win_cells:
                    pg.draw.circle(self.screen, (255, 255, 255), (cx, cy), CELL // 2 - 6, 5)
                elif piece and (r, c) == (last_row, ctl.last_col):
                    pg.draw.circle(self.screen, (255, 255, 255), (cx, cy), 10)
        for c in range(COLS):
            self._text(str(c), (BOARD_X + c * CELL + CELL // 2 - 5, BOARD_Y + BOARD_H + 12), self.font_small, MUTED)

        # bang ben phai
        status_color = BAD if ctl.blocked else (GOOD if ctl.game.is_terminal() else TEXT)
        self._text(ctl.status(), (PANEL_X, 40), self.font, status_color)
        for i, player in enumerate((PLAYER_1, PLAYER_2)):
            y = 110 + i * 90
            pg.draw.circle(self.screen, COLORS[player], (PANEL_X + 14, y + 12), 12)
            self._text(ctl.label(player), (PANEL_X + 38, y))
            ms = ctl.last_ms[player]
            if ctl.names[player] == HUMAN:
                info = "nguoi choi"
            else:
                info = "nuoc gan nhat: " + ("-" if ms is None else f"{ms:.1f} ms")
            self._text(info, (PANEL_X + 38, y + 30), self.font_small, MUTED)
        self._text(f"So nuoc da di: {len(ctl.game.moves_played())}", (PANEL_X, 300), self.font_small, MUTED)
        if ctl.message:
            self._text(ctl.message, (PANEL_X, 330), self.font_small, BAD)
        self._button("new", self.game_rects, (PANEL_X, 400, 140, 44), "Van moi")
        self._button("menu", self.game_rects, (PANEL_X + 150, 400, 140, 44), "Chon lai")

    # --- vong lap ---------------------------------------------------------
    def run(self) -> None:
        while self.running:
            for event in self.pg.event.get():
                self.handle_event(event)
            self.update()
            self.draw()
            self.clock.tick(60)
        self.pg.quit()


def run_gui(agent_a: str = HUMAN, agent_b: str = "heuristic", start: bool = False) -> None:
    """Mo cua so pygame. Goi tu `python -m connect_four.ui.gui`."""
    try:
        import pygame  # noqa: F401
    except ImportError as exc:
        raise SystemExit("Can cai pygame truoc: pip install pygame") from exc
    app = GuiApp(agent_a, agent_b)
    if start:
        app.start_game()
    app.run()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Giao dien pygame Connect Four")
    p.add_argument("--a", default=HUMAN, help=f"Ben X (di truoc): {HUMAN} hoac {sorted(AGENTS)}")
    p.add_argument("--b", default="heuristic", help="Ben O (di sau)")
    p.add_argument("--start", action="store_true", help="Vao thang van, bo qua man hinh chon")
    args = p.parse_args(argv)
    run_gui(args.a, args.b, args.start)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
