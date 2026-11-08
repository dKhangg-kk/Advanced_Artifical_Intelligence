# 3.1–3.2. Biểu diễn game và kiến trúc hệ thống

## 3.1. Biểu diễn game

Connect Four dùng bàn cờ 6 hàng × 7 cột. Hàng 0 là hàng dưới cùng; một hành
động là chỉ số cột từ 0 đến 6. `ReferenceGame` lưu bàn cờ bằng list hai chiều,
còn `ConnectFour` dùng hai bitboard, mỗi cột chiếm 7 bit: 6 bit cho ô thật và
1 bit đệm để tránh dịch bit vượt biên giữa hai cột.

Hai engine cùng thực hiện một hợp đồng `ConnectFourGame`, gồm nước đi hợp lệ,
thả quân, hoàn tác, sao chép trạng thái, phát hiện thắng/hòa, mã hóa trạng thái
và chuyển trạng thái thành tensor 2×6×7 cho các agent học máy.

## 3.2. Kiến trúc

Luồng xử lý là `UI/CLI → Agent → ConnectFourGame → Match/Logger`. Agent chỉ
nhận bản sao trạng thái và trả về một cột hợp lệ. Bộ chạy trận đo thời gian từng
nước, ghi nước đi, số node/simulation từ `last_stats`, kết quả và trạng thái
vượt ngân sách vào các file CSV.

`ReferenceGame` là bản chậm, dễ đọc để kiểm tra `ConnectFour` bitboard. Mọi
khẳng định định lượng trong báo cáo phải lấy từ log chạy thực tế và điền vào
`results/tables/report_numbers.csv` theo `run_id`.
