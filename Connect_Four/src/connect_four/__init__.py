"""Connect Four AI 7x6 - do an cuoi ky mon Tri tue nhan tao nang cao.

Cau truc:
    game/       Engine (bitboard + ban tham chieu) va hop dong API.
    agents/     Sau tac tu cap 1-6 cung mot giao dien chon nuoc.
    training/   Sinh nhan Alpha-Beta, huan luyen NN (cap 5) va DQN (cap 6).
    evaluation/ Giai dau vong tron, do luong va xuat log CSV.
    ui/         Demo pygame.
"""

__version__ = "0.1.0"
__all__ = ["__version__"]
