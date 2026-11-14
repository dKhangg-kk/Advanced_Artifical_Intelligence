# Dữ liệu

Thư mục này chứa **mô tả** dữ liệu và cách tái tạo. Dữ liệu lớn không đưa vào Git.

| Thư mục | Nội dung | Đưa vào Git? |
|---|---|---|
| `data/generated/` | Ván JSONL thô và các tập JSONL train/val/test sinh từ Alpha-Beta | Không (đã ignore) |
| `tests/data/` | Bộ vị trí kiểm thử viết tay | Có |
| `checkpoints/` | Trọng số mô hình (level5_cnn/ và level6_dqn/) | Chỉ hai checkpoint cuối `level5_cnn/final.pt`, `level6_dqn/final.pt` và metadata; trọng số trung gian bị ignore |

## Tái tạo dữ liệu huấn luyện

```bash
cd Connect_Four
PYTHONPATH=src python -c "from connect_four.training import generate_dataset; generate_dataset(seed=0)"
```

Mỗi dong `games.jsonl` la mot van, gom khai cuoc ngau nhien, toan bo chuoi nuoc
va nhan policy tai moi trang thai ma Alpha-Beta chon nuoc. Nhan duoc sinh boi
`AlphaBetaAgent` o do sau co dinh (mac dinh 4), khong phai nuoc toi uu toan hoc.
Mac dinh, khai cuoc ngau nhien dai 6-8 nuoc de tao du so van khac nhau.
Generator sinh bu den khi co du 5000 van duy nhat: 3000 van dau danh dau
`main_model`; 2000 van con lai danh dau `a3`.

Lenh tu dong tao `splits/train.jsonl`, `val.jsonl`, `test.jsonl` va
`splits/manifest.json`. Manifest ghi do sau, seed, so van tung cohort, so vi tri
duy nhat sau loc, ty le game/vi tri thuc te, so lan thu sinh va so ban lat
guong; manifest cung luu ID game tung split va so game khong con mau duy nhat
sau loc. Tung van trong `games.jsonl` luu khai cuoc da chon va chuoi nuoc. De
tranh ro ri, game duoc chia truoc theo ty le 70/15/15; vi tri trung hoac tuong
duong doi xung duoc giu o split dau tien va loai khoi split sau. Chi train duoc
lat guong, nhan cot `c` doi thanh `6-c`.

## Quy ước chia tập

- Chia **theo ván**, không chia theo trạng thái (tránh rò rỉ dữ liệu).
- Tỷ lệ khởi đầu 70/15/15.
- Lọc trạng thái trùng và tương đương đối xứng giữa các tập; ghi tỷ lệ thực tế sau lọc.
- Chỉ tăng cường đối xứng (lật gương) trong tập train, và **đổi nhãn cột** tương ứng.

## Huấn luyện CNN cấp 5

Sau khi có ba file `train.jsonl`, `val.jsonl`, `test.jsonl` trong
`data/generated/splits/`, huấn luyện và chọn checkpoint theo validation loss:

Mặc định chỉ dùng cohort `main_model` (3.000 ván); có thể truyền
`cohort="a3"` để huấn luyện riêng cohort A3. Cohort A3 có 2.000 ván, nhưng sau
chia 70/15/15 và lọc trùng chỉ còn **1.332 ván train**, **254 ván validation**
và **264 ván test** có mẫu duy nhất. Có thể giới hạn số ván train bằng
`game_limit=N`; validation/test vẫn cố định.

```bash
cd Connect_Four
python -c "from connect_four.training.train_supervised import train_supervised; train_supervised('data/generated/splits', epochs=20, batch_size=256, lr=1e-3, seed=0, cohort='main_model')"
```

Mỗi lần chạy ghi log `checkpoints/logs/train_cnn_<run_id>.csv` (hoặc
`results/logs/` nếu truyền `log_dir`); checkpoint có validation loss thấp nhất
được lưu tại `checkpoints/level5_cnn/final.pt`, kèm `final.json` chứa commit,
siêu tham số, seed, số ván/mẫu, phần cứng và thời gian chạy. Training chỉ đọc
train/validation. Sau khi chốt checkpoint, gọi
`evaluate_checkpoint(checkpoint, data_dir)` đúng một lần để đọc tập test;
run ID được ghi dấu để ngăn đánh giá lại cùng checkpoint. Kết quả trả về gồm
top-1 tổng thể và độ chính xác theo tình huống `win_now`, `block`,
`center_control`, `other` (xem `evaluation/situations.py`).

## Ablation A3 — kích thước dữ liệu CNN

A3 huấn luyện lại CNN trên các tập con 250, 500, 1.000 và 1.332 ván train của
cohort A3 (mức cuối là số ván train thực có sau dedupe), giữ cố định
validation/test. Chạy:

```bash
cd Connect_Four
PYTHONPATH=src python scripts/run_ablation_a3.py \
    --config configs/ablation_a3_cnn_data.yaml
```

Script ghi bảng `results/tables/ablation_a3_results.csv`, hình
`results/figures/ablation_a3_accuracy.png`, log
`results/logs/ablation_a3_<run_id>.csv`, log huấn luyện từng mức và metadata
checkpoint. Notebook `notebooks/02_cnn_analysis.ipynb` đọc các log này để trả
lời RQ2.
