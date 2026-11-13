# Bo vi tri kiem thu thu cong

`positions.csv` gom 31 the co, dung lam test hoi quy cho engine va Heuristic.
`test_positions.py` doc tung dong va doi chieu `winning_moves` cung
`blocking_moves` tren ca engine bitboard va `ReferenceGame`.

| Nhom | Vi du | Kiem tra |
|---|---|---|
| Thang doc | 3 quan chong cung cot | `winning_moves` tra dung cot |
| Thang ngang | 3 quan lien tiep hang day | thang o ca 2 dau |
| Thang cheo len | duong cheo `/` | dung khi chi con 1 cot |
| Thang cheo xuong | duong cheo `\` | |
| Chan | doi thu sap thang | `blocking_moves` tra dung |
| Don dep | doi thu co 2 de doa cung luc | phai chan, khong thang duoc |
| Hoa | ban co day khong ai thang | `is_terminal` True, `winner` None |
| Cot day | cot da day trong van chua ket thuc | khong con la nuoc hop le |

Quy uoc cot: `0` la cot trai nhat, `6` la cot phai nhat. Hang `0` la hang duoi cung.
