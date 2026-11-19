#!/usr/bin/env python3
"""Dong bang checkpoint DQN cuoi cung (Y5) tu o A4 ``default_decay`` seed 0.

QUY TAC CHON (viet truoc khi xem ket qua validation cua cac moc):

* Ung vien: cac moc episode (1.000 / 2.500 / 5.000 / 10.000) cua o A4
  ``default_decay`` seed 0 - mo hinh chinh theo ke hoach nhom.
* Diem cua moc = trung binh cua score truoc Random (seed validation 20261102) va
  score truoc Heuristic (seed validation 20261103); moi doi thu 100 van, DQN
  danh greedy (epsilon = 0).
* Chon moc co diem cao nhat; bang diem thi chon moc co so episode nho hon.
* Khong dung van giai dau (seed 20261118 / 20261119) de chon moc.

Ket qua: ``checkpoints/level6_dqn/final.pt`` (chi trong so mang, khong kem
optimizer, khoang 1,5 MB) va ``final.json`` (metadata, bang validation, sha256).

Chay tu ``Connect_Four/``:

    PYTHONPATH=src python scripts/freeze_dqn_checkpoint.py
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

SELECTION_RULE = (
    "Diem moc = trung binh(score vs Random seed 20261102, score vs Heuristic seed 20261103), "
    "moi doi thu 100 van, DQN greedy; chon diem cao nhat, bang diem thi chon moc episode nho hon; "
    "khong dung van giai dau de chon."
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _git(*args: str) -> str | None:
    try:
        return subprocess.run(
            ["git", *args], check=True, capture_output=True, text=True, timeout=5, cwd=_ROOT
        ).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def milestone_table(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    by_episode: dict[int, dict[str, dict[str, str]]] = {}
    for row in rows:
        by_episode.setdefault(int(row["episode"]), {})[row["opponent"]] = row
    table = []
    for episode, per_opp in sorted(by_episode.items()):
        score_random = float(per_opp["random"]["score"])
        score_heuristic = float(per_opp["heuristic"]["score"])
        table.append(
            {
                "episode": episode,
                "score_vs_random": score_random,
                "wdl_vs_random": "-".join(per_opp["random"][k] for k in ("wins", "draws", "losses")),
                "score_vs_heuristic": score_heuristic,
                "wdl_vs_heuristic": "-".join(per_opp["heuristic"][k] for k in ("wins", "draws", "losses")),
                "mean_validation_score": (score_random + score_heuristic) / 2,
            }
        )
    return table


def choose(table: list[dict[str, Any]]) -> dict[str, Any]:
    return max(table, key=lambda item: (round(item["mean_validation_score"], 9), -item["episode"]))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--decay", default="default_decay")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", default="checkpoints/level6_dqn/final.pt")
    args = parser.parse_args(argv)

    import torch

    cells = sorted(Path("results/logs").glob(f"ablation_a4_cell_a4-{args.decay}-s{args.seed}-*.csv"))
    if not cells:
        raise SystemExit("Chua co o A4 hoan tat cho cau hinh nay; chay run_ablation_a4.py truoc.")
    cell_path = cells[-1]
    with cell_path.open(encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    run_id = rows[0]["run_id"]
    table = milestone_table(rows)
    best = choose(table)
    episode = best["episode"]

    src_dir = Path("checkpoints/level6_dqn/a4") / f"{args.decay}_s{args.seed}"
    src = src_dir / f"dqn_model_ep{episode:06d}.pt"
    src_meta = json.loads(src.with_suffix(".json").read_text(encoding="utf-8"))
    payload = torch.load(src, map_location="cpu", weights_only=True)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state_dict": payload["model_state_dict"],
            "episode": payload["episode"],
            "epsilon": payload["epsilon"],
            "seed": payload["seed"],
            "run_id": run_id,
            "config": payload["config"],
        },
        out,
    )

    # Kiem tra tai lai bang DQNAgent that: dung luat, khong chon cot day.
    from connect_four.agents.dqn import DQNAgent
    from connect_four.game.engine import ConnectFour

    agent = DQNAgent(checkpoint=out, epsilon=0.0, seed=0)
    game = ConnectFour()
    assert agent.choose(game) in game.legal_actions()
    for _ in range(6):  # lap day cot 0 roi kiem tra agent khong chon cot day
        game.step(0)
        if game.is_terminal():
            break
    else:
        assert agent.choose(game) in game.legal_actions() and agent.choose(game) != 0

    metadata = {
        "checkpoint_file": out.name,
        "status": "frozen",
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "run_id": run_id,
        "ablation_cell": {"experiment": "A4", "config_id": args.decay, "seed": args.seed},
        "selected_episode": episode,
        "selection_rule": SELECTION_RULE,
        "validation": table,
        "validation_seeds": {"random": 20261102, "heuristic": 20261103},
        "validation_games_per_opponent": 100,
        "source_checkpoint": str(src),
        "source_checkpoint_sha256": _sha256(src),
        "sha256": _sha256(out),
        "size_bytes": out.stat().st_size,
        "optimizer_state_included": False,
        "optimizer_updates_at_checkpoint": src_meta["optimizer_updates"],
        "epsilon_at_checkpoint": src_meta["epsilon"],
        "training_elapsed_seconds_at_checkpoint": src_meta["training_elapsed_seconds"],
        "hyperparameters": payload["config"],
        "training_git_commit": src_meta.get("git_commit"),
        "freeze_git_commit": _git("rev-parse", "HEAD"),
        "training_log": f"results/logs/train_dqn_{run_id}.csv",
        "ablation_cell_table": str(cell_path),
        "python_version": src_meta["python_version"],
        "torch_version": src_meta["torch_version"],
        "device": src_meta["device"],
        "accelerator": src_meta["accelerator"],
        "hardware": src_meta["hardware"],
        "freeze_host": platform.platform(),
    }
    out.with_suffix(".json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(f"{'episode':>8} {'vs random':>10} {'vs heur.':>10} {'mean':>8}")
    for item in table:
        mark = "  <- chon" if item["episode"] == episode else ""
        print(
            f"{item['episode']:>8} {item['score_vs_random']:>10.3f} "
            f"{item['score_vs_heuristic']:>10.3f} {item['mean_validation_score']:>8.3f}{mark}"
        )
    print(f"final.pt: {out} ({out.stat().st_size / 1e6:.2f} MB), sha256={metadata['sha256'][:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
