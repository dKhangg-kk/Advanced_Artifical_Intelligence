# 4.7. Thảo luận: nguyên nhân, hạn chế và lợi thế đi trước

> Mục này diễn giải các số ở mục 4.1–4.5; mọi số có dòng trong
> `results/tables/report_numbers.csv` (mục `4.2`–`4.7`). Những câu về nguyên nhân là
> **giải thích có kiểm chứng một phần** (nêu rõ phép kiểm chứng) hoặc **giả thuyết**
> (ghi rõ). Chỉ áp dụng cho cấu hình, seed và máy đã ghi ở 4.1.

## 4.7.1. Thứ hạng và vì sao Alpha-Beta, MCTS đứng đầu

- Hai tác tử tìm kiếm có score chung cao nhất: MCTS 0,817 và Alpha-Beta 0,793 (mặc định), 0,871 và 0,794 (cùng thời gian 0,2 giây/nước). Trực tiếp với nhau, Alpha-Beta đạt 0,488 (khoảng 0,419–0,556) ở chế độ mặc định, tức chưa phân biệt được; ở 0,2 giây/nước còn 0,390 (0,300–0,488) trên 100 ván.
- Cả hai đều dùng nhiều tính toán hơn hẳn: ở chế độ mặc định Alpha-Beta khoảng 38 ms/nước và MCTS khoảng 21 ms/nước, trong khi CNN, DQN và Heuristic dưới 1 ms/nước (mục 4.3). Giải đấu không kiểm soát số phép tính, nên không kết luận “thuật toán nào hiệu quả hơn trên mỗi phép tính”; chế độ cùng thời gian chỉ kiểm soát thời gian treo tường.
- Hướng của kết quả khớp với ablation: MCTS tăng score khi tăng mô phỏng (A2: 0,135 → 0,740 khi 100 → 5.000 mô phỏng trước Alpha-Beta sâu 4), và Alpha-Beta sâu 5 gặp Heuristic ổn định quanh 0,81 (A5). Thứ tự sát nhau giữa MCTS và Alpha-Beta sâu 5 cũng khớp với A2, nơi MCTS 1.000 mô phỏng thắng Alpha-Beta sâu 4 với score 0,595.
- Ở chế độ cùng thời gian, MCTS dùng khoảng 16.000 mô phỏng/nước, nhiều hơn 16 lần mức 1.000 của chế độ mặc định, còn Alpha-Beta duyệt khoảng 8.800 nút so với 1.500 nút. Việc MCTS hưởng lợi nhiều hơn là **giả thuyết phù hợp với A2**, nhưng giải đấu không có thí nghiệm riêng tách yếu tố này.

## 4.7.2. Điểm yếu chiến thuật của Alpha-Beta trong giải đấu

Trên bộ 31 thế kiểm thử (mục 4.3b), Alpha-Beta độ sâu 5 chọn đúng nước thắng ngay ở 13/18 thế, còn MCTS ở 18/18. Kiểm tra `scripts/check_alphabeta_win_values.py` cho thấy ở 3 trong 5 thế sai, một nước không thắng ngay được chấm điểm cao hơn nước thắng ngay. Điều này nghĩa là hàm giá trị gốc của Alpha-Beta trong cấu hình mặc định không đảm bảo ưu tiên thắng ngay. **Chúng tôi chưa tìm ra nguyên nhân trong mã** (mã Alpha-Beta thuộc phần của Khang và không được sửa trong đợt này); đây là điểm cần Khang xem lại. Hệ quả cho kết quả: MCTS không có điểm yếu này nên có thể đã được lợi ở các ván có đòn thắng sớm; chưa có thí nghiệm tách riêng yếu tố này nên chỉ là giả thuyết.

## 4.7.3. DQN: vì sao yếu hơn Heuristic dù học được thứ gì đó

Kết quả: DQN thắng Random nhưng thua Heuristic nặng (Heuristic đạt 0,912 mặc định và 0,880 cùng thời gian) và thua cả CNN, Alpha-Beta, MCTS. Các bằng chứng:

1. **Quá khớp đường chơi cố định (có kiểm chứng).** Huấn luyện gặp Heuristic xác định từ bàn trống, nên các ván huấn luyện gần như lặp lại. Cùng checkpoint, từ bàn trống DQN đạt score 1,000 nhưng chỉ có 5 chuỗi nước đi khác nhau trong 100 ván; với 2 và 4 nước khai cuộc ngẫu nhiên score giảm xuống 0,369 và 0,180 (4.4, `dqn_opening_diagnostic.csv`). Giải đấu và validation dùng 4 nước ngẫu nhiên nên đo đúng điều kiện khó.
2. **Chưa học chiến thuật cơ bản (có kiểm chứng).** Trên 31 thế kiểm thử DQN thắng ngay đúng ở 0,22 (thấp hơn cả Random, 0,24) và chặn đúng ở 0,67 (CNN và Heuristic 0,83; Alpha-Beta và MCTS ≥ 0,98).
3. **Hướng khắc phục (một seed, chưa kết luận).** Ô mở rộng huấn luyện với 4 nước khai cuộc ngẫu nhiên đạt 0,425 trước Heuristic so với 0,120 của ô A4 gốc cùng seed (4.5). Cải thiện là rõ so với cùng seed nhưng chỉ một seed và không dùng để chọn checkpoint giải đấu.
4. **Mức decay không phải nguyên nhân chính (có kiểm chứng ở mức A4).** Ba mức decay cho score 0,137 / 0,162 / 0,148 trước Heuristic, chênh lệch nằm trong dao động giữa seed.
5. **Đổi đối thủ huấn luyện sang tự chơi hoặc Random không cứu được (có kiểm chứng, A6, 3 seed).** Cùng siêu tham số, mô hình tự chơi đạt 0,003 gặp Heuristic và 0,568 [0,512; 0,623] gặp Random, thua cả `final.pt` khi đấu trực tiếp (0,418 [0,363; 0,475]); mô hình gặp Random đạt 0,010 và 0,578. Heuristic vẫn là đối thủ huấn luyện tốt nhất trong ba lựa chọn (mục 4.5, A6). Như vậy điểm yếu của DQN không đến từ việc chọn sai đối thủ cố định: với 10.000 episode và phần thưởng chỉ ở cuối ván, cả ba cách huấn luyện đều chưa học được chiến thuật tốt.

Chưa kiểm tra: học mỗi 4 bước, kích thước mạng, số episode lớn hơn nhiều, lưu transition của cả hai bên khi tự chơi, trộn tự chơi với Heuristic hay thưởng định hình. Đây là giả thuyết cho giai đoạn sau, không phải kết luận.

Về CNN: CNN đạt 0,546, gần Heuristic nhưng kém nhẹ: Heuristic thắng CNN với score 0,595 [0,526; 0,661] ở chế độ mặc định (khoảng không chứa 0,5) và 0,575 [0,477; 0,667] ở chế độ cùng thời gian (có chứa 0,5). CNN học có giám sát từ nhãn của Alpha-Beta (mục 3.4), còn DQN học từ phần thưởng cuối ván; chênh lệch hiệu năng giữa hai tác tử (CNN thắng DQN với score 0,895 và 0,875) **không tách riêng được** vì khác cả phương pháp, dữ liệu lẫn ngân sách huấn luyện.

## 4.7.4. Lợi thế đi trước

Toàn giải, bên đi trước đạt score 0,522 [0,504; 0,540] trên 3.000 ván (mặc định) và 0,514 [0,488; 0,539] trên 1.500 ván (cùng thời gian). Khoảng của chế độ mặc định không chứa 0,5, của chế độ cùng thời gian thì có. Cần đọc cẩn thận:

- Các cặp có Random hoặc chênh lệch sức mạnh rất lớn gần như luôn có kết quả không phụ thuộc bên đi trước (score bên đi trước ≈ 0,5), nên làm **loãng** hiệu ứng khi gộp toàn giải.
- Ở các cặp mạnh–mạnh, hiệu ứng đi trước rõ hơn: Alpha-Beta–MCTS 0,592 [0,523; 0,658] và Heuristic–MCTS 0,588 [0,518; 0,653] ở chế độ mặc định. Ở cùng thời gian các khoảng rộng hơn (100 ván/cặp) và đều chứa 0,5, nên không kết luận từng cặp.
- Khai cuộc ngẫu nhiên 4 nước làm lệch ván khỏi thế thuần Connect Four từ bàn trống, nơi bên đi trước thắng về mặt lý thuyết; số đo ở đây là lợi thế trong điều kiện thi đấu của đồ án, không phải ước lượng lợi thế lý thuyết.
- Khoảng Wilson tính theo ván, các ván chung khai cuộc không hoàn toàn độc lập (mục Giới hạn bên dưới), nên khoảng thật có thể rộng hơn.

## 4.7.5. Hạn chế

- Một bộ seed cho mỗi chế độ giải đấu; chế độ cùng thời gian chỉ 100 ván/cặp nên khoảng tin cậy rộng.
- Chế độ cùng thời gian chạy trên máy 2 nhân CPU, một tiến trình mỗi tác tử; độ trễ và số nút phụ thuộc máy và có thể khác trên máy khác. Ablation A1/A2/A5 do Khang chạy trên máy ARM khác (4.5), nên **không so sánh độ trễ tuyệt đối giữa hai nhóm số liệu**.
- Checkpoint DQN được đóng băng ngày 18/11, muộn hơn kế hoạch 17/11; quy tắc chọn đã được đăng ký trước khi chạy giải và không điều chỉnh sau khi xem kết quả giải.
- Mọi cấu hình DQN chỉ chạy 10.000 episode. Thí nghiệm tự chơi (A6) chạy sau khi giải đấu đã xong, 3 seed, không đưa mô hình tự chơi vào giải đấu; kết luận về tự chơi chỉ áp dụng cho thiết kế tập 5 bản sao đã mô tả ở mục 3.5.4.
- Cấu hình Alpha-Beta (độ sâu 5) và MCTS (1.000 mô phỏng) là một điểm cấu hình; kết luận về thứ hạng không suy ra cho cấu hình khác.
- Khoảng tin cậy trong mục này là Wilson theo ván; A1/A2/A5 dùng bootstrap theo cặp khai cuộc (4.5). Hai phương pháp có giả định khác nhau nên không đặt cạnh nhau như cùng một thước đo.

## 4.7.6. Trả lời ngắn cho các câu hỏi nghiên cứu (chỉ phần có bằng chứng ở Chương 4)

- **RQ1** (tìm kiếm cùng chi phí): ở 0,2 giây/nước MCTS 0,871 và Alpha-Beta 0,794 score chung; trực tiếp Alpha-Beta thua MCTS (0,390). Chưa tách được ảnh hưởng của hiệu quả cài đặt và của thuật toán.
- **RQ3** (DQN tự học qua tương tác/tự chơi): DQN huấn luyện gặp Heuristic học được để thắng Random (score 0,658 trong giải mặc định) nhưng không vượt Heuristic; nguyên nhân chính được kiểm chứng là quá khớp đường chơi cố định của đối thủ huấn luyện. Tự chơi trong 10.000 episode học được rất ít (0,568 gặp Random, 0,003 gặp Heuristic, A6), nên câu trả lời cho phần "tự chơi" là **chưa, trong ngân sách đã thử**. Đối thủ huấn luyện ảnh hưởng mạnh: Heuristic > Random ≈ tự chơi; mức decay ảnh hưởng không phân biệt được với dao động giữa seed (A4).
- **RQ4** (CNN và DQN): CNN thắng DQN với score 0,895 (mặc định) và 0,875 (cùng thời gian); không tách được riêng nguyên nhân phương pháp.
