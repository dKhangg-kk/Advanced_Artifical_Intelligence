# 4.5. Ablation A4: lịch giảm epsilon × seed

Cấu hình: `configs/ablation_a4_dqn_training.yaml`. Ba mức decay theo episode (0,9990 / 0,9995 / 0,9998), ba seed (0, 42, 2026), 10.000 episode mỗi ô, đánh giá tại 1.000 / 2.500 / 5.000 / 10.000 episode với 100 ván/đối thủ trên seed validation cố định. Chạy ngày 18/11/2026; 9 ô, mỗi ô ~18–31 phút CPU. Bảng gốc: `results/tables/ablation_a4_results.csv`, tổng hợp: `results/tables/ablation_a4_summary.csv`.

## Kết quả chính (trung bình ± độ lệch chuẩn giữa 3 seed)

<!-- TABLE:a4_main -->
**Validation gặp Random** — score trung bình ± độ lệch chuẩn mẫu giữa các seed, [min–max]; mỗi điểm 100 ván/seed.

| Epsilon decay | 1.000 ep | 2.500 ep | 5.000 ep | 10.000 ep |
| --- | ---: | ---: | ---: | ---: |
| 0,9990 (nhanh) | 0,58 ± 0,08 [0,49–0,63] | 0,55 ± 0,02 [0,53–0,57] | 0,67 ± 0,07 [0,62–0,75] | 0,66 ± 0,07 [0,58–0,72] |
| 0,9995 (mặc định) | 0,60 ± 0,02 [0,59–0,62] | 0,55 ± 0,01 [0,53–0,56] | 0,61 ± 0,07 [0,55–0,69] | 0,66 ± 0,06 [0,62–0,73] |
| 0,9998 (chậm) | 0,57 ± 0,04 [0,54–0,62] | 0,62 ± 0,06 [0,57–0,69] | 0,60 ± 0,02 [0,58–0,62] | 0,63 ± 0,03 [0,59–0,65] |

**Validation gặp Heuristic** — score trung bình ± độ lệch chuẩn mẫu giữa các seed, [min–max]; mỗi điểm 100 ván/seed.

| Epsilon decay | 1.000 ep | 2.500 ep | 5.000 ep | 10.000 ep |
| --- | ---: | ---: | ---: | ---: |
| 0,9990 (nhanh) | 0,01 ± 0,01 [0,00–0,02] | 0,05 ± 0,03 [0,02–0,08] | 0,11 ± 0,02 [0,09–0,13] | 0,14 ± 0,01 [0,12–0,14] |
| 0,9995 (mặc định) | 0,00 ± 0,01 [0,00–0,01] | 0,07 ± 0,06 [0,03–0,14] | 0,12 ± 0,06 [0,07–0,18] | 0,16 ± 0,05 [0,12–0,21] |
| 0,9998 (chậm) | 0,01 ± 0,02 [0,00–0,03] | 0,03 ± 0,01 [0,02–0,03] | 0,06 ± 0,03 [0,03–0,08] | 0,15 ± 0,05 [0,12–0,20] |
<!-- /TABLE:a4_main -->

![Score theo mốc episode](../../results/figures/ablation_a4_score_vs_episode.png)

<!-- TABLE:a4_seeds -->
| Cấu hình | Seed | vs Random T–H–B | score | vs Heuristic T–H–B | score | Tỷ lệ thắng huấn luyện (500 ep cuối) | Thời gian huấn luyện (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast_decay | 0 | 67–0–33 | 0,67 | 14–1–85 | 0,14 | 0,70 | 1 929 |
| fast_decay | 42 | 72–0–28 | 0,72 | 12–0–88 | 0,12 | 0,73 | 1 920 |
| fast_decay | 2026 | 58–0–42 | 0,58 | 14–1–85 | 0,14 | 0,73 | 1 785 |
| default_decay | 0 | 63–0–37 | 0,63 | 12–0–88 | 0,12 | 0,68 | 1 564 |
| default_decay | 42 | 73–0–27 | 0,73 | 20–2–78 | 0,21 | 0,67 | 1 858 |
| default_decay | 2026 | 62–1–37 | 0,62 | 15–1–84 | 0,15 | 0,70 | 1 729 |
| slow_decay | 0 | 65–0–35 | 0,65 | 12–0–88 | 0,12 | 0,49 | 1 086 |
| slow_decay | 42 | 65–0–35 | 0,65 | 20–1–79 | 0,20 | 0,43 | 1 112 |
| slow_decay | 2026 | 59–0–41 | 0,59 | 12–0–88 | 0,12 | 0,46 | 1 063 |
<!-- /TABLE:a4_seeds -->

![Đường cong huấn luyện theo seed](../../results/figures/dqn_a4_training_curves.png)

## Nhận xét

- Ở 10.000 episode, score trước Heuristic là 0,137 (decay 0,9990), 0,162 (0,9995) và 0,148 (0,9998); độ lệch chuẩn giữa seed 0,014–0,049. Các khác biệt giữa ba mức decay **nhỏ hơn hoặc ngang** dao động giữa seed, nên với 3 seed chưa kết luận mức decay nào tốt hơn.
- Trước Random, score 0,657 / 0,662 / 0,630 (cũng trong dao động giữa seed).
- Decay chậm nhất (0,9998) còn epsilon 0,135 ở episode 10.000 nên tỷ lệ thắng *trong lúc huấn luyện* thấp hơn (do còn khám phá), nhưng điểm đánh giá greedy tương đương.
- Không cấu hình nào đạt kết quả tốt trước Heuristic trong đánh giá khai cuộc ngẫu nhiên; nguyên nhân chính là điều kiện huấn luyện (xem 4.4), không phải mức decay.

## Ô mở rộng sau chẩn đoán (không thuộc A4 gốc)

Sau khi thấy kết quả chẩn đoán ở 4.4, chạy thêm **một** ô `default_decay` seed 0 với 4 nước khai cuộc ngẫu nhiên mỗi episode (`--opening-plies 4`). Ô này không dùng để chọn checkpoint giải đấu (đã đóng băng trước) và chỉ có một seed.

<!-- TABLE:a4_extension -->
| Mốc episode | Đối thủ | T–H–B (mở rộng, 4 nước ngẫu nhiên) | score | Wilson 95% | T–H–B (A4 gốc, seed 0) | score (A4 gốc) |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 1.000 | heuristic | 2–0–98 | 0,02 | [0,01; 0,07] | 1–0–99 | 0,01 |
| 1.000 | random | 66–0–34 | 0,66 | [0,56; 0,75] | 59–0–41 | 0,59 |
| 2.500 | heuristic | 3–0–97 | 0,03 | [0,01; 0,08] | 5–0–95 | 0,05 |
| 2.500 | random | 68–0–32 | 0,68 | [0,58; 0,76] | 56–0–44 | 0,56 |
| 5.000 | heuristic | 13–1–86 | 0,14 | [0,08; 0,22] | 7–1–92 | 0,07 |
| 5.000 | random | 69–1–30 | 0,69 | [0,60; 0,78] | 55–0–45 | 0,55 |
| 10.000 | heuristic | 42–1–57 | 0,42 | [0,33; 0,52] | 12–0–88 | 0,12 |
| 10.000 | random | 74–0–26 | 0,74 | [0,65; 0,82] | 63–0–37 | 0,63 |
<!-- /TABLE:a4_extension -->

Ở 10.000 episode ô mở rộng đạt score 0,425 trước Heuristic và 0,740 trước Random, so với 0,120 và 0,630 của ô A4 gốc cùng seed; cải thiện cho thấy hướng khắc phục là đa dạng hóa khai cuộc, nhưng một seed không đủ kết luận định lượng. Đề xuất cho giai đoạn sau, nếu còn thời gian: huấn luyện lại có khai cuộc ngẫu nhiên và đóng băng trước khi chạy lại giải.
