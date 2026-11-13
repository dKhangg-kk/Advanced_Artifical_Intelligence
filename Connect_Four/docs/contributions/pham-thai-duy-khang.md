# Đóng góp của Phạm Thái Duy Khang (3124720033)

## Nhật ký

| Ngày | Việc đã làm | Issue/PR | Giờ |
| --- | --- | --- | --- |
| 08/11/2026 | Sửa link Tuan05 trong README, cho phép hai checkpoint cuối và thống nhất hướng dẫn lưu trọng số | [Issue #11](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/issues/11), [PR #56](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/56), commit `7ffca70` | Chưa ghi nhận |
| 09/11/2026 | Sửa ROADMAP theo báo cáo 5 chương và phân công đã có; thống nhất tài liệu checkpoint; kiểm tra link và quy tắc ignore | [Issue #11](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/issues/11), [PR #56](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/56) | Chưa ghi nhận |

## Công cụ hỗ trợ

Codex và Ponytail hỗ trợ rà soát, chỉnh sửa tài liệu, kiểm tra quy tắc bỏ qua checkpoint và chuẩn bị bản sửa cho Issue #11. Chưa huấn luyện mô hình hoặc tạo checkpoint trong công việc này. Thời gian đóng góp cần được tác giả bổ sung theo thực tế.

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

## Nhật ký K3

| Ngày | Việc | Dẫn chứng | Giờ |
| --- | --- | --- | --- |
| 11/11/2026 | Hoàn thiện MCTS-UCT, hỗ trợ ngân sách mô phỏng/thời gian, bổ sung kiểm thử và đánh giá 200 ván với Random | [Issue #14](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/issues/14), [PR #63](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/63), commit `4dbe441`, [log kiểm thử](../../results/logs/k3_pytest_20261111.txt) | khoảng 2 giờ |

- Nhánh: `feat/issue-14-mcts-uct`, phát triển từ `main`.
- Tệp chính: `src/connect_four/agents/mcts.py`, `tests/test_mcts.py`. Cài đặt đủ selection, expansion, simulation và backpropagation; hỗ trợ `Budget(simulations)`/`Budget(time_s)`, seed, thống kê và giữ nguyên game gốc.
- Kiểm tra: `python -m pytest -o addopts= -q` trong `Connect_Four` — **218 passed in 22.80s**, gồm 38 test MCTS mới. Kiểm tra trên hai engine, góc nhìn đối thủ, nước hợp lệ, ván kết thúc/hòa, ngân sách, timeout và bảo toàn bàn gốc. [CI đạt trên commit `8ba2040`](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/actions/runs/42873638181).
- Thực nghiệm: `scripts/evaluate_k3.py`, cấu hình `configs/k3_random_mcts.json`; **199 thắng, 0 hòa, 1 thua / 200 ván = 99,5%** ở **500 mô phỏng/nước**. 100 khai cuộc khác nhau dài 4 nước, đấu hai lần đổi bên; seed khai cuộc/MCTS = 0, Random = 1.
- Dẫn chứng: run chính `k3-mcts-random-20261110T181313Z-s0`, mã nguồn commit `4dbe441`; [log ván](../../results/logs/games_k3-mcts-random-20261110T181313Z-s0.csv), [log nước](../../results/logs/moves_k3-mcts-random-20261110T181313Z-s0.csv), [bảng tổng hợp](../../results/tables/k3-mcts-random-20261110T181313Z-s0.csv). Cấu hình, môi trường và log pilot được ghi trong [nhật ký thực nghiệm](../EXPERIMENT_LOG.md).
- Tài liệu: cập nhật README, ROADMAP, kế hoạch kiểm thử và hướng dẫn MCTS.
- Giới hạn: kết quả áp dụng cho bộ seed/khai cuộc đã công bố; hạn giờ được kiểm tra giữa các thao tác nên có thể vượt nhẹ. Chưa đánh giá trước Alpha-Beta hoặc chạy giải đấu/ablation M3.
- Công cụ: Codex hỗ trợ hoàn thiện. Tái sử dụng API engine, `Agent/Budget/SearchStats`, cấu trúc `MCTSNode`, mẫu đánh giá K1 và hệ thống `play_match`/`save_run`/manifest của dự án.
- Trạng thái: đã có code, test và log; PR #63 đang mở, chờ Đức review/approve trước khi merge.

## Nhật ký

| Ngày | Việc | Dẫn chứng | Giờ |
| --- | --- | --- | --- |
| 13/11/2026 | Hoàn thiện mục 2.1–2.2 về tác tử, Minimax, Alpha-Beta, MCTS/UCT và mục 3.3 về thuật toán cấp 1–4; đối chiếu proposal, tài liệu lý thuyết và mã nguồn | [Issue #35](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/issues/35), [PR #74](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/74), [mục 2.1–2.2](../report/02a_tim_kiem.md), [mục 3.3](../report/03b_thuat_toan.md) | Chưa ghi nhận |

- Nhánh: `docs/issue-35-search-report`; đã push và mở PR #74.
- Chỉ bổ sung tài liệu; không thay đổi thuật toán hoặc ghi thêm kết quả giải đấu.
- Kiểm tra tại máy: `python -m pytest -o addopts= -q` đạt **283 passed in 35.82s**; đối chiếu ví dụ trên hai engine và kiểm tra 27 liên kết tương đối trong hai mục báo cáo và nhật ký đóng góp. `git diff --check` đạt.
- Công cụ: Codex hỗ trợ hoàn thiện.
- Thời gian đóng góp và khả năng tự giải thích cần được tác giả xác nhận theo thực tế.
- Trạng thái: PR #74 đã mở, chờ Đức review/approve trước khi merge.
