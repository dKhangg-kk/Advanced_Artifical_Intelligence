# 3.1–3.2. Biểu diễn game và kiến trúc hệ thống

## 3.1. Biểu diễn game

Connect Four dùng bàn cờ 6 hàng × 7 cột. Hàng 0 là hàng dưới cùng; một hành
động là chỉ số cột từ 0 đến 6. `ReferenceGame` lưu bàn cờ bằng list hai chiều,
còn `ConnectFour` dùng hai bitboard, mỗi cột chiếm 7 bit: 6 bit cho ô thật và
1 bit đệm để tránh dịch bit vượt biên giữa hai cột.

Hai engine cùng thực hiện một hợp đồng `ConnectFourGame`, gồm nước đi hợp lệ,
thả quân, hoàn tác, sao chép trạng thái, phát hiện thắng/hòa, mã hóa trạng thái
và chuyển trạng thái thành tensor 2×6×7 cho các agent học máy.

Trong engine bitboard, mỗi bên có một số nguyên làm mặt nạ quân. Các ô của một
cột nằm liền nhau trong 7 bit; bit thứ bảy là bit đệm, không phải ô chơi. Nhờ
bit đệm, phép dịch giữa các cột không tạo nối giả qua biên. Hàm `_has_four`
kiểm tra các khoảng cách dịch 1, 7, 6 và 8, rồi dùng AND bit để phát hiện chuỗi
bốn theo chiều dọc, ngang và hai đường chéo. `ReferenceGame` cài cùng luật bằng
lưới hai chiều và quét 69 cửa sổ thắng; đây là đối chứng độc lập, ưu tiên dễ
đọc hơn tốc độ. Test cross-check chạy 1.000 chuỗi nước ngẫu nhiên và so sánh
bàn cờ, người chơi hiện tại, người thắng và nước hợp lệ sau từng nước.

## 3.2. Kiến trúc

```text
Người chơi ───────────────┐
                          v
play.py (terminal) ──┐  ui/gui.py (Pygame)
                     └───────┬──────────────
                             v
                       Agent.choose(game.clone())
                             |
                             v
              ConnectFourGame (hợp đồng chung)
                       /             \
          ConnectFour               ReferenceGame
          bitboard 49-bit           lưới 6 × 7
                       \             /
                        v           v
                 evaluation/match.py
                 play_game / play_match
                          |
                          v
               evaluation/runlog.py
             games.csv + moves.csv + manifest
```

Luồng điều khiển là `UI/CLI → Agent → ConnectFourGame`; nhánh đánh giá dùng
`evaluation/match.py` để chạy ván/cặp ván và `evaluation/runlog.py` để lưu log.
`play.py` phục vụ chơi trong terminal; `ui/gui.py` cung cấp giao diện Pygame.
Agent nhận bản sao trạng thái để không sửa bàn cờ của ván thật. Bộ chạy trận
đo thời gian từng nước bằng đồng hồ đơn điệu, ghi số node/simulation từ
`last_stats`, kết quả và cờ vượt ngân sách vào CSV.

### Vai trò các thành phần

| Thành phần | Trách nhiệm |
| --- | --- |
| `game/engine.py` | Engine bitboard 49-bit dùng trong chơi và đánh giá |
| `game/reference.py` | Engine dạng lưới, dùng đối chiếu độc lập |
| `evaluation/match.py` | Chạy một ván hoặc nhiều ván; dùng khai cuộc và đổi bên theo cặp |
| `evaluation/runlog.py` | Ghi manifest, log ván và log từng nước theo `run_id` |
| `play.py` | Chơi người–máy hoặc máy–máy trong terminal |
| `ui/gui.py` | Chọn người chơi/tác tử, hiển thị bàn cờ và thời gian nước đi |

Các thành phần được kiểm thử bằng test engine, cross-check, match và smoke
tests. Những con số thực nghiệm phải truy ngược được tới CSV thô và
`results/tables/report_numbers.csv`.
