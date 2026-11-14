# 4.1. Ket qua da thuc hien

Phan nay chi ghi so lieu co log nguon. Tai thoi diem cap nhat, nhom moi co mot
pilot Heuristic--Random; chua co co so de ket luan ve Alpha-Beta, MCTS, NN hoac
DQN.

## Pilot Heuristic--Random

| Chi so | Gia tri | Nguon |
| --- | ---: | --- |
| So van | 200 | `results/logs/games_k1-heuristic-random-20261109T061032Z-s0.csv` |
| Heuristic thang | 198 | cung file, `winner=a` |
| Hoa | 0 | cung file, `winner=draw` |
| Heuristic thua | 2 | cung file, `winner=b` |
| Score | 0.99 | `(198 + 0.5 * 0) / 200` |
| Thoi gian trung binh Heuristic | 0.2254 ms/nuoc | `moves_...csv`, `agent=heuristic` |
| P95 Heuristic | 0.3323 ms/nuoc | `moves_...csv`, `agent=heuristic` |

Thiet ke pilot dung 100 khai cuoc, moi khai cuoc choi hai lan va doi ben.
Ket qua nay chi xac nhan pipeline log va mot moc so sanh ban dau; khong chung
minh Heuristic dat 99% truoc moi seed hoac moi tac tu manh hon.

## Nhung ket qua chua duoc bao cao

Chua co log hop le cho giai dau day du, ablation, huan luyen NN/DQN hoac danh
gia bang solver tren tap lon. Cac muc nay phai duoc chay va ghi `run_id` truoc
khi dua vao bang ket qua hoac ket luan.
