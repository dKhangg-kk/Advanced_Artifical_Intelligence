"""Chay van, chay cap dau va chay giai dau vong tron.

Thiet ke da chot trong README:
    - N van/cap, chia deu di truoc / di sau.
    - Cung mot bo khai cuoc duoc dung cho moi cap (moi khai cuoc dau 2 lan,
      doi ben) de giam phuong sai.
    - Ghi log TUNG NUOC: doi thu, ben di truoc, chuoi nuoc, thoi gian,
      so nut / so mo phong.

Schema log nam trong ``docs/LOGGING.md``. Dung ``save_run()`` de ghi dong thoi
``games_<run_id>.csv`` va ``moves_<run_id>.csv``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from connect_four.agents.base import Agent
from connect_four.evaluation.metrics import mean, p95
from connect_four.evaluation.runlog import GAME_FIELDS, MOVE_FIELDS, new_run_id, write_csv
from connect_four.game.base import ConnectFourGame


@dataclass
class MatchConfig:
    """Cau hinh mot tran doi khang."""

    games_per_pair: int = 200
    openings: int = 100          # moi khai cuoc choi 2 lan, doi ben
    seed: int = 0
    max_moves: int = 42          # chan vong lap vo han khi engine loi
    time_per_move_s: float | None = None


@dataclass
class MoveRecord:
    """Mot nuoc di, dung de xuat ``moves_<run_id>.csv``."""

    game_id: str
    ply: int
    player: int
    agent: str
    action: int
    run_id: str = ""
    legal_actions: list[int] = field(default_factory=list)
    time_ms: float = 0.0
    nodes: int = 0
    simulations: int = 0
    depth_reached: int = 0
    eval_score: float | None = None
    is_terminal: bool = False


@dataclass
class GameRecord:
    """Mot van dau, dung de xuat ``games_<run_id>.csv``."""

    agent_a: str
    agent_b: str
    a_starts: bool
    run_id: str = ""
    game_id: str = ""
    pair: str = ""
    opening_id: int | None = None
    moves: list[int] = field(default_factory=list)
    winner: int | None = None      # 1 = A thang, 2 = B thang, None = hoa
    times_ms_a: list[float] = field(default_factory=list)
    times_ms_b: list[float] = field(default_factory=list)
    nodes_a: int = 0
    nodes_b: int = 0
    simulations_a: int = 0
    simulations_b: int = 0
    over_budget_a: bool = False
    over_budget_b: bool = False
    move_logs: list[MoveRecord] = field(default_factory=list)


def play_game(
    game: ConnectFourGame,
    agent_a: Agent,
    agent_b: Agent,
    opening: list[int] | None = None,
) -> GameRecord:
    """Choi mot van, tra ve ban ghi chi tiet."""
    raise NotImplementedError("TODO: vong lap van dau + ghi thoi gian tung nuoc")


def play_match(
    agent_a: Agent,
    agent_b: Agent,
    config: "MatchConfig",
    game_factory=...,
) -> list[GameRecord]:
    """Choi ``config.games_per_pair`` van giua hai tac tu."""
    raise NotImplementedError("TODO: sinh khai cuoc, doi ben, goi play_game")


def play_round_robin(
    agents: dict[str, Agent],
    config: "MatchConfig",
    game_factory=...,
) -> list[GameRecord]:
    """Giai dau vong tron: 6 tac tu -> 15 cap."""
    raise NotImplementedError("TODO: lap qua moi cap, goi play_match")


def _game_id(record: GameRecord, index: int) -> str:
    return record.game_id or f"g{index:05d}"


def _pair(record: GameRecord) -> str:
    return record.pair or f"{record.agent_a}_vs_{record.agent_b}"


def _winner_label(winner: int | None) -> str:
    if winner is None:
        return "draw"
    return "a" if winner == 1 else "b"


def save_games(records: list[GameRecord], path: str | Path) -> Path:
    """Ghi log tung van ra CSV theo schema ``GAME_FIELDS``."""
    rows: list[dict[str, object]] = []
    for index, record in enumerate(records):
        rows.append(
            {
                "run_id": record.run_id,
                "game_id": _game_id(record, index),
                "pair": _pair(record),
                "agent_a": record.agent_a,
                "agent_b": record.agent_b,
                "a_starts": record.a_starts,
                "opening_id": record.opening_id,
                "moves": record.moves,
                "winner": _winner_label(record.winner),
                "n_moves": len(record.moves),
                "mean_ms_a": mean(record.times_ms_a),
                "p95_ms_a": p95(record.times_ms_a) if record.times_ms_a else 0.0,
                "mean_ms_b": mean(record.times_ms_b),
                "p95_ms_b": p95(record.times_ms_b) if record.times_ms_b else 0.0,
                "nodes_a": record.nodes_a,
                "nodes_b": record.nodes_b,
                "simulations_a": record.simulations_a,
                "simulations_b": record.simulations_b,
                "over_budget_a": record.over_budget_a,
                "over_budget_b": record.over_budget_b,
            }
        )
    return write_csv(path, GAME_FIELDS, rows)


def save_moves(records: list[GameRecord], path: str | Path) -> Path:
    """Ghi log tung nuoc ra CSV theo schema ``MOVE_FIELDS``."""
    rows: list[dict[str, object]] = []
    for index, record in enumerate(records):
        default_game_id = _game_id(record, index)
        for move in record.move_logs:
            rows.append(
                {
                    "run_id": move.run_id or record.run_id,
                    "game_id": move.game_id or default_game_id,
                    "ply": move.ply,
                    "player": move.player,
                    "agent": move.agent,
                    "action": move.action,
                    "legal_actions": move.legal_actions,
                    "time_ms": move.time_ms,
                    "nodes": move.nodes,
                    "simulations": move.simulations,
                    "depth_reached": move.depth_reached,
                    "eval_score": move.eval_score,
                    "is_terminal": move.is_terminal,
                }
            )
    return write_csv(path, MOVE_FIELDS, rows)


def save_run(
    records: list[GameRecord],
    out_dir: str | Path = "results/logs",
    run_id: str | None = None,
) -> tuple[Path, Path]:
    """Ghi ca ``games_<run_id>.csv`` va ``moves_<run_id>.csv``.

    Returns:
        (duong_dan_games, duong_dan_moves)
    """
    if run_id is None:
        run_id = records[0].run_id if records and records[0].run_id else new_run_id("run")
    for record in records:
        if not record.run_id:
            record.run_id = run_id

    out = Path(out_dir)
    games_path = save_games(records, out / f"games_{run_id}.csv")
    moves_path = save_moves(records, out / f"moves_{run_id}.csv")
    return games_path, moves_path


def save_records(records: list[GameRecord], path: str | Path) -> Path:
    """Ghi log van ra CSV (ten cu, tuong thich voi CLI).

    Dung ``save_run()`` neu can ghi ca log tung nuoc.
    """
    return save_games(records, path)
