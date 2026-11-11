# Đóng góp của Bùi Quyền Kiệt

## Phần phụ trách

Bộ vị trí kiểm thử luật cho Connect Four trong milestone M1.

## Nhật ký

| Ngày | Việc đã làm | PR/commit và log |
| --- | --- | --- |
| 11/11/2026 | Bổ sung 31 vị trí kiểm tra thắng dọc/ngang/hai chéo, chặn, đòn kép, hòa và cột đầy; thêm kiểm thử đối chiếu hai engine. | PR sẽ được liên kết sau khi tạo; `cd Connect_Four && pytest -q` |

## Phần tôi giải thích được

- CSV lưu chuỗi nước đi hợp lệ, người đi kế tiếp, các cột thắng ngay và các cột cần chặn.
- Cùng một bộ dữ liệu được chạy qua engine bitboard và `ReferenceGame` để phát hiện sai khác.
- Vị trí hòa kiểm tra bàn đầy không có người thắng; vị trí cột đầy kiểm tra cột không hợp lệ khi ván vẫn đang tiếp tục.

## Công cụ và nguồn đã dùng

Python, pytest và các engine Connect Four trong repository.
