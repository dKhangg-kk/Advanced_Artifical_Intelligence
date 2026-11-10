"""Cap 4 - MCTS voi UCT.

Bon buoc: chon (UCT) -> mo rong -> mo phong (rollout) -> cap nhat.
Ngan sach: Budget.simulations hoac Budget.time_s.

Xong khi: thang Random >= 95% o 500 mo phong. Khao sat ngan sach
100 / 500 / 1000 / 2000 / 5000 mo phong de lam ablation A2.
"""

from __future__ import annotations

import random
from math import isfinite, log, sqrt
from time import perf_counter

from connect_four.agents.base import Agent, Budget, SearchStats
from connect_four.game.base import ConnectFourGame


class MCTSNode:
    """Mot nut trong cay tim kiem (N = so lan tham, W = tong phan thuong)."""

    __slots__ = ("parent", "action", "children", "visits", "wins", "untried")

    def __init__(self, parent: "MCTSNode | None" = None, action: int | None = None) -> None:
        self.parent = parent
        self.action = action
        self.children: dict[int, "MCTSNode"] = {}
        self.visits = 0
        self.wins = 0.0
        self.untried: list[int] = []


class MCTSAgent(Agent):
    """Monte Carlo Tree Search, chon nuoc bang UCT."""

    name = "mcts"
    level = 4

    def __init__(self, simulations: int = 1000, c: float = 1.414,
                 seed: int | None = None, *, budget: Budget | None = None) -> None:
        super().__init__(budget=budget or Budget(simulations=simulations), seed=seed)
        if self.budget.depth is not None or (
            self.budget.simulations is None and self.budget.time_s is None
        ):
            raise ValueError("MCTS chi nhan Budget(simulations) hoac Budget(time_s).")
        if self.budget.simulations is not None and (
            type(self.budget.simulations) is not int or self.budget.simulations < 0
        ):
            raise ValueError("So mo phong phai la so nguyen >= 0.")
        if self.budget.time_s is not None and (
            not isfinite(self.budget.time_s) or self.budget.time_s < 0
        ):
            raise ValueError("Thoi gian phai huu han va >= 0.")
        if not isfinite(c) or c < 0:
            raise ValueError("He so UCT phai huu han va >= 0.")
        self.c = c
        self._rng = random.Random(seed)

    def choose(self, game: ConnectFourGame) -> int:
        """Chay UCT, tra con tham nhieu nhat; het nuoc nem ValueError.

        Ngan sach 0 tra nuoc ngau nhien hop le. Chi dem mo phong da ket thuc;
        han gio kiem tra giua cac thao tac, khong phai gioi han thoi gian cung.
        """
        start = perf_counter()
        self.last_stats = SearchStats()
        legal = game.legal_actions()
        if not legal:
            raise ValueError("Khong con nuoc di hop le.")
        root = MCTSNode()
        root.untried = legal[:]
        self.last_stats.nodes = 1
        root_player = game.current_player
        deadline = start + self.budget.time_s if self.budget.time_s is not None else None

        def check_time() -> None:
            if deadline is not None and perf_counter() >= deadline:
                raise TimeoutError

        try:
            while (self.budget.simulations is None
                   or root.visits < self.budget.simulations):
                check_time()
                state = game.clone()
                node = root
                depth = 0
                # Selection: moi con luu diem cua nguoi vua di vao con do.
                while not node.untried and node.children:
                    check_time()
                    node = max(node.children.values(), key=lambda child: (
                        child.wins / child.visits
                        + self.c * sqrt(log(node.visits) / child.visits)
                    ))
                    state.step(node.action)
                    depth += 1
                # Expansion: them toi da mot con moi trong moi mo phong.
                if node.untried:
                    check_time()
                    action = self._rng.choice(node.untried)
                    node.untried.remove(action)
                    state.step(action)
                    child = MCTSNode(node, action)
                    child.untried = state.legal_actions()
                    node.children[action] = child
                    node = child
                    depth += 1
                    self.last_stats.nodes += 1
                tree_depth = depth
                # Simulation: rollout ngau nhien den trang thai ket thuc.
                while not state.is_terminal():
                    check_time()
                    state.step(self._rng.choice(state.legal_actions()))
                check_time()
                reward = state.result(root_player)
                # Backpropagation: doi goc nhin sau moi tang, ke ca luot doi thu.
                while node is not None:
                    node.visits += 1
                    node.wins += reward if depth % 2 else -reward
                    node = node.parent
                    depth -= 1
                self.last_stats.simulations = root.visits
                self.last_stats.depth_reached = max(self.last_stats.depth_reached, tree_depth)
        except TimeoutError:
            pass
        finally:
            self.last_stats.time_ms = (perf_counter() - start) * 1000
        visited = [child for child in root.children.values() if child.visits]
        if not visited:
            return self._rng.choice(legal)
        most_visits = max(child.visits for child in visited)
        best = self._rng.choice([child for child in visited if child.visits == most_visits])
        self.last_stats.extra["eval_score"] = best.wins / best.visits
        return best.action
