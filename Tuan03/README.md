# Lab 03 — Local Search


## 1. Nội dung được giao

| Bài tập | Mô tả ngắn |
|---|---|
| N-Queens | Giải bài toán n-Queens bằng Hill Climbing (steepest, stochastic, first-choice), random restart, Simulated Annealing; so sánh hiệu suất theo n |
| Traveling Salesman Problem (TSP) | Cài đặt 5 thuật toán local search (steepest HC, random restart, stochastic HC, first-choice HC, SA); so sánh chất lượng tour và thời gian chạy theo n |


## 2. Bài làm

| File | Loại | Mô tả | Trạng thái |
|---|---|---|---|
| [`n_queens.ipynb`](n_queens.ipynb) | Notebook | Hill Climbing, SA, so sánh theo n; Advanced (toán tử mở rộng) | Đủ task; chạy lại thành công |
| [`traveling_salesman_problem.ipynb`](traveling_salesman_problem.ipynb) | Notebook | 5 thuật toán HC+SA cho TSP; scalability n=10,15,20,30; bonus Genetic Algorithm | Đủ task; chạy lại thành công |
| [`lab03.docx`](lab03.docx) | Báo cáo | Báo cáo thực hành lab 03 | Đã có |


## 3. Cách chạy

### Môi trường

| Notebook | Python | Kernel |
|---|---|---|
| `n_queens.ipynb` | 3.14.6 | Python 3 |
| `traveling_salesman_problem.ipynb` | 3.13.5 | CS7320-AI |

> Khuyến nghị dùng **Python 3.10+** với Anaconda hoặc virtualenv.

### Thư viện cần cài

```bash
pip install numpy pandas matplotlib scipy
```

### Các bước chạy

```bash
cd lab03_localsearch_search_PhanLeNgocNhuY_3124720079
jupyter notebook
```

- Mở từng file `.ipynb` và chạy tất cả cell **từ đầu đến cuối** (Kernel → Restart & Run All).
- Không cần file dữ liệu ngoài; maze/dữ liệu đầu vào được sinh ngẫu nhiên trong notebook.

> **Đã kiểm tra:** Cả hai notebook chạy lại thành công toàn bộ cell trong môi trường Anaconda Python (Matplotlib Agg, không cần GUI).


## 4. Kết quả và nhận xét

### N-Queens (`n_queens.ipynb`)

| Task | Nội dung | Cell | Kết quả |
|---|---|---|---|
| Task 1 | Steepest hill climbing — duyệt đầy đủ láng giềng | 16 | Chạy đúng; hội tụ nhanh với n nhỏ |
| Task 2 | Stochastic hill climbing — chọn ngẫu nhiên trong tập cải thiện | 19 | Giảm thời gian mỗi bước |
| Task 3 | First-choice HC — ngưỡng dừng theo n, xác suất phủ lân cận | 22–23 | Phù hợp n lớn |
| Task 4 | Random restart cho cả 3 HC | 25–26 | Tăng tỷ lệ thành công |
| Task 5 | Simulated Annealing — 3 lịch nhiệt, biểu đồ 30 bàn cờ | 28–29 | SA vượt HC ở n lớn |
| Task 6 | 100 lần/thuật toán, n=4,8; hội tụ; log-log n=4,8,12,16,20 | 30–38 | Bảng đầy đủ; ước lượng số mũ và thảo luận |
| Advanced | 4 toán tử, 100 lần tại n=8,12; 3 loại biểu đồ | 39–41 | Có nhận xét so sánh |


### TSP (`traveling_salesman_problem.ipynb`)

| Thuật toán | Cell | Kết quả nổi bật |
|---|---|---|
| Steepest HC | 10 | Ổn định, hội tụ sớm |
| Random restarts HC | 13 | Cải thiện chất lượng tour |
| Stochastic HC | 16 | Nhanh hơn steepest mỗi bước |
| First-choice HC | 19 | Phù hợp n lớn |
| Simulated Annealing | 22 | Tour tốt nhất trong hầu hết cấu hình |
| So sánh tổng thể | 26 | n=10,15,20,30; 5 lần/cấu hình; bảng + hình tour trước/sau + biểu đồ |
| Genetic Algorithm (bonus) | 29–31 | Crossover, mutation, selection, elitism |


## 5. Phân công

| Thành viên | Phần việc thực tế |


| Phạm Thái Duy Khang, Bùi Anh Đức | Cài đặt 3 biến thể HC, SA, random restart; Task 6 so sánh; Advanced 4 toán tử |

| Bùi Quyền Kiệt, Phan Lê Ngọc Như Ý | Cài đặt 5 thuật toán TSP, so sánh scalability, phân tích, bonus GA |


