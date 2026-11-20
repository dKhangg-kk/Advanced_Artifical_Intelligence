# Mã nguồn và ý tưởng kế thừa

Cập nhật bảng này mỗi khi tham khảo mã hoặc ý tưởng từ bên ngoài.
Nếu **sao chép mã**, ghi rõ tệp và dòng.

| Nguồn | Giấy phép | Nhóm dùng gì | Nhóm tự làm gì |
|---|---|---|---|
| Mark Liu (2025), *AlphaGo Simplified*, CRC Press | Sách có bản quyền; mã kèm sách | Ý tưởng thuật toán (đọc chương 1–8) | Toàn bộ engine, agent, giải đấu, thống kê, kiểm thử |
| Stuart Russell & Peter Norvig (2022), *AIMA* 4th | Sách | Định nghĩa tác tử, minimax, alpha-beta, MCTS | Cài đặt lại theo thiết kế của nhóm |
| [Pascal Pons, `connect4/Position.hpp`](https://github.com/PascalPons/connect4/blob/master/Position.hpp) | Tài liệu kỹ thuật tham khảo; dự án upstream có giấy phép riêng | Ý tưởng 7 bit/cột (6 ô + bit đệm) và biểu diễn bàn cờ Connect Four | Tự cài đặt trong `src/connect_four/game/engine.py`; kiểm tra thắng bằng dịch bit theo cách của dự án; đối chiếu với `ReferenceGame` và test ngẫu nhiên; không sao chép nguyên mã nguồn |
| NumPy | BSD-3-Clause | Mảng bàn cờ và tensor trạng thái | Mã game/agent của dự án |
| Pygame | LGPL-2.1-or-later | Cửa sổ, sự kiện và vẽ giao diện trong `src/connect_four/ui/gui.py` | Điều phối game và giao diện của dự án |
| pytest | MIT | Chạy kiểm thử tự động | Bộ test của dự án |
| pandas, matplotlib, PyYAML, psutil | Các giấy phép tương ứng của thư viện | Khai báo làm dependency tiện ích/phân tích; không ghi nhận sử dụng trong các nội dung Mục 4.6 và slide của Đức | Không sửa mã thư viện |
| Codex (trợ lý AI) | Dịch vụ/phần mềm | Hỗ trợ tổng hợp log, biên tập Mục 4.6, mô tả kiến trúc, tạo script ghép DOCX và sinh slide trong phiên làm việc ngày 20/11/2026 | Số liệu được truy về log/bảng trong repo; tác giả cần đọc, xác nhận nội dung và tự giải thích khi bảo vệ; không dùng ghi nhận này để suy ra tác giả AI cho các commit mã nguồn trước đó |

## Quy ước

- Phần **kế thừa** phải ghi nguồn ngay tại chỗ dùng (docstring hoặc comment).
- Khi dùng công cụ AI để hỗ trợ, ghi lại phạm vi sử dụng theo yêu cầu của giảng viên.
