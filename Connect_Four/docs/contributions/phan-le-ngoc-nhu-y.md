# Phan Lê Ngọc Như Ý (3124720079)

**Dự án:** Connect Four AI — Học phần Trí tuệ nhân tạo nâng cao  
**Vai trò:** Phát triển tác tử học tăng cường cấp 6 (DQN), hệ thống giải đấu và phân tích thực nghiệm.

## 1. Phạm vi công việc được phân công

### 1.1. Phát triển tác tử DQN (Level 6)

- **ReplayBuffer:** Xây dựng bộ nhớ kinh nghiệm FIFO tối đa 100.000 transition; lưu trạng thái, hành động, phần thưởng, trạng thái kế tiếp, trạng thái kết thúc và mặt nạ hành động hợp lệ.
- **EpsilonSchedule:** Xây dựng lịch giảm epsilon theo episode từ 1.0, không thấp hơn 0.05.
- **Action Mask:** Loại các cột đã đầy khi chọn hành động và khi tính mục tiêu Bellman.
- **DQN Agent:** Xử lý trạng thái bàn cờ dạng 2×6×7, nạp checkpoint theo cơ chế lazy-load, dự đoán Q-value và chọn nước đi hợp lệ.
- **DQN Training:** Xây dựng vòng huấn luyện với phần thưởng thắng/hòa/thua (+1/0/−1), luân phiên bên đi trước, Replay Buffer, Target Network, Bellman Target có mask và Huber Loss.
- **Checkpoint & Logging:** Lưu checkpoint, metadata và log huấn luyện theo episode để theo dõi, đánh giá và tái lập.

### 1.2. Xây dựng hệ thống giải đấu

- Phát triển `evaluation/config.py` và `evaluation/cli.py`.
- Xây dựng cấu hình tác tử và giải đấu bằng YAML.
- Hỗ trợ chạy đối đầu từng cặp và giải đấu vòng tròn Round-Robin.
- Thiết lập hai chế độ đánh giá: mặc định và giới hạn thời gian cho mỗi nước đi.
- Ghi kết quả trận đấu, thông tin nước đi và Run Manifest ra CSV; hỗ trợ lưu kết quả theo từng cặp để dễ kiểm tra.

### 1.3. Thực nghiệm và phân tích kết quả

- Thực hiện Ablation A4 để khảo sát ảnh hưởng của các mức Epsilon Decay và Random Seed đến quá trình huấn luyện DQN.
- Đánh giá các mốc checkpoint bằng tập Validation trước khi chọn mô hình.
- Tổ chức và tổng hợp kết quả giải đấu, kiểm tra cân bằng lượt đi trước và đi sau.
- Phân tích thắng/hòa/thua, score, khoảng tin cậy Wilson, thời gian trung bình và p95 mỗi nước, chi phí tính toán và thời gian huấn luyện.
- Sử dụng notebook để xử lý dữ liệu, tạo bảng và biểu đồ; cập nhật số liệu có thể truy ngược về run_id trong `report_numbers.csv`.

### 1.4. Báo cáo và thuyết trình

| Phần | Nội dung phụ trách |
| --- | --- |
| Chương 2 – Mục 2.4 | Học tăng cường (RL), DQN, Self-play; phân biệt AlphaGo-inspired và AlphaZero-inspired |
| Chương 3 – Mục 3.5–3.6 | Thiết kế tác tử DQN cấp 6 và quy trình tổ chức giải đấu công bằng |
| Chương 4 – Mục 4.1–4.3 | Môi trường thực nghiệm, ma trận đối đầu, thắng/hòa/thua, độ trễ và chi phí |
| Chương 4 – Mục 4.4 | Phân tích đường cong huấn luyện DQN |
| Chương 4 – Mục 4.5 | Phân tích Ablation A4 |
| Chương 4 – Mục 4.7 | Thảo luận kết quả, nguyên nhân, hạn chế và lợi thế đi trước |

Ngoài ra, phụ trách 2–4 slide về DQN, giải đấu và kết quả thực nghiệm; phối hợp rà soát báo cáo và đối chiếu số liệu với log.

## 2. Các tệp và thư mục phụ trách

| Thành phần | Đường dẫn trong repository |
| --- | --- |
| DQN Agent | `Connect_Four/src/connect_four/agents/dqn.py` |
| DQN Network | Lớp DQNNet trong `Connect_Four/src/connect_four/agents/networks.py` |
| DQN Training | `Connect_Four/src/connect_four/training/train_dqn.py` |
| Tournament CLI và cấu hình | `Connect_Four/src/connect_four/evaluation/cli.py`, `config.py` |
| Kiểm thử | `Connect_Four/tests/test_dqn.py`, `test_cli.py` |
| Cấu hình giải đấu và A4 | `Connect_Four/configs/tournament_*`, `ablation_a4_dqn_training.yaml` |
| Notebook phân tích | `Connect_Four/notebooks/01_*` |
| Checkpoint DQN | `Connect_Four/checkpoints/level6_dqn/` |
| Log, bảng và biểu đồ | `Connect_Four/results/logs/`, `results/tables/`, `results/figures/` |
| Báo cáo | `Connect_Four/docs/report/02c_hoc_tang_cuong.md`, `03d_dqn_giai_dau.md`, các mục Chương 4 được phân công |

## 3. Kết quả đã có minh chứng

- **PR #59:** Hoàn thiện DQN Core và DQN Agent — [xem Pull Request](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/59).
- **PR #64:** Hoàn thiện vòng huấn luyện DQN và kiểm thử — [xem Pull Request](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/64).
- **PR #75:** Bổ sung Tournament CLI, cấu hình, pilot và minh chứng giữa kỳ — [xem Pull Request](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/75).
- Đợt kiểm thử ngày 13/11/2026 ghi nhận **289 test passed**.
- Pilot huấn luyện DQN 200 episode gặp Heuristic: 1 thắng, 0 hòa, 199 thua. Pilot này xác nhận pipeline và khả năng ghi log, **không phải kết quả chứng minh mô hình đã hội tụ**.
- Pilot Round-Robin gồm 3 cặp, 20 ván/cặp (60 ván). Kết quả pilot chưa đạt mức đánh giá chính thức tối thiểu 100 ván/cặp.

**Lưu ý về trạng thái:** Phần trên mô tả phạm vi được phân công và các kết quả đã có minh chứng. Ablation A4 đầy đủ, lựa chọn checkpoint cuối và giải đấu chính thức phải được cập nhật khi có log thực tế; không xem kế hoạch hoặc pilot là kết quả hoàn thành cuối kỳ.

## 4. Công nghệ sử dụng

Python, NumPy, PyTorch, PyYAML, pytest, Jupyter Notebook, pandas, Matplotlib, Git và GitHub.

## 5. Repository và tài liệu

- [Repository nhóm – Advanced Artificial Intelligence](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence)
- [Lịch sử Pull Request của Như Ý](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pulls?q=is%3Apr+author%3Amealley9-ui)
