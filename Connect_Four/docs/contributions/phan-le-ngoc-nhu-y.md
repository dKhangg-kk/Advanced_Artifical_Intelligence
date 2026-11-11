# Đóng góp của Phan Lê Ngọc Như Ý (3124720079)

## Phần phụ trách

Học tăng cường cấp 6 (DQN), phần lõi replay/epsilon, tác tử DQN và các phần đánh giá được phân công ở các mốc tiếp theo.

## Nhật ký

| Ngày | Việc đã làm | PR/commit | Giờ |
| --- | --- | --- | --- |
| 08/11/2026 | Cài đặt ReplayBuffer FIFO, lưu transition kèm mặt nạ cột hợp lệ của trạng thái kế tiếp; bổ sung lịch epsilon theo episode và test độc lập PyTorch. | feat/y1-dqn-core | Điền thời lượng thực tế |
| 09/11/2026 | Hoàn thiện mặt nạ Q-value, nạp DQN checkpoint theo cơ chế lazy-load, suy luận DQNAgent trên state 2×6×7 và kiểm tra không làm thay đổi game; PR #59 được merge vào main ngày 10/11. | feat/nhu-y-y1-y2 / PR #59 | Điền thời lượng thực tế |
| 10/11/2026 | PR #59 cho phần Y1/Y2 được merge vào `main`; đồng bộ code mới nhất và bắt đầu triển khai vòng huấn luyện Y3. | feat/nhu-y-y1-y2 / PR #59 | Điền thời lượng thực tế |
| 11/11/2026 | Bổ sung vòng huấn luyện DQN: luân phiên bên đi trước, lưu transition sau lượt đáp của đối thủ, Bellman target có mask, Huber loss, Target Network, checkpoint và CSV log theo episode. Chạy pilot 200 episode và cập nhật run_id/thời gian sau khi thực hiện trên máy. | feat/nhu-y-y3-dqn-training | Điền thời lượng thực tế và run_id sau khi chạy pilot |

## Phần cần nắm để trình bày

- ReplayBuffer dùng FIFO: khi đủ 100.000 transition, phần tử cũ nhất bị thay thế; lấy mẫu ngẫu nhiên không hoàn lại để giảm tương quan giữa các mẫu liên tiếp.
- Mỗi transition lưu `next_legal_mask` của bàn kế tiếp; khi tính max Q ở bước mục tiêu, chỉ dùng những cột hợp lệ.
- Epsilon giảm theo episode từ 1.0 theo hệ số decay và không thấp hơn 0.05; khi thi đấu, DQNAgent dùng epsilon = 0.0.
- DQNAgent chỉ đọc `legal_actions()` và `to_array()`, không thay đổi trạng thái game; Q-value ở cột không hợp lệ được đặt thành âm vô cùng trước khi lấy argmax.
- DQNNet nằm trong `agents/networks.py` và được khởi tạo bằng lazy import để các test lõi vẫn chạy khi chưa có PyTorch.
- Trong huấn luyện, mỗi transition của DQN chỉ được đưa vào ReplayBuffer sau khi đối thủ đã đi; vì vậy `next_state` là trạng thái ở lượt DQN kế tiếp. Transition kết thúc không bootstrap; transition chưa kết thúc chỉ lấy max Q-target trên các cột hợp lệ.
- Target Network đồng bộ theo số bước cập nhật; Huber loss được dùng cho sai số TD. Log CSV ghi một dòng mỗi episode; checkpoint luôn đi kèm JSON metadata về cấu hình, seed, commit và thiết bị.

## Công cụ và nguồn đã dùng

Python, NumPy, PyTorch, PyYAML và pytest. Công cụ AI hỗ trợ: ChatGPT được dùng để hỗ trợ diễn giải yêu cầu Y3, rà soát luồng huấn luyện và đề xuất test; người thực hiện cần tự đọc, chạy, kiểm tra và chịu trách nhiệm với mã nguồn trước khi nộp. Các nguồn và công cụ hỗ trợ được khai báo theo yêu cầu của proposal.
