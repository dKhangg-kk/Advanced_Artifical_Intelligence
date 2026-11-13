"""Kiem thu doc log huan luyen va ve duong cong hoc CNN."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from connect_four.evaluation.plots import best_epoch, read_training_log


def _write_log(path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["epoch", "train_loss", "val_loss", "train_accuracy", "val_accuracy", "best"])
        writer.writerow([1, 1.5, 1.4, 0.40, 0.45, "true"])
        writer.writerow([2, 1.2, 1.3, 0.50, 0.50, "true"])
        writer.writerow([3, 1.0, 1.5, 0.60, 0.52, "false"])


def test_read_training_log_parses_epoch(tmp_path: Path) -> None:
    log = tmp_path / "train.csv"
    _write_log(log)
    rows = read_training_log(log)
    assert [row["epoch"] for row in rows] == [1, 2, 3]
    assert rows[0]["train_loss"] == "1.5"


def test_read_training_log_rejects_missing_columns(tmp_path: Path) -> None:
    log = tmp_path / "train.csv"
    log.write_text("epoch,train_loss\n1,1.0\n", encoding="utf-8")
    with pytest.raises(ValueError, match="thieu cot"):
        read_training_log(log)


def test_best_epoch_uses_flag_then_val_loss(tmp_path: Path) -> None:
    log = tmp_path / "train.csv"
    _write_log(log)
    assert best_epoch(read_training_log(log)) == 2

    log_no_flag = tmp_path / "train_no_flag.csv"
    log_no_flag.write_text(
        "epoch,train_loss,val_loss,train_accuracy,val_accuracy\n"
        "1,1.5,1.4,0.40,0.45\n"
        "2,1.2,1.1,0.50,0.50\n",
        encoding="utf-8",
    )
    assert best_epoch(read_training_log(log_no_flag)) == 2


def test_plot_training_curve_writes_png(tmp_path: Path) -> None:
    pytest.importorskip("matplotlib")
    from connect_four.evaluation.plots import plot_training_curve

    log = tmp_path / "train.csv"
    _write_log(log)
    out = tmp_path / "figures" / "curve.png"
    result = plot_training_curve(log, out, title="Kiem thu")
    assert result == out
    assert out.is_file()
    assert out.stat().st_size > 0
