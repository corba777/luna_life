| seed | arm | k (k_H for KH) | n distinct example inputs | g1 solo share | g1 largest-false share | modal rule at g10 (+ n_ops) | modal share g10 | J g10 | J mean | first gen P_e modal (or never) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | K2 | 2 | 92 | 0.29 | 0.68 | shift_symbols(1);swap(2,3) (2-op) | 1.00 | 1.00 | 0.84 | 3 |
| 2 | K2 | 2 | 100 | 0.25 | 0.22 | rotate_left(1);swap(0,3) (2-op) | 0.98 | 0.98 | 0.81 | 1 |
| 3 | K2 | 2 | 96 | 0.47 | 0.39 | shift_symbols(6);swap(1,3) (2-op) | 0.99 | 0.99 | 0.91 | 1 |
| 4 | K2 | 2 | 99 | 0.19 | 0.23 | reverse;shift_symbols(6) (2-op) | 1.00 | 1.00 | 0.66 | 3 |
| 5 | K2 | 2 | 89 | 0.47 | 0.46 | shift_symbols(1);swap(0,3) (2-op) | 1.00 | 1.00 | 0.91 | 1 |
| 1 | K4 | 4 | 68 | 0.12 | 0.88 | shift_symbols(1);swap(2,3) (2-op) | 1.00 | 1.00 | 0.67 | 4 |
| 2 | K4 | 4 | 78 | 0.00 | 0.33 | rotate_left(1);swap(0,3) (2-op) | 0.90 | 0.90 | 0.36 | 5 |
| 3 | K4 | 4 | 77 | 0.08 | 0.85 | shift_symbols(6);swap(1,3) (2-op) | 1.00 | 1.00 | 0.54 | 6 |
| 4 | K4 | 4 | 54 | 0.01 | 0.82 | reverse;shift_symbols(6) (2-op) | 0.83 | 0.83 | 0.39 | 7 |
| 5 | K4 | 4 | 76 | 0.00 | 1.00 | shift_symbols(1);swap(0,3) (2-op) | 0.57 | 0.57 | 0.21 | 10 |
| 1 | KH | 11 (k_H=11) | 8 | 0.00 | 1.00 | shift_symbols(1) (1-op) | 0.61 | 0.10 | 0.03 | never |
| 2 | KH | 24 (k_H=24) | 8 | 0.00 | 0.68 | swap(1,3) (1-op) | 0.52 | 0.00 | 0.00 | never |
| 3 | KH | 11 (k_H=11) | 8 | 0.00 | 1.00 | shift_symbols(6);swap(1,3) (2-op) | 0.43 | 0.43 | 0.13 | 10 |
| 4 | KH | 11 (k_H=11) | 8 | 0.00 | 0.98 | shift_symbols(6) (1-op) | 0.53 | 0.00 | 0.00 | never |
| 5 | KH | 11 (k_H=11) | 8 | 0.00 | 1.00 | shift_symbols(1);swap(0,3) (2-op) | 0.50 | 0.50 | 0.16 | 10 |
| 1 | KHs | 11 (k_H=11) | 8 | 0.00 | 1.00 | shift_symbols(1) (1-op) | 0.99 | 0.00 | 0.00 | never |
| 2 | KHs | 24 (k_H=24) | 8 | 0.00 | 0.61 | reverse;reverse (2-op) | 0.66 | 0.01 | 0.00 | never |
| 3 | KHs | 11 (k_H=11) | 8 | 0.00 | 0.98 | shift_symbols(6) (1-op) | 1.00 | 0.00 | 0.00 | never |
| 4 | KHs | 11 (k_H=11) | 8 | 0.00 | 1.00 | shift_symbols(6) (1-op) | 1.00 | 0.00 | 0.00 | never |
| 5 | KHs | 11 (k_H=11) | 8 | 0.00 | 0.99 | shift_symbols(1) (1-op) | 0.99 | 0.00 | 0.00 | never |
