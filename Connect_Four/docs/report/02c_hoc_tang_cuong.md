# 2.4. Học tăng cường, DQN và self-play

Mục này trình bày nền tảng lý thuyết cho tác tử cấp 6 (DQN). Phần cài đặt cụ thể
nằm ở mục 3.5 (`03d_dqn_giai_dau.md`), kết quả huấn luyện ở mục 4.4
(`04c_dqn_duong_cong.md`), ablation A4 và thí nghiệm đối thủ huấn luyện A6 ở mục 4.5
(`04f_ablation_dqn.md`).

## 2.4.1. Học tăng cường và quá trình quyết định Markov

Học tăng cường (Reinforcement Learning, RL) nghiên cứu một tác tử học cách hành
động qua tương tác thử–sai với môi trường, chỉ dựa vào tín hiệu phần thưởng
thay vì nhãn đúng cho từng trạng thái (Sutton và Barto, 2018). Bài toán được mô
hình hóa thành quá trình quyết định Markov (MDP) gồm:

- tập trạng thái `S` — với Connect Four là cấu hình bàn 6×7 và người đến lượt;
- tập hành động `A(s)` — các cột chưa đầy (tối đa 7);
- hàm chuyển `P(s' | s, a)` — sau nước của tác tử, đối thủ đáp lại; nếu đối thủ
  có yếu tố ngẫu nhiên thì chuyển trạng thái cũng ngẫu nhiên theo góc nhìn tác tử;
- phần thưởng `r` — trong đồ án là +1 khi thắng, 0 khi hòa, −1 khi thua, các
  bước trung gian bằng 0 (phần thưởng thưa);
- hệ số chiết khấu `γ ∈ [0, 1]`.

Mục tiêu là tìm chính sách `π(a | s)` cực đại hóa tổng phần thưởng chiết khấu kỳ
vọng `G_t = Σ_k γ^k r_{t+k+1}`. Hàm giá trị hành động
`Q^π(s, a) = E_π[G_t | s_t = s, a_t = a]` cho biết một nước tốt đến đâu nếu sau đó
tiếp tục theo `π`. Hàm tối ưu `Q*` thỏa phương trình Bellman tối ưu:

```text
Q*(s, a) = E[ r + γ · max_{a' ∈ A(s')} Q*(s', a') | s, a ]
```

Khi đã biết `Q*`, chính sách tốt nhất chỉ là chọn `argmax_a Q*(s, a)` trên các
hành động hợp lệ.

## 2.4.2. Q-learning dạng bảng

Q-learning (Watkins và Dayan, 1992) ước lượng `Q*` trực tiếp từ kinh nghiệm,
không cần biết `P`. Sau mỗi bước `(s, a, r, s')`, giá trị được cập nhật theo sai
số chênh lệch thời gian (TD error):

```text
Q(s, a) ← Q(s, a) + α · [ r + γ · max_{a'} Q(s', a') − Q(s, a) ]
```

Đây là phương pháp *off-policy*: tác tử có thể hành động thăm dò (ví dụ chọn
ngẫu nhiên) nhưng vẫn học giá trị của chính sách tham lam. Sách của Mark Liu
(2025, chương 12) minh họa Q-learning dạng bảng trên các trò chơi nhỏ. Với
Connect Four, số trạng thái hợp lệ khoảng 4,5 × 10¹² nên bảng Q không khả thi; cần
hàm xấp xỉ có khả năng khái quát giữa các trạng thái giống nhau.

## 2.4.3. Deep Q-Network (DQN)

DQN (Mnih và cộng sự, 2015) thay bảng Q bằng mạng nơ-ron `Q(s, a; θ)` và tối ưu
`θ` bằng gradient trên sai số Bellman. Ghép trực tiếp Q-learning với mạng nơ-ron
thường không ổn định vì hai lý do; DQN đưa ra hai cơ chế tương ứng:

1. **Replay Buffer.** Các bước liền nhau trong một ván rất tương quan và phân
   phối dữ liệu thay đổi theo chính sách. DQN lưu transition
   `(s, a, r, s', done)` vào bộ nhớ và lấy mẫu ngẫu nhiên một batch để huấn luyện,
   nhờ đó phá tương quan giữa các mẫu liền nhau và dùng lại mỗi kinh nghiệm nhiều
   lần.
2. **Target Network.** Nếu mục tiêu `y = r + γ max Q(s', a'; θ)` dùng chính `θ`
   đang được cập nhật, mục tiêu "chạy theo" dự đoán và dễ phân kỳ. DQN giữ một bản
   sao `θ⁻` cố định, chỉ đồng bộ `θ⁻ ← θ` sau mỗi `C` bước; giữa hai lần đồng bộ,
   mục tiêu Bellman đứng yên.

Hàm mất mát là Huber (smooth L1) trên `y − Q(s, a; θ)`, ít nhạy với sai số lớn
hơn bình phương sai số. Thăm dò dùng **epsilon-greedy**: với xác suất `ε` chọn
một hành động hợp lệ ngẫu nhiên, ngược lại chọn `argmax Q`. `ε` giảm dần từ 1,0
để chuyển từ khám phá sang khai thác, nhưng giữ một sàn (0,05 trong đồ án) để
tác tử vẫn tiếp tục gặp trạng thái mới và Replay Buffer không chỉ chứa một kiểu
ván lặp lại.

Hai chi tiết riêng cho trò chơi đối kháng có luật về nước hợp lệ:

- **Mặt nạ hành động.** Cột đầy phải bị loại cả khi chọn nước lẫn khi tính
  `max_{a'} Q(s', a')` trong mục tiêu. Nếu chỉ che khi chọn nước, mục tiêu có thể
  lấy giá trị của một nước không bao giờ được đi, làm Q bị ước lượng sai.
- **Bàn kế là bàn sau khi đối thủ đáp lại.** Với đối thủ cố định, môi trường của
  DQN là "đi một nước, rồi đối thủ đi một nước". Trạng thái kế `s'` vì vậy là bàn
  ở lượt DQN tiếp theo; nếu lấy bàn ngay sau nước của DQN, `s'` là lượt của đối
  thủ và giá trị `max Q(s')` mang sai góc nhìn. Khi ván kết thúc, `y = r` và không
  bootstrap.

## 2.4.4. Self-play

Trong self-play, tác tử học bằng cách đấu với chính nó hoặc các phiên bản trước
của nó (Mark Liu, 2025, chương 13). Lợi ích là đối thủ mạnh dần cùng tác tử nên
tín hiệu học không bão hòa như khi đấu một đối thủ cố định. Nhược điểm là quá
trình không còn là một MDP dừng: môi trường thay đổi khi chính sách thay đổi, dễ
xuất hiện dao động hoặc "quên" cách thắng các lối chơi cũ, nên thường cần giữ
một tập đối thủ lịch sử. Mô hình chính của cấp 6 được huấn luyện với đối thủ cố định (Heuristic cấp 2)
để MDP dừng, dễ kiểm tra và dễ tái lập trong thời gian hai tuần. Self-play được
cài đặt sau đó như một thí nghiệm riêng (A6): đối thủ là một trong 5 bản sao đóng
băng gần nhất của chính mạng đang học, chép mới mỗi 500 episode (mục 3.5.4). Tập
đối thủ lịch sử này là cách giảm dao động và hiện tượng quên vừa nêu; kết quả so
sánh với đối thủ cố định ở mục 4.5.

## 2.4.5. AlphaGo-inspired và AlphaZero-inspired

Đề bài phân biệt cấp 7 (AlphaGo-inspired) và cấp 8 (AlphaZero-inspired). Hai hệ
thống gốc đều kết hợp mạng nơ-ron với MCTS nhưng khác ở nguồn tri thức:

| Tiêu chí | AlphaGo (Silver và cộng sự, 2016) | AlphaZero (Silver và cộng sự, 2018) |
| --- | --- | --- |
| Khởi đầu | Mạng chính sách học có giám sát từ ván của người chơi giỏi | Từ trọng số ngẫu nhiên, không dùng dữ liệu người |
| Học tăng cường | Policy gradient qua self-play để cải thiện mạng chính sách; mạng giá trị học từ ván self-play | Self-play hoàn toàn; MCTS sinh phân phối nước làm nhãn cho mạng |
| Mạng | Mạng chính sách và mạng giá trị tách riêng, cộng rollout nhanh | Một mạng hai đầu (policy và value), bỏ rollout |
| Tìm kiếm | MCTS dùng prior từ mạng chính sách, lá được đánh giá bằng trộn value và rollout | PUCT với prior từ policy head, lá đánh giá bằng value head |

Theo đó, một tác tử "AlphaGo-inspired" trong đồ án sẽ là MCTS dùng CNN cấp 5 (học
từ nhãn Alpha-Beta) làm prior; "AlphaZero-inspired" là vòng self-play mà MCTS tạo
nhãn cho chính mạng của nó. Kế hoạch nhóm không làm cấp 7–8 vì đó là điểm cộng và
đề ưu tiên chứng minh tác dụng của từng thành phần ở cấp 1–6.

DQN cấp 6 khác cả hai: không có tìm kiếm khi chơi, chính sách là `argmax Q` một
bước, và tín hiệu học chỉ đến từ phần thưởng cuối ván khi đấu đối thủ cố định. Vì
không nhìn trước, DQN được kỳ vọng yếu hơn Alpha-Beta và MCTS ở cùng thời gian
mỗi nước; câu hỏi thực nghiệm là nó học được bao nhiêu so với Random và Heuristic
(mục 4.4–4.5).

## Tài liệu tham khảo cho mục 2.4

- Liu, M. (2025). *AlphaGo Simplified*. Chương 12 (Q-learning dạng
  bảng), chương 13 (self-play deep RL), §16.1 và §19.1–19.2.
- Mnih, V., Kavukcuoglu, K., Silver, D., và cộng sự (2015). Human-level control
  through deep reinforcement learning. *Nature*, 518, 529–533.
- Silver, D., Huang, A., Maddison, C. J., và cộng sự (2016). Mastering the game
  of Go with deep neural networks and tree search. *Nature*, 529, 484–489.
- Silver, D., Hubert, T., Schrittwieser, J., và cộng sự (2018). A general
  reinforcement learning algorithm that masters chess, shogi, and Go through
  self-play. *Science*, 362, 1140–1144.
- Sutton, R. S., và Barto, A. G. (2018). *Reinforcement Learning: An
  Introduction* (2nd ed.). MIT Press. Chương 6 (TD learning, Q-learning).
- Watkins, C. J. C. H., và Dayan, P. (1992). Q-learning. *Machine Learning*, 8,
  279–292.
