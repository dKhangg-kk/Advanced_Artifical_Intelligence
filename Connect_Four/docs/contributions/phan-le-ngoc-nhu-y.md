# Đóng góp của Phan Lê Ngọc Như Ý (3124720079)

## Nhật ký

| Ngày | Việc đã làm | Issue/PR/commit | Giờ |
| --- | --- | --- | --- |
| 08–10/11/2026 | Xây dựng ReplayBuffer FIFO, EpsilonSchedule, mặt nạ cột hợp lệ và DQN Agent | [PR #59](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/59), nhánh `feat/nhu-y-y1-y2` | Chưa ghi nhận |
| 11–13/11/2026 | Hoàn thiện vòng huấn luyện DQN, Target Network, Bellman Target có mask, Huber Loss, lưu checkpoint và log | [PR #64](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/64) | Chưa ghi nhận |
| 12–13/11/2026 | Xây dựng Tournament CLI, cấu hình YAML, kiểm thử và chạy pilot DQN/Round-Robin | [PR #75](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/75), nhánh `feat/nhu-y-y4-cli-tournament-pilot` | Chưa ghi nhận |
| 13/11/2026 | Chạy kiểm thử toàn dự án và bổ sung log, bảng, hình, notebook phân tích pilot | [PR #75](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/75), run `20261113_140831_508593` | Chưa ghi nhận |
| Đến 15/11/2026 | Hoàn thiện phần báo cáo giữa kỳ về DQN cấp 6 và thiết kế giải đấu | `docs/report/03d_dqn_giai_dau.md`, [PR #75](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/75) | Chưa ghi nhận |

Các PR #59, #64 và #75 đã được merge vào `main`. Chưa có số Issue riêng được ghi nhận cho các mục Y1–Y6; không tự bổ sung mã Issue hoặc thời lượng chưa xác nhận.

## Công cụ hỗ trợ

Python, NumPy, PyTorch, PyYAML, pytest, Jupyter Notebook, pandas, Matplotlib, Git và GitHub. ChatGPT được dùng hỗ trợ rà soát yêu cầu, cấu trúc triển khai và diễn giải kiểm thử; mã nguồn, kết quả chạy và số liệu cần được người thực hiện tự kiểm tra và chịu trách nhiệm.

Thời gian đóng góp cá nhân chưa được ghi nhận; tác giả bổ sung theo thời lượng thực tế, không suy ra từ thời gian chạy tự động.

## Nhật ký Y1 — ReplayBuffer, EpsilonSchedule và Action Mask

| Ngày | Việc | Dẫn chứng | Giờ |
| --- | --- | --- | --- |
| 08/11/2026 | Xây dựng ReplayBuffer FIFO tối đa 100.000 transition; bổ sung lịch epsilon từ 1.0 với mức sàn 0.05; lưu mặt nạ cột hợp lệ của trạng thái kế tiếp | [PR #59](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/59) | Chưa ghi nhận |

- Tệp: `src/connect_four/training/train_dqn.py` (ReplayBuffer, EpsilonSchedule), `src/connect_four/agents/dqn.py` (Action Mask), `tests/test_dqn.py`.
- ReplayBuffer thay thế transition cũ nhất khi đầy và lấy mẫu ngẫu nhiên không hoàn lại.
- Mỗi transition lưu `next_legal_mask`; cột đã đầy bị loại khỏi lựa chọn hành động và phép lấy max Q ở bước mục tiêu.
- Kiểm thử các thành phần lõi không phụ thuộc việc import PyTorch ở cấp module.
- Trạng thái: phần DQN Core nằm trong PR #59, đã merge vào `main`.

## Nhật ký Y2 — DQN Agent

| Ngày | Việc | Dẫn chứng | Giờ |
| --- | --- | --- | --- |
| 09–10/11/2026 | Hoàn thiện DQNAgent, nạp checkpoint ở lần gọi đầu, chuyển trạng thái bàn cờ sang đầu vào mạng và chỉ chọn cột hợp lệ | [PR #59](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/59), commit đầu nhánh `feat/nhu-y-y1-y2` | Chưa ghi nhận |

- Tệp: `src/connect_four/agents/dqn.py`, lớp `DQNNet` trong `src/connect_four/agents/networks.py`, `tests/test_dqn.py`.
- Đầu vào mạng có dạng `2×6×7`, biểu diễn quân của người đang đi và quân đối thủ.
- Agent dùng `game.to_array()`, lấy các hành động hợp lệ, che Q-value ở cột đầy trước `argmax`; epsilon khi thi đấu bằng 0.
- Kiểm tra agent không làm thay đổi trạng thái game và không chọn cột đầy, kể cả khi chỉ còn một cột hợp lệ.
- Trạng thái: PR #59 đã merge vào `main`.

## Nhật ký Y3 — Vòng huấn luyện DQN

| Ngày | Việc | Dẫn chứng | Giờ |
| --- | --- | --- | --- |
| 11–13/11/2026 | Hoàn thiện vòng huấn luyện DQN, cơ chế cập nhật mạng mục tiêu, mục tiêu Bellman có Action Mask, Huber Loss và lưu log/checkpoint | [PR #64](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/64) | Chưa ghi nhận |

- Tệp: `src/connect_four/training/train_dqn.py`, `configs/dqn_training_pilot.yaml`, `tests/test_dqn.py`.
- Mỗi episode là một ván; luân phiên bên đi trước. Phần thưởng cuối ván theo góc nhìn DQN: thắng +1, hòa 0, thua −1.
- Transition được lưu sau khi đối thủ đáp lại để trạng thái kế tiếp là bàn cờ ở lượt DQN tiếp theo.
- Dùng Target Network, Huber Loss và Bellman Target chỉ xét những hành động hợp lệ; đồng bộ Target Network mỗi 500 optimizer updates trong cấu hình pilot đã ghi nhận.
- Lưu log CSV theo episode và checkpoint kèm JSON metadata.
- Trạng thái: PR #64 đã merge vào `main`.

### Pilot huấn luyện đã ghi nhận

- Run ID: `20261113_140831_508593`.
- Cấu hình: 200 episode, đối thủ Heuristic, seed 42, chạy CPU.
- Kết quả: 1 thắng, 0 hòa, 199 thua; mean reward = −0.99; 757 optimizer updates.
- Đây là pilot để xác nhận pipeline huấn luyện và ghi log, **không phải bằng chứng DQN đã hội tụ hoặc đạt hiệu suất tốt**.
- Dẫn chứng: `results/logs/train_dqn_20261113_140831_508593.csv`, `checkpoints/level6_dqn/pilot/dqn_model.json`, `docs/EXPERIMENT_LOG.md`.

## Nhật ký Y4 — Tournament CLI và cấu hình giải đấu

| Ngày | Việc | Dẫn chứng | Giờ |
| --- | --- | --- | --- |
| 12–13/11/2026 | Xây dựng cấu hình YAML và CLI để chạy đối đầu từng cặp hoặc Round-Robin; ghi log trận, nước đi và manifest | [PR #75](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/75) | Chưa ghi nhận |

- Tệp: `src/connect_four/evaluation/config.py`, `src/connect_four/evaluation/cli.py`, `configs/agents_dqn_pilot.yaml`, `configs/tournament_dqn_pilot.yaml`, `tests/test_cli.py`.
- Đọc cấu hình tác tử và giải đấu từ YAML, tránh hard-code tham số.
- Hỗ trợ chạy một cặp tác tử và vòng tròn Round-Robin.
- Ghi `games_<run_id>.csv`, `moves_<run_id>.csv` và `run_manifest.csv`; lưu theo từng cặp để có thể nhận diện lần chạy chưa hoàn tất.
- Bổ sung kiểm thử CLI; PR #75 đã merge vào `main`.

## Nhật ký Y5 — Ablation A4 và lựa chọn checkpoint

| Ngày dự kiến | Việc được phân công | Tệp/kết quả dự kiến | Trạng thái tại 15/11/2026 |
| --- | --- | --- | --- |
| 14–17/11/2026 | So sánh các mức Epsilon Decay và Random Seed; đánh giá checkpoint theo Validation trước khi đóng băng mô hình | `configs/ablation_a4_dqn_training.yaml`, `notebooks/01_dqn_analysis.ipynb`, `checkpoints/level6_dqn/` | Chưa có minh chứng hoàn thành đầy đủ trong nhật ký đã kiểm tra |

- Kế hoạch phân công: 3 mức decay × 3 seed (0, 42, 2026); theo dõi kết quả tại các mốc episode và đánh giá riêng với Random/Heuristic.
- Chọn checkpoint theo Validation, không dùng kết quả giải đấu cuối để điều chỉnh siêu tham số.
- Chỉ cập nhật trạng thái hoàn thành khi có đủ cấu hình, log ablation, kết quả đánh giá và metadata checkpoint.

## Nhật ký Y6 — Giải đấu, số liệu và phân tích

| Ngày | Việc | Dẫn chứng | Giờ |
| --- | --- | --- | --- |
| 13/11/2026 | Chạy pilot Round-Robin 3 tác tử, 20 ván mỗi cặp; lưu CSV, manifest và bảng tổng hợp | [PR #75](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/75), run prefix `tournament-default-20261113T140850Z-s20261113` | Chưa ghi nhận |

- Pilot gồm Random, Heuristic và DQN; 3 cặp × 20 ván = 60 ván, 10 khai cuộc dùng chung, seed 20261113.
- Kết quả pilot theo góc nhìn từng cặp: Random–Heuristic (0–0–20); Random–DQN (6–0–14, DQN thắng 14/20); Heuristic–DQN (20–0–0, DQN thua 20/20).
- Tệp minh chứng: `results/logs/games_*.csv`, `results/logs/moves_*.csv`, `results/logs/run_manifest.csv`, `results/tables/tournament-default-20261113T140850Z-s20261113_summary.csv`.
- Kiểm thử toàn dự án trong đợt pilot ngày 13/11: **289 passed**.
- Giới hạn: đây là kết quả pilot 20 ván/cặp, chưa đạt mức đánh giá chính thức tối thiểu 100 ván/cặp; không dùng pilot này để kết luận cuối cùng về sức mạnh các tác tử.
- Phần việc tiếp theo theo kế hoạch: giải đấu mặc định và giới hạn thời gian sau khi checkpoint được đóng băng; bổ sung số liệu có run_id vào `results/tables/report_numbers.csv`, phân tích bằng notebook và đối chiếu với `docs/EXPERIMENT_LOG.md`.

## Báo cáo và thuyết trình

Các mục được phân công trong báo cáo 5 chương:

| Mục | Nội dung | Tệp theo kế hoạch |
| --- | --- | --- |
| 2.4 | Học tăng cường (RL), DQN, Self-play; phân biệt AlphaGo-inspired và AlphaZero-inspired | `docs/report/02c_hoc_tang_cuong.md` |
| 3.5–3.6 | Thiết kế DQN cấp 6 và quy chuẩn giải đấu công bằng | `docs/report/03d_dqn_giai_dau.md` |
| 4.1–4.3 | Môi trường thực nghiệm, ma trận đối đầu, thắng/hòa/thua, độ trễ và chi phí | `docs/report/04a_ket_qua.md` |
| 4.4 | Đường cong huấn luyện DQN | `docs/report/04c_dqn_duong_cong.md` |
| 4.5 | Ablation A4 | `docs/report/04f_ablation_dqn.md` |
| 4.7 | Thảo luận kết quả, nguyên nhân, hạn chế và lợi thế đi trước | `docs/report/04h_thao_luan.md` |

- Đã có phần báo cáo giữa kỳ về DQN và giải đấu tại `docs/report/03d_dqn_giai_dau.md`.
- Theo phân công, chuẩn bị 2–4 slide về tác tử DQN cấp 6, giải đấu và kết quả thực nghiệm trong `docs/slides/y.pptx`.
- Các mục Chương 4 và slide cuối kỳ được cập nhật theo số liệu thực chạy, không đưa kết quả dự kiến vào báo cáo như kết quả đã hoàn thành.

## Nội dung cần tự giải thích khi review

- Replay Buffer giảm tương quan giữa các transition liên tiếp; Target Network giúp mục tiêu Bellman ổn định giữa các lần đồng bộ.
- Action Mask phải được áp dụng cả khi chọn hành động và khi tính max Q ở trạng thái kế tiếp.
- Transition của DQN chỉ được chốt sau lượt đáp của đối thủ để trạng thái kế tiếp đúng với lượt DQN tiếp theo.
- Cần luân phiên bên đi trước và dùng seed/khai cuộc có kiểm soát để giảm sai lệch trong đánh giá.
- Khoảng tin cậy Wilson phù hợp hơn khi tỷ lệ thắng gần 0 hoặc 1; pilot ít ván chưa đủ để kết luận hiệu năng cuối cùng.

## Công cụ và khai báo hỗ trợ

Python, NumPy, PyTorch, PyYAML, pytest, Jupyter Notebook, pandas và Matplotlib. ChatGPT được dùng hỗ trợ rà soát yêu cầu, cấu trúc triển khai và diễn giải kiểm thử; người thực hiện cần tự đọc, chạy, kiểm tra và chịu trách nhiệm với mã nguồn, log và số liệu trước khi nộp.

