# Ke hoach kiem thu

Chay:

```bash
cd Connect_Four
pytest -q
```

| File | Noi dung | Trang thai |
|---|---|---|
| `test_smoke.py` | Hop dong API, registry 6 tac tu, hang so | Da co, dang chay |
| `test_logging.py` | `run_id`, manifest, ghi CSV ván/nước, percentile | Da co, dang chay |
| `test_engine.py` | Luat: tha quan, cot day, thang/hoa, undo, clone | Can viet khi lam Task 1 |
| `test_crosscheck.py` | Engine bitboard vs `ReferenceGame` tren 1000 chuoi nuoc ngau nhien | Can viet sau khi co ban tham chieu |
| `test_positions.py` | Doc `data/positions.csv`, kiem tra `winning_moves` | Can viet |
| `test_data_split.py` | Sinh nhãn Alpha-Beta, chia theo ván, lọc trùng và lật gương chỉ ở train | Đã có |
| `test_agents.py` | Random/Heuristic: nuoc hop le, seed, khong doi game, van ket thuc | Da co, chay tren ca hai engine |
| `test_heuristic.py` | Thang > chan > an toan > diem; hoa diem, ham diem, van hoa, thong ke | Da co, chay tren ca hai engine |
| `test_alphabeta.py` | Minimax do sau 1–4, bon to hop cat tia/sap xep, thong ke, Budget(depth/time_s), timeout va khong doi game | Da co, chay tren ca hai engine |
| `test_mcts.py` | MCTS thang Random >= 95% o 500 mo phong | Can viet |
| `test_metrics.py` | Wilson, bootstrap, p95 | Can viet |

Nguyen tac:
- Test phai chay duoc khi **chua cai torch** (tren CI).
- Khong dung `time.sleep`; test thoi gian chi kiem tra nguong rong.
- Moi bug tim thay tren GitHub phai co mot test tai hien truoc khi sua.

Danh gia K1 (khong can CLI giai dau):

```bash
PYTHONPATH=src python scripts/evaluate_k1.py
```

Cau hinh `configs/k1_random_heuristic.json`: 200 van, 100 khai cuoc ngau nhien
khac nhau, moi khai cuoc dau hai lan doi ben; seed khai cuoc/Heuristic = 0,
Random = 1. Script luu log van, nuoc, manifest va bang ket qua; bao loi neu
Heuristic thang duoi 190/200 van. Xem `docs/EXPERIMENT_LOG.md` de doc lan chay thuc te.
