# Đóng góp của Phạm Thái Duy Khang (3124720033)

## Nhật ký K1

| Ngày | Việc | Dẫn chứng | Giờ |
| --- | --- | --- | --- |
| 09/11/2026 | Hoàn thiện Heuristic, kiểm thử Random/Heuristic trên hai engine; thêm script đánh giá và chạy 200 ván | [Issue #12](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/issues/12), [PR #57](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/57), commit `1c22a73`; run `k1-heuristic-random-20261109T061032Z-s0` | Chưa ghi nhận |

- Tệp: `src/connect_four/agents/heuristic.py`, docstring Random, `tests/test_agents.py`, `tests/test_heuristic.py`, `scripts/evaluate_k1.py`, cấu hình K1 và log/tài liệu liên quan.
- Kiểm tra: 80 test đạt; Heuristic thắng 198, hòa 0, thua 2 trong 200 ván. Log và môi trường ở [nhật ký thực nghiệm](../EXPERIMENT_LOG.md).
- Nội dung cần tự giải thích khi review: thứ tự luật, cách tránh mở nước thắng cho đối thủ, góc nhìn của `score()`, xử lý hòa điểm theo seed và cách đổi bên trong 200 ván.
- Công cụ: Codex và Ponytail hỗ trợ đọc dự án, cài đặt, viết test, chạy đánh giá và chuẩn bị PR. Tái sử dụng API engine, `play_match`, `save_run` và bộ ghi manifest của dự án.
- Thời gian đóng góp và mức độ tự giải thích do tác giả xác nhận theo thực tế; không suy ra từ thời gian chạy tự động.
