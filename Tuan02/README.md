# Lab 02 — Search: Solving a Maze Using a Goal-based Agent


## 1. Nội dung được giao

Giải mê cung bằng các thuật toán tìm kiếm:

| Task | Nội dung |
|---|---|
| Task 1 | Định nghĩa bài toán: trạng thái, hành động, hàm chuyển trạng thái, goal, chi phí; ước lượng d, m, b |
| Task 2 | Cài đặt BFS và DFS; chạy trên 4 maze mẫu; hiển thị đường đi và bảng so sánh |
| Task 3 | Cài đặt Greedy BFS (GBFS) và A* với heuristic Manhattan distance; so sánh với Task 2 |
| Task 4 | So sánh 4 thuật toán trên 8 maze; hiển thị lời giải từng maze |
| Advanced | Iterative Deepening Search (IDS); Multiple Goals (DFS/BFS/IDS) |


## 2. Bài làm

| File | Loại | Mô tả | Trạng thái |
|---|---|---|---|
| [`Ex1_Maze_completed.ipynb`](Ex1_Maze_completed.ipynb) | Notebook | Cài đặt đầy đủ BFS, DFS, GBFS, A\*; bảng so sánh 8 maze; trực quan hóa lời giải; phần Advanced IDS & Multiple Goals | **Hoàn thành 100%** |
| [`Ex2_Maze_simplified.ipynb`](Ex2_Maze_simplified.ipynb) | Notebook | Phiên bản rút gọn — BFS, định nghĩa bài toán, ước lượng d,m,b, thực nghiệm 4 maze và thảo luận độ phức tạp | **Hoàn thành 100%** |
| [`Ex3_Show_all_mazes.ipynb`](Ex3_Show_all_mazes.ipynb) | Notebook | Hiển thị 8 maze mẫu bằng `maze_helper` | Đã có `maze_helper.py` và đầy đủ 8 file `.txt`, chạy thành công |
| [`lab02.docx`](lab02.docx) | Báo cáo | Báo cáo thực hành lab 02 | Đã có |


## 3. Cách chạy

### Môi trường
- **Python:** 3.12+ (kernel Python 3 / `.venv 3.12.3`)
- **Jupyter Notebook** hoặc **JupyterLab**

### Thư viện cần cài

```bash
pip install numpy matplotlib pandas
```

> Thư mục đã bao gồm đầy đủ module `maze_helper.py` và 8 file dữ liệu mê cung `.txt`:
> `small_maze.txt`, `medium_maze.txt`, `large_maze.txt`, `open_maze.txt`, `L_maze.txt`, `loops_maze.txt`, `empty_maze.txt`, `empty_maze_2.txt`.

### Các bước chạy

```bash
cd lab02_search_PhanLeNgocNhuY_3124720079
jupyter notebook
```

Thứ tự chạy đề xuất:
1. `Ex3_Show_all_mazes.ipynb` — xem trực quan 8 maze mẫu.
2. `Ex2_Maze_simplified.ipynb` — hoàn thành Task 1, Task 2 (BFS trên 4 maze), Task 3 (thảo luận độ phức tạp, so sánh A*).
3. `Ex1_Maze_completed.ipynb` — chạy toàn bộ 4 thuật toán (BFS, DFS, GBFS, A*) trên 8 maze, biểu đồ so sánh, hiển thị trực quan lời giải từng thuật toán, phần Advanced IDS trên toàn bộ maze và Multiple Goals trên Medium Maze.


## 4. Kết quả và nhận xét chi tiết

### Ex1 — Maze Completed (Hoàn thành đầy đủ)

- **Task 1:** Định nghĩa hình thức đầy đủ bài toán tìm đường (Initial state, Actions, Transition model, Goal test, Path cost) và ước lượng kích thước không gian tìm kiếm ($d, m, b$).
- **Task 2 — BFS/DFS:**
  - **BFS:** Tìm đường đi tối ưu với chi phí bước nhỏ nhất cho mọi mê cung.
  - **DFS:** Sử dụng cấu trúc ngăn xếp LIFO và kiểm tra chu trình trên nhánh hiện tại (`on_path`). 
  - **Bộ nhớ DFS:** Đã làm rõ sự khác biệt giữa bộ nhớ tìm kiếm hoạt động thực tế ($\mathcal{O}(bm)$ gồm stack và ancestors) và tập phụ trợ `expanded_states` chỉ dùng để vẽ hình hiển thị mà không can thiệp chặn nhánh duyệt.
  - **Trường hợp Open Maze:** DFS không có tập `visited` toàn cục duyệt qua không gian nhánh lũy thừa của các đường đi đơn, chạm ngưỡng 200.000 bước mà không tới đích; đã đánh dấu rõ `N/A*` cùng ghi chú giải thích chi tiết dưới bảng.
- **Task 3 — GBFS/A\*:** Cài đặt với heuristic Manhattan distance $h(n) = |r_n - r_g| + |c_n - c_g|$, chứng minh tính admissible và consistent trên lưới 4 hướng; so sánh sự đánh đổi giữa số nút mở rộng và tính tối ưu.
- **Task 4 — So sánh và Hiển thị Lời giải:**
  - Bảng Markdown đầy đủ 8 mê cung $\times$ 4 thuật toán với các chỉ số: path cost, nodes expanded, max tree depth, max memory, max frontier.
  - Biểu đồ trực quan hóa số lượng nút mở rộng và chi phí đường đi.
  - **Trực quan hóa lời giải:** Gọi hàm `display_solution()` hiển thị hình ảnh mê cung với các ô đã thăm (`.`) và đường đi cuối cùng (`P`), đồng thời in chuỗi hành động cụ thể cho từng thuật toán trên các mê cung đại diện.
- **Advanced Task — IDS:**
  - Đã thử nghiệm IDS trên toàn bộ 8 mê cung.
  - Phân tích chi tiết nguyên nhân IDS hoạt động tối ưu trên mê cung có tường/hành lang hẹp (`small_maze`: 19 bước, `medium_maze`: 68 bước), nhưng gặp bùng nổ tổ hợp trên không gian mở (`open_maze`, `empty_maze`) do lặp lại các đường đi đơn cùng tọa độ ở mỗi vòng lặp tăng độ sâu.
- **Advanced Task — Multiple Goals:**
  - Xây dựng 2 cấu hình mê cung nhiều đích dựa trên `medium_maze.txt` (thêm 1 và 2 đích phụ).
  - Khắc phục cơ chế đếm nút mở rộng của IDS để tích lũy chính xác qua tất cả các độ sâu $0 \dots d$.
  - Thực nghiệm chứng minh BFS và IDS luôn tìm được đích tối ưu gần nhất (chi phí 49 và 27), trong khi DFS đi sâu vào một nhánh và kết thúc ở đường vòng không tối ưu (chi phí 99).

### Ex2 — Maze Simplified (Hoàn thành đầy đủ)

| Task | Điểm | Trạng thái | Nội dung chi tiết |
|---|---|---|---|
| Task 1 — Định nghĩa bài toán & Kích thước | 2/2 | Hoàn thành | Định nghĩa toán học 5 thành phần tìm kiếm; phân tích chi tiết ý nghĩa và cách xác định $d$, $m$, $b$ |
| Task 2 — Cài đặt BFS & Trực quan | 5/5 | Hoàn thành | Cài đặt BFS chuẩn giáo trình với `frontier` FIFO và `reached` hash set; không sửa đổi bản đồ mê cung; chạy trên 4 mê cung (`small`, `large`, `open`, `empty`); điền bảng kết quả và xuất hình ảnh hiển thị đường đi `P` cùng các ô đã duyệt `.` |
| Task 3 — Thảo luận phân tích | 3/3 | Hoàn thành | Trả lời đầy đủ 3 câu hỏi: chứng minh tính đầy đủ và tối ưu, độ phức tạp thời gian/không gian của BFS; so sánh cải tiến của A* với heuristic Euclidean; phân tích nguyên nhân BFS quá tải bộ nhớ trên bài toán lớn và các thuật toán thay thế (IDS, IDA*, SMA*, A*) |

### Ex3 — Show All Mazes

- Đã bổ sung `maze_helper.py` và toàn bộ 8 file dữ liệu `.txt`.
- Chạy trơn tru và hiển thị đầy đủ hình ảnh 8 mê cung mẫu.


## 5. Phân công

| Thành viên | MSSV | Phần việc thực tế |


| Phan Lê Ngọc Như Ý | 3124720079 | Tổng hợp, hoàn thiện `Ex2_Maze_simplified.ipynb` (BFS, phân tích độ phức tạp, thực nghiệm 4 maze), báo cáo `lab02.docx` |

| Bùi Anh Đức | 3124720016 | Cài đặt và thực nghiệm 4 thuật toán trong `Ex1_Maze_completed.ipynb`, trực quan hóa lời giải, `Ex3_Show_all_mazes.ipynb` |

| Phạm Thái Duy Khang | 3124720033 | Cài đặt và phân tích DFS, Cycle Checking, Advanced IDS trên toàn bộ mê cung |

| Bùi Quyền Kiệt | 3124720036 | Cài đặt A*, thực nghiệm Multiple Goals trên Medium Maze và so sánh tính tối ưu |
