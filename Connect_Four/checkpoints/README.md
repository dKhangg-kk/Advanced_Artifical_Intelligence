# Checkpoints

File trọng số (`.pt`, `.pth`, `.pkl`) **không** được commit (xem `.gitignore`).
Chỉ commit file mô tả này và log huấn luyện dạng text/CSV.

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
