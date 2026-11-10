# Alpha-Beta K2 — cách hoạt động và kiểm tra

Phạm vi: [issue #13](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/issues/13).
Mã ở `src/connect_four/agents/alphabeta.py`, test ở `tests/test_alphabeta.py`.

## 1. Chọn nước theo độ sâu

`AlphaBetaAgent(budget=Budget(depth=4))` tìm tối đa bốn nước tính từ bàn hiện tại.
`choose(game)` thử các cột hợp lệ trên bản sao `clone_after()`, chọn nước có điểm
lớn nhất và giữ nguyên bàn đầu vào. Nếu ván đã kết thúc thì ném `ValueError`.
Nếu nhiều nước cùng điểm, giữ nước được duyệt trước; không dùng ngẫu nhiên.

`negamax()` là cách viết gọn minimax: điểm ở cha được tính bằng âm của điểm
ở con. Khi xuống con, cửa sổ tìm kiếm đổi từ `(alpha, beta)` thành
`(-beta, -alpha)`. Ở lá, dùng điểm của `HeuristicAgent.score()`.

Hàm điểm hiện tại có trọng số tấn công/phòng thủ khác nhau, nên không bảo đảm
`score(game, 1) == -score(game, 2)`. Vì vậy luôn đánh giá từ người chơi ở gốc
và nhân `color` (+1/-1) khi đổi lượt. Không thay đổi trọng số hoặc hành vi của
Heuristic để tránh ảnh hưởng công việc K1.

Test tham chiếu dùng minimax max/min riêng, luôn tính điểm từ người chơi ở
gốc. Bản test cũ đổi người tính điểm theo tầng giống Negamax nên bỏ sót lỗi:
thế cờ `[3, 2, 3, 4, 1]`, độ sâu 3, kết quả từng lệch minimax.

## 2. Cắt tỉa, sắp xếp và đếm nút

- `use_pruning=True`: cập nhật alpha và bỏ nhánh khi `alpha >= beta`.
- `use_pruning=False`: duyệt đầy đủ, dùng để đối chiếu.
- `use_ordering=True`: duyệt cột theo `CENTER_FIRST`, bỏ cột không hợp lệ.
- `use_ordering=False`: dùng thứ tự từ `legal_actions()`.

Hai tùy chọn giữ nguyên giá trị tối ưu ở cùng độ sâu; cột được chọn có thể
khác nếu nhiều nước hòa điểm. Sắp xếp nước không bảo đảm giảm số nút ở mọi
thế cờ. Độ sâu 1 cũng không bảo đảm chặn nước thắng ở lượt kế tiếp của đối thủ.

`last_stats` được đặt lại cho mỗi lần chọn nước hợp lệ:

| Trường | Ý nghĩa |
| --- | --- |
| `nodes` | Số lần thăm nút, tính cả gốc; cộng các vòng tìm sâu dần và vòng bị ngắt |
| `depth_reached` | Độ sâu mục tiêu của vòng tìm đã hoàn tất gần nhất; 0 nếu chưa xong vòng nào |
| `time_ms` | Thời gian thực tế cho lượt chọn nước, đơn vị mili giây |
| `extra["eval_score"]` | Điểm từ người chơi ở gốc của vòng hoàn tất gần nhất; không có nếu chỉ dùng nước dự phòng |

Ví dụ không cắt tỉa, bàn trống, độ sâu 2: `1 + 7 + 49 = 57` nút.

## 3. Chọn nước theo thời gian

`AlphaBetaAgent(budget=Budget(time_s=0.1))` tìm sâu dần 1, 2, 3… đến hết giờ
hoặc hết số nước còn lại. Chế độ này không bị giới hạn bởi `depth=5` mặc định.
Chỉ cập nhật kết quả sau một vòng hoàn tất; vòng đang tìm dở không ghi đè
kết quả trước đó. Kiểm tra hạn giờ trong cả vòng gốc lẫn đệ quy.

Nếu ngân sách bằng 0 hoặc hết giờ trước vòng đầu, trả nước hợp lệ đầu tiên
theo thứ tự đã chọn. Hạn giờ được xóa trong `finally` để lần gọi sau không
bị ảnh hưởng. Không nhận số mô phỏng, độ sâu không phải số nguyên dương, thời gian
âm, NaN hoặc vô hạn.

Đây là kiểm tra giờ giữa các thao tác; một lần sao chép bàn hoặc lượng giá
có thể khiến thời gian thực tế vượt nhẹ ngân sách. Không phải hạn cứng của
hệ điều hành.

## 4. Kiểm tra lại

Trong `Connect_Four`, với môi trường Python có các thư viện của dự án:

```bash
python -m pytest tests/test_alphabeta.py -q
python -m pytest -q
```

Test chạy trên cả `ConnectFour` và `ReferenceGame`: đối chiếu minimax ở độ sâu
1–4, hai lượt người chơi, bốn tổ hợp công tắc, thắng/chặn, cột đầy, ván hòa,
giữ nguyên bàn, ngân sách, thống kê và đặt lại trạng thái. Test đồng hồ giả
kiểm tra ngắt đúng giữa vòng; test đồng hồ thật dùng ngưỡng rộng để tránh
phụ thuộc tốc độ máy. Log lần kiểm tra K2 ở
[`results/logs/k2_pytest_20261110.txt`](../results/logs/k2_pytest_20261110.txt).

## 5. Nội dung cần tự giải thích khi review

1. Vì sao đổi dấu và cửa sổ alpha/beta khi xuống con?
2. Vì sao giữ người chơi ở gốc dù Negamax đổi lượt?
3. Vì sao cắt tỉa không thay đổi giá trị tối ưu?
4. Vì sao hết giờ phải giữ vòng đã hoàn tất?
5. Vì sao hai nước khác cột vẫn có thể đúng khi cùng điểm?

Code và test được hoàn thiện với Codex/Ponytail từ phần tác giả đã viết.
Tác giả cần đọc, chạy lại và tự xác nhận khả năng giải thích trước khi review.
