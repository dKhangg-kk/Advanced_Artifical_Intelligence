from threading import Event

import pytest

from connect_four.game.constants import PLAYER_1, PLAYER_2
from connect_four.ui import gui
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


@pytest.mark.parametrize("seed, expected", [(None, (20, 40)), (0, (0, 0))])
def test_new_game_assigns_seeds_without_switching_sides(monkeypatch, seed, expected):
    random_seeds = iter((20, 40))
    monkeypatch.setattr(gui, "randbits", lambda bits: next(random_seeds))
    controller = GameController({PLAYER_1: "alphabeta", PLAYER_2: "mcts"}, seed=seed)
    for index, game_seed in enumerate(expected):
        if index:
            controller.new_game()
        assert controller.agents[PLAYER_1].name == "alphabeta"
        assert controller.agents[PLAYER_1].seed == game_seed
        assert controller.agents[PLAYER_2].name == "mcts"
        assert controller.agents[PLAYER_2].seed == game_seed + 1
        assert controller.game.current_player == PLAYER_1


@pytest.mark.parametrize("args, expected", [([], None), (["--seed", "0"], 0)])
def test_cli_seed_reaches_gui(monkeypatch, args, expected):
    seeds = []
    monkeypatch.setattr(gui, "run_gui", lambda *args, seed: seeds.append(seed))
    assert gui.main(args) == 0
    assert seeds == [expected]


@pytest.mark.parametrize("seed", ["-1", str(2**63)])
def test_cli_rejects_out_of_range_seed(seed):
    with pytest.raises(SystemExit) as error:
        gui.main(["--seed", seed])
    assert error.value.code == 2


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
