# Mã nguồn và ý tưởng kế thừa

Cập nhật bảng này mỗi khi tham khảo mã hoặc ý tưởng từ bên ngoài.
Nếu **sao chép mã**, ghi rõ tệp và dòng.

| Nguồn | Giấy phép | Nhóm dùng gì | Nhóm tự làm gì |
|---|---|---|---|
| Mark Liu (2025), *AlphaGo Simplified*, CRC Press | Sách có bản quyền; mã kèm sách | Ý tưởng thuật toán (đọc chương 1–8) | Toàn bộ engine, agent, giải đấu, thống kê, kiểm thử |
| Stuart Russell & Peter Norvig (2022), *AIMA* 4th | Sách | Định nghĩa tác tử, minimax, alpha-beta, MCTS | Cài đặt lại theo thiết kế của nhóm |
| [Pascal Pons, `connect4/Position.hpp`](https://github.com/PascalPons/connect4/blob/master/Position.hpp); slide bài giảng; Mark Liu, *AlphaGo Simplified*; tài liệu mạng | Tài liệu kỹ thuật tham khảo; không sao chép mã nguồn | Ý tưởng bitboard 7 bit/cột và kiểm tra bốn quân bằng dịch bit | Tự cài đặt trong `src/connect_four/game/engine.py`; đối chiếu `ReferenceGame` và test ngẫu nhiên |
| Claude (Anthropic), công cụ AI — phần việc của Phan Lê Ngọc Như Ý (Y5–Y6) | Dịch vụ thương mại, không kế thừa mã | Hỗ trợ viết `scripts/run_ablation_a4.py`, `freeze_dqn_checkpoint.py`, `summarize_a4.py`, `summarize_tournament.py`, `evaluate_positions.py`, `diagnose_dqn_openings.py`, `check_alphabeta_win_values.py`, `build_report_numbers_y.py`; chạy ablation A4, giải đấu và tổng hợp bảng/hình; soạn nháp các mục báo cáo 2.4, 4.1–4.5, 4.7, slide `docs/slides/y.pptx` và nhật ký thực nghiệm ngày 18–19/11/2026 | Các số liệu đều lấy từ log thô trong `results/logs/`; Như Ý cần đọc, chạy lại và tự giải thích phần này trước khi nộp (chưa xác nhận) |
| NumPy | BSD-3-Clause | Mảng bàn cờ và tensor trạng thái | Mã game/agent của dự án |
| PyTorch | BSD-style | Mạng neural và huấn luyện tác tử | Mã mô hình/huấn luyện của dự án |
| Pygame | LGPL-2.1-or-later | Cửa sổ, sự kiện và vẽ giao diện trong `src/connect_four/ui/gui.py` | Điều phối game và giao diện của dự án |
| pytest | MIT | Chạy kiểm thử tự động | Bộ test của dự án |
| pandas, matplotlib, PyYAML, psutil | Giấy phép tương ứng của từng thư viện | Tiện ích phân tích, cấu hình và đo môi trường | Không sửa mã thư viện |
| Codex (trợ lý AI) — phần việc của Bùi Anh Đức (Đ6) | Dịch vụ/phần mềm | Hỗ trợ tổng hợp log, biên tập Mục 4.6, mô tả kiến trúc, tạo script ghép DOCX và sinh slide trong phiên làm việc ngày 20/11/2026 | Số liệu được truy về log/bảng trong repo; tác giả cần đọc, xác nhận nội dung và tự giải thích khi bảo vệ; không dùng ghi nhận này để suy ra tác giả AI cho các commit mã nguồn trước đó |

## Quy ước

- Phần **kế thừa** phải ghi nguồn ngay tại chỗ dùng (docstring hoặc comment).
- Khi dùng công cụ AI để hỗ trợ, ghi lại phạm vi sử dụng theo yêu cầu của giảng viên.

## Phạm Thái Duy Khang — tác tử tìm kiếm và thực nghiệm

| Phạm vi | Nguồn / công cụ | Cách sử dụng và phần triển khai |
| --- | --- | --- |
| Minimax, Alpha-Beta, MCTS/UCT; cơ sở lý thuyết 2.1–2.2 | Russell và Norvig, AIMA 4, Chương 6; tài liệu học phần và proposal nhóm | Dùng để diễn giải thuật toán; hiện thực cụ thể được đối chiếu với `agents/alphabeta.py`, `agents/mcts.py` và các test. |
| Luật chọn nước Heuristic | Mark Liu, *AlphaGo Simplified*; proposal nhóm | Tham khảo ý tưởng tác tử trò chơi và tránh/chặn nước. Không coi thuật toán phổ biến là ý tưởng mới của nhóm. |
| Hoàn thiện Random/Heuristic, Alpha-Beta, MCTS và kiểm thử | Codex hỗ trợ hoàn thiện | Hỗ trợ viết/sửa mã, đối chiếu minimax, kiểm tra seed/ngân sách/bàn gốc và chuẩn bị tài liệu trong PR #57, #61, #63. |
| Báo cáo tìm kiếm và thuật toán cấp 1–4 | Codex hỗ trợ hoàn thiện | Hỗ trợ tổng hợp, diễn giải và đối chiếu nội dung với mã trong PR #74. |
| A1/A2/A5, notebook phân tích, phần báo cáo và slide của Khang | Codex hỗ trợ hoàn thiện | Hỗ trợ triển khai chương trình chạy, kiểm thử, thực thi và phân tích log thực tế, soạn tài liệu. Không dùng số liệu mô phỏng giả để thay kết quả chạy. |
| Hạ tầng thực nghiệm | API engine, bộ chạy trận, thống kê và ghi log của chính dự án | Tái sử dụng `ConnectFour`, `ReferenceGame`, `play_game`, `save_run`, `bootstrap_ci`, `wilson_interval` và `runlog`|

Các mục trên khai báo phạm vi hỗ trợ xác định được, không khẳng định đã kiểm tra
nguồn gốc từng dòng của toàn bộ mã lịch sử. Nếu sử dụng nguyên đoạn mã bên ngoài,
người thực hiện cần ghi đúng nguồn, giấy phép và vị trí sử dụng. Tài liệu tham khảo
không đồng nghĩa với sao chép mã nguồn. Khang chịu trách nhiệm kiểm tra và tự giải
thích phần bàn giao; giờ đóng góp thực tế được ghi riêng trong nhật ký cá nhân.
