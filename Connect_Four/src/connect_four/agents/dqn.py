"""Cap 6 - Reinforcement Learning: Deep Q-Network (DQN).

Thiet ke theo Proposal Do an cuoi ky:
    - Bieu dien trang thai: Tensor nhi phan 2x6x7 (quan ta, quan doi thu).
    - Mo hinh: Deep Q-Network uoc luong Q(s, a) cho 7 hanh dong (cot 0-6).
    - Ra quyet dinh: Loc mat na tren cac cot hop le (legal action mask), chon nuoc
      di co Q-value cao nhat trong tap hop le: a = argmax_{c in legal} Q(s, c).
    - Huan luyen:
      * Replay Buffer (kich thuoc toi da 100.000 transition).
      * Target Network dong bang cap nhat dinh ky (giam thieu mat on dinh).
      * Chien luoc kham pha Epsilon-Greedy co lich trinh suy giam (Epsilon Decay).
      * Ham mat mat: Huber Loss hoac MSE Loss giua Q(s, a) va muc tieu Bellman:
        y = r + gamma * max_{a'} Q_target(s', a').
      * Danh gia checkpoint doc lap tai cac moc 1.000, 2.500, 5.000, 10.000 episode.

LUU Y: PyTorch duoc import lazy ben trong model/choose de khong anh huong toi
kiem thu co ban khi chua cai dat torch.
"""

from __future__ import annotations

from pathlib import Path
import random

from connect_four.agents.base import Agent
from connect_four.game.base import ConnectFourGame


class DQNAgent(Agent):
    """Tac tu hoc tang cuong bang Deep Q-Network (Cap 6)."""

    name = "dqn"
    level = 6

    def __init__(
        self,
        checkpoint: str | Path | None = None,
        epsilon: float = 0.0,
        seed: int | None = None,
    ) -> None:
        super().__init__(seed=seed)
        self.checkpoint = Path(checkpoint) if checkpoint else None
        self.epsilon = float(epsilon)
        self._model = None
        self._rng = random.Random(seed)

    def choose(self, game: ConnectFourGame) -> int:
        """Chon nuoc di dua tren Q-value va mat na nuoc di hop le.

        Neu epsilon > 0 va dang trong qua trinh kham pha (training), co the chon
        ngau nhien nuoc di hop le theo xac suat epsilon. Khi thi dau/danh gia
        (evaluation), epsilon mac dinh = 0.0 (hoan toan greedy).
        """
        legal = game.legal_actions()
        if not legal:
            raise ValueError("Khong con nuoc di hop le.")

        # Epsilon-greedy kham pha
        if self.epsilon > 0.0 and self._rng.random() < self.epsilon:
            return self._rng.choice(legal)

        # TODO: Khi da cai dat trong so / PyTorch:
        # 1. Chuyen trang thai `game` ve tensor (1, 2, 6, 7).
        # 2. Dua qua Q-network tinh q_values (1, 7).
        # 3. Dat q_values cua cac cot khong hop le ve -inf.
        # 4. Tra ve argmax(q_values).
        raise NotImplementedError("TODO: Nap checkpoint DQN va tinh Q-values tren cot hop le.")
