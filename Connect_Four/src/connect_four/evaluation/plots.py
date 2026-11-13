"""Ve duong cong hoc tu log huan luyen CNN.

Module nay chi doc CSV va ve hinh; khong bat buoc matplotlib khi chi import.
Nho vay CI nhe (chi numpy + pytest) van import duoc package, con buoc ve hinh
can cai them extra ``analysis``.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


_TRAIN_LOG_COLUMNS = (
    "epoch",
    "train_loss",
    "val_loss",
    "train_accuracy",
    "val_accuracy",
)


def read_training_log(path: str | Path) -> list[dict[str, Any]]:
    """Doc log ``train_cnn_*.csv`` va tra ve danh sach ban ghi theo epoch.

    Moi ban ghi giu nguyen chuoi goc, rieng ``epoch`` duoc doi sang ``int``.
    Ham bao loi ro rang neu thieu cot bat buoc hoac file rong.
    """
    log_path = Path(path)
    with log_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = [name for name in _TRAIN_LOG_COLUMNS if name not in (reader.fieldnames or ())]
        if missing:
            raise ValueError(f"Log thieu cot: {', '.join(missing)}")
        rows = [dict(row) for row in reader]
    if not rows:
        raise ValueError(f"Log rong: {log_path}")
    for row in rows:
        row["epoch"] = int(row["epoch"])
    return rows


def best_epoch(rows: list[dict[str, Any]]) -> int:
    """Tra ve epoch co validation loss thap nhat.

    Cung quy tac voi buoc chon checkpoint khi huan luyen: uu tien cot ``best``
    neu co, neu khong thi tu tim theo ``val_loss``.
    """
    flagged = [row for row in rows if str(row.get("best", "")).lower() == "true"]
    if flagged:
        return int(flagged[-1]["epoch"])
    return int(min(rows, key=lambda row: float(row["val_loss"]))["epoch"])


def plot_training_curve(
    log_path: str | Path,
    out_path: str | Path,
    *,
    title: str | None = None,
) -> Path:
    """Ve hai panel loss/accuracy (train va validation) theo epoch.

    Tra ve duong dan anh da ghi. Ham import matplotlib ben trong de khong lam
    nang phan loi chi can numpy.
    """
    rows = read_training_log(log_path)
    marker_epoch = best_epoch(rows)

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as err:  # pragma: no cover - phu thuoc moi truong
        raise ImportError(
            "Can cai matplotlib de ve hinh: pip install -e '.[analysis]'"
        ) from err

    epochs = [row["epoch"] for row in rows]
    figure, axes = plt.subplots(1, 2, figsize=(12.0, 4.6))
    series = (
        ("loss", "train_loss", "val_loss", "Cross-entropy loss"),
        ("accuracy", "train_accuracy", "val_accuracy", "Top-1 accuracy"),
    )
    for axis, (_, train_key, val_key, ylabel) in zip(axes, series):
        axis.plot(epochs, [float(row[train_key]) for row in rows], marker="o",
                  linewidth=1.7, label="Train")
        axis.plot(epochs, [float(row[val_key]) for row in rows], marker="s",
                  linewidth=1.7, label="Validation")
        axis.axvline(marker_epoch, color="grey", linestyle="--", linewidth=1.0,
                     label=f"Checkpoint tot nhat (epoch {marker_epoch})")
        axis.set_xlabel("Epoch")
        axis.set_ylabel(ylabel)
        axis.grid(alpha=0.3)
        axis.legend(fontsize=8)

    figure.suptitle(title or "Duong cong hoc CNN")
    figure.tight_layout()
    destination = Path(out_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(destination, dpi=160)
    plt.close(figure)
    return destination
