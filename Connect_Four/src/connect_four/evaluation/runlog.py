"""Sinh ``run_id`` và ghi log thực nghiệm theo quy ước trong ``docs/LOGGING.md``.

Module này chỉ dùng thư viện chuẩn. Các thư viện nặng (numpy, torch, psutil)
được import bên trong hàm để CI nhẹ vẫn chạy được.
"""

from __future__ import annotations

import csv
import hashlib
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

RUN_MANIFEST_FIELDS: tuple[str, ...] = (
    "run_id",
    "started_at",
    "finished_at",
    "git_commit",
    "config_file",
    "config_hash",
    "command",
    "seed",
    "python_version",
    "numpy_version",
    "torch_version",
    "cpu",
    "gpu",
    "ram_gb",
    "os",
    "status",
    "notes",
)

GAME_FIELDS: tuple[str, ...] = (
    "run_id",
    "game_id",
    "pair",
    "agent_a",
    "agent_b",
    "a_starts",
    "opening_id",
    "moves",
    "winner",
    "n_moves",
    "mean_ms_a",
    "p95_ms_a",
    "mean_ms_b",
    "p95_ms_b",
    "nodes_a",
    "nodes_b",
    "simulations_a",
    "simulations_b",
    "over_budget_a",
    "over_budget_b",
)

MOVE_FIELDS: tuple[str, ...] = (
    "run_id",
    "game_id",
    "ply",
    "player",
    "agent",
    "action",
    "legal_actions",
    "time_ms",
    "nodes",
    "simulations",
    "depth_reached",
    "eval_score",
    "is_terminal",
)

TRAIN_CNN_FIELDS: tuple[str, ...] = (
    "run_id",
    "epoch",
    "split",
    "loss",
    "val_loss",
    "accuracy",
    "top3_accuracy",
    "lr",
    "time_s",
)

TRAIN_DQN_FIELDS: tuple[str, ...] = (
    "run_id",
    "episode",
    "reward",
    "avg_reward",
    "epsilon",
    "loss",
    "buffer_size",
    "eval_win_rate",
    "train_time_s",
    "checkpoint_path",
)

ABLATION_FIELDS: tuple[str, ...] = (
    "run_id",
    "experiment",
    "config_id",
    "seed",
    "param_name",
    "param_value",
    "metric",
    "value",
    "raw_log_path",
)

REPORT_NUMBER_FIELDS: tuple[str, ...] = (
    "report_section",
    "metric",
    "value",
    "unit",
    "type",
    "source_type",
    "source_path",
    "source_filter",
    "formula",
    "run_id",
)


def new_run_id(prefix: str, seed: int | None = None) -> str:
    """Tạo ``run_id`` duy nhất theo UTC.

    Ví dụ: ``tournament-default-20261106T143000Z-s20261102``.
    """
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    suffix = f"-s{seed}" if seed is not None else ""
    return f"{prefix}-{stamp}{suffix}"


def utc_now() -> str:
    """Thời điểm hiện tại dạng ISO-8601 UTC."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def config_hash(path: str | Path) -> str:
    """SHA-256 của file cấu hình, dùng để phát hiện sửa tay."""
    p = Path(path)
    if not p.is_file():
        return ""
    digest = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]


def git_commit(cwd: str | Path | None = None) -> str:
    """Commit hash ngắn của repo hiện tại, hoặc chuỗi rỗng nếu không có Git."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=None if cwd is None else str(cwd),
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    return out.stdout.strip()


def environment_info() -> dict[str, str]:
    """Thu thập phiên bản phần mềm và phần cứng cơ bản cho manifest."""
    info: dict[str, str] = {
        "python_version": platform.python_version(),
        "numpy_version": "",
        "torch_version": "",
        "cpu": platform.processor() or platform.machine(),
        "gpu": "",
        "ram_gb": "",
        "os": f"{platform.system()} {platform.release()}",
    }

    try:
        import numpy as np

        info["numpy_version"] = np.__version__
    except ImportError:
        pass

    try:
        import torch

        info["torch_version"] = torch.__version__
        if torch.cuda.is_available():
            info["gpu"] = torch.cuda.get_device_name(0)
    except ImportError:
        pass

    try:
        import psutil

        info["ram_gb"] = f"{psutil.virtual_memory().total / (1024 ** 3):.1f}"
    except ImportError:
        pass

    return info


def make_manifest_row(
    run_id: str,
    *,
    config_file: str | Path | None = None,
    command: str = "",
    seed: int | None = None,
    status: str = "completed",
    notes: str = "",
    started_at: str | None = None,
    finished_at: str | None = None,
    cwd: str | Path | None = None,
) -> dict[str, Any]:
    """Tạo một dòng cho ``run_manifest.csv``."""
    row: dict[str, Any] = {
        "run_id": run_id,
        "started_at": started_at or utc_now(),
        "finished_at": finished_at or "",
        "git_commit": git_commit(cwd),
        "config_file": "" if config_file is None else str(config_file),
        "config_hash": "" if config_file is None else config_hash(config_file),
        "command": command,
        "seed": "" if seed is None else seed,
        "status": status,
        "notes": notes,
    }
    row.update(environment_info())
    return row


def _csv_value(value: Any) -> Any:
    """Chuẩn hoá giá trị trước khi ghi CSV."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, (list, tuple)):
        return " ".join(str(item) for item in value)
    return value


def write_csv(
    path: str | Path,
    fieldnames: Sequence[str],
    rows: Iterable[Mapping[str, Any]],
) -> Path:
    """Ghi mới một file CSV với header cố định."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(fieldnames), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _csv_value(value) for key, value in row.items()})
    return p


def append_csv(
    path: str | Path,
    fieldnames: Sequence[str],
    rows: Iterable[Mapping[str, Any]],
) -> Path:
    """Ghi thêm vào CSV; tự tạo header nếu file chưa có."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    has_content = p.is_file() and p.stat().st_size > 0
    with p.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(fieldnames), extrasaction="ignore")
        if not has_content:
            writer.writeheader()
        for row in rows:
            writer.writerow({key: _csv_value(value) for key, value in row.items()})
    return p


def append_manifest(path: str | Path, row: Mapping[str, Any]) -> Path:
    """Ghi thêm một dòng vào ``run_manifest.csv``."""
    return append_csv(path, RUN_MANIFEST_FIELDS, [row])


__all__ = [
    "ABLATION_FIELDS",
    "GAME_FIELDS",
    "MOVE_FIELDS",
    "REPORT_NUMBER_FIELDS",
    "RUN_MANIFEST_FIELDS",
    "TRAIN_CNN_FIELDS",
    "TRAIN_DQN_FIELDS",
    "append_csv",
    "append_manifest",
    "config_hash",
    "environment_info",
    "git_commit",
    "make_manifest_row",
    "new_run_id",
    "utc_now",
    "write_csv",
]
