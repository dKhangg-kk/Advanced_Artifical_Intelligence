# Slide deck - Connect Four AI

Day la noi dung slide toi thieu dua tren so lieu da kiem chung. Khi co them
log, cac slide ket qua phai duoc sinh lai tu `results/tables/report_numbers.csv`.

## Slide 1 - De tai

Connect Four 7x6: engine, tac tu heuristic va danh gia doi khang.

## Slide 2 - Mo hinh game

- Hai nguoi choi, thong tin day du, tat dinh, tong bang khong.
- Hanh dong la cot 0-6; quan roi xuong o trong thap nhat.
- Ket thuc khi co chuoi bon hoac ban day.

## Slide 3 - Cac thanh phan da co

- Bitboard engine va reference engine.
- Random, Heuristic, Alpha-Beta, MCTS.
- ExactSolver dung lam thuoc do cho vi tri nho/tan cuoc.
- Test cheo engine va test agent.

## Slide 4 - Pilot that

Heuristic dau Random: 200 van, 198 thang, 0 hoa, 2 thua, score 0.99.
Thoi gian Heuristic trung binh 0.2254 ms/nuoc; P95 la 0.3323 ms/nuoc.

## Slide 5 - Dien giai than trong

Day la pilot mot cap dau va mot thiet lap seed. Chua duoc dung de xep hang
toan bo tac tu hoac ket luan ve NN/DQN.

## Slide 6 - Viec con lai

MCTS tournament, NN/DQN checkpoint, ablation, thong ke CI, demo GUI va tai lap
tren may sach.
