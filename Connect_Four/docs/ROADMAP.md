# Lộ trình thực hiện

Ký hiệu: **[L]** = lập trình, **[D]** = chạy/tài liệu.

Mỗi mục nên được tạo thành một GitHub Issue, làm trên nhánh riêng, gộp qua pull request.
Commit theo quy ước của học phần: `TuanXX/DuAn/Noi dung cong viec`.

## Mốc M1 — Engine đúng luật (ưu tiên số 1)

- [ ] **[L]** `game/constants.py` — đã có hằng số, không cần sửa
- [ ] **[L]** `game/reference.py` — bản chậm bằng list 2 chiều
- [ ] **[L]** `game/engine.py` — bitboard 49-bit
- [ ] **[L]** `tests/test_engine.py` — luật: thả quân, cột đầy, 4 hướng thắng, hòa, undo, clone
- [ ] **[L]** `tests/test_crosscheck.py` — 1000 chuỗi nước ngẫu nhiên, bitboard == reference
- [ ] **[D]** `tests/data/positions.csv` — nâng lên ≥ 30 vị trí

**Điều kiện xong:** `pytest -q` xanh; `ConnectFour` và `ReferenceGame` cho cùng kết quả trên mọi chuỗi test.

## Mốc M2 — Bốn tác tử cổ điển

- [x] **[L]** `agents/random_agent.py` — cấp 1, có test hành động hợp lệ và seed
- [x] **[L]** `agents/heuristic.py` — cấp 2, thắng > chặn > an toàn > điểm; có test trên hai engine
- [x] **[L]** `agents/alphabeta.py` — cấp 3, negamax + cắt tỉa/sắp xếp bật tắt, đếm nút, ngân sách độ sâu/thời gian; có test trên hai engine (K2, chờ review PR)
- [ ] **[L]** `agents/mcts.py` — cấp 4, UCT + ngân sách mô phỏng
- [ ] **[L]** `evaluation/metrics.py` — Wilson, bootstrap, p95
- [ ] **[L]** `evaluation/runlog.py` + `evaluation/match.py` + `evaluation/cli.py` — `run_id`, manifest, chạy trận, ghi CSV ván/nước
- [ ] **[L]** `play.py` — chơi terminal

**Điều kiện xong:** Heuristic và MCTS thắng Random ≥ 95% trên 200 ván; có log CSV thô.

K1: Heuristic thắng Random 198/200 ván (99%), seed khai cuộc/Heuristic = 0,
Random = 1; 100 khai cuộc, đổi bên theo cặp. Xem lần chạy
`k1-heuristic-random-20261109T061032Z-s0` trong [nhật ký thực nghiệm](EXPERIMENT_LOG.md).
K2: đã có code/test Alpha-Beta, chờ review PR; xem [hướng dẫn K2](ALPHABETA.md).
Mốc M2 còn MCTS và đánh giá tương ứng, cùng bước review/bàn giao K2.

## Mốc M3 — Giải đấu và ablation

- [ ] **[D]** Pilot: 20–50 ván/cặp để chốt ngân sách thời gian
- [ ] **[D]** Giải đấu chế độ mặc định: 200 ván × 6 cặp (4 tác tử) = 1.200 ván
- [ ] **[D]** Giải đấu chế độ cùng thời gian mỗi nước
- [ ] **[D]** Ghi `results/logs/run_manifest.csv`, `games_<run_id>.csv`, `moves_<run_id>.csv`
- [ ] **[D]** Ghi mục tương ứng trong `docs/EXPERIMENT_LOG.md`
- [ ] **[L]** Ablation A1: bật/tắt cắt tỉa (xem `configs/ablation_a1_pruning.yaml`)
- [ ] **[L]** Ablation A2: ngân sách MCTS 100→5000 (xem `configs/ablation_a2_mcts_budget.yaml`)

**Điều kiện xong:** `results/logs/*.csv` + `results/tables/*.csv` + hình trong `results/figures/`.

## Mốc M4 — Cấp 5 (NN) và cấp 6 (DQN)

- [ ] **[L]** `agents/networks.py` — định nghĩa kiến trúc CNN Policy và DQN Net
- [ ] **[L]** `training/gen_data.py` — sinh nhãn bằng Alpha-Beta, chia theo ván
- [ ] **[L]** `training/train_supervised.py` — huấn luyện CNN policy net
- [ ] **[L]** `agents/nn_agent.py` — nạp checkpoint, chọn nước hợp lệ (cấp 5)
- [ ] **[L]** `training/train_dqn.py` — Deep Q-Network, Replay Buffer, Target Network, đối thủ cố định → self-play
- [ ] **[L]** `agents/dqn.py` — chọn nước đi bằng Q-values trên cột hợp lệ (cấp 6)
- [ ] **[D]** Ghi `results/logs/train_cnn_<run_id>.csv` và `train_dqn_<run_id>.csv`
- [ ] **[D]** Giải đấu đầy đủ 6 tác tử: 15 cặp × 200 ván = 3.000 ván/chế độ

**Điều kiện xong:** có checkpoint riêng cho cấp 5 và cấp 6, có log huấn luyện, có điểm đối kháng.

## Mốc M5 — Demo và báo cáo

- [ ] **[L]** `ui/gui.py` — pygame, chọn tác tử, hiện thời gian mỗi nước
- [ ] **[L]** `notebooks/01_tournament_analysis.ipynb` — dựng bảng/hình từ log thô
- [ ] **[D]** Hoàn thiện `docs/EXPERIMENT_LOG.md` và `results/tables/report_numbers.csv`
- [ ] **[D]** Báo cáo bám cấu trúc 7 mục của proposal (Tóm tắt + mục 1–7) trong `docs/report/`
- [ ] **[D]** Slide `docs/slides/`, poster `docs/poster/`
- [ ] **[D]** Đóng gói ZIP đúng quy định, kiểm tra chạy lại trên máy sạch

## Việc nên làm ngay (tuần này)

1. Commit khung này.
2. Tạo 3 issue: Engine (M1), Heuristic + Alpha-Beta (M2), Giải đấu (M3).
3. Mỗi thành viên nhận một issue, tạo nhánh `feat/engine-bitboard`, `feat/alphabeta`, ...
4. Chốt lịch: ai làm engine xong trước thì người khác viết test song song.
