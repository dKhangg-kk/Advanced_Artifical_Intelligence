# Log thực nghiệm

Thư mục này chứa **log thô** của mọi lần chạy. Quy ước đầy đủ và bảng ánh xạ
chỉ số → nguồn nằm trong [`docs/LOGGING.md`](../../docs/LOGGING.md).

## Cấu trúc

```text
results/logs/
├── run_manifest.csv                  # 1 dòng / lần chạy (file dùng chung)
├── games_<run_id>.csv                # 1 dòng / ván
├── moves_<run_id>.csv                # 1 dòng / nước đi
├── train_cnn_<run_id>.csv            # 1 dòng / epoch
├── train_dqn_<run_id>.csv            # 1 dòng / episode hoặc mốc đánh giá
├── ablation_<run_id>.csv             # 1 dòng / cấu hình/seed/độ đo
└── templates/                        # header mẫu, không chứa số liệu
    ├── games.csv
    ├── moves.csv
    ├── train_cnn.csv
    ├── train_dqn.csv
    └── ablation.csv
```

## Quy tắc

1. Mỗi lần chạy có một `run_id` duy nhất, ví dụ
   `tournament-default-20261106T143000Z-s20261102`.
2. Tên file log phải chứa đúng `run_id`.
3. Không sửa file log sau khi chạy; chạy lại thì tạo `run_id` mới.
4. Mỗi `run_id` phải có một mục trong [`docs/EXPERIMENT_LOG.md`](../../docs/EXPERIMENT_LOG.md).
5. Lần chạy lỗi vẫn ghi vào `run_manifest.csv` với `status=failed`.
6. Bảng/hình trong `results/tables/` và `results/figures/` phải sinh lại được từ log thô.
7. Mỗi số `measured`/`derived` trong báo cáo phải có mặt trong
   `results/tables/report_numbers.csv`.

## Tạo file log mới

Có thể copy header từ `templates/`:

```bash
cp results/logs/templates/games.csv \
   results/logs/games_<run_id>.csv
```

Hoặc dùng helper trong code:

```python
from connect_four.evaluation.runlog import new_run_id, write_csv, GAME_FIELDS

run_id = new_run_id("tournament-default", seed=20261102)
write_csv(f"results/logs/games_{run_id}.csv", GAME_FIELDS, rows)
```

Không commit file log rỗng hoặc log giả. Chỉ commit log của lần chạy thật.
