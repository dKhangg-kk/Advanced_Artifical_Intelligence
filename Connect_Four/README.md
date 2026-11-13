# Connect Four AI

[← Về README môn học](../README.md)

Đồ án cuối kỳ học phần **Trí tuệ nhân tạo nâng cao**, thực hiện bởi nhóm 4 sinh viên. Phạm vi dự án gồm trò chơi Connect Four cùng **6 tác tử AI cấp 1–6**, giao diện người–máy/máy–máy và hệ thống đánh giá đối kháng.

**Trạng thái: Đang phát triển.**

### Trạng thái đã kiểm chứng (13/11/2026)

- Engine bitboard và `ReferenceGame` đã có kiểm thử chéo.
- Random, Heuristic, Alpha-Beta và MCTS có test tự động.
- Heuristic đã xử lý đúng vị trí có hai đe dọa thắng: đây là thế thua bắt buộc,
  không được mô tả là chặn thành công.
- Đã bổ sung `connect_four.solver.ExactSolver` để đo vị trí nhỏ/tàn cuộc; solver
  dùng negamax, alpha-beta và bảng chuyển vị, không tham gia giải đấu.
- Pilot thật hiện có: 200 ván, 198 thắng, 0 hòa, 2 thua, score 0,99. Nguồn:
  `k1-heuristic-random-20261109T061032Z-s0` trong `results/logs/`.
- MCTS tournament, NN/DQN training, checkpoint và giải đấu toàn bộ tác tử vẫn
  chưa được xác nhận hoàn thành; không dùng chúng làm kết quả trong báo cáo.

Alpha-Beta K2: xem [cách hoạt động, ngân sách và kiểm thử](docs/ALPHABETA.md).

MCTS-UCT K3: xem [bốn bước, ngân sách và cách kiểm tra](docs/MCTS.md).

## Mục lục

- [Mục tiêu](#mục-tiêu)
- [Luật chơi](#luật-chơi)
- [Phạm vi dự án](#phạm-vi-dự-án)
- [Huấn luyện cấp 5 và cấp 6](#huấn-luyện-cấp-5-và-cấp-6)
- [Chức năng](#chức-năng)
- [Công nghệ sử dụng](#công-nghệ-sử-dụng)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Hướng dẫn chạy](#hướng-dẫn-chạy)
- [Thiết kế thực nghiệm](#thiết-kế-thực-nghiệm)
- [Thành viên và phối hợp](#thành-viên-và-phối-hợp)
- [Sản phẩm bàn giao](#sản-phẩm-bàn-giao)
- [Tài liệu tham khảo](#tài-liệu-tham-khảo)

## Mục tiêu

- Xây dựng engine đúng luật, có API thống nhất và kiểm thử tự động.
- Triển khai Random, Heuristic, Minimax/Alpha-Beta và MCTS.
- Huấn luyện thực tế cả mạng học có giám sát ở cấp 5 và tác tử học tăng cường ở cấp 6.
- So sánh sức mạnh thi đấu với thời gian suy luận và chi phí huấn luyện.
- Cung cấp demo chơi được và lưu đủ mã, cấu hình, checkpoint, log để chạy lại thực nghiệm.

Hai câu hỏi nghiên cứu chính:

1. Trong cùng thời gian suy nghĩ mỗi nước, Alpha-Beta và MCTS khác nhau thế nào về điểm đối kháng và độ trễ?
2. Neural Network học từ Alpha-Beta và tác tử RL đạt sức mạnh, tốc độ suy luận và chi phí huấn luyện ở mức nào so với các tác tử đối chứng?

## Luật chơi

- Bàn tiêu chuẩn có **7 cột × 6 hàng**, dành cho 2 người chơi luân phiên.
- Mỗi lượt, người chơi thả một quân vào cột chưa đầy. Quân nằm ở ô trống thấp nhất của cột.
- Người đầu tiên tạo được **4 quân cùng màu liên tiếp** theo hàng ngang, dọc hoặc chéo thắng.
- Bàn đầy mà chưa có người thắng thì hòa. Ván kết thúc ngay khi xác định thắng hoặc hòa.
- Không chấp nhận cột đầy, chỉ số cột sai hoặc nước đi sau khi ván đã kết thúc.

Quy ước biểu diễn: hành động là chỉ số cột `0–6`; trạng thái gồm bàn cờ, người đến lượt và thông tin kết thúc. Trò chơi có thông tin đầy đủ, tính xác định và có thể mô hình hóa dưới dạng tổng bằng không.

Giao diện engine được thống nhất gồm `reset()`, `legal_actions()`, `step(action)`, `is_terminal()`, `result()`, `render()` và `clone()` hoặc `undo()`.

## Phạm vi dự án

Phạm vi dự án bao gồm đầy đủ sáu cấp dưới đây.

| Cấp | Tác tử | Phương pháp |
| --- | --- | --- |
| 1 | Random | Chọn đều trong các cột hợp lệ, dùng làm mốc đối chứng. |
| 2 | Rule-based / Heuristic | Ưu tiên thắng ngay, chặn đối thủ rồi đánh giá chuỗi quân và vị trí; công bố thứ tự ưu tiên. |
| 3 | Minimax / Alpha-Beta | Tìm kiếm giới hạn độ sâu, dùng hàm lượng giá; đối chiếu số nút và thời gian khi bật/tắt cắt tỉa. |
| 4 | MCTS với UCT | Chọn nút, mở rộng, mô phỏng và cập nhật kết quả; khảo sát ngân sách mô phỏng. |
| 5 | Neural Network | Học có giám sát để dự đoán nước đi từ nhãn Alpha-Beta. |
| 6 | Deep Q-Network (DQN) | Học giá trị hành động Q(s, a) qua tương tác (Replay Buffer, Target Network, Epsilon-Greedy). |

**Cấp 1–6 thuộc phạm vi chính.** Kết hợp mạng với MCTS hoặc thực hiện các cấp cảm hứng AlphaGo/AlphaZero là hướng mở rộng sau khi hoàn thành phần chính. Cấp phương pháp cao hơn không mặc nhiên bảo đảm tác tử chơi mạnh hơn.

## Huấn luyện cấp 5 và cấp 6

### Cấp 5 — Học có giám sát

- Sinh các ván hợp lệ, dùng Alpha-Beta có cấu hình công bố rõ để tạo nhãn nước đi.
- Mạng policy nhận trạng thái và người đến lượt, dự đoán hành động trên 7 cột.
- Chia train/validation/test **theo ván** với tỷ lệ khởi đầu `70/15/15`; kiểm soát trạng thái trùng giữa các tập và ghi lại tỷ lệ thực tế sau lọc.
- Chỉ tăng cường đối xứng trong train; khi lật gương bàn phải đổi nhãn cột tương ứng.
- Chọn checkpoint bằng validation; báo cáo loss, kết quả test và sức mạnh đối đầu.

Nhãn từ Alpha-Beta giới hạn độ sâu phản ánh tác tử tạo nhãn, không được mặc định là nước tối ưu toán học.

### Cấp 6 — Học tăng cường (DQN)

- Khởi tạo mạng Q-Network riêng và huấn luyện bằng **Deep Q-Network (DQN)**.
- Mỗi episode là một ván. Thưởng cuối ván theo góc nhìn tác tử đang học: **thắng `+1`, hòa `0`, thua `−1`**.
- Sử dụng **Replay Buffer** (tối đa 100.000 transition) lưu `(s, a, r, s', done)` để phá vỡ tương quan giữa các mẫu liên tiếp.
- Sử dụng **Target Network** đồng bộ định kỳ sau mỗi `C` bước để ổn định quá trình tối ưu hàm mục tiêu Bellman:
  $$y = r + \gamma \max_{a' \in \text{legal}} Q_{\text{target}}(s', a')$$
- Lịch trình khám phá **$\epsilon$-Greedy** suy giảm dần từ `1.0` về `0.05`. Khi thi đấu hoặc đánh giá, $\epsilon = 0.0$ (hoàn toàn tham lam trên các cột hợp lệ).
- Bắt đầu đối đầu với Random/Heuristic cố định; sau đó mở rộng sang self-play. Chỉ cập nhật tác tử đang học.
- Đánh giá độc lập các checkpoint tại các mốc `1.000`, `2.500`, `5.000` và `10.000` episodes với seed cố định.
- Lưu số episode, loss Bellman, phần thưởng trung bình, tỷ lệ thắng trước baseline và đường cong hội tụ.

Hai cấp có thể dùng chung kiến trúc nhưng phải có **trọng số, checkpoint và log huấn luyện riêng**. Khi chọn nước, cả hai phải loại cột đầy. Không dùng mạng chưa huấn luyện để minh chứng hoàn thành cấp 5 hoặc 6; không dùng bộ đánh giá cuối để chọn mô hình hoặc siêu tham số.

## Chức năng

| Chức năng | Nội dung |
| --- | --- |
| Quản lý ván chơi | Khởi tạo bàn, kiểm tra nước đi, cập nhật lượt và xác định kết quả. |
| Chọn tác tử | Chọn một trong 6 tác tử và cấu hình tìm kiếm hoặc checkpoint. |
| Demo | Người đấu máy và máy đấu máy; hiển thị bàn, lượt, kết quả và thời gian mỗi nước. |
| Huấn luyện | Sinh dữ liệu cấp 5, huấn luyện NN/RL, lưu checkpoint và lịch sử học. |
| Đánh giá tự động | Đấu vòng tròn, ghi log và tổng hợp bảng/biểu đồ. |

## Công nghệ sử dụng

Các công cụ nhóm đã thống nhất cho việc triển khai:

| Công cụ | Vai trò |
| --- | --- |
| Python, NumPy | Engine, xử lý trạng thái và các thuật toán. |
| Pygame | Giao diện chơi và demo trên máy cá nhân. |
| PyTorch | Huấn luyện và suy luận cho NN/RL. |
| pytest | Kiểm thử luật, trạng thái và hành động hợp lệ. |
| pandas, Matplotlib | Phân tích log, ma trận đối đầu và đường cong học. |
| GitHub | Quản lý mã nguồn, phân công và lịch sử đóng góp. |
| Google Colab, tùy chọn | Hỗ trợ notebook huấn luyện khi cần tài nguyên bổ sung. |

Máy cá nhân là môi trường chính cho phát triển, demo và đánh giá. Nếu huấn luyện trên Colab, cần lưu checkpoint ra nơi bền vững và công bố phần cứng thực dùng. Các tác tử trong cùng phép so sánh phải chạy trong điều kiện phần cứng được kiểm soát.

Phiên bản Python và thư viện phải được ghi trong cấu hình môi trường để bảo đảm các thành viên có thể cài đặt và chạy lại cùng thiết lập.

## Cấu trúc dự án

Đồ án nằm trong thư mục `Connect_Four/` của repo môn học. Khung dưới đây đã được tạo sẵn; các tệp thuật toán sẽ được điền dần theo [lộ trình](docs/ROADMAP.md).

```text
Connect_Four/
├── README.md
├── CONTRIBUTING.md           # Quy ước nhánh, commit, PR và code
├── requirements.txt          # Thư viện và phiên bản
├── pyproject.toml            # Khai báo gói, entry point, cấu hình pytest
├── configs/                  # Cấu hình tác tử, giải đấu và ablation
│   ├── agents.yaml
│   ├── tournament_default.yaml
│   ├── tournament_timed.yaml
│   ├── ablation_a1_pruning.yaml
│   ├── ablation_a2_mcts_budget.yaml
│   ├── ablation_a3_cnn_data.yaml
│   ├── ablation_a4_dqn_training.yaml
│   └── ablation_a5_depth.yaml
├── src/
│   └── connect_four/
│       ├── game/             # constants, base (hợp đồng API), engine, reference
│       ├── agents/           # base, networks (PyTorch), và sáu tác tử (cấp 1–6)
│       │   ├── base.py
│       │   ├── networks.py   # Kiến trúc CNN Policy và DQN Net
│       │   ├── random_agent.py
│       │   ├── heuristic.py
│       │   ├── alphabeta.py
│       │   ├── mcts.py
│       │   ├── nn_agent.py
│       │   └── dqn.py
│       ├── ui/               # Demo Pygame
│       ├── training/         # Sinh nhãn, huấn luyện CNN (cấp 5) và DQN (cấp 6)
│       │   ├── gen_data.py
│       │   ├── train_supervised.py
│       │   └── train_dqn.py
│       ├── evaluation/       # Runner giải đấu, độ đo, runlog và CLI
│       └── play.py           # Chơi trong terminal
├── tests/                    # Test khung, kế hoạch test và bộ vị trí kiểm thử
├── notebooks/                # Phân tích, biểu đồ và notebook huấn luyện
├── data/                     # raw/ (dữ liệu chuyên gia thô) và processed/ (train/val/test)
├── checkpoints/              # Chỉ commit level5_cnn/final.pt và level6_dqn/final.pt
├── results/                  # logs/ (manifest, games, moves, train), tables/, figures/
└── docs/                     # proposal/, ROADMAP, THIRD_PARTY, LOGGING, EXPERIMENT_LOG, report/, slides/, poster/
```

Dữ liệu và checkpoint lớn cần có hướng dẫn tải hoặc tái tạo nếu không lưu trực tiếp trong Git. Hai checkpoint cuối được phép commit theo [quy ước checkpoint](checkpoints/README.md); trọng số trung gian vẫn bị bỏ qua. Mô tả dữ liệu, cấu hình, seed và cách chạy lại vẫn phải được cung cấp. Quy tắc bỏ qua tệp nằm ở `.gitignore` gốc repo và `Connect_Four/.gitignore`; cần kiểm tra để không bỏ qua nhầm các log hoặc kết quả cần nộp.

## Hướng dẫn chạy

**Trạng thái:** đã có engine bitboard và bản tham chiếu, Random, Heuristic,
Alpha-Beta, MCTS, solver đo và bộ kiểm thử. NN/DQN training, checkpoint và giải
đấu đầy đủ vẫn chưa hoàn thành; xem [lộ trình](docs/ROADMAP.md).

Đánh giá K1 không cần CLI giải đấu: chạy `PYTHONPATH=src python scripts/evaluate_k1.py`
từ thư mục `Connect_Four/`. Cấu hình cố định trong `configs/k1_random_heuristic.json`;
200 ván dùng 100 khai cuộc và đổi bên theo cặp. Heuristic thắng 198/200 ván (99%)
ở seed khai cuộc/Heuristic = 0, Random = 1; xem [log và điều kiện chạy](docs/EXPERIMENT_LOG.md).

### Cài đặt

```bash
cd Connect_Four
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .                 # tùy chọn: tạo lệnh c4-play, c4-tournament
```

### Cài đặt sạch trên Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pytest -q
```

Nếu chỉ cần engine và test lõi, `requirements.txt` là đủ. PyTorch, Pygame và
các gói phân tích là phần tùy chọn; cài thêm theo mục
`[project.optional-dependencies]` trong `pyproject.toml` khi chạy NN/DQN, GUI
hoặc tổng hợp biểu đồ.

### Solver đo chất lượng nước đi

```python
from connect_four.game import ConnectFour
from connect_four.solver import ExactSolver

game = ConnectFour()
solver = ExactSolver()
value = solver.solve(game)       # 1, 0 hoặc -1 theo bên sắp đi
best = solver.best_moves(game)    # tất cả nước đi tối ưu
```

Solver có chi phí tăng rất nhanh ở khai cuộc. Chỉ dùng nó cho vị trí đã giới
hạn/tàn cuộc hoặc tập mẫu có ngân sách; không tuyên bố toàn bộ bàn cờ đã được
giải nếu chưa có log chứng minh.

### Kiểm thử

```bash
pytest -q                        # các test khung phải xanh
```

### Các lệnh dự kiến

Các lệnh lõi dưới đây đã có implementation. NN/DQN chỉ chạy được khi có
checkpoint hợp lệ; GUI cần cài thêm Pygame.

| Lệnh | Mục đích | Trạng thái |
| --- | --- | --- |
| `python -m connect_four.play --opponent heuristic` | Chơi người–máy trong terminal | Đã có; cần chạy tương tác |
| `python -m connect_four.evaluation.cli --a random --b heuristic --out results/logs/r_vs_h.csv` | Chạy một cặp đấu, ghi log CSV | Đã có; nên smoke-test trước |
| `python -m connect_four.ui.gui` | Demo Pygame | Đã có; cần Pygame/display |

Chỉ các lệnh đã chạy kiểm tra thực tế mới được chuyển sang trạng thái "đã kiểm chứng".

## Thiết kế thực nghiệm

### Giải đấu

- Đấu vòng tròn giữa **6 tác tử**, tương ứng **15 cặp**.
- Mỗi chế độ có tối thiểu **100 ván/cặp**, mục tiêu **200 ván/cặp**; chia đều đi trước/đi sau.
- Dùng nhiều seed cho phương pháp có tính ngẫu nhiên, công bố cách phân bổ ván.
- Chạy ít nhất hai chế độ: **cùng trần thời gian mỗi nước** và **cấu hình mặc định minh bạch**.
- Với mục tiêu 200 ván/cặp, mỗi chế độ có **3.000 ván**; hai chế độ có **6.000 ván**, chưa gồm khảo sát bổ sung.
- Giữ cố định luật, phiên bản mã, phần cứng và thiết bị suy luận; công bố cách xử lý nước sai hoặc quá thời gian. Không suy diễn công bằng tính toán chỉ từ cùng độ sâu tìm kiếm.

### Các chỉ số

- Số lượng và tỷ lệ thắng/hòa/thua.
- `score = (số thắng + 0.5 × số hòa) / tổng số ván`.
- Thời gian trung bình và p95 mỗi nước.
- Số nút duyệt hoặc số mô phỏng; RAM/VRAM khi phù hợp.
- Thời gian huấn luyện, loss của NN, reward và điểm đối kháng theo episode của RL.
- Ma trận đối đầu, khoảng tin cậy và kết quả tách theo bên đi trước/đi sau.

### Hai khảo sát chính

1. **Alpha-Beta bật/tắt cắt tỉa:** giữ cùng trạng thái, độ sâu, hàm lượng giá và thứ tự nước; so sánh kết quả tìm kiếm, số nút và thời gian.
2. **Ngân sách MCTS:** thay số mô phỏng trong khi cố định đối thủ, chính sách rollout và cách sử dụng seed; đo thay đổi score và độ trễ.

Phân tích thêm ảnh hưởng seed, độ sâu, lượt đi trước và những thế cờ tác tử mắc lỗi. Với cặp tác tử tất định, không coi các ván lặp y hệt là mẫu độc lập để làm hẹp khoảng tin cậy.

### Lưu trữ để tái lập

Mỗi đợt chạy cần lưu phiên bản mã/commit, luật, cấu hình, seed, phần cứng và checkpoint sử dụng. Log ván gồm đối thủ, bên đi trước, chuỗi nước và kết quả; log từng nước có thời gian cùng số nút hoặc mô phỏng khi áp dụng. Notebook phải tạo lại được bảng/hình từ log thô. Quy ước log và cách truy vết từng con số nằm trong [`docs/LOGGING.md`](docs/LOGGING.md); nhật ký từng lần chạy nằm trong [`docs/EXPERIMENT_LOG.md`](docs/EXPERIMENT_LOG.md).

**Kết quả thực nghiệm hiện có:** chỉ pilot Heuristic–Random 200 ván; xem
[`docs/report/04a_ket_qua.md`](docs/report/04a_ket_qua.md). Các bảng xếp hạng
toàn bộ tác tử và kết luận về NN/DQN chỉ được bổ sung sau khi chạy thực tế.

## Thành viên và phối hợp

| Thành viên | Mã sinh viên |
| --- | --- |
| Phan Lê Ngọc Như Ý | 3124720079 |
| Bùi Quyền Kiệt | 3124720036 |
| Phạm Thái Duy Khang | 3124720033 |
| Bùi Anh Đức | 3124720016 |

Nhóm thống nhất người phụ trách các mảng engine/UI, tác tử tìm kiếm, MCTS/giải đấu và NN/RL. Phần RL cần phối hợp giữa người phụ trách vòng lặp đối đầu và người phụ trách mạng, huấn luyện. Bảng phân công theo tên và tỷ lệ đóng góp sẽ cập nhật theo công việc thực tế.

Mỗi công việc nên được ghi thành issue, thực hiện trên nhánh riêng và review qua pull request trước khi gộp vào `main`. Mỗi thành viên dùng tài khoản của mình để lưu lịch sử đóng góp.

Commit của đồ án theo quy ước chung `TuanXX/DuAn/Noi dung cong viec`, ví dụ `Tuan04/DuAn/Cai dat kiem tra thang Connect Four`; số tuần phản ánh tuần học thực tế.

## Sản phẩm bàn giao

- Demo cho phép chọn tác tử và chơi người–máy/máy–máy.
- Mã nguồn Python, cấu hình, yêu cầu thư viện, test tự động và hướng dẫn cài đặt/train/evaluate/demo.
- Thông tin dữ liệu NN; checkpoint riêng của cấp 5 và 6; log và đường cong huấn luyện.
- Log thi đấu thô, notebook tạo bảng/hình, ma trận đối đầu và phân tích.
- Nhật ký thực nghiệm `docs/EXPERIMENT_LOG.md`, quy ước log `docs/LOGGING.md` và bảng truy vết số liệu `results/tables/report_numbers.csv`.
- Báo cáo, slide, poster; liên kết GitHub, lịch sử commit, phân công và tỷ lệ đóng góp.
- Tệp ZIP đặt tên theo quy định: `NhomXX_TenGame_TTNTNC_HoTen_MaSV.zip`.

Nguồn sách, thư viện, công cụ AI và mã tham khảo phải được trích dẫn; phân biệt phần tự cài đặt với phần kế thừa. Không báo cáo training/benchmark chưa chạy hoặc chỉ chọn ván thắng để minh họa kết luận tổng thể.

## Tài liệu tham khảo

1. Đề tài cuối kỳ môn Trí tuệ nhân tạo nâng cao, chủ đề *Xây dựng và đánh giá Game AI đa cấp độ*.
2. Tài liệu học phần về tìm kiếm có đối thủ, Minimax, Alpha-Beta và MCTS.
3. Mark Liu (2025). *Rule-Based AI*, Phần I, chương 1–8, trích từ *AlphaGo Simplified: Rule-Based AI and Deep Learning in Everyday Games*. CRC Press. Bản trích nhóm sử dụng: `Liu - Rule-Based AI Games.pdf`.
4. Mark Liu (2025). *AlphaGo Simplified: Rule-Based AI and Deep Learning in Everyday Games*. CRC Press. [DOI: 10.1201/9781032722207](https://doi.org/10.1201/9781032722207).
5. Stuart J. Russell và Peter Norvig (2022). *Artificial Intelligence: A Modern Approach*, Fourth Edition, Global Edition. Pearson Education Limited.

Thông tin năm và ấn bản theo các bản sách nhóm đang sử dụng. Các nguồn mã và thư viện cụ thể sẽ được bổ sung khi triển khai.
