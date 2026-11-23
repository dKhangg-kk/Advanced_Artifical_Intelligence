# 2.3. Policy network, value network và học có giám sát

## 2.3.1. Từ tìm kiếm sang học hàm xấp xỉ

Các tác tử ở cấp 1–4 ra quyết định bằng luật viết tay hoặc bằng tìm kiếm trên
cây trò chơi. Cách tiếp cận này không cần dữ liệu huấn luyện nhưng chi phí suy
luận tăng theo độ sâu hoặc số mô phỏng. Với Connect Four, không gian trạng thái
có cùng bậc 10¹² vị trí, nên việc duyệt toàn bộ là không khả thi trong thời
gian thực.

Một hướng khác là **học hàm xấp xỉ**: dùng mạng nơ-ron để ánh xạ trạng thái bàn
cờ sang quyết định hoặc giá trị. Sau khi huấn luyện, chi phí suy luận chỉ còn
một lượt lan truyền tiến (forward pass), không phụ thuộc độ sâu tìm kiếm. Hai
hàm mục tiêu thường được học là:

- **Policy** `π(a | s)`: phân phối xác suất trên các hành động tại trạng thái
  `s`, dùng để chọn nước đi.
- **Value** `V(s)` hoặc `Q(s, a)`: giá trị kỳ vọng của trạng thái hoặc của cặp
  trạng thái–hành động, dùng để đánh giá mức thuận lợi.

Trong đồ án, cấp 5 dùng **policy network** học có giám sát từ nhãn Alpha-Beta.
Cấp 6 dùng **DQN** để học `Q(s, a)` từ phần thưởng tương tác. Báo cáo phân biệt
rõ hai hướng này; không có một value network riêng được huấn luyện cho cấp 5.

## 2.3.2. Policy network

### Định nghĩa và đầu ra

Policy network nhận trạng thái `s` và trả về logits `z = f_θ(s) ∈ R^7`, sau đó
chuẩn hóa bằng softmax:

```
π_θ(a | s) = exp(z_a) / Σ_b exp(z_b)
```

Với Connect Four, đầu vào là tensor 2×6×7 (quân của người đang đi và quân đối
thủ), đầu ra là 7 logits tương ứng 7 cột. Khi chọn nước đi, các cột đã đầy được
gán xác suất bằng 0 (hoặc logit bằng −∞) trước khi lấy `argmax`, nhờ đó tác tử
luôn trả về một nước hợp lệ.

### Hàm mất mát

Nếu nhãn chuyên gia tại trạng thái `s` là `a*`, học có giám sát tối thiểu hóa
cross-entropy:

```
L(θ) = −(1/N) Σ_i log π_θ(a*_i | s_i)
```

Đây là bài toán phân loại nhiều lớp với 7 lớp (7 cột). Mô hình không học phân
phối của toàn bộ nước đi tối ưu, mà học phân phối có xu hướng đặt xác suất cao
nhất vào nước đi mà chuyên gia đã chọn.

### Chỉ số đánh giá

- **Loss:** giá trị cross-entropy trung bình trên một tập dữ liệu.
- **Top-1 accuracy:** tỷ lệ trạng thái mà cột dự đoán trùng nhãn chuyên gia.
- **Top-k accuracy:** tỷ lệ trạng thái mà nhãn nằm trong `k` cột có xác suất
  cao nhất. Chỉ số này hữu ích khi nhiều nước đi gần tương đương nhau.
- **Tỷ lệ nước hợp lệ:** tỷ lệ dự đoán rơi vào cột chưa đầy. Trong đồ án, chỉ số
  này được đo trên đầu ra chưa che cột không hợp lệ, nhằm kiểm tra bản thân mô
  hình đã học được ràng buộc luật chơi hay chưa.

Top-1 accuracy cao không đồng nghĩa với sức mạnh thi đấu cao. Một mô hình có
thể bắt chước tốt nhãn chuyên gia trên phân phối dữ liệu huấn luyện nhưng vẫn
thua khi gặp trạng thái xa phân phối hoặc khi đối thủ chơi khác chuyên gia. Vì
vậy kết quả đối kháng là bằng chứng bổ sung, không thay thế được accuracy.

## 2.3.3. Value network

### Định nghĩa

Value network ước lượng giá trị của một trạng thái:

```
V_φ(s) ≈ E[G_t | s]
```

hoặc giá trị của một cặp trạng thái–hành động:

```
Q_φ(s, a) ≈ E[G_t | s, a]
```

Trong đó `G_t` là tổng phần thưởng từ thời điểm `t` đến khi kết thúc ván. Với
Connect Four, `G_t` thường lấy giá trị +1 khi thắng, −1 khi thua và 0 khi hòa,
xét theo góc nhìn của người chơi tại trạng thái `s`.

### Vai trò

Value network trả lời câu hỏi “trạng thái này tốt hay xấu cho tôi?”, trong khi
policy network trả lời “tôi nên đi cột nào?”. Value network có thể được dùng để:

- đánh giá lá của cây tìm kiếm thay cho hàm lượng giá viết tay;
- xếp hạng hoặc cắt tỉa nhánh trong tìm kiếm;
- làm baseline cho học tăng cường (ví dụ advantage);
- ước lượng chất lượng checkpoint mà không cần chơi hết ván.

### Quan hệ với đồ án

Đồ án **không** huấn luyện một value network độc lập cho cấp 5. Lý do:

- Nguồn nhãn hiện có là nước đi Alpha-Beta, phù hợp trực tiếp với bài toán
  policy; nhãn giá trị của trạng thái không được sinh ra trong pipeline dữ liệu.
- Mục tiêu của cấp 5 là kiểm chứng khả năng bắt chước chính sách chuyên gia
  (RQ2), nên policy network là lựa chọn tối thiểu và đo được.
- Cấp 6 dùng DQN, tức học `Q(s, a)` từ phần thưởng. Khái niệm value xuất hiện ở
  đó dưới dạng action-value, với tín hiệu học khác hẳn nhãn có giám sát.

Việc phân biệt này quan trọng để không gán nhầm kết quả: top-1 accuracy của
CNN Policy là thước đo mức độ bắt chước chuyên gia, không phải thước đo giá trị
trạng thái.

## 2.3.4. Học có giám sát

### Dữ liệu và nhãn

Học có giám sát cần một tập cặp `(s_i, a*_i)`. Trong đồ án, `s_i` là trạng thái
bàn cờ trước nước đi và `a*_i` là cột do `AlphaBetaAgent` độ sâu 4 chọn. Dữ liệu
được sinh từ các ván Alpha-Beta sau một khai cuộc ngẫu nhiên 6–8 nước, nhằm đa
dạng hóa trạng thái khởi đầu thay vì chỉ học từ một khai cuộc cố định.

Mỗi mẫu được lưu cùng `game_id`, `ply`, `state`, `action`; nhờ `game_id`, dữ
liệu có thể được chia theo ván để tránh rò rỉ trạng thái giữa các tập.

### Chia dữ liệu

Dữ liệu được chia theo **ván**, không chia theo từng mẫu:

- Training: 70%;
- Validation: 15%;
- Test: 15%.

Cách chia theo ván bảo đảm mọi trạng thái của một ván chỉ nằm trong đúng một
tập. Nếu chia theo mẫu, các trạng thái gần nhau trong cùng ván có thể xuất hiện
ở cả train và test, khiến accuracy bị đánh giá cao giả tạo.

Sau khi chia, các trạng thái trùng hoặc đối xứng qua phép lật ngang được loại
theo thứ tự train → validation → test. Chỉ tập train được bổ sung ảnh gương,
với nhãn cột đổi từ `c` thành `6 − c`. Validation dùng để chọn checkpoint; test
chỉ được đọc một lần sau khi chốt mô hình.

### Huấn luyện và chọn mô hình

Quy trình chuẩn:

1. Khởi tạo mạng với seed cố định.
2. Huấn luyện trên tập train, theo dõi loss và accuracy trên tập validation sau
   mỗi epoch.
3. Lưu checkpoint có **validation loss thấp nhất**.
4. Sau khi kết thúc huấn luyện, nạp checkpoint tốt nhất và đánh giá đúng một
   lần trên tập test.

Việc chọn checkpoint theo validation loss thay vì train loss giúp tránh chọn
mô hình đã học thuộc dữ liệu huấn luyện nhưng kém khái quát.

### Hiện tượng quá khớp

Học có giám sát trên dữ liệu hữu hạn dễ gặp quá khớp: train loss tiếp tục giảm
trong khi validation loss tăng trở lại. Khi đó, checkpoint tốt nhất thường nằm
ở epoch tương đối sớm. Trong lần huấn luyện CNN chính của đồ án, train accuracy
tăng đến 88,68% ở epoch 20 nhưng validation accuracy cao nhất chỉ khoảng 59,79%
(epoch 9), còn validation loss thấp nhất ở epoch 5. Đây là lý do báo cáo dùng
checkpoint theo validation loss và không dùng train accuracy làm thước đo cuối.

### Nhiễu nhãn và giới hạn của bắt chước

Nhãn Alpha-Beta không phải “nhãn đúng duy nhất”. Ở một trạng thái, nhiều cột có
thể cùng dẫn tới thắng hoặc cùng là nước hợp lý; Alpha-Beta chỉ chọn một cột
theo thứ tự tìm kiếm và hàm lượng giá. Vì vậy:

- Top-1 accuracy thấp hơn 100% không nhất thiết là lỗi chiến thuật.
- Với tình huống thắng ngay hoặc chặn, cần đo **độ chính xác theo yêu cầu chiến
  thuật** (dự đoán có nằm trong tập nước thắng/chặn hay không), thay vì chỉ so
  khớp với một nhãn duy nhất.
- Mô hình học có giám sát bị giới hạn bởi chuyên gia: nó không thể vượt xa
  chính sách sinh nhãn nếu chỉ tối ưu cross-entropy.

Các biện pháp giảm thiểu trong đồ án:

- đa dạng hóa khai cuộc khi sinh dữ liệu;
- chia theo ván và khử trùng lặp để hạn chế rò rỉ;
- báo cáo cả top-1 và độ chính xác theo tình huống chiến thuật;
- dùng validation loss để chọn checkpoint;
- xem kết quả đối kháng là bằng chứng bổ sung ở giai đoạn giải đấu.

## 2.3.5. Liên hệ với sáu cấp độ tác tử

| Cấp | Tác tử | Tín hiệu học | Hàm mục tiêu |
| --- | --- | --- | --- |
| 1 | Random | Không | Chọn ngẫu nhiên cột hợp lệ |
| 2 | Heuristic | Không | Luật ưu tiên thắng/chặn/an toàn/trung tâm |
| 3 | Alpha-Beta | Không | Tìm kiếm đối kháng có cắt tỉa |
| 4 | MCTS-UCT | Không | Mô phỏng và cân bằng khai thác–khám phá |
| 5 | CNN Policy | Nhãn nước đi Alpha-Beta | Cross-entropy |
| 6 | DQN | Phần thưởng từ tương tác | TD loss trên Q-value |

Như vậy, “học có giám sát” trong đồ án gắn với cấp 5; “học tăng cường” gắn với
cấp 6. Hai hướng dùng chung biểu diễn trạng thái 2×6×7 và chung engine, nhưng
khác nhau ở nguồn tín hiệu học và hàm mục tiêu.

## 2.3.6. Kết luận chương mục

Policy network và value network là hai cách bổ sung để xấp xỉ quyết định của
tác tử. Policy network phù hợp khi có chuyên gia cung cấp nhãn nước đi; value
network phù hợp khi cần đánh giá trạng thái hoặc làm nền cho học tăng cường.
Đồ án chọn policy network cho cấp 5 vì pipeline dữ liệu hiện có sinh trực tiếp
cặp `(trạng thái, nước đi Alpha-Beta)`, đồng thời giữ value network như một
khái niệm lý thuyết và một thành phần của DQN ở cấp 6.

Các giới hạn đã nêu — nhiễu nhãn, quá khớp, khoảng cách giữa accuracy và sức
mạnh thi đấu — được phản ánh trực tiếp trong thiết kế thực nghiệm ở mục 3.4 và
trong cách diễn giải kết quả ở Chương 4.
