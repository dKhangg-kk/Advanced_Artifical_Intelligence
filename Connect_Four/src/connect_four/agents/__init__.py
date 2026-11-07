"""Dang ky cac tac tu theo ten, de CLI va giai dau tao bang chuoi.

Them tac tu moi: viet lop ke thua `Agent`, roi them vao `AGENTS`.
"""

from __future__ import annotations

from typing import Callable

from connect_four.agents.alphabeta import AlphaBetaAgent
from connect_four.agents.base import Agent, Budget, SearchStats
from connect_four.agents.dqn import DQNAgent
from connect_four.agents.heuristic import HeuristicAgent
from connect_four.agents.mcts import MCTSAgent
from connect_four.agents.nn_agent import NNAgent
from connect_four.agents.random_agent import RandomAgent

AGENTS: dict[str, Callable[..., Agent]] = {
    "random": RandomAgent,        # Cap 1
    "heuristic": HeuristicAgent,  # Cap 2
    "alphabeta": AlphaBetaAgent,  # Cap 3
    "mcts": MCTSAgent,            # Cap 4
    "nn": NNAgent,                # Cap 5
    "dqn": DQNAgent,              # Cap 6
}


def make_agent(name: str, **kwargs) -> Agent:
    """Tao tac tu theo ten trong `AGENTS`.

    Raises:
        KeyError: ten chua duoc dang ky.
    """
    try:
        factory = AGENTS[name]
    except KeyError:
        raise KeyError(f"Tac tu '{name}' chua dang ky. Co san: {sorted(AGENTS)}") from None
    return factory(**kwargs)


__all__ = [
    "AGENTS",
    "Agent",
    "AlphaBetaAgent",
    "Budget",
    "DQNAgent",
    "HeuristicAgent",
    "MCTSAgent",
    "NNAgent",
    "RandomAgent",
    "SearchStats",
    "make_agent",
]
