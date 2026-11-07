"""Cap 5 - Huan luyen co giam sat (policy network).

LUU Y: `import torch` phai nam BEN TRONG ham/class, khong o cap module,
de `pytest` van chay tren may chua cai torch.
"""

from __future__ import annotations

from pathlib import Path


def train_supervised(
    data_dir: str | Path,
    out_dir: str | Path = "checkpoints",
    epochs: int = 20,
    batch_size: int = 256,
    lr: float = 1e-3,
    seed: int = 0,
) -> Path:
    """Huan luyen mang policy, chon checkpoint bang validation.

    Returns:
        Duong dan checkpoint tot nhat (vi du checkpoints/nn_policy.pt).
    """
    raise NotImplementedError("TODO: vong lap huan luyen + chon checkpoint theo val loss")


def evaluate_checkpoint(checkpoint: str | Path, data_dir: str | Path) -> dict[str, float]:
    """Danh gia tren tap test: loss, top-1 accuracy, va ty le nuoc hop le."""
    raise NotImplementedError("TODO: danh gia tren tap test (chi dung mot lan)")
