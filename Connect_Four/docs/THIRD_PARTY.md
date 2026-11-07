# Mã nguồn và ý tưởng kế thừa

Cập nhật bảng này mỗi khi tham khảo mã hoặc ý tưởng từ bên ngoài.
Nếu **sao chép mã**, ghi rõ tệp và dòng.

| Nguồn | Giấy phép | Nhóm dùng gì | Nhóm tự làm gì |
|---|---|---|---|
| Mark Liu (2025), *AlphaGo Simplified*, CRC Press | Sách có bản quyền; mã kèm sách | Ý tưởng thuật toán (đọc chương 1–8) | Toàn bộ engine, agent, giải đấu, thống kê, kiểm thử |
| Stuart Russell & Peter Norvig (2022), *AIMA* 4th | Sách | Định nghĩa tác tử, minimax, alpha-beta, MCTS | Cài đặt lại theo thiết kế của nhóm |
| Pascal Pons — kỹ thuật bitboard Connect Four | — | Ý tưởng 7 bit/cột và kiểm tra 4 quân bằng dịch bit | Tự cài đặt và kiểm thử chéo với bản tham chiếu |
| Thư viện: numpy, torch, pygame, pytest, pandas, matplotlib | BSD/MIT/Apache | Dùng như công cụ | Không sửa mã thư viện |

## Quy ước

- Phần **kế thừa** phải ghi nguồn ngay tại chỗ dùng (docstring hoặc comment).
- Khi dùng công cụ AI để hỗ trợ, ghi lại phạm vi sử dụng theo yêu cầu của giảng viên.
