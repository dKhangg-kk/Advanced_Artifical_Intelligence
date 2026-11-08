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

import itertools
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from connect_four.agents.base import Agent
from connect_four.evaluation.metrics import mean, p95
from connect_four.evaluation.runlog import GAME_FIELDS, MOVE_FIELDS, new_run_id, write_csv
from connect_four.game.base import ConnectFourGame
from connect_four.game.constants import PLAYER_1, PLAYER_2
from connect_four.game.engine import ConnectFour


@dataclass
class MatchConfig:
    """Cau hinh mot tran doi khang."""

    games_per_pair: int = 200
    openings: int = 100          # moi khai cuoc choi 2 lan, doi ben
    seed: int = 0
    max_moves: int = 42          # chan vong lap vo han khi engine loi
    time_per_move_s: float | None = None  # chi de danh dau over_budget, khong ngat nuoc di
    opening_plies: int = 4       # so nuoc ngau nhien o moi khai cuoc (chan, de A va B deu den luot nhu nhau)


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


def _agent_name(agent: Agent) -> str:
    return getattr(agent, "name", type(agent).__name__)


def play_game(
    game: ConnectFourGame,
    agent_a: Agent,
    agent_b: Agent,
    opening: list[int] | None = None,
    *,
    a_starts: bool = True,
    time_per_move_s: float | None = None,
    max_moves: int = 42,
    name_a: str | None = None,
    name_b: str | None = None,
) -> GameRecord:
    """Choi mot van, tra ve ban ghi chi tiet.

    Args:
        game: engine o trang thai bat ky (thuong la van moi); ham se `reset()` no.
        opening: cac nuoc khai cuoc dat truoc, KHONG tinh gio va khong ghi vao
            ``move_logs`` (chi nam trong ``moves``).
        a_starts: True thi A la nguoi choi 1 (di truoc), nguoc lai B di truoc.
        time_per_move_s: neu co, danh dau ``over_budget_*`` khi mot nuoc vuot
            moc nay (chi danh dau, khong cat nuoc di).
        max_moves: chan vong lap khi engine loi.

    Raises:
        ValueError: khai cuoc khong hop le, hoac tac tu tra ve cot khong hop le
            (hop dong `Agent` cam dieu nay nen khong am tham chap nhan).
    """
    name_a = name_a or _agent_name(agent_a)
    name_b = name_b or _agent_name(agent_b)
    game.reset()
    agent_a.reset()
    agent_b.reset()

    a_player = PLAYER_1 if a_starts else PLAYER_2
    record = GameRecord(agent_a=name_a, agent_b=name_b, a_starts=a_starts)

    for move in opening or []:
        game.step(move)  # nem ValueError neu khai cuoc sai luat

    while not game.is_terminal():
        if len(game.moves_played()) >= max_moves:
            raise RuntimeError(f"Van vuot {max_moves} nuoc ma chua ket thuc: engine co the bi loi")

        player = game.current_player
        is_a = player == a_player
        agent = agent_a if is_a else agent_b
        legal = game.legal_actions()

        view = game.clone()  # tac tu khong duoc phep lam hong van that
        start = time.perf_counter()
        action = agent.choose(view)
        elapsed_ms = (time.perf_counter() - start) * 1000.0

        if action not in legal:
            raise ValueError(
                f"Tac tu {_agent_name(agent)} tra ve nuoc khong hop le {action!r}; hop le: {legal}"
            )

        stats = agent.last_stats
        ply = len(game.moves_played())
        game.step(action)

        record.move_logs.append(
            MoveRecord(
                game_id="",
                ply=ply,
                player=player,
                agent=name_a if is_a else name_b,
                action=int(action),
                legal_actions=legal,
                time_ms=elapsed_ms,
                nodes=stats.nodes,
                simulations=stats.simulations,
                depth_reached=stats.depth_reached,
                eval_score=stats.extra.get("eval_score") if stats.extra else None,
                is_terminal=game.is_terminal(),
            )
        )

        over = time_per_move_s is not None and elapsed_ms > time_per_move_s * 1000.0
        if is_a:
            record.times_ms_a.append(elapsed_ms)
            record.nodes_a += stats.nodes
            record.simulations_a += stats.simulations
            record.over_budget_a = record.over_budget_a or over
        else:
            record.times_ms_b.append(elapsed_ms)
            record.nodes_b += stats.nodes
            record.simulations_b += stats.simulations
            record.over_budget_b = record.over_budget_b or over

    record.moves = list(game.moves_played())
    winner = game.winner()
    if winner is None:
        record.winner = None
    else:
        record.winner = 1 if winner == a_player else 2
    return record


def generate_openings(
    count: int,
    plies: int = 4,
    seed: int = 0,
    game_factory: Callable[[], ConnectFourGame] = ConnectFour,
) -> list[list[int]]:
    """Sinh `count` khai cuoc KHAC NHAU, moi khai cuoc la `plies` nuoc ngau nhien hop le.

    Chi phu thuoc `seed` (khong phu thuoc cap tac tu), nen moi cap trong giai dau
    dung dung cung mot bo khai cuoc. Khai cuoc khong duoc ket thuc van.
    """
    rng = random.Random(seed)
    seen: set[tuple[int, ...]] = set()
    openings: list[list[int]] = []
    attempts = 0
    while len(openings) < count:
        attempts += 1
        if attempts > 1000 * max(count, 1):
            raise ValueError(
                f"Khong sinh du {count} khai cuoc khac nhau voi {plies} nuoc; "
                "tang opening_plies hoac giam so khai cuoc"
            )
        game = game_factory()
        moves: list[int] = []
        for _ in range(plies):
            if game.is_terminal():
                break
            move = rng.choice(game.legal_actions())
            game.step(move)
            moves.append(move)
        if game.is_terminal() or tuple(moves) in seen:
            continue
        seen.add(tuple(moves))
        openings.append(moves)
    return openings


def play_match(
    agent_a: Agent,
    agent_b: Agent,
    config: "MatchConfig",
    game_factory: Callable[[], ConnectFourGame] = ConnectFour,
    *,
    openings: list[list[int]] | None = None,
    name_a: str | None = None,
    name_b: str | None = None,
) -> list[GameRecord]:
    """Choi ``config.games_per_pair`` van giua hai tac tu.

    Van thu ``g`` dung khai cuoc ``g // 2``; hai van lien tiep cua cung mot khai
    cuoc doi ben di truoc (van chan A di truoc, van le B di truoc). Nhu vay A va B
    gap dung cung cac the co khoi dau o ca hai phe.

    Raises:
        ValueError: ``games_per_pair`` lon hon ``2 * openings`` (se phai lap lai khai cuoc).
    """
    name_a = name_a or _agent_name(agent_a)
    name_b = name_b or _agent_name(agent_b)
    needed = (config.games_per_pair + 1) // 2
    if needed > config.openings:
        raise ValueError(
            f"games_per_pair={config.games_per_pair} can {needed} khai cuoc khac nhau "
            f"nhung chi co openings={config.openings}"
        )
    if openings is None:
        openings = generate_openings(
            needed, config.opening_plies, config.seed, game_factory
        )
    elif len(openings) < needed:
        raise ValueError(f"Chi co {len(openings)} khai cuoc, can {needed}")

    pair = f"{name_a}_vs_{name_b}"
    records: list[GameRecord] = []
    for g in range(config.games_per_pair):
        opening_id = g // 2
        record = play_game(
            game_factory(),
            agent_a,
            agent_b,
            openings[opening_id],
            a_starts=(g % 2 == 0),
            time_per_move_s=config.time_per_move_s,
            max_moves=config.max_moves,
            name_a=name_a,
            name_b=name_b,
        )
        record.pair = pair
        record.opening_id = opening_id
        record.game_id = f"{pair}-g{g:03d}"
        for move in record.move_logs:
            move.game_id = record.game_id
        records.append(record)
    return records


def play_round_robin(
    agents: dict[str, Agent],
    config: "MatchConfig",
    game_factory: Callable[[], ConnectFourGame] = ConnectFour,
) -> list[GameRecord]:
    """Giai dau vong tron: n tac tu -> n(n-1)/2 cap (6 tac tu -> 15 cap).

    Moi cap choi tren cung bo khai cuoc (sinh mot lan tu ``config.seed``).
    """
    needed = (config.games_per_pair + 1) // 2
    openings = generate_openings(needed, config.opening_plies, config.seed, game_factory)
    records: list[GameRecord] = []
    for name_a, name_b in itertools.combinations(agents, 2):
        records.extend(
            play_match(
                agents[name_a],
                agents[name_b],
                config,
                game_factory,
                openings=openings,
                name_a=name_a,
                name_b=name_b,
            )
        )
    return records


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
