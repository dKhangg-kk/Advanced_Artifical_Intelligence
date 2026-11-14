"""Doc cau hinh tac tu va giai dau Connect Four tu YAML.

Module nay giu tham so tac tu trong configs/agents.yaml va cac chinh sach giai
Dau trong configs/tournament_*.yaml; CLI khong hard-code tham so mo hinh.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from connect_four.agents import AGENTS, make_agent
from connect_four.agents.base import Agent, Budget
from connect_four.evaluation.match import MatchConfig


@dataclass(frozen=True)
class TournamentSettings:
    """Cac tham so dieu khien mot giai dau Round-Robin."""

    mode: str
    games_per_pair: int
    openings: int
    seed: int
    max_moves: int
    time_per_move_s: float | None
    agents: tuple[str, ...]
    agent_config: Path
    output_dir: Path
    figures_dir: Path
    tables_dir: Path

    def match_config(self) -> MatchConfig:
        return MatchConfig(
            games_per_pair=self.games_per_pair,
            openings=self.openings,
            seed=self.seed,
            max_moves=self.max_moves,
            time_per_move_s=self.time_per_move_s,
        )


def _read_yaml(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"Khong tim thay file cau hinh: {source}")
    try:
        data = yaml.safe_load(source.read_text(encoding="utf-8"))
    except yaml.YAMLError as err:
        raise ValueError(f"YAML khong hop le trong {source}: {err}") from err
    if not isinstance(data, dict):
        raise ValueError(f"Noi dung {source} phai la mot mapping YAML.")
    return data


def load_agent_config(path: str | Path = "configs/agents.yaml") -> dict[str, dict[str, Any]]:
    """Tai va kiem tra danh sach tham so 6 tac tu."""
    data = _read_yaml(path)
    unknown = sorted(set(data) - set(AGENTS))
    if unknown:
        raise ValueError(f"Ten tac tu chua duoc dang ky trong {path}: {unknown}")
    result: dict[str, dict[str, Any]] = {}
    for name, settings in data.items():
        if not isinstance(settings, dict):
            raise ValueError(f"Cau hinh tac tu {name!r} phai la mapping.")
        result[name] = dict(settings)
    return result


def load_tournament_config(
    path: str | Path,
    *,
    agent_config_path: str | Path = "configs/agents.yaml",
) -> TournamentSettings:
    """Doc file giai dau; che do timed dung cung gioi han cho moi tac tu."""
    data = _read_yaml(path)
    allowed = {
        "mode", "games_per_pair", "openings", "seed", "max_moves",
        "time_per_move_s", "agents", "agent_config", "output_dir",
        "figures_dir", "tables_dir", "notes",
    }
    extra = sorted(set(data) - allowed)
    if extra:
        raise ValueError(f"Tham so giai dau khong duoc ho tro: {extra}")

    mode = data.get("mode", "default")
    if mode not in {"default", "timed"}:
        raise ValueError("mode phai la 'default' hoac 'timed'.")

    games = data.get("games_per_pair", 200)
    openings = data.get("openings", (games + 1) // 2 if isinstance(games, int) else 100)
    seed = data.get("seed", 0)
    max_moves = data.get("max_moves", 42)
    for key, value in (("games_per_pair", games), ("openings", openings), ("seed", seed), ("max_moves", max_moves)):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{key} phai la so nguyen.")
    if games <= 0 or openings <= 0 or max_moves <= 0:
        raise ValueError("games_per_pair, openings va max_moves phai > 0.")
    if (games + 1) // 2 > openings:
        raise ValueError("openings khong du de tao games_per_pair voi khai cuoc khong trung.")

    time_per_move = data.get("time_per_move_s")
    if mode == "timed":
        if isinstance(time_per_move, bool) or not isinstance(time_per_move, (int, float)) or time_per_move <= 0:
            raise ValueError("Che do timed can time_per_move_s la so huu han duong.")
        time_per_move = float(time_per_move)
    else:
        time_per_move = None

    names = data.get("agents")
    if not isinstance(names, list) or len(names) < 2:
        raise ValueError("agents phai la danh sach co it nhat hai tac tu.")
    if any(not isinstance(name, str) or name not in AGENTS for name in names):
        raise ValueError(f"Danh sach agents phai nam trong {sorted(AGENTS)}.")
    if len(set(names)) != len(names):
        raise ValueError("Danh sach agents khong duoc lap ten.")

    cfg = Path(data.get("agent_config", agent_config_path))
    # Doc va xac nhan ngay de bao loi cau hinh truoc khi chay giai dau.
    agent_settings = load_agent_config(cfg)
    missing = sorted(set(names) - set(agent_settings))
    if missing:
        raise ValueError(f"Thieu cau hinh cho tac tu: {missing}")

    return TournamentSettings(
        mode=mode,
        games_per_pair=games,
        openings=openings,
        seed=seed,
        max_moves=max_moves,
        time_per_move_s=time_per_move,
        agents=tuple(names),
        agent_config=cfg,
        output_dir=Path(data.get("output_dir", "results/logs")),
        figures_dir=Path(data.get("figures_dir", "results/figures")),
        tables_dir=Path(data.get("tables_dir", "results/tables")),
    )


def build_agent(
    name: str,
    agent_settings: dict[str, dict[str, Any]],
    *,
    seed: int | None = None,
    time_budget_s: float | None = None,
    depth: int | None = None,
    simulations: int | None = None,
    checkpoint: str | Path | None = None,
) -> Agent:
    """Tao agent tu YAML, co the ghi de ngan sach/seed/checkpoint cho mot tran."""
    if name not in AGENTS:
        raise KeyError(f"Tac tu {name!r} chua duoc dang ky. Co san: {sorted(AGENTS)}")
    if name not in agent_settings:
        raise ValueError(f"Khong co cau hinh cho tac tu {name!r}.")
    values = dict(agent_settings[name])
    values.pop("level", None)
    values.pop("seed", None)
    configured_seed = seed

    if name == "random":
        return make_agent(name, seed=configured_seed)
    if name == "heuristic":
        return make_agent(name, weights=values.get("weights"), seed=configured_seed)
    if name == "alphabeta":
        selected_depth = depth if depth is not None else int(values.get("depth", 5))
        budget = Budget(time_s=time_budget_s) if time_budget_s is not None else Budget(depth=selected_depth)
        return make_agent(
            name,
            budget=budget,
            depth=selected_depth,
            use_pruning=bool(values.get("use_pruning", True)),
            use_ordering=bool(values.get("use_ordering", True)),
            seed=configured_seed,
        )
    if name == "mcts":
        selected_simulations = simulations if simulations is not None else int(values.get("simulations", 1000))
        budget = Budget(time_s=time_budget_s) if time_budget_s is not None else Budget(simulations=selected_simulations)
        return make_agent(name, budget=budget, c=float(values.get("c", 1.414)), seed=configured_seed)
    if name == "nn":
        model_path = checkpoint or values.get("checkpoint")
        return make_agent(name, checkpoint=model_path, seed=configured_seed)
    if name == "dqn":
        model_path = checkpoint or values.get("checkpoint")
        return make_agent(name, checkpoint=model_path, epsilon=0.0, seed=configured_seed)
    raise AssertionError("Danh sach AGENTS va build_agent chua dong bo.")


__all__ = [
    "TournamentSettings", "build_agent", "load_agent_config", "load_tournament_config",
]
