"""Nội dung bộ slide Connect Four — Nhóm 26.

Một nguồn duy nhất cho cả file .pptx và bản thuyết minh Markdown.
Mỗi slide: part, title, bullets, notes, time (giây), layout, image, table...
"""

from __future__ import annotations

ASSETS = "assets"

SLIDES: list[dict] = [
    {
        "kind": "title",
        "title": "Connect Four AI",
        "subtitle": "Sáu cấp tác tử: từ tìm kiếm đến học tăng cường",
        "meta": [
            "Đồ án cuối kỳ · Trí tuệ nhân tạo nâng cao",
            "Nhóm 26 · Trường Đại học Sài Gòn · 11/2026",
            "GV hướng dẫn: Đỗ Như Tài",
        ],
        "members": [
            "Phan Lê Ngọc Như Ý — 3124720079",
            "Bùi Quyền Kiệt — 3124720036",
            "Phạm Thái Duy Khang — 3124720033",
            "Bùi Anh Đức — 3124720016",
        ],
        "time": 30,
        "notes": (
            "Kính chào thầy và các bạn. Nhóm 26 xin trình bày đồ án Connect Four AI.\n\n"
            "Câu chuyện của nhóm là một câu hỏi rất cũ của trí tuệ nhân tạo: với cùng một trò chơi, "
            "cách ra quyết định nào tốt hơn — tìm kiếm cổ điển, tìm kiếm xác suất, hay học máy? "
            "Nhóm cài đặt sáu tác tử ở sáu cấp độ, cho chúng đấu vòng tròn trên cùng một engine, "
            "cùng bộ khai cuộc và cùng cách tính điểm, rồi phân tích cả điểm số lẫn chi phí tính toán.\n\n"
            "Bài trình bày khoảng 25–30 phút, gồm bốn phần: nền tảng, sáu tác tử, giải đấu và kết quả, "
            "cuối cùng là phân tích và kết luận. Mời thầy và các bạn theo dõi."
        ),
    },
    {
        "kind": "content",
        "part": "MỞ ĐẦU",
        "title": "Nhóm thực hiện & nội dung trình bày",
        "layout": "table",
        "table": {
            "headers": ["Thành viên", "MSSV", "Phụ trách chính", "Slide"],
            "widths": [3.0, 1.5, 5.3, 1.9],
            "rows": [
                ["Phan Lê Ngọc Như Ý", "3124720079", "DQN, giải đấu, A4/A6, lợi thế đi trước", "14–21, 24–25, 27"],
                ["Bùi Quyền Kiệt", "3124720036", "CNN: dữ liệu, kiến trúc, kết quả, ablation A3", "11–13, 23"],
                ["Phạm Thái Duy Khang", "3124720033", "Luật, cấp 1–4, A1/A2/A5, ván MCTS thua", "3–4, 8–10, 22, 26"],
                ["Bùi Anh Đức", "3124720016", "Mở đầu, engine, kiến trúc, kết luận", "1–2, 5–7, 28–29"],
            ],
            "font": 13,
        },
        "bullets": [
            "**Bốn phần:** nền tảng (3–7) · sáu tác tử (8–15) · giải đấu & kết quả (16–21) · phân tích & kết luận (22–28)",
            "**Sản phẩm:** engine bitboard, hai giao diện, sáu tác tử, 4.500 ván đấu có log, năm nhóm ablation",
            "**Nguyên tắc:** mọi con số trong slide truy về CSV thô và `results/tables/report_numbers.csv`",
        ],
        "time": 50,
        "notes": (
            "Phần này để thầy và các bạn biết ai phụ trách gì, và bốn phần của bài nói.\n\n"
            "Nhóm chia việc theo tầng kỹ thuật: Đức làm engine và kiến trúc — phần nền móng; Khang làm bốn tác tử "
            "tìm kiếm, tức các cấp 1 đến 4; Kiệt làm CNN ở cấp 5; Ý làm DQN ở cấp 6, giải đấu và các phân tích "
            "về sau. Cách chia này giúp mỗi người hiểu sâu phần mình và vẫn ghép được thành một hệ thống chung.\n\n"
            "Điểm nhóm muốn nhấn mạnh ngay từ đầu: đây không phải bài \"cài xong thuật toán rồi kết luận\", mà là "
            "một quy trình đo lường. Mỗi kết quả đều có run ID, seed, log từng nước và bảng tổng hợp. "
            "Nhờ vậy, khi một con số trông lạ — ví dụ DQN thua Heuristic rất đậm — nhóm có thể truy ngược xem "
            "đó là lỗi hay là bản chất của cách huấn luyện."
        ),
    },
    {
        "kind": "content",
        "part": "PHẦN 1 · NỀN TẢNG",
        "title": "Bài toán & bốn câu hỏi nghiên cứu",
        "kicker": "Không giải lại trò chơi — đo và so sánh sáu cách ra quyết định trên cùng một sân chơi.",
        "layout": "cards",
        "bullets": [
            "Connect Four 7×6: luật đơn giản, thông tin đầy đủ, khoảng **4,5 × 10¹²** trạng thái, đã có lời giải lý thuyết (Allis, 1988)",
            "Mỗi tác tử chỉ được nhìn thấy **cùng một luật chơi, cùng bộ khai cuộc, cùng cách tính điểm**",
        ],
        "cards": [
            {"label": "RQ1", "text": "Alpha-Beta và MCTS khác nhau thế nào về tỷ lệ thắng, thời gian và số trạng thái đã khám phá?"},
            {"label": "RQ2", "text": "CNN học từ nhãn Alpha-Beta đạt hiệu năng nào, và có nhận diện được các thế chiến thuật?"},
            {"label": "RQ3", "text": "DQN có tự học được chiến lược? Số episode, cách khám phá và đối thủ huấn luyện ảnh hưởng ra sao?"},
            {"label": "RQ4", "text": "Học có giám sát và học tăng cường khác nhau thế nào về tỷ lệ thắng, chi phí và độ ổn định?"},
        ],
        "time": 60,
        "notes": (
            "Vì sao chọn Connect Four? Vì trò chơi này có ba tính chất rất thuận lợi cho một đồ án so sánh. "
            "Thứ nhất, luật rõ và tất định, nên kết quả ván đấu không phụ thuộc may mắn. Thứ hai, không gian "
            "trạng thái khoảng 4,5 nghìn tỷ — đủ lớn để tìm kiếm có ý nghĩa, nhưng đủ nhỏ để huấn luyện trong "
            "phạm vi học phần. Thứ ba, trò chơi đã được chứng minh có lời giải cho người đi trước, nên nhóm "
            "không đặt mục tiêu giải lại trò chơi; mục tiêu là so sánh phương pháp.\n\n"
            "Bốn câu hỏi RQ1 đến RQ4 tương ứng bốn cặp so sánh: tìm kiếm với tìm kiếm, học có giám sát với "
            "chuyên gia, học tăng cường với chính nó, và hai họ học với nhau. Khi trình bày kết quả, nhóm sẽ "
            "quay lại đúng bốn câu này để trả lời, thay vì kể lể từng thuật toán."
        ),
    },
    {
        "kind": "content",
        "part": "PHẦN 1 · NỀN TẢNG",
        "title": "Luật chơi & những gì tạo nên chiến thuật",
        "layout": "image-right",
        "image": "rules_board.png",
        "image_caption": "Bàn 7×6; quân rơi xuống ô trống thấp nhất. Bốn quân vàng ở hàng đáy là một chuỗi thắng.",
        "bullets": [
            "Bàn **7 cột × 6 hàng**; người chơi chỉ chọn cột, quân tự rơi xuống ô trống thấp nhất.",
            "Thắng khi có **4 quân liên tiếp** ngang, dọc hoặc chéo; hòa khi bàn đầy.",
            "Có **69 chuỗi bốn ô**: 24 ngang, 21 dọc, 24 chéo.",
            "Chiến thuật đáng đo: thắng ngay, chặn đối thủ, tạo **đòn kép**, kiểm soát cột giữa.",
            "Trọng lực là điểm khó: một cửa sổ trống chưa chắc đã đi được ngay.",
        ],
        "time": 45,
        "notes": (
            "Luật ai cũng biết, nhưng có hai chi tiết quan trọng cho phần sau.\n\n"
            "Một là số chuỗi thắng: 69. Con số này xuất hiện lại trong hàm lượng giá của Heuristic và trong "
            "cách nhóm kiểm tra engine. Hai là trọng lực: người chơi chỉ chọn cột, nên một đe dọa trên giấy "
            "có thể không thực hiện được nếu ô bên dưới đã bị lấp. Vì vậy nhóm tách riêng hàm đếm nước thắng "
            "hợp lệ, không suy ra chỉ từ việc đếm cửa sổ.\n\n"
            "Bốn tình huống chiến thuật — thắng ngay, chặn, đòn kép, kiểm soát trung tâm — sẽ trở thành bộ 31 "
            "thế kiểm thử ở phần kết quả. Nói cách khác, slide này không chỉ là luật chơi mà còn là định nghĩa "
            "thước đo của cả đồ án."
        ),
    },
    {
        "kind": "content",
        "part": "PHẦN 1 · NỀN TẢNG",
        "title": "Kiến trúc: một hợp đồng, nhiều cách chơi",
        "layout": "image-full",
        "image": "deck_architecture.png",
        "bullets": [
            "Hai engine cùng một hợp đồng: **bitboard 49-bit** (nhanh) và **lưới 6×7** (đối chứng độc lập).",
            "Mọi tác tử chỉ cần cài `choose(game.clone())`; đánh giá và giao diện không biết bên trong là thuật toán gì.",
        ],
        "time": 60,
        "notes": (
            "Đây là xương sống kỹ thuật của đồ án. Nhóm không viết sáu chương trình rời nhau, mà viết một hệ "
            "thống có hợp đồng chung.\n\n"
            "Engine có hai cài đặt: bản bitboard dùng trong chơi và đánh giá, và bản lưới dùng làm đối chứng. "
            "Hai bản phải cho cùng kết quả trên cùng chuỗi nước — đó là phép kiểm tra chéo mà Đức sẽ nói ở slide sau.\n\n"
            "Tác tử nhận một bản sao bàn cờ, nên không thể vô tình sửa trạng thái thật. Nhờ vậy cùng một agent "
            "chạy được trong terminal, trong Pygame, trong giải đấu và trong notebook phân tích. Phần đánh giá "
            "ghi ba loại log: manifest, một dòng mỗi ván, và một dòng mỗi nước. Đây là lý do mọi con số trong "
            "bài đều truy ngược được."
        ),
    },
    {
        "kind": "content",
        "part": "PHẦN 1 · NỀN TẢNG",
        "title": "Engine bitboard: nhanh nhưng vẫn kiểm chứng được",
        "layout": "bullets",
        "bullets": [
            "Hai số nguyên 64-bit đại diện hai bên; mỗi cột chiếm **7 bit** = 6 ô + 1 bit đệm chống tràn sang cột bên.",
            "Phát hiện thắng bằng bốn phép dịch **1, 7, 6, 8 bit** rồi AND — ứng với ngang, dọc và hai đường chéo.",
            "`ReferenceGame` cài lại luật bằng lưới 6×7 và quét 69 cửa sổ; ưu tiên dễ đọc hơn tốc độ.",
            "**Cross-check 1.000 chuỗi nước ngẫu nhiên:** bàn cờ, lượt đi, người thắng và nước hợp lệ khớp tuyệt đối.",
            "**289 test tự động** phủ engine, agent, match, logging và logic GUI không cần màn hình.",
            "Đánh đổi: bitboard nhanh hơn nhiều lần, nhưng mọi tối ưu đều phải chứng minh trước engine tham chiếu.",
        ],
        "callout": "Bài học: tối ưu chỉ đáng tin khi có một bản cài đặt chậm nhưng hiển nhiên để đối chiếu.",
        "time": 60,
        "notes": (
            "Phần này giải thích vì sao engine đủ nhanh để chạy 4.500 ván mà vẫn đáng tin.\n\n"
            "Ý tưởng bitboard: mỗi cột là bảy bit liền nhau, sáu bit chơi và một bit đệm. Bit đệm rất quan trọng: "
            "khi dịch bit giữa hai cột, nếu không có nó, quân ở cột này có thể \"nhảy\" sang cột bên và tạo chuỗi "
            "thắng giả. Với bit đệm, bốn phép dịch 1, 7, 6, 8 đủ để kiểm tra bốn hướng.\n\n"
            "Nhưng tối ưu kiểu gì cũng có thể sai. Vì vậy nhóm viết thêm ReferenceGame bằng lưới, chạy 1.000 "
            "chuỗi nước ngẫu nhiên và so từng bước. Nếu hai engine lệch nhau ở bất kỳ bước nào, test sẽ bắt được. "
            "Cách làm này tốn công ban đầu nhưng tiết kiệm rất nhiều thời gian gỡ lỗi về sau — nhất là khi "
            "kết quả giải đấu trông bất thường."
        ),
    },
    {
        "kind": "content",
        "part": "PHẦN 1 · NỀN TẢNG",
        "title": "Sáu cấp tác tử: mỗi cấp thêm một cách học",
        "layout": "table",
        "table": {
            "headers": ["Cấp", "Tác tử", "Cách ra quyết định", "Ngân sách / quy mô"],
            "widths": [0.9, 2.4, 5.6, 2.8],
            "rows": [
                ["1", "Random", "Chọn ngẫu nhiên trong các cột hợp lệ", "baseline"],
                ["2", "Heuristic", "Hàm điểm 69 cửa sổ + luật thắng/chặn/an toàn", "không tìm kiếm"],
                ["3", "Alpha-Beta", "Negamax + cắt tỉa + sắp xếp nước", "độ sâu 5"],
                ["4", "MCTS", "UCT, rollout ngẫu nhiên đến hết ván", "1.000 mô phỏng/nước"],
                ["5", "CNN Policy", "Học có giám sát từ nước Alpha-Beta chọn", "420.551 tham số"],
                ["6", "DQN", "Học tăng cường từ thưởng thắng/thua", "10.000 episode, replay 100k"],
            ],
            "font": 13.5,
        },
        "bullets": [
            "Cấp 1–4 là **tìm kiếm và luật**; cấp 5–6 là **học máy** — nhưng tất cả dùng chung một giao diện.",
            "Mỗi cấp là một giả thuyết: thêm tri thức hoặc thêm dữ liệu thì mạnh hơn đến đâu, và trả giá bao nhiêu?",
        ],
        "time": 45,
        "notes": (
            "Sáu cấp không phải sáu sản phẩm rời mà là một thang đo. Cấp 1 là mốc thấp nhất: ngẫu nhiên nhưng "
            "hợp lệ. Cấp 2 thêm hiểu biết về bàn cờ bằng hàm điểm. Cấp 3 thêm khả năng nhìn trước. Cấp 4 thay "
            "việc nhìn trước bằng mô phỏng. Cấp 5 học từ chuyên gia. Cấp 6 tự học từ phần thưởng.\n\n"
            "Tham số ở cột phải là tham số đã công bố và đóng băng trước giải đấu, không phải tham số được "
            "chỉnh sau khi thấy kết quả. Ví dụ Alpha-Beta luôn sâu 5, MCTS luôn 1.000 mô phỏng, CNN và DQN dùng "
            "checkpoint đã chọn theo quy tắc đăng ký trước.\n\n"
            "Cách trình bày từng cấp ở các slide sau sẽ theo cùng một khung: ý tưởng, cài đặt, chi phí, và điểm yếu."
        ),
    },
    {
        "kind": "content",
        "part": "PHẦN 2 · SÁU TÁC TỬ",
        "title": "Cấp 1–2: Random & Heuristic",
        "layout": "bullets",
        "bullets": [
            "**Random** là mốc so sánh: chọn đều trong các cột còn trống, không nhìn trước.",
            "**Heuristic** chấm điểm bằng 69 cửa sổ bốn ô, cộng thưởng cột giữa (6/12/18 điểm theo khoảng cách).",
            "Công thức: `E = C + 100·n₃ + 10·n₂ − 80·m₃ − 10·m₂ + 9000·win_p − 5000·win_q`",
            "Trọng số chính: thắng 10.000 · chặn 9.000 · tránh mở đường 5.000 · ba quân 100 · hai quân 10.",
            "Thứ tự quyết định: **thắng ngay → chặn → nước an toàn → điểm cao nhất**.",
            "Kết quả: 0,592 chung; thắng Random 200–0–0; thua Alpha-Beta 0,240 nhưng thắng DQN 0,912.",
        ],
        "callout": "Heuristic không phải “đối thủ yếu để lót đường” — nó là baseline mạnh nhất mà hai mô hình học phải vượt.",
        "time": 75,
        "notes": (
            "Heuristic là tác tử quan trọng nhất trong bài, vì nó vừa là đối thủ, vừa là chuyên gia sinh nhãn cho CNN, "
            "vừa là đối thủ huấn luyện của DQN.\n\n"
            "Hàm điểm nhìn 69 cửa sổ bốn ô. Với mỗi cửa sổ, nếu chỉ có quân mình thì cộng điểm theo số quân; "
            "nếu có quân địch thì trừ. Cộng thêm thưởng cột giữa vì cột 3 tạo nhiều chuỗi nhất. Điểm thắng và "
            "điểm chặn được xử lý riêng, không chỉ dựa vào hàm điểm — đó là lý do Heuristic thắng ngay 100% "
            "trên bộ thế kiểm thử.\n\n"
            "Con số 0,592 là điểm trung bình trước năm đối thủ còn lại. Nó thắng Random tuyệt đối, thua Alpha-Beta "
            "và MCTS, nhưng thắng CNN nhẹ và thắng DQN rất đậm. Điều này đặt ra một câu hỏi thú vị: nếu một hàm "
            "luật đơn giản làm được vậy, học máy cần gì để vượt?"
        ),
    },
    {
        "kind": "content",
        "part": "PHẦN 2 · SÁU TÁC TỬ",
        "title": "Cấp 3: Alpha-Beta — nhìn trước 5 nước",
        "layout": "bullets",
        "bullets": [
            "Negamax + cắt tỉa Alpha-Beta; lượng giá tại lá bằng Heuristic, giữ góc nhìn của người đi gốc.",
            "Sắp xếp nước **trung tâm trước** để tạo cận sớm; cùng giá trị minimax nhưng ít nút hơn.",
            "A1 ở độ sâu 6: **58.678 → 2.697 nút** (−95,4%) và **1.965 → 79,6 ms** (nhanh 24,7 lần).",
            "Giải đấu: **0,793**; 38,1 ms/nước; 1.542 nút/nước — nhiều tính toán nhất trong sáu tác tử.",
            "Điểm yếu: bỏ sót **5/18 nước thắng ngay** trên bộ 31 thế (độ đúng 0,72).",
        ],
        "callout": "Alpha-Beta mạnh vì nhìn xa, nhưng “nhìn xa” không đồng nghĩa “không bao giờ bỏ sót nước thắng ngay”.",
        "time": 75,
        "notes": (
            "Alpha-Beta là tác tử mạnh thứ hai và là tác tử đắt nhất về tính toán.\n\n"
            "Cài đặt dùng negamax: giá trị ở lá là điểm Heuristic nhân với màu của người chơi gốc, nên toàn bộ "
            "cây luôn được đánh giá từ một góc nhìn. Cắt tỉa Alpha-Beta không đổi giá trị minimax — đó là điều "
            "A1 kiểm chứng — nhưng giảm mạnh số nút phải duyệt.\n\n"
            "Con số ấn tượng nhất: ở độ sâu 6, bật cả cắt tỉa và sắp xếp giảm 95,4% số nút, thời gian từ gần 2 "
            "giây xuống 80 mili-giây. Đây là lý do thực nghiệm có thể chạy 3.000 ván.\n\n"
            "Nhưng có một điểm yếu đáng nói: trên bộ 31 thế, Alpha-Beta chỉ thắng ngay 13/18 lần. Nghe lạ, nhưng "
            "hợp lý: ở độ sâu 5, nếu nước thắng ngay nằm ngoài tầm nhìn hoặc bị hàm lượng giá \"che\" bởi một "
            "nước khác cũng tốt, nó có thể chọn nước khác. Nhóm báo cáo đúng con số này thay vì chỉ khoe điểm chung."
        ),
    },
    {
        "kind": "content",
        "part": "PHẦN 2 · SÁU TÁC TỬ",
        "title": "Cấp 4: MCTS — mô phỏng thay vì lượng giá",
        "layout": "bullets",
        "bullets": [
            "Chọn nhánh theo **UCT**: `w/n + c·√(ln N / n)`, cân bằng khai thác và khám phá.",
            "Mỗi nước chạy **1.000 mô phỏng**; rollout ngẫu nhiên đến khi kết thúc ván.",
            "Không cần hàm lượng giá thủ công; là thuật toán **anytime** — càng nhiều thời gian càng tốt.",
            "Giải đấu: **0,817** — cao nhất; 20,7 ms/nước; 1.000 mô phỏng/nước.",
            "Chiến thuật: **1,00** thắng ngay · **0,975** chặn · **0,95** đòn kép.",
        ],
        "callout": "MCTS đổi “hiểu bàn cờ” lấy “thử nhiều đường”: đơn giản hơn về tri thức, nhưng tốn thời gian hơn.",
        "time": 75,
        "notes": (
            "MCTS là tác tử dẫn đầu giải đấu. Cách nó ra quyết định khác hẳn Alpha-Beta: không cần hàm lượng giá, "
            "mà chơi thử ngẫu nhiên nhiều lần rồi chọn nước có tỷ lệ thắng thực nghiệm cao nhất.\n\n"
            "Công thức UCT có hai phần: phần khai thác là w/n — tỷ lệ thắng của nhánh; phần khám phá là căn bậc "
            "hai của log tổng số lần chia số lần thăm nhánh. Nhờ vậy nhánh chưa thử vẫn có cơ hội được thăm.\n\n"
            "Với 1.000 mô phỏng mỗi nước, MCTS chỉ mất khoảng 21 mili-giây — nhanh hơn Alpha-Beta — mà vẫn đạt "
            "0,817. Trên bộ thế chiến thuật, nó gần như hoàn hảo: thắng ngay 100%, chặn 97,5%, đòn kép 95%. "
            "Điểm yếu là chi phí tăng tuyến tính theo số mô phỏng, và rollout ngẫu nhiên có thể bỏ sót nước phòng "
            "thủ hiển nhiên — nhóm sẽ có một ván minh họa ở cuối bài."
        ),
    },
    {
        "kind": "content",
        "part": "PHẦN 2 · SÁU TÁC TỬ",
        "title": "Cấp 5: CNN — dữ liệu đến từ chuyên gia",
        "layout": "bullets",
        "bullets": [
            "Sinh **5.000 ván**; nhãn tại mỗi thế là nước mà **Alpha-Beta sâu 5** chọn.",
            "110.083 mẫu thô → loại 18.025 mẫu trùng/đối xứng → **133.208 mẫu train** sau lật gương.",
            "Chia **theo ván** 70/15/15 và khử trùng lặp xuyên tập: không có trạng thái nào xuất hiện ở cả train và test.",
            "Cohort chính: 1.982 ván train (79.924 mẫu), 7.958 mẫu validation, **7.399 mẫu test**.",
            "Đầu vào **2×6×7**: kênh 0 là quân của bên đang đi, kênh 1 là quân đối thủ — cùng một mạng dùng cho cả hai bên.",
        ],
        "callout": "Bài toán thực chất là bắt chước chuyên gia: CNN học “Alpha-Beta sẽ đi đâu”, không học “nước nào thắng”.",
        "time": 60,
        "notes": (
            "CNN học có giám sát, nên chất lượng nhãn là gốc rễ. Nhóm cho Alpha-Beta sâu 5 tự chơi 5.000 ván, "
            "rồi tại mỗi thế ghi lại nước nó chọn. Nói cách khác, CNN học bắt chước một chuyên gia cụ thể, "
            "không học trực tiếp từ kết quả thắng thua.\n\n"
            "Ba chi tiết chống rò rỉ dữ liệu. Một, chia theo ván chứ không chia theo thế — nếu chia theo thế, "
            "hai thế gần nhau trong cùng ván có thể rơi vào train và test. Hai, khử trùng lặp xuyên tập, kể cả "
            "bản đối xứng qua trục dọc. Ba, chỉ lật gương tập train, không đụng validation và test.\n\n"
            "Kết quả là 7.399 mẫu test hoàn toàn chưa thấy. Đầu vào hai kênh tương đối giúp cùng một mạng chơi "
            "được cả khi đi trước lẫn đi sau, thay vì phải học hai bộ trọng số."
        ),
    },
    {
        "kind": "content",
        "part": "PHẦN 2 · SÁU TÁC TỬ",
        "title": "Cấp 5: kiến trúc & huấn luyện",
        "layout": "image-right",
        "image": "state_tensor.png",
        "image_caption": "Hai kênh đầu vào: quân mình (0) và quân đối thủ (1).",
        "bullets": [
            "Ba lớp **Conv 3×3, 64 filter**, BatchNorm + ReLU, `padding=1` giữ nguyên 6×7.",
            "Flatten 2.688 → FC 128 → **7 logits**; **420.551 tham số**.",
            "Không pooling: bàn chỉ 42 ô, giảm kích thước sớm sẽ mất vị trí cho chuỗi bốn.",
            "Train: Adam 1e-3, batch 256, 20 epoch, cross-entropy; **best epoch 5**, val loss **1,08349**.",
            "Che cột đầy bằng −∞ trước `argmax` → **100% nước hợp lệ** khi thi đấu.",
        ],
        "time": 60,
        "notes": (
            "Kiến trúc cố ý nhỏ. Ba lớp tích chập 3×3 với 64 filter, giữ nguyên kích thước 6×7, rồi hai lớp "
            "fully connected. Tổng khoảng 420 nghìn tham số — rất nhỏ so với các mạng thị giác, nhưng đủ cho "
            "một bàn cờ 42 ô.\n\n"
            "Quyết định không dùng pooling là có chủ đích: chuỗi bốn quân phụ thuộc vào vị trí tương đối của "
            "các ô. Nếu giảm kích thước sớm, mạng có thể mất chính thông tin cần cho việc nhận ra chuỗi.\n\n"
            "Huấn luyện chỉ mất khoảng 134 giây trên CPU. Điểm chọn checkpoint là validation loss thấp nhất, "
            "rơi vào epoch 5; sau đó mô hình bắt đầu quá khớp. Khi suy luận, các cột đầy bị gán âm vô cực "
            "trước khi lấy argmax, nên tác tử không bao giờ trả về nước không hợp lệ — kể cả khi trọng số còn "
            "ngẫu nhiên."
        ),
    },
    {
        "kind": "content",
        "part": "PHẦN 2 · SÁU TÁC TỬ",
        "title": "Cấp 5: kết quả — học được, nhưng chưa vượt chuyên gia",
        "layout": "image-full",
        "image": "cnn_main_learning_curve.png",
        "bullets": [
            "Test top-1 **56,76%** trên 7.399 mẫu; 100% nước hợp lệ. Thắng ngay 0,61 · chặn 0,83 · đòn kép 0,67.",
            "Giải đấu **0,546**: thắng Random 0,988 · thua Heuristic 0,405 · thua Alpha-Beta 0,233 · thắng DQN 0,895.",
        ],
        "time": 60,
        "notes": (
            "Ba con số cần nhớ. Thứ nhất, top-1 56,76%: mô hình chọn đúng nước của Alpha-Beta hơn một nửa số thế. "
            "Với bảy cột, đoán ngẫu nhiên chỉ khoảng 14%, nên đây là tín hiệu học thật.\n\n"
            "Thứ hai, độ chính xác theo tình huống không đều: chặn 83%, nhưng thắng ngay chỉ 61%. Mô hình bắt "
            "chước chuyên gia khá tốt ở thế phòng thủ, nhưng vẫn bỏ sót một số nước thắng trước mắt — điều này "
            "khớp với việc nhãn đến từ Alpha-Beta sâu 5, bản thân chuyên gia cũng bỏ sót 5/18 nước thắng ngay.\n\n"
            "Thứ ba, điểm giải đấu 0,546: trên Random rất cao, dưới Heuristic và hai tác tử tìm kiếm, trên DQN. "
            "Đường cong học cho thấy validation loss chạm đáy ở epoch 5 rồi tăng — nếu huấn luyện thêm, mô hình "
            "sẽ học thuộc train mà không giỏi hơn. Đây là lý do nhóm đóng băng checkpoint tại epoch 5."
        ),
    },
    {
        "kind": "content",
        "part": "PHẦN 2 · SÁU TÁC TỬ",
        "title": "Cấp 6: DQN — tự học từ thắng/thua",
        "layout": "image-right",
        "image": "dqn_training_flow.png",
        "image_caption": "Vòng huấn luyện: chơi → lưu transition → lấy batch → cập nhật Q.",
        "bullets": [
            "**MDP:** state 2×6×7; 7 cột (mặt nạ cột đầy); thưởng cuối ván **+1 / 0 / −1**, giữa ván bằng 0.",
            "Mấu chốt: `s'` là bàn **sau khi đối thủ đáp trả** — lấy ngay sau nước DQN sẽ đánh giá sai góc nhìn.",
            "Mạng 2 Conv + FC 128 → 7 giá trị Q; **383.239 tham số**.",
            "Replay **100.000**, batch 64, γ 0,99, target network mỗi **500** cập nhật, Huber, Adam 1e-3.",
            "ε: 1,0 → 0,05 (decay 0,9995); **10.000 episode**, ~26 phút CPU, 94.696 cập nhật optimizer.",
        ],
        "time": 75,
        "notes": (
            "DQN là tác tử duy nhất học từ phần thưởng thay vì bắt chước. Thiết kế MDP nghe đơn giản nhưng có "
            "một chi tiết dễ sai: trạng thái kế tiếp phải là bàn cờ sau khi đối thủ đã đáp lại, tức là lượt kế "
            "tiếp của DQN. Nếu lấy ngay sau nước DQN, `max Q(s')` sẽ đánh giá bàn cờ từ góc nhìn của đối thủ và "
            "toàn bộ mục tiêu Bellman sai.\n\n"
            "Mạng nhỏ hơn CNN một chút, khoảng 383 nghìn tham số. Replay buffer 100 nghìn transition, batch 64, "
            "target network đồng bộ mỗi 500 cập nhật, loss Huber. Epsilon giảm từ 1 xuống 0,05 theo episode.\n\n"
            "Huấn luyện 10.000 episode mất khoảng 26 phút CPU, tương đương 94.696 lần cập nhật. Đối thủ huấn luyện "
            "là Heuristic, bắt đầu từ bàn trống. Chính lựa chọn này — đối thủ cố định, bàn trống — sẽ là nguồn gốc "
            "của vấn đề ở các slide sau."
        ),
    },
    {
        "kind": "content",
        "part": "PHẦN 2 · SÁU TÁC TỬ",
        "title": "Cấp 6: chọn checkpoint trước khi nhìn kết quả giải",
        "layout": "table",
        "table": {
            "headers": ["Mốc episode", "Score vs Random", "Score vs Heuristic", "Điểm chọn mốc"],
            "widths": [2.4, 3.0, 3.2, 2.6],
            "rows": [
                ["1.000", "0,59 (59–0–41)", "0,01 (1–0–99)", "0,300"],
                ["2.500", "0,56 (56–0–44)", "0,05 (5–0–95)", "0,305"],
                ["5.000", "0,55 (55–0–45)", "0,07 (7–1–92)", "0,312"],
                ["10.000", "0,63 (63–0–37)", "0,12 (12–0–88)", "0,375  ← chọn"],
            ],
            "font": 14,
        },
        "bullets": [
            "Quy tắc **đăng ký trước**: chọn mốc có điểm validation trung bình cao nhất trong 4 mốc; hòa thì chọn mốc sớm hơn.",
            "Validation: 100 ván/đối thủ, seed **20261102 / 20261103** — tách hoàn toàn khỏi seed giải đấu.",
            "Đóng băng **18/11/2026**: `final.pt` ~1,5 MB, kèm sha256, commit và siêu tham số trong `final.json`.",
            "Kết quả giải: **0,178** — chỉ trên Random; nhóm không chỉnh checkpoint sau khi thấy kết quả.",
        ],
        "callout": "Một checkpoint yếu nhưng được chọn đúng quy tắc vẫn là bằng chứng trung thực hơn một checkpoint đẹp nhưng chọn sau khi biết đáp án.",
        "time": 60,
        "notes": (
            "Slide này quan trọng về phương pháp luận. Nếu chọn checkpoint sau khi xem kết quả giải, con số cuối "
            "cùng sẽ mất ý nghĩa thống kê. Vì vậy nhóm đăng ký trước quy tắc: trong bốn mốc 1.000, 2.500, 5.000, "
            "10.000 episode, chọn mốc có điểm validation trung bình cao nhất; hòa thì chọn mốc sớm hơn.\n\n"
            "Validation dùng seed riêng, không dùng seed giải đấu. Kết quả là mốc 10.000 episode, với 0,375 điểm "
            "trung bình — vẫn rất thấp trước Heuristic, nhưng cao nhất trong bốn mốc.\n\n"
            "Checkpoint được đóng băng ngày 18/11, kèm sha256 và commit. Khi giải đấu cho ra 0,178, nhóm giữ "
            "nguyên, không huấn luyện lại để \"cứu\" điểm. Đây là lựa chọn có chủ đích: một kết quả âm tính trung "
            "thực vẫn dạy được nhiều hơn một con số đẹp nhưng không kiểm chứng được."
        ),
    },
    {
        "kind": "content",
        "part": "PHẦN 3 · GIẢI ĐẤU & KẾT QUẢ",
        "title": "Thiết kế giải đấu: công bằng trước, kết quả sau",
        "layout": "bullets",
        "bullets": [
            "6 tác tử → **15 cặp**. Mặc định: 100 khai cuộc × 2 bên = **200 ván/cặp**, tổng **3.000 ván**, seed 20261118.",
            "Cùng thời gian: 50 khai cuộc × 2 bên = 100 ván/cặp, tổng **1.500 ván**, seed 20261119.",
            "Khai cuộc là **4 nước ngẫu nhiên hợp lệ**, khác nhau đôi một; mọi cặp dùng chung một bộ khai cuộc.",
            "Mỗi khai cuộc chơi hai ván **đổi bên**; score = (thắng + 0,5·hòa)/số ván; CI Wilson 95%.",
            "Chế độ 0,2 s/nước: Alpha-Beta lặp sâu dần, MCTS mô phỏng đến hết giờ — cùng một ngân sách thời gian.",
            "Tham số, seed, khai cuộc và log từng nước được ghi lại để tái lập.",
        ],
        "callout": "Tổng cộng 4.500 ván — mọi kết luận ở phần sau đều dựa trên cùng một giao thức này.",
        "time": 60,
        "notes": (
            "Giải đấu được thiết kế để loại bỏ ba nguồn thiên lệch thường gặp.\n\n"
            "Thiên lệch thứ nhất là đi trước: trong Connect Four, người đi trước có lợi thế nhỏ. Nhóm cho mỗi "
            "khai cuộc chơi hai ván đổi bên, nên lợi thế này chia đều cho cả hai tác tử.\n\n"
            "Thiên lệch thứ hai là khai cuộc: nếu mỗi cặp bắt đầu từ bàn trống, các tác tử tất định sẽ lặp lại "
            "cùng một ván. Nhóm dùng 100 khai cuộc bốn nước ngẫu nhiên, khác nhau đôi một, và mọi cặp dùng chung "
            "bộ khai cuộc. Nhờ vậy so sánh là cùng điều kiện.\n\n"
            "Thiên lệch thứ ba là ngân sách. Chế độ mặc định để mỗi tác tử dùng tham số công bố của mình — đây "
            "là so sánh \"sản phẩm hoàn chỉnh\". Chế độ cùng thời gian ép Alpha-Beta và MCTS chỉ được dùng 0,2 "
            "giây mỗi nước, để trả lời câu hỏi khác: nếu bị giới hạn thời gian như nhau thì ai hơn?\n\n"
            "Điểm được tính (thắng + 0,5 hòa)/số ván, kèm khoảng tin cậy Wilson 95%."
        ),
    },
    {
        "kind": "content",
        "part": "PHẦN 3 · GIẢI ĐẤU & KẾT QUẢ",
        "title": "Kết quả tổng thể: tìm kiếm vẫn dẫn đầu",
        "layout": "image-full",
        "image": "deck_scores.png",
        "bullets": [
            "Mặc định: **MCTS 0,817 > Alpha-Beta 0,793 > Heuristic 0,592 > CNN 0,546 > DQN 0,178 > Random 0,073**.",
            "Cùng 0,2 s/nước: thứ hạng **không đổi**; MCTS tăng lên 0,871, Alpha-Beta 0,794.",
        ],
        "time": 60,
        "notes": (
            "Đây là bức tranh tổng thể. Hai tác tử tìm kiếm dẫn đầu, Heuristic đứng giữa, CNN bám sát Heuristic, "
            "DQN và Random ở cuối.\n\n"
            "Điều đáng chú ý là thứ hạng không đổi khi chuyển sang chế độ cùng thời gian. Điều này gợi ý rằng "
            "khoảng cách không chỉ do Alpha-Beta được phép tính lâu hơn; MCTS vẫn giữ vị trí dẫn đầu khi cả hai "
            "bị ép trong 0,2 giây.\n\n"
            "Cũng cần đọc đúng khoảng cách: MCTS 0,817 và Alpha-Beta 0,793 chỉ hơn nhau 0,024 — trong khoảng "
            "tin cậy, chưa chắc khác biệt. Còn CNN 0,546 so với Heuristic 0,592 là khoảng 0,046, cũng không lớn. "
            "Vì vậy thông điệp không phải \"MCTS vô địch tuyệt đối\", mà là \"hai họ tìm kiếm tạo thành nhóm dẫn "
            "đầu, học có giám sát bám sát nhóm giữa, còn DQN thì chưa cạnh tranh được\"."
        ),
    },
    {
        "kind": "content",
        "part": "PHẦN 3 · GIẢI ĐẤU & KẾT QUẢ",
        "title": "Ma trận đối đầu: ai thắng ai?",
        "layout": "image-right",
        "image": "deck_matrix.png",
        "image_caption": "Hàng là tác tử, cột là đối thủ; ô càng đậm là score càng cao.",
        "bullets": [
            "Alpha-Beta và MCTS **chia đôi**: 0,49 và 0,51 — chưa phân biệt được ở chế độ mặc định.",
            "Heuristic thắng CNN **0,59** nhưng thua cả hai tác tử tìm kiếm (0,24 và 0,21).",
            "CNN thắng DQN **0,90**, thắng Random 0,99; DQN gần như không thắng nổi nhóm tìm kiếm (0,00–0,04).",
            "Không có đường tắt: tác tử mạnh nhất vẫn thua vài ván trước tác tử yếu nhất.",
        ],
        "callout": "Đọc ma trận theo hàng: mỗi hàng là “thành tích” của một tác tử trước năm đối thủ còn lại.",
        "time": 60,
        "notes": (
            "Ma trận này cho thấy cấu trúc của giải đấu rõ hơn bảng điểm trung bình.\n\n"
            "Góc trên trái là cuộc đối đầu trực tiếp giữa hai tác tử mạnh nhất: Alpha-Beta 0,49, MCTS 0,51. "
            "Chênh lệch 0,02 với 200 ván là quá nhỏ để kết luận.\n\n"
            "Cột Heuristic là cột đáng chú ý: nó thắng Random và DQN gần tuyệt đối, thắng CNN 0,59, nhưng chỉ "
            "đạt 0,24 trước Alpha-Beta và 0,21 trước MCTS. Nói cách khác, Heuristic là \"trần\" của nhóm không "
            "tìm kiếm.\n\n"
            "DQN gần như trắng trước ba tác tử tìm kiếm: 0,04 trước Alpha-Beta, 0,00 trước MCTS. Nhưng nó vẫn "
            "thắng Random 0,66, cho thấy mô hình đã học được gì đó, chỉ là chưa đủ để cạnh tranh.\n\n"
            "Cuối cùng, ngay cả MCTS cũng thua 1 ván trước Random trong 200 ván. Không có tác tử nào bất bại — "
            "đó là lý do nhóm phân tích cả ván thua, không chỉ trình bày điểm trung bình."
        ),
    },
    {
        "kind": "content",
        "part": "PHẦN 3 · GIẢI ĐẤU & KẾT QUẢ",
        "title": "Alpha-Beta vs MCTS: ngang nhau, cho đến khi bị ép thời gian",
        "layout": "table",
        "table": {
            "headers": ["", "Mặc định", "Cùng 0,2 s/nước"],
            "widths": [4.2, 3.8, 3.8],
            "rows": [
                ["Score của Alpha-Beta trước MCTS", "0,487  [0,419; 0,556]", "0,390  [0,300; 0,488]"],
                ["Kết quả 200 / 100 ván", "96–3–101", "37–4–59"],
                ["Chi phí mỗi nước", "1.542 nút", "8.786 nút  ·  15.948 mô phỏng"],
                ["Kết luận", "Chưa phân biệt được (CI chứa 0,5)", "MCTS nhỉnh hơn (CI không chứa 0,5)"],
            ],
            "font": 13.5,
        },
        "bullets": [
            "Ở chế độ mặc định, Alpha-Beta và MCTS gần như **hòa**: 0,487 với khoảng tin cậy chứa 0,5.",
            "Khi cùng bị giới hạn 0,2 giây, Alpha-Beta chỉ còn **0,390** — MCTS dùng trọn ngân sách tốt hơn.",
            "Không kết luận “thuật toán nào hiệu quả hơn trên mỗi phép tính”: giải đấu không kiểm soát số phép tính.",
        ],
        "time": 75,
        "notes": (
            "Đây là cặp đấu được quan tâm nhất, và cũng là chỗ dễ nói quá.\n\n"
            "Ở chế độ mặc định, Alpha-Beta đạt 0,487 trước MCTS. Khoảng tin cậy 95% là 0,419 đến 0,556, chứa 0,5. "
            "Nghĩa là với 200 ván, chưa thể nói bên nào mạnh hơn. Đây là kết quả hòa về mặt thống kê.\n\n"
            "Khi chuyển sang 0,2 giây mỗi nước, bức tranh rõ hơn: Alpha-Beta chỉ còn 0,390, khoảng 0,300 đến "
            "0,488, không chứa 0,5. Vì sao? Alpha-Beta bị cắt độ sâu khi hết giờ, nên có những nước chỉ nhìn "
            "được vài tầng; MCTS là thuật toán anytime, dừng lúc nào cũng có kết quả tạm ổn. Trong 0,2 giây, "
            "MCTS chạy được gần 16.000 mô phỏng, trong khi Alpha-Beta duyệt khoảng 8.800 nút.\n\n"
            "Nhưng nhóm không kết luận \"MCTS hiệu quả hơn trên mỗi phép tính\". Một nút Alpha-Beta và một "
            "rollout MCTS không cùng đơn vị chi phí. Muốn trả lời câu đó cần một thí nghiệm cân bằng số phép "
            "tính, mà đồ án chưa làm."
        ),
    },
    {
        "kind": "content",
        "part": "PHẦN 3 · GIẢI ĐẤU & KẾT QUẢ",
        "title": "Chi phí tính toán: cái giá của việc nhìn xa",
        "layout": "image-full",
        "image": "deck_latency.png",
        "bullets": [
            "Alpha-Beta **38,1 ms/nước** (p95 100,6) và MCTS **20,7 ms** (p95 32,8); Heuristic, CNN, DQN đều **dưới 1 ms**.",
            "Cùng 0,2 s/nước: Alpha-Beta 170,3 ms và MCTS 206,0 ms — cả hai đều chạm ngân sách.",
        ],
        "time": 45,
        "notes": (
            "Slide này trả lời phần \"cái giá\" của RQ1. Hai tác tử tìm kiếm đắt hơn ba bậc so với phần còn lại: "
            "Alpha-Beta 38 mili-giây mỗi nước, MCTS 21 mili-giây, trong khi Heuristic 0,2 mili-giây, CNN 0,6, "
            "DQN 0,46.\n\n"
            "Điều này giải thích một phần vì sao chúng mạnh hơn: chúng được phép tính nhiều hơn. Vì vậy khi nói "
            "\"tìm kiếm thắng\", phải nói kèm \"với nhiều tính toán hơn\". Đây không phải so sánh công bằng về "
            "chi phí, mà là so sánh sản phẩm ở cấu hình công bố.\n\n"
            "Chế độ cùng thời gian mới là phép thử công bằng hơn về thời gian: cả hai bị ép 0,2 giây, và cả hai "
            "đều vượt nhẹ ngân sách ở một số nước vì kiểm tra giờ chỉ sau mỗi vòng. Độ trễ còn phụ thuộc máy và "
            "tải nền, nên nhóm chỉ so trong cùng một lần chạy, không so với máy khác."
        ),
    },
    {
        "kind": "content",
        "part": "PHẦN 3 · GIẢI ĐẤU & KẾT QUẢ",
        "title": "Độ đúng chiến thuật: thắng bằng điểm chưa đủ",
        "layout": "image-full",
        "image": "deck_tactical.png",
        "bullets": [
            "**31 thế** (30 thế còn chơi + 1 bàn hòa đầy): 18 lượt thắng ngay, 6 chặn, 3 đòn kép, 6 thế yên — có thế thuộc nhiều nhóm.",
            "MCTS gần hoàn hảo (1,00 · 0,975 · 0,95); Alpha-Beta chặn và đòn kép 1,00 nhưng chỉ 0,72 thắng ngay.",
        ],
        "time": 60,
        "notes": (
            "Điểm trung bình có thể che đi lỗi chiến thuật. Bộ 31 thế này kiểm tra trực tiếp: gặp nước thắng ngay, "
            "tác tử có thấy không? Gặp đe dọa, có chặn không? Có tạo được đòn kép không?\n\n"
            "MCTS gần như hoàn hảo. Alpha-Beta chặn và đòn kép 100%, nhưng chỉ thắng ngay 72% — tức bỏ sót 5 "
            "trong 18 thế. Nghe nghịch lý, nhưng có thể giải thích: ở độ sâu 5, một nước thắng ngay có thể bị "
            "hàm lượng giá xếp sau một nước khác cũng được điểm cao, hoặc nằm ngoài tầm nhìn. Nhóm chưa tách "
            "riêng nguyên nhân, nên chỉ báo cáo hiện tượng.\n\n"
            "CNN đạt 61% thắng ngay và 83% chặn — khá hơn kỳ vọng với một mạng nhỏ. DQN yếu nhất: 22% thắng ngay, "
            "67% chặn, 33% đòn kép.\n\n"
            "Một lưu ý thống kê: với CNN và DQN, mỗi thế chỉ chạy một lần vì mô hình tất định, nên khoảng tin cậy "
            "rất rộng. Các con số này là tín hiệu định hướng, không phải ước lượng chính xác."
        ),
    },
    {
        "kind": "content",
        "part": "PHẦN 4 · PHÂN TÍCH",
        "title": "Ablation tìm kiếm: cắt tỉa, mô phỏng, độ sâu",
        "layout": "image-full",
        "image": "deck_search.png",
        "bullets": [
            "**A1:** cắt tỉa + sắp xếp giảm **95,4%** số nút ở độ sâu 6, nhanh **24,7 lần**.",
            "**A2:** 100 → 5.000 mô phỏng: score 0,135 → 0,740, nhưng 2,5 → 126,8 ms/nước.",
            "**A5:** sâu 4–6 đều khoảng 0,81; tăng sâu chỉ tăng chi phí (10,4 → 148,7 ms).",
        ],
        "callout": "Không có “càng nhiều càng tốt”: mỗi đơn vị tính toán thêm phải đổi lại bằng chất lượng nước đi.",
        "time": 75,
        "notes": (
            "Ba ablation này trả lời câu hỏi: thành phần nào thực sự tạo ra sức mạnh?\n\n"
            "A1 là kết quả rõ nhất: ở độ sâu 6, bật cắt tỉa và sắp xếp giảm từ 58.678 nút xuống 2.697 nút, tức "
            "95,4%, thời gian từ gần 2 giây xuống 80 mili-giây. Điều quan trọng là giá trị minimax không đổi — "
            "đây là tối ưu thuần túy về chi phí, không phải đánh đổi chất lượng.\n\n"
            "A2 cho thấy MCTS cải thiện mạnh từ 100 lên 1.000 mô phỏng, nhưng từ 1.000 lên 5.000 chỉ tăng thêm "
            "khoảng 0,15 điểm trong khi thời gian tăng gấp năm. Đây là lý do nhóm chọn 1.000 mô phỏng cho cấu "
            "hình chính.\n\n"
            "A5 là ví dụ về hiệu suất không đơn điệu: sâu 2 đạt 0,765, sâu 3 lại giảm còn 0,600, sâu 4–6 đều "
            "khoảng 0,81. Tăng độ sâu không bảo đảm mạnh hơn, vì hàm lượng giá và hiệu ứng chẵn/lẻ của điểm dừng "
            "có thể làm lệch đánh giá. Nhóm giữ độ sâu 5 theo cấu hình đã công bố, nhưng không tuyên bố đó là "
            "tối ưu."
        ),
    },
    {
        "kind": "content",
        "part": "PHẦN 4 · PHÂN TÍCH",
        "title": "Ablation A3: thêm dữ liệu, CNN mạnh lên thật",
        "layout": "image-full",
        "image": "deck_a3.png",
        "bullets": [
            "250 → 1.332 ván train: top-1 **47,19% → 57,08%** (+9,90 điểm phần trăm).",
            "Chặn cải thiện mạnh nhất: **52,99% → 77,64%**; thắng ngay **42,37% → 59,81%**.",
            "Một seed; top-1 không phải tỷ lệ thắng; nhãn vẫn đến từ chuyên gia sâu 5.",
        ],
        "time": 60,
        "notes": (
            "A3 là ablation quan trọng nhất của phần học có giám sát, vì nó trả lời trực tiếp: thêm dữ liệu có "
            "giúp không, hay mô hình đã bão hòa?\n\n"
            "Kết quả là có. Top-1 tăng từ 47,19% lên 57,08% khi số ván train tăng từ 250 lên 1.332. Điều đáng "
            "chú ý là mức tăng không đều: chặn tăng gần 25 điểm, thắng ngay tăng 17 điểm, trong khi kiểm soát "
            "trung tâm chỉ tăng khoảng 11 điểm. Nói cách khác, dữ liệu giúp mô hình học các tình huống có hậu "
            "quả rõ ràng trước.\n\n"
            "Nhưng phải đọc kèm ba hạn chế. Một, chỉ một seed cho mỗi mức, nên chưa tách được nhiễu huấn luyện. "
            "Hai, top-1 là khớp nhãn, không phải tỷ lệ thắng trước Alpha-Beta. Ba, nhãn do chuyên gia sâu 5 tạo "
            "ra, nên mô hình không thể giỏi hơn nhãn ở những thế chuyên gia sai. Đây là lý do nhóm không tuyên "
            "bố CNN \"học được chiến lược tối ưu\", mà chỉ nói nó học được tín hiệu từ dữ liệu."
        ),
    },
    {
        "kind": "content",
        "part": "PHẦN 4 · PHÂN TÍCH",
        "title": "Ablation A4: đổi lịch epsilon không cứu được DQN",
        "layout": "image-full",
        "image": "deck_a4.png",
        "bullets": [
            "3 mức decay × 3 seed × 10.000 episode: **không cấu hình nào vượt Heuristic** (0,137–0,162).",
            "Kéo dài khám phá không phải nút thắt; vấn đề nằm ở **phân phối ván huấn luyện**.",
            "Thêm 4 nước khai cuộc ngẫu nhiên: 0,162 → **0,425** trước Heuristic (một seed, chỉ là hướng sửa).",
        ],
        "time": 60,
        "notes": (
            "A4 là thí nghiệm về lịch giảm epsilon: ba mức nhanh, mặc định, chậm, mỗi mức ba seed, 10.000 episode. "
            "Kết quả khá dứt khoát: cả ba đều chỉ đạt khoảng 0,14 đến 0,16 trước Heuristic. Kéo dài khám phá "
            "không giúp gì đáng kể.\n\n"
            "Điều này gợi ý vấn đề không nằm ở epsilon. Nhóm thử một biến khác: thêm bốn nước khai cuộc ngẫu "
            "nhiên mỗi episode, để DQN gặp nhiều thế hơn thay vì lặp lại một đường. Kết quả nhảy từ 0,162 lên "
            "0,425 trước Heuristic, và 0,740 trước Random.\n\n"
            "Nhưng phải rất cẩn thận: đây chỉ là một seed, chạy sau khi đã thấy chẩn đoán, và không được dùng để "
            "chọn checkpoint giải đấu. Nó là bằng chứng định hướng, không phải kết quả đã kiểm chứng. Nhóm ghi "
            "rõ như vậy để tránh biến một thử nghiệm hậu kiểm thành tuyên bố chính thức."
        ),
    },
    {
        "kind": "content",
        "part": "PHẦN 4 · PHÂN TÍCH",
        "title": "Vì sao DQN yếu? Học thuộc một đường chơi",
        "layout": "image-right",
        "image": "deck_dqn_openings.png",
        "image_caption": "Cùng checkpoint, chỉ đổi số nước khai cuộc ngẫu nhiên trước khi DQN vào ván.",
        "bullets": [
            "Từ bàn trống, DQN thắng Heuristic **100–0**, nhưng chỉ **5/100 ván khác nhau** → gần như học thuộc một chuỗi.",
            "Thêm 2 nước ngẫu nhiên: 0,37; thêm 4 nước: **0,18** — score sụp khi phân phối đổi.",
            "A6 (10k episode, 3 seed): huấn luyện với Random → **0,010** trước Heuristic; tự chơi → **0,003**.",
            "Không phải lỗi mã: test mặt nạ cột, Bellman target và target network đều đạt.",
        ],
        "callout": "DQN học rất tốt một phân phối hẹp — và trả giá bằng khả năng tổng quát.",
        "time": 90,
        "notes": (
            "Đây là slide nhóm thích nhất vì nó biến một con số xấu thành một bài học rõ ràng.\n\n"
            "Nếu chỉ nhìn giải đấu, DQN 0,178 có vẻ như \"mô hình hỏng\". Nhưng chẩn đoán khai cuộc cho thấy "
            "nguyên nhân cụ thể. Từ bàn trống, DQN thắng Heuristic 100–0 — nghe rất giỏi. Nhưng trong 100 ván "
            "đó chỉ có 5 ván là khác nhau; 95 ván còn lại lặp lại gần như cùng một chuỗi. Nó đã học thuộc đường "
            "đi của một đối thủ xác định.\n\n"
            "Khi thêm hai nước ngẫu nhiên, score còn 0,37. Thêm bốn nước, còn 0,18. Với Random, mức giảm nhẹ hơn "
            "vì Random vốn đa dạng. Đây là hiện tượng quá khớp phân phối, không phải lỗi cài đặt: các test về "
            "mặt nạ cột, mục tiêu Bellman và target network đều đạt.\n\n"
            "A6 xác nhận thêm: trong cùng 10.000 episode, huấn luyện với Random hoặc tự chơi còn tệ hơn trước "
            "Heuristic — lần lượt 0,010 và 0,003. Tự chơi có tiến bộ so với chính nó (0,418 trước bản đóng băng), "
            "nhưng vẫn xa mức cần thiết. Kết luận: vấn đề là dữ liệu và phân phối, không phải vài siêu tham số."
        ),
    },
    {
        "kind": "content",
        "part": "PHẦN 4 · PHÂN TÍCH",
        "title": "Một ván thua của tác tử mạnh nhất",
        "layout": "two-images",
        "images": ["mcts_loss_before.png", "mcts_loss_after.png"],
        "captions": ["Trước: Random (đỏ) đã có ba quân cột 1–3; MCTS (vàng) chọn cột 0.", "Sau: Random thả cột 4 và thắng ngang cột 1–4."],
        "bullets": [
            "Trong 200 ván MCTS–Random, MCTS thắng 199 và thua đúng 1 ván — nhóm phân tích ván thua đó, không chọn ván thắng.",
            "MCTS vẫn có thể bỏ sót nước chặn ngay khi rollout ngẫu nhiên không đủ đại diện cho thế nguy hiểm.",
            "Bài học: điểm trung bình cao không thay thế được kiểm tra chiến thuật theo tình huống.",
        ],
        "time": 60,
        "notes": (
            "Nhóm chọn phân tích ván thua duy nhất của MCTS trong 200 ván đấu với Random, thay vì chọn một ván "
            "thắng đẹp.\n\n"
            "Thế trước khi sai: Random đã có ba quân đỏ ở hàng đáy cột 1, 2, 3. Chỉ cần thả cột 4 là thắng ngang. "
            "MCTS chọn cột 0. Vì sao? Với 1.000 mô phỏng, nếu các rollout ngẫu nhiên không thường xuyên đi vào "
            "cột 4, nhánh đó có thể bị đánh giá thấp. Random thả cột 4 và thắng.\n\n"
            "Điều này khớp với bộ 31 thế: MCTS chặn 97,5%, không phải 100%. Nó rất mạnh nhưng không bất bại. "
            "Bài học nhóm muốn nhấn mạnh: một tác tử có thể thắng 199/200 ván mà vẫn mắc lỗi chiến thuật cơ bản "
            "trong ván còn lại. Vì vậy đánh giá theo tình huống là cần thiết, không chỉ nhìn tỷ lệ thắng."
        ),
    },
    {
        "kind": "content",
        "part": "PHẦN 4 · PHÂN TÍCH",
        "title": "Thảo luận: lợi thế đi trước & giới hạn của kết quả",
        "layout": "bullets",
        "bullets": [
            "**Lợi thế đi trước:** 0,522 [0,504; 0,540] ở chế độ mặc định; 0,514 [0,488; 0,539] khi cùng thời gian.",
            "Lợi thế nhỏ nhưng có thật ở mặc định; ở chế độ cùng thời gian, khoảng tin cậy chứa 0,5 — chưa kết luận.",
            "**Vì sao tìm kiếm thắng:** dùng nhiều tính toán hơn (38 ms so với dưới 1 ms), không phải “miễn phí”.",
            "**Vì sao CNN tiệm cận Heuristic:** học từ chuyên gia mạnh, nhưng bị giới hạn bởi chính nhãn của chuyên gia.",
            "**Hạn chế:** một cohort khai cuộc · độ trễ phụ thuộc máy · CNN chủ yếu một seed · 31 thế là bộ nhỏ · chưa đo hiệu quả trên mỗi phép tính.",
        ],
        "callout": "Mọi kết luận chỉ đúng cho cấu hình, seed và máy đã ghi — nhóm không suy rộng ra ngoài phạm vi đã đo.",
        "time": 75,
        "notes": (
            "Phần này tổng hợp những gì kết quả cho phép nói và không cho phép nói.\n\n"
            "Về lợi thế đi trước: toàn giải đạt 0,522 cho bên đi trước, khoảng 0,504 đến 0,540. Đây là lợi thế nhỏ "
            "nhưng có ý nghĩa thống kê ở chế độ mặc định. Ở chế độ cùng thời gian, 0,514 với khoảng 0,488 đến "
            "0,539 — chứa 0,5, nên chưa kết luận. Điều này hợp lý vì khi hai bên bị ép cùng thời gian, khác biệt "
            "về độ sâu giảm đi.\n\n"
            "Về nguyên nhân thứ hạng: tìm kiếm thắng vì được tính nhiều hơn. Đây là lời giải thích có kiểm chứng "
            "một phần, không phải định luật. CNN tiệm cận Heuristic vì học từ chính chuyên gia đó; nó không thể "
            "vượt trần của nhãn.\n\n"
            "Về hạn chế: một cohort khai cuộc, độ trễ phụ thuộc máy, CNN chủ yếu một seed, bộ 31 thế nhỏ, và chưa "
            "có thí nghiệm cân bằng số phép tính. Những điều này không làm kết quả sai, nhưng giới hạn phạm vi "
            "kết luận. Nhóm ghi rõ để người đọc không suy rộng quá mức."
        ),
    },
    {
        "kind": "content",
        "part": "KẾT LUẬN",
        "title": "Đã làm được gì & đi tiếp thế nào",
        "layout": "bullets",
        "bullets": [
            "**Sản phẩm:** engine bitboard + engine tham chiếu, hai giao diện, sáu tác tử, giải đấu 4.500 ván, log truy vết, năm nhóm ablation.",
            "**RQ1:** MCTS và Alpha-Beta dẫn đầu; hòa ở mặc định, MCTS nhỉnh khi cùng 0,2 s/nước.",
            "**RQ2:** CNN học được tín hiệu (top-1 56,76%) và bám sát Heuristic, nhưng chưa vượt chuyên gia.",
            "**RQ3:** DQN thất bại vì quá khớp phân phối hẹp; đa dạng khai cuộc là hướng sửa có triển vọng.",
            "**RQ4:** học có giám sát ổn định hơn học tăng cường trong phạm vi dữ liệu của đồ án.",
            "**Hướng phát triển:** CNN lớn hơn / policy-value, DQN với khai cuộc ngẫu nhiên và self-play dài hơi, opening book, đo cùng số phép tính, hoàn thiện GUI.",
        ],
        "callout": "Bài học lớn nhất: tìm kiếm + lượng giá vẫn là xương sống; học máy chỉ mạnh khi dữ liệu đủ đa dạng.",
        "time": 60,
        "notes": (
            "Tóm lại, đồ án đã giao được một hệ thống chạy được từ đầu đến cuối: engine, giao diện, sáu tác tử, "
            "giải đấu và toàn bộ log. Điều nhóm tự hào nhất không phải một con số cao, mà là mọi con số đều truy "
            "ngược được và mọi tuyên bố đều có giới hạn rõ ràng.\n\n"
            "Bốn câu hỏi nghiên cứu đã được trả lời ở các mức độ khác nhau. RQ1 và RQ2 có kết quả khá chắc. RQ3 "
            "cho một kết quả âm tính nhưng rất có giá trị: DQN không hội tụ trong điều kiện huấn luyện hẹp. RQ4 "
            "chỉ so sánh được trong phạm vi đồ án, chưa đủ để nói họ học nào tốt hơn về lâu dài.\n\n"
            "Hướng đi tiếp rõ nhất là mở rộng dữ liệu và đa dạng hóa khai cuộc cho DQN, đồng thời thử một kiến "
            "trúc CNN lớn hơn hoặc mạng policy-value. Nếu có thêm thời gian, nhóm muốn chạy một chế độ cân bằng "
            "số phép tính để trả lời đúng câu \"hiệu quả trên mỗi phép tính\"."
        ),
    },
    {
        "kind": "closing",
        "title": "Cảm ơn thầy và các bạn",
        "subtitle": "Câu hỏi & thảo luận",
        "meta": [
            "Mã nguồn: github.com/…/Connect_Four",
            "Báo cáo & số liệu: docs/report · results/tables",
        ],
        "time": 30,
        "notes": (
            "Nhóm xin cảm ơn thầy và các bạn đã lắng nghe. Phần trình bày đến đây là hết.\n\n"
            "Nhóm sẵn sàng nhận câu hỏi về ba chỗ dễ bị chất vấn nhất: thứ nhất, vì sao DQN yếu — câu trả lời "
            "nằm ở chẩn đoán khai cuộc và A6; thứ hai, vì sao không kết luận MCTS mạnh hơn Alpha-Beta — vì khoảng "
            "tin cậy ở chế độ mặc định chứa 0,5; thứ ba, vì sao CNN không vượt Heuristic — vì nhãn do chính "
            "Alpha-Beta tạo ra và dữ liệu còn ít.\n\n"
            "Nếu thầy muốn xem demo, nhóm có thể mở giao diện Pygame hoặc chạy một ván terminal ngay tại lớp."
        ),
    },
]
