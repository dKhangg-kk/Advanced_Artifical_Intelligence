# 1. Giới thiệu

## 1.1. Bối cảnh nghiên cứu

Trò chơi đối kháng có thông tin đầy đủ (perfect-information game) là môi trường
thuận lợi để nghiên cứu khả năng ra quyết định, lập kế hoạch và dự đoán hành vi
đối thủ của tác tử trí tuệ nhân tạo. Trong môi trường này, mọi trạng thái đều
quan sát được, luật chơi xác định và kết quả ván đấu đo được rõ ràng, nên có
thể so sánh các phương pháp một cách có kiểm soát.

Ba hướng tiếp cận tiêu biểu được dùng trong đồ án:

- **Tìm kiếm đối kháng cổ điển:** Minimax/Negamax kết hợp cắt tỉa Alpha-Beta,
  dùng hàm lượng giá để giới hạn độ sâu tìm kiếm.
- **Tìm kiếm xác suất:** Monte Carlo Tree Search (MCTS) với công thức UCT, cân
  bằng khai thác và khám phá thông qua mô phỏng.
- **Học máy:** học có giám sát để bắt chước chính sách chuyên gia và học tăng
  cường để cập nhật giá trị hành động từ phần thưởng.

Connect Four (bàn cờ 7 cột × 6 hàng) được chọn làm trường hợp nghiên cứu vì
luật chơi đơn giản, trạng thái dễ biểu diễn nhưng vẫn chứa nhiều tình huống
chiến thuật. Trò chơi đủ nhỏ để huấn luyện và đánh giá trong phạm vi một đồ án
học phần, nhưng đủ lớn để các phương pháp tìm kiếm và học máy thể hiện khác
biệt về chất lượng nước đi và chi phí tính toán.

Connect Four chuẩn 7×6 đã được chứng minh có lời giải lý thuyết cho người đi
trước khi cả hai bên chơi tối ưu (Allis, 1988). Vì vậy đồ án **không** đặt mục
tiêu giải lại trò chơi hay chứng minh nước đi tối ưu. Trọng tâm là cài đặt đúng
các thuật toán, xây dựng một môi trường đánh giá thống nhất và phân tích kết quả
dựa trên số liệu chạy thực tế.

## 1.2. Game, luật chơi và ý nghĩa

### 1.2.1. Luật chơi

Connect Four dùng bàn cờ 7 cột × 6 hàng. Hai người chơi luân phiên thả quân vào
một cột còn chỗ trống; quân tự động rơi xuống ô trống thấp nhất của cột đó.

Các quy tắc chính:

- **Cơ chế trọng lực:** người chơi chỉ chọn cột, không chọn hàng.
- **Lượt chơi:** mỗi lượt thả đúng một quân, hai bên luân phiên.
- **Điều kiện thắng:** tạo được bốn quân liên tiếp theo hàng ngang, hàng dọc
  hoặc đường chéo.
- **Điều kiện hòa:** bàn cờ đầy nhưng không bên nào tạo được bốn quân liên tiếp.
- **Nước đi hợp lệ:** chỉ được chọn cột chưa đầy.

Trên bàn cờ 7×6 có 69 chuỗi bốn ô có thể tạo thành chiến thắng: 24 chuỗi ngang,
21 chuỗi dọc và 24 chuỗi chéo. Các yếu tố chiến thuật được quan tâm gồm:

- kiểm soát cột trung tâm;
- thắng ngay (immediate win);
- chặn đối thủ thắng ngay (immediate block);
- tạo đòn kép (double threat);
- tránh nước đi mở cơ hội thắng cho đối thủ ở lượt kế tiếp.

### 1.2.2. Mô hình hóa toán học

Connect Four là trò chơi đối kháng, tất định, theo lượt, có thông tin đầy đủ và
tổng bằng không. Các thành phần chính:

- **Trạng thái (state):** bàn cờ được biểu diễn bằng tensor nhị phân 2×6×7.
  Kênh 0 là quân của người đang đi, kênh 1 là quân của đối thủ. Cách biểu diễn
  tương đối này giúp cùng một mạng nơ-ron dùng được cho cả hai bên.
- **Hành động (action):** chọn một cột trong 0..6. Tập hành động hợp lệ là các
  cột chưa đầy.
- **Hàm chuyển trạng thái:** đặt quân vào ô trống thấp nhất của cột được chọn
  rồi chuyển lượt.
- **Hàm phần thưởng:** +1 nếu tác tử thắng, −1 nếu thua, 0 nếu hòa, xét theo
  góc nhìn của tác tử đang học.

Theo proposal, không gian trạng thái hợp lệ của bàn cờ có cùng bậc 10¹² vị trí,
và cây trò chơi còn lớn hơn nhiều vì một vị trí có thể đạt được bằng nhiều thứ
tự nước đi. Do đó không thể duyệt toàn bộ trong thời gian thực: tác tử tìm kiếm
phải giới hạn độ sâu hoặc ngân sách mô phỏng, còn tác tử học máy phải khái quát
hóa từ một phần nhỏ của không gian trạng thái.

### 1.2.3. Ý nghĩa của việc chọn Connect Four

- **Tính đại diện:** trò chơi có đủ các yếu tố của bài toán ra quyết định đối
  kháng nhưng không quá lớn để mọi thí nghiệm có thể chạy lại trong điều kiện
  của nhóm.
- **Tính đo lường:** kết quả ván đấu, thời gian suy luận, số nút duyệt và số
  mô phỏng đều ghi được thành log, thuận lợi cho việc so sánh định lượng.
- **Tính giáo dục:** cùng một trò chơi cho phép nối liền ba nhóm kiến thức:
  tìm kiếm có đối thủ, tối ưu hóa dưới bất định và học từ dữ liệu.
- **Giới hạn có kiểm soát:** vì trò chơi đã có lời giải lý thuyết, đồ án không
  cần tuyên bố tính tối ưu; mọi kết luận chỉ có giá trị trong cấu hình và ngân
  sách tính toán đã thử.

## 1.3. Mục tiêu nghiên cứu

Đồ án hướng tới ba mục tiêu.

**Mục tiêu 1 — Xây dựng Game Engine và hệ thống mô phỏng.** Xây dựng engine
quản lý bàn cờ, lượt chơi, nước đi hợp lệ và điều kiện kết thúc; cung cấp API
thống nhất cho mọi tác tử; có bộ kiểm thử luật chơi và giao diện chơi
người–máy/máy–máy.

**Mục tiêu 2 — Xây dựng sáu cấp độ tác tử.** Phát triển đủ sáu tác tử:

1. Random;
2. Heuristic/Rule-based;
3. Minimax/Negamax kết hợp Alpha-Beta;
4. MCTS-UCT;
5. CNN Policy học có giám sát từ nhãn Alpha-Beta;
6. DQN học tăng cường qua tương tác với môi trường.

Mỗi tác tử phải chọn được nước đi hợp lệ và tích hợp vào cùng một engine. CNN
và DQN cần có mô hình, checkpoint và số liệu huấn luyện thực tế.

**Mục tiêu 3 — Thiết kế thực nghiệm và đánh giá khoa học.** Tổ chức giải đấu
Round-Robin giữa các tác tử, so sánh trong ngân sách tính toán xác định, đánh
giá quá trình học của CNN/DQN và thực hiện ít nhất hai thí nghiệm
Ablation/Sensitivity Analysis. Kết quả gồm ma trận đối đầu, các chỉ số hiệu
năng, đường cong học và phân tích ván đấu tiêu biểu.

Bản báo cáo giữa kỳ tập trung vào Chương 1–3: làm rõ bối cảnh, cơ sở lý thuyết
và thiết kế/cài đặt. Các kết quả đối kháng đầy đủ và thảo luận được trình bày
ở Chương 4–5.

## 1.4. Câu hỏi nghiên cứu

| Mã | Câu hỏi | Bằng chứng dự kiến |
| --- | --- | --- |
| **RQ1** | Trong cùng ngân sách tính toán, Alpha-Beta và MCTS khác nhau thế nào về tỷ lệ thắng, thời gian suy luận và số trạng thái được khám phá? | Win/Draw/Loss, điểm thi đấu, thời gian mỗi nước, số nút duyệt, số lần mô phỏng |
| **RQ2** | CNN Policy Network học từ nhãn Alpha-Beta đạt hiệu năng ra sao so với tác tử tìm kiếm, và có nhận diện được các tình huống chiến thuật quan trọng không? | Loss, Top-1 Accuracy, độ chính xác theo tình huống thắng ngay/chặn/kiểm soát trung tâm; kết quả đối kháng bổ sung |
| **RQ3** | DQN có thể tự học chiến lược qua tương tác/tự chơi không? Số episode, cách khám phá và đối thủ huấn luyện ảnh hưởng thế nào? | Win Rate trước baseline, Average Reward, đường cong học, độ ổn định giữa các seed |
| **RQ4** | CNN học có giám sát và DQN học tăng cường khác nhau thế nào về tỷ lệ thắng, thời gian huấn luyện và khả năng thích nghi với đối thủ? | So sánh đối đầu trực tiếp, thời gian huấn luyện, thời gian suy luận, độ ổn định |

Các hướng kiểm chứng tương ứng:

- **RQ1:** chạy hai tác tử trong cùng ngân sách thời gian hoặc số mô phỏng, cùng
  số ván và seed, luân phiên bên đi trước. Hai loại lượng tính toán (nút duyệt
  và mô phỏng) được báo cáo riêng, không quy đổi cho nhau.
- **RQ2:** huấn luyện CNN với cách chia theo ván, đánh giá trên tập test chưa
  dùng để huấn luyện; đo thêm độ chính xác theo bốn nhóm tình huống
  `win_now`, `block`, `center_control`, `other`. Kết quả đối kháng trực tiếp
  được bổ sung ở giai đoạn giải đấu.
- **RQ3:** đánh giá checkpoint tại các mốc episode, khảo sát epsilon decay và
  tập đối thủ huấn luyện; đo win rate trên các trận độc lập với seed cố định.
- **RQ4:** đặt CNN và DQN vào cùng engine, cùng nhóm đối thủ, số ván, seed và
  quy tắc đổi bên; so sánh win rate, thời gian huấn luyện và thời gian suy luận.

Đây là kế hoạch kiểm chứng, không phải kết luận định trước. Câu trả lời chính
thức chỉ được đưa ra khi có số liệu tương ứng trong log thực nghiệm.

## 1.5. Phạm vi

### 1.5.1. Trong phạm vi

- Trò chơi Connect Four 7×6, luật chuẩn, hai người chơi.
- Sáu tác tử cấp 1–6 dùng chung API và cùng engine.
- Sinh dữ liệu policy từ Alpha-Beta độ sâu 4 sau khai cuộc ngẫu nhiên; chia
  train/validation/test theo ván; khử trùng lặp và lật gương dữ liệu train.
- Huấn luyện CNN Policy cấp 5, lưu checkpoint, log huấn luyện và đánh giá test
  đúng một lần cho mỗi lần chạy.
- Giải đấu Round-Robin, các thí nghiệm ablation A1–A5 và phân tích kết quả
  trong giới hạn tài nguyên của nhóm.
- Giao diện chơi người–máy/máy–máy, tài liệu tái lập và báo cáo.

### 1.5.2. Ngoài phạm vi

- Giải lại Connect Four hoặc chứng minh nước đi tối ưu.
- Tích hợp CNN với MCTS/PUCT theo kiểu AlphaGo/AlphaZero.
- Huấn luyện phân tán, tìm kiếm siêu tham số quy mô lớn hoặc triển khai
  production.
- Ngoại suy kết quả sang trò chơi khác như một kết luận; mọi ngoại suy chỉ là
  giả thuyết.
- Đánh giá đối kháng của CNN trước Alpha-Beta trong phạm vi báo cáo giữa kỳ;
  phần này thuộc giai đoạn giải đấu và được bổ sung sau.

### 1.5.3. Giới hạn tài nguyên

Các lần huấn luyện CNN được báo cáo trong báo cáo này chạy trên CPU, không dùng
GPU. Vì vậy quy mô dữ liệu, số epoch và số cấu hình được khảo sát được chọn để
phù hợp với thời gian của đồ án; các kết luận không được suy rộng ra ngoài cấu
hình đã chạy.

## 1.6. Sản phẩm bàn giao

| Sản phẩm | Nội dung chính | Trạng thái tại bản giữa kỳ |
| --- | --- | --- |
| Game Engine | Luật 7×6, bitboard và bản tham chiếu, API thống nhất, kiểm thử luật | Đã có |
| Tác tử cấp 1–4 | Random, Heuristic, Alpha-Beta, MCTS-UCT | Đã có mã và kiểm thử |
| Dữ liệu policy | 5.000 ván Alpha-Beta depth 4, chia theo ván, khử trùng lặp, lật gương train | Đã chạy, có manifest và split |
| CNN Policy cấp 5 | Kiến trúc `CNNPolicyNet`, checkpoint, log huấn luyện, đánh giá test | Đã huấn luyện và đánh giá |
| DQN cấp 6 | Mạng Q, Replay Buffer, Target Network, vòng huấn luyện | Mã lõi và vòng huấn luyện đã có; kết quả huấn luyện/đánh giá trình bày ở Chương 4–5 |
| Đánh giá | Khung chạy trận, `run_id`, log ván/nước, bảng và hình | Hạ tầng và các lần chạy pilot đã có; giải đấu đầy đủ tiếp tục ở giai đoạn sau |
| Báo cáo | Chương 1–3 của bản giữa kỳ | Tệp này cùng các tệp `02b`, `03a`, `03c` |
| Slide, poster, demo | Tóm tắt phương pháp và kết quả, demo chơi được | Dự kiến hoàn thiện ở mốc M5 |

Mọi số liệu đo trong báo cáo được dẫn về `results/tables/report_numbers.csv`
và `run_id` tương ứng. Số liệu kế hoạch (ví dụ số ván dự kiến trong proposal)
được ghi rõ là `planned`, không dùng làm bằng chứng cho kết luận thực nghiệm.
