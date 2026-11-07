# Quy ước log và truy vết số liệu

Tài liệu này quy định **mọi con số xuất hiện trong báo cáo, slide, poster phải
truy vết được** về một lần chạy cụ thể. Mục tiêu là đáp ứng yêu cầu của giảng
viên: không có số liệu nào được ghi “tay” mà không có log nguồn.

## 1. Ba tầng log

```text
Tầng 1 — Log thô (machine-readable)
    results/logs/run_manifest.csv
    results/logs/games_<run_id>.csv
    results/logs/moves_<run_id>.csv
    results/logs/train_cnn_<run_id>.csv
    results/logs/train_dqn_<run_id>.csv
    results/logs/ablation_<run_id>.csv

Tầng 2 — Bảng tổng hợp (derived)
    results/tables/*.csv

Tầng 3 — Nhật ký người đọc
    docs/EXPERIMENT_LOG.md
    results/tables/report_numbers.csv
```

Nguyên tắc: **bảng và hình phải sinh lại được từ tầng 1**. Tầng 2 và tầng 3
không được chứa số liệu không tìm thấy trong tầng 1 (trừ số kế hoạch, xem mục 5).

## 2. `run_id`

Mỗi lần chạy có đúng một `run_id`, không dùng lại. Định dạng khuyến nghị:

```text
<loai>-<UTC timestamp>-<seed>
```

Ví dụ:

```text
tournament-default-20261106T143000Z-s20261102
ablation-a1-20261106T151500Z-s0
train-cnn-20261107T090000Z-s42
```

Quy tắc:

- `run_id` xuất hiện trong **mọi** file log của lần chạy đó.
- Không sửa file log sau khi chạy; muốn sửa thì chạy lại và tạo `run_id` mới.
- Lần chạy lỗi vẫn phải ghi manifest với `status=failed` và lý do ở `notes`.
- Mỗi `run_id` phải có một mục trong `docs/EXPERIMENT_LOG.md`.

## 3. Schema từng file

### 3.1. `results/logs/run_manifest.csv`

Một dòng cho mỗi lần chạy.

```text
run_id,started_at,finished_at,git_commit,config_file,config_hash,command,seed,
python_version,numpy_version,torch_version,cpu,gpu,ram_gb,os,status,notes
```

- `git_commit`: commit hash lúc chạy.
- `config_file`, `config_hash`: cấu hình và hash nội dung để phát hiện sửa tay.
- `command`: lệnh đã chạy, copy nguyên văn.
- `status`: `completed`, `failed` hoặc `partial`.
- `notes`: lý do lỗi, khác biệt môi trường, cảnh báo.

### 3.2. `results/logs/games_<run_id>.csv`

Một dòng cho mỗi ván.

```text
run_id,game_id,pair,agent_a,agent_b,a_starts,opening_id,moves,winner,n_moves,
mean_ms_a,p95_ms_a,mean_ms_b,p95_ms_b,
nodes_a,nodes_b,simulations_a,simulations_b,
over_budget_a,over_budget_b
```

- `winner`: `a`, `b` hoặc `draw`.
- `a_starts`: `1` nếu A đi trước, `0` nếu B đi trước.
- `moves`: chuỗi cột cách nhau bằng dấu cách, ví dụ `3 2 4 3`.
- `over_budget_*`: `1` nếu agent vượt ngân sách thời gian.

Nguồn cho: Win/Draw/Loss Rate, Score, Wilson/Bootstrap CI, so sánh cặp đấu.

### 3.3. `results/logs/moves_<run_id>.csv`

Một dòng cho mỗi nước đi.

```text
run_id,game_id,ply,player,agent,action,legal_actions,
time_ms,nodes,simulations,depth_reached,eval_score,is_terminal
```

- `legal_actions`: các cột hợp lệ tại thời điểm chọn, cách nhau bằng dấu cách.
- `time_ms`: thời gian suy nghĩ của **một** nước.
- `nodes`, `simulations`, `depth_reached`: lấy từ `Agent.last_stats`.
- `eval_score`: điểm lượng giá nếu agent có trả về, để trống nếu không.

Nguồn cho: Average Move Time, P95 Latency, Nodes Visited, Simulations.

### 3.4. `results/logs/train_cnn_<run_id>.csv`

Một dòng cho mỗi epoch.

```text
run_id,epoch,split,loss,val_loss,accuracy,top3_accuracy,lr,time_s
```

Nguồn cho: Learning Curve, Accuracy, Top-k Accuracy, Training Time.

### 3.5. `results/logs/train_dqn_<run_id>.csv`

Một dòng cho mỗi episode hoặc mỗi mốc đánh giá.

```text
run_id,episode,reward,avg_reward,epsilon,loss,buffer_size,
eval_win_rate,train_time_s,checkpoint_path
```

Nguồn cho: Average Reward, Epsilon Decay, Bellman Loss, Win Rate theo episode,
Training Time, checkpoint được chọn.

### 3.6. `results/logs/ablation_<run_id>.csv`

Một dòng cho mỗi cấu hình/seed/độ đo.

```text
run_id,experiment,config_id,seed,param_name,param_value,
metric,value,raw_log_path
```

- `experiment`: `a1_pruning`, `a2_mcts_budget`, ...
- `param_name`, `param_value`: tham số đang khảo sát.
- `raw_log_path`: file log thô dùng để tính `metric`.

Nguồn cho: toàn bộ bảng ablation và sensitivity analysis.

### 3.7. `results/tables/report_numbers.csv`

Bảng truy vết từng số trong báo cáo.

```text
report_section,metric,value,unit,type,source_type,source_path,
source_filter,formula,run_id
```

- `report_section`: ví dụ `5.1`, `5.3`, `Bảng 4`.
- `type`: `planned`, `measured` hoặc `derived`.
- `source_type`: `proposal`, `config`, `log`, `table`, `formula`.
- `source_filter`: điều kiện lọc, ví dụ `pair=alphabeta_vs_mcts`.
- `formula`: công thức nếu là số tính toán.

## 4. Ánh xạ chỉ số → nguồn

| Chỉ số trong báo cáo | Nguồn | Cột / công thức |
|---|---|---|
| Win Rate | `games_<run_id>.csv` | `count(winner=a) / count(*)` |
| Draw Rate | `games_<run_id>.csv` | `count(winner=draw) / count(*)` |
| Loss Rate | `games_<run_id>.csv` | `count(winner=b) / count(*)` |
| Score | `games_<run_id>.csv` | `(wins + 0.5 × draws) / total` |
| Khoảng tin cậy 95% | `games_<run_id>.csv` | Wilson hoặc bootstrap từ từng ván |
| Average Move Time | `moves_<run_id>.csv` | trung bình cột `time_ms` |
| P95 Latency | `moves_<run_id>.csv` | phân vị 95 cột `time_ms` |
| Nodes Visited | `moves_<run_id>.csv` | tổng/trung bình cột `nodes` |
| Simulations | `moves_<run_id>.csv` | tổng/trung bình cột `simulations` |
| Training Time | `train_cnn_*` hoặc `train_dqn_*` | tổng `time_s` |
| CNN Loss / Accuracy | `train_cnn_<run_id>.csv` | `loss`, `val_loss`, `accuracy` |
| Average Reward | `train_dqn_<run_id>.csv` | trung bình `reward` |
| Epsilon | `train_dqn_<run_id>.csv` | cột `epsilon` |
| Kết quả ablation | `ablation_<run_id>.csv` + `raw_log_path` | `metric`, `value` |
| Phần cứng / phiên bản | `run_manifest.csv` | `cpu`, `gpu`, `ram_gb`, `python_version`, ... |

## 5. Số kế hoạch và số đo

Không phải mọi con số đều đến từ log. Cần phân biệt:

- `planned`: mục tiêu trong proposal hoặc config, ví dụ “3.000 ván”, “10.000 episode”.
  Nguồn là proposal/config, **không** phải log.
- `measured`: số đo thực tế, **bắt buộc** có log.
- `derived`: số tính từ log, phải ghi công thức và `run_id`.

Trong báo cáo, mọi bảng nên có cột `Nguồn` hoặc ghi chú `[run_id, file, cột]`.
Với số `planned`, ghi rõ “theo proposal mục 5.1” hoặc “theo config ...”.

## 6. Quy tắc trước khi nộp

1. Mỗi hình/bảng trong báo cáo phải có script hoặc notebook tái tạo từ log thô.
2. Không sửa trực tiếp file trong `results/logs/`.
3. Không xóa lần chạy lỗi; ghi `status=failed` và lý do.
4. Không chọn lọc ván thắng để minh họa kết luận.
5. `docs/EXPERIMENT_LOG.md` phải có đủ mục cho mọi `run_id` được trích trong báo cáo.
6. `results/tables/report_numbers.csv` là bảng kiểm tra cuối cùng: mọi số `measured`/`derived`
   phải xuất hiện ở đây và trỏ đúng file log.
