# K3 — MCTS với UCT (issue #14)

## Đã thay đổi gì?

Trước K3, `MCTSNode` chỉ giữ dữ liệu, `MCTSAgent.choose()` ném
`NotImplementedError`. Hiện `choose()` thực hiện đủ bốn bước, nhận ngân sách
mô phỏng hoặc thời gian, trả cột hợp lệ và ghi thống kê. Giữ constructor cũ
`MCTSAgent(simulations, c, seed)`; thêm tham số keyword `budget` giống hợp đồng
`Agent`. `budget` được ưu tiên khi truyền cùng `simulations`.

Không thay engine, Random, Heuristic hoặc Alpha-Beta. Registry đã có `mcts`,
CLI chơi đã nhận `--simulations`, cấu hình `agents.yaml` đã khai báo `c` và
rollout random nên tái sử dụng các phần đó. Không thêm thư viện.

## Một mô phỏng diễn ra thế nào?

1. **Selection:** clone bàn gốc; từ gốc đi theo con có UCT lớn nhất cho đến
   nút còn nước chưa thử hoặc nút kết thúc.
2. **Expansion:** chọn ngẫu nhiên một nước chưa thử, tạo đúng một con và
   khởi tạo danh sách nước hợp lệ của con. Mỗi mô phỏng thêm tối đa một nút.
3. **Simulation:** từ con vừa tạo (hoặc nút kết thúc đã có), chọn ngẫu nhiên
   đều trong các nước hợp lệ cho đến khi thắng/thua/hòa. Đây là rollout random,
   không gọi Heuristic và không có luật thắng/chặn được chèn vào trước tìm kiếm.
4. **Backpropagation:** tăng `visits` và cộng kết quả dọc đường về gốc.
   Kết quả thắng/hòa/thua là `+1/0/-1`.

UCT của một con:

```text
wins / visits + c * sqrt(log(parent.visits) / visits)
```

`wins` là tổng điểm của **người vừa đi vào nút đó**. Vì vậy, ở tầng của đối thủ,
UCT cũng tối đa hóa lợi ích của đối thủ, thay vì giả định đối thủ giúp mình.
Khi cập nhật ngược, góc nhìn đổi sau mỗi tầng. Gốc lưu điểm của người trước
lượt gốc, chỉ dùng `visits` của gốc cho UCT và đếm mô phỏng.
Mỗi con mới được rollout và cập nhật trước lần selection tiếp theo nên
không chia cho 0. Nếu hết giờ giữa chừng thì thoát luôn vòng tìm kiếm.

Sau hết ngân sách, chọn con có **số lần thăm lớn nhất**, không chọn bằng điểm
UCT (UCT dành cho việc khám phá trong lúc tìm kiếm). Nếu bằng số lần thăm,
chọn theo bộ sinh ngẫu nhiên riêng có seed. Khi UCT bằng nhau, giữ con được
mở trước; thứ tự mở cũng phụ thuộc seed.

## Ngân sách và cách gọi

```python
from connect_four.agents import Budget, MCTSAgent
from connect_four.game import ConnectFour

game = ConnectFour()
agent = MCTSAgent(budget=Budget(simulations=500), seed=0)
action = agent.choose(game)
assert action in game.legal_actions()
assert agent.last_stats.simulations == 500
assert game.moves_played() == ()

timed = MCTSAgent(budget=Budget(time_s=0.1), seed=0)
action = timed.choose(game)
```

- Mô phỏng phải là số nguyên không âm; thời gian và `c` phải hữu hạn, không âm.
  Từ chối `Budget(depth=...)` và `Budget()` rỗng cho MCTS.
- Ngân sách bằng 0 trả nước ngẫu nhiên hợp lệ mà không chạy mô phỏng.
- Kiểm tra hạn giờ giữa các bước cây và từng nước rollout. Một thao tác engine
  đang chạy có thể làm quá hạn nhẹ; đây không phải giới hạn thời gian cứng.
- Rollout bị ngắt không được cộng vào `simulations` và không cập nhật điểm.
  Nút đã cấp phát vẫn được tính trong `nodes`. Chọn trong các con đã được thăm;
  nếu chưa có con nào hoàn tất, dùng nước hợp lệ dự phòng.
- Ván đã kết thúc ném `ValueError`. Mỗi `choose()` tạo cây mới và đặt lại thống kê.
- Seed tái lập được trong chế độ số mô phỏng; thời gian thật có thể làm số mô
  phỏng khác nhau giữa các lần chạy, kể cả cùng seed.

`last_stats`: `nodes` gồm gốc và các nút được tạo, `simulations` là số rollout
hoàn tất, `depth_reached` là độ sâu cây lớn nhất của một mô phỏng hoàn tất
(không phải độ dài rollout), `time_ms` là thời gian tìm kiếm,
`extra['eval_score']` là điểm trung bình của con được chọn theo người ở gốc.
Không có `eval_score` khi chưa mô phỏng xong.

## Kiểm thử và đánh giá

Chạy trong `Connect_Four`:

```bash
python -m pytest -o addopts= -q
python -m pytest -o addopts= -q tests/test_mcts.py
PYTHONPATH=src python scripts/evaluate_k3.py
PYTHONPATH=src python -m connect_four.play --a mcts --b random --simulations 500 --auto
```

`tests/test_mcts.py` kiểm tra cả bitboard và reference: nước hợp lệ, cột đầy,
seed, giữ nguyên bàn/lịch sử undo, số mô phỏng chính xác, thắng/chặn khi cả hai
bên đến lượt, nước cuối dẫn đến hòa, ván đã kết thúc, reset, constructor và
registry, ngân sách sai, đồng hồ thật và ngắt giữa rollout bằng đồng hồ giả.
Một cây trò chơi nhỏ có nhánh bẫy đối thủ kiểm tra selection, expansion,
đổi góc nhìn backpropagation, số lần thăm/điểm từng nút và lựa chọn cuối.

`scripts/evaluate_k3.py` làm theo mẫu K1, dùng lại `play_match`, `save_run` và
manifest. Cấu hình nằm ở `configs/k3_random_mcts.json`: 500 mô phỏng/nước,
200 ván, 100 khai cuộc khác nhau dài 4 nước, mỗi khai cuộc đổi bên hai lần;
seed khai cuộc/MCTS = 0, Random = 1. Script phát lại **tất cả** chuỗi nước để
đối chiếu kết quả, lưu log ván/nước, bảng tổng hợp và môi trường, rồi mới
kiểm tra ít nhất 190/200 ván thắng. Nếu không đạt vẫn giữ log thất bại.

Kết quả cụ thể và liên kết log nằm trong [nhật ký thực nghiệm](EXPERIMENT_LOG.md).
Tỷ lệ này là kết quả trên một cấu hình và bộ seed cố định, không bảo đảm cho
mọi seed/khai cuộc và không suy ra sức mạnh trước Alpha-Beta. Ablation A2
100–5000 mô phỏng và giải đấu M3 vẫn là công việc riêng.

## Công cụ hỗ trợ và phần cần tự giải thích

Codex hỗ trợ đọc issue và dự án; viết phần vòng lặp UCT từ khung sẵn có;
viết test, cấu hình, script đánh giá; chạy test/đánh giá, đọc log;
soạn hướng dẫn, nhật ký đóng góp và PR. Tái sử dụng API và hệ thống ghi log
của nhóm. Không ghi nhận toàn bộ phần này là mã tác giả tự viết thủ công.

Khi review, tác giả cần tự giải thích: vì sao lưu điểm theo người vừa đi,
vì sao UCT ở tầng đối thủ vẫn lấy max, khác biệt UCT và số lần thăm cuối,
vì sao rollout hết giờ không được tính, và cách đổi bên trong 200 ván.
Thời gian cá nhân và mức độ hiểu do tác giả xác nhận, không suy từ thời gian
chạy tự động. Chờ Đức review/approve trước khi merge; không tự merge.
