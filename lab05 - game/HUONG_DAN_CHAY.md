# Hướng dẫn chạy – Lab 05: Tìm kiếm đối kháng và trò chơi

## 1. Các file trong thư mục

| Bài (theo đề) | File | Nội dung chính |
|---|---|---|
| Bài 1 | `tictactoe_definitions.ipynb` | Định nghĩa trò chơi Tic-Tac-Toe, Random vs. Random |
| Bài 2 | `tictactoe_and_or_tree_search.ipynb` | AND-OR Tree Search, kế hoạch có điều kiện |
| Bài 3 | `tictactoe_alpha_beta_tree_search.ipynb` | Minimax và cắt tỉa Alpha-Beta |
| Bài 4 | `tictactoe_heuristic_alpha_beta_tree_search.ipynb` | Alpha-Beta với heuristic và giới hạn độ sâu |
| Bài 5 | `tictactoe_pure_monte_carlo_search.ipynb` | Pure Monte Carlo Search |
| Bài 6 | `tictactoe_monte_carlo_tree_search_restricted.ipynb` | UCB1 / MCTS độ sâu 1 |
| Bài 7 | `tictactoe_interactive.ipynb` | Chơi Tic-Tac-Toe tương tác |
| Bài 8 | `assignment_connect4.ipynb` | Connect 4 |
| Bài 9 | `assignment_mean_connect4.ipynb` | "Mean" Connect 4 |
| Bài 10 | `assignment_dots_and_boxes.ipynb` | Dots and Boxes |
| Mục 4 – 5 | `tictactoe_tong_hop.ipynb` | Bảng tổng hợp, 6 câu hỏi thảo luận, nhận xét chung |

Các file của giảng viên được giữ nguyên: `tictactoe.py`, `profiling_code.ipynb`, `store_agent_state_information.ipynb`, `README.md`.
Trong các notebook, mọi nội dung gốc của giảng viên (lời dẫn, yêu cầu, mã) vẫn còn nguyên; phần nhóm làm thêm là các ô có tag `lab05_added`
(bật **View → Cell Toolbar → Tags** để xem), thường bắt đầu bằng "Nhận xét" hoặc có tiêu đề "Lab 05 – …".

## 2. Môi trường

* Python 3.9 trở lên (đã kiểm tra cú pháp với 3.9 và 3.11, chạy lại toàn bộ bằng 3.13).
* Thư viện: `numpy`, `matplotlib`, `pandas`, cùng `jupyterlab` hoặc `notebook`:

```
pip install numpy matplotlib pandas jupyterlab
```

* Không cần Internet. File `tictactoe.py` phải nằm **cùng thư mục** với các notebook.

## 3. Cách chạy

1. Mở thư mục bằng Jupyter (`jupyter lab`), mở từng notebook và chọn **Kernel → Restart Kernel and Run All Cells**.
2. Hoặc chạy bằng dòng lệnh (kết quả ghi đè lên chính notebook):

```
jupyter nbconvert --to notebook --execute --inplace assignment_connect4.ipynb
```

3. Trên Google Colab: tải tất cả file lên cùng một thư mục (ví dụ trong Google Drive) rồi chạy như thường.

Các notebook đã được chạy sẵn và lưu kết quả đầu ra; chỉ cần chạy lại khi muốn kiểm tra hoặc thay đổi tham số.
Thứ tự không quan trọng, mỗi notebook độc lập (notebook tổng hợp tự nhúng mã các tác tử cần dùng).

## 4. Thời gian chạy tham khảo (máy 2 nhân, đo khi chạy lại toàn bộ)

| Notebook | Thời gian |
|---|---|
| `tictactoe_definitions`, `tictactoe_interactive` (phần tự động) | vài giây |
| `tictactoe_and_or_tree_search` | khoảng 15 giây |
| `tictactoe_heuristic_alpha_beta_tree_search` | khoảng 25 giây |
| `tictactoe_alpha_beta_tree_search` | khoảng 1,5 phút |
| `tictactoe_tong_hop` | khoảng 1,5 phút |
| `tictactoe_pure_monte_carlo_search`, `tictactoe_monte_carlo_tree_search_restricted` | khoảng 3,5 – 4 phút mỗi notebook |
| `assignment_dots_and_boxes` | khoảng 7,5 phút |
| `assignment_mean_connect4` | khoảng 8,5 phút |
| `assignment_connect4` | khoảng 22 phút |

Thời gian phụ thuộc cấu hình máy; số nút duyệt và tỉ lệ thắng/hòa/thua mới là thước đo ổn định để so sánh.

## 5. Tái lập kết quả

* Các thí nghiệm có yếu tố ngẫu nhiên đều đặt seed cố định (thường là `np.random.seed(2026)`), nên chạy lại cho cùng kết quả.
  Các ô gốc của giảng viên không đặt seed nên số liệu ở những ô đó có thể lệch nhẹ giữa các lần chạy.
* Mỗi cặp tác tử đấu ít nhất 100 ván (Random vs. Random dùng 1.000 ván vì rất nhẹ).

## 6. Những điểm cần lưu ý

* **Bài 7 (chơi tương tác):** hàm `interactive_player` và hai ô gốc của giảng viên (`play(interactive_player, random_player, …)` và
  `play(random_player, interactive_player, …)`) được giữ nguyên; hai ô này gọi `input()` nên cần người ngồi nhập nước đi trong JupyterLab
  (kết quả hiển thị sẵn ở đó là của lần chơi gốc). Phần **Bài 7** ở cuối notebook chạy hoàn toàn tự động: các nước đi của "người chơi"
  (cẩn thận / bất cẩn) được nạp sẵn cho `input()` để ghi lại ván đấu với Alpha-Beta và Pure Monte Carlo Search. Vì vậy với notebook này,
  *Run All* sẽ dừng ở hai ô gốc chờ nhập tay; hãy nhập nước đi (hoặc chạy từng ô, bỏ qua hai ô đó).
* **Mean Connect 4:** các quy ước về luật chuyển quân (quân được chuyển giữ màu đối thủ, hòa khi cả hai cùng có 4 quân,
  hòa khi lặp thế 3 lần hoặc quá số nửa-nước tối đa) được ghi ở đầu notebook; quy ước khác sẽ cho kết quả khác.
* **Dots and Boxes:** kích thước bàn tính theo *số chấm* (5 × 5 chấm = 4 × 4 ô); bộ giải chính xác chỉ dùng cho bàn nhỏ,
  bàn lớn dùng cắt độ sâu với heuristic và Monte Carlo.
* **Connect 4:** ô đầu của `assignment_connect4.ipynb` có ba dòng khai báo cá nhân (`[Add your name]`, `[list tools]`, `[your initials]`)
  do giảng viên đặt sẵn; nhóm cần tự điền trước khi nộp.
* Mọi số liệu trong báo cáo Word (Chương 1) lấy từ kết quả đã chạy của các notebook trong thư mục này.
