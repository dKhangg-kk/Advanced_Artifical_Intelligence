# Checkpoints

Chỉ commit hai checkpoint cuối đã chọn: `level5_cnn/final.pt` và
`level6_dqn/final.pt`, kèm metadata `.json` cùng tên và log huấn luyện.
Các trọng số trung gian (`.pt`, `.pth`, `.pkl`) vẫn bị bỏ qua (xem `.gitignore`).
Sao chép checkpoint được chọn sang tên `final.pt` sau khi đánh giá;
không đổi tên các checkpoint trung gian đang dùng cho thực nghiệm.

## Cấu trúc thư mục

```
checkpoints/
├── README.md
├── level5_cnn/
│   └── nn_policy_<data_tag>_<seed>.pt          # Cấp 5 - học có giám sát
└── level6_dqn/
    └── dqn_<opponent>_ep<so_episode>_<seed>.pt # Cấp 6 - Deep Q-Network
```

Ví dụ:

```
checkpoints/level5_cnn/nn_policy_ab4_g2000_s0.pt
checkpoints/level6_dqn/dqn_heuristic_ep5000_s0.pt
checkpoints/level6_dqn/dqn_ep10000_s0.pt
```

## Thông tin phải lưu cùng checkpoint

Mỗi checkpoint cần một file `.json` đi kèm (nên commit) ghi:

- commit hash của mã lúc huấn luyện
- siêu tham số (lr, batch, epochs, entropy_coef, ...)
- dữ liệu: số ván, độ sâu nhãn, seed, cách chia tập
- kết quả: val loss / accuracy, điểm đối kháng trên tập đánh giá
- thời gian huấn luyện và phần cứng (CPU/GPU, RAM/VRAM)

Ngoài metadata cuối, log từng epoch/episode phải nằm trong
`results/logs/train_cnn_<run_id>.csv` hoặc `results/logs/train_dqn_<run_id>.csv`
(xem [`docs/LOGGING.md`](../docs/LOGGING.md)). Metadata JSON phải trỏ tới `run_id`.

## Cấp 5 và cấp 6 phải dùng checkpoint riêng

Không dùng chung trọng số giữa hai cấp. Không dùng mạng chưa huấn luyện để
minh chứng hoàn thành cấp 5 hoặc cấp 6.
