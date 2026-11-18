# Mã nguồn và ý tưởng kế thừa

Cập nhật bảng này mỗi khi tham khảo mã hoặc ý tưởng từ bên ngoài.
Nếu **sao chép mã**, ghi rõ tệp và dòng.

| Nguồn | Giấy phép | Nhóm dùng gì | Nhóm tự làm gì |
|---|---|---|---|
| Mark Liu (2025), *AlphaGo Simplified*, CRC Press | Sách có bản quyền; mã kèm sách | Ý tưởng thuật toán (đọc chương 1–8) | Toàn bộ engine, agent, giải đấu, thống kê, kiểm thử |
| Stuart Russell & Peter Norvig (2022), *AIMA* 4th | Sách | Định nghĩa tác tử, minimax, alpha-beta, MCTS | Cài đặt lại theo thiết kế của nhóm |
| Pascal Pons — kỹ thuật bitboard Connect Four |Slide bài giảng /  Liu - AlphaGo  / Tài liệu mạng| Ý tưởng 7 bit/cột và kiểm tra 4 quân bằng dịch bit | Tự cài đặt và kiểm thử chéo với bản tham chiếu |
| Thư viện: numpy, torch, pygame, pytest, pandas, matplotlib | BSD/MIT/Apache | Dùng như công cụ | Không sửa mã thư viện |

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
