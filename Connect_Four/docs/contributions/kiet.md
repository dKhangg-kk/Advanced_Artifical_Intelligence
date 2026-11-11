# Đóng góp của Bùi Quyền Kiệt (3124720036)

## Mã việc và phạm vi sở hữu

| Mã việc | Milestone | Phụ trách | Review | Tệp trong phạm vi |
| --- | --- | --- | --- | --- |
| `METRICS-CI` ([Issue #18](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/issues/18)) | M2 — Bốn tác tử cổ điển | Bùi Quyền Kiệt | Ý | `src/connect_four/evaluation/metrics.py`, `tests/test_metrics.py` |
| `DONGGOP-KIET` ([Issue #44](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/issues/44)) | M5 — Demo và báo cáo | Bùi Quyền Kiệt | Ý | `docs/contributions/kiet.md` |

Issue #18 giao phần khoảng tin cậy; Issue #44 giao nhật ký này. Các tệp khác trong [lộ trình M5](../ROADMAP.md) không được xem là phân công cá nhân nếu chưa có issue hoặc xác nhận riêng.

## Nhật ký

| Ngày | Việc | PR/commit | Giờ |
| --- | --- | --- | --- |
| 08/11/2026 | Xác minh lịch sử tài khoản: commit đầu tiên trong ngày là `e7cdfa0`, nhưng thay đổi thuộc Tuan01/Lab00, không thuộc dự án Connect Four nên không tính là đóng góp cho đồ án. | [Commit `e7cdfa0`](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/commit/e7cdfa0) | Chưa ghi nhận; không tính giờ đồ án từ commit ngoài phạm vi |
| 09/11/2026 | Chưa xác minh được hoạt động Connect Four của tôi trong lịch sử Git/PR đã kiểm tra. | Chưa có dẫn chứng | Chưa ghi nhận |
| 10/11/2026 | Chưa xác minh được hoạt động Connect Four của tôi trong lịch sử Git/PR đã kiểm tra. | Chưa có dẫn chứng | Chưa ghi nhận |
| 11/11/2026 | Cài đặt Wilson và bootstrap CI có seed; bổ sung test cho giá trị 200/200, tính lặp lại và dữ liệu sai; cập nhật tài liệu và nhật ký. | Issue #18; commit `19521e5` (local, chưa push; thiếu Git credentials để mở PR) | Chưa ghi nhận; cần tác giả xác nhận |

Không thể dùng commit ngày 08/11 nói trên làm căn cứ cho một commit Connect Four trong ngày đó. Không hồi tố ngày commit, không suy ra số giờ từ timestamp hoặc thời gian chạy công cụ. Tiếp tục bổ sung từng ngày đến 21/11/2026; ngày không làm việc cần ghi rõ, và giờ cần dựa trên thời gian thực tế.

Kiểm tra Issue #18: `python -m pytest -q tests/test_metrics.py` đạt 12 test; toàn bộ `python -m pytest -q` đạt 189 test, 3 test skip. Import `connect_four.evaluation.metrics` không nạp `torch`.

## Căn cứ chốt tỷ lệ đóng góp

Tỷ lệ đóng góp chưa được xác định. Trước 19/11 cần tổng hợp các PR đã review/merge, commit thuộc phạm vi, tệp và kết quả bàn giao, log thực nghiệm (nếu có), cùng giờ thực tế được xác nhận. Không tính commit ngoài đồ án hoặc công việc chưa có bằng chứng.

## Phần tôi tự giải thích được

- Phạm vi của Issue #44 và lý do nhật ký chỉ nhận quyền sở hữu đối với tệp được giao.
- Công thức Wilson và cách khoảng tin cậy vẫn có cận dưới hữu ích khi tỷ lệ quan sát là 200/200.
- Cách bootstrap lấy mẫu có hoàn lại, tính khoảng percentile và dùng seed để tái lập kết quả.
- Cách phân biệt một commit trên tài khoản cá nhân với đóng góp thực sự thuộc dự án Connect Four.
- Cách dùng PR/commit, kết quả bàn giao và thời lượng thực tế làm căn cứ; không suy ra tỷ lệ hay giờ từ lịch sử commit đơn thuần.

Các hạng mục M5 khác chưa được xác nhận là phân công cá nhân tại thời điểm cập nhật này.

## Công cụ và nguồn

- Git và GitHub: kiểm tra lịch sử commit, Issue #18, Issue #44 và các PR liên quan.
- GitHub Copilot: hỗ trợ đối chiếu thông tin và soạn nhật ký; nội dung cần được tôi xác nhận theo công việc thực tế.
- Nguồn trong repository: [README thành viên](../../README.md), [lộ trình](../ROADMAP.md), [quy ước đóng góp](../../CONTRIBUTING.md) và các nhật ký đóng góp hiện có.
- Issue #18 và Issue #44 dẫn nguồn “Kế hoạch & phân công Nhóm 100 - Connect Four AI (8 11 → 22 11 2026).docx”. Bản DOCX không có trong workspace tại thời điểm ghi nhật ký; vì vậy không suy diễn thêm phân công ngoài thông tin có trong issue và repository.
