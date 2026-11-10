# Trí tuệ nhân tạo nâng cao

Repo nhóm lưu trữ bài thực hành theo tuần và đồ án cuối kỳ **Connect Four AI** của học phần **Trí tuệ nhân tạo nâng cao**. Nội dung được tổ chức để giảng viên và các thành viên theo dõi bài làm, kết quả và lịch sử đóng góp trong cùng một repo.

**Đồ án cuối kỳ:** [Connect Four AI — phạm vi, phương pháp và thực nghiệm](Connect_Four/README.md).

## Mục lục

- [Thành viên](#thành-viên)
- [Nội dung học phần trong repo](#nội-dung-học-phần-trong-repo)
- [Cấu trúc repo](#cấu-trúc-repo)
- [Tổ chức bài làm theo tuần](#tổ-chức-bài-làm-theo-tuần)
- [Đồ án cuối kỳ Connect Four AI](#đồ-án-cuối-kỳ-connect-four-ai)
- [Công cụ sử dụng](#công-cụ-sử-dụng)
- [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)
- [Quy ước làm việc và commit](#quy-ước-làm-việc-và-commit)
- [Nguồn tham khảo](#nguồn-tham-khảo)

## Thành viên

| Thành viên | Mã sinh viên |
| --- | --- |
| Phan Lê Ngọc Như Ý | 3124720079 |
| Bùi Quyền Kiệt | 3124720036 |
| Phạm Thái Duy Khang | 3124720033 |
| Bùi Anh Đức | 3124720016 |

Phân công và đóng góp được ghi trong README của từng tuần hoặc từng phần công việc, kèm lịch sử commit và pull request tương ứng.

## Nội dung học phần trong repo

- **Bài thực hành:** mã nguồn hoặc notebook, kết quả chạy và nhận xét của từng lab.
- **Đồ án cuối kỳ:** engine Connect Four, các tác tử AI, giao diện, huấn luyện, thực nghiệm và tài liệu báo cáo.

Các chủ đề của các lab đã thực hiện:

| Lab | Chủ đề | Bài toán trong tài liệu thực hành |
| --- | --- | --- |
| Lab 01 | Intelligent Agents | Robot hút bụi, Lunar Lander và Gridhunt. |
| Lab 02 | Problem Solving by Search | Tìm đường trong mê cung; tìm kiếm và so sánh cách duyệt trạng thái. |
| Lab 03 | Local Search | Bài toán N-Queens và người du lịch (TSP). |
| Lab 04 | Constraint Satisfaction Problems | Tô màu đồ thị và bài toán thỏa mãn ràng buộc. |
| Lab 05 | Adversarial Search and Games | Tic-Tac-Toe (AND-OR, Alpha-Beta, heuristic, Monte Carlo, MCTS), Connect 4, "Mean" Connect 4 và Dots and Boxes. |

Bài làm, phạm vi đã thực hiện và kết quả của từng lab được ghi trong README của tuần tương ứng. Riêng Lab 05 nằm trong thư mục [`Tuan05/`](<Tuan05/README.md>), kèm [hướng dẫn chạy và tái lập kết quả](<Tuan05/HUONG_DAN_CHAY.md>).

## Cấu trúc repo

Quy ước tổ chức dùng chung cho cả nhóm; các thư mục tuần được bổ sung cùng bài làm thực tế.

```text
.
├── README.md                       # Giới thiệu và điều hướng toàn bộ repo
├── .gitignore                      # Quy tắc bỏ qua tệp dùng chung
├── Tuan01/
│   ├── README.md                   # Nội dung, phân công, cách chạy và nhận xét
│   └── LabXX/                      # Mã nguồn, notebook và kết quả của lab
├── Tuan02/
├── Tuan03/
├── Tuan04/
├── Tuan05/                   # Lab 05: Tìm kiếm đối kháng và trò chơi
│   ├── README.md                   # Danh mục notebook của giảng viên
│   ├── HUONG_DAN_CHAY.md           # Hướng dẫn chạy và tái lập kết quả
│   └── ...                         # Notebook bài tập và kết quả đã chạy
└── Connect_Four/
        ├── README.md               # Tài liệu riêng của đồ án cuối kỳ
        └── ...                     # Cấu trúc chi tiết trong README đồ án
```


## Tổ chức bài làm theo tuần

README của mỗi tuần ghi rõ:

1. **Nội dung được giao:** bài thực hành hoặc yêu cầu bổ sung của giảng viên.
2. **Bài làm:** đường dẫn đến mã nguồn, notebook và báo cáo thực hành trong thư mục tuần.
3. **Cách chạy:** môi trường, thư viện và các bước đã được nhóm kiểm tra.
4. **Kết quả và nhận xét:** đầu ra thực tế, giải thích kết quả và vấn đề còn gặp.
5. **Phân công:** phần việc thực tế của từng thành viên; dẫn tới commit hoặc pull request khi phù hợp.

Với notebook, lưu đầu ra cần thiết để đọc được kết quả. Các bảng, biểu đồ và kết luận phải có dữ liệu hoặc lần chạy tương ứng. Giữ lại thông tin tác giả và giấy phép của mã/tài liệu được cung cấp, đồng thời phân biệt phần tham khảo với phần nhóm tự thực hiện.

## Đồ án cuối kỳ Connect Four AI

**Đề tài:** Xây dựng và đánh giá Game AI đa cấp độ cho trò chơi Connect Four.

Xem [README Connect Four](Connect_Four/README.md) để biết phạm vi, phương pháp, cấu trúc dự án, hướng dẫn chạy và thiết kế thực nghiệm.

## Công cụ sử dụng

| Công cụ | Mục đích |
| --- | --- |
| Python, NumPy | Bài thực hành, xử lý dữ liệu và thuật toán AI. |
| Jupyter Notebook | Trình bày bài thực hành, kết quả và phân tích. |
| Pygame | Giao diện demo Connect Four. |
| PyTorch | Mạng học có giám sát và học tăng cường của đồ án. |
| pytest | Kiểm thử engine và hành động hợp lệ. |
| pandas, Matplotlib | Tổng hợp kết quả và vẽ biểu đồ. |
| Git, GitHub | Quản lý phiên bản, phối hợp và lưu lịch sử đóng góp. |
| Google Colab, tùy chọn | Chạy notebook và hỗ trợ huấn luyện khi cần thêm tài nguyên. |

Các thư viện chuyên biệt của từng lab được ghi trong tài liệu môi trường của lab đó. Máy cá nhân là môi trường chính cho phát triển, demo và đánh giá Connect Four; thông tin phần cứng và môi trường huấn luyện được công bố cùng thực nghiệm.



## Quy ước làm việc và commit

Mỗi thành viên dùng tài khoản GitHub riêng. Nội dung commit cần chỉ rõ **tuần / lab hoặc đồ án / công việc đã thực hiện**, theo yêu cầu của giảng viên:

```text
TuanXX/LabXX/Noi dung cong viec
TuanXX/DuAn/Noi dung cong viec
```

Ví dụ cách đặt thông điệp:

```text
Tuan01/Lab01/Bo sung bai Agent va ket qua chay
Tuan02/Lab02/Sua kiem tra trang thai lap khi tim duong
Tuan03/Lab03/Sua cach tinh so cap hau xung dot
Tuan04/DuAn/Cai dat kiem tra thang Connect Four
```

Thay số tuần và số lab theo công việc thực tế. Mỗi commit tập trung vào một thay đổi rõ ràng. Với bài được đưa lên bổ sung sau tuần học, ghi đúng tuần của bài và giữ thời gian commit thực tế; không suy diễn thời điểm làm bài chỉ từ thời điểm tải lên.

Với thay đổi cần phối hợp, nhóm sử dụng issue, nhánh công việc và pull request để trao đổi, kiểm tra trước khi gộp vào nhánh chính. Phân công trong README phản ánh đóng góp thực tế, kể cả phần đã làm trước khi đưa lên GitHub.

## Nguồn tham khảo

- Đề bài, bài giảng và tài liệu thực hành do giảng viên cung cấp.
- Tác giả, nguồn mã và giấy phép được ghi tại từng bài thực hành.
- Sách và tài liệu nghiên cứu cho đồ án được liệt kê trong [tài liệu tham khảo Connect Four](Connect_Four/README.md#tài-liệu-tham-khảo).

Nhóm chịu trách nhiệm hiểu, kiểm tra và giải thích bài làm. Khi sử dụng mã, tài liệu hoặc công cụ AI để hỗ trợ, ghi nhận nguồn theo yêu cầu học phần và trình bày rõ phần nhóm tự thực hiện.
