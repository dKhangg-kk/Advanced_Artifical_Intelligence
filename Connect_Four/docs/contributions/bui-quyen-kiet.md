# Đóng góp của Bùi Quyền Kiệt

## Phần phụ trách

Sinh/chia dữ liệu policy gán nhãn Alpha-Beta và huấn luyện CNN cấp 5, gồm nguồn dữ liệu chính và cohort dành cho ablation A3.

## Nhật ký

| Ngày | Việc đã làm | PR/commit và log |
| --- | --- | --- |
| 11/11/2026 | Hoàn thiện bộ sinh 5.000 ván duy nhất ở Alpha-Beta depth 4 sau khai cuộc ngẫu nhiên 6–8 nước; chia theo ván 70/15/15, lọc trạng thái trùng/đối xứng và chỉ lật gương train. | [PR #68](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/68); commits `769b4e4`, `8e10571`, `8c2569c`; manifest: `data/generated/splits/manifest.json`. |
| 11/11/2026 | Chạy bộ dữ liệu seed 0: 5.000 ván (3.000 main model, 2.000 A3), 110.083 mẫu thô, loại 18.025 trạng thái trùng; còn 66.619/13.028/12.411 mẫu train/val/test trước lật gương. | `cd Connect_Four && .venv/bin/python -c "from connect_four.training.gen_data import generate_dataset; generate_dataset(seed=0)"`; pytest xanh. |
| 11/11/2026 | Huấn luyện CNN seed 0 trong 20 epoch trên 79.924 mẫu train / 7.958 validation; checkpoint tốt nhất ở epoch 5 (val loss 1,0835). Đánh giá test đúng một lần trên 7.399 mẫu main_model: loss 1,1122, top-1 56,76%, tỷ lệ dự đoán hợp lệ 100%; thời gian 134,27 giây trên CPU. | [PR #69](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/69); commit huấn luyện `bc8010b`; run `20261111T140304Z_87e7371b`; checkpoint, metadata, CSV và báo cáo test tại `checkpoints/level5_cnn/` và `checkpoints/logs/`. |
| 11/11/2026 | Hoàn thành ablation A3 và phân tích CNN cho RQ2: sửa config về đúng số ván A3 thực có `[250, 500, 1000, 1332]`, thêm bộ phân loại tình huống `win_now` / `block` / `center_control` / `other`, huấn luyện lại CNN ở bốn mức và đo top-1 + tactical accuracy. Top-1 tăng 47,19% → 57,08%; thắng ngay 42,37% → 59,81%; chặn 52,99% → 77,64%; trung tâm (top-1) 41,55% → 52,65%. | Issue #22; commit `0516a8e`; run ablation `ablation-a3-20261111T150514Z-s20261105`; bảng `results/tables/ablation_a3_results.csv`; hình `results/figures/ablation_a3_accuracy.png`; notebook `notebooks/02_cnn_analysis.ipynb`; nhật ký `docs/EXPERIMENT_LOG.md`. |

## Phần tôi giải thích được

- Mỗi ván dùng `AlphaBetaAgent` ở một độ sâu cố định; các khai cuộc ngẫu nhiên tạo đa dạng, còn phần còn lại của ván được gán nhãn bằng nước Alpha-Beta chọn.
- Chia game trước khi lọc các trạng thái giống nhau hoặc tương đương qua phép lật ngang, nhờ đó không rò rỉ giữa train, validation và test.
- Chỉ mẫu train được lật gương; nhãn cột được đổi theo `6-c`. Manifest ghi ID game từng tập, tỷ lệ thực tế và số mẫu bị lọc.
- CNN huấn luyện mặc định chỉ đọc cohort `main_model`; tập validation chọn checkpoint, còn tập test được đọc một lần sau khi chốt mô hình.

## Công cụ và nguồn đã dùng

Python, NumPy và pytest; engine `ConnectFour`, `AlphaBetaAgent` và cấu hình ablation A3 trong repository.
