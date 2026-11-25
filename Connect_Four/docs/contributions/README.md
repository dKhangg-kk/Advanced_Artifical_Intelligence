# Bảng đối soát đóng góp

Bảng này là nơi tổng hợp để nộp cùng báo cáo. Số giờ và tỷ lệ đóng góp phải do
từng thành viên xác nhận; không tự suy ra từ số dòng code
| Thành viên | Phần việc đã có dấu vết | Hồ sơ và minh chứng | Tỷ lệ |
| --- | --- | --- | ---: |
| Bùi Anh Đức | Engine bitboard, engine tham chiếu, test/check và tài liệu kiến trúc | [Hồ sơ đóng góp](bui-anh-duc.md) | 25% |
| Phạm Thái Duy Khang | Heuristic, Alpha-Beta, pilot K1 | [Hồ sơ đóng góp](pham-thai-duy-khang.md) | 25% |
| Phan Lê Ngọc Như Ý | DQN Level 6, vòng huấn luyện, Tournament CLI, thực nghiệm và phân tích | [Hồ sơ công việc chi tiết](phan-le-ngoc-nhu-y.md) | 25% |
| Bùi Quyền Kiệt | Metrics/CI, kiểm thử luật, dữ liệu và CNN, ablation, báo cáo | [Hồ sơ đóng góp](kiet.md) | 25% |

## Quy tắc chốt trước khi nộp

1. Mỗi thành viên bổ sung số giờ thực tế, không điền theo ước lượng.
2. Mỗi dòng công việc phải có commit, PR, issue hoặc file kết quả tương ứng.
3. Tổng tỷ lệ đóng góp phải bằng 100% và phản ánh cả code, tài liệu, thí nghiệm,
   thuyết trình.
4. Không ghi nhận training, benchmark hoặc checkpoint nếu không có log/chứng
   cứ trong repository.

## Phân công và bằng chứng thực nghiệm

- Bảng phân công 4 thành viên: [`results/experiment_plan.csv`](../../results/experiment_plan.csv).
- Người chạy từng lần thử nghiệm: [`results/experiment_assignments.csv`](../../results/experiment_assignments.csv).
  Các dòng `CHƯA XÁC NHẬN` phải do thành viên xác nhận trước khi nộp.
- File tổng hợp duy nhất gửi giảng viên: [`results/experiment_schedule.xlsx`](../../results/experiment_schedule.xlsx)
  gồm 3 sheet: `Phan cong`, `Thuc nghiem`, `Minh chung`. Mọi dòng ở sheet
  `Thuc nghiem` có ngày giờ đầy đủ, đã đổi từ UTC sang giờ Việt Nam (UTC+7).
- Sinh lại file: `cd Connect_Four && PYTHONPATH=src python scripts/build_experiment_workbook.py`
  (cần `python -m pip install -e ".[analysis]"` để có `openpyxl`).
- **Không sửa tay file `.xlsx`** — nguồn sự thật là `results/logs/run_manifest.csv`
  và hai file CSV nêu trên.
- Mỗi người làm trên nhánh `exp/<ten>/<task>`, commit log + CSV + nhật ký rồi mở
  PR. Sau khi PR được merge, chạy lại script và commit file Excel mới.
