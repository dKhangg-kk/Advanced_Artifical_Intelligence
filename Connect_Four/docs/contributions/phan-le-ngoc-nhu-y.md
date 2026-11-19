# Đóng góp của Phan Lê Ngọc Như Ý (3124720079)

## Nhật ký

| Ngày | Việc đã làm | Issue/PR/commit | Giờ |
| --- | --- | --- | --- |
| 08–10/11/2026 | Xây dựng ReplayBuffer FIFO, EpsilonSchedule, mặt nạ cột hợp lệ và DQN Agent | [PR #59](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/59), nhánh `feat/nhu-y-y1-y2` | Chưa ghi nhận |
| 11–13/11/2026 | Hoàn thiện vòng huấn luyện DQN, Target Network, Bellman Target có mask, Huber Loss, lưu checkpoint và log | [PR #64](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/64) | Chưa ghi nhận |
| 12–13/11/2026 | Xây dựng Tournament CLI, cấu hình YAML, kiểm thử và chạy pilot DQN/Round-Robin | [PR #75](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/75), nhánh `feat/nhu-y-y4-cli-tournament-pilot` | Chưa ghi nhận |
| 13/11/2026 | Chạy kiểm thử toàn dự án và bổ sung log, bảng, hình, notebook phân tích pilot | [PR #75](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/75), run `20261113_140831_508593` | Chưa ghi nhận |
| Đến 15/11/2026 | Hoàn thiện phần báo cáo giữa kỳ về DQN cấp 6 và thiết kế giải đấu | `docs/report/03d_dqn_giai_dau.md`, [PR #75](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/75) | Chưa ghi nhận |


## Công cụ hỗ trợ

Python, NumPy, PyTorch, PyYAML, pytest, Jupyter Notebook, pandas, Matplotlib, Git và GitHub. ChatGPT được dùng hỗ trợ rà soát yêu cầu. Kết quả chạy và số liệu cần được người thực hiện tự kiểm tra và chịu trách nhiệm.

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

| Ngày | Việc | Dẫn chứng | Giờ |
| --- | --- | --- | --- |
| 18/11/2026 | Chạy A4 (3 decay × 3 seed), đóng băng checkpoint theo quy tắc validation đăng ký trước, chẩn đoán khai cuộc, 1 ô mở rộng có gán nhãn | `scripts/run_ablation_a4.py`, `scripts/freeze_dqn_checkpoint.py`, `checkpoints/level6_dqn/final.json`, `results/tables/ablation_a4_*.csv`, `docs/report/04c_dqn_duong_cong.md`, `04f_ablation_dqn.md` | Chưa ghi nhận |

- Phần Y5, Y6 và các mục 4.1–4.7, slide được **Claude (Anthropic) thực hiện thay Như Ý** trong các phiên ngày 18–19/11/2026 (đã khai báo trong `docs/THIRD_PARTY.md`). Các commit mang danh tính Claude, không phải Như Ý. **Như Ý cần đọc lại, chạy lại script và tự giải thích được số liệu trước khi nộp**; kế hoạch yêu cầu mỗi thành viên commit bằng tài khoản của mình.
- Đóng băng ngày 18/11, **muộn hơn kế hoạch (17/11)**. Mốc 10.000 episode được chọn (validation trung bình 0,375).
- Giờ làm việc không được suy đoán: để "Chưa ghi nhận" cho đến khi Như Ý tự điền.

## Nhật ký Y6 — Giải đấu, số liệu và phân tích

| Ngày | Việc | Dẫn chứng | Giờ |
| --- | --- | --- | --- |
| 13/11/2026 | Pilot Round-Robin 3 tác tử, 20 ván/cặp | [PR #75](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/75), prefix `tournament-default-20261113T140850Z-s20261113` | Chưa ghi nhận |
| 18/11/2026 | Round-Robin 6 tác tử: mặc định 200 ván/cặp và cùng thời gian 0,2 s (100 ván/cặp); bảng, hình, notebook | `results/tables/y6_*`, `results/figures/y6_*`, `notebooks/01_*.ipynb` | Chưa ghi nhận |
| 19/11/2026 | Hợp nhất vào bản zip mới; kiểm tra `report_numbers.csv`; mục 4.1–4.3, 4.7; slide Y | `docs/report/04a_ket_qua.md`, `04h_thao_luan.md`, `docs/slides/y.pptx` | Chưa ghi nhận |

- Kiểm thử toàn dự án sau khi hợp nhất: tất cả test đạt.
- `report_numbers.csv`: các dòng A1/A2/A5 (Khang), A3 (Kiệt), A4 và giải đấu (Ý) đều có `run_id`. Còn 32 dòng của Kiệt (mục 3.4) trỏ tới `data/generated/` vốn không commit (theo kế hoạch); đã sửa đường dẫn sai của 7 dòng pilot DQN (mục 3.5).
- Phát hiện cho Khang: Alpha-Beta độ sâu 5 bỏ lỡ 5/18 thế thắng ngay (xem 4.3b và 4.7.2); `docs/report/05_ket_luan.md` vẫn mô tả DQN ở mức pilot, cần cập nhật theo 4.4–4.7.

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

Python, NumPy, PyTorch, PyYAML, pytest, Jupyter Notebook, pandas, Matplotlib, Git và GitHub. ChatGPT được dùng hỗ trợ rà soát yêu cầu. Kết quả chạy và số liệu cần được người thực hiện tự kiểm tra và chịu trách nhiệm.

