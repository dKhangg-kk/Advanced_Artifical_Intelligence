# Quy ước đóng góp

## 1. Nhánh

| Loại | Mẫu | Ví dụ |
|---|---|---|
| Tính năng | `feat/<mo-ta-ngan>` | `feat/engine-bitboard` |
| Sửa lỗi | `fix/<mo-ta-ngan>` | `fix/undo-sai-nguoi` |
| Tài liệu | `docs/<mo-ta-ngan>` | `docs/roadmap-tuan-5` |

Không commit trực tiếp lên `main`. Mỗi nhánh một việc, mở pull request khi xong.

## 2. Commit

Theo quy ước của học phần, ghi rõ **tuần / đồ án / việc đã làm**:

```text
TuanXX/DuAn/Noi dung cong viec
```

Ví dụ:

```text
Tuan05/DuAn/Cai dat engine bitboard va test luat
Tuan05/DuAn/Bo sung Heuristic theo thu tu uu tien 1-4
Tuan06/DuAn/Chay giai dau 4 tac tu va luu log CSV
```

Mỗi commit một thay đổi rõ ràng. Không gộp code + định dạng + đổi tên file vào một commit.

## 3. Pull request

- Tiêu đề: `[Mốc] Việc đã làm`, ví dụ `[M1] Engine bitboard + test crosscheck`
- Mô tả: làm gì, **cách kiểm tra**, ảnh/log nếu có
- Bắt buộc: `pytest -q` xanh trước khi mở PR
- Người review kiểm tra logic, không chỉ chạy test

## 4. Chạy thử

```bash
cd Connect_Four
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .          # tuy chon, de chay lenh c4-play / c4-tournament
pytest -q
```

## 5. Quy ước code

- Python 3.10+, type hint đầy đủ cho hàm public.
- Không import `torch` / `pygame` / `pandas` ở cấp module — chỉ import trong hàm,
  để `pytest` chạy được trên máy chưa cài đủ thư viện (và trên CI).
- Mọi hàm public có docstring ngắn: làm gì, tham số, ngoại lệ.
- Không hard-code tham số thuật toán: đọc từ `configs/*.yaml`.
- Không sửa trực tiếp trạng thái `game` trong `Agent.choose()`; dùng `clone()` / `undo()`.
- Mọi ngẫu nhiên phải nhận `seed` và dùng `random.Random(seed)` / `np.random.default_rng(seed)`.

## 6. Thêm một tác tử mới

1. Tạo `src/connect_four/agents/<ten>.py`, kế thừa `Agent`, khai báo `name` và `level`.
2. Cài đặt `choose(game) -> int`, cập nhật `self.last_stats`.
3. Đăng ký trong `AGENTS` ở `agents/__init__.py`.
4. Thêm mục vào `configs/agents.yaml`.
5. Viết test trong `tests/test_agents.py`.

## 7. Định nghĩa "xong"

Một việc chỉ được đánh dấu xong khi:

- có code + test đi kèm,
- `pytest -q` xanh,
- tài liệu liên quan (README, ROADMAP) đã cập nhật,
- nếu tạo ra số liệu thực nghiệm: có log thô trong `results/logs/` và cấu hình trong `configs/`.

## 8. Không nộp những gì chưa chạy

Không ghi kết quả huấn luyện/benchmark chưa thực hiện. Không dùng checkpoint chưa huấn luyện
để minh chứng hoàn thành cấp 5/6. Không chọn các ván thắng để minh họa kết luận tổng thể.
