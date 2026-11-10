# Dữ liệu

Thư mục này chứa **mô tả** dữ liệu và cách tái tạo. Dữ liệu lớn không đưa vào Git.

| Thư mục | Nội dung | Đưa vào Git? |
|---|---|---|
| `data/raw/` | Dữ liệu ván đấu thô JSONL/CSV sinh từ Alpha-Beta để huấn luyện cấp 5 | Không (đã ignore) |
| `data/processed/` | Dữ liệu sau khi lọc trùng, lật đối xứng dạng .npz/.pt (train/val/test) | Không (đã ignore) |
| `tests/data/` | Bộ vị trí kiểm thử viết tay | Có |
| `checkpoints/` | Trọng số mô hình (level5_cnn/ và level6_dqn/) | Chỉ hai checkpoint cuối `level5_cnn/final.pt`, `level6_dqn/final.pt` và metadata; trọng số trung gian bị ignore |

## Tái tạo dữ liệu huấn luyện

```bash
cd Connect_Four
python -c "from connect_four.training.gen_data import generate_dataset; generate_dataset(n_games=2000, depth=4, seed=0)"
```

Mỗi lần sinh phải ghi lại: số ván, độ sâu Alpha-Beta, seed, số khai cuộc ngẫu nhiên,
commit đang dùng, và tỷ lệ thực tế của train/validation/test sau khi lọc trùng.

## Quy ước chia tập

- Chia **theo ván**, không chia theo trạng thái (tránh rò rỉ dữ liệu).
- Tỷ lệ khởi đầu 70/15/15.
- Kiểm tra trạng thái trùng giữa các tập và ghi lại tỷ lệ thực tế sau lọc.
- Chỉ tăng cường đối xứng (lật gương) trong tập train, và **đổi nhãn cột** tương ứng.
