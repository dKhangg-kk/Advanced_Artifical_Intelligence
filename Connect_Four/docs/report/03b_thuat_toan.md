# 3.3. Cài đặt thuật toán tác tử cấp 1–4

Bốn tác tử Random, Heuristic, Alpha-Beta và MCTS thực hiện giao diện
`Agent.choose(game) -> int`, trả về chỉ số cột từ 0 đến 6. Mỗi tác tử
kiểm tra danh sách nước đi hợp lệ; nếu danh sách rỗng thì phát sinh
`ValueError`. Các bước thử nước được thực hiện trên bản sao để giữ
nguyên bàn cờ và lịch sử đầu vào. Các thuật toán sử dụng chung hợp đồng
`ConnectFourGame`, chạy được trên cả `ConnectFour` và `ReferenceGame`.

Phần này cụ thể hóa nhóm tác tử cổ điển trong mục 3.1 của proposal.
Mã nguồn là căn cứ cho hành vi triển khai; các thuật toán được giải thích
ở [mục 2.1–2.2](02a_tim_kiem.md). Các thành phần engine và kiến trúc
chung nằm ở [mục 3.1–3.2](03a_kien_truc.md).

## 3.3.1. Cấp 1 — Random

[`RandomAgent`](../../src/connect_four/agents/random_agent.py) lấy
`legal_actions()` rồi dùng `random.Random(seed).choice(legal)` để chọn
đều một cột hợp lệ. Tác tử không xét điểm vị trí hoặc phản ứng đối thủ.
Đây là đối chứng đơn giản để đo tác dụng của luật chiến thuật và tìm kiếm.

Bộ sinh ngẫu nhiên là đối tượng riêng của tác tử, tránh phụ thuộc bộ sinh
toàn cục. Cùng seed và cùng chuỗi lời gọi trên cùng các trạng thái cho
cùng chuỗi lựa chọn; hai lần gọi liên tiếp không buộc phải trả cùng cột
vì bộ sinh đã tiến trạng thái. Random ghi số nút, mô phỏng và độ sâu bằng 0.

## 3.3.2. Cấp 2 — Heuristic

[`HeuristicAgent.choose()`](../../src/connect_four/agents/heuristic.py)
áp dụng các bước theo thứ tự:

```text
Lấy các cột hợp lệ; nếu rỗng thì báo lỗi.
Nếu có nước thắng ngay: chọn một nước thắng theo seed và trả về.
Nếu đối thủ có nước thắng ngay: tập ứng viên là các cột chặn.
Nếu không: tập ứng viên là tất cả cột hợp lệ.
Tạo trạng thái con cho từng ứng viên.
Giữ các ứng viên không để đối thủ thắng ngay ở lượt sau, nếu có.
Nếu không còn ứng viên an toàn: giữ tập ứng viên trước bước lọc.
Chấm điểm các trạng thái con theo người đang đi ở gốc.
Chọn ngẫu nhiên theo seed trong các ứng viên có điểm cao nhất.
```

Thứ tự này bảo đảm luật thắng ngay được xét trước chặn và luật an toàn
được xét trước điểm vị trí. Ví dụ, chuỗi nước `[0, 6, 0, 6, 0, 6]` đưa
người 1 đến lượt, có thể thắng tại cột 0 trong khi đối thủ đe dọa cột 6;
Heuristic chọn thắng tại cột 0. Nếu đối thủ có hai nước thắng độc lập mà
không thể chặn cả hai, tác tử vẫn trả nước hợp lệ trong các cột chặn;
không tuyên bố có thể tránh thua ở mọi thế cờ.

Hàm `score(game, player)` trả điểm theo `player` được chỉ định. Ở trạng
thái kết thúc, điểm là `game.result(player) * win`. Nếu chưa kết thúc,
điểm gồm lợi thế vị trí, chuỗi quân và số nước có thể thắng ngay:

$$
E(s,p)=C(s,p)+100n_{p,3}+10n_{p,2}
-80n_{q,3}-10n_{q,2}+9000t_p-5000t_q,
$$

trong đó $q$ là đối thủ; $n_{p,k}$ đếm cửa sổ bốn ô có đúng $k$
quân của $p$ và không có quân đối thủ; $t_p$ là số cột thắng ngay
của $p$. Các hệ số trên là giá trị mặc định, không phải kết quả học
hoặc tối ưu siêu tham số.

Thành phần vị trí với cột $c\in\{0,\ldots,6\}$ là:

$$
C(s,p)=6\sum_{r=0}^{5}\sum_{c=0}^{6}
(3-|c-3|)\left(\mathbb{1}[B_{r,c}=p]-\mathbb{1}[B_{r,c}=q]\right).
$$

Một quân ở cột 3 đóng góp 18 điểm; cột 2 hoặc 4 là 12 điểm; cột 1 hoặc
5 là 6 điểm; cột biên là 0. Hàm điểm xét 69 cửa sổ bốn ô theo cả ngang,
dọc và hai đường chéo. Cửa sổ không có quân đối thủ chưa chắc là đe dọa
có thể thực hiện ngay do trọng lực; `winning_moves()` được tính riêng
để nhận biết các nước thắng hợp lệ.

| Khóa trọng số | Mặc định | Vai trò |
| --- | --- | --- |
| `win` | 10000 | Điểm thắng cuối ván; thua lấy dấu âm |
| `block` | 9000 | Hệ số số nước thắng ngay của bên được lượng giá |
| `avoid_opponent_win` | 5000 | Hệ số trừ số nước thắng ngay của đối thủ |
| `own_three` | 100 | Cửa sổ có ba quân mình, không có quân đối thủ |
| `own_two` | 10 | Cửa sổ hai quân mình; cũng dùng để trừ cửa sổ hai quân đối thủ |
| `opponent_three` | 80 | Hệ số trừ cửa sổ ba quân đối thủ |
| `center_bonus` | 6 | Hệ số nhân mức gần cột giữa |

Các trọng số có trong `DEFAULT_WEIGHTS` và
[`configs/agents.yaml`](../../configs/agents.yaml). Constructor Heuristic
nhận `weights` trực tiếp; bản thân lớp không tự đọc YAML. Alpha-Beta tạo
`HeuristicAgent()` nội bộ nên dùng trọng số mặc định trong mã. Tên `block`
và `avoid_opponent_win` là hệ số hàm điểm; thứ tự thắng/chặn/an toàn trong
`choose()` được quyết định bằng các nhánh luật riêng.

Hàm điểm chưa chặn miền giá trị của trạng thái chưa kết thúc. Vì vậy,
điểm cuối ván $\pm10000$ không phải cận được bảo đảm cho mọi điểm
heuristic; không thể diễn giải điểm này thành xác suất thắng hoặc lời
chứng minh thắng bắt buộc. Các trọng số tấn công/phòng thủ không đối xứng
cũng là lý do Alpha-Beta phải giữ góc nhìn lượng giá ở gốc.

## 3.3.3. Cấp 3 — Negamax với Alpha-Beta

[`AlphaBetaAgent`](../../src/connect_four/agents/alphabeta.py) duyệt
trạng thái con bằng `clone_after(action)`. Tại lá hết độ sâu hoặc cuối
ván, giá trị là `color * HeuristicAgent.score(game, root_player)`.
Khi xuống con, thuật toán giảm độ sâu, đổi dấu `color`, đổi cửa sổ thành
`(-beta, -alpha)` và lấy âm giá trị trả về. Giữ `root_player` cố định
giúp kết quả tương đương Minimax max/min dùng cùng hàm điểm.

Hai công tắc phục vụ đối chiếu:

- `use_pruning=True` cập nhật alpha và dừng nhánh khi `alpha >= beta`;
  tắt công tắc thì duyệt đầy đủ cây ở độ sâu yêu cầu.
- `use_ordering=True` duyệt cột theo `(3, 2, 4, 1, 5, 0, 6)`, bỏ cột
  không hợp lệ; tắt thì dùng thứ tự từ `legal_actions()`.

Khi điểm bằng nhau, tác tử giữ hành động được xét trước. Tham số `seed`
thuộc giao diện chung nhưng không dùng để phá hòa ở Alpha-Beta. Các công
tắc giữ nguyên giá trị tối ưu, song có thể làm đổi hành động giữa các
nước đồng hạng. Cài đặt chưa có bảng chuyển vị, lưu cây giữa các lượt
hoặc thưởng riêng cho thắng sớm.

Tác tử hỗ trợ hai chế độ ngân sách:

| Chế độ | Hành vi |
| --- | --- |
| `Budget(depth=d)` | Tìm một vòng đến độ sâu `d`, với `d` là số nguyên dương |
| `Budget(time_s=t)` | Tìm sâu dần từ 1 đến số ô còn trống, dừng khi hết thời gian |

Ở chế độ thời gian, chỉ vòng hoàn tất mới cập nhật nước tốt nhất và
`depth_reached`; nút đã duyệt của vòng bị ngắt vẫn được tính. Nếu chưa
hoàn tất vòng đầu, trả cột hợp lệ đầu tiên theo thứ tự duyệt. Ngân sách
0 giây cũng dùng nước dự phòng này. Tác tử từ chối ngân sách số mô phỏng,
độ sâu không hợp lệ và thời gian âm hoặc không hữu hạn.

Độ sâu mặc định là 5. Độ sâu tính theo từng nước của một bên (*ply*),
không phải một cặp lượt. Chẳng hạn độ sâu 2 xét nước của tác tử rồi
phản ứng đối thủ; độ sâu 1 không bảo đảm nhận biết mọi đe dọa ở lượt sau.
Chi tiết bổ sung ở [hướng dẫn Alpha-Beta](../ALPHABETA.md).

## 3.3.4. Cấp 4 — MCTS với UCT

[`MCTSNode`](../../src/connect_four/agents/mcts.py) lưu cha, hành động
đi vào nút, các con, số lần thăm `visits`, tổng kết quả `wins` và danh
sách nước chưa mở rộng `untried`. Mỗi lần `MCTSAgent.choose()` tạo cây
mới. Với một mô phỏng, tác tử sao chép bàn gốc rồi thực hiện:

1. **Chọn:** khi nút đã thử hết nước và còn con, chọn con có UCT lớn nhất,
   thực hiện nước của con trên bản sao và tiếp tục đi xuống.
2. **Mở rộng:** nếu còn nước chưa thử, chọn một nước theo bộ sinh có seed,
   tạo một con và lấy các nước hợp lệ của trạng thái mới. Mỗi vòng thêm
   tối đa một nút.
3. **Mô phỏng:** chọn đều các nước hợp lệ cho cả hai bên đến khi ván kết
   thúc. Không gọi Heuristic, CNN hoặc luật thắng/chặn bổ sung.
4. **Cập nhật:** lấy `result(root_player)` và cộng kết quả dọc đường về
   gốc. Ở độ sâu lẻ cộng kết quả đó; ở độ sâu chẵn cộng giá trị đối dấu,
   nên mỗi nút lưu lợi ích của người vừa đi vào nó.

UCT dùng `wins / visits + c * sqrt(log(parent.visits) / visits)`.
Mặc định `c = 1.414`; đây là tham số khởi điểm, chưa phải hệ số tối ưu
đã được thực nghiệm xác nhận. Con mới được mô phỏng/cập nhật trước lần
selection tiếp theo nên không áp dụng công thức cho con có 0 lượt thăm.
Khi UCT bằng nhau, phép `max` giữ con được mở trước; thứ tự mở phụ thuộc seed.

Sau khi hết ngân sách, tác tử chọn ngẫu nhiên theo seed trong các con
có số lần thăm lớn nhất. Chỉ con có ít nhất một mô phỏng hoàn tất mới
được xét. Nếu chưa có con như vậy, tác tử chọn một cột hợp lệ ngẫu nhiên.

MCTS nhận `Budget(simulations=n)` hoặc `Budget(time_s=t)`. Số mô phỏng
phải là số nguyên không âm; thời gian và `c` phải hữu hạn, không âm.
Tác tử từ chối ngân sách độ sâu và ngân sách rỗng. Mặc định là 1000 mô
phỏng/nước; cấu hình đánh giá K3 dùng 500 là một cấu hình riêng.

Nếu hết giờ trong rollout, mô phỏng dở không tăng `simulations` và
không cập nhật điểm. Nút đã tạo vẫn được tính vào `nodes`. Ngân sách 0
không chạy rollout và trả nước dự phòng. Chế độ số mô phỏng có thể tái
lập với cùng seed, trạng thái và chuỗi gọi; chế độ thời gian có thể
hoàn tất số mô phỏng khác nhau do tốc độ máy. Chi tiết và kiểm thử cây
bẫy đối thủ nằm ở [hướng dẫn MCTS](../MCTS.md).

## 3.3.5. Thống kê và tích hợp

Các lớp dùng [`Budget` và `SearchStats`](../../src/connect_four/agents/base.py).
Một `Budget` chỉ được đặt tối đa một trong `depth`, `simulations`,
`time_s`; mỗi tác tử tiếp tục kiểm tra loại và miền giá trị mà nó hỗ trợ.
Registry trong [`agents/__init__.py`](../../src/connect_four/agents/__init__.py)
đăng ký bốn tên `random`, `heuristic`, `alphabeta` và `mcts`.

| Trường | Random/Heuristic | Alpha-Beta | MCTS |
| --- | --- | --- | --- |
| `nodes` | Random: 0; Heuristic: số trạng thái con được tạo, 0 nếu thắng ngay | Số lần thăm nút, gồm gốc và các vòng tìm sâu dần, kể cả vòng dở | Số nút cây được cấp phát, gồm gốc và nút của vòng dở |
| `simulations` | 0 | 0 | Số rollout hoàn tất và đã cập nhật |
| `depth_reached` | Random: 0; Heuristic: 1 khi chấm điểm, 0 nếu thắng ngay | Độ sâu mục tiêu của vòng hoàn tất gần nhất | Độ sâu cây lớn nhất trong vòng hoàn tất, không gồm độ dài rollout |
| `extra["eval_score"]` | Heuristic: điểm của nước chọn; Random không ghi | Điểm từ góc nhìn gốc của vòng hoàn tất | Điểm trung bình của con chọn theo người ở gốc |

Alpha-Beta và MCTS tự đo `time_ms`; thời gian nước đi để so sánh cả bốn
tác tử cần lấy từ bộ chạy trận, vì Random/Heuristic không tự điền phép
đo này. Ngắt theo thời gian được kiểm tra giữa các thao tác; một lần
clone, bước engine hoặc lượng giá đang chạy có thể khiến thời gian thực
tế vượt ngân sách. Đây là giới hạn kiểm tra bằng phần mềm, không phải
hạn thời gian cứng.

Ví dụ tái lập số nút: trên bàn trống, Alpha-Beta độ sâu 2 khi tắt cắt
tỉa thăm `1 + 7 + 49 = 57` nút. MCTS với ngân sách 25 mô phỏng hoàn tất
25 rollout nếu không dùng hạn thời gian. Hai số này có ý nghĩa khác
nhau, không dùng để quy đổi trực tiếp lượng tính toán.

## 3.3.6. Kiểm chứng và liên hệ thực nghiệm

Các kiểm thử hiện có đối chiếu hành vi trên cả hai engine:

| Tệp kiểm thử | Nội dung liên quan |
| --- | --- |
| [`test_agents.py`](../../tests/test_agents.py) | Random/Heuristic trả nước hợp lệ, seed, giữ nguyên bàn và từ chối ván kết thúc |
| [`test_heuristic.py`](../../tests/test_heuristic.py) | Ưu tiên thắng/chặn/an toàn, hòa điểm, cửa sổ bốn hướng, hòa và góc nhìn điểm |
| [`test_alphabeta.py`](../../tests/test_alphabeta.py) | Đối chiếu Minimax max/min độc lập ở độ sâu 1–4, công tắc cắt tỉa/sắp xếp, thống kê, giữ vòng hoàn tất khi hết giờ |
| [`test_mcts.py`](../../tests/test_mcts.py) | Bốn bước UCT qua cây bẫy đối thủ, đổi dấu kết quả, số mô phỏng, seed, ngân sách và rollout bị ngắt |

Chạy trong thư mục `Connect_Four`, với môi trường đã cài thư viện dự án:

```bash
python -m pytest -q tests/test_agents.py tests/test_heuristic.py tests/test_alphabeta.py tests/test_mcts.py
python -m pytest -q
```

Kiểm thử chức năng không thay thế đánh giá sức mạnh. Kết quả đối đầu,
độ trễ và các khảo sát A1 (cắt tỉa), A2 (ngân sách MCTS), A5 (độ sâu)
cần log chạy thực tế, cấu hình và `run_id` tương ứng ở Chương 4.
Các mức ngân sách trong cấu hình khảo sát là kế hoạch thí nghiệm,
không phải kết quả đã đạt. Phần này không suy ra tỷ lệ thắng hoặc
kết luận Alpha-Beta mạnh hơn MCTS từ việc bộ kiểm thử đạt.
