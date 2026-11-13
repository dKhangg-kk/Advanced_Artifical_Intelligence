# 3.5. Thiết kế tác tử Deep Q-Network (Level 6) và 3.6.1. Quy chuẩn giải đấu Round-Robin

## 3.5.1. Mô hình hóa môi trường học tăng cường

Bài toán Connect Four được mô hình hóa thành quá trình quyết định Markov (MDP) gồm trạng thái `s`, hành động `a`, phần thưởng `r`, trạng thái kế tiếp `s'` và hệ số chiết khấu `γ`. Tại một lượt của DQN, trạng thái được biểu diễn bởi tensor hai kênh kích thước 2×6×7: kênh 0 là quân của người chơi hiện tại, kênh 1 là quân đối thủ. Tập hành động gồm bảy cột, nhưng chỉ các cột chưa đầy mới hợp lệ.

Trong huấn luyện, DQN đối đầu Random hoặc Heuristic. Mỗi episode luân phiên bên đi trước. DQN nhận phần thưởng cuối ván theo góc nhìn của chính nó: +1 khi thắng, 0 khi hòa và −1 khi thua; các bước chưa kết thúc nhận 0. Sau khi DQN đi, hệ thống chờ đối thủ đáp lại rồi mới lưu transition để `next_state` là bàn ở lượt DQN kế tiếp. Trường hợp ván kết thúc ngay sau nước của DQN được lưu terminal transition và không bootstrap.

## 3.5.2. Kiến trúc DQN và cơ chế chọn hành động hợp lệ

`DQNNet` trong `agents/networks.py` nhận tensor `(B, 2, 6, 7)`, đi qua hai lớp tích chập 3×3 với ReLU, sau đó qua tầng fully-connected và xuất bảy Q-value. `DQNAgent` nạp checkpoint theo cơ chế lazy-load; khi chọn nước, agent lấy `legal_actions()`, suy luận Q-value và đặt giá trị tại cột không hợp lệ thành âm vô cùng trước `argmax`. Vì vậy, ngay cả khi mạng có trọng số ngẫu nhiên hoặc Q-value ở cột đầy lớn nhất, agent vẫn không chọn nước sai.

## 3.5.3. Replay Buffer, Target Network và quy trình huấn luyện

Replay Buffer là bộ nhớ FIFO có sức chứa mặc định 100.000 transition. Transition giữ `state`, `action`, `reward`, `next_state`, `done` và `next_legal_mask`. Khi bộ nhớ đầy, transition mới ghi đè mẫu cũ nhất; khi huấn luyện, batch được lấy ngẫu nhiên không hoàn lại.

Mạng trực tuyến `Qθ` dự đoán giá trị hành động; mạng mục tiêu `Qθ−` dùng để tính mục tiêu TD và được đồng bộ định kỳ. Với transition không kết thúc, mục tiêu là `y = r + γ max_{a' hợp lệ} Qθ−(s',a')`. Với transition terminal, `y = r`. Các Q-value ở cột không hợp lệ bị mask trước phép `max`. Hàm mất mát Huber (`smooth_l1_loss`) được dùng để tối ưu sai số giữa Q dự đoán và mục tiêu.

Cấu hình pilot ngày 13/11/2026 dùng 200 episode, đối thủ Heuristic, seed 42, learning rate 0.001, `γ=0.99`, epsilon từ 1.0 với decay 0.9995, batch 64, replay tối đa 100.000 và đồng bộ Target Network mỗi 500 optimizer updates. Pilot tạo 757 updates; kết quả 1 thắng và 199 thua cho thấy đường ống chạy được nhưng mô hình chưa hội tụ.

## 3.5.4. Thiết kế thí nghiệm Ablation A4

A4 khảo sát ba hệ số epsilon decay (0.9990, 0.9995, 0.9998) trên ba seed (0, 42, 2026). Các mốc đánh giá dự kiến là 1.000, 2.500, 5.000 và 10.000 episode; mỗi checkpoint được đánh giá trên tập validation cố định gồm các trận gặp Random và Heuristic. Hai seed validation (20261102, 20261103) tách biệt seed giải đấu. Checkpoint cuối được chọn theo validation rồi mới đóng băng; không dùng kết quả test/giải đấu cuối để chọn siêu tham số. Tính đến gói giữa kỳ, A4 đầy đủ và checkpoint cuối chưa hoàn thành.

## 3.6.1. Quy chuẩn giải đấu Round-Robin

Giải đấu Round-Robin tổ chức cho mỗi cặp tác tử với số khai cuộc cố định. Mỗi khai cuộc được chơi hai lượt đổi bên để cân bằng lợi thế đi trước; seed và cấu hình được lưu trong manifest. Có hai chế độ so sánh: cấu hình mặc định và ngân sách thời gian tương đương cho mỗi nước. Mỗi trận ghi kết quả, số nước, chuỗi nước đi, thời gian trung bình và p95 mỗi agent, số nút/mô phỏng và cờ vượt ngân sách.

CLI nhận tên tác tử và cấu hình qua YAML; có thể chạy một cặp hoặc toàn bộ vòng tròn. Mỗi cặp được ghi ngay ra `games_<run_id>.csv`, `moves_<run_id>.csv` và `run_manifest.csv`, tránh mất toàn bộ giải đấu khi chương trình dừng đột ngột. Pilot 13/11 gồm ba tác tử Random, Heuristic, DQN; 20 ván mỗi cặp, 10 khai cuộc dùng chung, seed 20261113 (60 ván). DQN thắng Random 14/20 nhưng thua Heuristic 20/20; đây là số liệu pilot, chưa đủ 100 ván/cặp theo yêu cầu đánh giá chính thức.

## Bằng chứng mã nguồn và chạy thử

- `tests/test_cli.py`: kiểm tra đọc cấu hình, override ngân sách thời gian, chạy cặp agent và Round-Robin.
- `tests/test_dqn.py`: kiểm tra FIFO, kích thước batch, epsilon schedule và legal-action mask.
- `results/logs/train_dqn_20261113_140831_508593.csv`: log 200 episode.
- `results/logs/games_tournament-default-20261113T140850Z-s20261113-*.csv`: 60 trận pilot và các file moves tương ứng.
- `results/tables/report_numbers.csv`: số liệu được liên kết tới `run_id` và đường dẫn log.

Các giới hạn cần nêu: pilot DQN chỉ 200 episode; vòng tròn mới có 20 ván/cặp; checkpoint tạo ra mang trạng thái `pilot`, không phải checkpoint đóng băng; A4 đủ 9 tổ hợp và đợt đánh giá chính thức còn ở mốc tiếp theo.
