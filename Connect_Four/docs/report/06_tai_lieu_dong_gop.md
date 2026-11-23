# Tài liệu tham khảo và đóng góp

## Tài liệu tham khảo

[1] Stuart J. Russell và Peter Norvig (2022). *Artificial Intelligence: A Modern
Approach*, ấn bản 4, Global Edition. Pearson. ISBN 978-1-292-40113-3.
Chương 6 là nguồn cho tìm kiếm đối kháng, minimax, Alpha-Beta và MCTS ở mục
2.1–2.2. Năm 2022 theo trang bản quyền bản Global Edition nhóm sử dụng;
bản Hoa Kỳ có năm xuất bản khác.

[2] Mark Liu (2025). *AlphaGo Simplified: Rule-Based AI and Deep Learning in
Everyday Games*. CRC Press. DOI: [10.1201/9781032722207](https://doi.org/10.1201/9781032722207).
Dùng làm tài liệu học về tác tử trò chơi, tìm kiếm và mạng chính sách.
Năm 2025 theo trang bản quyền, dù tên tệp tài liệu học có ghi 2024.

[3] Levente Kocsis và Csaba Szepesvári (2006). “Bandit Based Monte-Carlo
Planning.” *Machine Learning: ECML 2006*, tr. 282–293.
[Bản bài báo](https://aima.eecs.berkeley.edu/~russell/classes/cs294/s11/readings/Kocsis%2BSzepesvari%3A2006.pdf).
Nguồn thuật toán UCT; cách biểu diễn phần thưởng và chọn nước cuối cùng của
nhóm được mô tả riêng trong mục 2.2 và 3.3.

[4] Pascal Pons. “Solving Connect Four — Bitboard.”
[Bài viết của tác giả](http://blog.gamesolver.org/solving-connect-four/06-bitboard/).
Nguồn kỹ thuật biểu diễn bitboard được nhóm khai báo tại `docs/THIRD_PARTY.md`.
Không suy ra việc sao chép mã chỉ từ việc dùng cùng biểu diễn 7 bit/cột.

[5] Volodymyr Mnih và cộng sự (2015). “Human-level control through deep
reinforcement learning.” *Nature*, 518, tr. 529–533.
DOI: [10.1038/nature14236](https://doi.org/10.1038/nature14236).
Nguồn nền tảng cho DQN; không dùng kết quả Atari của bài báo làm kết quả
Connect Four của nhóm.

[6] Nhóm 26 (2026). [Proposal Connect Four](../proposal/ConnectFour_7x6_Proposal_Nhom26_HoanChinh.docx),
[kế hoạch và phân công](../kehoachphancong.pdf),
[mã nguồn và lịch sử đóng góp](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence).
Đây là tài liệu nội bộ xác định phạm vi, phân công và thiết kế thực nghiệm.

Thông tin thư mục được đối chiếu ngày 15/11/2026; đường dẫn Pascal Pons lấy từ nguồn đã khai báo, chưa tải lại được trong lần kiểm tra này. Mỗi tài liệu được dùng cho phần
được nêu ở trên; danh mục tham khảo không phải tuyên bố đã sử dụng toàn bộ
mã nguồn đi kèm tài liệu.

## Phần triển khai, kế thừa và công cụ hỗ trợ

Nhóm triển khai hệ thống Connect Four gồm engine, giao diện tác tử, bộ chạy
trận, kiểm thử và các phương pháp học/tìm kiếm trong repository. Các thuật toán
minimax, Alpha-Beta, UCT, CNN và DQN là phương pháp đã có; đóng góp của đồ án
là hiện thực, tích hợp, kiểm tra và đánh giá trong phạm vi Connect Four 7×6.

Nguồn tham khảo, phạm vi tái sử dụng và công cụ AI được khai báo tại
[THIRD_PARTY](../THIRD_PARTY.md). Với phần của Khang: **Codex hỗ trợ hoàn thiện**
mã, kiểm thử, thực nghiệm, tài liệu và slide. Khang cần tự kiểm tra và giải thích
phần bàn giao; thời gian chạy tự động không được quy thành giờ lao động cá nhân.
Không khẳng định toàn bộ mã lịch sử do từng cá nhân viết độc lập nếu chưa có
bằng chứng tương ứng. Phần nguồn của mỗi thành viên do thành viên đó xác nhận.

## Bảng phân công và tỷ lệ đóng góp

Theo xác nhận của trưởng nhóm Phạm Thái Duy Khang ngày 15/11/2026, tỷ lệ đóng
góp thống nhất là **25% mỗi thành viên, tổng 100%**. Đây là tỷ lệ nhóm xác nhận,
không phải phép tính dựa trên số commit, số dòng mã hoặc giờ máy chạy.

| Thành viên | MSSV | Phần phụ trách chính | Tỷ lệ |
| --- | --- | --- | ---: |
| Bùi Anh Đức | 3124720016 | Engine, chạy trận, terminal/GUI, biên tập báo cáo và đóng gói | 25% |
| Phạm Thái Duy Khang | 3124720033 | Tác tử cấp 1–4, A1/A2/A5, báo cáo tìm kiếm/kết luận, tổng hợp nhóm | 25% |
| Bùi Quyền Kiệt | 3124720036 | CNN cấp 5, dữ liệu, thống kê, A3, poster và in ấn | 25% |
| Phan Lê Ngọc Như Ý | 3124720079 | DQN cấp 6, giải đấu, phân tích kết quả và A4 | 25% |
| **Tổng** | | | **100%** |

Bằng chứng chi tiết nằm trong nhật ký của
[Đức](../contributions/bui-anh-duc.md),
[Khang](../contributions/pham-thai-duy-khang.md),
[Kiệt](../contributions/kiet.md) và
[Ý](../contributions/phan-le-ngoc-nhu-y.md), cùng PR/commit được dẫn trong đó.
Bảng phân công mô tả trách nhiệm, không có nghĩa mọi hạng mục của toàn nhóm đã
hoàn tất tại ngày xác nhận tỷ lệ.

## Khả năng truy vết

Số liệu thực nghiệm phải truy về `results/tables/report_numbers.csv`, bảng
kết quả tương ứng, log thô và `run_id` trong `results/logs/run_manifest.csv`.
Các mục còn thiếu giờ của Khang đã được liệt kê trong nhật ký cá nhân để bổ
sung sau. Báo cáo giữa kỳ đã nộp theo xác nhận của Khang; bản lưu và tag giữa kỳ cần
đối chiếu riêng khi hoàn tất hồ sơ repository.
