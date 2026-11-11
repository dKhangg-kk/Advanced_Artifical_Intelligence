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
- [x] **[L]** `evaluation/metrics.py` — Wilson, bootstrap có seed, p95
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
- [ ] **[D]** Báo cáo đủ 5 chương theo cấu trúc bên dưới trong `docs/report/`
- [ ] **[D]** Slide `docs/slides/`, poster `docs/poster/`
- [ ] **[D]** Đóng gói ZIP đúng quy định, kiểm tra chạy lại trên máy sạch

## Cấu trúc báo cáo 5 chương

Theo phân công báo cáo trong các issue #30, #31, #35, #36, #40, #41, #45 và #46.
Các tên tệp dưới đây tính từ `docs/report/`; tệp chưa có sẽ được bổ sung theo issue tương ứng.

| Chương | Nội dung | Tệp theo phân công |
| --- | --- | --- |
| 1. Giới thiệu | Bối cảnh, luật Connect Four, mục tiêu, câu hỏi nghiên cứu, phạm vi và sản phẩm | `01_gioi_thieu.md` |
| 2. Cơ sở lý thuyết | Tác tử trò chơi; Minimax, Alpha-Beta, MCTS/UCT; policy/value network, học có giám sát; RL, DQN và self-play | `02a_tim_kiem.md`, `02b_hoc_giam_sat.md`, `02c_hoc_tang_cuong.md` |
| 3. Thiết kế và cài đặt | Biểu diễn game, state/action/reward; kiến trúc engine–agent–UI; thuật toán cấp 1–4; CNN cấp 5; DQN cấp 6 và thiết kế giải đấu | `03a_kien_truc.md`, `03b_thuat_toan.md`, `03c_cnn.md`, `03d_dqn_giai_dau.md` |
| 4. Thực nghiệm và thảo luận | Môi trường, kết quả đối đầu, độ trễ và chi phí; đường cong học CNN/DQN; ablation A1–A5; ván minh họa, thất bại và hạn chế | `04a_ket_qua.md` đến `04h_thao_luan.md` |
| 5. Kết luận và hướng phát triển | Trả lời câu hỏi nghiên cứu; thành tựu, hạn chế, khả năng tái lập và hướng mở rộng | `05_ket_luan.md` |

Bìa và mục lục nằm trong `00_bia_muc_luc.md`. Tài liệu tham khảo, nguồn kế thừa và tỷ lệ đóng góp nằm trong `06_tai_lieu_dong_gop.md`; đây là phần cuối báo cáo, không phải Chương 6.

Bản giữa kỳ gồm Chương 1–3; bản cuối kỳ đủ 5 chương. Số liệu phải dẫn về `results/tables/report_numbers.csv` và `run_id`; không ghi kết quả chưa chạy.

## Phối hợp thực hiện

1. Mỗi thành viên theo dõi issue đã được giao và làm trên nhánh riêng.
2. Mở PR liên kết issue, cập nhật nhật ký đóng góp và kết quả kiểm tra.
3. Có ít nhất một approve từ người review trước khi merge; thay đổi mã nguồn phải có test phù hợp và `pytest -q` xanh.
