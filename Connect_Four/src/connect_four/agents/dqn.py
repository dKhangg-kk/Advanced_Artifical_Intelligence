"""Tac tu DQN cap 6 va cac ham mat na hanh dong hop le.

Cac ham ``legal_action_mask`` va ``mask_q_values`` chi dung NumPy nen co the
kiem thu tren moi truong chua cai PyTorch. PyTorch chi duoc nap khi DQNAgent
can khoi tao mang o lan ``choose()`` dau tien.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
import random
import time
from typing import Any

import numpy as np

from connect_four.agents.base import Agent, SearchStats
from connect_four.game.base import ConnectFourGame
from connect_four.game.constants import COLS, ROWS


def legal_action_mask(
    legal_actions: Sequence[int], action_size: int = COLS
) -> np.ndarray:
    """Tao bool mask cho cac cot hop le.

    Gia tri True danh dau hanh dong duoc phep; False danh dau cot day/khong hop
    le. Tap hanh dong rong duoc chap nhan de bieu dien trang thai da ket thuc.
    """
    if isinstance(action_size, bool) or not isinstance(action_size, int) or action_size <= 0:
        raise ValueError("action_size phai la so nguyen duong.")

    mask = np.zeros(action_size, dtype=np.bool_)
    for action in legal_actions:
        if isinstance(action, bool) or not isinstance(action, (int, np.integer)):
            raise ValueError(f"Hanh dong khong hop le: {action!r}")
        column = int(action)
        if not 0 <= column < action_size:
            raise ValueError(f"Cot nam ngoai mien 0..{action_size - 1}: {column}")
        mask[column] = True
    return mask


def mask_q_values(q_values: Sequence[float] | np.ndarray, legal_actions: Sequence[int]) -> np.ndarray:
    """Dat Q-value cua moi hanh dong khong hop le thanh ``-inf``.

    Ham tra ve mang moi, khong sua mang dau vao. Neu khong con hanh dong hop le,
    ham nem ValueError de tranh argmax tren mot trang thai da ket thuc.
    """
    values = np.asarray(q_values, dtype=np.float64)
    if values.ndim != 1 or values.shape[0] != COLS:
        raise ValueError(f"q_values phai co shape ({COLS},), nhan duoc {values.shape}.")

    mask = legal_action_mask(legal_actions, action_size=values.shape[0])
    if not bool(mask.any()):
        raise ValueError("Khong con hanh dong hop le de chon.")
    if not np.isfinite(values[mask]).all():
        raise ValueError("Q-value cua hanh dong hop le phai la so huu han.")

    masked = values.copy()
    masked[~mask] = -np.inf
    return masked


class DQNAgent(Agent):
    """Tac tu dung Deep Q-Network da huan luyen (Cap 6).

    Khi ``checkpoint`` la None, agent tao DQNNet voi trong so khoi tao ngau
    nhien de kiem thu/tich hop. Truong hop nay khong duoc xem la checkpoint da
    huan luyen. Neu co duong dan checkpoint, trong so duoc nap o lan choose dau.
    """

    name = "dqn"
    level = 6

    def __init__(
        self,
        checkpoint: str | Path | None = None,
        epsilon: float = 0.0,
        seed: int | None = None,
    ) -> None:
        super().__init__(seed=seed)
        if not np.isfinite(epsilon) or not 0.0 <= float(epsilon) <= 1.0:
            raise ValueError("epsilon phai nam trong khoang [0, 1].")
        self.checkpoint = Path(checkpoint) if checkpoint is not None else None
        self.epsilon = float(epsilon)
        self._model: Any | None = None
        self._torch: Any | None = None
        self._rng = random.Random(seed)

    @staticmethod
    def _state_dict_from_checkpoint(payload: Any) -> Any:
        """Lay state_dict tu checkpoint dang tensor truc tiep hoac dict bao."""
        if isinstance(payload, dict):
            for key in ("model_state_dict", "q_network_state_dict", "policy_state_dict", "state_dict"):
                candidate = payload.get(key)
                if isinstance(candidate, dict):
                    return candidate
        return payload

    def _ensure_model_loaded(self) -> None:
        """Khoi tao DQNNet va nap checkpoint toi da mot lan."""
        if self._model is not None:
            return

        if self.checkpoint is not None and not self.checkpoint.is_file():
            raise FileNotFoundError(f"Khong tim thay checkpoint DQN: {self.checkpoint}")

        try:
            import torch
        except ImportError as err:
            raise ImportError(
                "Can cai PyTorch de su dung DQNAgent: pip install '.[torch]' hoac pip install torch."
            ) from err

        from connect_four.agents.networks import DQNNet

        model = DQNNet(in_channels=2)
        if self.checkpoint is not None:
            try:
                payload = torch.load(self.checkpoint, map_location="cpu", weights_only=True)
            except TypeError:  # Tuong thich voi cac ban PyTorch cu hon.
                payload = torch.load(self.checkpoint, map_location="cpu")
            state_dict = self._state_dict_from_checkpoint(payload)
            if not isinstance(state_dict, dict):
                raise ValueError("Checkpoint DQN khong chua state_dict hop le.")
            model.load_state_dict(state_dict)

        model.eval()
        self._torch = torch
        self._model = model

    def choose(self, game: ConnectFourGame) -> int:
        """Chon cot hop le theo epsilon-greedy va cap nhat ``last_stats``.

        ``game`` chi duoc doc qua ``legal_actions()`` va ``to_array()``; trang
        thai game khong bi thay doi. O che do thi dau, dat epsilon = 0.0.
        """
        started = time.perf_counter()
        self.last_stats = SearchStats()
        legal = game.legal_actions()
        if not legal:
            raise ValueError("Khong con nuoc di hop le.")

        # Nap checkpoint tai lan goi dau tien, ke ca khi nuoc nay la exploration.
        self._ensure_model_loaded()

        if self.epsilon > 0.0 and self._rng.random() < self.epsilon:
            action = int(self._rng.choice(legal))
        else:
            state = np.asarray(game.to_array(), dtype=np.float32)
            expected_shape = (2, ROWS, COLS)
            if state.shape != expected_shape:
                raise ValueError(
                    f"game.to_array() phai co shape {expected_shape}, nhan duoc {state.shape}."
                )

            tensor = self._torch.as_tensor(state, dtype=self._torch.float32).unsqueeze(0)
            with self._torch.no_grad():
                prediction = self._model(tensor)
            q_values = prediction.detach().cpu().numpy()
            if q_values.shape != (1, COLS):
                raise ValueError(
                    f"DQNNet phai tra ve shape (1, {COLS}), nhan duoc {q_values.shape}."
                )
            masked_values = mask_q_values(q_values[0], legal)
            action = int(np.argmax(masked_values))

        self.last_stats.extra["epsilon"] = self.epsilon
        self.last_stats.extra["legal_actions"] = float(len(legal))
        self.last_stats.time_ms = (time.perf_counter() - started) * 1000.0
        return action
