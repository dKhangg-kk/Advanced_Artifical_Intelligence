# Nhật ký thực nghiệm

File này là **nhật ký người đọc** cho toàn bộ đồ án. Mỗi lần chạy thực nghiệm
(giải đấu, ablation, huấn luyện, kiểm thử thủ công có số liệu) phải có một mục
ở đây. Mục này liên kết tới log thô trong `results/logs/` và bảng tổng hợp trong
`results/tables/`.

> Quy ước chi tiết về schema và cách truy vết số liệu: xem [`docs/LOGGING.md`](LOGGING.md).

## Cách ghi

Mỗi mục dùng mẫu sau:

```markdown
## <run_id> — <mục tiêu ngắn>

- **Ngày:** YYYY-MM-DD
- **Người chạy:** Họ tên / MSSV
- **Loại:** tournament | ablation | train-cnn | train-dqn | smoke-test
- **Mục tiêu:** trả lời RQ nào / kiểm tra giả thuyết nào
- **Config:** `configs/<file>.yaml`
- **Commit:** `<hash>`
- **Lệnh chạy:**
  ```bash
  <copy nguyên văn lệnh>
  ```
- **Seed:** <seed>
- **Môi trường:** CPU/GPU/RAM, Python, NumPy, PyTorch
- **Thời gian chạy:** bắt đầu → kết thúc
- **Trạng thái:** completed | failed | partial
- **Log thô:**
  - `results/logs/games_<run_id>.csv`
  - `results/logs/moves_<run_id>.csv`
  - `results/logs/train_<run_id>.csv` (nếu có)
- **Bảng/hình liên quan:** `results/tables/...`, `results/figures/...`
- **Số liệu chính:**

  | Chỉ số | Giá trị | Nguồn |
  |---|---|---|
  | ... | ... | file + cột + bộ lọc |

- **Nhận xét:** điều quan sát được, khác biệt so với lần trước, vấn đề cần điều tra.
- **Việc tiếp theo:** ...
```md

## Quy tắc

1. `run_id` phải khớp với `run_manifest.csv` và tên file log.
2. Không ghi số liệu vào nhật ký nếu chưa có log thô tương ứng.
3. Số kế hoạch (ví dụ “3.000 ván”) ghi rõ nguồn là proposal/config, không giả làm số đo.
4. Lần chạy lỗi vẫn ghi lại, kèm lý do và log nếu có.
5. Không sửa mục cũ; nếu chạy lại, thêm mục mới với `run_id` mới.
6. Mỗi bảng/hình trong báo cáo phải trỏ về một mục trong nhật ký này.

## Danh sách lần chạy

| run_id | Ngày | Loại | Mục tiêu | Trạng thái | Log thô |
|---|---|---|---|---|---|
| k1-heuristic-random-20261109T060914Z-s0 | 2026-11-09 | tournament | K1 Heuristic vs Random (pilot) | completed | `results/logs/games_k1-heuristic-random-20261109T060914Z-s0.csv` |
| k1-heuristic-random-20261109T061032Z-s0 | 2026-11-09 | tournament | K1 Heuristic vs Random (bản đã commit) | completed | `results/logs/games_k1-heuristic-random-20261109T061032Z-s0.csv` |

## Mục chi tiết

<!-- Thêm mục mới lên đầu hoặc cuối, miễn giữ thứ tự thời gian rõ ràng. -->

### Ví dụ minh hoạ — không phải số liệu thật

```markdown
## tournament-default-20261106T143000Z-s20261102 — So sánh 6 agent

- **Ngày:** 2026-11-06
- **Người chạy:** Phạm Thái Duy Khang / 3124720033
- **Loại:** tournament
- **Mục tiêu:** RQ1 — Alpha-Beta vs MCTS trong cùng ngân sách thời gian
- **Config:** `configs/tournament_timed.yaml`
- **Commit:** `abc1234`
- **Lệnh chạy:**
  ```bash
  python -m connect_four.evaluation.cli \
    --a alphabeta --b mcts --time-a 1.0 --time-b 1.0 \
    --openings 100 --seed 20261102 \
    --out results/logs/games_tournament-default-20261106T143000Z-s20261102.csv
  ```
- **Seed:** 20261102
- **Môi trường:** CPU i7-12700, GPU RTX 3060, 16 GB RAM, Python 3.12, NumPy 2.x, PyTorch 2.x
- **Thời gian chạy:** 14:30 → 16:10 UTC
- **Trạng thái:** completed
- **Log thô:**
  - `results/logs/games_tournament-default-20261106T143000Z-s20261102.csv`
  - `results/logs/moves_tournament-default-20261106T143000Z-s20261102.csv`
- **Bảng/hình liên quan:** `results/tables/tournament_timed.csv`, `results/figures/score_matrix.png`
- **Số liệu chính:**

  | Chỉ số | Giá trị | Nguồn |
  |---|---|---|
  | Số ván | 200 | `games_...csv`, `count(*)` |
  | Alpha-Beta thắng | 62.5% | `games_...csv`, `winner=a`, `pair=alphabeta_vs_mcts` |
  | P95 Alpha-Beta | 420 ms | `moves_...csv`, phân vị 95 `time_ms`, `agent=alphabeta` |

- **Nhận xét:** ví dụ minh hoạ cách ghi, không dùng làm kết quả báo cáo.
- **Việc tiếp theo:** chạy thêm seed 42 và 2026 để kiểm tra độ ổn định.
```

## k1-heuristic-random-20261109T060914Z-s0 — K1 Heuristic vs Random (pilot)

- **Ngày:** 09/11/2026 (giờ Việt Nam).
- **Thực hiện:** Codex chạy trên máy của Phạm Thái Duy Khang / 3124720033.
- **Loại/mục tiêu:** tournament; kiểm tra điều kiện Issue #12, thắng Random ít nhất 190/200 ván.
- **Config:** `configs/k1_random_heuristic.json` (hash `b702f737ddf17e96`).
- **Commit:** `431ca16` + thay đổi chưa commit lúc chạy; chỉ là pilot, không tái tạo được từ commit nền. Dùng lần chạy kế tiếp để kiểm chứng.
- **Lệnh chạy:** `PYTHONPATH=src python scripts/evaluate_k1.py` từ `Connect_Four/`; dùng Python trong môi trường riêng có NumPy/pytest.
- **Seed:** khai cuộc = 0, Heuristic = 0, Random = 1; không đổi seed để chọn kết quả tốt.
- **Thiết kế:** 100 khai cuộc ngẫu nhiên khác nhau, mỗi khai cuộc 4 nước; đấu hai lần đổi bên, tổng 200 ván và 100 ván mỗi bên đi trước. Agent giữ chuỗi RNG qua các ván, không reseed sau mỗi ván.
- **Môi trường:** Python 3.13.7, NumPy 2.5.4, CPU `arm`, Darwin 25.6.0; không dùng GPU; RAM không được thu thập vì môi trường tối thiểu không cài psutil.
- **Thời gian (UTC):** 2026-11-09T06:09:14+00:00 → 2026-11-09T06:09:15+00:00.
- **Trạng thái:** completed.
- **Log thô:** `results/logs/games_k1-heuristic-random-20261109T060914Z-s0.csv`, `results/logs/moves_k1-heuristic-random-20261109T060914Z-s0.csv`; thông tin lần chạy trong `results/logs/run_manifest.csv`.
- **Bảng:** `results/tables/k1-heuristic-random-20261109T060914Z-s0.csv`.
- **Kết quả:** thắng 198, hòa 0, thua 2; tỷ lệ thắng 99% (chỉ tính thắng, không cộng ván hòa).
- **Kiểm chứng:** phát lại toàn bộ chuỗi nước, kiểm tra ván kết thúc và người thắng trước khi lưu log.
- **Giới hạn:** một bộ seed cố định; không khẳng định đạt 99% ở mọi khai cuộc/seed hoặc trước các tác tử mạnh hơn. Chưa đánh giá Alpha-Beta/MCTS.

## k1-heuristic-random-20261109T061032Z-s0 — K1 Heuristic vs Random

- **Ngày:** 09/11/2026 (giờ Việt Nam).
- **Thực hiện:** Codex chạy trên máy của Phạm Thái Duy Khang / 3124720033.
- **Loại/mục tiêu:** tournament; kiểm tra điều kiện Issue #12, thắng Random ít nhất 190/200 ván.
- **Config:** `configs/k1_random_heuristic.json` (hash `b702f737ddf17e96`).
- **Commit:** `1c22a73` (mã và test đã commit trước khi chạy).
- **Lệnh chạy:** `PYTHONPATH=src python scripts/evaluate_k1.py` từ `Connect_Four/`; dùng Python trong môi trường riêng có NumPy/pytest.
- **Seed:** khai cuộc = 0, Heuristic = 0, Random = 1; không đổi seed để chọn kết quả tốt.
- **Thiết kế:** 100 khai cuộc ngẫu nhiên khác nhau, mỗi khai cuộc 4 nước; đấu hai lần đổi bên, tổng 200 ván và 100 ván mỗi bên đi trước. Agent giữ chuỗi RNG qua các ván, không reseed sau mỗi ván.
- **Môi trường:** Python 3.13.7, NumPy 2.5.4, CPU `arm`, Darwin 25.6.0; không dùng GPU; RAM không được thu thập vì môi trường tối thiểu không cài psutil.
- **Thời gian (UTC):** 2026-11-09T06:10:32+00:00 → 2026-11-09T06:10:32+00:00.
- **Trạng thái:** completed.
- **Log thô:** `results/logs/games_k1-heuristic-random-20261109T061032Z-s0.csv`, `results/logs/moves_k1-heuristic-random-20261109T061032Z-s0.csv`; thông tin lần chạy trong `results/logs/run_manifest.csv`.
- **Bảng:** `results/tables/k1-heuristic-random-20261109T061032Z-s0.csv`.
- **Kết quả:** thắng 198, hòa 0, thua 2; tỷ lệ thắng 99% (chỉ tính thắng, không cộng ván hòa).
- **Kiểm chứng:** phát lại toàn bộ chuỗi nước, kiểm tra ván kết thúc và người thắng trước khi lưu log.
- **Giới hạn:** một bộ seed cố định; không khẳng định đạt 99% ở mọi khai cuộc/seed hoặc trước các tác tử mạnh hơn. Chưa đánh giá Alpha-Beta/MCTS.
