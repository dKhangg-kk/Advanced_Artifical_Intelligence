# Lab 01 — Intelligent Agents


## 1. Nội dung được giao

| Bài tập | Mô tả ngắn |
|---|---|
| Robot Vacuum | Xây dựng môi trường hút bụi, cài đặt simple reflex agent, model-based reflex agent, so sánh hiệu suất trên nhiều kích thước phòng |
| GridHunt (đơn agent) | Cài đặt model-based agent săn quái vật trong lưới, so sánh với random agent và teleport |
| GridHunt (đa agent) | Cài đặt greedy hunter cộng tác đuổi monster, thí nghiệm trên nhiều kích thước lưới |
| Lunar Lander | Cải tiến reflex agent điều khiển tàu đáp lên mặt trăng bằng Gymnasium, đánh giá qua 100 episode |


## 2. Bài làm

| File | Loại | Mô tả |
|---|---|---|
| [`Robot_Vacuum.ipynb`](Robot_Vacuum.ipynb) | Notebook | Môi trường hút bụi + 3 loại agent + nghiên cứu so sánh |
| [`gridhunt_mini_assignment_completed.ipynb`](gridhunt_mini_assignment_completed.ipynb) | Notebook | GridHunt đơn agent — model-based, random, teleport |
| [`gridhunt_multiagent_mini_assignment.ipynb`](gridhunt_multiagent_mini_assignment.ipynb) | Notebook | GridHunt đa agent — greedy hunter vs random |
| [`lunar_lander-2.ipynb`](lunar_lander-2.ipynb) | Notebook | Reflex agent điều khiển Lunar Lander (Gymnasium) |
| [`lab01.docx`](lab01.docx) | Báo cáo | Báo cáo thực hành lab 01 |


## 3. Cách chạy

### Môi trường chung
- **Python:** 3.12+ (kernel Python 3 / `.venv 3.12.3` / `base`)
- **Jupyter Notebook** hoặc **JupyterLab**

### Thư viện cần cài

```bash
pip install numpy pandas matplotlib
```

Riêng **Lunar Lander** cần thêm:

```bash
pip install gymnasium
pip install gymnasium[box2d]       # render LunarLander
pip install gymnasium-display-recorder
```

### Các bước chạy

1. Mở terminal, vào thư mục lab:
   ```bash
   cd lab01_agent_PhanLeNgocNhuY_3124720079
   jupyter notebook
   ```
2. Mở từng file `.ipynb` theo thứ tự đề xuất:
   - `Robot_Vacuum.ipynb` → chạy tất cả cell từ trên xuống.
   - `gridhunt_mini_assignment_completed.ipynb` → chạy tất cả cell.
   - `gridhunt_multiagent_mini_assignment.ipynb` → chạy tất cả cell.
   - `lunar_lander-2.ipynb` → **chú ý:** phải chạy cell đánh giá (cell 39) **trước** cell vẽ biểu đồ (cell 38) để tránh `NameError: name 'baseline_rewards' is not defined`.

> **Đã kiểm tra:** GridHunt đơn agent và đa agent chạy lại thành công toàn bộ trong môi trường Anaconda Python. Robot Vacuum chạy được nhưng chưa kiểm tra phần GUI/video. Lunar Lander cần sửa thứ tự cell trước khi chạy lại từ đầu.


## 4. Kết quả và nhận xét

### Robot Vacuum

- **Task 1–3:** Môi trường lưới bẩn (xác suất 0.2), simple reflex agent và model-based reflex agent (về góc Tây-Bắc rồi quét zích-zắc) hoạt động đúng. Kiểm tra với phòng toàn bụi n=1, 2, 5 — 10 seed mỗi kích thước — đều dừng trước giới hạn bước.
- **Task 4:** Thí nghiệm 3 agent × 3 kích thước (5×5, 10×10, 100×100) × 100 lần. Bảng và biểu đồ có đầu ra. Tuy nhiên khi hết `max_steps`, kết quả vẫn được tính vào trung bình như lần dọn xong; **cần tách tỷ lệ hoàn thành thực sự khỏi số bước tiêu thụ.**
- **Task 5 + Advanced:** Có thảo luận về robustness (phòng bất thường, vật cản, nhiễu); agent quét hai lượt trong môi trường nhiễu 10% cải thiện rõ rệt số ô còn bẩn (có bảng so sánh 100 lần chạy).
- **Vấn đề còn gặp:** Task 4 không phân biệt "hết ngân sách" và "dọn sạch thành công"; phần trình bày dùng comment thay Markdown; ngân sách hai agent trong phần Advanced khác nhau (500 vs 1000 bước) nên cần nêu khi so sánh.

### GridHunt (đơn agent)

- Model-based agent nhớ vị trí monster sau lệnh `listen`, lưu riêng theo từng episode.
- Thí nghiệm 100 lần, lưới 10×10 và 30×30: model-based agent vượt trội random; teleport được phân tích riêng.
- **Phần tự thực hiện:** cài đặt model-based agent (cell 22–23), thí nghiệm so sánh (cell 25–26), kết luận (cell 28, 30).
- **Tham chiếu gốc:** khung môi trường GridHunt do giảng viên cung cấp. Tên tác giả ghi trong notebook là "Bùi Kiệt" (cần xác nhận lại khi nộp).

### GridHunt (đa agent)

- Greedy hunter đuổi theo vị trí hiện tại của monster; thử nghiệm 30×30, 50×50, 80×80 — 100 lần mỗi cấu hình.
- **Hạn chế môi trường gốc:** `np.random.randint(0, n-1, ...)` không chọn hàng/cột cuối; kiểm tra bắt monster chỉ xét đầu lượt — đây là hạn chế của khung gốc, cần lưu ý khi diễn giải kết quả.
- **Phần tự thực hiện:** greedy hunter (cell 22), thí nghiệm (cell 24), kết luận (cell 26, 28).
- Cell 1 còn placeholder `[Add your name]`, `[list tools]`, `[your initials]` — cần điền trước khi nộp.

### Lunar Lander

- Agent cải tiến dùng thruster trái/phải và kiểm soát góc; đánh giá qua 100 episode.
- Output lưu cho thấy reward trung bình tốt hơn baseline, tuy nhiên tỷ lệ hạ cánh thành công vẫn thấp.
- **Vấn đề còn gặp:**
  - Cell 38 vẽ biểu đồ dùng `baseline_rewards` / `better_rewards`, nhưng hai biến chỉ được gán ở cell 39 → trong phiên mới gây `NameError`. **Cần chuyển cell 39 lên trước cell 38** và chạy lại.
  - Cell 36 lưu 10/100 lần thành công, cell 39 lưu 4/100 — hai mẫu ngẫu nhiên khác nhau; biểu đồ và kết luận cần chỉ rõ đang dùng mẫu nào.
  - `run_episode()` chỉ dừng theo `terminated`, chưa xử lý `truncated` theo API Gymnasium hiện tại.


## 5. Phân công

| Thành viên | Phần việc thực tế |


| Bùi Kiệt | Cài đặt model-based agent GridHunt đơn agent, thí nghiệm, kết luận |

| Phan Lê Ngọc Như Ý | Cài đặt greedy hunter, thí nghiệm đa agent |

| Phạm Thái Duy Khang | Agent cải tiến Lunar Lander, đánh giá 100 episode |

| Bùi Anh Đức | Môi trường, simple/model-based agent, nghiên cứu so sánh |



