# 2.1–2.2. Tác tử trò chơi và tìm kiếm đối kháng

## 2.1. Tác tử trong trò chơi Connect Four

Một tác tử trò chơi nhận trạng thái hiện tại và chọn một hành động hợp lệ.
Trong Connect Four, hành động là cột thả quân; engine chịu trách nhiệm áp dụng
trọng lực, chuyển lượt và xác định thắng, thua hoặc hòa. Tách quyết định của
tác tử khỏi luật chơi cho phép các phương pháp dùng chung môi trường và được
so sánh trên cùng một cơ chế chuyển trạng thái.

Connect Four chuẩn dùng bàn cờ 6 hàng × 7 cột, có hai người chơi luân phiên.
Đây là môi trường tất định, có thông tin đầy đủ và đối kháng tổng bằng không:
mỗi bên nhìn thấy toàn bộ bàn cờ; một nước đi hợp lệ xác định duy nhất trạng
thái tiếp theo; lợi ích thắng của một bên tương ứng với thất bại của bên kia.
Ngẫu nhiên trong Random hoặc MCTS thuộc phương pháp ra quyết định, không
phải yếu tố ngẫu nhiên của luật chơi.

Có thể mô hình hóa trò chơi bằng các thành phần sau:

| Ký hiệu | Ý nghĩa trong Connect Four |
| --- | --- |
| $s=(B,p)$ | Bàn cờ $B$ và người chơi $p$ đến lượt |
| $A(s)$ | Các cột chưa đầy nếu ván chưa kết thúc; tập rỗng khi ván đã kết thúc |
| $T(s,a)$ | Thả quân vào ô trống thấp nhất của cột $a$, cập nhật kết quả và lượt |
| $\mathrm{terminal}(s)$ | Có bốn quân liên tiếp cùng bên hoặc bàn đầy |
| $U(s,p)$ | Kết quả cuối ván từ góc nhìn $p$: thắng $+1$, hòa $0$, thua $-1$ |
| $\pi(s)$ | Quy tắc hoặc phân phối chọn hành động hợp lệ |

Trên bàn 7 cột, số hành động tại một trạng thái không vượt quá 7. Một ván
có tối đa 42 nước, nhưng thường kết thúc sớm khi xuất hiện bốn quân liên
tiếp. Duyệt mọi diễn biến đến cuối ván có chi phí lớn, nên tác tử thực tế
phải giới hạn độ sâu hoặc ngân sách mô phỏng/thời gian.

Bốn cấp đầu trong đề tài thể hiện các cách sử dụng thông tin khác nhau.
Random chọn đều trong các cột hợp lệ. Heuristic sử dụng luật chiến thuật
và điểm thế cờ. Alpha-Beta tìm trước các phản ứng đối thủ trong một cây có
giới hạn độ sâu. MCTS phân bổ ngân sách cho các nhánh bằng kết quả mô phỏng.
Các cấp này không cần tập dữ liệu huấn luyện hay checkpoint; thông tin của
chúng đến từ trạng thái, luật chơi, trọng số thủ công và các trạng thái
tự tạo trong lúc tìm kiếm. Số thứ tự cấp biểu thị phương pháp triển khai,
không phải bằng chứng rằng cấp sau luôn thắng cấp trước.

## 2.2. Minimax, Alpha-Beta và MCTS/UCT

### 2.2.1. Nguyên lý Minimax

Minimax giả định mỗi bên chọn nước tốt nhất cho mình trong cây trò chơi.
Giữ cố định người chơi ở gốc là $p$: nút đến lượt $p$ lấy giá trị lớn
nhất, còn nút đến lượt đối thủ lấy giá trị nhỏ nhất. Theo Russell và Norvig,
*Artificial Intelligence: A Modern Approach*, ấn bản 4, mục 6.2, đây là cách
suy ngược giá trị từ trạng thái kết thúc về quyết định ở gốc.

Với $d$ là số nước còn được phép tìm trước và $E(s,p)$ là hàm lượng giá,
phiên bản giới hạn độ sâu được viết như sau:

$$
V(s,d;p)=
\begin{cases}
U(s,p), & s\text{ kết thúc},\\
E(s,p), & d=0,\\
\max_{a\in A(s)}V(T(s,a),d-1;p), & \text{đến lượt }p,\\
\min_{a\in A(s)}V(T(s,a),d-1;p), & \text{đến lượt đối thủ}.
\end{cases}
$$

Giá trị ở trạng thái kết thúc và điểm lượng giá phải dùng thang điểm nhất
quán. Trong cài đặt của đề tài, kết quả cuối ván được nhân với trọng số
`win = 10000`; chi tiết hàm điểm nằm ở mục 3.3.2.

Ở gốc, tác tử chọn hành động có giá trị lớn nhất. Ví dụ minh họa, nếu hai
nước A và B dẫn đến các phản ứng đối thủ có điểm lần lượt là $[3,5]$ và
$[2,9]$, đối thủ lấy các điểm nhỏ nhất là 3 và 2; tác tử chọn A. Đây là
ví dụ tính toán, không phải kết quả thi đấu của dự án.

Với hệ số phân nhánh $b$ và độ sâu $d$, số nút của Minimax có cấp độ
$O(b^d)$. Giới hạn độ sâu làm giảm chi phí nhưng khiến quyết định phụ
thuộc hàm lượng giá và có thể bỏ sót đe dọa ngoài chân trời tìm kiếm
(Russell và Norvig, mục 6.3). Vì vậy, tìm kiếm đúng ở độ sâu đã chọn không
đồng nghĩa với giải tối ưu toàn bộ Connect Four.

### 2.2.2. Negamax và góc nhìn lượng giá

Trong trò chơi hai bên tổng bằng không, Negamax viết hai bước max/min bằng
một bước cực đại và phép đổi dấu. Với quy ước điểm theo bên đến lượt và hàm
điểm đối xứng dấu, công thức có dạng:

$$
N(s,d)=\max_{a\in A(s)}[-N(T(s,a),d-1)].
$$

Điều kiện về góc nhìn cần được giữ nhất quán ở cả nút trong và nút lá.
Hàm điểm của dự án có trọng số tấn công và phòng thủ khác nhau, nên không
bảo đảm $E(s,1)=-E(s,2)$. Cài đặt Alpha-Beta vì thế giữ cố định người
chơi ở gốc $p$ và dùng biến `color`: lá trả về
`color * score(s, p)`; mỗi lần xuống con đổi `color` thành `-color` và
đổi dấu kết quả khi quay lên. Nhờ đó, biểu thức Negamax vẫn biểu diễn
Minimax max/min với cùng một hàm điểm từ góc nhìn gốc.

### 2.2.3. Cắt tỉa Alpha-Beta và sắp xếp nước đi

Alpha-Beta duy trì hai cận: $\alpha$ là cận dưới của giá trị tốt nhất mà
phía tối đa hóa đã biết, $\beta$ là cận trên do phía tối thiểu hóa đặt
ra. Khi $\alpha\ge\beta$, phần còn lại của nhánh không thể cải thiện
quyết định của tổ tiên và được bỏ qua. Trong Negamax, lời gọi xuống con
đổi cửa sổ $(\alpha,\beta)$ thành $(-\beta,-\alpha)$.

Trong ví dụ ở mục 2.2.1, sau khi A cho giá trị 3, nếu phản ứng đầu tiên
dưới B cho điểm 2 thì không cần xét phản ứng còn lại: B có giá trị không
lớn hơn 2, không thể tốt hơn A. Cắt tỉa đúng giữ nguyên giá trị Minimax
ở cùng độ sâu và cùng hàm lượng giá; nó giảm việc duyệt cây chứ không
sửa tiêu chuẩn đánh giá.

Hiệu quả phụ thuộc thứ tự duyệt. Trường hợp xấu vẫn có chi phí
$O(b^d)$; với thứ tự lý tưởng, số nút có thể giảm về cấp độ
$O(b^{d/2})$ (Russell và Norvig, mục 6.2.3–6.2.4). Dự án ưu tiên
cột giữa theo thứ tự `(3, 2, 4, 1, 5, 0, 6)`. Đây là lựa chọn triển khai
cần được đo bằng ablation, không phải bảo đảm giảm nút trên mọi bàn cờ.
Nếu nhiều nước bằng điểm, thay thứ tự có thể làm đổi cột được chọn trong
khi giá trị tối ưu không đổi.

Với ngân sách thời gian, tìm sâu dần (*iterative deepening*) lần lượt hoàn
tất độ sâu 1, 2, 3, … và giữ kết quả của vòng hoàn tất gần nhất. Nếu hết giờ
giữa một vòng, kết quả chưa hoàn chỉnh không thay thế kết quả trước đó.

### 2.2.4. Monte Carlo Tree Search và UCT

MCTS xây dựng cây từng phần bằng các mô phỏng đến cuối ván. Theo Russell
và Norvig, mục 6.4, mỗi vòng gồm bốn bước:

1. **Selection:** từ gốc, đi theo chính sách chọn nút cho đến nơi có thể mở rộng.
2. **Expansion:** thêm một hành động chưa thử vào cây.
3. **Simulation:** mô phỏng từ trạng thái đó đến kết thúc bằng chính sách rollout.
4. **Backpropagation:** cập nhật số lần thăm và tổng kết quả trên đường về gốc.

UCT cân bằng khai thác nhánh có điểm tốt và khám phá nhánh còn ít được thử.
Với nút con $v$, nút cha $u$, công thức sử dụng trong đề tài là:

$$
\operatorname{UCT}(v)=\frac{W(v)}{N(v)}
+c\sqrt{\frac{\ln N(u)}{N(v)}}.
$$

$N(v)$ là số mô phỏng hoàn tất đi qua nút, $W(v)$ là tổng kết quả
có dấu và $c\ge0$ điều chỉnh mức khám phá. Thành phần thứ nhất là
điểm trung bình; thành phần thứ hai ưu tiên nút ít được thăm. Nút chưa
được thăm phải được mở rộng và mô phỏng trước khi áp dụng phép chia này.

Dự án dùng kết quả $+1/0/-1$ và lưu $W(v)$ theo **người vừa đi vào
nút**. Khi quay về cha, góc nhìn đổi dấu. Vì vậy, tại cả tầng của mình
lẫn tầng đối thủ, chọn con có UCT lớn nhất là chọn lợi ích của bên đang
ra quyết định. Dùng duy nhất điểm của người ở gốc rồi lấy max ở mọi tầng
sẽ sai vì coi đối thủ cũng đang giúp người ở gốc.

Tên trường `wins` trong mã là tổng kết quả có dấu, không phải số ván
thắng. Do có thua và hòa, `wins / visits` thuộc $[-1,1]$, không trực
tiếp là xác suất thắng. Sau khi hết ngân sách, tác tử chọn con có
**số lần thăm lớn nhất**. UCT phục vụ phân bổ mô phỏng khi tìm kiếm,
không phải tiêu chí chọn nước cuối cùng.

Rollout của đề tài chọn ngẫu nhiên đều trong các hành động hợp lệ, không
dùng mạng nơ-ron hoặc Heuristic. Với ngân sách hữu hạn, kết quả mô phỏng
có thể nhiễu và bỏ sót phản ứng chiến thuật hiếm. Tăng mô phỏng làm thay
đổi lượng thông tin thu thập, nhưng không bảo đảm thắng nhiều hơn trong
từng ván cụ thể hoặc vượt Alpha-Beta trên mọi cấu hình.

### 2.2.5. Cơ sở so sánh các phương pháp

| Phương pháp | Căn cứ ra quyết định | Giới hạn chính |
| --- | --- | --- |
| Random | Phân phối đều trên nước hợp lệ | Không phân tích chiến thuật |
| Heuristic | Thắng/chặn, an toàn một lượt và điểm thế cờ | Phụ thuộc luật và trọng số thủ công |
| Minimax/Alpha-Beta | Phản ứng đối kháng và lượng giá ở độ sâu giới hạn | Chi phí tăng theo độ sâu; sai số hàm điểm |
| MCTS/UCT | Thống kê mô phỏng và cân bằng khám phá–khai thác | Nhiễu mô phỏng; phụ thuộc ngân sách và rollout |

Một lần thăm nút Alpha-Beta, một nút MCTS được cấp phát và một rollout
không có cùng ý nghĩa hoặc chi phí. Khi so sánh sức mạnh, cần công bố
cấu hình mặc định và chế độ cùng ngân sách thời gian, đổi bên đi trước,
giữ khai cuộc/seed có thể tái lập và ghi thời gian thực tế. Các chỉ số
thi đấu và ablation thuộc Chương 4; phần lý thuyết này không suy ra
thứ hạng các tác tử.

### Tài liệu đối chiếu

- Stuart J. Russell và Peter Norvig, *Artificial Intelligence: A Modern
  Approach*, ấn bản 4, Global Edition, Pearson, 2022, Chương 6:
  mục 6.1–6.2, tr. 192–201; mục 6.3, tr. 202–206; mục 6.4, tr. 207–210.
- [Proposal của Nhóm 100](../proposal/ConnectFour_7x6_Proposal_Nhom100_HoanChinh.docx),
  mục 1.2–1.3, 3.1 và 5.3: luật chơi, nhóm tác tử cổ điển và thiết kế khảo sát.
- Chi tiết hiện thực và liên kết mã nguồn nằm trong [mục 3.3](03b_thuat_toan.md).
