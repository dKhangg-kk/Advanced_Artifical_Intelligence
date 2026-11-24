# Đóng góp của Bùi Anh Đức (3124720016)

Tệp này là bản kê chi tiết theo yêu cầu bàn giao Đ6; hồ sơ đóng góp đã được
nhóm lập trước đó nằm tại [bui-anh-duc.md](./bui-anh-duc.md).

## Nhật ký công việc

| Ngày | Công việc | Bằng chứng | Thời gian |
| --- | --- | --- | --- |
| 08/11/2026 | ReferenceGame, engine bitboard, bộ chạy trận và giao diện cơ bản | commit `0f31c47` | Đức xác nhận theo giờ thực tế |
| 08/11/2026 | Terminal, test engine/cross-check/match, mục kiến trúc 3.1–3.2 | commit `1e1ca30` | Đức xác nhận theo giờ thực tế |
| 12/11/2026 | CLI giải đấu, ngân sách, đổi bên, CSV và test MCTS bổ sung | commit `48a682c` | Đức xác nhận theo giờ thực tế |
| 20/11/2026 | Hỗ trợ đối chiếu run K1/K3, biên tập mục 4.6, kiến trúc, bìa/mục lục; tạo công cụ ghép DOCX và slide 4 trang | `docs/report/04g_van_minh_hoa.md`, `docs/report/build_report.py`, `docs/slides/duc.pptx` | Hỗ trợ Codex; không quy đổi thành giờ lao động cá nhân |
| 25/11/2026 | Thực nghiệm CLI cross-check (3 nhiệm vụ: Random–Heuristic 10 openings, AlphaBeta d=3 vs Random 5 openings, MCTS 200 sims vs Random 5 openings, seed 2026), cập nhật manifest, assignments, EXPERIMENT_LOG.md và hoàn tất merge PR #87 | PR #87 / commit `6572c26` | Đức tự điền giờ thực tế |
| 25/11/2026 | Kiểm thử tái lập README trên máy sạch (Đ6): giả lập môi trường tách biệt `%TEMP%\connect4_clean_verify`, kiểm chứng trọn vẹn 5 bước hướng dẫn chạy (venv, pytest, play terminal, pygame gui, evaluation cli), bổ sung `openpyxl` vào requirements.txt, chuẩn hóa tài liệu hướng dẫn chạy | `Connect_Four/README.md`, `Connect_Four/requirements.txt`, kết quả kiểm thử tái lập | Đức xác nhận theo giờ thực tế |

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

## Kết quả kiểm chứng tái lập trên máy sạch (Hạng mục Đ6 - 25/11/2026)

Thực hiện kiểm thử độc lập quy trình tái lập dự án từ môi trường sạch hoàn toàn (Clean Environment) mô phỏng máy chấm bài của giảng viên:
- **Hệ điều hành:** Windows 11 Home / Windows 10 (OS Build 26100), x86_64 architecture.
- **Phiên bản Python kiểm chuẩn:** Python 3.11.9 (CPython 64-bit).
- **Môi trường giả lập:** Thư mục cô lập hoàn toàn `%TEMP%\connect4_clean_verify`, loại bỏ toàn bộ `.venv*`, `__pycache__`, `.pytest_cache`, `*.egg-info`.
- **Cài đặt thư viện:** Cài đặt thành công qua `pip install -r requirements.txt` và `pip install -e .` (đã bổ sung `openpyxl>=3.1,<4` cho tính năng xuất báo cáo Excel của nhóm).
- **Kết quả kiểm thử tự động (`pytest -q` / `pytest -ra`):**
  + **380 / 380 tests passed** (100% test suite đạt trạng thái xanh, 0 failed, 0 error).
  + Thời gian chạy toàn bộ test suite: ~85 giây.
  + Kiểm thử toàn diện: Engine bitboard, Reference game, Random, Heuristic, Alpha-Beta, MCTS, CNN (Cấp 5), DQN (Cấp 6), ExactSolver, Pygame Controller, CLI evaluation và báo cáo thực nghiệm.
- **Kiểm chứng các luồng thực thi trong README:**
  1. *Cài đặt:* Tạo venv, kích hoạt và cài đặt gói nội bộ `pip install -e .` thành công, các lệnh CLI entrypoint `c4-play` và `c4-tournament` hoạt động chính xác.
  2. *Kiểm thử:* `python -m pytest -q` trả về `380 passed`.
  3. *Chơi trên Terminal:*
     - Chế độ Người vs Máy: `python -m connect_four.play --opponent heuristic` nhận diện đúng nước đi cột 0–6.
     - Chế độ Máy vs Máy: `python -m connect_four.play --a random --b heuristic --auto` chạy trọn vẹn ván cờ, xuất bàn cờ và xác định thắng thua rõ ràng.
  4. *Giao diện Pygame:* `python -m connect_four.ui.gui --a human --b dqn --start` tải thành công trọng số `checkpoints/level6_dqn/final.pt`, xử lý mượt mà sự kiện chuột/phím và cơ chế guard chặn nước thua tức thời.
  5. *Đánh giá đối kháng CLI:* `python -m connect_four.evaluation.cli --a random --b heuristic --openings 1 --out results/logs/smoke_r_vs_h.csv` ghi nhận 2 ván đổi bên đối xứng, xuất đủ log ván/nước và tóm tắt tỷ số chính xác.
