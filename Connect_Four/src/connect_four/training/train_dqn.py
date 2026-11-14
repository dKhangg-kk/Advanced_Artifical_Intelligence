"""Vong lap huan luyen Deep Q-Network (DQN), cap 6.

Module chi import NumPy va thu vien chuan o cap module. PyTorch va PyYAML
chi duoc nap khi thuc su bat dau huan luyen/doc cau hinh, de cac test ReplayBuffer
van chay duoc tren moi truong chua cai thu vien nang.
"""

from __future__ import annotations

import argparse
import csv
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import platform
import random
import re
import subprocess
import time
from typing import Any, Deque, Sequence

import numpy as np

from connect_four.game.constants import COLS, ROWS, PLAYER_1


@dataclass(frozen=True)
class DQNTransition:
    """Mot mau trai nghiem va mat na hanh dong hop le cua trang thai ke tiep."""

    state: np.ndarray
    action: int
    reward: float
    next_state: np.ndarray
    done: bool
    next_legal_mask: np.ndarray


def _copy_state(value: np.ndarray, field_name: str) -> np.ndarray:
    """Kiem tra va sao chep state theo quy uoc (2, 6, 7)."""
    state = np.asarray(value, dtype=np.float32)
    expected_shape = (2, ROWS, COLS)
    if state.shape != expected_shape:
        raise ValueError(f"{field_name} phai co shape {expected_shape}, nhan duoc {state.shape}.")
    if not np.isfinite(state).all():
        raise ValueError(f"{field_name} chi duoc chua gia tri huu han.")
    return state.copy()


def _copy_legal_mask(value: np.ndarray, done: bool) -> np.ndarray:
    """Kiem tra mask 7 cot; trang thai terminal co the khong con cot hop le."""
    mask = np.asarray(value, dtype=np.bool_)
    if mask.shape != (COLS,):
        raise ValueError(f"next_legal_mask phai co shape ({COLS},), nhan duoc {mask.shape}.")
    if not done and not bool(mask.any()):
        raise ValueError("Transition chua ket thuc phai co it nhat mot cot hop le o next_state.")
    return mask.copy()


class ReplayBuffer:
    """Bo nho kinh nghiem DQN theo FIFO, mac dinh toi da 100.000 transition.

    Khi day, transition moi se ghi de phan tu cu nhat. ``sample(batch_size)``
    lay ngau nhien khong hoan lai va tra ve dung so mau duoc yeu cau.
    """

    def __init__(self, capacity: int = 100_000, seed: int | None = None) -> None:
        if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity <= 0:
            raise ValueError("capacity phai la so nguyen duong.")
        self.capacity = capacity
        self._memory: Deque[DQNTransition] = deque(maxlen=capacity)
        self._rng = random.Random(seed)

    def __len__(self) -> int:
        return len(self._memory)

    def add(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
        next_legal_mask: np.ndarray,
    ) -> None:
        """Them mot transition; tu dong sao chep cac mang dau vao.

        ``next_legal_mask`` la bool mask cua BAN KE TIEP, khong phai ban hien tai.
        O trang thai ket thuc, mask co the gom toan False.
        """
        if isinstance(action, bool) or not isinstance(action, (int, np.integer)):
            raise ValueError("action phai la so nguyen trong khoang 0..6.")
        action = int(action)
        if not 0 <= action < COLS:
            raise ValueError("action phai nam trong khoang 0..6.")
        if not isinstance(done, (bool, np.bool_)):
            raise ValueError("done phai la gia tri bool.")
        reward = float(reward)
        if not math.isfinite(reward):
            raise ValueError("reward phai la so huu han.")

        transition = DQNTransition(
            state=_copy_state(state, "state"),
            action=action,
            reward=reward,
            next_state=_copy_state(next_state, "next_state"),
            done=bool(done),
            next_legal_mask=_copy_legal_mask(next_legal_mask, bool(done)),
        )
        self._memory.append(transition)

    def push(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
        next_legal_mask: np.ndarray,
    ) -> None:
        """Alias thong dung cua ``add()``."""
        self.add(state, action, reward, next_state, done, next_legal_mask)

    def sample(self, batch_size: int) -> list[DQNTransition]:
        """Lay ngau nhien batch khong lap; loi neu buffer chua du mau."""
        if isinstance(batch_size, bool) or not isinstance(batch_size, int) or batch_size <= 0:
            raise ValueError("batch_size phai la so nguyen duong.")
        if batch_size > len(self._memory):
            raise ValueError(
                f"Khong du transition de lay batch: can {batch_size}, hien co {len(self._memory)}."
            )
        return self._rng.sample(list(self._memory), batch_size)

    def clear(self) -> None:
        """Xoa toan bo transition dang luu."""
        self._memory.clear()


@dataclass
class EpsilonSchedule:
    """Lich epsilon giam theo episode, co san toi thieu 0.05."""

    start: float = 1.0
    minimum: float = 0.05
    decay: float = 0.9995
    episode: int = 0

    def __post_init__(self) -> None:
        self.start = float(self.start)
        self.minimum = float(self.minimum)
        self.decay = float(self.decay)
        if not (0.0 <= self.minimum <= self.start <= 1.0):
            raise ValueError("Can thoa 0 <= minimum <= start <= 1.")
        if not (0.0 < self.decay <= 1.0):
            raise ValueError("decay phai nam trong khoang (0, 1].")
        if isinstance(self.episode, bool) or not isinstance(self.episode, int) or self.episode < 0:
            raise ValueError("episode phai la so nguyen khong am.")

    @property
    def value(self) -> float:
        """Epsilon hien tai sau ``episode`` lan cap nhat."""
        return max(self.minimum, self.start * (self.decay ** self.episode))

    def step(self) -> float:
        """Tien them mot episode va tra ve epsilon moi."""
        self.episode += 1
        return self.value

    def reset(self) -> None:
        """Dat lich ve episode 0 va epsilon ban dau."""
        self.episode = 0


def epsilon_for_episode(
    episode: int,
    start: float = 1.0,
    minimum: float = 0.05,
    decay: float = 0.9995,
) -> float:
    """Tinh epsilon truc tiep tai episode (episode 0 la gia tri start)."""
    schedule = EpsilonSchedule(start=start, minimum=minimum, decay=decay)
    if isinstance(episode, bool) or not isinstance(episode, int) or episode < 0:
        raise ValueError("episode phai la so nguyen khong am.")
    return max(schedule.minimum, schedule.start * (schedule.decay ** episode))


def _git_revision() -> str | None:
    """Lay commit hien tai de ghi vao metadata checkpoint neu dang o Git repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=3,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() or None


def _build_opponent(name: str, seed: int) -> Any:
    """Tao doi thu co seed rieng cho mot episode."""
    if name == "random":
        from connect_four.agents.random_agent import RandomAgent

        return RandomAgent(seed=seed)
    if name == "heuristic":
        from connect_four.agents.heuristic import HeuristicAgent

        return HeuristicAgent(seed=seed)
    raise ValueError("opponent chi ho tro 'random' hoac 'heuristic'.")


def _select_training_action(
    game: Any,
    q_network: Any,
    epsilon: float,
    rng: np.random.Generator,
    torch: Any,
    device: Any,
) -> int:
    """Chon nuoc bang epsilon-greedy, luon chi tren cac cot hop le."""
    from connect_four.agents.dqn import mask_q_values

    legal = game.legal_actions()
    if not legal:
        raise ValueError("Khong con nuoc di hop le cho DQN.")
    if float(rng.random()) < epsilon:
        return int(rng.choice(legal))

    state = np.asarray(game.to_array(), dtype=np.float32)
    if state.shape != (2, ROWS, COLS):
        raise ValueError(f"game.to_array() phai co shape (2, {ROWS}, {COLS}).")
    state_tensor = torch.as_tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
    with torch.no_grad():
        q_values = q_network(state_tensor)[0].detach().cpu().numpy()
    return int(np.argmax(mask_q_values(q_values, legal)))


def _train_batch(
    replay_buffer: ReplayBuffer,
    q_network: Any,
    target_network: Any,
    optimizer: Any,
    torch: Any,
    functional: Any,
    device: Any,
    batch_size: int,
    gamma: float,
) -> float:
    """Thuc hien mot cap nhat Bellman voi Huber loss va mask next-state."""
    batch = replay_buffer.sample(batch_size)
    states = torch.as_tensor(
        np.stack([item.state for item in batch]), dtype=torch.float32, device=device
    )
    actions = torch.as_tensor(
        [item.action for item in batch], dtype=torch.long, device=device
    )
    rewards = torch.as_tensor(
        [item.reward for item in batch], dtype=torch.float32, device=device
    )
    next_states = torch.as_tensor(
        np.stack([item.next_state for item in batch]), dtype=torch.float32, device=device
    )
    dones = torch.as_tensor(
        [item.done for item in batch], dtype=torch.bool, device=device
    )
    next_masks = torch.as_tensor(
        np.stack([item.next_legal_mask for item in batch]), dtype=torch.bool, device=device
    )

    predicted_q = q_network(states).gather(1, actions.unsqueeze(1)).squeeze(1)
    with torch.no_grad():
        next_q_values = target_network(next_states)
        next_q_values = next_q_values.masked_fill(~next_masks, -torch.inf)
        max_next_q = next_q_values.max(dim=1).values
        # Cac transition ket thuc co mask rong va khong bootstrap.
        max_next_q = torch.where(dones, torch.zeros_like(max_next_q), max_next_q)
        target_q = rewards + gamma * max_next_q

    loss = functional.smooth_l1_loss(predicted_q, target_q)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()
    return float(loss.detach().cpu().item())


def _write_checkpoint(
    path: Path,
    episode: int,
    q_network: Any,
    optimizer: Any,
    epsilon: float,
    config: dict[str, Any],
    run_id: str,
    device_name: str,
    torch: Any,
    updates: int,
    elapsed_seconds: float,
) -> None:
    """Luu state_dict va JSON metadata doc lap, tuong thich voi DQNAgent."""
    path.parent.mkdir(parents=True, exist_ok=True)
    state_dict = {key: value.detach().cpu() for key, value in q_network.state_dict().items()}
    torch.save(
        {
            "model_state_dict": state_dict,
            "optimizer_state_dict": optimizer.state_dict(),
            "episode": episode,
            "epsilon": epsilon,
            "seed": config["seed"],
            "config": config,
        },
        path,
    )
    metadata = {
        "checkpoint_file": path.name,
        "episode": episode,
        "epsilon": epsilon,
        "optimizer_updates": updates,
        "run_id": run_id,
        "status": "pilot" if episode < 1_000 else "training",
        "git_commit": _git_revision(),
        "python_version": platform.python_version(),
        "torch_version": torch.__version__,
        "device": device_name,
        "accelerator": (
            torch.cuda.get_device_name(0)
            if device_name == "cuda" and torch.cuda.is_available()
            else (platform.processor() or "CPU")
        ),
        "hardware": platform.platform(),
        "training_elapsed_seconds": round(elapsed_seconds, 3),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": config,
    }
    path.with_suffix(".json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def train_dqn(
    episodes: int = 10_000,
    opponent: str = "heuristic",
    lr: float = 1e-3,
    gamma: float = 0.99,
    epsilon_start: float = 1.0,
    epsilon_min: float = 0.05,
    epsilon_decay: float = 0.9995,
    buffer_size: int = 100_000,
    batch_size: int = 64,
    target_update_freq: int = 500,
    checkpoint_milestones: Sequence[int] = (1_000, 2_500, 5_000, 10_000),
    out_dir: str | Path = "checkpoints/level6_dqn",
    log_dir: str | Path = "results/logs",
    seed: int = 0,
    device: str = "auto",
    run_id: str | None = None,
) -> Path:
    """Huan luyen DQN gap Random/Heuristic va tra ve checkpoint cuoi.

    Moi episode doi ben di truoc/sau. Transition cua DQN duoc ghi sau khi doi
    thu da dap lai, de ``next_state`` la ban co o luot DQN tiep theo. Phan thuong
    cuoi van theo goc nhin DQN: thang +1, hoa 0, thua -1; cac buoc chua ket thuc
    nhan 0. Target Network dung mask cot hop le va Huber loss.

    PyTorch chi duoc import khi ham duoc goi. Log moi episode duoc ghi vao
    ``results/logs/train_dqn_<run_id>.csv``. Checkpoint o cac moc duoc kem JSON
    metadata; checkpoint cuoi luon duoc luu de tiep tuc huan luyen/kiem tra.
    """
    if isinstance(episodes, bool) or not isinstance(episodes, int) or episodes <= 0:
        raise ValueError("episodes phai la so nguyen duong.")
    if opponent not in {"random", "heuristic"}:
        raise ValueError("opponent chi ho tro 'random' hoac 'heuristic'.")
    if not math.isfinite(lr) or lr <= 0:
        raise ValueError("lr phai la so huu han duong.")
    if not math.isfinite(gamma) or not 0.0 <= gamma <= 1.0:
        raise ValueError("gamma phai nam trong [0, 1].")
    if isinstance(buffer_size, bool) or not isinstance(buffer_size, int) or buffer_size <= 0:
        raise ValueError("buffer_size phai la so nguyen duong.")
    if isinstance(batch_size, bool) or not isinstance(batch_size, int) or batch_size <= 0:
        raise ValueError("batch_size phai la so nguyen duong.")
    if batch_size > buffer_size:
        raise ValueError("batch_size khong duoc lon hon buffer_size.")
    if (
        isinstance(target_update_freq, bool)
        or not isinstance(target_update_freq, int)
        or target_update_freq <= 0
    ):
        raise ValueError("target_update_freq phai la so nguyen duong.")
    schedule = EpsilonSchedule(epsilon_start, epsilon_min, epsilon_decay)
    milestones = tuple(sorted(set(checkpoint_milestones)))
    if any(isinstance(value, bool) or not isinstance(value, int) or value <= 0 for value in milestones):
        raise ValueError("checkpoint_milestones phai gom cac so nguyen duong.")
    if device != "auto" and device not in {"cpu", "cuda"}:
        raise ValueError("device chi nhan 'auto', 'cpu' hoac 'cuda'.")
    if run_id is None:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", run_id):
        raise ValueError("run_id chi duoc chua chu, so, gach ngang va gach duoi.")

    try:
        import torch
        import torch.nn.functional as functional
    except ImportError as err:
        raise ImportError(
            "Can PyTorch de huan luyen DQN. Cai dat bang: python -m pip install '.[torch]'"
        ) from err

    from connect_four.agents.dqn import legal_action_mask
    from connect_four.agents.networks import DQNNet
    from connect_four.game import ConnectFour, PLAYER_2

    selected_device = "cuda" if device == "auto" and torch.cuda.is_available() else device
    if selected_device == "auto":
        selected_device = "cpu"
    if selected_device == "cuda" and not torch.cuda.is_available():
        raise ValueError("Da chon device='cuda' nhung PyTorch khong nhan dien GPU CUDA.")
    torch_device = torch.device(selected_device)

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    rng = np.random.default_rng(seed)

    q_network = DQNNet(in_channels=2).to(torch_device)
    target_network = DQNNet(in_channels=2).to(torch_device)
    target_network.load_state_dict(q_network.state_dict())
    target_network.eval()
    optimizer = torch.optim.Adam(q_network.parameters(), lr=lr)
    replay_buffer = ReplayBuffer(capacity=buffer_size, seed=seed)

    out_path = Path(out_dir)
    log_path = Path(log_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    log_path.mkdir(parents=True, exist_ok=True)
    csv_path = log_path / f"train_dqn_{run_id}.csv"
    final_checkpoint = out_path / "dqn_model.pt"
    config_snapshot: dict[str, Any] = {
        "episodes": episodes,
        "opponent": opponent,
        "lr": lr,
        "gamma": gamma,
        "epsilon_start": epsilon_start,
        "epsilon_min": epsilon_min,
        "epsilon_decay": epsilon_decay,
        "buffer_size": buffer_size,
        "batch_size": batch_size,
        "target_update_freq": target_update_freq,
        "checkpoint_milestones": list(milestones),
        "out_dir": str(out_path),
        "log_dir": str(log_path),
        "seed": seed,
        "device": selected_device,
    }

    update_steps = 0
    started_all = time.perf_counter()
    columns = [
        "episode",
        "opponent",
        "agent_player",
        "result",
        "reward",
        "moves",
        "dqn_moves",
        "epsilon",
        "mean_loss",
        "optimizer_updates",
        "replay_size",
        "elapsed_seconds",
        "seed",
        "device",
    ]

    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=columns)
        writer.writeheader()

        for episode in range(1, episodes + 1):
            game = ConnectFour()
            agent_player = PLAYER_1 if episode % 2 == 1 else PLAYER_2
            opponent_agent = _build_opponent(opponent, seed + episode)
            epsilon_used = schedule.value
            episode_losses: list[float] = []
            dqn_moves = 0
            pending: tuple[np.ndarray, int] | None = None
            episode_started = time.perf_counter()

            while not game.is_terminal():
                transition_added = False
                if game.current_player == agent_player:
                    state = np.asarray(game.to_array(), dtype=np.float32)
                    action = _select_training_action(
                        game, q_network, epsilon_used, rng, torch, torch_device
                    )
                    game.step(action)
                    dqn_moves += 1
                    pending = (state, action)

                    # Neu DQN thang ngay bang nuoc vua di, khong cho doi thu dap lai.
                    if game.is_terminal():
                        next_state = np.asarray(game.to_array(), dtype=np.float32)
                        replay_buffer.add(
                            state,
                            action,
                            game.result(agent_player),
                            next_state,
                            True,
                            np.zeros(COLS, dtype=np.bool_),
                        )
                        transition_added = True
                        pending = None
                else:
                    opponent_action = opponent_agent.choose(game)
                    game.step(opponent_action)
                    if pending is not None:
                        done = game.is_terminal()
                        next_state = np.asarray(game.to_array(), dtype=np.float32)
                        next_mask = legal_action_mask(game.legal_actions())
                        reward = game.result(agent_player) if done else 0.0
                        replay_buffer.add(
                            pending[0],
                            pending[1],
                            reward,
                            next_state,
                            done,
                            next_mask,
                        )
                        transition_added = True
                        pending = None

                if transition_added and len(replay_buffer) >= batch_size:
                    q_network.train()
                    loss_value = _train_batch(
                        replay_buffer,
                        q_network,
                        target_network,
                        optimizer,
                        torch,
                        functional,
                        torch_device,
                        batch_size,
                        gamma,
                    )
                    episode_losses.append(loss_value)
                    update_steps += 1
                    if update_steps % target_update_freq == 0:
                        target_network.load_state_dict(q_network.state_dict())
                        target_network.eval()

            episode_reward = float(game.result(agent_player))
            result_label = "win" if episode_reward > 0 else "loss" if episode_reward < 0 else "draw"
            elapsed_episode = time.perf_counter() - episode_started
            mean_loss = float(np.mean(episode_losses)) if episode_losses else 0.0
            writer.writerow(
                {
                    "episode": episode,
                    "opponent": opponent,
                    "agent_player": agent_player,
                    "result": result_label,
                    "reward": episode_reward,
                    "moves": len(game.moves_played()),
                    "dqn_moves": dqn_moves,
                    "epsilon": epsilon_used,
                    "mean_loss": mean_loss,
                    "optimizer_updates": update_steps,
                    "replay_size": len(replay_buffer),
                    "elapsed_seconds": round(elapsed_episode, 6),
                    "seed": seed,
                    "device": selected_device,
                }
            )
            csv_file.flush()

            schedule.step()
            if episode in milestones:
                milestone_path = out_path / f"dqn_model_ep{episode:06d}.pt"
                _write_checkpoint(
                    milestone_path,
                    episode,
                    q_network,
                    optimizer,
                    schedule.value,
                    config_snapshot,
                    run_id,
                    selected_device,
                    torch,
                    update_steps,
                    time.perf_counter() - started_all,
                )

    elapsed_all = time.perf_counter() - started_all
    _write_checkpoint(
        final_checkpoint,
        episodes,
        q_network,
        optimizer,
        schedule.value,
        config_snapshot,
        run_id,
        selected_device,
        torch,
        update_steps,
        elapsed_all,
    )
    print(
        f"DQN training done: episodes={episodes}, opponent={opponent}, "
        f"updates={update_steps}, log={csv_path}, checkpoint={final_checkpoint}, "
        f"elapsed={elapsed_all:.1f}s"
    )
    return final_checkpoint


def train_dqn_from_config(config_path: str | Path) -> Path:
    """Doc YAML va goi ``train_dqn`` voi cac tham so trong file cau hinh."""
    try:
        import yaml
    except ImportError as err:
        raise ImportError(
            "Can PyYAML de doc cau hinh. Cai dat bang: python -m pip install PyYAML"
        ) from err

    path = Path(config_path)
    if not path.is_file():
        raise FileNotFoundError(f"Khong tim thay file cau hinh DQN: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Noi dung YAML phai la mot mapping tham so DQN.")

    allowed = {
        "episodes",
        "opponent",
        "lr",
        "gamma",
        "epsilon_start",
        "epsilon_min",
        "epsilon_decay",
        "buffer_size",
        "batch_size",
        "target_update_freq",
        "checkpoint_milestones",
        "out_dir",
        "log_dir",
        "seed",
        "device",
        "run_id",
    }
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise ValueError(f"Tham so khong duoc ho tro trong YAML: {unknown}")
    return train_dqn(**data)


def main(argv: Sequence[str] | None = None) -> None:
    """Diem vao CLI: python -m connect_four.training.train_dqn --config ..."""
    parser = argparse.ArgumentParser(description="Huan luyen DQN cho Connect Four 7x6")
    parser.add_argument(
        "--config",
        default="configs/dqn_training_pilot.yaml",
        help="Duong dan file YAML cau hinh huan luyen",
    )
    args = parser.parse_args(argv)
    train_dqn_from_config(args.config)


if __name__ == "__main__":
    main()
