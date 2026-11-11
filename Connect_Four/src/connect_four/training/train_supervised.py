"""Supervised CNN policy training and one-time held-out test evaluation."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import json
import math
import platform
from pathlib import Path
import random
import subprocess
import time
from typing import Any
import uuid

import numpy as np

from connect_four.game.constants import COLS, ROWS


_REPO_ROOT = Path(__file__).resolve().parents[4]
_DATA_COHORTS = {"main_model", "a3"}


def _require_torch() -> Any:
    try:
        import torch
    except ImportError as err:
        raise ImportError(
            "Can cai PyTorch de huan luyen CNN: pip install '.[torch]' hoac pip install torch."
        ) from err
    return torch


def _load_split(
    data_dir: Path,
    split: str,
    cohort: str | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    if cohort is not None and (not isinstance(cohort, str) or cohort not in _DATA_COHORTS):
        raise ValueError(f"cohort phai la mot trong {sorted(_DATA_COHORTS)}.")
    path = data_dir / f"{split}.jsonl"
    states: list[np.ndarray] = []
    actions: list[int] = []

    with path.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as err:
                raise ValueError(f"{path}:{line_number}: JSON khong hop le.") from err
            if not isinstance(row, dict) or "state" not in row or "action" not in row:
                raise ValueError(f"{path}:{line_number}: can co truong state va action.")
            if cohort is not None:
                row_cohort = row.get("planned_use")
                if not isinstance(row_cohort, str) or row_cohort not in _DATA_COHORTS:
                    raise ValueError(f"{path}:{line_number}: planned_use khong hop le.")
                if row_cohort != cohort:
                    continue

            state = np.asarray(row["state"], dtype=np.float32)
            if state.shape != (2, ROWS, COLS):
                raise ValueError(
                    f"{path}:{line_number}: state phai co shape (2, {ROWS}, {COLS}), "
                    f"nhan duoc {state.shape}."
                )
            if not np.isfinite(state).all() or not np.isin(state, (0.0, 1.0)).all():
                raise ValueError(f"{path}:{line_number}: state phai gom cac gia tri 0/1 huu han.")

            action = row["action"]
            if isinstance(action, bool) or not isinstance(action, int) or not 0 <= action < COLS:
                raise ValueError(
                    f"{path}:{line_number}: action phai la so nguyen trong 0..{COLS - 1}."
                )
            if state[:, :, action].sum() >= ROWS:
                raise ValueError(f"{path}:{line_number}: nhan action nam trong cot da day.")

            states.append(state)
            actions.append(action)

    if not states:
        raise ValueError(f"Tep split {path} khong co mau.")
    return np.stack(states), np.asarray(actions, dtype=np.int64)


def _make_loader(
    torch: Any,
    states: np.ndarray,
    actions: np.ndarray,
    batch_size: int,
    *,
    shuffle: bool,
    seed: int,
):
    dataset = torch.utils.data.TensorDataset(
        torch.from_numpy(states),
        torch.from_numpy(actions),
    )
    generator = torch.Generator().manual_seed(seed) if shuffle else None
    return torch.utils.data.DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        generator=generator,
    )


def _run_epoch(
    torch: Any,
    model: Any,
    loader: Any,
    device: Any,
    optimizer: Any | None = None,
) -> tuple[float, float]:
    training = optimizer is not None
    model.train(training)
    total_loss = 0.0
    correct = 0
    examples = 0
    context = torch.enable_grad() if training else torch.no_grad()

    with context:
        for states, actions in loader:
            states = states.to(device)
            actions = actions.to(device)
            logits = model(states)
            loss = torch.nn.functional.cross_entropy(logits, actions)
            if not torch.isfinite(loss):
                raise RuntimeError("Loss khong huu han; dung huan luyen de tranh checkpoint hong.")
            if training:
                optimizer.zero_grad(set_to_none=True)
                loss.backward()
                optimizer.step()

            count = int(actions.size(0))
            total_loss += float(loss.detach()) * count
            correct += int((logits.argmax(dim=1) == actions).sum())
            examples += count

    if examples == 0:
        raise ValueError("Split khong co mau de tinh metric.")
    return total_loss / examples, correct / examples


def train_supervised(
    data_dir: str | Path,
    out_dir: str | Path = "checkpoints",
    epochs: int = 20,
    batch_size: int = 256,
    lr: float = 1e-3,
    seed: int = 0,
    cohort: str = "main_model",
) -> Path:
    """Train on train/val only and save the lowest-validation-loss checkpoint.

    Test examples are never opened here. Call :func:`evaluate_checkpoint` once
    after model selection to evaluate the held-out test split. By default only
    the 3,000-game ``main_model`` cohort is used; pass ``cohort="a3"`` for A3.
    """
    for name, value in (("epochs", epochs), ("batch_size", batch_size), ("seed", seed)):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{name} phai la so nguyen.")
    if epochs <= 0 or batch_size <= 0 or seed < 0:
        raise ValueError("epochs, batch_size phai duong va seed khong am.")
    if (
        isinstance(lr, bool)
        or not isinstance(lr, (int, float))
        or not math.isfinite(lr)
        or lr <= 0
    ):
        raise ValueError("lr phai la so huu han duong.")
    if not isinstance(cohort, str) or cohort not in _DATA_COHORTS:
        raise ValueError(f"cohort phai la mot trong {sorted(_DATA_COHORTS)}.")

    data_path = Path(data_dir)
    train_states, train_actions = _load_split(data_path, "train", cohort=cohort)
    val_states, val_actions = _load_split(data_path, "val", cohort=cohort)

    torch = _require_torch()
    from connect_four.agents.networks import CNNPolicyNet

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = CNNPolicyNet(in_channels=2).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    train_loader = _make_loader(
        torch, train_states, train_actions, batch_size, shuffle=True, seed=seed
    )
    val_loader = _make_loader(
        torch, val_states, val_actions, batch_size, shuffle=False, seed=seed
    )

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8]
    output_path = Path(out_dir)
    checkpoint_dir = output_path / "level5_cnn"
    log_dir = output_path / "logs"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = checkpoint_dir / "final.pt"
    metadata_path = checkpoint_dir / "final.json"
    log_path = log_dir / f"train_cnn_{run_id}.csv"
    started_at = datetime.now(timezone.utc)
    started = time.perf_counter()
    best_val_loss = math.inf
    best_epoch = 0

    with log_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=("epoch", "train_loss", "val_loss", "train_accuracy", "val_accuracy", "best"),
        )
        writer.writeheader()
        for epoch in range(1, epochs + 1):
            train_loss, train_accuracy = _run_epoch(
                torch, model, train_loader, device, optimizer=optimizer
            )
            val_loss, val_accuracy = _run_epoch(torch, model, val_loader, device)
            is_best = val_loss < best_val_loss
            if is_best:
                best_val_loss = val_loss
                best_epoch = epoch
                state_dict = {
                    name: value.detach().cpu()
                    for name, value in model.state_dict().items()
                }
                torch.save({"model_state_dict": state_dict}, checkpoint_path)
            writer.writerow(
                {
                    "epoch": epoch,
                    "train_loss": f"{train_loss:.8f}",
                    "val_loss": f"{val_loss:.8f}",
                    "train_accuracy": f"{train_accuracy:.8f}",
                    "val_accuracy": f"{val_accuracy:.8f}",
                    "best": str(is_best).lower(),
                }
            )
            file.flush()

    duration_seconds = time.perf_counter() - started
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=_REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    metadata = {
        "run_id": run_id,
        "commit": commit,
        "model": "CNNPolicyNet",
        "hyperparameters": {
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": lr,
            "seed": seed,
            "in_channels": 2,
            "hidden_channels": 64,
            "optimizer": "Adam",
            "loss": "CrossEntropyLoss",
            "cohort": cohort,
        },
        "data": {
            "directory": str(data_path),
            "cohort": cohort,
            "train_examples": int(len(train_actions)),
            "val_examples": int(len(val_actions)),
            "test_used_during_training": False,
        },
        "selection": {
            "criterion": "minimum validation loss",
            "best_epoch": best_epoch,
            "best_val_loss": best_val_loss,
        },
        "seed": seed,
        "hardware": {
            "device": str(device),
            "platform": platform.platform(),
            "processor": platform.processor() or platform.machine(),
            "gpu": torch.cuda.get_device_name(device) if device.type == "cuda" else None,
            "torch_version": torch.__version__,
        },
        "started_at": started_at.isoformat(),
        "duration_seconds": duration_seconds,
        "training_log": str(log_path),
    }
    with metadata_path.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2, sort_keys=True)
        file.write("\n")
    return checkpoint_path


def evaluate_checkpoint(checkpoint: str | Path, data_dir: str | Path) -> dict[str, float]:
    """Evaluate the selected checkpoint on test exactly once per training run."""
    checkpoint_path = Path(checkpoint)
    if not checkpoint_path.is_file():
        raise FileNotFoundError(f"Khong tim thay checkpoint CNN: {checkpoint_path}")

    metadata_path = checkpoint_path.with_suffix(".json")
    if not metadata_path.is_file():
        raise FileNotFoundError(f"Khong tim thay metadata checkpoint CNN: {metadata_path}")
    with metadata_path.open(encoding="utf-8") as file:
        metadata = json.load(file)
    if not isinstance(metadata, dict):
        raise ValueError(f"Metadata checkpoint khong hop le: {metadata_path}")
    run_id = metadata.get("run_id")
    if (
        not isinstance(run_id, str)
        or not run_id
        or not run_id.replace("_", "").isalnum()
    ):
        raise ValueError(f"Metadata checkpoint khong co run_id hop le: {metadata_path}")
    data_metadata = metadata.get("data")
    if not isinstance(data_metadata, dict):
        raise ValueError(f"Metadata checkpoint khong co data hop le: {metadata_path}")
    cohort = data_metadata.get("cohort")
    if not isinstance(cohort, str) or cohort not in _DATA_COHORTS:
        raise ValueError(f"Metadata checkpoint khong co cohort hop le: {metadata_path}")

    torch = _require_torch()
    from connect_four.agents.networks import CNNPolicyNet

    try:
        payload = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    except TypeError:
        payload = torch.load(checkpoint_path, map_location="cpu")
    state_dict = payload.get("model_state_dict") if isinstance(payload, dict) else None
    if not isinstance(state_dict, dict):
        raise ValueError(f"Checkpoint CNN khong chua model_state_dict hop le: {checkpoint_path}")

    model = CNNPolicyNet(in_channels=2)
    model.load_state_dict(state_dict)
    model.eval()

    usage_path = checkpoint_path.parent / f"test_evaluation_{run_id}.json"
    if usage_path.exists():
        raise RuntimeError(
            f"Tep test da duoc su dung cho run {run_id}; khong duoc danh gia lai."
        )
    test_path = Path(data_dir) / "test.jsonl"
    if not test_path.is_file():
        raise FileNotFoundError(f"Khong tim thay tap test: {test_path}")
    try:
        marker = usage_path.open("x", encoding="utf-8")
    except FileExistsError as err:
        raise RuntimeError(
            f"Tep test da duoc su dung cho run {run_id}; khong duoc danh gia lai."
        ) from err
    with marker:
        json.dump({"run_id": run_id, "status": "evaluation_started"}, marker)
        marker.write("\n")

    test_states, test_actions = _load_split(test_path.parent, "test", cohort=cohort)
    loader = _make_loader(
        torch, test_states, test_actions, batch_size=512, shuffle=False, seed=0
    )
    total_loss = 0.0
    correct = 0
    legal_predictions = 0
    examples = 0
    with torch.no_grad():
        for states, actions in loader:
            logits = model(states)
            loss = torch.nn.functional.cross_entropy(logits, actions, reduction="sum")
            legal_mask = states.sum(dim=(1, 2)) < ROWS
            if not bool(legal_mask.any(dim=1).all()):
                raise ValueError("Tap test co trang thai khong con cot hop le.")
            predictions = logits.argmax(dim=1)
            legal_predictions += int(legal_mask.gather(1, predictions.unsqueeze(1)).sum())
            masked_logits = logits.masked_fill(~legal_mask, -torch.inf)
            correct += int((masked_logits.argmax(dim=1) == actions).sum())
            total_loss += float(loss)
            examples += int(actions.size(0))

    if examples == 0:
        raise ValueError("Tap test khong co mau de danh gia.")
    metrics = {
        "test_loss": total_loss / examples,
        "top1_accuracy": correct / examples,
        "legal_action_rate": legal_predictions / examples,
        "test_examples": float(examples),
    }
    with usage_path.open("w", encoding="utf-8") as file:
        json.dump(
            {
                "run_id": run_id,
                "status": "completed",
                "evaluated_at": datetime.now(timezone.utc).isoformat(),
                "metrics": metrics,
            },
            file,
            indent=2,
            sort_keys=True,
        )
        file.write("\n")
    return metrics
