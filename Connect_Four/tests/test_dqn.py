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


def test_train_dqn_runs_two_episodes_logs_and_saves_loadable_checkpoint(tmp_path) -> None:
    pytest.importorskip("torch")
    import csv

    from connect_four.game import ConnectFour
    from connect_four.training.train_dqn import train_dqn

    checkpoint = train_dqn(
        episodes=2,
        opponent="heuristic",
        lr=1e-3,
        gamma=0.99,
        epsilon_start=1.0,
        epsilon_min=0.05,
        epsilon_decay=0.9995,
        buffer_size=256,
        batch_size=4,
        target_update_freq=5,
        checkpoint_milestones=(),
        out_dir=tmp_path / "checkpoints",
        log_dir=tmp_path / "logs",
        seed=23,
        device="cpu",
        run_id="unit_test_dqn",
    )

    assert checkpoint.is_file()
    assert checkpoint.with_suffix(".json").is_file()
    log_file = tmp_path / "logs" / "train_dqn_unit_test_dqn.csv"
    assert log_file.is_file()
    with log_file.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))

    assert len(rows) == 2
    assert [int(row["agent_player"]) for row in rows] == [1, 2]
    assert all(row["opponent"] == "heuristic" for row in rows)
    assert all(row["result"] in {"win", "draw", "loss"} for row in rows)
    assert all(float(row["reward"]) in {-1.0, 0.0, 1.0} for row in rows)
    assert any(int(row["optimizer_updates"]) > 0 for row in rows)

    agent = DQNAgent(checkpoint=checkpoint, epsilon=0.0, seed=9)
    game = ConnectFour()
    before = tuple(game.moves_played())
    assert agent.choose(game) in game.legal_actions()
    assert tuple(game.moves_played()) == before
    assert agent.last_stats.time_ms >= 0.0


def test_train_dqn_rejects_invalid_training_settings() -> None:
    from connect_four.training.train_dqn import train_dqn

    with pytest.raises(ValueError, match="episodes"):
        train_dqn(episodes=0)
    with pytest.raises(ValueError, match="opponent"):
        train_dqn(episodes=1, opponent="alphabeta")
    with pytest.raises(ValueError, match="batch_size"):
        train_dqn(episodes=1, buffer_size=4, batch_size=8)


def test_train_dqn_opening_plies_default_keeps_old_behaviour_and_validates(tmp_path) -> None:
    pytest.importorskip("torch")
    import csv
    import json

    from connect_four.training.train_dqn import train_dqn

    def run(out: str, **extra: object) -> tuple[list[dict[str, str]], dict[str, object]]:
        checkpoint = train_dqn(
            episodes=4, opponent="random", buffer_size=64, batch_size=4, target_update_freq=5,
            checkpoint_milestones=(), out_dir=tmp_path / out, log_dir=tmp_path / out,
            seed=11, device="cpu", run_id="unit_open", **extra,
        )
        with (tmp_path / out / "train_dqn_unit_open.csv").open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        return rows, json.loads(checkpoint.with_suffix(".json").read_text(encoding="utf-8"))

    rows_default, meta_default = run("default")
    rows_zero, meta_zero = run("zero", opening_plies=0)
    # opening_plies=0 khong goi them so ngau nhien va khong them khoa vao metadata
    assert [r["reward"] for r in rows_default] == [r["reward"] for r in rows_zero]
    assert [r["moves"] for r in rows_default] == [r["moves"] for r in rows_zero]
    assert "opening_plies" not in meta_default["config"] and "opening_plies" not in meta_zero["config"]

    rows_open, meta_open = run("open", opening_plies=4)
    assert meta_open["config"]["opening_plies"] == 4
    # 4 nuoc dat truoc + it nhat mot nuoc nua nen moi van dai tu 5 nuoc tro len
    assert all(int(r["moves"]) >= 5 for r in rows_open)
    # DQN chi tinh cac nuoc cua chinh no, khong tinh 4 nuoc khai cuoc
    assert all(int(r["dqn_moves"]) < int(r["moves"]) - 3 for r in rows_open)

    with pytest.raises(ValueError, match="opening_plies"):
        train_dqn(episodes=1, opening_plies=11)
    with pytest.raises(ValueError, match="opening_plies"):
        train_dqn(episodes=1, opening_plies=-1)


def test_selfplay_pool_snapshots_are_frozen_copies_and_capped() -> None:
    torch = pytest.importorskip("torch")
    import numpy as np

    from connect_four.agents.networks import DQNNet
    from connect_four.game import ConnectFour
    from connect_four.training.train_dqn import SelfPlayOpponentPool

    net = DQNNet(in_channels=2)
    pool = SelfPlayOpponentPool(lambda: DQNNet(in_channels=2), torch, torch.device("cpu"),
                                np.random.default_rng(0), snapshot_every=3, pool_size=2)
    pool.add_snapshot(net, 0)
    assert [ep for ep, _ in pool.snapshots] == [0]
    assert not pool.maybe_snapshot(net, 2)
    assert pool.maybe_snapshot(net, 3) and pool.maybe_snapshot(net, 6)
    # chi giu pool_size ban gan nhat
    assert [ep for ep, _ in pool.snapshots] == [3, 6]

    # ban sao khong doi khi mang dang hoc doi trong so, va khong nhan gradient
    _, snapshot = pool.snapshots[-1]
    before = [p.detach().clone() for p in snapshot.parameters()]
    with torch.no_grad():
        for parameter in net.parameters():
            parameter.add_(1.0)
    assert all(torch.equal(a, b) for a, b in zip(before, snapshot.parameters()))
    assert not any(p.requires_grad for p in snapshot.parameters())

    # doi thu greedy luon chon cot hop le va khong sua game
    game = ConnectFour()
    for column in [3, 3, 3, 3, 3, 3]:
        game.step(column)
    opponent = pool.sample(epsilon=0.0)
    before_moves = tuple(game.moves_played())
    assert opponent.choose(game) in game.legal_actions()
    assert tuple(game.moves_played()) == before_moves
    assert opponent.snapshot_episode in {3, 6}


def test_train_dqn_selfplay_logs_snapshot_and_saves_config(tmp_path) -> None:
    pytest.importorskip("torch")
    import csv
    import json

    from connect_four.agents.dqn import DQNAgent
    from connect_four.game import ConnectFour
    from connect_four.training.train_dqn import train_dqn

    checkpoint = train_dqn(
        episodes=6, opponent="selfplay", buffer_size=128, batch_size=4, target_update_freq=5,
        checkpoint_milestones=(6,), out_dir=tmp_path, log_dir=tmp_path, seed=5, device="cpu",
        run_id="unit_selfplay", selfplay_snapshot_every=2, selfplay_pool_size=2,
    )
    with (tmp_path / "train_dqn_unit_selfplay.csv").open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 6
    assert all(row["opponent"] == "selfplay" for row in rows)
    assert [int(row["agent_player"]) for row in rows] == [1, 2, 1, 2, 1, 2]
    # episode 1-2 chi co ban khoi tao (0); ban moi duoc chep sau episode 2 va 4
    assert {int(r["opponent_snapshot_episode"]) for r in rows[:2]} == {0}
    assert all(int(r["opponent_snapshot_episode"]) in {0, 2, 4} for r in rows)
    assert all(int(r["opponent_snapshot_episode"]) < int(r["episode"]) for r in rows)
    assert any(int(row["optimizer_updates"]) > 0 for row in rows)

    meta = json.loads(checkpoint.with_suffix(".json").read_text(encoding="utf-8"))
    assert meta["config"]["opponent"] == "selfplay"
    assert meta["config"]["selfplay_snapshot_every"] == 2
    assert meta["config"]["selfplay_pool_size"] == 2
    agent = DQNAgent(checkpoint=checkpoint, epsilon=0.0, seed=1)
    assert agent.choose(ConnectFour()) in range(7)

    with pytest.raises(ValueError, match="selfplay_snapshot_every"):
        train_dqn(episodes=1, opponent="selfplay", selfplay_snapshot_every=0, out_dir=tmp_path / "x",
                  log_dir=tmp_path / "x", device="cpu", run_id="bad")


def test_fixed_opponent_runs_do_not_log_selfplay_fields(tmp_path) -> None:
    pytest.importorskip("torch")
    import csv
    import json

    from connect_four.training.train_dqn import train_dqn

    checkpoint = train_dqn(
        episodes=2, opponent="random", buffer_size=64, batch_size=4, checkpoint_milestones=(),
        out_dir=tmp_path, log_dir=tmp_path, seed=3, device="cpu", run_id="unit_fixed",
    )
    with (tmp_path / "train_dqn_unit_fixed.csv").open(newline="", encoding="utf-8") as stream:
        header = next(csv.reader(stream))
    assert "opponent_snapshot_episode" not in header
    meta = json.loads(checkpoint.with_suffix(".json").read_text(encoding="utf-8"))
    assert "selfplay_snapshot_every" not in meta["config"]


def test_train_dqn_resume_after_crash_matches_uninterrupted_run(tmp_path, monkeypatch) -> None:
    torch = pytest.importorskip("torch")
    import csv

    import importlib

    module = importlib.import_module("connect_four.training.train_dqn")

    common = dict(episodes=6, opponent="selfplay", buffer_size=128, batch_size=4, target_update_freq=3,
                  checkpoint_milestones=(3, 6), seed=21, device="cpu", run_id="unit_resume",
                  selfplay_snapshot_every=2, selfplay_pool_size=2)

    def rows(folder):
        with (folder / "train_dqn_unit_resume.csv").open(newline="", encoding="utf-8") as stream:
            return [{k: v for k, v in r.items() if k != "elapsed_seconds"} for r in csv.DictReader(stream)]

    straight = tmp_path / "straight"
    module.train_dqn(out_dir=straight, log_dir=straight, **common)

    crashed = tmp_path / "crashed"
    original_sample = module.SelfPlayOpponentPool.sample
    calls = {"n": 0}

    def crash_on_fifth(self, epsilon):
        calls["n"] += 1
        if calls["n"] == 5:
            raise RuntimeError("may sap gia lap")
        return original_sample(self, epsilon)

    monkeypatch.setattr(module.SelfPlayOpponentPool, "sample", crash_on_fifth)
    with pytest.raises(RuntimeError, match="may sap"):
        module.train_dqn(out_dir=crashed, log_dir=crashed, resume_every=2, **common)
    assert (crashed / "resume_state.pt").is_file()
    monkeypatch.setattr(module.SelfPlayOpponentPool, "sample", original_sample)
    module.train_dqn(out_dir=crashed, log_dir=crashed, resume_every=2, **common)

    assert not (crashed / "resume_state.pt").exists()
    assert rows(straight) == rows(crashed)
    a = torch.load(straight / "dqn_model.pt", weights_only=False)["model_state_dict"]
    b = torch.load(crashed / "dqn_model.pt", weights_only=False)["model_state_dict"]
    assert all(torch.equal(a[k], b[k]) for k in a)

    with pytest.raises(ValueError, match="resume_every"):
        module.train_dqn(episodes=1, resume_every=-1)
