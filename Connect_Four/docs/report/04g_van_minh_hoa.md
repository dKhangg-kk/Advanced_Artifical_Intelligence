# 4.6. Minh họa ván cờ và phân tích thất bại

Phân tích dưới đây lấy từ log thô, không chọn riêng ván thắng. Hai ván đầu
minh họa hai cặp đấu có run thực tế; phần thất bại xét ván thua duy nhất của
MCTS trong run MCTS–Random. Đây là pilot theo seed/cấu hình đã ghi, không phải
giải đấu đầy đủ giữa mọi tác tử.

## Ván đầu tiên của các cặp đấu tiêu biểu

| run_id | game_id | Cặp đấu | Kết quả | Nước đi (cột 0–6) |
| --- | --- | --- | --- | --- |
| `k1-heuristic-random-20261109T061032Z-s0` | `heuristic_vs_random-g000` | Heuristic – Random | Heuristic thắng | `6 3 6 3 6 1 6` |
| `k3-mcts-random-20261110T181313Z-s0` | `mcts_vs_random-g000` | MCTS – Random | MCTS thắng | `6 3 6 3 4 1 6 4 6` |

Nguồn: `results/logs/games_<run_id>.csv`; log nước tương ứng nằm trong
`results/logs/moves_<run_id>.csv`. Cả hai là ván đầu tiên (`g000`) của run.

## Ván thua của tác tử mạnh nhất trong các run hiện có

Trong run MCTS–Random có 200 ván: MCTS thắng 199, hòa 0, thua 1. Đây là tỷ lệ
của pilot cố định, không phải khẳng định tổng quát. Ván thua duy nhất:

| run_id | game_id | Bên đi trước | Kết quả | Nước đi |
| --- | --- | --- | --- | --- |
| `k3-mcts-random-20261110T181313Z-s0` | `mcts_vs_random-g085` | Random | Random thắng | `2 6 1 1 3 0 4` |

### Bước ngoặt

Theo quy ước log, cột `moves` là chuỗi nước theo thứ tự; số `ply` trong
`moves_*.csv` bắt đầu từ 0. Trước nước MCTS tại `ply=5`, bàn cờ có dạng sau
(hàng 0 là hàng đáy; `R` = Random, `M` = MCTS):

```text
       c0 c1 c2 c3 c4 c5 c6
r5     .  .  .  .  .  .  .
r4     .  .  .  .  .  .  .
r3     .  .  .  .  .  .  .
r2     .  .  .  .  .  .  .
r1     .  M  .  .  .  .  .
r0     .  R  R  R  .  .  M
```

MCTS chọn cột 0; nước này hợp lệ nhưng không chặn hàng ngang đang mở ở đáy.
Random thả cột 4 tại `ply=6`, tạo bốn quân liên tiếp tại cột 1–4 và kết thúc ván:

```text
       c0 c1 c2 c3 c4 c5 c6
r1     .  M  .  .  .  .  .
r0     M  R  R  R  R  .  M   ← Random thắng ngang
```

### Nguyên nhân và giới hạn kết luận

- Log ghi MCTS đã dùng 500 mô phỏng ở nước sai lầm; `depth_reached=4`,
  `over_budget_a=0`. Vì vậy bằng chứng của ván này **không ủng hộ** nguyên nhân
  hết ngân sách thời gian. `depth_reached` là giá trị do tác tử ghi lại, không
  chứng minh mọi nước thắng đối thủ được giải chính xác đến độ sâu đó.
- Trạng thái bàn cờ và nước đi kế tiếp cho thấy tác tử bỏ lỡ nước chặn cột 4.
  Đây là mô tả quan sát được. Log không lưu phân phối UCT, cây tìm kiếm hay lời
  giải exact tại vị trí, nên không thể kết luận sâu hơn rằng nguyên nhân cụ thể
  là một nhánh rollout, đòn kép hay giới hạn thuật toán nào.
- Log nước của ván này bắt đầu từ `ply=4`; chuỗi đầy đủ lấy từ bản ghi ván
  `games.csv`, còn ngân sách lấy từ các hàng nước thực sự có. Không giả định
  rằng `moves.csv` lưu đầy đủ mọi ply.

Nguồn trực tiếp: `results/logs/games_k3-mcts-random-20261110T181313Z-s0.csv`
và `results/logs/moves_k3-mcts-random-20261110T181313Z-s0.csv`. Bảng tổng hợp
199–0–1 nằm trong `results/tables/k3-mcts-random-20261110T181313Z-s0.csv`.

### Đối chiếu `report_numbers.csv`

`results/tables/report_numbers.csv` hiện có các số K1 cho mục 4.1, nhưng chưa
có hàng cho run K3 hoặc mục 4.6. Vì vậy số 199–0–1 ở trên được đối chiếu trực
tiếp với bảng K3 và log thô, **không** được ghi là số đã có trong
`report_numbers.csv`. Cần người phụ trách bảng số liệu bổ sung hàng truy vết
trước khi hợp nhất/chốt báo cáo; tệp bảng dùng chung không bị sửa trong phần
việc này.
