"""Demo giao dien pygame.

Chuc nang can co (theo README):
    - Chon tac tu cho tung ben, choi nguoi-may hoac may-may.
    - Hien thi ban co, luot di, ket qua.
    - Hien thi thoi gian moi nuoc.

`pygame` chi duoc import ben trong `run_gui()` de khong lam hong test/CI.
"""

from __future__ import annotations


def run_gui(agent_a: str = "heuristic", agent_b: str = "mcts") -> None:
    """Mo cua so pygame. Goi tu `python -m connect_four.ui.gui`."""
    raise NotImplementedError("TODO: ve ban co 7x6 + vong lap su kien pygame")


if __name__ == "__main__":
    run_gui()
