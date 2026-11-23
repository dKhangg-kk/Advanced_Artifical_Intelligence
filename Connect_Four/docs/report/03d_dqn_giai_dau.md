# 3.5. Tác tử Deep Q-Network (cấp 6) và 3.6. Thiết kế giải đấu công bằng

Mục này mô tả thiết kế và cài đặt đã dùng cho bản cuối kỳ. Lý thuyết nằm ở mục 2.4
(`02c_hoc_tang_cuong.md`); số liệu huấn luyện, giải đấu và ablation nằm ở Chương 4
(mục 4.1–4.5, 4.7). Mã nguồn: `src/connect_four/agents/dqn.py`,
`src/connect_four/agents/networks.py` (lớp `DQNNet`),
`src/connect_four/training/train_dqn.py`, `src/connect_four/evaluation/cli.py`,
`src/connect_four/evaluation/config.py`.

## 3.5.1. Mô hình hóa bài toán học tăng cường

| Thành phần | Cài đặt trong đồ án |
| --- | --- |
| Trạng thái `s` | Tensor 2×6×7 từ `game.to_array()`: kênh 0 là quân của bên đang đến lượt, kênh 1 là quân đối thủ. Vì luôn nhìn từ góc của bên đang đi, cùng một mạng dùng được khi DQN đi trước hay đi sau. |
| Hành động `a` | Một trong 7 cột; chỉ các cột chưa đầy là hợp lệ. |
| Phần thưởng `r` | Chỉ ở cuối ván, theo góc nhìn DQN: thắng +1, hòa 0, thua −1; mọi bước giữa ván nhận 0. |
| Trạng thái kế `s'` | Bàn cờ **sau khi đối thủ đã đáp lại**, tức là lượt DQN kế tiếp. Nếu nước của DQN kết thúc ván thì lưu transition kết thúc ngay, không chờ đối thủ. |
| Kết thúc | `done = True` khi có người thắng hoặc bàn đầy; khi đó mục tiêu là `y = r`, không bootstrap. |
| Episode | Một ván. Bên đi trước đổi luân phiên: episode lẻ DQN đi trước, episode chẵn DQN đi sau. |

Chốt transition sau lượt đáp của đối thủ là điểm quan trọng nhất của cài đặt. Nếu lấy
`s'` ngay sau nước của DQN thì `s'` là lượt của đối thủ, và `max Q(s')` sẽ đánh giá bàn
cờ theo góc nhìn sai.

## 3.5.2. Mạng `DQNNet` và chọn nước hợp lệ

`DQNNet` nhận tensor `(B, 2, 6, 7)` và trả về 7 giá trị Q:

```text
Conv2d(2→64, 3×3, padding 1) → ReLU → Conv2d(64→64, 3×3, padding 1) → ReLU
→ Flatten (64·6·7 = 2.688) → Linear(2.688→128) → ReLU → Linear(128→7)
```

Mạng có 383.239 tham số; file trọng số đóng băng `checkpoints/level6_dqn/final.pt`
khoảng 1,5 MB.

`DQNAgent.choose()` nạp checkpoint ở lần gọi đầu tiên (lazy-load), suy luận Q trên
`game.to_array()`, đặt `−∞` cho cột đầy rồi lấy `argmax` (hàm `mask_q_values`). Khi thi
đấu và đánh giá, `ε = 0`. Agent không thay đổi đối tượng `game` truyền vào và ghi thời
gian suy luận vào `last_stats`. Nhờ mặt nạ, agent không bao giờ chọn cột đầy, kể cả khi
trọng số còn ngẫu nhiên hoặc chỉ còn một cột hợp lệ (có test riêng).

## 3.5.3. Replay Buffer, Target Network và vòng huấn luyện

- **Replay Buffer** (`ReplayBuffer`): FIFO tối đa 100.000 transition. Mỗi transition lưu
  `state, action, reward, next_state, done` và **mặt nạ cột hợp lệ của `next_state`**.
  Khi đầy, mẫu cũ nhất bị ghi đè; batch được lấy ngẫu nhiên không hoàn lại.
- **Mục tiêu Bellman có mặt nạ**: `y = r + γ · max_{a' hợp lệ} Q_target(s', a')`; cột
  không hợp lệ bị đặt `−∞` trước phép `max`. Với transition kết thúc, `y = r`.
- **Target Network**: bản sao của mạng trực tuyến, đồng bộ sau mỗi 500 lần cập nhật
  optimizer; giữa hai lần đồng bộ mục tiêu đứng yên.
- **Hàm mất mát và tối ưu**: Huber (`smooth_l1_loss`), Adam. Mỗi khi có transition mới và
  buffer đủ một batch thì cập nhật một bước.
- **Thăm dò**: epsilon-greedy giảm theo episode, `ε_e = max(0,05; 1,0 · decay^e)`.

Siêu tham số của mô hình chính (lấy từ `checkpoints/level6_dqn/final.json`):

| Tham số | Giá trị |
| --- | --- |
| Đối thủ huấn luyện | Heuristic (cấp 2), bắt đầu từ bàn trống |
| Số episode | 10.000 |
| Learning rate (Adam) | 0,001 |
| γ | 0,99 |
| ε: bắt đầu / sàn / decay | 1,0 / 0,05 / 0,9995 mỗi episode (chạm sàn ở khoảng episode 6.000) |
| Replay Buffer / batch | 100.000 / 64 |
| Đồng bộ Target Network | mỗi 500 cập nhật |
| Seed | 0 |
| Thiết bị | CPU, 1 luồng PyTorch |

Mỗi lần chạy ghi log từng episode vào `results/logs/train_dqn_<run_id>.csv` (kết quả,
thưởng, ε, loss trung bình, số cập nhật, cỡ buffer, thời gian) và lưu checkpoint ở 1.000 /
2.500 / 5.000 / 10.000 episode kèm JSON metadata (commit, siêu tham số, seed, phiên bản
Python/PyTorch, phần cứng, thời gian huấn luyện). Từ bản cuối kỳ, `train_dqn` có thêm tùy
chọn `resume_every`: lưu toàn bộ trạng thái (hai mạng, optimizer, Replay Buffer, mọi bộ
sinh số ngẫu nhiên) để chạy tiếp sau khi máy khởi động lại. Test
`test_train_dqn_resume_after_crash_matches_uninterrupted_run` kiểm tra rằng chạy tiếp cho
log và trọng số giống hệt chạy liền một mạch.

## 3.5.4. Ba loại đối thủ huấn luyện

`train_dqn(opponent=...)` hỗ trợ ba loại đối thủ, cùng một vòng lặp, cùng cách tính thưởng
và chốt transition:

1. **Đối thủ cố định `heuristic` hoặc `random`.** Mỗi episode tạo đối thủ với seed
   `seed + episode`. Đây là cách huấn luyện của mô hình chính và của A4.
2. **Khai cuộc ngẫu nhiên** (`opening_plies`, ví dụ 4). Trước mỗi episode đặt sẵn vài nước
   ngẫu nhiên hợp lệ; các nước này không sinh transition cho DQN. Dùng cho ô mở rộng sau chẩn
   đoán ở mục 4.5.
3. **Tự chơi (`selfplay`).** Đối thủ là **bản sao đóng băng của chính mạng đang học**,
   quản lý bởi `SelfPlayOpponentPool`: bản đầu tiên là trọng số khởi tạo; sau mỗi 500
   episode, trọng số hiện tại được chép thành một bản mới; chỉ giữ 5 bản gần nhất; mỗi
   episode lấy ngẫu nhiên một bản. Đối thủ chọn nước epsilon-greedy với cùng ε của episode
   và cũng dùng mặt nạ cột hợp lệ. Chỉ mạng đang học nhận gradient. Giữ nhiều phiên bản cũ
   thay vì đấu với mạng vừa cập nhật giúp môi trường ít dao động hơn và giảm hiện tượng
   "quên" cách thắng các lối chơi cũ (mục 2.4.4). Log ghi thêm cột
   `opponent_snapshot_episode` để biết mỗi ván gặp phiên bản nào.

## 3.5.5. Chọn và đóng băng checkpoint

Quy tắc được đăng ký trước khi chạy giải đấu: trong 4 mốc của ô A4 `default_decay` seed 0,
chọn mốc có điểm validation trung bình cao nhất, trong đó điểm validation là trung bình của
score gặp Random và score gặp Heuristic, mỗi đối thủ 100 ván. Validation dùng seed riêng:
20261102 cho Random và 20261103 cho Heuristic. Nếu bằng điểm, chọn mốc sớm hơn. DQN đánh giá
ở chế độ greedy, khai cuộc 4 nước ngẫu nhiên, đổi bên. Kết quả chọn mốc 10.000 episode (mục 4.4).
`scripts/freeze_dqn_checkpoint.py` chép trọng số (bỏ trạng thái optimizer) thành
`checkpoints/level6_dqn/final.pt` và ghi `final.json` gồm quy tắc chọn, bảng validation,
sha256 của file nguồn và file đóng băng, commit, phần cứng. Giải đấu chỉ nạp file đóng băng
này (`configs/agents_y6.yaml`). Việc đóng băng làm ngày 18/11/2026, muộn một ngày so với kế
hoạch (17/11), nhưng trước khi chạy giải đấu.

## 3.5.6. Thiết kế thí nghiệm A4 và A6

- **A4: lịch giảm ε × seed** (`configs/ablation_a4_dqn_training.yaml`,
  `scripts/run_ablation_a4.py`). Ba mức decay 0,9990 / 0,9995 / 0,9998 (chạm sàn 0,05 ở
  khoảng 3.000 / 6.000 episode; mức chậm nhất chưa chạm sàn ở 10.000), ba seed 0 / 42 / 2026,
  đều gặp Heuristic. Đánh giá ở 4 mốc, mỗi mốc 100 ván với Random và 100 ván với Heuristic
  trên hai seed validation ở trên.
- **A6: đối thủ huấn luyện (mở rộng cho RQ3)** (`configs/ablation_a6_dqn_opponent.yaml`,
  `scripts/run_ablation_a6.py`). Giữ nguyên siêu tham số của ô A4 `default_decay`, chỉ đổi
  đối thủ: Heuristic (dùng lại ba ô A4, không chạy lại), Random và tự chơi. Đánh giá giống hệt
  A4. Ở mốc 10.000 thêm hai phép đo: 100 ván đấu trực tiếp với checkpoint đóng băng
  `final.pt` (seed 20261104, khác seed validation và seed giải đấu) và độ đúng trên bộ vị trí
  kiểm thử `tests/data/positions.csv`. A6 chạy **sau** khi checkpoint giải đấu đã đóng băng
  và giải đấu đã xong, nên không được dùng để chọn checkpoint hay sửa kết quả mục 4.1–4.3.

## 3.6. Thiết kế giải đấu công bằng

### 3.6.1. Tổ chức Round-Robin

- 6 tác tử (Random, Heuristic, Alpha-Beta, MCTS, CNN, DQN), 15 cặp. Tham số mỗi tác tử lấy
  từ `configs/agents_y6.yaml`, không viết cứng trong mã: Alpha-Beta độ sâu 5 (bật cắt tỉa và
  sắp xếp nước), MCTS 1.000 mô phỏng (c = 1,414, rollout ngẫu nhiên), CNN và DQN dùng
  checkpoint đóng băng.
- **Khai cuộc**: mỗi khai cuộc là 4 nước ngẫu nhiên hợp lệ, các khai cuộc trong một lần chạy
  khác nhau đôi một, và mọi cặp dùng chung một bộ khai cuộc sinh từ seed của giải. Số nước
  khai cuộc chẵn nên sau khai cuộc luôn đến lượt bên được xếp đi trước.
- **Đổi bên**: mỗi khai cuộc được chơi hai ván, A đi trước rồi B đi trước. Như vậy số ván đi
  trước của hai bên bằng nhau và lợi thế đi trước được đo riêng (cột `a_starts`).
- Hai tác tử tất định (ví dụ CNN gặp DQN) vẫn cho các ván khác nhau nhờ khai cuộc khác nhau.

### 3.6.2. Hai chế độ ngân sách

| Chế độ | Cấu hình | Ván/cặp | Seed | Ý nghĩa |
| --- | --- | ---: | ---: | --- |
| Mặc định | `configs/tournament_y6_default.yaml` | 200 (100 khai cuộc × 2) | 20261118 | Mỗi tác tử dùng tham số công bố của mình |
| Cùng thời gian | `configs/tournament_y6_timed.yaml` | 100 (50 khai cuộc × 2) | 20261119 | Alpha-Beta và MCTS dùng `Budget(time_s = 0,2)` mỗi nước (lặp sâu dần / mô phỏng đến hết giờ) |

Ngân sách 0,2 giây/nước được chọn thay cho 1,0 giây theo ước tính thời gian chạy trong kế
hoạch nhóm: với 1,0 giây/nước một chế độ cần khoảng 10 giờ, với 0,2 giây khoảng 2 giờ. Chế độ cùng thời gian
chạy 100 ván/cặp theo phương án cắt giảm số 3 của kế hoạch, vẫn đạt mức tối thiểu 100
ván/cặp của đề. Tác tử không tìm kiếm (Random, Heuristic, CNN, DQN) dùng dưới 1 ms/nước nên
không bị ảnh hưởng. Bộ chạy trận **không ngắt** nước đi quá giờ mà đánh dấu
`over_budget_a/b` cho ván có ít nhất một nước vượt ngân sách; tỷ lệ này được báo cáo riêng ở
mục 4.3. `configs/tournament_default.yaml` và `tournament_timed.yaml` là bản rút gọn trỏ
cùng tham số với hai tệp trên.

### 3.6.3. Chỉ số và thống kê

- Thắng/hòa/thua của từng cặp và từng tác tử; `score = (W + 0,5·D) / N`.
- Khoảng tin cậy Wilson 95% cho score (`evaluation/metrics.py`). Wilson được chọn thay cho
  `p ± 1,96·SE` vì nhiều cặp có tỷ lệ gần 0 hoặc 1 (ví dụ 200/200), nơi khoảng chuẩn cho độ
  rộng bằng 0 hoặc vượt ra ngoài [0; 1].
- Thời gian mỗi nước: trung bình, p95 và lớn nhất, đo bằng `time.perf_counter()` quanh
  `choose()`; số nút (Alpha-Beta, Heuristic) và số mô phỏng (MCTS) mỗi nước.
- Lợi thế đi trước: score của bên đi trước theo từng cặp và gộp toàn giải.
- Độ đúng chiến thuật trên 31 vị trí kiểm thử (thắng ngay, chặn, đòn kép, thế yên).

### 3.6.4. Tách seed và kiểm soát môi trường

| Mục đích | Seed |
| --- | --- |
| Validation chọn checkpoint DQN (gặp Random / Heuristic) | 20261102 / 20261103 |
| Đấu trực tiếp với checkpoint đóng băng trong A6 | 20261104 |
| Giải đấu mặc định / cùng thời gian | 20261118 / 20261119 |

Không seed nào dùng cho cả chọn mô hình và đánh giá cuối. Giải đấu chạy trên một máy 2 nhân
CPU, `OMP_NUM_THREADS=1`, không chạy huấn luyện song song trong lúc giải đang chạy để số đo
thời gian có ý nghĩa; thông tin CPU, hệ điều hành, phiên bản Python, NumPy, PyTorch được ghi
trong `results/logs/run_manifest.csv`.

### 3.6.5. Ghi log và truy vết

`python -m connect_four.evaluation.cli --config <tệp giải>` chạy toàn bộ vòng tròn;
`--a alphabeta --b mcts --openings 5` chạy một cặp. CLI ghi **ngay sau mỗi cặp** các tệp
`games_<run_id>.csv` (mỗi ván một dòng: cặp, bên đi trước, khai cuộc, chuỗi nước, người thắng,
thời gian trung bình/p95, số nút/mô phỏng, cờ vượt ngân sách), `moves_<run_id>.csv` (mỗi nước
một dòng) và một dòng trong `run_manifest.csv`. Nếu máy dừng giữa chừng, các cặp đã xong vẫn
còn, lần chạy dở được ghi `status=partial` và phần còn lại chạy bằng `run_id` mới. Bảng và
hình được dựng lại từ log thô bằng `scripts/summarize_tournament.py` và
`notebooks/01_tournament_analysis.ipynb`. Mọi con số dùng trong Chương 4 có một dòng trong
`results/tables/report_numbers.csv` trỏ về `run_id` và đường dẫn log.

## 3.5–3.6. Bằng chứng kiểm thử

- `tests/test_dqn.py`: Replay Buffer (FIFO, cỡ batch, sao chép mảng, mặt nạ rỗng chỉ khi kết
  thúc), lịch ε, mặt nạ Q, DQNAgent (lazy-load, không sửa game, không chọn cột đầy), vòng huấn
  luyện, khai cuộc ngẫu nhiên, tự chơi (bản sao đóng băng, giới hạn tập đối thủ, log phiên
  bản đối thủ) và chạy tiếp sau khi dừng.
- `tests/test_cli.py`: đọc cấu hình, ghi đè ngân sách thời gian, chạy một cặp và Round-Robin
  với Random hai bên.
- `tests/test_y_scripts.py`: chọn mốc checkpoint, tổng hợp giải đấu và A4, bảng
  `report_numbers.csv`, độ đúng vị trí của A6.
