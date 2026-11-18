# 4.1. Ket qua da thuc hien

Phan nay trinh bay rieng pilot Heuristic--Random co log nguon. Ket qua
A1/A2/A5 nam o [ablation tim kiem](04d_ablation_tim_kiem.md), CNN o
[A3](04e_ablation_cnn.md), DQN pilot o [muc 3.5–3.6](03d_dqn_giai_dau.md).
Khong dung pilot mot cap de xep hang toan bo tac tu.

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

Chua co giai dau day du sau tac tu o hai che do hay danh gia solver tren tap
lon. Da co A1/A2/A3/A5, log CNN va DQN pilot nhu cac muc duoc dan o tren;
cac ket qua do khong thay the giai dau day du hoac A4. Moi ket luan phai
gioi han theo dung cau hinh va log da chay.
