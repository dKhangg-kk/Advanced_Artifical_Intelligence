# Đóng góp của Bùi Anh Đức (3124720016)

## Phần phụ trách

Nền tảng game: engine bitboard, engine tham chiếu, chạy trận, giao diện/terminal,
test đối chiếu và phần báo cáo kiến trúc tương ứng (mục 3.1–3.2).

## Nhật ký

| Ngày | Việc đã làm | PR/commit | Giờ |
| --- | --- | --- | --- |
| 08/11/2026 | Bổ sung `ReferenceGame`, hoàn thiện engine bitboard, bộ chạy trận và giao diện cơ bản | `0f31c47` | TODO |
| 08/11/2026 | Bổ sung terminal, test engine/cross-check/match và tài liệu kiến trúc mục 3.1–3.2 | `1e1ca30` | TODO |

## Kết quả kiểm tra

- `pytest -q`: **42 passed**.
- `random` đấu `random` chạy hoàn tất một ván trong terminal.
- `ReferenceGame` và `ConnectFour` được kiểm tra chéo trên các chuỗi nước đi ngẫu nhiên.
- Phần này **không bao gồm** việc hoàn thiện các tác tử Heuristic, Alpha-Beta, MCTS,
  CNN/DQN hoặc toàn bộ hệ thống giải đấu; các phần đó do thành viên/phần việc khác phụ trách.

## Phần tôi giải thích được

- Vì sao bitboard dùng 7 bit cho mỗi cột.
- Vì sao cần `ReferenceGame` chậm để đối chiếu engine nhanh.
- Cách dùng cùng một tập khai cuộc và đổi bên trong `play_match`.
- Cách log từng nước và kết quả ván để tái lập báo cáo.

## Công cụ và nguồn đã dùng

- Python và NumPy: cài đặt trạng thái game, bitboard và biểu diễn bàn cờ.
- pytest: kiểm thử engine, đối chiếu bitboard với `ReferenceGame` và kiểm thử chạy trận.
- Pygame: giao diện GUI của dự án.
- Không ghi nhận việc sao chép mã nguồn bên ngoài trong các commit nêu trên; các thư viện sử dụng
  được khai báo trong `requirements.txt`/`pyproject.toml`.

## Việc còn cần bổ sung trước khi nộp

- Điền số giờ thực tế cho từng dòng nhật ký.
- Nếu nhóm dùng công cụ AI hoặc mã tham khảo bên ngoài, ghi cụ thể công cụ, nguồn và phần đã dùng
  tại đây và trong `docs/THIRD_PARTY.md`.
- Tạo/liên kết PR nếu quy trình nhóm yêu cầu bằng chứng review; hiện nhật ký đang dùng commit hash.
