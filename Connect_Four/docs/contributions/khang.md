# Đóng góp của Phạm Thái Duy Khang (3124720033)

## Nhật ký K1

| Ngày | Việc | Dẫn chứng | Giờ |
| --- | --- | --- | --- |
| 09/11/2026 | Hoàn thiện Heuristic, kiểm thử Random/Heuristic trên hai engine; thêm script đánh giá và chạy 200 ván | [Issue #12](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/issues/12), [PR #57](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/57), commit `1c22a73`; run `k1-heuristic-random-20261109T061032Z-s0` | khoảng 2 giờ |

- Tệp: `src/connect_four/agents/heuristic.py`, docstring Random, `tests/test_agents.py`, `tests/test_heuristic.py`, `scripts/evaluate_k1.py`, cấu hình K1 và log/tài liệu liên quan.
- Kiểm tra: 80 test đạt; Heuristic thắng 198, hòa 0, thua 2 trong 200 ván. Log và môi trường ở [nhật ký thực nghiệm](../EXPERIMENT_LOG.md).
- Nội dung cần tự giải thích khi review: thứ tự luật, cách tránh mở nước thắng cho đối thủ, góc nhìn của `score()`, xử lý hòa điểm theo seed và cách đổi bên trong 200 ván.
- Công cụ: Codex hỗ trợ hoàn thiện. Tái sử dụng API engine, `play_match`, `save_run` và bộ ghi manifest của dự án.
- Thời gian đóng góp và mức độ tự giải thích do tác giả xác nhận theo thực tế; không suy ra từ thời gian chạy tự động.

## Nhật ký K2

| Ngày | Việc | Dẫn chứng | Giờ |
| --- | --- | --- | --- |
| 10/11/2026 | Hoàn thiện Alpha-Beta từ phần đang viết: sửa góc nhìn lượng giá, đối chiếu minimax, thêm ngân sách thời gian, kiểm thử và tài liệu | [Issue #13](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/issues/13), [PR #61](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/61), [log kiểm tra](../../results/logs/k2_pytest_20261110.txt) | Khoảng 2 giờ 30 phút |

- Nhánh: `feat/issue-13-alphabeta`, đã đồng bộ `main` trước khi bàn giao.
- Chặng độ sâu: commit `0397f44`, Negamax, hai công tắc, thống kê, test minimax độc lập. Toàn bộ dự án lúc đó đạt 152 test.
- Chặng thời gian: commit `a7b579e`, tìm sâu dần, ngắt theo hạn giờ, giữ vòng hoàn tất, nước dự phòng và kiểm tra ngân sách.
- Kiểm tra cuối mã nguồn: `python -m pytest -o addopts= -q` trong `Connect_Four`; **180 passed in 25.17s**. Đối chiếu minimax ở độ sâu 1–4, cả hai engine và hai bên đến lượt; bốn tổ hợp cắt tỉa/sắp xếp. Kiểm tra cả đồng hồ giả và thật, nước hợp lệ, ván kết thúc/hòa, bàn gốc, số nút và reset.
- Lỗi được tái hiện trước khi sửa: minimax giữ góc nhìn ở gốc cho kết quả khác Negamax cũ tại `[3, 2, 3, 4, 1]`, độ sâu 3. Sửa tại Alpha-Beta, giữ nguyên hàm điểm và trọng số K1.
- Tệp chính: `src/connect_four/agents/alphabeta.py`, `tests/test_alphabeta.py`. Cập nhật README, kế hoạch kiểm thử, ROADMAP; giải thích từng phần tại [hướng dẫn Alpha-Beta](../ALPHABETA.md).
- Giới hạn: thời gian là hạn kiểm tra giữa các thao tác; độ sâu 1 không bảo đảm chặn đối thủ ở lượt sau. Chưa chạy giải đấu/ablation M3 và không đưa ra kết luận tỷ lệ thắng hoặc tốc độ.
- Công cụ: Codex/Ponytail hỗ trợ hoàn thiện. Thời gian cá nhân và khả năng tự giải thích do tác giả xác nhận, chưa ghi nhận thay.
- Trạng thái: đã có code/test và bằng chứng, chờ Đức review/approve trước khi merge. Chưa đánh dấu issue đã hoàn tất bàn giao.
