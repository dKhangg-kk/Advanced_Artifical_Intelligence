#!/usr/bin/env python3
"""Chay ablation A3: anh huong kich thuoc du lieu huan luyen CNN (RQ2).

Script doc ``configs/ablation_a3_cnn_data.yaml``, huan luyen lai CNN tren cac
tap con van cua cohort ``a3`` (250, 500, 1000, ... den toi da so van train
thuc co), giu nguyen validation/test, roi do top-1 va do chinh xac theo tinh
huong ``win_now`` / ``block`` / ``center_control``.

Chay tu ``Connect_Four/``:

    PYTHONPATH=src python scripts/run_ablation_a3.py \
        --config configs/ablation_a3_cnn_data.yaml
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import sys
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
_TABLE_FIELDS = (
    "run_id",
    "ablation_run_id",
    "games",
    "train_games",
    "train_examples",
    "val_games",
    "val_examples",
    "test_examples",
    "best_epoch",
    "best_val_loss",
    "test_loss",
    "top1_accuracy",
    "legal_action_rate",
    "win_now_n",
    "win_now_top1_accuracy",
    "win_now_situation_accuracy",
    "block_n",
    "block_top1_accuracy",
    "block_situation_accuracy",
    "center_control_n",
    "center_control_top1_accuracy",
    "center_control_situation_accuracy",
    "other_n",
    "other_top1_accuracy",
    "other_situation_accuracy",
    "duration_seconds",
    "training_log",
    "test_evaluation",
    "checkpoint",
)
_ABLATION_METRICS = (
    "train_games",
    "train_examples",
    "val_examples",
    "test_examples",
    "best_epoch",
    "best_val_loss",
    "test_loss",
    "top1_accuracy",
    "legal_action_rate",
    "win_now_n",
    "win_now_top1_accuracy",
    "win_now_situation_accuracy",
    "block_n",
    "block_top1_accuracy",
    "block_situation_accuracy",
    "center_control_n",
    "center_control_top1_accuracy",
    "center_control_situation_accuracy",
    "other_n",
    "other_top1_accuracy",
    "other_situation_accuracy",
)
_TEST_METRICS = {
    "test_examples",
    "test_loss",
    "top1_accuracy",
    "legal_action_rate",
    "win_now_n",
    "win_now_top1_accuracy",
    "win_now_situation_accuracy",
    "block_n",
    "block_top1_accuracy",
    "block_situation_accuracy",
    "center_control_n",
    "center_control_top1_accuracy",
    "center_control_situation_accuracy",
    "other_n",
    "other_top1_accuracy",
    "other_situation_accuracy",
}


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError as err:
        raise SystemExit(
            "Can cai PyYAML de doc config: pip install -e '.[analysis]'"
        ) from err
    with path.open(encoding="utf-8") as file:
        config = yaml.safe_load(file)
    if not isinstance(config, dict):
        raise SystemExit(f"Config khong hop le: {path}")
    return config


def _positive_int(config: dict[str, Any], key: str) -> int:
    value = config.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise SystemExit(f"{key} phai la so nguyen duong trong config.")
    return value


def _non_negative_int(config: dict[str, Any], key: str) -> int:
    value = config.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise SystemExit(f"{key} phai la so nguyen khong am trong config.")
    return value


def _positive_float(config: dict[str, Any], key: str) -> float:
    value = config.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise SystemExit(f"{key} phai la so duong trong config.")
    return float(value)


def _dataset_sizes(config: dict[str, Any]) -> list[int]:
    sizes = config.get("dataset_sizes_games")
    if not isinstance(sizes, list) or not sizes:
        raise SystemExit("dataset_sizes_games phai la danh sach khong rong.")
    if any(isinstance(size, bool) or not isinstance(size, int) or size <= 0 for size in sizes):
        raise SystemExit("Moi phan tu dataset_sizes_games phai la so nguyen duong.")
    if sizes != sorted(set(sizes)):
        raise SystemExit("dataset_sizes_games phai tang dan va khong trung lap.")
    return sizes


def _relative(path: Path) -> str:
    try:
        return str(path.relative_to(_REPO_ROOT))
    except ValueError:
        return str(path)


def _plot_results(rows: list[dict[str, Any]], output: Path) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as err:
        raise SystemExit(
            "Can cai matplotlib de ve hinh: pip install -e '.[analysis]'"
        ) from err

    sizes = [int(row["games"]) for row in rows]
    figure, axis = plt.subplots(figsize=(8.0, 5.0))
    axis.plot(
        sizes,
        [float(row["top1_accuracy"]) for row in rows],
        marker="o",
        linewidth=2,
        label="Top-1 tong the (khop nhan Alpha-Beta)",
    )
    for key, label, marker in (
        ("win_now", "Thang ngay", "s"),
        ("block", "Chan thang ngay", "^"),
        ("center_control", "Kiem soat trung tam", "D"),
    ):
        axis.plot(
            sizes,
            [float(row[f"{key}_situation_accuracy"]) for row in rows],
            marker=marker,
            linewidth=1.6,
            label=label,
        )
    axis.set_xlabel("So van huan luyen (cohort A3)")
    axis.set_ylabel("Do chinh xac")
    axis.set_ylim(0.0, 1.0)
    axis.grid(alpha=0.3)
    axis.legend()
    figure.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=160)
    plt.close(figure)


def _append_training_manifest(
    metadata: dict[str, Any],
    *,
    config_path: Path,
    command: str,
    size: int,
    checkpoint: Path,
) -> None:
    from connect_four.evaluation.runlog import append_manifest, make_manifest_row

    started_at = metadata["started_at"]
    started = datetime.fromisoformat(started_at)
    finished = started + timedelta(seconds=float(metadata["duration_seconds"]))
    row = make_manifest_row(
        metadata["run_id"],
        config_file=config_path,
        command=command,
        seed=metadata["seed"],
        status="completed",
        notes=(
            f"A3 dataset_games={size}; cohort={metadata['data']['cohort']}; "
            f"train_games={metadata['data']['train_games']}; "
            f"checkpoint={_relative(checkpoint)}"
        ),
        started_at=started_at,
        finished_at=finished.isoformat(),
        cwd=_REPO_ROOT,
    )
    append_manifest(_REPO_ROOT / "results" / "logs" / "run_manifest.csv", row)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default="configs/ablation_a3_cnn_data.yaml",
        help="Duong dan config YAML (tu Connect_Four/).",
    )
    args = parser.parse_args(argv)

    os.chdir(_REPO_ROOT)
    config_path = Path(args.config)
    config = _load_yaml(config_path)
    sizes = _dataset_sizes(config)
    cohort = config.get("cohort", "a3")
    if cohort != "a3":
        raise SystemExit("Ablation A3 phai dung cohort='a3'.")

    data_dir = Path(config.get("data_dir", "data/generated/splits"))
    out_dir = Path(config.get("out_dir", "checkpoints"))
    log_dir = Path(config.get("log_dir", "results/logs"))
    table_path = Path(
        config.get("table_output", config.get("output", "results/tables/ablation_a3_results.csv"))
    )
    figure_path = Path(
        config.get("figure_output", "results/figures/ablation_a3_accuracy.png")
    )
    epochs = _positive_int(config, "epochs")
    batch_size = _positive_int(config, "batch_size")
    lr = _positive_float(config, "lr")
    seed = _non_negative_int(config, "seed")

    from connect_four.evaluation.runlog import (
        ABLATION_FIELDS,
        append_manifest,
        make_manifest_row,
        new_run_id,
        utc_now,
        write_csv,
    )
    from connect_four.training.train_supervised import (
        count_cohort_games,
        evaluate_checkpoint,
        train_supervised,
    )

    available_train_games = count_cohort_games(data_dir, "train", cohort=cohort)
    if sizes[-1] > available_train_games:
        raise SystemExit(
            f"dataset_sizes_games={sizes[-1]} vuot qua so van train A3 thuc co "
            f"({available_train_games}). Sua config cho khop du lieu."
        )
    if sizes[-1] != available_train_games:
        print(
            f"CANH BAO: muc lon nhat {sizes[-1]} chua dung toi da "
            f"{available_train_games} van train A3 thuc co.",
            file=sys.stderr,
        )

    ablation_run_id = new_run_id("ablation-a3", seed=seed)
    command = " ".join([sys.executable, *sys.argv])
    started_at = utc_now()
    rows: list[dict[str, Any]] = []
    ablation_rows: list[dict[str, Any]] = []

    print(
        f"A3 run {ablation_run_id}: {len(sizes)} muc, "
        f"toi da {available_train_games} van train, seed={seed}"
    )
    for size in sizes:
        print(f"- Huan luyen {size} van ...", flush=True)
        checkpoint = train_supervised(
            data_dir,
            out_dir=out_dir,
            epochs=epochs,
            batch_size=batch_size,
            lr=lr,
            seed=seed,
            cohort=cohort,
            game_limit=size,
            checkpoint_stem=f"a3_g{size}",
            log_dir=log_dir,
        )
        metadata = json.loads(checkpoint.with_suffix(".json").read_text(encoding="utf-8"))
        metrics = evaluate_checkpoint(checkpoint, data_dir)
        training_run_id = metadata["run_id"]
        training_log = Path(metadata["training_log"])
        test_evaluation = checkpoint.parent / f"test_evaluation_{training_run_id}.json"

        row = {
            "run_id": training_run_id,
            "ablation_run_id": ablation_run_id,
            "games": size,
            "train_games": metadata["data"]["train_games"],
            "train_examples": metadata["data"]["train_examples"],
            "val_games": metadata["data"]["val_games"],
            "val_examples": metadata["data"]["val_examples"],
            "best_epoch": metadata["selection"]["best_epoch"],
            "best_val_loss": metadata["selection"]["best_val_loss"],
            "duration_seconds": metadata["duration_seconds"],
            "training_log": _relative(training_log),
            "test_evaluation": _relative(test_evaluation),
            "checkpoint": _relative(checkpoint),
            **metrics,
        }
        rows.append(row)

        for metric in _ABLATION_METRICS:
            raw_path = test_evaluation if metric in _TEST_METRICS else training_log
            ablation_rows.append(
                {
                    "run_id": ablation_run_id,
                    "experiment": "a3_cnn_data",
                    "config_id": f"a3_g{size}",
                    "seed": seed,
                    "param_name": "dataset_games",
                    "param_value": size,
                    "metric": metric,
                    "value": row[metric],
                    "raw_log_path": _relative(raw_path),
                }
            )

        _append_training_manifest(
            metadata,
            config_path=config_path,
            command=command,
            size=size,
            checkpoint=checkpoint,
        )
        print(
            f"  run={training_run_id} top1={metrics['top1_accuracy']:.4f} "
            f"win={metrics['win_now_situation_accuracy']:.4f} "
            f"block={metrics['block_situation_accuracy']:.4f} "
            f"center={metrics['center_control_situation_accuracy']:.4f}",
            flush=True,
        )

    write_csv(table_path, _TABLE_FIELDS, rows)
    write_csv(
        log_dir / f"ablation_a3_{ablation_run_id}.csv",
        ABLATION_FIELDS,
        ablation_rows,
    )
    _plot_results(rows, figure_path)

    append_manifest(
        log_dir / "run_manifest.csv",
        make_manifest_row(
            ablation_run_id,
            config_file=config_path,
            command=command,
            seed=seed,
            status="completed",
            notes=(
                f"Issue #22; A3 cohort={cohort}; sizes={sizes}; "
                f"max_train_games={available_train_games}; table={_relative(table_path)}; "
                f"figure={_relative(figure_path)}"
            ),
            started_at=started_at,
            finished_at=utc_now(),
            cwd=_REPO_ROOT,
        ),
    )
    print(f"Bang: {table_path}")
    print(f"Hinh: {figure_path}")
    print(f"Log ablation: {log_dir / f'ablation_a3_{ablation_run_id}.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
