# Nhật ký thực nghiệm

File này là **nhật ký người đọc** cho toàn bộ đồ án. Mỗi lần chạy thực nghiệm
(giải đấu, ablation, huấn luyện, kiểm thử thủ công có số liệu) phải có một mục
ở đây. Mục này liên kết tới log thô trong `results/logs/` và bảng tổng hợp trong
`results/tables/`.

> Quy ước chi tiết về schema và cách truy vết số liệu: xem [`docs/LOGGING.md`](LOGGING.md).

> Bảng tổng hợp gửi giảng viên: [`results/experiment_schedule.xlsx`](../results/experiment_schedule.xlsx).
> File được sinh từ `run_manifest.csv` và `results/experiment_assignments.csv`; giờ trong bảng đã đổi từ UTC sang UTC+7.

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
| random-vs-heuristic-20261124T204523Z-s2026 | 2026-11-25 | tournament | Random vs Heuristic, 10 openings | completed | `results/logs/games_random-vs-heuristic-20261124T204523Z-s2026.csv` |
| alphabeta-vs-random-20261124T204529Z-s2026 | 2026-11-25 | tournament | Alpha-Beta depth 3 vs Random, 5 openings | completed | `results/logs/games_alphabeta-vs-random-20261124T204529Z-s2026.csv` |
| mcts-vs-random-20261124T204536Z-s2026 | 2026-11-25 | tournament | MCTS 200 simulations vs Random, 5 openings | completed | `results/logs/games_mcts-vs-random-20261124T204536Z-s2026.csv` |
| k1-heuristic-random-20261109T060914Z-s0 | 2026-11-09 | tournament | K1 Heuristic vs Random (pilot) | completed | `results/logs/games_k1-heuristic-random-20261109T060914Z-s0.csv` |
| k1-heuristic-random-20261109T061032Z-s0 | 2026-11-09 | tournament | K1 Heuristic vs Random (bản đã commit) | completed | `results/logs/games_k1-heuristic-random-20261109T061032Z-s0.csv` |
| ablation-a3-20261111T150514Z-s20261105 | 2026-11-11 | ablation | A3 — ảnh hưởng số ván huấn luyện CNN (RQ2) | completed | `results/logs/ablation_a3_ablation-a3-20261111T150514Z-s20261105.csv` |

## Mục chi tiết

<!-- Thêm mục mới lên đầu hoặc cuối, miễn giữ thứ tự thời gian rõ ràng. -->

## random-vs-heuristic-20261124T204523Z-s2026 — Random vs Heuristic

- **Ngày:** 2026-11-25 (UTC+7)
- **Người chạy:** Bùi Anh Đức
- **Loại:** tournament
- **Mục tiêu:** Cross-check Random–Heuristic theo phân công nhóm 26.
- **Config:** `configs/agents.yaml` (mặc định)
- **Commit:** `ba1be81`
- **Lệnh chạy:**
  ```powershell
  python -m connect_four.evaluation.cli --a random --b heuristic --openings 10 --seed 2026
  ```
- **Seed:** 2026
- **Môi trường:** Windows 10/11, CPU Intel 6/154; Python 3.11.9, NumPy 2.4.6, PyTorch 2.15.0+cpu (theo `results/logs/run_manifest.csv`).
- **Thời gian chạy:** 2026-11-25 03:45:23 → 03:45:23 UTC+7 (2026-11-24 20:45:23 → 20:45:23 UTC)
- **Trạng thái:** completed
- **Log thô:**
  - `results/logs/games_random-vs-heuristic-20261124T204523Z-s2026.csv`
  - `results/logs/moves_random-vs-heuristic-20261124T204523Z-s2026.csv`
- **Bảng/hình liên quan:** Không tạo bảng/hình riêng.
- **Số liệu chính:** 20 ván; Random thắng 0, hòa 0, thua 20; score_A = 0.000. Nguồn: log ván và output CLI.
- **Nhận xét:** Heuristic thắng tuyệt đối 20/20 ván trước Random khi đổi bên đối xứng trên 10 thế khai cuộc.

## alphabeta-vs-random-20261124T204529Z-s2026 — Alpha-Beta depth 3 vs Random

- **Ngày:** 2026-11-25 (UTC+7)
- **Người chạy:** Bùi Anh Đức
- **Loại:** tournament
- **Mục tiêu:** Cross-check Alpha-Beta depth 3 vs Random theo phân công nhóm 26.
- **Config:** `configs/agents.yaml` (mặc định), depth-a = 3
- **Commit:** `ba1be81`
- **Lệnh chạy:**
  ```powershell
  python -m connect_four.evaluation.cli --a alphabeta --b random --openings 5 --seed 2026 --depth-a 3
  ```
- **Seed:** 2026
- **Môi trường:** Windows 10/11, CPU Intel 6/154; Python 3.11.9, NumPy 2.4.6, PyTorch 2.15.0+cpu (theo `results/logs/run_manifest.csv`).
- **Thời gian chạy:** 2026-11-25 03:45:29 → 03:45:29 UTC+7 (2026-11-24 20:45:29 → 20:45:29 UTC)
- **Trạng thái:** completed
- **Log thô:**
  - `results/logs/games_alphabeta-vs-random-20261124T204529Z-s2026.csv`
  - `results/logs/moves_alphabeta-vs-random-20261124T204529Z-s2026.csv`
- **Bảng/hình liên quan:** Không tạo bảng/hình riêng.
- **Số liệu chính:** 10 ván; Alpha-Beta thắng 10, hòa 0, thua 0; score_A = 1.000. Nguồn: log ván và output CLI.
- **Nhận xét:** Alpha-Beta depth 3 thắng 10/10 ván trước Random, thời gian ra nước đi nhanh chóng và ổn định.

## mcts-vs-random-20261124T204536Z-s2026 — MCTS 200 simulations vs Random

- **Ngày:** 2026-11-25 (UTC+7)
- **Người chạy:** Bùi Anh Đức
- **Loại:** tournament
- **Mục tiêu:** Cross-check MCTS 200 simulations vs Random theo phân công nhóm 26.
- **Config:** `configs/agents.yaml` (mặc định), sims-a = 200
- **Commit:** `ba1be81`
- **Lệnh chạy:**
  ```powershell
  python -m connect_four.evaluation.cli --a mcts --b random --openings 5 --seed 2026 --sims-a 200
  ```
- **Seed:** 2026
- **Môi trường:** Windows 10/11, CPU Intel 6/154; Python 3.11.9, NumPy 2.4.6, PyTorch 2.15.0+cpu (theo `results/logs/run_manifest.csv`).
- **Thời gian chạy:** 2026-11-25 03:45:36 → 03:45:36 UTC+7 (2026-11-24 20:45:36 → 20:45:36 UTC)
- **Trạng thái:** completed
- **Log thô:**
  - `results/logs/games_mcts-vs-random-20261124T204536Z-s2026.csv`
  - `results/logs/moves_mcts-vs-random-20261124T204536Z-s2026.csv`
- **Bảng/hình liên quan:** Không tạo bảng/hình riêng.
- **Số liệu chính:** 10 ván; MCTS thắng 10, hòa 0, thua 0; score_A = 1.000. Nguồn: log ván và output CLI.
- **Nhận xét:** MCTS với ngân sách 200 simulations thắng 10/10 ván trước Random, ra nước chính xác và không vi phạm luật.

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

## ablation-a3-20261111T150514Z-s20261105 — Ablation A3: số ván huấn luyện CNN (RQ2)

- **Ngày:** 11/11/2026 (giờ Việt Nam).
- **Người chạy:** Bùi Quyền Kiệt / 3124720036.
- **Loại:** ablation.
- **Mục tiêu:** RQ2 — khi tăng số ván huấn luyện CNN từ 250 đến tối đa ván train A3 thực có, top-1 và độ chính xác theo tình huống thắng ngay / chặn / kiểm soát trung tâm thay đổi thế nào.
- **Config:** `configs/ablation_a3_cnn_data.yaml` (hash `bf81b780b50f3ccd`), `dataset_sizes_games: [250, 500, 1000, 1332]`.
- **Commit:** `0516a8e` (mã, test và config đã commit trước khi chạy).
- **Lệnh chạy:**
  ```bash
  cd Connect_Four
  PYTHONPATH=src .venv/bin/python scripts/run_ablation_a3.py \
      --config configs/ablation_a3_cnn_data.yaml
  ```
- **Seed:** 20261105 cho cả chia dữ liệu và huấn luyện.
- **Thiết kế:** cohort A3 sau chia theo ván 70/15/15 và dedupe còn 1.332 ván train / 254 ván validation / 264 ván test. Validation và test giữ cố định; mỗi mức chỉ lấy N ván train đầu tiên theo thứ tự split đã xáo trộn nên các tập con lồng nhau. Kiến trúc, optimizer, 20 epoch, batch 64, learning rate 0,001 giữ nguyên; checkpoint chọn theo validation loss thấp nhất, test đọc một lần cho mỗi lần huấn luyện.
- **Môi trường:** Python 3.14.9, NumPy 2.5.4, PyTorch 2.15.0+cu132, CPU x86_64, Linux 7.3.3, RAM 27,2 GB; không dùng GPU.
- **Thời gian (UTC):** 2026-11-11T15:05:14+00:00 → 2026-11-11T15:08:16+00:00.
- **Trạng thái:** completed.
- **Log thô:**
  - `results/logs/ablation_a3_ablation-a3-20261111T150514Z-s20261105.csv`
  - `results/logs/train_cnn_20261111T150516Z_4ead9059.csv`
  - `results/logs/train_cnn_20261111T150537Z_cde1dfc3.csv`
  - `results/logs/train_cnn_20261111T150613Z_8a36348a.csv`
  - `results/logs/train_cnn_20261111T150709Z_a9cc707c.csv`
  - `checkpoints/level5_cnn/test_evaluation_<run_id>.json` cho bốn run huấn luyện
- **Bảng/hình liên quan:** `results/tables/ablation_a3_results.csv`, `results/figures/ablation_a3_accuracy.png`, `results/figures/ablation_a3_learning_curves.png`, `notebooks/02_cnn_analysis.ipynb`.
- **Số liệu chính** (test A3: 5.012 mẫu; 321 thắng ngay, 568 chặn, 3.090 kiểm soát trung tâm, 1.033 khác):

  | Ván train | Run huấn luyện | Mẫu train | Epoch tốt nhất | Val loss | Test loss | Top-1 | Thắng ngay (tactical) | Chặn (tactical) | Trung tâm (top-1) | Trung tâm (chọn cột 3) |
  |---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
  | 250 | `20261111T150516Z_4ead9059` | 10.857 | 3 | 1,3832 | 1,3959 | 47,19% | 42,37% | 52,99% | 41,55% | 38,51% |
  | 500 | `20261111T150537Z_cde1dfc3` | 21.098 | 7 | 1,2830 | 1,3088 | 51,74% | 60,44% | 71,30% | 46,44% | 28,83% |
  | 1.000 | `20261111T150613Z_8a36348a` | 40.561 | 5 | 1,1637 | 1,1589 | 55,35% | 58,57% | 73,59% | 50,87% | 21,62% |
  | 1.332 | `20261111T150709Z_a9cc707c` | 53.284 | 5 | 1,1150 | 1,1106 | 57,08% | 59,81% | 77,64% | 52,65% | 27,57% |

  Nguồn: `results/tables/ablation_a3_results.csv` (các cột `top1_accuracy`, `win_now_situation_accuracy`, `block_situation_accuracy`, `center_control_top1_accuracy`, `center_control_situation_accuracy`).

- **Nhận xét:** Top-1 tăng 9,90 điểm phần trăm từ 250 lên 1.332 ván; thắng ngay (tactical) tăng 17,45 điểm; chặn (tactical) tăng 24,65 điểm; kiểm soát trung tâm (top-1) tăng 11,10 điểm. Chặn là tình huống cải thiện mạnh nhất. Tỷ lệ chọn đúng cột giữa giảm khi tăng dữ liệu (38,51% → 27,57%) vì mô hình học sát nhãn Alpha-Beta hơn, mà Alpha-Beta depth 4 chỉ chọn cột giữa ở khoảng 22,8% vị trí không có nước chiến thuật; vì vậy chỉ báo cáo tỷ lệ này như chẩn đoán. Trong 321 vị trí thắng ngay của test, 98 nhãn Alpha-Beta (30,5%) không phải nước thắng ngay, nên tactical accuracy mới là thước đo đúng cho `win_now`.
- **Việc tiếp theo:** lặp thêm seed/bộ chia để có khoảng tin cậy; đo win rate đối kháng trước Alpha-Beta ở hạng mục đánh giá giải đấu (ngoài phạm vi Issue #22).

## K3 — MCTS-UCT, issue #14 (11/11/2026, giờ Việt Nam)

- **Mục tiêu:** MCTS thắng Random ít nhất 95% ở 500 mô phỏng/nước.
- **Mã nguồn:** commit `4dbe441`, nhánh `feat/issue-14-mcts-uct`.
- **Lệnh:** `PYTHONPATH=src python scripts/evaluate_k3.py` trong `Connect_Four`.
- **Cấu hình:** [`configs/k3_random_mcts.json`](../configs/k3_random_mcts.json);
  200 ván, 100 khai cuộc khác nhau dài 4 nước, đổi bên từng cặp;
  seed khai cuộc/MCTS = 0, Random = 1, `c=1.414`, rollout random.
- **Run chính thức:** `k3-mcts-random-20261110T181313Z-s0`, thực hiện sau khi commit mã nguồn.
- **Kết quả:** **199 thắng, 0 hòa, 1 thua — 99,5%**, vượt ngưỡng 190/200.
- **Log thô:** [ván](../results/logs/games_k3-mcts-random-20261110T181313Z-s0.csv),
  [nước](../results/logs/moves_k3-mcts-random-20261110T181313Z-s0.csv),
  [bảng tổng hợp](../results/tables/k3-mcts-random-20261110T181313Z-s0.csv),
  [manifest và môi trường](../results/logs/run_manifest.csv).
- **Kiểm tra:** script phát lại toàn bộ 200 ván, đối chiếu bên thắng và số ván
  đi trước/đi sau; log MCTS ghi đúng 500 mô phỏng cho mỗi nước.
  Toàn bộ kiểm thử: **218 passed in 22.80s**, gồm 38 test K3;
  [log kiểm thử](../results/logs/k3_pytest_20261111.txt).
- **Lần thử trước commit:** `k3-mcts-random-20261110T181053Z-s0` cũng đạt
  199/200; giữ nguyên log và ghi rõ trong manifest rằng `9e03821` chưa chứa
  thay đổi lúc chạy. Dùng run chính thức ở trên để tái lập.
- **Giới hạn:** một bộ seed và cấu hình cố định, không bảo đảm tỷ lệ này với
  mọi khai cuộc/seed hoặc đối thủ mạnh hơn. Chưa chạy ablation A2/giải đấu M3.
  `run_id` và manifest dùng UTC; 18:13 ngày 10/11 UTC là 01:13 ngày 11/11 tại Việt Nam.
- **Giải thích thuật toán/công cụ:** [hướng dẫn MCTS](MCTS.md),
  [nhật ký đóng góp](contributions/pham-thai-duy-khang.md). Chờ review trước khi merge.


## 2026-11-13 — DQN pilot va Round-Robin pilot (Như Ý)

- **Training run_id:** `20261113_140831_508593`
- **Cau hinh:** 200 episodes; doi thu `heuristic`; seed 42; lr=0.001; gamma=0.99; epsilon 1.0 → floor 0.05 voi decay 0.9995; batch_size=64; replay capacity=100000; target sync moi 500 optimizer updates; CPU (`torch 2.10.0+cpu`, Python 3.13.5, NumPy 2.3.5).
- **Ket qua pilot:** 1 win, 0 draw, 199 losses; mean reward=-0.99; 757 optimizer updates; mean episode loss (cot `mean_loss`)≈0.004874; metadata elapsed=10.665 s; replay size=820.
- **Artifacts:** `results/logs/train_dqn_20261113_140831_508593.csv`; `checkpoints/level6_dqn/pilot/dqn_model.json`; model `.pt` giu local de kiem tra, chua phai checkpoint dong bang va khong dua vao patch GitHub giua ky.
- **Tournament run_id prefix:** `tournament-default-20261113T140850Z-s20261113`
- **Cau hinh:** 3 agents (`random`, `heuristic`, `dqn`); 20 games/pair; 10 shared openings; mode `default`; seed 20261113; total 60 games.
- **W-D-L theo agent A:** random–heuristic 0-0-20; random–DQN 6-0-14; heuristic–DQN 20-0-0. DQN (agent B) thang 14/20 truoc Random va 0/20 truoc Heuristic.
- **Artifacts:** `results/logs/games_tournament-default-20261113T140850Z-s20261113-*.csv`, cac file `moves_*.csv`, `results/tables/tournament-default-20261113T140850Z-s20261113_summary.csv`, `results/logs/run_manifest.csv`.
- **Environment:** Linux x86_64; CPU-only; `git_commit` khong co do chay tren ban ZIP khong kem thu muc `.git`; khong tu gan commit id.
- **Interpretation:** day la pilot 20 games/pair, khong dap ung nguong chinh thuc toi thieu 100 games/pair; khong dung de ket luan cuoi cung. DQN pilot chua hoc duoc chien luoc tot truoc Heuristic; can chay A4 3 decay × 3 seeds va chon checkpoint bang validation theo ke hoach truoc khi dong bang (17/11).

## K4 — A1/A2/A5, ngày 15/11/2026 (giờ Việt Nam)

- Mã chạy: `1b79dd5`; thuật toán lấy từ main `3a40170`, không thay đổi tác tử.
- A1: `ablation-a1-20261114T172315Z-s20261104`, 00:23:15–00:35:51 giờ Việt Nam.
  30 thế hoạt động × 3 độ sâu × 4 cấu hình × 5 lần = 1.800 lần đo;
  thế hòa đầy bàn ghi riêng là `excluded_terminal`.
- A5: `ablation-a5-20261114T173556Z-s20261104`, 00:35:56–00:39:56.
  450 lần đo thế và 500 ván trước Heuristic ở độ sâu 2–6.
- A2: `ablation-a2-20261114T173956Z-s20261104`, 00:39:56–00:45:54.
  500 ván trước Alpha-Beta sâu 4 ở 100/500/1000/2000/5000 mô phỏng.
- Cấu hình: các YAML `ablation_a1_pruning`, `ablation_a2_mcts_budget`,
  `ablation_a5_depth`; hash cấu hình và bộ thế ghi trong manifest.
- Khai cuộc A2/A5: 50 khai cuộc dài 4 nước, seed 20261104, đổi bên từng cặp;
  mỗi mức dùng cùng lịch RNG ván `seed + i`, i=0..99.
- Môi trường: ARM CPU, RAM 16 GB, Darwin 25.6.0, Python 3.13.7, NumPy 2.5.4;
  chạy tuần tự trên CPU. Thời gian máy không phải giờ đóng góp cá nhân.
- Kiểm tra: mọi ván phát lại bằng ReferenceGame; mọi nước MCTS đúng số mô
  phỏng; A1 giữ cùng giá trị minimax theo thế/độ sâu và giữ nguyên bàn đầu vào.
- Kết quả: bảng `results/tables/ablation_a{1,2,5}_results.csv`, bản bất biến
  theo run ID và log `positions_`, `games_`, `moves_`, `ablation_` trong
  `results/logs/`; bảng đối đầu liên kết run cha và run con theo từng mức.
- Phân tích: `scripts/analyze_search_ablations.py` kiểm tra lại các độ đo từ
  log trước khi dựng ba hình và thêm dòng vào `report_numbers.csv`.
  CI score bootstrap theo cặp khai cuộc, 10.000 lần lấy mẫu.
- Diễn giải/giới hạn: xem [mục 4.5](report/04d_ablation_tim_kiem.md).
  Giữ nguyên kết quả Alpha-Beta sâu 3 kém sâu 2; không coi tăng độ sâu luôn
  tăng sức mạnh. A2 chưa phải so sánh cùng thời gian mỗi nước. Chưa đóng băng
  số liệu toàn nhóm ngày 19/11.

## 2026-11-18 — A4, đóng băng DQN, chẩn đoán, giải đấu Round-Robin đầy đủ 

- **Quy tắc chọn checkpoint (đăng ký trước khi xem giải đấu):** mốc có validation trung bình cao nhất (Random seed 20261102, Heuristic seed 20261103, 100 ván, 4 nước khai cuộc ngẫu nhiên, DQN greedy) trong ô `default_decay` seed 0; hòa chọn mốc sớm. Kết quả: episode 10.000 (0,375). `checkpoints/level6_dqn/final.pt` + `final.json` (sha256 trong JSON). Đóng băng ngày 18/11, muộn hơn kế hoạch 17/11.
- **A4:** 3 decay (0,9990/0,9995/0,9998) × seed (0, 42, 2026) × 10.000 episode; chạy 2 tiến trình song song, `OMP_NUM_THREADS=1`. Log: `results/logs/ablation_a4_cell_*.csv`, `ablation_a4-*.csv`, `train_dqn_a4-*.csv`; bảng: `results/tables/ablation_a4_results.csv`, `ablation_a4_summary.csv`. Các run_id nằm trong `results/logs/run_manifest.csv`.
- **Ô mở rộng (không thuộc A4 gốc):** `default_decay_open4` seed 0 với `--opening-plies 4`, chạy sau chẩn đoán; không dùng để chọn checkpoint.
- **Chẩn đoán:** `scripts/diagnose_dqn_openings.py` → `results/tables/dqn_opening_diagnostic.csv` (0/2/4 nước khai cuộc ngẫu nhiên).
- **Bộ 31 vị trí:** `scripts/evaluate_positions.py` → `y6_position_choices.csv`, `y6_position_accuracy.csv`; `scripts/check_alphabeta_win_values.py` → `y6_alphabeta_root_values.csv` (Alpha-Beta bỏ lỡ 5/18 thế thắng ngay; chưa sửa, chuyển cho Khang).
- **Giải đấu mặc định:** `configs/tournament_y6_default.yaml`, seed 20261118, 200 ván/cặp, prefix `tournament-default-20261118T163224Z-s20261118`. Chạy một mình trên máy 2 nhân, `OMP_NUM_THREADS=1`.
- **Giải đấu cùng thời gian:** `configs/tournament_y6_timed.yaml`, seed 20261119, 0,2 s/nước, 100 ván/cặp, prefix `tournament-timed-20261118T164206Z-s20261119`.
- **Tổng hợp:** `scripts/summarize_tournament.py` → `results/tables/y6_<default|timed>_*.csv`, `results/figures/y6_*`; `scripts/build_report_numbers_y.py` → `results/tables/report_numbers.csv`.
- **Giải thích:** DQN thua Heuristic rõ (score Heuristic 0,912/0,880); nguyên nhân chẩn đoán là quá khớp đường chơi cố định của Heuristic khi huấn luyện từ bàn trống (xem `docs/report/04c_dqn_duong_cong.md`). Không điều chỉnh checkpoint sau khi xem giải.
- **Giới hạn:** `git_commit` trong manifest có thể là commit trước khi các thay đổi chưa commit lúc chạy được lưu; tái lập bằng commit chứa các file này.

## 2026-11-19 — Hợp nhất và kiểm tra số liệu 

- Hợp nhất công việc Y5–Y6 vào bản zip ngày 19/11 (có A1/A2/A5 của Khang). Xung đột ở nhật ký, `report_numbers.csv`, `run_manifest.csv`, 04a và hồ sơ đóng góp được giải bằng cách giữ cả hai phía; dòng của Ý được dựng lại bằng `scripts/build_report_numbers_y.py` (idempotent).
- Kiểm tra `report_numbers.csv`: 1.219 dòng, không trùng (`report_section`, `metric`), mọi dòng có `run_id`. 32 dòng mục 3.4 (Kiệt) trỏ tới `data/generated/`, thư mục không commit theo kế hoạch. Sửa đường dẫn sai của 7 dòng pilot DQN (`train_dqn_train_dqn_…` → `train_dqn_…`).
- Mục báo cáo 4.7 (`docs/report/04h_thao_luan.md`) và slide `docs/slides/y.pptx` đã soạn nháp từ các bảng ở trên; không có thí nghiệm mới.
- Không chạy lại giải đấu hay A4; số liệu giữ nguyên bộ ngày 18/11.

## 2026-11-20 — A6: đối thủ huấn luyện DQN (Heuristic / Random / tự chơi), mở rộng cho RQ3 

- **Mục tiêu:** trả lời phần "tự chơi" và "đối thủ huấn luyện" của RQ3, phần A4 chưa đo.
- **Thời điểm:** chạy sau khi checkpoint giải đấu đã đóng băng (18/11) và sau giải đấu; không dùng để chọn checkpoint, không đổi số liệu mục 4.1–4.3.
- **Cấu hình:** `configs/ablation_a6_dqn_opponent.yaml`; siêu tham số như A4 `default_decay` (lr 0,001, γ 0,99, ε 1,0 → 0,05 decay 0,9995, buffer 100.000, batch 64, target 500); 10.000 episode; seed 0 / 42 / 2026. Tự chơi: tập 5 bản sao đóng băng của chính mạng, chép mỗi 500 episode. Ô Heuristic dùng lại 3 ô A4 `default_decay`.
- **Lệnh:** `PYTHONPATH=src python scripts/run_ablation_a6.py --opponent <random|selfplay> --seed <s>` (2 tiến trình song song, `OMP_NUM_THREADS=1`), rồi `--merge`, `scripts/summarize_a6.py`, `scripts/build_report_numbers_y.py`, `scripts/render_report_tables_y.py`.
- **Đánh giá:** như A4 (seed validation 20261102/20261103, 100 ván/đối thủ/mốc); thêm 100 ván gặp `final.pt` (seed 20261104) và bộ vị trí `tests/data/positions.csv` ở mốc 10.000.
- **Môi trường:** máy 2 nhân CPU x86_64 Linux, Python 3.13, PyTorch 2.15 CPU; mỗi ô 2.022–2.211 giây.
- **Sự cố:** máy khởi động lại khi hai ô đầu đang chạy (~1.700 episode); hai lần chạy dở bị xóa (không có run_id hoàn tất nào bị mất) và chạy lại từ đầu sau khi thêm `resume_every` vào `train_dqn` (lưu trạng thái mỗi 250 episode).
- **run_id:** `a6-opp_random-s0-20261120T132502Z`, `a6-opp_selfplay-s0-20261120T132501Z`, `a6-opp_selfplay-s42-20261120T135944Z`, `a6-opp_selfplay-s2026-20261120T140154Z`, `a6-opp_random-s42-20261120T143551Z`, `a6-opp_random-s2026-20261120T143811Z`.
- **Kết quả (gộp 3 seed, mốc 10.000):** tự chơi 0,568 gặp Random, 0,003 gặp Heuristic, 0,418 gặp `final.pt`; đối thủ Random 0,578 / 0,010 / 0,393; đối thủ Heuristic (A4) 0,662 / 0,162. Bảng: `results/tables/ablation_a6_*.csv`; hình: `results/figures/ablation_a6_*.png`; diễn giải: `docs/report/04f_ablation_dqn.md` (A6), `04h_thao_luan.md` (4.7.3, 4.7.6).
- **Không commit:** các file `.pt` mốc của A6 (đã chặn bởi `.gitignore`, mỗi file ~4,6 MB); chỉ commit JSON metadata.

## ablation-a1-20261124T181149Z-s20261104 — A1: Cắt tỉa Alpha-Beta

- **Ngày:** 25/11/2026, giờ Việt Nam (UTC+7).
- **Người chạy:** Phạm Thái Duy Khang / 3124720033.
- **Loại và mục tiêu:** ablation, RQ3. Đo ảnh hưởng của cắt tỉa và sắp xếp nước đi ở độ sâu 4, 5 và 6.
- **Config và commit:** `configs/ablation_a1_pruning.yaml`, `57991d3`.
- **Lệnh chạy:** `PYTHONPATH=src python scripts/run_search_ablations.py --experiment a1`.
- **Seed:** `20261104`.
- **Môi trường:** CPU ARM, RAM 16 GB, Python 3.13.7, NumPy 2.5.4, PyTorch 2.15.0.
- **Thời gian chạy:** 01:11:49 → 01:20:53 (9 phút 04 giây).
- **Trạng thái:** `completed`.
- **Log thô:** `results/logs/positions_ablation-a1-20261124T181149Z-s20261104.csv`.
- **Bảng kết quả:** `results/tables/ablation-a1-20261124T181149Z-s20261104.csv`.
- **Số liệu chính:** Ở `depth=6`, khi chuyển từ tắt cả hai sang bật cả cắt tỉa và sắp xếp, `mean_nodes` giảm từ 58.678 xuống 2.697,1 và `mean_ms` giảm từ 1.418,29 xuống 55,55 ms.
- **Nhận xét:** Bật cả hai kỹ thuật giảm khoảng 95,4% số nút duyệt trung bình ở độ sâu 6 trên tập thế cờ đo.

## ablation-a5-20261124T185729Z-s20261104 — A5: Độ sâu Alpha-Beta

- **Ngày:** 25/11/2026, giờ Việt Nam (UTC+7).
- **Người chạy:** Phạm Thái Duy Khang / 3124720033.
- **Loại và mục tiêu:** ablation, RQ3. Đo tỷ lệ thắng và chi phí tìm kiếm ở độ sâu 2–6 khi gặp Heuristic, 100 ván mỗi độ sâu.
- **Config và commit:** `configs/ablation_a5_depth.yaml`, `57991d3`.
- **Lệnh chạy:** `PYTHONPATH=src python scripts/run_search_ablations.py --experiment a5`.
- **Seed:** `20261104`.
- **Môi trường:** CPU ARM, RAM 16 GB, Python 3.13.7, NumPy 2.5.4, PyTorch 2.15.0.
- **Thời gian chạy:** 01:57:29 → 02:00:20 (2 phút 51 giây).
- **Trạng thái:** `completed`.
- **Log thô:** `results/logs/positions_ablation-a5-20261124T185729Z-s20261104.csv`. Đường dẫn log ván và log nước đi của cả 5 độ sâu nằm ở các cột `raw_log_path` và `moves_log_path` của các dòng `phase=games` trong bảng kết quả bên dưới.
- **Bảng kết quả:** `results/tables/ablation-a5-20261124T185729Z-s20261104.csv`.
- **Số liệu chính:** Theo `phase=games`, `win_rate` ở độ sâu 2–6 lần lượt là 72%, 57%, 79%, 79% và 80%. `mean_ms` ở độ sâu 4 và 6 lần lượt là 9,00 và 100,89 ms mỗi nước.
- **Nhận xét:** Từ độ sâu 4 lên 6, tỷ lệ thắng tăng 1 điểm phần trăm, trong khi thời gian trung bình mỗi nước tăng khoảng 11,2 lần.

## alphabeta-vs-mcts-20261124T190359Z-s42 — Alpha-Beta vs MCTS, lượt đối chiếu

- **Ngày:** 25/11/2026, giờ Việt Nam (UTC+7).
- **Người chạy:** Phạm Thái Duy Khang / 3124720033.
- **Loại và mục tiêu:** tournament, K2/K3. Đối chiếu Alpha-Beta độ sâu 4 với MCTS 500 mô phỏng, 5 khai cuộc và 10 ván đổi bên.
- **Config và commit:** `configs/agents.yaml`, `57991d3`.
- **Lệnh chạy:** `PYTHONPATH=src python -m connect_four.evaluation.cli --a alphabeta --b mcts --openings 5 --seed 42 --depth-a 4 --sims-b 500`.
- **Seed:** `42`.
- **Môi trường:** CPU ARM, RAM 16 GB, Python 3.13.7, NumPy 2.5.4, PyTorch 2.15.0.
- **Thời gian chạy:** 02:03:57 → 02:03:59.
- **Trạng thái:** `completed`.
- **Log ván:** `results/logs/games_alphabeta-vs-mcts-20261124T190359Z-s42.csv`.
- **Log nước đi:** `results/logs/moves_alphabeta-vs-mcts-20261124T190359Z-s42.csv`.
- **Số liệu chính:** Alpha-Beta thắng 6, hòa 1, thua 3. Điểm `score_A` là 0,650, tính từ cột `winner` của log ván.
- **Nhận xét:** Kết quả thắng–hòa–thua của từng ván trùng với lượt `190429Z` khi đối chiếu theo khai cuộc và bên đi trước.

## alphabeta-vs-mcts-20261124T190429Z-s42 — Alpha-Beta vs MCTS, kết quả chính

- **Ngày:** 25/11/2026, giờ Việt Nam (UTC+7).
- **Người chạy:** Phạm Thái Duy Khang / 3124720033.
- **Loại và mục tiêu:** tournament, K2/K3. Đối chiếu Alpha-Beta độ sâu 4 với MCTS 500 mô phỏng, 5 khai cuộc và 10 ván đổi bên.
- **Config và commit:** `configs/agents.yaml`, `57991d3`.
- **Lệnh chạy:** `PYTHONPATH=src python -m connect_four.evaluation.cli --a alphabeta --b mcts --openings 5 --seed 42 --depth-a 4 --sims-b 500`.
- **Seed:** `42`.
- **Môi trường:** CPU ARM, RAM 16 GB, Python 3.13.7, NumPy 2.5.4, PyTorch 2.15.0.
- **Thời gian chạy:** 02:04:27 → 02:04:29.
- **Trạng thái:** `completed`.
- **Log ván:** `results/logs/games_alphabeta-vs-mcts-20261124T190429Z-s42.csv`.
- **Log nước đi:** `results/logs/moves_alphabeta-vs-mcts-20261124T190429Z-s42.csv`.
- **Số liệu chính:** Alpha-Beta thắng 6, hòa 1, thua 3 theo cột `winner` của log ván. Tỷ lệ thắng là 60%, `score_A = (6 + 0,5 × 1) / 10 = 0,650`.
- **Nhận xét:** Alpha-Beta đạt 6,5/10 điểm theo cấu hình và tập khai cuộc của lượt này. Báo cáo kết quả chính với cỡ mẫu 10 ván.