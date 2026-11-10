"""Test cho ReplayBuffer, EpsilonSchedule, action mask va DQNAgent."""

from __future__ import annotations

import numpy as np
import pytest

from connect_four.agents.dqn import DQNAgent, legal_action_mask, mask_q_values
from connect_four.game.reference import ReferenceGame
from connect_four.training.train_dqn import EpsilonSchedule, ReplayBuffer, epsilon_for_episode


def _add_sample(buffer: ReplayBuffer, value: float, *, done: bool = False) -> None:
    state = np.full((2, 6, 7), value, dtype=np.float32)
    next_state = np.full((2, 6, 7), value + 1, dtype=np.float32)
    next_mask = np.zeros(7, dtype=np.bool_) if done else np.array([True, True, True, True, True, True, True])
    buffer.add(state, int(value) % 7, float(value), next_state, done, next_mask)


def test_replay_buffer_respects_capacity_and_overwrites_oldest() -> None:
    buffer = ReplayBuffer(capacity=3, seed=7)
    for value in range(4):
        _add_sample(buffer, float(value))

    assert len(buffer) == 3
    stored_values = [item.reward for item in buffer._memory]
    assert stored_values == [1.0, 2.0, 3.0]


def test_replay_buffer_samples_exact_batch_without_replacement() -> None:
    buffer = ReplayBuffer(capacity=5, seed=11)
    for value in range(5):
        _add_sample(buffer, float(value))

    batch = buffer.sample(3)
    assert len(batch) == 3
    assert len({item.reward for item in batch}) == 3


def test_replay_buffer_copies_states_and_next_legal_mask() -> None:
    buffer = ReplayBuffer(capacity=2, seed=1)
    state = np.zeros((2, 6, 7), dtype=np.float32)
    next_state = np.ones((2, 6, 7), dtype=np.float32)
    mask = np.array([True, False, True, False, True, False, True])
    buffer.add(state, 0, 1.0, next_state, False, mask)

    state[:] = 9
    next_state[:] = 9
    mask[:] = False
    saved = buffer.sample(1)[0]
    assert np.all(saved.state == 0)
    assert np.all(saved.next_state == 1)
    assert saved.next_legal_mask.tolist() == [True, False, True, False, True, False, True]


def test_replay_buffer_allows_empty_next_mask_only_when_done() -> None:
    buffer = ReplayBuffer(capacity=2)
    _add_sample(buffer, 1.0, done=True)
    assert not buffer.sample(1)[0].next_legal_mask.any()

    with pytest.raises(ValueError, match="it nhat mot cot hop le"):
        buffer.add(
            np.zeros((2, 6, 7), dtype=np.float32),
            0,
            0.0,
            np.zeros((2, 6, 7), dtype=np.float32),
            False,
            np.zeros(7, dtype=np.bool_),
        )


def test_replay_buffer_rejects_invalid_batch_and_transition() -> None:
    buffer = ReplayBuffer(capacity=2)
    with pytest.raises(ValueError, match="Khong du transition"):
        buffer.sample(1)
    with pytest.raises(ValueError, match="batch_size"):
        buffer.sample(0)
    with pytest.raises(ValueError, match="shape"):
        buffer.add(np.zeros((6, 7)), 0, 0.0, np.zeros((2, 6, 7)), False, np.ones(7))


def test_epsilon_schedule_starts_at_one_and_never_below_floor() -> None:
    schedule = EpsilonSchedule(start=1.0, minimum=0.05, decay=0.5)
    assert schedule.value == 1.0
    assert schedule.step() == 0.5
    assert schedule.step() == 0.25
    for _ in range(20):
        schedule.step()
    assert schedule.value == 0.05
    schedule.reset()
    assert schedule.episode == 0
    assert schedule.value == 1.0


def test_epsilon_for_episode_uses_episode_decay() -> None:
    assert epsilon_for_episode(0) == 1.0
    assert epsilon_for_episode(1) == pytest.approx(0.9995)
    assert epsilon_for_episode(100_000) == 0.05


def test_epsilon_schedule_rejects_invalid_parameters() -> None:
    with pytest.raises(ValueError):
        EpsilonSchedule(start=0.01, minimum=0.05)
    with pytest.raises(ValueError):
        EpsilonSchedule(decay=0.0)


def test_legal_action_mask_marks_only_available_columns() -> None:
    mask = legal_action_mask([0, 3, 6])
    assert mask.dtype == np.bool_
    assert mask.tolist() == [True, False, False, True, False, False, True]
    assert legal_action_mask([]).tolist() == [False] * 7


def test_mask_q_values_sets_full_columns_to_negative_infinity() -> None:
    original = np.arange(7, dtype=np.float32)
    masked = mask_q_values(original, [1, 4])
    assert np.isneginf(masked[[0, 2, 3, 5, 6]]).all()
    assert masked[1] == 1.0
    assert masked[4] == 4.0
    assert np.array_equal(original, np.arange(7, dtype=np.float32))


def test_mask_q_values_rejects_empty_legal_actions_and_wrong_shape() -> None:
    with pytest.raises(ValueError, match="Khong con hanh dong"):
        mask_q_values(np.zeros(7), [])
    with pytest.raises(ValueError, match="shape"):
        mask_q_values(np.zeros((1, 7)), [0])


def test_dqn_agent_rejects_invalid_epsilon() -> None:
    with pytest.raises(ValueError, match="epsilon"):
        DQNAgent(epsilon=1.1)


def test_dqn_agent_loads_checkpoint_lazily_and_preserves_game(tmp_path) -> None:
    torch = pytest.importorskip("torch")
    from connect_four.agents.networks import DQNNet

    model = DQNNet()
    checkpoint = tmp_path / "dqn_state.pt"
    torch.save({"model_state_dict": model.state_dict()}, checkpoint)

    game = ReferenceGame()
    game.step(3)
    game.step(2)
    before_moves = tuple(game.moves_played())
    agent = DQNAgent(checkpoint=checkpoint, epsilon=0.0, seed=17)

    assert agent._model is None
    action = agent.choose(game)

    assert agent._model is not None
    assert action in game.legal_actions()
    assert tuple(game.moves_played()) == before_moves
    assert agent.last_stats.time_ms >= 0.0


def test_dqn_agent_selects_only_remaining_column() -> None:
    pytest.importorskip("torch")

    class OneColumnGame:
        def legal_actions(self) -> list[int]:
            return [5]

        def to_array(self) -> np.ndarray:
            return np.zeros((2, 6, 7), dtype=np.float32)

    agent = DQNAgent(epsilon=0.0, seed=3)
    assert agent.choose(OneColumnGame()) == 5  # type: ignore[arg-type]


def test_dqn_agent_reports_missing_checkpoint_before_loading_torch(tmp_path) -> None:
    missing = tmp_path / "missing.pt"
    agent = DQNAgent(checkpoint=missing)

    class OneColumnGame:
        def legal_actions(self) -> list[int]:
            return [5]

        def to_array(self) -> np.ndarray:
            return np.zeros((2, 6, 7), dtype=np.float32)

    with pytest.raises(FileNotFoundError, match="Khong tim thay checkpoint"):
        agent.choose(OneColumnGame())  # type: ignore[arg-type]


def test_dqn_net_outputs_seven_action_values() -> None:
    torch = pytest.importorskip("torch")
    from connect_four.agents.networks import DQNNet

    model = DQNNet()
    with torch.no_grad():
        output = model(torch.zeros((2, 2, 6, 7), dtype=torch.float32))
    assert tuple(output.shape) == (2, 7)
