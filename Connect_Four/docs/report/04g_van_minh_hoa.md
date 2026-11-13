# 4.6. Minh hoa van co va phan tich that bai

Phan nay chi dung cac van co co trong log that. Run duoc dung la
`k1-heuristic-random-20261109T061032Z-s0`; day la pilot Heuristic--Random,
khong phai giai dau day du cua do an.

## Van dau tien cua run

| run_id | game_id | cap dau | ket qua | chuoi nuoc |
| --- | --- | --- | --- | --- |
| `k1-heuristic-random-20261109T061032Z-s0` | `heuristic_vs_random-g000` | Heuristic vs Random | Heuristic thang | `6 3 6 3 6 1 6` |

Van ket thuc sau 7 nuoc. Nhat ky chi tiet tung nuoc nam trong
`results/logs/moves_k1-heuristic-random-20261109T061032Z-s0.csv`.

## Hai van Heuristic thua

| game_id | ben di truoc | chuoi nuoc | so nuoc |
| --- | ---: | --- | ---: |
| `heuristic_vs_random-g069` | Random | `4 5 3 6 0 2 6 3 4 4 6 5 6 5 6` | 15 |
| `heuristic_vs_random-g159` | Random | `1 1 5 3 4 3 3 4 0 2 2 5 1 6 6 3 4 2 6 5 4` | 21 |

Hai van nay duoc giu lai de phan tich that bai, khong chi chon van thang.
Tuy nhien, log hien tai chua co solver chay tren tung ply, nen khong duoc ket
luan nguyen nhan chien thuat cua hai van nay.

## Gioi han

Pilot co 200 van, 100 khai cuoc va doi ben. Chua co du lieu de phan tich loi
Alpha-Beta, MCTS, NN hoac DQN; cac phan do chi duoc them sau khi co run log
tuong ung.
