#!/usr/bin/env python3
"""Sinh bang Markdown cho cac muc bao cao 4.1-4.5 cua Y tu cac bang CSV da tong hop.

Tranh chep tay so lieu: trong file ``docs/report/*.md`` dat cap dau hieu

    <!-- TABLE:ten_bang -->
    <!-- /TABLE:ten_bang -->

roi chay script, noi dung giua hai dau hieu duoc sinh lai tu ``results/tables``.
Chay lai nhieu lan an toan. Ten bang hop le: xem ``RENDERERS``.

    PYTHONPATH=src python scripts/render_report_tables_y.py docs/report/04a_ket_qua.md ...
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
import re
import sys

TABLES = Path("results/tables")
AGENTS = ["random", "heuristic", "alphabeta", "mcts", "nn", "dqn"]
MODE_NAME = {"default": "chế độ mặc định", "timed": "chế độ cùng thời gian (0,2 giây/nước)"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def md(headers: list[str], rows: list[list[str]], align: list[str] | None = None) -> str:
    align = align or ["---"] * len(headers)
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(align) + " |"]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(lines)


def f2(x: str | float) -> str:
    return f"{float(x):.2f}".replace(".", ",")


def f3(x: str | float) -> str:
    return f"{float(x):.3f}".replace(".", ",")


def num(x: str | float, digits: int = 1) -> str:
    """Dinh dang so kieu Viet: dau cach ngan nghin, dau phay thap phan."""
    return f"{float(x):,.{digits}f}".replace(",", " ").replace(".", ",")


def matrix(mode: str) -> str:
    pairs = read(TABLES / f"y6_{mode}_pair_summary.csv")
    cell: dict[tuple[str, str], str] = {}
    for p in pairs:
        cell[(p["agent_a"], p["agent_b"])] = f2(p["score_a"])
        cell[(p["agent_b"], p["agent_a"])] = f2(1 - float(p["score_a"]))
    names = [a for a in AGENTS if any(a in (p["agent_a"], p["agent_b"]) for p in pairs)]
    rows = [[f"**{r}**"] + [cell.get((r, c), "—") for c in names] for r in names]
    return md(["score của hàng khi gặp cột"] + names, rows, ["---"] + ["---:"] * len(names))


def pairs_table(mode: str) -> str:
    rows = []
    for p in read(TABLES / f"y6_{mode}_pair_summary.csv"):
        rows.append([
            f"{p['agent_a']} – {p['agent_b']}", p["games"], f"{p['wins_a']}–{p['draws']}–{p['wins_b']}",
            f2(p["score_a"]), f"[{f2(p['score_ci95_low'])}; {f2(p['score_ci95_high'])}]",
        ])
    return md(["Cặp (A – B)", "Số ván", "A thắng–hòa–B thắng", "score của A", "Wilson 95%"], rows,
              ["---", "---:", "---:", "---:", "---:"])


def latency(mode: str) -> str:
    rows = []
    for a in read(TABLES / f"y6_{mode}_agent_summary.csv"):
        extra = f"{int(float(a['over_budget_games']))}" if mode == "timed" else "—"
        rows.append([
            a["agent"], a["games"], f2(a["score"]), f"[{f2(a['score_ci95_low'])}; {f2(a['score_ci95_high'])}]",
            num(a["mean_ms_per_move"], 2), num(a["p95_ms_per_move"], 2), num(a["max_ms_per_move"], 1),
            num(a["mean_nodes_per_move"], 0) if float(a["mean_nodes_per_move"]) else "—",
            num(a["mean_simulations_per_move"], 0) if float(a["mean_simulations_per_move"]) else "—", extra,
        ])
    return md(["Tác tử", "Số ván", "score chung", "Wilson 95%", "ms/nước (TB)", "ms/nước (p95)", "ms/nước (max)",
               "nút/nước", "mô phỏng/nước", "ván có nước > 0,2 s" if mode == "timed" else "ván vượt ngân sách"],
              rows, ["---", "---:", "---:", "---:", "---:", "---:", "---:", "---:", "---:", "---:"])


def first_move(mode: str) -> str:
    rows = []
    for r in read(TABLES / f"y6_{mode}_first_move.csv"):
        name = "**tất cả các cặp**" if r["agent_a"] == "ALL" else f"{r['agent_a']} – {r['agent_b']}"
        rows.append([name, r["games"], f"{r['first_player_wins']}–{r['draws']}–{r['second_player_wins']}",
                     f2(r["first_player_score"]),
                     f"[{f2(r['first_player_score_ci95_low'])}; {f2(r['first_player_score_ci95_high'])}]"])
    return md(["Cặp", "Số ván", "Đi trước thắng–hòa–đi sau thắng", "score của bên đi trước", "Wilson 95%"], rows,
              ["---", "---:", "---:", "---:", "---:"])


def positions() -> str:
    data = read(TABLES / "y6_position_accuracy.csv")
    groups = ["win_now", "block", "double_threat", "quiet_legal"]
    head = {"win_now": "thắng ngay", "block": "chặn", "double_threat": "đòn kép (tập con của chặn/thắng)", "quiet_legal": "thế yên (chỉ cần hợp lệ)"}
    ns = {g: next(r for r in data if r["situation"] == g)["positions"] for g in groups}
    rows = []
    for a in AGENTS:
        row = [a]
        for g in groups:
            r = next(x for x in data if x["agent"] == a and x["situation"] == g)
            row.append(f"{f2(r['accuracy'])} ({r['hits']}/{r['attempts']})")
        rows.append(row)
    return md(["Tác tử"] + [f"{head[g]} (n={ns[g]} thế)" for g in groups], rows, ["---"] + ["---:"] * len(groups))


def dqn_validation() -> str:
    meta = json.loads(Path("checkpoints/level6_dqn/final.json").read_text(encoding="utf-8"))
    rows = []
    for v in meta["validation"]:
        chosen = " ← chọn" if v["episode"] == meta["selected_episode"] else ""
        rows.append([f"{v['episode']:,}".replace(",", "."), f"{f2(v['score_vs_random'])} ({v['wdl_vs_random']})",
                     f"{f2(v['score_vs_heuristic'])} ({v['wdl_vs_heuristic']})", f3(v["mean_validation_score"]) + chosen])
    return md(["Mốc episode", "score vs Random (T–H–B)", "score vs Heuristic (T–H–B)", "Điểm chọn mốc (trung bình)"],
              rows, ["---:", "---:", "---:", "---:"])


def a4_main() -> str:
    summary = read(TABLES / "ablation_a4_summary.csv")
    configs = [c for c in ("fast_decay", "default_decay", "slow_decay") if any(s["config_id"] == c for s in summary)]
    episodes = sorted({int(s["episode"]) for s in summary})
    label = {"fast_decay": "0,9990 (nhanh)", "default_decay": "0,9995 (mặc định)", "slow_decay": "0,9998 (chậm)"}
    out = []
    for opponent, title in (("random", "Validation gặp Random"), ("heuristic", "Validation gặp Heuristic")):
        rows = []
        for c in configs:
            row = [label[c]]
            for ep in episodes:
                s = next((x for x in summary if x["config_id"] == c and int(x["episode"]) == ep and x["opponent"] == opponent), None)
                row.append("—" if s is None else f"{f2(s['score_mean'])} ± {f2(s['score_sd'])} [{f2(s['score_min'])}–{f2(s['score_max'])}]")
            rows.append(row)
        out.append(f"**{title}** — score trung bình ± độ lệch chuẩn mẫu giữa các seed, [min–max]; mỗi điểm 100 ván/seed.\n\n"
                   + md(["Epsilon decay"] + [f"{e:,}".replace(",", ".") + " ep" for e in episodes], rows,
                        ["---"] + ["---:"] * len(episodes)))
    return "\n\n".join(out)


def a4_seeds() -> str:
    rows = []
    order = {"fast_decay": 0, "default_decay": 1, "slow_decay": 2}
    # bang theo seed o moc cuoi (10.000 episode)
    final_ep = max(int(r["episode"]) for r in read(TABLES / "ablation_a4_results.csv"))
    data = [r for r in read(TABLES / "ablation_a4_results.csv") if int(r["episode"]) == final_ep and r["config_id"] in order]
    keys = sorted({(r["config_id"], int(r["seed"])) for r in data}, key=lambda k: (order[k[0]], k[1]))
    for cfg, seed in keys:
        get = lambda opp: next(r for r in data if r["config_id"] == cfg and int(r["seed"]) == seed and r["opponent"] == opp)
        rnd, heu = get("random"), get("heuristic")
        rows.append([cfg, str(seed), f"{rnd['wins']}–{rnd['draws']}–{rnd['losses']}", f2(rnd["score"]),
                     f"{heu['wins']}–{heu['draws']}–{heu['losses']}", f2(heu["score"]),
                     f2(rnd["train_win_rate_last500"]), num(rnd["training_elapsed_seconds"], 0)])
    return md(["Cấu hình", "Seed", "vs Random T–H–B", "score", "vs Heuristic T–H–B", "score",
               "Tỷ lệ thắng huấn luyện (500 ep cuối)", "Thời gian huấn luyện (s)"], rows,
              ["---", "---:", "---:", "---:", "---:", "---:", "---:", "---:"])


def a4_extension() -> str:
    data = [r for r in read(TABLES / "ablation_a4_results.csv") if r["config_id"] == "default_decay_open4"]
    base = {(r["episode"], r["opponent"]): r for r in read(TABLES / "ablation_a4_results.csv")
            if r["config_id"] == "default_decay" and r["seed"] == "0"}
    if not data:
        return "_Chưa có lần chạy mở rộng._"
    rows = []
    for r in sorted(data, key=lambda x: (int(x["episode"]), x["opponent"])):
        b = base.get((r["episode"], r["opponent"]))
        rows.append([f"{int(r['episode']):,}".replace(",", "."), r["opponent"],
                     f"{r['wins']}–{r['draws']}–{r['losses']}", f2(r["score"]),
                     f"[{f2(r['score_ci95_low'])}; {f2(r['score_ci95_high'])}]",
                     "—" if b is None else f"{b['wins']}–{b['draws']}–{b['losses']}",
                     "—" if b is None else f2(b["score"])])
    return md(["Mốc episode", "Đối thủ", "T–H–B (mở rộng, 4 nước ngẫu nhiên)", "score", "Wilson 95%",
               "T–H–B (A4 gốc, seed 0)", "score (A4 gốc)"], rows, ["---:", "---", "---:", "---:", "---:", "---:", "---:"])


def opening_diag() -> str:
    rows = []
    for r in read(TABLES / "dqn_opening_diagnostic.csv"):
        rows.append([r["opponent"], r["opening_plies"], r["games"], f"{r['wins']}–{r['draws']}–{r['losses']}",
                     f2(r["score"]), f"[{f2(r['wilson95_low'])}; {f2(r['wilson95_high'])}]",
                     f"{r['distinct_games']}/{r['games']}"])
    return md(["Đối thủ", "Nước khai cuộc ngẫu nhiên", "Số ván", "DQN T–H–B", "score", "Wilson 95%", "Số ván khác nhau"],
              rows, ["---", "---:", "---:", "---:", "---:", "---:", "---:"])


RENDERERS = {
    "default_matrix": lambda: matrix("default"), "timed_matrix": lambda: matrix("timed"),
    "default_pairs": lambda: pairs_table("default"), "timed_pairs": lambda: pairs_table("timed"),
    "default_latency": lambda: latency("default"), "timed_latency": lambda: latency("timed"),
    "default_first_move": lambda: first_move("default"), "timed_first_move": lambda: first_move("timed"),
    "positions": positions, "dqn_validation": dqn_validation, "a4_main": a4_main, "a4_seeds": a4_seeds,
    "a4_extension": a4_extension, "opening_diag": opening_diag,
}


def render_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    count = 0

    def sub(match: re.Match[str]) -> str:
        nonlocal count
        name = match.group(1)
        if name not in RENDERERS:
            raise SystemExit(f"{path}: bang '{name}' khong ton tai; hop le: {sorted(RENDERERS)}")
        count += 1
        return f"<!-- TABLE:{name} -->\n{RENDERERS[name]()}\n<!-- /TABLE:{name} -->"

    new = re.sub(r"<!-- TABLE:(\w+) -->.*?<!-- /TABLE:\1 -->", sub, text, flags=re.S)
    path.write_text(new, encoding="utf-8")
    return count


def main(argv: list[str]) -> int:
    if not argv:
        raise SystemExit(__doc__)
    for name in argv:
        print(f"{name}: {render_file(Path(name))} bang")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
