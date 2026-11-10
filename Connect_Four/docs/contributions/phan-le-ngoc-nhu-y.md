# Đóng góp của Phan Lê Ngọc Như Ý (3124720079)

## Phần phụ trách

Học tăng cường cấp 6 (DQN), phần lõi replay/epsilon, tác tử DQN và các phần đánh giá được phân công ở các mốc tiếp theo.

## Nhật ký

| Ngày | Việc đã làm | PR/commit | Giờ |
| --- | --- | --- | --- |
| 08/11/2026 | Cài đặt ReplayBuffer FIFO, lưu transition kèm mặt nạ cột hợp lệ của trạng thái kế tiếp; bổ sung lịch epsilon theo episode và test độc lập PyTorch. | feat/y1-dqn-core | Điền thời lượng thực tế |
| 09/11/2026 | Hoàn thiện mặt nạ Q-value, nạp DQN checkpoint theo cơ chế lazy-load, suy luận DQNAgent trên state 2×6×7 và kiểm tra không làm thay đổi game. | feat/y2-dqn-agent | Điền thời lượng thực tế |

## Phần cần nắm để trình bày

- ReplayBuffer dùng FIFO: khi đủ 100.000 transition, phần tử cũ nhất bị thay thế; lấy mẫu ngẫu nhiên không hoàn lại để giảm tương quan giữa các mẫu liên tiếp.
- Mỗi transition lưu `next_legal_mask` của bàn kế tiếp; khi tính max Q ở bước mục tiêu, chỉ dùng những cột hợp lệ.
- Epsilon giảm theo episode từ 1.0 theo hệ số decay và không thấp hơn 0.05; khi thi đấu, DQNAgent dùng epsilon = 0.0.
- DQNAgent chỉ đọc `legal_actions()` và `to_array()`, không thay đổi trạng thái game; Q-value ở cột không hợp lệ được đặt thành âm vô cùng trước khi lấy argmax.
- DQNNet nằm trong `agents/networks.py` và được khởi tạo bằng lazy import để các test lõi vẫn chạy khi chưa có PyTorch.

## Công cụ và nguồn đã dùng

Python, NumPy, PyTorch và pytest. Ghi nhận đầy đủ các công cụ hỗ trợ và tài liệu tham khảo đã sử dụng theo quy định của học phần trước khi nộp báo cáo.
