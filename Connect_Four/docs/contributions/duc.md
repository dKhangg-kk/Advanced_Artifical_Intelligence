# Đóng góp của Bùi Anh Đức (3124720016)

Tệp này là bản kê chi tiết theo yêu cầu bàn giao Đ6; hồ sơ đóng góp đã được
nhóm lập trước đó nằm tại [bui-anh-duc.md](./bui-anh-duc.md).

## Nhật ký đến 20/11/2026

| Ngày | Công việc | Bằng chứng | Thời gian |
| --- | --- | --- | --- |
| 08/11/2026 | ReferenceGame, engine bitboard, bộ chạy trận và giao diện cơ bản | commit `0f31c47` | Đức xác nhận theo giờ thực tế |
| 08/11/2026 | Terminal, test engine/cross-check/match, mục kiến trúc 3.1–3.2 | commit `1e1ca30` | Đức xác nhận theo giờ thực tế |
| 12/11/2026 | CLI giải đấu, ngân sách, đổi bên, CSV và test MCTS bổ sung | commit `48a682c` | Đức xác nhận theo giờ thực tế |
| 20/11/2026 | Hỗ trợ đối chiếu run K1/K3, biên tập mục 4.6, kiến trúc, bìa/mục lục; tạo công cụ ghép DOCX và slide 4 trang | `docs/report/04g_van_minh_hoa.md`, `docs/report/build_report.py`, `docs/slides/duc.pptx` | Hỗ trợ Codex; không quy đổi thành giờ lao động cá nhân |

Không suy ra số giờ từ số commit, thời gian chạy chương trình hoặc thời lượng
phiên trợ lý. Đức cần tự bổ sung số giờ thực tế và xác nhận đã đọc, hiểu các
nội dung được hỗ trợ trước khi dùng làm bằng chứng cá nhân.

## Phần có thể giải thích

- Vì sao bitboard Connect Four cấp 7 bit cho mỗi cột, và bit đệm ngăn phép dịch
  bit nối nhầm qua biên cột như thế nào.
- Khác biệt giữa engine bitboard và `ReferenceGame`; cách cross-check 1.000
  chuỗi ngẫu nhiên hỗ trợ kiểm tra luật.
- Vai trò của `play_game`, `play_match`, tập khai cuộc, đổi bên `a_starts` và
  việc ghi log ván/nước theo `run_id`.
- Bằng chứng trong log MCTS–Random cho thấy nước chặn cột 4 bị bỏ lỡ ở
  `mcts_vs_random-g085`; `over_budget=0` không ủng hộ giả thuyết timeout.

## Công cụ và nguồn

- Codex hỗ trợ tổng hợp thông tin từ repo, biên tập văn bản, tạo script ghép
  DOCX và sinh slide. Nội dung cần tác giả rà soát và chịu trách nhiệm giải thích.
- Ý tưởng bitboard 7 bit/cột và phát hiện bốn quân bằng dịch bit được ghi nhận
  tại `docs/THIRD_PARTY.md` (kỹ thuật của Pascal Pons); phần mã trong dự án tự
  cài đặt và được đối chiếu với `ReferenceGame`.
- Thư viện Pygame dùng cho UI; các thư viện ngoài được liệt kê trong
  `requirements.txt` và `docs/THIRD_PARTY.md`.
