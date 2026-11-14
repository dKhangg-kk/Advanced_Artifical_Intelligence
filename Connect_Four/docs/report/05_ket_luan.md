# Chương 5. Kết luận và hướng phát triển

## 5.1. Kết quả đạt được

Đề tài xây dựng hệ thống Connect Four 7×6 với engine bitboard, engine tham
chiếu, giao diện chung cho tác tử, bộ chạy trận và cơ chế ghi log. Phần tìm
kiếm gồm Random, Heuristic, Alpha-Beta và MCTS-UCT, có kiểm thử hành động hợp
lệ, bảo toàn bàn cờ, seed, ngân sách và các tính chất thuật toán.

Heuristic thắng Random 198/200 ván trong K1; MCTS ở 500 mô phỏng thắng Random
199/200 ván trong K3. Hai phép thử xác nhận yêu cầu baseline trên bộ seed và
khai cuộc đã công bố; không dùng các tỷ lệ này để xếp hạng mọi tác tử.
Nguồn: [nhật ký thực nghiệm](../EXPERIMENT_LOG.md),
[bảng K1](../../results/tables/k1-heuristic-random-20261109T061032Z-s0.csv) và
[bảng K3](../../results/tables/k3-mcts-random-20261110T181313Z-s0.csv).

A1/A2/A5 bổ sung thực nghiệm có kiểm soát về cắt tỉa, thứ tự duyệt, ngân sách
mô phỏng và độ sâu. Các lần chạy lưu log thô, cấu hình, môi trường, commit và
`run_id`; notebook dựng lại bảng/hình từ log. Tác dụng chính của ablation là
cho thấy thành phần nào ảnh hưởng đến chi phí hoặc kết quả trong điều kiện
cụ thể, thay vì chỉ liệt kê các thuật toán đã cài đặt.

Phần học được đã có triển khai CNN/DQN, log CNN và pilot DQN. Trạng thái
triển khai không đồng nghĩa với đã chứng minh hiệu năng đối kháng cuối cùng.
Kết luận dưới đây giới hạn theo bằng chứng có đến ngày 15/11/2026; chưa phải
xác nhận bộ số liệu toàn nhóm đã đóng băng.

## 5.2. Trả lời các câu hỏi nghiên cứu

### RQ1 — Alpha-Beta và MCTS trong cùng ngân sách

A1 chứng minh trên bộ kiểm tra rằng cắt tỉa/sắp xếp giữ nguyên giá trị minimax
và giảm chi phí. A2 cho thấy khi tăng mô phỏng, MCTS cải thiện kết quả trước
Alpha-Beta sâu 4; A5 cho thấy tăng độ sâu làm tăng chi phí nhưng score không
tăng đều. Chi tiết số đo và CI nằm tại
[mục ablation tìm kiếm](04d_ablation_tim_kiem.md).

Tuy nhiên, A2 dùng hai loại giới hạn khác nhau: độ sâu và số mô phỏng. Do
chưa có kết quả đối đầu cùng thời gian tương ứng, **chưa trả lời đầy đủ phần
“cùng ngân sách tính toán” của RQ1**. Không thể kết luận MCTS hoặc Alpha-Beta
ưu việt hơn chỉ từ số nút, số mô phỏng hay tỷ lệ thắng ở cấu hình riêng.

### RQ2 — CNN học từ nhãn Alpha-Beta

A3 cho thấy trên tập test cố định, tăng số ván train từ 250 lên 1.332 làm
top-1 tăng từ khoảng 47,19% lên 57,08%; kết quả theo tình huống được báo cáo
riêng để phân biệt khớp nhãn với chọn nước chiến thuật tốt. Điều này là bằng
chứng CNN học được thông tin từ nhãn trong thí nghiệm đã chạy.

Top-1 không phải tỷ lệ thắng trước Alpha-Beta/MCTS. Chưa có đối đầu đầy đủ để
kết luận CNN mạnh hơn chuyên gia sinh nhãn hoặc tác tử tìm kiếm. Nhãn của
chuyên gia hữu hạn độ sâu và cách chia tập là giới hạn quan trọng.
Nguồn: [A3](04e_ablation_cnn.md),
[bảng A3](../../results/tables/ablation_a3_results.csv) và các dòng `a3_*`
trong `report_numbers.csv`.

### RQ3 — DQN học qua tương tác hoặc tự chơi

Pilot DQN ghi nhận 200 episode trước Heuristic, có replay buffer, target
network và mặt nạ hành động hợp lệ. Pilot đối đầu có 20 ván/cặp, chưa đạt quy
mô đánh giá chính thức. Các bằng chứng này xác nhận đường ống huấn luyện và
đánh giá hoạt động, **chưa chứng minh hội tụ, độ ổn định qua nhiều seed hoặc
khả năng self-play**. A4 và huấn luyện self-play cần kết quả riêng trước khi
được đưa vào kết luận.
Nguồn: [thiết kế và pilot DQN](03d_dqn_giai_dau.md).

### RQ4 — So sánh CNN với DQN

Chưa có kết quả CNN–DQN trực tiếp trên checkpoint cuối và cùng bộ khai cuộc,
ngân sách, seed. Không dùng CNN accuracy để so với DQN win rate, cũng không
so sánh thời gian huấn luyện từ hai máy/cấu hình khác nhau như một phép thử
đã kiểm soát. **Chưa đủ dữ liệu để kết luận mô hình nào mạnh hơn hoặc thích
nghi tốt hơn.** Đây là giới hạn bằng chứng hiện tại, không phải kết quả hòa.

## 5.3. Hạn chế

1. Các phép thử tìm kiếm dùng một cohort khai cuộc; cần lặp cohort độc lập để
   đánh giá độ ổn định. Độ trễ phụ thuộc máy và tải nền.
2. Hàm lượng giá thủ công và rollout ngẫu nhiên đều có thể bỏ sót chiến thuật.
   Độ sâu lớn hơn không bảo đảm cải thiện kết quả ở mọi tập thử.
3. Thực nghiệm CNN hiện dựa trên một seed/split; độ khớp nhãn không thay thế
   sức mạnh đối kháng. Pilot DQN chưa đủ để đánh giá học lâu dài.
4. Chưa có đầy đủ giải đấu sáu tác tử ở hai chế độ, A4 và checkpoint DQN cuối
   trong repository tại thời điểm tổng hợp. Những hạng mục này cần hoàn tất
   trước khi tuyên bố toàn bộ kế hoạch của nhóm đã đạt.
5. Chưa kiểm tra trọn gói nộp trên một máy sạch độc lập. Nhật ký cá nhân còn
   một số mục thiếu giờ thực tế, đã liệt kê để tác giả bổ sung.

## 5.4. Tái lập và hướng phát triển

Giữ log thô bất biến theo `run_id`; lưu cấu hình, seed và commit; tạo bảng và
hình bằng notebook; dẫn số trong báo cáo về `report_numbers.csv`. Phần tự
triển khai, phần kế thừa và hỗ trợ AI được khai báo ở
[tài liệu tham khảo và đóng góp](06_tai_lieu_dong_gop.md).

Ưu tiên tiếp theo là hoàn tất giải đấu cùng thời gian và checkpoint học được,
lặp các seed/khai cuộc độc lập, phân tích những ván thất bại theo quy tắc chọn
mẫu công khai. Với Alpha-Beta, có thể khảo sát hàm lượng giá và bảng chuyển vị;
với MCTS, có thể khảo sát rollout có định hướng. Mỗi thay đổi cần ablation
riêng thay vì gộp nhiều tối ưu rồi quy toàn bộ cải thiện cho một thành phần.

Kết quả hiện tại hỗ trợ việc đánh giá thuật toán theo cả chất lượng quyết
định và chi phí tính toán trong Connect Four. Khả năng chuyển kết luận sang
trò chơi khác cần được kiểm chứng bằng thí nghiệm mới.
