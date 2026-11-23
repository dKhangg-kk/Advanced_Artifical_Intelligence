from threading import Event

import pytest

from connect_four.game.constants import PLAYER_1, PLAYER_2
from connect_four.ui.gui import GameController


@pytest.mark.parametrize(
    ("name", "checkpoint_dir"), [("dqn", "level6_dqn"), ("nn", "level5_cnn")]
)
def test_demo_uses_trained_checkpoint_from_any_working_directory(
    name, checkpoint_dir, monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    controller = GameController({PLAYER_1: "human", PLAYER_2: name})

    assert not controller.blocked, controller.error
    checkpoint = controller.agents[PLAYER_2].checkpoint
    assert checkpoint.parent.name == checkpoint_dir
    assert checkpoint.name == "final.pt"
    assert checkpoint.is_file()


def test_late_result_from_old_game_does_not_overwrite_new_move():
    release_old_game = Event()

    class TestAgent:
        def __init__(self, column, ready):
            self.column = column
            self.ready = ready

        def reset(self):
            pass

        def choose(self, game):
            assert self.ready.wait(timeout=5)
            return self.column

    new_game_ready = Event()
    new_game_ready.set()
    agents = iter((TestAgent(0, release_old_game), TestAgent(3, new_game_ready)))
    controller = GameController(
        {PLAYER_1: "random", PLAYER_2: "human"},
        agent_factory=lambda name, seed: next(agents),
    )

    controller.update()
    old_thread = controller._thread
    try:
        controller.new_game()
        controller.update()
        new_thread = controller._thread
        new_thread.join(timeout=5)
        assert not new_thread.is_alive()
    finally:
        release_old_game.set()
        old_thread.join(timeout=5)

    assert not old_thread.is_alive()
    controller.update(allow_start=False)
    assert controller.game.moves_played() == (3,)
