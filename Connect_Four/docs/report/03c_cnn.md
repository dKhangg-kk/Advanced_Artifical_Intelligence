# 3.4. Cấp 5 — CNN Policy: dữ liệu, mô hình và quy trình huấn luyện

Cấp 5 dùng một mạng nơ-ron tích chập (CNN) để học chính sách chọn nước đi từ
các ván do Alpha-Beta sinh ra. Khác với cấp 1–4, tác tử cấp 5 không duyệt cây
khi suy luận: sau khi huấn luyện, mỗi nước đi chỉ cần một lượt lan truyền tiến
qua mạng.

Mục này mô tả đúng pipeline đã chạy: cách sinh và chia dữ liệu, kiến trúc mạng,
quy trình huấn luyện/chọn checkpoint, cùng kết quả thực tế của mô hình chính và
thí nghiệm ablation A3. Mọi số liệu đều có `run_id` và đường dẫn nguồn; các số
kế hoạch được ghi rõ là kế hoạch.

## 3.4.1. Dữ liệu

### Nguồn sinh dữ liệu

Dữ liệu policy được sinh từ các ván Connect Four do `AlphaBetaAgent` độ sâu 4
chơi với chính nó sau một khai cuộc ngẫu nhiên 6–8 nước. Khai cuộc ngẫu nhiên
giúp đa dạng hóa trạng thái khởi đầu; phần còn lại của ván được gán nhãn bằng
nước đi Alpha-Beta chọn.

Mỗi mẫu gồm:

- `game_id`: định danh ván, dùng để chia tập theo ván;
- `ply`: số nước đã đi;
- `state`: tensor 2×6×7;
- `action`: cột Alpha-Beta chọn.

Ngoài ra, mỗi ván lưu chuỗi nước đi, độ sâu Alpha-Beta, kết quả và nhóm sử dụng
(`main_model` hoặc `a3`). Cách lưu này cho phép tái lập và kiểm tra rò rỉ dữ
liệu.

### Quy mô thực tế

Lần sinh dữ liệu seed 0 tạo 5.000 ván duy nhất. Trong quá trình sinh, 16 chuỗi
ván trùng bị loại; các ván còn lại được ghi vào `data/generated/games.jsonl`.
Sau đó dữ liệu được chia theo ván với tỷ lệ 70/15/15, khử trùng lặp và lật gương
tập train.

| Chỉ số | Giá trị | Nguồn |
| --- | ---: | --- |
| Số ván duy nhất | 5.000 | `data/generated/splits/manifest.json` |
| Số mẫu thô trước lọc | 110.083 | `manifest.json`, `raw_examples` |
| Số mẫu trùng/đối xứng bị loại | 18.025 | `manifest.json`, `duplicate_examples_removed` |
| Mẫu train trước lật gương | 66.619 | `manifest.json`, `retained_examples.train` |
| Mẫu validation | 13.028 | `manifest.json`, `retained_examples.val` |
| Mẫu test | 12.411 | `manifest.json`, `retained_examples.test` |
| Mẫu gương bổ sung cho train | 66.589 | `manifest.json`, `mirror_examples_added_to_train` |
| Mẫu train sau lật gương | 133.208 | `manifest.json`, `written_examples.train` |

Tỷ lệ mẫu trước khi lật gương là 72,37% train / 14,15% validation / 13,48%
test, lệch nhẹ so với 70/15/15 do một số trạng thái bị loại vì trùng hoặc đối
xứng. Sau khi bổ sung ảnh gương cho train, tổng số mẫu là 158.647, trong đó
train chiếm 83,97%, validation 8,21% và test 7,82%. Việc lật gương chỉ áp dụng
cho train nên làm tăng tỷ trọng train; validation và test giữ nguyên số mẫu.
Số ván không còn mẫu duy nhất là 186 ở train, 85 ở validation và 101 ở test;
các ván này không xuất hiện trong tập tương ứng.

### Chia theo ván và chống rò rỉ

Thứ tự xử lý:

1. Xáo trộn danh sách `game_id` bằng seed cố định.
2. Chia ván vào train/validation/test theo 70/15/15.
3. Duyệt lần lượt train → validation → test; trạng thái đã xuất hiện ở tập trước
   bị loại khỏi tập sau. Phép so khớp tính cả bản đối xứng qua trục dọc.
4. Chỉ tập train được bổ sung ảnh gương; nhãn cột đổi từ `c` thành `6 − c`.
   Trạng thái đối xứng với chính nó không được nhân đôi.

Nhờ bước 3, không có trạng thái nào xuất hiện ở cả train và test. Đánh đổi là
validation/test có thể mất một phần mẫu so với dự kiến; vì vậy báo cáo dùng số
mẫu thực tế, không dùng số kế hoạch.

### Hai cohort dữ liệu

5.000 ván được chia thành hai cohort ngay từ khâu sinh:

- **`main_model`:** 3.000 ván đầu, dùng cho mô hình CNN chính.
- **`a3`:** 2.000 ván còn lại, dùng riêng cho ablation A3.

Sau chia theo ván và khử trùng lặp, số liệu thực tế như sau:

| Cohort | Tập | Số ván còn mẫu | Số mẫu |
| --- | --- | ---: | ---: |
| `main_model` | train | 1.982 | 79.924 |
| `main_model` | validation | 411 | 7.958 |
| `main_model` | test | 385 | 7.399 |
| `a3` | train | 1.332 | 53.284 |
| `a3` | validation | 254 | 5.070 |
| `a3` | test | 264 | 5.012 |

Hai cohort không dùng chung ván, nên kết quả A3 không rò rỉ sang mô hình chính
và ngược lại. Số ván A3 thực có ít hơn 2.000 vì sau khử trùng lặp chỉ còn 1.332
ván train có mẫu duy nhất; vì vậy cấu hình A3 dùng các mức
`[250, 500, 1000, 1332]` thay vì các mức lớn hơn.

## 3.4.2. Mô hình

### Kiến trúc `CNNPolicyNet`

Mạng nhận tensor đầu vào 2×6×7 và trả về 7 logits, mỗi logit ứng với một cột:

| Thành phần | Cấu hình | Kích thước đầu ra |
| --- | --- | --- |
| Conv 1 | `Conv2d(2, 64, kernel_size=3, padding=1)` + BatchNorm + ReLU | 64×6×7 |
| Conv 2 | `Conv2d(64, 64, kernel_size=3, padding=1)` + BatchNorm + ReLU | 64×6×7 |
| Conv 3 | `Conv2d(64, 64, kernel_size=3, padding=1)` + BatchNorm + ReLU | 64×6×7 |
| Flatten | — | 2.688 |
| Fully connected 1 | `Linear(2688, 128)` + ReLU | 128 |
| Fully connected 2 | `Linear(128, 7)` | 7 |

Các điểm thiết kế:

- `padding=1` giữ nguyên kích thước không gian 6×7 qua ba lớp tích chập, nhờ đó
  mạng học được quan hệ cục bộ giữa các ô gần nhau mà không làm mất biên bàn cờ.
- BatchNorm đặt sau mỗi lớp tích chập giúp ổn định quá trình huấn luyện.
- Không dùng pooling: bàn cờ chỉ có 42 ô, giảm kích thước quá sớm sẽ mất thông
  tin vị trí cần cho các chuỗi bốn ô.
- Lớp cuối trả về logits, không qua softmax; `CrossEntropyLoss` của PyTorch tự
  kết hợp softmax và negative log-likelihood.
- Số tham số tính từ kiến trúc xấp xỉ 420.551, chủ yếu nằm ở lớp
  `Linear(2688, 128)`.

### Biểu diễn đầu vào

Kênh 0 là quân của người đang đi, kênh 1 là quân của đối thủ. Cách biểu diễn
tương đối này cho phép cùng một mạng dùng cho cả hai bên và tránh phải học hai
bộ trọng số khác nhau.

### Chọn nước đi khi suy luận

Khi suy luận, mạng tính logits cho 7 cột. Các cột đã đầy bị gán logit bằng −∞
trước khi lấy `argmax`, nên tác tử luôn trả về cột hợp lệ. Trong đánh giá test,
tỷ lệ nước hợp lệ còn được đo trên đầu ra **chưa che** để kiểm tra mô hình có
tự học được ràng buộc luật chơi hay không.

## 3.4.3. Quy trình huấn luyện

### Siêu tham số

| Tham số | Mô hình chính | Ablation A3 |
| --- | --- | --- |
| Optimizer | Adam | Adam |
| Learning rate | 1e-3 | 1e-3 |
| Hàm mất mát | CrossEntropyLoss | CrossEntropyLoss |
| Số epoch | 20 | 20 |
| Batch size | 256 | 64 |
| Seed | 0 | 20261105 |
| Thiết bị | CPU | CPU |

### Vòng huấn luyện

1. Nạp tập train và validation của cohort tương ứng. Tập test **không** được mở
   trong giai đoạn này.
2. Khởi tạo `CNNPolicyNet(in_channels=2)` với seed cố định.
3. Với mỗi epoch: huấn luyện trên train, sau đó đo loss và accuracy trên
   validation.
4. Nếu validation loss thấp hơn mức tốt nhất đã ghi nhận, lưu checkpoint và ghi
   lại epoch tốt nhất.
5. Ghi log từng epoch vào `train_cnn_<run_id>.csv`.
6. Sau epoch cuối, nạp checkpoint tốt nhất và đánh giá **đúng một lần** trên
   test.

Cơ chế bảo vệ test: trước khi đọc test, chương trình tạo tệp đánh dấu
`test_evaluation_<run_id>.json`. Nếu tệp đã tồn tại, lần đánh giá thứ hai bị từ
chối. Nhờ vậy test không bị dùng lặp lại để chọn mô hình.

### Chọn checkpoint

Checkpoint được chọn theo **validation loss thấp nhất**, không theo train loss
và không theo accuracy. Lý do: loss phản ánh chất lượng phân phối dự đoán, còn
accuracy chỉ quan tâm cột đứng đầu và dễ bão hòa khi nhiều cột gần tương đương.
Trong lần chạy chính, validation loss thấp nhất ở epoch 5; các epoch sau train
loss tiếp tục giảm nhưng validation loss tăng, cho thấy quá khớp.

## 3.4.4. Kết quả chạy thực tế

### Mô hình chính (`main_model`)

Lần huấn luyện chính:

- `run_id`: `20261111T140304Z_87e7371b`
- Dữ liệu: 79.924 mẫu train / 7.958 mẫu validation
- Checkpoint tốt nhất: epoch 5, validation loss 1,08349
- Test: 7.399 mẫu, đọc một lần sau khi chốt checkpoint
- Thời gian huấn luyện: 134,27 giây trên CPU
- Phần cứng: CPU x86_64, không dùng GPU; PyTorch 2.15.0+cu132

| Chỉ số test | Giá trị |
| --- | ---: |
| Test loss | 1,11221 |
| Top-1 accuracy | 56,76% |
| Tỷ lệ dự đoán hợp lệ | 100% |
| Số mẫu test | 7.399 |

Nguồn: `checkpoints/level5_cnn/test_evaluation_20261111T140304Z_87e7371b.json`;
metadata huấn luyện tại `checkpoints/level5_cnn/final.json`; log epoch tại
`checkpoints/logs/train_cnn_20261111T140304Z_87e7371b.csv`.

Kết quả này cho thấy mô hình học được ràng buộc luật chơi rất tốt (100% dự đoán
hợp lệ) và bắt chước đúng nhãn Alpha-Beta ở hơn một nửa số trạng thái test. Tuy
nhiên, 56,76% top-1 chưa đủ để kết luận về sức mạnh thi đấu; cần kết quả đối
kháng ở giai đoạn giải đấu.

### Ablation A3 — ảnh hưởng của số ván huấn luyện

Ablation A3 giữ nguyên kiến trúc, optimizer, số epoch và tập validation/test,
chỉ thay đổi số ván train lấy từ cohort `a3`. Các mức 250, 500, 1.000 và 1.332
ván tạo thành các tập con lồng nhau theo thứ tự split đã xáo trộn.

- `run_id` ablation: `ablation-a3-20261111T150514Z-s20261105`
- Tập validation: 5.070 mẫu; tập test: 5.012 mẫu
- Test có 321 vị trí `win_now`, 568 `block`, 3.090 `center_control` và 1.033
  `other`
- Bốn lần huấn luyện:
  `20261111T150516Z_4ead9059` (250),
  `20261111T150537Z_cde1dfc3` (500),
  `20261111T150613Z_8a36348a` (1.000),
  `20261111T150709Z_a9cc707c` (1.332)

| Ván train | Mẫu train | Epoch tốt nhất | Val loss | Test loss | Top-1 | Thắng ngay (tactical) | Chặn (tactical) | Trung tâm (top-1) | Trung tâm (chọn cột 3) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 250 | 10.857 | 3 | 1,3832 | 1,3959 | 47,19% | 42,37% | 52,99% | 41,55% | 38,51% |
| 500 | 21.098 | 7 | 1,2830 | 1,3088 | 51,74% | 60,44% | 71,30% | 46,44% | 28,83% |
| 1.000 | 40.561 | 5 | 1,1637 | 1,1589 | 55,35% | 58,57% | 73,59% | 50,87% | 21,62% |
| 1.332 | 53.284 | 5 | 1,1150 | 1,1106 | 57,08% | 59,81% | 77,64% | 52,65% | 27,57% |

Nguồn: `results/tables/ablation_a3_results.csv`; log từng epoch tại
`results/logs/train_cnn_<run_id>.csv`; nhật ký đầy đủ tại
`docs/EXPERIMENT_LOG.md`, mục `ablation-a3-20261111T150514Z-s20261105`.

### Diễn giải

- **Top-1 tăng theo dữ liệu:** từ 47,19% lên 57,08%, tức tăng 9,90 điểm phần
  trăm khi số ván train tăng từ 250 lên 1.332. Xu hướng này phù hợp với việc
  mô hình có thêm dữ liệu để khái quát hóa.
- **Chặn là tình huống cải thiện mạnh nhất:** độ chính xác theo yêu cầu chiến
  thuật tăng từ 52,99% lên 77,64% (24,65 điểm phần trăm). Đây là tín hiệu tốt
  vì bỏ sót nước chặn thường dẫn tới thua ngay.
- **Thắng ngay cũng cải thiện:** từ 42,37% lên 59,81% (17,45 điểm phần trăm),
  nhưng không đơn điệu: mức 500 ván đạt 60,44%, cao hơn mức 1.332 ván. Chênh
  lệch này cho thấy cần thêm seed để đánh giá độ ổn định.
- **Kiểm soát trung tâm:** top-1 tăng từ 41,55% lên 52,65% (11,10 điểm phần
  trăm). Chỉ số “chọn đúng cột 3” lại giảm từ 38,51% xuống 27,57%; đây là chỉ
  số chẩn đoán, không phải thước đo sức mạnh, vì nhãn Alpha-Beta độ sâu 4 không
  ưu tiên tuyệt đối cột giữa khi không có nước chiến thuật. Khi tăng dữ liệu,
  mô hình học sát nhãn Alpha-Beta hơn nên tỷ lệ chọn cột giữa giảm.
- **Nhiễu nhãn ở `win_now`:** trong 321 vị trí thắng ngay của tập test, 98 nhãn
  Alpha-Beta (30,5%) không phải nước thắng ngay. Vì vậy top-1 so khớp nhãn
  không phản ánh đúng năng lực chiến thuật ở nhóm này; báo cáo dùng
  `win_now_situation_accuracy` (dự đoán có nằm trong tập nước thắng ngay hay
  không) làm thước đo chính.

## 3.4.5. Hạn chế của thiết kế hiện tại

- **Một seed cho mỗi cấu hình:** mô hình chính dùng seed 0, ablation dùng seed
  20261105. Chưa có khoảng tin cậy, nên các chênh lệch nhỏ giữa các mức chưa
  thể coi là khác biệt có ý nghĩa thống kê.
- **Một kiến trúc, ít tinh chỉnh siêu tham số:** báo cáo chỉ khảo sát ảnh hưởng
  của lượng dữ liệu, chưa khảo sát độ rộng mạng, learning rate, batch size hay
  số epoch.
- **Nhãn phụ thuộc Alpha-Beta độ sâu 4:** mô hình bị giới hạn bởi chuyên gia
  sinh nhãn. Top-1 cao không chứng minh mô hình mạnh hơn Alpha-Beta.
- **Kích thước test nhỏ:** mô hình chính có 7.399 mẫu test từ 385 ván; A3 có
  5.012 mẫu từ 264 ván. Các tỷ lệ phần trăm có thể dao động khi đổi tập test.
- **Chưa đo sức mạnh đối kháng:** báo cáo giữa kỳ chỉ có loss, top-1, tỷ lệ nước
  hợp lệ và độ chính xác theo tình huống. Kết quả đấu với Alpha-Beta/MCTS thuộc
  giai đoạn giải đấu và chưa được dùng để kết luận ở đây.
- **Chỉ chạy trên CPU:** thời gian huấn luyện bị giới hạn bởi CPU, nên quy mô
  khảo sát nhỏ hơn tiềm năng nếu có GPU.

Các hạn chế trên được ghi nhận để tránh diễn giải quá mức. Kết luận về RQ2 sẽ
được hoàn thiện khi có thêm seed, kết quả đối kháng và phân tích ván đấu ở
Chương 4–5.
