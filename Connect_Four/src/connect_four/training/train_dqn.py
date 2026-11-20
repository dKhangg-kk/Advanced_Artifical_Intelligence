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

    def state_dict(self) -> dict[str, Any]:
        """Trang thai day du (transition theo thu tu FIFO + RNG) de tiep tuc huan luyen."""
        items = list(self._memory)
        empty_state = np.zeros((0, 2, ROWS, COLS), dtype=np.float32)
        return {
            "capacity": self.capacity,
            "rng_state": self._rng.getstate(),
            "states": np.stack([t.state for t in items]) if items else empty_state,
            "actions": np.asarray([t.action for t in items], dtype=np.int64),
            "rewards": np.asarray([t.reward for t in items], dtype=np.float32),
            "next_states": np.stack([t.next_state for t in items]) if items else empty_state.copy(),
            "dones": np.asarray([t.done for t in items], dtype=np.bool_),
            "next_legal_masks": (
                np.stack([t.next_legal_mask for t in items]) if items else np.zeros((0, COLS), dtype=np.bool_)
            ),
        }

    def load_state_dict(self, state: dict[str, Any]) -> None:
        """Khoi phuc tu ``state_dict()``; giu nguyen thu tu FIFO va trang thai RNG."""
        if int(state["capacity"]) != self.capacity:
            raise ValueError("capacity cua trang thai luu khong khop ReplayBuffer hien tai.")
        self._memory.clear()
        for i in range(len(state["actions"])):
            self._memory.append(
                DQNTransition(
                    state=np.asarray(state["states"][i], dtype=np.float32).copy(),
                    action=int(state["actions"][i]),
                    reward=float(state["rewards"][i]),
                    next_state=np.asarray(state["next_states"][i], dtype=np.float32).copy(),
                    done=bool(state["dones"][i]),
                    next_legal_mask=np.asarray(state["next_legal_masks"][i], dtype=np.bool_).copy(),
                )
            )
        self._rng.setstate(state["rng_state"])


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


SUPPORTED_OPPONENTS = ("random", "heuristic", "selfplay")


def _build_opponent(name: str, seed: int) -> Any:
    """Tao doi thu co seed rieng cho mot episode.

    ``selfplay`` khong tao o day: doi thu tu choi la ban sao dong bang cua chinh
    mang dang hoc, do ``SelfPlayOpponentPool`` quan ly trong ``train_dqn``.
    """
    if name == "random":
        from connect_four.agents.random_agent import RandomAgent

        return RandomAgent(seed=seed)
    if name == "heuristic":
        from connect_four.agents.heuristic import HeuristicAgent

        return HeuristicAgent(seed=seed)
    raise ValueError("opponent chi ho tro 'random' hoac 'heuristic' (selfplay dung SelfPlayOpponentPool).")


class SnapshotOpponent:
    """Doi thu tu choi: ban sao dong bang cua Q-network, chon nuoc epsilon-greedy.

    Ban sao khong bao gio duoc cap nhat gradient. Nuoc di luon nam trong cac cot
    hop le (mat na -inf truoc argmax), giong DQNAgent. ``epsilon`` duoc gan lai
    moi episode de doi thu kham pha cung muc voi tac tu dang hoc.
    """

    def __init__(
        self,
        network: Any,
        torch: Any,
        device: Any,
        rng: np.random.Generator,
        epsilon: float,
        snapshot_episode: int,
    ) -> None:
        self.network = network
        self.torch = torch
        self.device = device
        self.rng = rng
        self.epsilon = float(epsilon)
        self.snapshot_episode = int(snapshot_episode)

    def choose(self, game: Any) -> int:
        return _select_training_action(
            game, self.network, self.epsilon, self.rng, self.torch, self.device
        )


class SelfPlayOpponentPool:
    """Tap doi thu lich su cho self-play (Liu 2025, ch.13; Silver va cs. 2016).

    Moi ``snapshot_every`` episode, trong so hien tai cua mang dang hoc duoc chep
    thanh mot doi thu dong bang moi; chi giu ``pool_size`` ban gan nhat. Moi
    episode lay ngau nhien mot doi thu trong tap. Giu nhieu phien ban cu giup giam
    hien tuong "quen" cach thang cac loi choi cu va lam moi truong it dao dong hon
    so voi doi dau truc tiep voi mang dang cap nhat.
    """

    def __init__(
        self,
        make_network: Any,
        torch: Any,
        device: Any,
        rng: np.random.Generator,
        snapshot_every: int = 500,
        pool_size: int = 5,
    ) -> None:
        if isinstance(snapshot_every, bool) or not isinstance(snapshot_every, int) or snapshot_every <= 0:
            raise ValueError("selfplay_snapshot_every phai la so nguyen duong.")
        if isinstance(pool_size, bool) or not isinstance(pool_size, int) or pool_size <= 0:
            raise ValueError("selfplay_pool_size phai la so nguyen duong.")
        self.make_network = make_network
        self.torch = torch
        self.device = device
        self.rng = rng
        self.snapshot_every = snapshot_every
        self.pool_size = pool_size
        self.snapshots: Deque[tuple[int, Any]] = deque(maxlen=pool_size)

    def add_snapshot(self, q_network: Any, episode: int) -> None:
        network = self.make_network().to(self.device)
        network.load_state_dict(q_network.state_dict())
        network.eval()
        for parameter in network.parameters():
            parameter.requires_grad_(False)
        self.snapshots.append((int(episode), network))

    def maybe_snapshot(self, q_network: Any, episode: int) -> bool:
        """Them ban sao neu ``episode`` la boi cua ``snapshot_every``."""
        if episode % self.snapshot_every == 0:
            self.add_snapshot(q_network, episode)
            return True
        return False

    def sample(self, epsilon: float) -> SnapshotOpponent:
        if not self.snapshots:
            raise ValueError("Tap doi thu self-play dang rong.")
        index = int(self.rng.integers(len(self.snapshots)))
        episode, network = self.snapshots[index]
        return SnapshotOpponent(network, self.torch, self.device, self.rng, epsilon, episode)


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
    opening_plies: int = 0,
    selfplay_snapshot_every: int = 500,
    selfplay_pool_size: int = 5,
    resume_every: int = 0,
) -> Path:
    """Huan luyen DQN gap Random/Heuristic hoac tu choi (self-play), tra ve checkpoint cuoi.

    Moi episode doi ben di truoc/sau. Transition cua DQN duoc ghi sau khi doi
    thu da dap lai, de ``next_state`` la ban co o luot DQN tiep theo. Phan thuong
    cuoi van theo goc nhin DQN: thang +1, hoa 0, thua -1; cac buoc chua ket thuc
    nhan 0. Target Network dung mask cot hop le va Huber loss.

    ``opening_plies`` (mac dinh 0 = bat dau tu ban trong, hanh vi goc) cho phep dat truoc
    mot so nuoc ngau nhien hop le o dau moi episode, de huan luyen tren cung kieu
    khai cuoc ngau nhien nhu luc validation/giai dau. Cac nuoc dat truoc khong tao
    transition cho DQN.

    ``opponent="selfplay"``: doi thu la mot ban sao dong bang cua chinh mang dang
    hoc, lay ngau nhien tu tap ``selfplay_pool_size`` ban gan nhat; ban sao moi
    duoc chep moi ``selfplay_snapshot_every`` episode (ban dau la trong so khoi
    tao). Doi thu choi epsilon-greedy voi cung epsilon cua episode. Chi tac tu
    dang hoc nhan gradient; vong lap, phan thuong va cach chot transition giu
    nguyen nhu khi gap doi thu co dinh.

    ``resume_every`` > 0: cu moi ``resume_every`` episode luu ``resume_state.pt``
    (mang, mang muc tieu, optimizer, Replay Buffer, tap self-play, moi trang thai
    RNG) vao ``out_dir``. Goi lai voi cung tham so va ``run_id`` se tiep tuc tu
    episode da luu, cat log CSV ve dung episode do; ket qua giong het chay mot
    mach. Mac dinh 0 = tat (hanh vi cu).

    PyTorch chi duoc import khi ham duoc goi. Log moi episode duoc ghi vao
    ``results/logs/train_dqn_<run_id>.csv``. Checkpoint o cac moc duoc kem JSON
    metadata; checkpoint cuoi luon duoc luu de tiep tuc huan luyen/kiem tra.
    """
    if isinstance(episodes, bool) or not isinstance(episodes, int) or episodes <= 0:
        raise ValueError("episodes phai la so nguyen duong.")
    if opponent not in SUPPORTED_OPPONENTS:
        raise ValueError("opponent chi ho tro 'random', 'heuristic' hoac 'selfplay'.")
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
    if isinstance(opening_plies, bool) or not isinstance(opening_plies, int) or not 0 <= opening_plies <= 10:
        raise ValueError("opening_plies phai la so nguyen trong khoang 0..10.")
    if isinstance(resume_every, bool) or not isinstance(resume_every, int) or resume_every < 0:
        raise ValueError("resume_every phai la so nguyen khong am.")
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
    selfplay_pool: SelfPlayOpponentPool | None = None
    if opponent == "selfplay":
        selfplay_pool = SelfPlayOpponentPool(
            lambda: DQNNet(in_channels=2),
            torch,
            torch_device,
            np.random.default_rng(seed + 1),
            snapshot_every=selfplay_snapshot_every,
            pool_size=selfplay_pool_size,
        )
        selfplay_pool.add_snapshot(q_network, 0)

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
    if opening_plies:
        config_snapshot["opening_plies"] = opening_plies
    if opponent == "selfplay":
        config_snapshot["selfplay_snapshot_every"] = selfplay_snapshot_every
        config_snapshot["selfplay_pool_size"] = selfplay_pool_size

    update_steps = 0
    start_episode = 1
    elapsed_offset = 0.0
    resume_path = out_path / "resume_state.pt"
    if resume_every and resume_path.is_file():
        saved = torch.load(resume_path, map_location=torch_device, weights_only=False)
        if saved["run_id"] != run_id or saved["config"] != config_snapshot:
            raise ValueError(
                f"{resume_path} thuoc run/cau hinh khac; xoa file hoac dung dung run_id va tham so."
            )
        q_network.load_state_dict(saved["q_network"])
        target_network.load_state_dict(saved["target_network"])
        optimizer.load_state_dict(saved["optimizer"])
        replay_buffer.load_state_dict(saved["replay_buffer"])
        schedule.episode = int(saved["schedule_episode"])
        update_steps = int(saved["update_steps"])
        start_episode = int(saved["episode"]) + 1
        elapsed_offset = float(saved["elapsed_seconds"])
        rng.bit_generator.state = saved["numpy_rng"]
        random.setstate(saved["python_random"])
        np.random.set_state(saved["numpy_global"])
        torch.set_rng_state(saved["torch_rng"])
        if selfplay_pool is not None:
            selfplay_pool.snapshots.clear()
            for snap_episode, snap_state in saved["selfplay_snapshots"]:
                snap = DQNNet(in_channels=2).to(torch_device)
                snap.load_state_dict(snap_state)
                selfplay_pool.add_snapshot(snap, snap_episode)
            selfplay_pool.rng.bit_generator.state = saved["selfplay_rng"]
        print(f"Tiep tuc {run_id} tu episode {start_episode} ({resume_path})", flush=True)

    def _save_resume(episode_done: int) -> None:
        payload = {
            "run_id": run_id,
            "config": config_snapshot,
            "episode": episode_done,
            "q_network": q_network.state_dict(),
            "target_network": target_network.state_dict(),
            "optimizer": optimizer.state_dict(),
            "replay_buffer": replay_buffer.state_dict(),
            "schedule_episode": schedule.episode,
            "update_steps": update_steps,
            "elapsed_seconds": time.perf_counter() - started_all,
            "numpy_rng": rng.bit_generator.state,
            "python_random": random.getstate(),
            "numpy_global": np.random.get_state(),
            "torch_rng": torch.get_rng_state(),
            "selfplay_snapshots": (
                [(ep, net.state_dict()) for ep, net in selfplay_pool.snapshots] if selfplay_pool else []
            ),
            "selfplay_rng": selfplay_pool.rng.bit_generator.state if selfplay_pool else None,
        }
        tmp_path = resume_path.with_suffix(".tmp")
        torch.save(payload, tmp_path)
        tmp_path.replace(resume_path)

    started_all = time.perf_counter() - elapsed_offset
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
    if selfplay_pool is not None:
        columns.append("opponent_snapshot_episode")

    if start_episode > 1 and csv_path.is_file():
        # Cat log ve dung episode da luu trong resume_state (bo cac dong chay do sau do).
        with csv_path.open(newline="", encoding="utf-8") as stream:
            kept = [row for row in csv.DictReader(stream) if int(row["episode"]) < start_episode]
        with csv_path.open("w", newline="", encoding="utf-8") as stream:
            rewrite = csv.DictWriter(stream, fieldnames=columns)
            rewrite.writeheader()
            rewrite.writerows(kept)
    csv_mode = "a" if start_episode > 1 else "w"

    with csv_path.open(csv_mode, newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=columns)
        if csv_mode == "w":
            writer.writeheader()

        for episode in range(start_episode, episodes + 1):
            game = ConnectFour()
            for _ in range(opening_plies):
                game.step(int(rng.choice(game.legal_actions())))
            agent_player = PLAYER_1 if episode % 2 == 1 else PLAYER_2
            epsilon_used = schedule.value
            if selfplay_pool is not None:
                opponent_agent = selfplay_pool.sample(epsilon_used)
            else:
                opponent_agent = _build_opponent(opponent, seed + episode)
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
            log_row = {
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
            if selfplay_pool is not None:
                log_row["opponent_snapshot_episode"] = opponent_agent.snapshot_episode
            writer.writerow(log_row)
            csv_file.flush()
            if selfplay_pool is not None:
                selfplay_pool.maybe_snapshot(q_network, episode)

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
            if resume_every and episode % resume_every == 0 and episode < episodes:
                _save_resume(episode)

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
    if resume_path.is_file():
        resume_path.unlink()  # da xong; file trang thai lon (Replay Buffer) khong can giu
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
        "opening_plies",
        "selfplay_snapshot_every",
        "selfplay_pool_size",
        "resume_every",
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
