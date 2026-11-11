# Đóng góp của Bùi Quyền Kiệt

## Phần phụ trách

Sinh và chia dữ liệu policy được gán nhãn Alpha-Beta cho cấp 5, gồm nguồn dữ liệu chính và cohort dành cho ablation A3.

## Nhật ký

| Ngày | Việc đã làm | PR/commit và log |
| --- | --- | --- |
| 11/11/2026 | Hoàn thiện bộ sinh 5.000 ván duy nhất ở Alpha-Beta depth 4 sau khai cuộc ngẫu nhiên 6–8 nước; chia theo ván 70/15/15, lọc trạng thái trùng/đối xứng và chỉ lật gương train. | [PR #68](https://github.com/dKhangg-kk/Advanced_Artifical_Intelligence/pull/68); commits `769b4e4`, `8e10571`, `8c2569c`; manifest: `data/generated/splits/manifest.json`. |
| 11/11/2026 | Chạy bộ dữ liệu seed 0: 5.000 ván (3.000 main model, 2.000 A3), 110.083 mẫu thô, loại 18.025 trạng thái trùng; còn 66.619/13.028/12.411 mẫu train/val/test trước lật gương. | `cd Connect_Four && .venv/bin/python -c "from connect_four.training.gen_data import generate_dataset; generate_dataset(seed=0)"`; pytest xanh. |

## Phần tôi giải thích được

- Mỗi ván dùng `AlphaBetaAgent` ở một độ sâu cố định; các khai cuộc ngẫu nhiên tạo đa dạng, còn phần còn lại của ván được gán nhãn bằng nước Alpha-Beta chọn.
- Chia game trước khi lọc các trạng thái giống nhau hoặc tương đương qua phép lật ngang, nhờ đó không rò rỉ giữa train, validation và test.
- Chỉ mẫu train được lật gương; nhãn cột được đổi theo `6-c`. Manifest ghi ID game từng tập, tỷ lệ thực tế và số mẫu bị lọc.

## Công cụ và nguồn đã dùng

Python, NumPy và pytest; engine `ConnectFour`, `AlphaBetaAgent` và cấu hình ablation A3 trong repository.
