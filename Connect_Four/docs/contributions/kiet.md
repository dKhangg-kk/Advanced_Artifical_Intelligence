# Đóng góp của Bùi Quyền Kiệt (3124720036)

## Mã việc và phạm vi sở hữu

| Mã việc | Milestone | Phụ trách | Review | Tệp trong phạm vi |
| --- | --- | --- | --- | --- |
| `DONGGOP-KIET` ([Issue #44](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/issues/44)) | M5 — Demo và báo cáo | Bùi Quyền Kiệt | Ý | `docs/contributions/kiet.md` |
| `DATA-CNN` ([Issue #20](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/issues/20)) | M4 — Cấp 5 và cấp 6 | Bùi Quyền Kiệt | Ý | `src/connect_four/training/gen_data.py`, `data/generated/` |
| `CNN-L5` ([Issue #21](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/issues/21)) | M4 — Cấp 5 và cấp 6 | Bùi Quyền Kiệt | Ý | `src/connect_four/agents/networks.py`, `src/connect_four/agents/nn_agent.py`, `src/connect_four/training/train_supervised.py`, `checkpoints/level5_cnn/` |
| `ABL-A3` ([Issue #22](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/issues/22)) | M4 — Cấp 5 và cấp 6 | Bùi Quyền Kiệt | Ý | `configs/ablation_a3_cnn_data.yaml`, `src/connect_four/evaluation/situations.py`, `results/tables/ablation_a3_results.csv`, `docs/EXPERIMENT_LOG.md` |
| `BC13-KIET` ([Issue #40](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/issues/40)) | Giữa kỳ | Bùi Quyền Kiệt | Ý | `docs/report/01_gioi_thieu.md`, `docs/report/02b_hoc_giam_sat.md`, `docs/report/03c_cnn.md`, `results/tables/report_numbers.csv` |
| `BC45-KIET` ([Issue #41](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/issues/41)) | M5 — Demo và báo cáo | Bùi Quyền Kiệt | Ý | `docs/report/04b_cnn_duong_cong.md`, `docs/report/04e_ablation_cnn.md`, `results/figures/cnn_main_learning_curve.png`, `src/connect_four/evaluation/plots.py`, `tests/test_plots.py`, `results/tables/report_numbers.csv` |

Issue #44 giao nhật ký đóng góp này. Issue #20–#22 giao pipeline dữ liệu, CNN
cấp 5 và ablation A3. Issue #40 giao phần báo cáo Chương 1–3; Issue #41 giao
mục 4.4 (đường cong học CNN) và 4.5 (ablation A3). Các tệp khác trong
[lộ trình M5](../ROADMAP.md) không được xem là phân công cá nhân nếu chưa có
issue hoặc xác nhận riêng.

## Nhật ký

| Ngày | Việc | PR/commit | Giờ |
| --- | --- | --- | --- |
| 08/11/2026 | Xác minh lịch sử tài khoản: commit đầu tiên trong ngày là `e7cdfa0`, nhưng thay đổi thuộc Tuan01/Lab00, không thuộc dự án Connect Four nên không tính là đóng góp cho đồ án. | [Commit `e7cdfa0`](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/commit/e7cdfa0) | Chưa ghi nhận; không tính giờ đồ án từ commit ngoài phạm vi |
| 09/11/2026 | Chưa xác minh được hoạt động Connect Four của tôi trong lịch sử Git/PR đã kiểm tra. | Chưa có dẫn chứng | Chưa ghi nhận |
| 10/11/2026 | Chưa xác minh được hoạt động Connect Four của tôi trong lịch sử Git/PR đã kiểm tra. | Chưa có dẫn chứng | Chưa ghi nhận |
| 11/11/2026 | Đối chiếu Issue #44, thông tin thành viên và lộ trình; lập nhật ký này. Cập nhật lần sau bằng công việc thực tế, dẫn chứng và thời lượng do tôi xác nhận. | Issue #44; commit `49d129f` (nhánh local, chưa có PR) | Chưa ghi nhận; cần tác giả xác nhận |
| 11/11/2026 | Hoàn thiện bộ sinh 5.000 ván duy nhất ở Alpha-Beta depth 4 sau khai cuộc ngẫu nhiên 6–8 nước; chia theo ván 70/15/15, lọc trạng thái trùng/đối xứng và chỉ lật gương train. | [PR #68](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/68); commits `769b4e4`, `8e10571`, `8c2569c`; manifest: `data/generated/splits/manifest.json` | Chưa ghi nhận; cần tác giả xác nhận |
| 11/11/2026 | Chạy bộ dữ liệu seed 0: 5.000 ván (3.000 main model, 2.000 A3), 110.083 mẫu thô, loại 18.025 trạng thái trùng; còn 66.619/13.028/12.411 mẫu train/val/test trước lật gương. | `cd Connect_Four && .venv/bin/python -c "from connect_four.training.gen_data import generate_dataset; generate_dataset(seed=0)"`; pytest xanh | Chưa ghi nhận; cần tác giả xác nhận |
| 11/11/2026 | Huấn luyện CNN seed 0 trong 20 epoch trên 79.924 mẫu train / 7.958 validation; checkpoint tốt nhất ở epoch 5 (val loss 1,0835). Đánh giá test đúng một lần trên 7.399 mẫu main_model: loss 1,1122, top-1 56,76%, tỷ lệ dự đoán hợp lệ 100%; thời gian 134,27 giây trên CPU. | [PR #69](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/69); commit huấn luyện `bc8010b`; run `20261111T140304Z_87e7371b`; checkpoint, metadata, CSV và báo cáo test tại `checkpoints/level5_cnn/` và `checkpoints/logs/` | Chưa ghi nhận; cần tác giả xác nhận |
| 11/11/2026 | Hoàn thành ablation A3 và phân tích CNN cho RQ2: sửa config về đúng số ván A3 thực có `[250, 500, 1000, 1332]`, thêm bộ phân loại tình huống `win_now` / `block` / `center_control` / `other`, huấn luyện lại CNN ở bốn mức và đo top-1 + tactical accuracy. Top-1 tăng 47,19% → 57,08%; thắng ngay 42,37% → 59,81%; chặn 52,99% → 77,64%; trung tâm (top-1) 41,55% → 52,65%. | [PR #70](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/70); Issue #22; commit `0516a8e`; run ablation `ablation-a3-20261111T150514Z-s20261105`; bảng `results/tables/ablation_a3_results.csv`; hình `results/figures/ablation_a3_accuracy.png`; notebook `notebooks/02_cnn_analysis.ipynb`; nhật ký `docs/EXPERIMENT_LOG.md` | Chưa ghi nhận; cần tác giả xác nhận |
| 13/11/2026 | Viết Chương 1 (bối cảnh, luật chơi, mục tiêu, câu hỏi nghiên cứu, phạm vi, sản phẩm), mục 2.3 (policy network, value network, học có giám sát) và mục 3.4 (dữ liệu, mô hình CNN, quy trình huấn luyện, kết quả main model và ablation A3). Bổ sung 103 dòng truy vết vào `results/tables/report_numbers.csv`; đối chiếu số liệu với manifest, metadata checkpoint, log huấn luyện và bảng ablation. | [PR #72](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/72) (`Closes #40`); nhánh `kietbuideptrai/issue40`; commit `4c8d382`; tệp `docs/report/01_gioi_thieu.md`, `docs/report/02b_hoc_giam_sat.md`, `docs/report/03c_cnn.md` | Chưa ghi nhận; cần tác giả xác nhận |
| 13/11/2026 | Viết mục 4.4 (đường cong học CNN) và 4.5 (ablation A3): phân tích quá khớp, chọn checkpoint theo validation loss, lợi ích biên theo lượng dữ liệu, nhiễu nhãn `win_now` và giới hạn. Thêm hàm vẽ đường cong `evaluation/plots.py` kèm test, sinh hình `cnn_main_learning_curve.png`; bổ sung 118 dòng truy vết vào `results/tables/report_numbers.csv`. | [PR #73](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/73) (`Closes #41`); nhánh `kietbuideptrai/issue41`; commit `895d5a4`; tệp `docs/report/04b_cnn_duong_cong.md`, `docs/report/04e_ablation_cnn.md` | Chưa ghi nhận; cần tác giả xác nhận |

Không thể dùng commit ngày 08/11 nói trên làm căn cứ cho một commit Connect Four
trong ngày đó. Không hồi tố ngày commit, không suy ra số giờ từ timestamp hoặc
thời gian chạy công cụ. Tiếp tục bổ sung từng ngày đến 21/11/2026; ngày không
làm việc cần ghi rõ, và giờ cần dựa trên thời gian thực tế.

## Căn cứ chốt tỷ lệ đóng góp

Tỷ lệ đóng góp chưa được xác định. Trước 19/11 cần tổng hợp các PR đã
review/merge, commit thuộc phạm vi, tệp và kết quả bàn giao, log thực nghiệm
(nếu có), cùng giờ thực tế được xác nhận. Không tính commit ngoài đồ án hoặc
công việc chưa có bằng chứng.

## Phần tôi tự giải thích được

- Phạm vi của Issue #44, #20–#22 và #40; lý do nhật ký chỉ nhận quyền sở hữu
  đối với các tệp được giao.
- Cấu trúc báo cáo 5 chương và phạm vi bản giữa kỳ (Chương 1–3).
- Phân biệt policy network và value network; vì sao cấp 5 chỉ huấn luyện policy
  network từ nhãn Alpha-Beta, còn value/Q-value thuộc cấp 6.
- Cách đọc `results/tables/report_numbers.csv`: phân biệt `planned`, `measured`,
  `derived`; đối chiếu `source_path`, `source_filter` và `run_id`.
- Cách diễn giải top-1 accuracy so với tactical accuracy; vì sao top-1 không
  đồng nghĩa với sức mạnh thi đấu.
- Hiện tượng quá khớp: train accuracy tiếp tục tăng trong khi validation loss
  tăng, nên checkpoint được chọn theo validation loss thấp nhất.
- Cách đọc đường cong học ở mục 4.4: phân biệt train/validation, loss/accuracy;
  vì sao validation loss ổn định hơn validation accuracy khi chọn checkpoint.
- Thiết kế ablation A3: bốn tập con lồng nhau 250 ⊂ 500 ⊂ 1.000 ⊂ 1.332 ván,
  validation/test cố định, và vì sao trần dữ liệu là 1.332 ván sau khử trùng lặp.
- Cách đọc lợi ích biên: bước 250 → 500 lớn nhất, các bước sau giảm dần, riêng
  tình huống chặn vẫn cải thiện; vì sao `win_now` không đơn điệu.
- Nhiễu nhãn: 98/321 nhãn `win_now` (30,53%) không phải nước thắng ngay, nên
  tactical accuracy là thước đo đúng thay vì top-1.
- Vì sao `center_control_top1_accuracy` tăng nhưng tỷ lệ chọn cột 3 giảm: mô
  hình bắt chước nhãn Alpha-Beta sát hơn, không phải yếu đi.
- Ý nghĩa của bộ số đóng băng 19/11/2026 22:00 và việc phải đối chiếu lại bản
  nháp trước khi merge.
- Cách dùng `run_id` và log huấn luyện để tái lập kết quả CNN và ablation A3.

## Công cụ và nguồn

- Git và GitHub: kiểm tra lịch sử commit, Issue #20–#22, Issue #40–#41, Issue #44
  và các PR liên quan.
- Nguồn trong repository: proposal đã nộp
  `docs/proposal/ConnectFour_7x6_Proposal_Nhom100_HoanChinh.docx`,
  [lộ trình](../ROADMAP.md), [quy ước đóng góp](../../CONTRIBUTING.md),
  `data/generated/splits/manifest.json`, `checkpoints/level5_cnn/`,
  `checkpoints/logs/`, `results/logs/train_cnn_*.csv`,
  `results/tables/ablation_a3_results.csv`, `results/figures/*.png`,
  `notebooks/02_cnn_analysis.ipynb`, `configs/ablation_a3_cnn_data.yaml`,
  `docs/EXPERIMENT_LOG.md` và `results/tables/report_numbers.csv`.
- GitHub Copilot và trợ lý OpenCode: hỗ trợ đối chiếu thông tin, soạn thảo và
  kiểm tra số liệu; nội dung cần được tôi xác nhận theo công việc thực tế.
- Issue #44 dẫn nguồn “Kế hoạch & phân công Nhóm 100 - Connect Four AI
  (8 11 → 22 11 2026).docx”.
