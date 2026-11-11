"""Tac tu CNN policy cap 5, nap mo hinh bang lazy import PyTorch."""

from __future__ import annotations

from pathlib import Path
import time
from typing import Any

import numpy as np

from connect_four.agents.base import Agent, SearchStats
from connect_four.game.base import ConnectFourGame
from connect_four.game.constants import COLS, ROWS


class NNAgent(Agent):
    """Tac tu chon nuoc hop le bang CNNPolicyNet da huan luyen."""

    name = "nn"
    level = 5

    def __init__(self, checkpoint: str | Path | None = None, seed: int | None = None) -> None:
        super().__init__(seed=seed)
        self.checkpoint = Path(checkpoint) if checkpoint is not None else None
        self._model: Any | None = None
        self._torch: Any | None = None

    @staticmethod
    def _state_dict_from_checkpoint(payload: Any) -> Any:
        if isinstance(payload, dict):
            for key in ("model_state_dict", "policy_state_dict", "state_dict"):
                candidate = payload.get(key)
                if isinstance(candidate, dict):
                    return candidate
        return payload

    def _ensure_model_loaded(self) -> None:
        if self._model is not None:
            return
        if self.checkpoint is not None and not self.checkpoint.is_file():
            raise FileNotFoundError(f"Khong tim thay checkpoint CNN: {self.checkpoint}")

        try:
            import torch
        except ImportError as err:
            raise ImportError(
                "Can cai PyTorch de su dung NNAgent: pip install '.[torch]' hoac pip install torch."
            ) from err
        from connect_four.agents.networks import CNNPolicyNet

        if self.seed is not None:
            torch.manual_seed(self.seed)
        model = CNNPolicyNet(in_channels=2)
        if self.checkpoint is not None:
            try:
                payload = torch.load(self.checkpoint, map_location="cpu", weights_only=True)
            except TypeError:
                payload = torch.load(self.checkpoint, map_location="cpu")
            state_dict = self._state_dict_from_checkpoint(payload)
            if not isinstance(state_dict, dict):
                raise ValueError(f"Checkpoint CNN khong chua state_dict hop le: {self.checkpoint}")
            model.load_state_dict(state_dict)
        model.eval()
        self._torch = torch
        self._model = model

    def choose(self, game: ConnectFourGame) -> int:
        """Chon cot hop le co logit cao nhat, khong sua trang thai game."""
        started = time.perf_counter()
        self.last_stats = SearchStats()
        legal = game.legal_actions()
        if not legal:
            raise ValueError("Khong con nuoc di hop le.")

        legal_mask = np.zeros(COLS, dtype=np.bool_)
        for action in legal:
            if isinstance(action, bool) or not isinstance(action, (int, np.integer)):
                raise ValueError(f"Cot hop le khong dung dinh dang so nguyen: {action!r}")
            if not 0 <= int(action) < COLS:
                raise ValueError(f"Cot hop le nam ngoai mien 0..{COLS - 1}: {action!r}")
            legal_mask[int(action)] = True

        state = np.asarray(game.to_array(), dtype=np.float32)
        if state.shape != (2, ROWS, COLS):
            raise ValueError(
                f"game.to_array() phai co shape (2, {ROWS}, {COLS}), nhan duoc {state.shape}."
            )
        if not np.isfinite(state).all():
            raise ValueError("game.to_array() chi duoc chua gia tri huu han.")

        self._ensure_model_loaded()
        tensor = self._torch.as_tensor(state, dtype=self._torch.float32).unsqueeze(0)
        with self._torch.no_grad():
            prediction = self._model(tensor)
        logits = prediction.detach().cpu().numpy()
        if logits.shape != (1, COLS):
            raise ValueError(f"CNNPolicyNet phai tra ve shape (1, {COLS}), nhan duoc {logits.shape}.")
        if not np.isfinite(logits[0, legal_mask]).all():
            raise ValueError("Logit cua cac cot hop le phai la so huu han.")

        masked_logits = logits[0].copy()
        masked_logits[~legal_mask] = -np.inf
        action = int(np.argmax(masked_logits))
        self.last_stats.extra["legal_actions"] = float(len(legal))
        self.last_stats.time_ms = (time.perf_counter() - started) * 1000.0
        return action
