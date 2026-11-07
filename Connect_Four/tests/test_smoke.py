"""Kiem thu khung: hop dong API, registry tac tu va hang so.

Cac test o day chi kiem tra CAU TRUC, nen van xanh trong khi thuat toan
chua duoc cai dat. Khi cai dat xong, bo sung test hanh vi vao cac file khac.
"""

from __future__ import annotations

import inspect

import pytest

import connect_four
from connect_four.agents import AGENTS, Agent, Budget, make_agent
from connect_four.agents.alphabeta import AlphaBetaAgent
from connect_four.agents.heuristic import HeuristicAgent
from connect_four.agents.mcts import MCTSAgent
from connect_four.agents.nn_agent import NNAgent
from connect_four.agents.random_agent import RandomAgent
from connect_four.agents.dqn import DQNAgent
from connect_four.game import ConnectFour, ConnectFourGame, ReferenceGame
from connect_four.game.constants import COLS, ROWS, WIN_LENGTH, other


def test_constants() -> None:
    assert (ROWS, COLS, WIN_LENGTH) == (6, 7, 4)


def test_other_player() -> None:
    assert other(1) == 2
    assert other(2) == 1


def test_other_rejects_invalid() -> None:
    with pytest.raises(ValueError):
        other(3)


def test_engine_can_be_instantiated() -> None:
    assert isinstance(ConnectFour(), ConnectFourGame)
    assert isinstance(ReferenceGame(), ConnectFourGame)


API_METHODS = [
    "reset",
    "legal_actions",
    "is_legal",
    "step",
    "undo",
    "clone",
    "clone_after",
    "is_terminal",
    "winner",
    "result",
    "winning_moves",
    "key",
    "to_array",
    "render",
    "moves_played",
]


@pytest.mark.parametrize("cls", [ConnectFour, ReferenceGame])
def test_engine_implements_full_api(cls: type) -> None:
    for name in API_METHODS:
        assert hasattr(cls, name), f"{cls.__name__} thieu {name}()"


def test_registry_has_six_levels() -> None:
    expected = {"random", "heuristic", "alphabeta", "mcts", "nn", "dqn"}
    assert expected <= set(AGENTS)


@pytest.mark.parametrize(
    ("name", "cls", "level"),
    [
        ("random", RandomAgent, 1),
        ("heuristic", HeuristicAgent, 2),
        ("alphabeta", AlphaBetaAgent, 3),
        ("mcts", MCTSAgent, 4),
        ("nn", NNAgent, 5),
        ("dqn", DQNAgent, 6),
    ],
)
def test_agent_classes(name: str, cls: type, level: int) -> None:
    assert issubclass(cls, Agent)
    assert cls.name == name
    assert cls.level == level
    assert AGENTS[name] is cls


def test_agent_contract_is_abstract() -> None:
    assert inspect.isabstract(Agent)
    with pytest.raises(TypeError):
        Agent()  # type: ignore[abstract]


def test_make_agent_unknown_name() -> None:
    with pytest.raises(KeyError, match="chua dang ky"):
        make_agent("khong_ton_tai")


def test_budget_accepts_single_constraint() -> None:
    assert Budget(depth=4).depth == 4
    assert Budget(simulations=100).simulations == 100
    assert Budget(time_s=0.5).time_s == 0.5


def test_budget_rejects_two_constraints() -> None:
    with pytest.raises(ValueError, match="mot trong"):
        Budget(depth=4, time_s=0.5)


def test_package_version() -> None:
    assert connect_four.__version__
