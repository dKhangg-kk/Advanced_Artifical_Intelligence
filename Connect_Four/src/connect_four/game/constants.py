"""Hang so dung chung cho engine va cac tac tu.

Quy uoc bieu dien (thong nhat toan du an):
    - Ban co 6 hang x 7 cot. Hang 0 la hang DUOI CUNG.
    - O trong = EMPTY (0), nguoi choi 1 = PLAYER_1 (1), nguoi choi 2 = PLAYER_2 (2).
    - Hanh dong = chi so cot 0..6.
    - Luoi `board` co shape (ROWS, COLS), dtype int8.
"""

ROWS = 6
COLS = 7
WIN_LENGTH = 4

EMPTY = 0
PLAYER_1 = 1
PLAYER_2 = 2

PLAYERS = (PLAYER_1, PLAYER_2)


def other(player: int) -> int:
    """Tra ve doi thu cua `player`."""
    if player not in PLAYERS:
        raise ValueError(f"Nguoi choi khong hop le: {player!r}")
    return PLAYER_2 if player == PLAYER_1 else PLAYER_1


# Thu tu duyet cot mac dinh: uu tien cot giua (tot cho cat tia Alpha-Beta).
CENTER_FIRST = (3, 2, 4, 1, 5, 0, 6)
