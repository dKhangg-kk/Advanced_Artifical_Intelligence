# Biên bản chạy DQN–Heuristic và rà soát bằng chứng của Như Ý

- Ngày kiểm tra: 25/11/2026 (UTC+7).
- Repository: dKhangg-kk/Advanced_Artifical_Intelligence.

## 1. Run DQN cấp 6 đối đầu Heuristic

- run_id: `dqn-vs-heuristic-20261125T163855Z-s2026`.
- Lệnh: `python -m connect_four.evaluation.cli --a dqn --b heuristic --openings 5 --seed 2026 --checkpoint-a checkpoints/level6_dqn/final.pt`.
- Checkpoint: `checkpoints/level6_dqn/final.pt`.
- Seed: 2026; 5 khai cuộc × 2 lượt đổi bên = 10 ván.
- Kết quả DQN: **2 thắng – 1 hòa – 7 thua**, score = **0.250**.
- Log ván: `results/logs/games_dqn-vs-heuristic-20261125T163855Z-s2026.csv`.
- Log nước đi: `results/logs/moves_dqn-vs-heuristic-20261125T163855Z-s2026.csv`.

## 2. Kết quả audit 49 run cũ

| Nhóm | Số run | Kiểm tra bằng chứng |
|---|---:|---|
| Tournament | 33 | Games log và moves log tồn tại; manifest completed |
| A4 DQN | 10 | Train log và ablation log tồn tại; manifest completed |
| A6 DQN | 6 | Train log và ablation log tồn tại; manifest completed |
| **Tổng** | **49** | **Đã kiểm tra** |

- Đã gán người thực hiện cho 43/43 dòng CHƯA XÁC NHẬN: 33 tournament và 10 A4.
- Sáu run A6 đã có tên Như Ý từ trước và được giữ nguyên.
- Tổng manifest sau run mới: 70; tổng assignments: 70.
- Dòng assignments theo người thực hiện: {'Phạm Thái Duy Khang': 12, 'Bùi Quyền Kiệt': 5, 'Phan Lê Ngọc Như Ý': 50, 'Bùi Anh Đức': 3}.
- Đối chiếu ID: manifest và assignments khớp một-một; không có ID trùng, thiếu hoặc mồ côi.

## 3. Đối chiếu report_numbers

- Có 43/49 run được dẫn trực tiếp bằng run_id trong results/tables/report_numbers.csv.
- 6 run A4 không có dòng run_id riêng; log thô vẫn tồn tại và metric A4 được tổng hợp ở bảng kết quả A4.
- Không tự tạo số liệu report_numbers cho run không có dòng nguồn trực tiếp.

Các run A4 không có run_id riêng trong report_numbers:
- `a4-fast_decay-s0-20261118T171251Z`
- `a4-fast_decay-s2026-20261118T174456Z`
- `a4-fast_decay-s42-20261118T171251Z`
- `a4-slow_decay-s0-20261118T174505Z`
- `a4-slow_decay-s2026-20261118T181447Z`
- `a4-slow_decay-s42-20261118T183210Z`

## 4. Danh sách 49 run đã audit

### Tournament (33)
- `tournament-default-20261113T140850Z-s20261113-random-vs-heuristic`
- `tournament-default-20261113T140850Z-s20261113-random-vs-dqn`
- `tournament-default-20261113T140850Z-s20261113-heuristic-vs-dqn`
- `tournament-default-20261118T163224Z-s20261118-random-vs-heuristic`
- `tournament-default-20261118T163224Z-s20261118-random-vs-alphabeta`
- `tournament-default-20261118T163224Z-s20261118-random-vs-mcts`
- `tournament-default-20261118T163224Z-s20261118-random-vs-nn`
- `tournament-default-20261118T163224Z-s20261118-random-vs-dqn`
- `tournament-default-20261118T163224Z-s20261118-heuristic-vs-alphabeta`
- `tournament-default-20261118T163224Z-s20261118-heuristic-vs-mcts`
- `tournament-default-20261118T163224Z-s20261118-heuristic-vs-nn`
- `tournament-default-20261118T163224Z-s20261118-heuristic-vs-dqn`
- `tournament-default-20261118T163224Z-s20261118-alphabeta-vs-mcts`
- `tournament-default-20261118T163224Z-s20261118-alphabeta-vs-nn`
- `tournament-default-20261118T163224Z-s20261118-alphabeta-vs-dqn`
- `tournament-default-20261118T163224Z-s20261118-mcts-vs-nn`
- `tournament-default-20261118T163224Z-s20261118-mcts-vs-dqn`
- `tournament-default-20261118T163224Z-s20261118-nn-vs-dqn`
- `tournament-timed-20261118T164206Z-s20261119-random-vs-heuristic`
- `tournament-timed-20261118T164206Z-s20261119-random-vs-alphabeta`
- `tournament-timed-20261118T164206Z-s20261119-random-vs-mcts`
- `tournament-timed-20261118T164206Z-s20261119-random-vs-nn`
- `tournament-timed-20261118T164206Z-s20261119-random-vs-dqn`
- `tournament-timed-20261118T164206Z-s20261119-heuristic-vs-alphabeta`
- `tournament-timed-20261118T164206Z-s20261119-heuristic-vs-mcts`
- `tournament-timed-20261118T164206Z-s20261119-heuristic-vs-nn`
- `tournament-timed-20261118T164206Z-s20261119-heuristic-vs-dqn`
- `tournament-timed-20261118T164206Z-s20261119-alphabeta-vs-mcts`
- `tournament-timed-20261118T164206Z-s20261119-alphabeta-vs-nn`
- `tournament-timed-20261118T164206Z-s20261119-alphabeta-vs-dqn`
- `tournament-timed-20261118T164206Z-s20261119-mcts-vs-nn`
- `tournament-timed-20261118T164206Z-s20261119-mcts-vs-dqn`
- `tournament-timed-20261118T164206Z-s20261119-nn-vs-dqn`

### A4 DQN (10)
- `a4-default_decay-s0-20261118T155757Z`
- `a4-default_decay-s42-20261118T155757Z`
- `a4-fast_decay-s42-20261118T171251Z`
- `a4-fast_decay-s0-20261118T171251Z`
- `a4-slow_decay-s0-20261118T174505Z`
- `a4-fast_decay-s2026-20261118T174456Z`
- `a4-default_decay-s2026-20261118T180315Z`
- `a4-slow_decay-s2026-20261118T181447Z`
- `a4-slow_decay-s42-20261118T183210Z`
- `a4-default_decay_open4-s0-20261118T184141Z`

### A6 DQN (6)
- `a6-opp_random-s0-20261120T132502Z`
- `a6-opp_selfplay-s0-20261120T132501Z`
- `a6-opp_selfplay-s42-20261120T135944Z`
- `a6-opp_selfplay-s2026-20261120T140154Z`
- `a6-opp_random-s42-20261120T143551Z`
- `a6-opp_random-s2026-20261120T143811Z`

## 5. Kết luận

- Run mới có games log, moves log và manifest; số W-D-L được tính trực tiếp từ games log.
- 49 run cũ trong phạm vi Như Ý đã được kiểm tra file bằng chứng; 43 dòng chưa xác nhận được cập nhật phân công.
- Không chạy lại A4/A6, không sửa checkpoint đã đóng băng và không tạo số liệu báo cáo thay cho nguồn thiếu.
- File Excel được dựng lại từ manifest, assignments và plan bằng scripts/build_experiment_workbook.py.
