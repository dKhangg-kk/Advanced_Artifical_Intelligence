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
| `test_heuristic.py` | Thu tu uu tien: thang ngay > chan > nuoc thuong | Can viet |
| `test_alphabeta.py` | Trung khop minimax thuan o do sau <= 4; dem so nut | Can viet |
| `test_mcts.py` | MCTS thang Random >= 95% o 500 mo phong | Can viet |
| `test_metrics.py` | Wilson, bootstrap, p95 | Can viet |

Nguyen tac:
- Test phai chay duoc khi **chua cai torch** (tren CI).
- Khong dung `time.sleep`; test thoi gian chi kiem tra nguong rong.
- Moi bug tim thay tren GitHub phai co mot test tai hien truoc khi sua.
