"""Exact Connect Four solver for small/endgame positions.

The solver is an evaluation tool, not a tournament agent.  It returns the
minimax value from the player-to-move perspective:

    1  = the player to move can force a win
    0  = perfect play leads to a draw
   -1  = the player to move will lose against perfect play

It deliberately talks only to ``ConnectFourGame`` so it can be checked against
both the bitboard engine and the slow reference engine.
"""

from __future__ import annotations

from dataclasses import dataclass

from connect_four.game.base import ConnectFourGame
from connect_four.game.constants import CENTER_FIRST


@dataclass
class SolverStats:
    nodes: int = 0
    cache_hits: int = 0


class ExactSolver:
    """Negamax solver with alpha-beta pruning and an exact-value cache."""

    def __init__(self) -> None:
        self._cache: dict[int, int] = {}
        self.stats = SolverStats()

    def solve(self, game: ConnectFourGame) -> int:
        """Return the exact value for ``game`` without mutating it."""
        self._cache.clear()
        self.stats = SolverStats()
        return self._negamax(game, -1, 1)

    def best_moves(self, game: ConnectFourGame) -> list[int]:
        """Return every legal move whose child has the optimal exact value."""
        if game.is_terminal():
            return []
        self._cache.clear()
        self.stats = SolverStats()
        immediate = game.winning_moves(game.current_player)
        if immediate:
            return immediate
        values = {action: -self._negamax(game.clone_after(action), -1, 1)
                  for action in game.legal_actions()}
        best = max(values.values())
        return [action for action in game.legal_actions() if values[action] == best]

    def choose(self, game: ConnectFourGame) -> int:
        """Return one optimal move, preferring the centre for reproducibility."""
        moves = self.best_moves(game)
        if not moves:
            raise ValueError("Khong con nuoc di hop le.")
        return next((action for action in CENTER_FIRST if action in moves), moves[0])

    def _negamax(self, game: ConnectFourGame, alpha: int, beta: int) -> int:
        self.stats.nodes += 1
        if game.is_terminal():
            return int(game.result(game.current_player))

        key = game.key()
        cached = self._cache.get(key)
        if cached is not None:
            self.stats.cache_hits += 1
            return cached

        # A direct win is exact and avoids exploring unrelated branches before
        # the winning column in the centre-first ordering.
        if game.winning_moves(game.current_player):
            self._cache[key] = 1
            return 1

        actions = [action for action in CENTER_FIRST if action in game.legal_actions()]
        best = -1
        cutoff = False
        for action in actions:
            value = -self._negamax(game.clone_after(action), -beta, -alpha)
            best = max(best, value)
            alpha = max(alpha, value)
            if best == 1:
                break
            if alpha >= beta:
                cutoff = True
                break

        # A cut-off only gives a bound, not an exact value, so never cache it.
        if not cutoff:
            self._cache[key] = best
        return best
