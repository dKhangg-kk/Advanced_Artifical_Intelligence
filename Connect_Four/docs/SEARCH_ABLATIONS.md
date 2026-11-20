# A1/A2/A5 — chạy và tái lập

Chạy từ thư mục `Connect_Four`. Dùng Python 3.10+ và các phụ thuộc đã có trong
dự án (`pip install -e '.[dev,analysis]'`). Không cần torch cho các tác tử tìm kiếm.

```sh
PYTHONPATH=src python scripts/run_search_ablations.py --experiment a1
PYTHONPATH=src python scripts/run_search_ablations.py --experiment a5
PYTHONPATH=src python scripts/run_search_ablations.py --experiment a2
PYTHONPATH=src python scripts/analyze_search_ablations.py
```

Ba lệnh chạy nên thực hiện tuần tự để tránh tranh CPU khi đo độ trễ. Cấu hình
nằm trong `configs/ablation_a1_pruning.yaml`, `ablation_a2_mcts_budget.yaml`,
`ablation_a5_depth.yaml`. Không thay tham số sau khi chạy rồi gán lại cho log cũ.

## Sản phẩm

- `results/logs/positions_<run_id>.csv`: từng thế, độ sâu, công tắc, lần lặp,
  cột chọn, điểm, nút và thời gian. Thế kết thúc ghi `excluded_terminal`.
- `results/logs/games_<run_id>-<mức>.csv` và `moves_<run_id>-<mức>.csv`:
  kết quả và từng nước của A2/A5; `run_id` con liên kết với run cha qua bảng.
- `results/logs/ablation_<run_id>.csv`: độ đo theo schema chung.
- `results/logs/run_manifest.csv`: commit, hash cấu hình, hash bộ thế (nếu có),
  thời điểm UTC, seed, môi trường và trạng thái. Thời gian này là giờ máy chạy.
- `results/tables/<run_id>.csv`: bảng gắn lần chạy; tên `ablation_a*_results.csv`
  là bảng hiện hành dùng cho notebook, được cập nhật khi chạy lại.
- `notebooks/03_search_ablations.ipynb`: phân tích từ log thô và dựng ba hình
  `results/figures/ablation_a{1,2,5}_search.png`.

Script phân tích kiểm tra lại các độ đo với log trước khi cập nhật
`report_numbers.csv`; chỉ thay các dòng của run K4 đang phân tích, giữ các run
khác. Không chạy lại ván đấu khi chỉ muốn dựng lại hình.

## Quy tắc thí nghiệm

A1: bộ 31 thế có một thế hòa đầy bàn nên 30 thế được đo; độ sâu 4/5/6, bốn
công tắc, năm lần lặp. Kiểm tra cùng giá trị minimax, không bắt buộc cùng cột
khi hòa điểm. A5 đo bộ thế ở sâu 2–6, ba lần lặp; mỗi mức còn đấu 100 ván với
Heuristic. A2 dùng 100/500/1000/2000/5000 mô phỏng, mỗi mức đấu 100 ván với
Alpha-Beta sâu 4. Cả hai dùng 50 khai cuộc dài bốn nước đổi bên.

Seed khai cuộc: 20261104. Seed tác tử ngẫu nhiên ván `i` (0–99): `seed+i`.
Mỗi mức tạo lại tác tử và dùng cùng lịch seed. Đây là một cohort khai cuộc,
không phải 100 thí nghiệm độc lập. Mọi ván được replay bằng ReferenceGame.

Score = (thắng + 0,5 × hòa)/N. CI score lấy bootstrap 10.000 lần trên cặp
khai cuộc. Wilson tỷ lệ thắng được lưu để tham khảo, do hai ván chung khai
cuộc không hoàn toàn độc lập. Độ trễ được gộp từ từng nước; p95 là nearest-rank.

## Các lần chạy đã lưu

| Thí nghiệm | Run ID | Mã chạy |
| --- | --- | --- |
| A1 | `ablation-a1-20261114T172315Z-s20261104` | `1b79dd5` |
| A5 | `ablation-a5-20261114T173556Z-s20261104` | `1b79dd5` |
| A2 | `ablation-a2-20261114T173956Z-s20261104` | `1b79dd5` |

Ngày địa phương là 15/11/2026; ID dùng UTC. Có 1.800 lần đo A1, 450 lần đo
thế A5 và 1.000 ván đối đầu. Dữ liệu hoàn tất không tự đồng nghĩa với bộ số
liệu toàn nhóm đã đóng băng.

Nếu chạy bị ngắt, giữ log đã có và chạy lại với ID mới. Chương trình ghi bảng
và log đối đầu sau mỗi mức hoàn tất; các ván của mức chưa xong có thể phải
chạy lại. Không nối dữ liệu hai lần chạy thành một `run_id`.
