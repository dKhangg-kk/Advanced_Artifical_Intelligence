# Đóng góp của Phan Lê Ngọc Như Ý (3124720079)

## Phần phụ trách

Học tăng cường cấp 6 (DQN), lõi Replay Buffer/epsilon, DQN Agent, vòng huấn luyện, CLI/cấu hình giải đấu, pilot Round-Robin và phân tích ban đầu.

## Nhật ký công việc đến 15/11/2026

| Ngày | Việc thực hiện | Nhánh / PR / bằng chứng |
| --- | --- | --- |
| 08/11/2026 | Cài đặt ReplayBuffer FIFO sức chứa 100.000 transition; lưu mặt nạ cột hợp lệ của trạng thái kế tiếp; lấy mẫu ngẫu nhiên không hoàn lại; bổ sung EpsilonSchedule từ 1.0, có sàn 0.05 và kiểm thử độc lập PyTorch. | `feat/y1-dqn-core` |
| 09–10/11/2026 | Hoàn thiện DQNAgent lazy-load checkpoint; chuyển `game.to_array()` dạng 2×6×7 qua DQNNet; che cột không hợp lệ trước argmax; kiểm tra không sửa trạng thái game. | `feat/nhu-y-y1-y2`; PR #59 đã merge vào `main` theo nhật ký nhóm |
| 11–13/11/2026 | Hoàn thiện vòng huấn luyện DQN: luân phiên bên đi trước; lưu transition sau lượt đáp của đối thủ; thưởng cuối ván +1/0/−1; Bellman target có mask; Huber loss; đồng bộ Target Network mỗi 500 optimizer updates; lưu CSV theo episode và checkpoint kèm JSON metadata. | `training/train_dqn.py`; run pilot `20261113_140831_508593` |
| 12–13/11/2026 | Bổ sung `evaluation/config.py` và hoàn thiện `evaluation/cli.py`: cấu hình agent bằng YAML, chạy một cặp hoặc Round-Robin, ghi log games/moves/manifest và bảng tổng hợp theo từng cặp. Bổ sung `tests/test_cli.py`. | `evaluation/config.py`, `evaluation/cli.py`, `tests/test_cli.py` |
| 13/11/2026 | Chạy bộ kiểm thử đầy đủ: 289 passed. Chạy pilot huấn luyện 200 episode (CPU, 10.665 giây trong metadata; 757 optimizer updates), sau đó chạy pilot Round-Robin 3 cặp × 20 ván (60 ván). | `results/logs/`, `results/tables/`, `results/figures/`; log chi tiết trong `docs/EXPERIMENT_LOG.md` |
| Đến 15/11/2026 | Hoàn thiện phần báo cáo giữa kỳ được phân công: mục tiêu/phạm vi, cơ sở RL-DQN, thiết kế Level 6, quy chuẩn Round-Robin và phân tích pilot. | `docs/report/03d_dqn_giai_dau.md`; bản ghép giữa kỳ trong `docs/report/dist/` (do nhóm trưởng quản lý) |

## Kết quả pilot đã kiểm chứng

- Huấn luyện 200 episode gặp Heuristic, seed 42: 1 thắng, 0 hòa, 199 thua; mean reward = −0.99; 757 optimizer updates. Đây là pilot để xác nhận pipeline chạy và ghi log, chưa chứng minh DQN hội tụ.
- Round-Robin pilot 20 ván/cặp, 10 khai cuộc dùng chung, seed 20261113: Random–Heuristic (0–0–20 theo góc nhìn Random); Random–DQN (6–0–14 theo góc nhìn Random, do đó DQN thắng 14/20); Heuristic–DQN (20–0–0 theo góc nhìn Heuristic, do đó DQN thua 20/20).
- Kết quả chỉ là pilot, chưa đạt mức đánh giá chính thức tối thiểu 100 ván/cặp. Ablation A4 đủ 3 decay × 3 seed và checkpoint đóng băng vẫn thuộc mốc 14–17/11, chưa ghi nhận hoàn thành trong nhật ký này.

## Phần cần nắm để trình bày

- ReplayBuffer FIFO thay thế transition cũ nhất khi đầy; lấy mẫu không hoàn lại để giảm tương quan giữa các mẫu liên tiếp.
- Mỗi transition lưu `next_legal_mask` của bàn kế tiếp. Khi tính max Q ở mục tiêu Bellman, chỉ các cột còn hợp lệ được tham gia phép lấy cực đại.
- Epsilon-greedy khởi đầu 1.0, giảm theo episode và không thấp hơn 0.05; khi thi đấu, DQNAgent dùng epsilon = 0.0.
- Mỗi transition chỉ được chốt sau khi đối thủ đáp lại, để `next_state` phản ánh trạng thái ở lượt DQN tiếp theo. Trạng thái kết thúc không bootstrap.
- Target Network giữ mục tiêu Bellman ổn định giữa hai lần đồng bộ; Huber loss hạn chế ảnh hưởng của sai số TD lớn.
- Pilot 200 episode thua Heuristic gần như toàn bộ, cho thấy cần tăng huấn luyện, kiểm tra reward/góc nhìn/mặt nạ và lựa chọn mô hình theo validation, không chọn checkpoint theo kết quả test.

## Công cụ và khai báo hỗ trợ

Python, NumPy, PyTorch, PyYAML và pytest. ChatGPT được dùng hỗ trợ rà soát yêu cầu, cấu trúc triển khai và diễn giải kiểm thử; người thực hiện cần đọc, chạy, kiểm tra và chịu trách nhiệm với mã nguồn và số liệu trước khi nộp. Thời lượng lao động cá nhân và mã PR cho các phần mới chưa được điền vì không có dữ liệu xác thực trong snapshot.
