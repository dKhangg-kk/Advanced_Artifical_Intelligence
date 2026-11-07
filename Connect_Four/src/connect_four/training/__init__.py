"""Sinh du lieu, huan luyen mang policy (cap 5) va hoc tang cuong DQN (cap 6)."""

from connect_four.training.gen_data import generate_dataset
from connect_four.training.train_dqn import train_dqn
from connect_four.training.train_supervised import train_supervised

__all__ = ["generate_dataset", "train_dqn", "train_supervised"]
