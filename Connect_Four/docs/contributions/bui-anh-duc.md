# Đóng góp của Bùi Anh Đức (3124720016)

## Phần phụ trách

Nền tảng game: engine bitboard, engine tham chiếu, chạy trận, giao diện/terminal,
test đối chiếu và phần báo cáo kiến trúc tương ứng (mục 3.1–3.2).

## Nhật ký

| Ngày | Việc đã làm | PR/commit | Giờ |
| --- | --- | --- | --- |
| 08/11/2026 | Bổ sung `ReferenceGame`, hoàn thiện engine bitboard, bộ chạy trận và giao diện cơ bản | `0f31c47` | TODO |
| 08/11/2026 | Bổ sung terminal, test engine/cross-check/match và tài liệu kiến trúc mục 3.1–3.2 | `1e1ca30` | TODO |
| 12/11/2026 | Hoàn thiện CLI giải đấu: tạo tác tử theo tham số, áp dụng ngân sách depth/simulation/time, chạy cặp đấu đổi bên và lưu log games/moves; bổ sung test MCTS về nước hợp lệ, tính tái lập, ngân sách và không làm đổi bàn cờ | `48a682c` | Chưa ghi nhận |
| 25/11/2026 | Thực hiện 3 nhiệm vụ thực nghiệm CLI cross-check theo phân công: Random–Heuristic (10 openings, seed 2026), Alpha-Beta depth 3 vs Random (5 openings, seed 2026), MCTS 200 sims vs Random (5 openings, seed 2026); cập nhật manifest, assignments, EXPERIMENT_LOG.md và hoàn tất merge PR #87 | PR #87 / commit `6572c26` | Đức tự điền giờ thực tế |
| 25/11/2026 | Hoàn thiện hạng mục Đ6 - Kiểm thử tái lập trên môi trường máy sạch: giả lập `%TEMP%\connect4_clean_verify`, chuẩn hóa 5 bước hướng dẫn chạy trong README.md, bổ sung `openpyxl` vào requirements.txt, xác nhận 380/380 tests passed 100% | `docs/contributions/duc.md`, `Connect_Four/README.md`, `requirements.txt` | Đức tự điền giờ thực tế |

## Kết quả kiểm tra

- `pytest -q`: **380 passed** (toàn bộ test suite đồ án đạt 100% xanh).
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
