# Kết quả thực nghiệm

Thư mục này chứa log thô, bảng tổng hợp và hình. Quy ước đầy đủ về `run_id`,
schema và cách truy vết số liệu nằm trong
[`docs/LOGGING.md`](../docs/LOGGING.md).

## Cấu trúc

| Thư mục / file | Nội dung |
|---|---|
| `logs/run_manifest.csv` | Một dòng cho mỗi lần chạy: commit, config, seed, môi trường, trạng thái |
| `logs/games_<run_id>.csv` | Một dòng cho mỗi ván: đối thủ, bên đi trước, chuỗi nước, kết quả, thời gian, nodes/simulations |
| `logs/moves_<run_id>.csv` | Một dòng cho mỗi nước: thời gian, nodes, simulations, depth, eval score |
| `logs/train_cnn_<run_id>.csv` | Một dòng cho mỗi epoch CNN |
| `logs/train_dqn_<run_id>.csv` | Một dòng cho mỗi episode/mốc đánh giá DQN |
| `logs/ablation_<run_id>.csv` | Một dòng cho mỗi cấu hình/seed/độ đo ablation |
| `logs/templates/` | Header CSV mẫu, không chứa số liệu |
| `tables/` | Bảng tổng hợp sinh từ log thô |
| `tables/report_numbers.csv` | Bảng truy vết từng con số trong báo cáo về log nguồn |
| `figures/` | Biểu đồ sinh từ log/bảng |

## Cột bắt buộc trong log ván

```text
run_id, game_id, pair, agent_a, agent_b, a_starts, opening_id,
moves, winner, n_moves,
mean_ms_a, p95_ms_a, mean_ms_b, p95_ms_b,
nodes_a, nodes_b, simulations_a, simulations_b,
over_budget_a, over_budget_b
```

- `winner`: `a`, `b` hoặc `draw`.
- `a_starts = 1` nghĩa là tác tử A đi trước.
- `moves`: chuỗi cột cách nhau bằng dấu cách, ví dụ `3 2 4 3`.

## Cột bắt buộc trong log nước

```text
run_id, game_id, ply, player, agent, action, legal_actions,
time_ms, nodes, simulations, depth_reached, eval_score, is_terminal
```

Log nước là nguồn để tính `mean_ms`, `p95_ms`, `nodes`, `simulations`.
Không tính các chỉ số này từ log ván nếu log nước đã có.

## Quy tắc

- **Không sửa tay** file trong `logs/`; muốn sửa thì chạy lại và ghi `run_id` mới.
- Mỗi lần chạy phải có một dòng trong `run_manifest.csv` và một mục trong
  [`docs/EXPERIMENT_LOG.md`](../docs/EXPERIMENT_LOG.md).
- Mỗi `run_id` chỉ dùng cho một lần chạy; không tái sử dụng.
- Lần chạy lỗi vẫn ghi manifest với `status=failed` và lý do.
- Bảng/biểu đồ trong báo cáo phải tạo lại được từ `logs/` bằng notebook/script.
- Không chọn lọc ván thắng để minh họa kết luận.
- Mọi số `measured`/`derived` trong báo cáo phải có mặt trong
  `tables/report_numbers.csv` và trỏ đúng file log.

## Ghi log từ code

```python
from connect_four.evaluation import GameRecord, save_run
from connect_four.evaluation.runlog import make_manifest_row, append_manifest

run_id = "tournament-default-20261106T143000Z-s20261102"
records = [...]  # list[GameRecord]

games_path, moves_path = save_run(records, "results/logs", run_id=run_id)
append_manifest(
    "results/logs/run_manifest.csv",
    make_manifest_row(run_id, config_file="configs/tournament_default.yaml"),
)
```
