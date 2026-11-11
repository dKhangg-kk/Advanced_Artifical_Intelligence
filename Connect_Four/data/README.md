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
