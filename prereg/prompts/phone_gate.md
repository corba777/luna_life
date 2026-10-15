# Phone gate — dry renders (inbox blocks at g2)

**PHONE_SEED** `20261016`. World seed `1`. P_e `shift_symbols(1);swap(2,3)`.
No Alls arm. Template body matches Ca-r / Da-r; only the inbox block differs.

## Assertions

- R8 cell 1 draw (repro): `[60, 91, 19, 47, 34, 56, 28, 8]` (len=8, no self)
- All inboxes: count of publishing others (sources always publish P_e)

## R8 — inbox blocks at g2

### cell 1

slots=8, nonempty=7, distinct=4

```
Visible messages (8 slots):
  1. empty
  2. sender=91 generation=0 signal=0 say='shift_symbols(1)'
  3. sender=19 generation=0 signal=0 say='shift_symbols(6)'
  4. sender=47 generation=0 signal=0 say='shift_symbols(6)'
  5. sender=34 generation=0 signal=0 say='shift_symbols(7)'
  6. sender=56 generation=0 signal=0 say='shift_symbols(1)'
  7. sender=28 generation=0 signal=0 say='shift_symbols(1)'
  8. sender=8 generation=0 signal=0 say='shift_symbols(2)'
```

### cell 2

slots=8, nonempty=5, distinct=4

```
Visible messages (8 slots):
  1. empty
  2. sender=29 generation=0 signal=0 say='shift_symbols(2)'
  3. sender=98 generation=0 signal=0 say='shift_symbols(1)'
  4. empty
  5. empty
  6. sender=70 generation=0 signal=0 say='shift_symbols(1)'
  7. sender=32 generation=0 signal=0 say='shift_symbols(5)'
  8. sender=34 generation=0 signal=0 say='shift_symbols(7)'
```

### cell 4

slots=8, nonempty=6, distinct=3

```
Visible messages (8 slots):
  1. sender=31 generation=0 signal=0 say='shift_symbols(4)'
  2. empty
  3. empty
  4. sender=77 generation=0 signal=0 say='shift_symbols(1)'
  5. sender=56 generation=0 signal=0 say='shift_symbols(1)'
  6. sender=5 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
  7. sender=98 generation=0 signal=0 say='shift_symbols(1)'
  8. sender=50 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
```

## All — inbox blocks at g2

### cell 1

slots=66, nonempty=66, distinct=8

```
Visible messages (66 slots):
  1. sender=0 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
  2. sender=2 generation=0 signal=0 say='shift_symbols(3)'
  3. sender=4 generation=0 signal=0 say='shift_symbols(5)'
  4. sender=5 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
  5. sender=7 generation=0 signal=0 say='shift_symbols(1)'
  6. sender=8 generation=0 signal=0 say='shift_symbols(2)'
  7. sender=10 generation=0 signal=0 say='shift_symbols(4)'
  8. sender=11 generation=0 signal=0 say='shift_symbols(5)'
  9. sender=13 generation=0 signal=0 say='shift_symbols(7)'
  10. sender=14 generation=0 signal=0 say='shift_symbols(1)'
  11. sender=16 generation=0 signal=0 say='shift_symbols(3)'
  12. sender=17 generation=0 signal=0 say='shift_symbols(4)'
  13. sender=19 generation=0 signal=0 say='shift_symbols(6)'
  14. sender=20 generation=0 signal=0 say='shift_symbols(7)'
  15. sender=22 generation=0 signal=0 say='shift_symbols(2)'
  16. sender=23 generation=0 signal=0 say='shift_symbols(3)'
  17. sender=25 generation=0 signal=0 say='shift_symbols(5)'
  18. sender=26 generation=0 signal=0 say='shift_symbols(6)'
  19. sender=28 generation=0 signal=0 say='shift_symbols(1)'
  20. sender=29 generation=0 signal=0 say='shift_symbols(2)'
  21. sender=31 generation=0 signal=0 say='shift_symbols(4)'
  22. sender=32 generation=0 signal=0 say='shift_symbols(5)'
  23. sender=34 generation=0 signal=0 say='shift_symbols(7)'
  24. sender=35 generation=0 signal=0 say='shift_symbols(1)'
  25. sender=37 generation=0 signal=0 say='shift_symbols(3)'
  26. sender=38 generation=0 signal=0 say='shift_symbols(4)'
  27. sender=40 generation=0 signal=0 say='shift_symbols(6)'
  28. sender=41 generation=0 signal=0 say='shift_symbols(7)'
  29. sender=43 generation=0 signal=0 say='shift_symbols(2)'
  30. sender=44 generation=0 signal=0 say='shift_symbols(3)'
  31. sender=46 generation=0 signal=0 say='shift_symbols(5)'
  32. sender=47 generation=0 signal=0 say='shift_symbols(6)'
  33. sender=49 generation=0 signal=0 say='shift_symbols(1)'
  34. sender=50 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
  35. sender=52 generation=0 signal=0 say='shift_symbols(4)'
  36. sender=53 generation=0 signal=0 say='shift_symbols(5)'
  37. sender=55 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
  38. sender=56 generation=0 signal=0 say='shift_symbols(1)'
  39. sender=58 generation=0 signal=0 say='shift_symbols(3)'
  40. sender=59 generation=0 signal=0 say='shift_symbols(4)'
  41. sender=61 generation=0 signal=0 say='shift_symbols(6)'
  42. sender=62 generation=0 signal=0 say='shift_symbols(7)'
  43. sender=64 generation=0 signal=0 say='shift_symbols(2)'
  44. sender=65 generation=0 signal=0 say='shift_symbols(3)'
  45. sender=67 generation=0 signal=0 say='shift_symbols(5)'
  46. sender=68 generation=0 signal=0 say='shift_symbols(6)'
  47. sender=70 generation=0 signal=0 say='shift_symbols(1)'
  48. sender=71 generation=0 signal=0 say='shift_symbols(2)'
  49. sender=73 generation=0 signal=0 say='shift_symbols(4)'
  50. sender=74 generation=0 signal=0 say='shift_symbols(5)'
  51. sender=76 generation=0 signal=0 say='shift_symbols(7)'
  52. sender=77 generation=0 signal=0 say='shift_symbols(1)'
  53. sender=79 generation=0 signal=0 say='shift_symbols(3)'
  54. sender=80 generation=0 signal=0 say='shift_symbols(4)'
  55. sender=82 generation=0 signal=0 say='shift_symbols(6)'
  56. sender=83 generation=0 signal=0 say='shift_symbols(7)'
  57. sender=85 generation=0 signal=0 say='shift_symbols(2)'
  58. sender=86 generation=0 signal=0 say='shift_symbols(3)'
  59. sender=88 generation=0 signal=0 say='shift_symbols(5)'
  60. sender=89 generation=0 signal=0 say='shift_symbols(6)'
  61. sender=91 generation=0 signal=0 say='shift_symbols(1)'
  62. sender=92 generation=0 signal=0 say='shift_symbols(2)'
  63. sender=94 generation=0 signal=0 say='shift_symbols(4)'
  64. sender=95 generation=0 signal=0 say='shift_symbols(5)'
  65. sender=97 generation=0 signal=0 say='shift_symbols(7)'
  66. sender=98 generation=0 signal=0 say='shift_symbols(1)'
```

### cell 2

slots=66, nonempty=66, distinct=8

```
Visible messages (66 slots):
  1. sender=0 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
  2. sender=1 generation=0 signal=0 say='shift_symbols(2)'
  3. sender=4 generation=0 signal=0 say='shift_symbols(5)'
  4. sender=5 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
  5. sender=7 generation=0 signal=0 say='shift_symbols(1)'
  6. sender=8 generation=0 signal=0 say='shift_symbols(2)'
  7. sender=10 generation=0 signal=0 say='shift_symbols(4)'
  8. sender=11 generation=0 signal=0 say='shift_symbols(5)'
  9. sender=13 generation=0 signal=0 say='shift_symbols(7)'
  10. sender=14 generation=0 signal=0 say='shift_symbols(1)'
  11. sender=16 generation=0 signal=0 say='shift_symbols(3)'
  12. sender=17 generation=0 signal=0 say='shift_symbols(4)'
  13. sender=19 generation=0 signal=0 say='shift_symbols(6)'
  14. sender=20 generation=0 signal=0 say='shift_symbols(7)'
  15. sender=22 generation=0 signal=0 say='shift_symbols(2)'
  16. sender=23 generation=0 signal=0 say='shift_symbols(3)'
  17. sender=25 generation=0 signal=0 say='shift_symbols(5)'
  18. sender=26 generation=0 signal=0 say='shift_symbols(6)'
  19. sender=28 generation=0 signal=0 say='shift_symbols(1)'
  20. sender=29 generation=0 signal=0 say='shift_symbols(2)'
  21. sender=31 generation=0 signal=0 say='shift_symbols(4)'
  22. sender=32 generation=0 signal=0 say='shift_symbols(5)'
  23. sender=34 generation=0 signal=0 say='shift_symbols(7)'
  24. sender=35 generation=0 signal=0 say='shift_symbols(1)'
  25. sender=37 generation=0 signal=0 say='shift_symbols(3)'
  26. sender=38 generation=0 signal=0 say='shift_symbols(4)'
  27. sender=40 generation=0 signal=0 say='shift_symbols(6)'
  28. sender=41 generation=0 signal=0 say='shift_symbols(7)'
  29. sender=43 generation=0 signal=0 say='shift_symbols(2)'
  30. sender=44 generation=0 signal=0 say='shift_symbols(3)'
  31. sender=46 generation=0 signal=0 say='shift_symbols(5)'
  32. sender=47 generation=0 signal=0 say='shift_symbols(6)'
  33. sender=49 generation=0 signal=0 say='shift_symbols(1)'
  34. sender=50 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
  35. sender=52 generation=0 signal=0 say='shift_symbols(4)'
  36. sender=53 generation=0 signal=0 say='shift_symbols(5)'
  37. sender=55 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
  38. sender=56 generation=0 signal=0 say='shift_symbols(1)'
  39. sender=58 generation=0 signal=0 say='shift_symbols(3)'
  40. sender=59 generation=0 signal=0 say='shift_symbols(4)'
  41. sender=61 generation=0 signal=0 say='shift_symbols(6)'
  42. sender=62 generation=0 signal=0 say='shift_symbols(7)'
  43. sender=64 generation=0 signal=0 say='shift_symbols(2)'
  44. sender=65 generation=0 signal=0 say='shift_symbols(3)'
  45. sender=67 generation=0 signal=0 say='shift_symbols(5)'
  46. sender=68 generation=0 signal=0 say='shift_symbols(6)'
  47. sender=70 generation=0 signal=0 say='shift_symbols(1)'
  48. sender=71 generation=0 signal=0 say='shift_symbols(2)'
  49. sender=73 generation=0 signal=0 say='shift_symbols(4)'
  50. sender=74 generation=0 signal=0 say='shift_symbols(5)'
  51. sender=76 generation=0 signal=0 say='shift_symbols(7)'
  52. sender=77 generation=0 signal=0 say='shift_symbols(1)'
  53. sender=79 generation=0 signal=0 say='shift_symbols(3)'
  54. sender=80 generation=0 signal=0 say='shift_symbols(4)'
  55. sender=82 generation=0 signal=0 say='shift_symbols(6)'
  56. sender=83 generation=0 signal=0 say='shift_symbols(7)'
  57. sender=85 generation=0 signal=0 say='shift_symbols(2)'
  58. sender=86 generation=0 signal=0 say='shift_symbols(3)'
  59. sender=88 generation=0 signal=0 say='shift_symbols(5)'
  60. sender=89 generation=0 signal=0 say='shift_symbols(6)'
  61. sender=91 generation=0 signal=0 say='shift_symbols(1)'
  62. sender=92 generation=0 signal=0 say='shift_symbols(2)'
  63. sender=94 generation=0 signal=0 say='shift_symbols(4)'
  64. sender=95 generation=0 signal=0 say='shift_symbols(5)'
  65. sender=97 generation=0 signal=0 say='shift_symbols(7)'
  66. sender=98 generation=0 signal=0 say='shift_symbols(1)'
```

### cell 4

slots=66, nonempty=66, distinct=8

```
Visible messages (66 slots):
  1. sender=0 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
  2. sender=1 generation=0 signal=0 say='shift_symbols(2)'
  3. sender=2 generation=0 signal=0 say='shift_symbols(3)'
  4. sender=5 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
  5. sender=7 generation=0 signal=0 say='shift_symbols(1)'
  6. sender=8 generation=0 signal=0 say='shift_symbols(2)'
  7. sender=10 generation=0 signal=0 say='shift_symbols(4)'
  8. sender=11 generation=0 signal=0 say='shift_symbols(5)'
  9. sender=13 generation=0 signal=0 say='shift_symbols(7)'
  10. sender=14 generation=0 signal=0 say='shift_symbols(1)'
  11. sender=16 generation=0 signal=0 say='shift_symbols(3)'
  12. sender=17 generation=0 signal=0 say='shift_symbols(4)'
  13. sender=19 generation=0 signal=0 say='shift_symbols(6)'
  14. sender=20 generation=0 signal=0 say='shift_symbols(7)'
  15. sender=22 generation=0 signal=0 say='shift_symbols(2)'
  16. sender=23 generation=0 signal=0 say='shift_symbols(3)'
  17. sender=25 generation=0 signal=0 say='shift_symbols(5)'
  18. sender=26 generation=0 signal=0 say='shift_symbols(6)'
  19. sender=28 generation=0 signal=0 say='shift_symbols(1)'
  20. sender=29 generation=0 signal=0 say='shift_symbols(2)'
  21. sender=31 generation=0 signal=0 say='shift_symbols(4)'
  22. sender=32 generation=0 signal=0 say='shift_symbols(5)'
  23. sender=34 generation=0 signal=0 say='shift_symbols(7)'
  24. sender=35 generation=0 signal=0 say='shift_symbols(1)'
  25. sender=37 generation=0 signal=0 say='shift_symbols(3)'
  26. sender=38 generation=0 signal=0 say='shift_symbols(4)'
  27. sender=40 generation=0 signal=0 say='shift_symbols(6)'
  28. sender=41 generation=0 signal=0 say='shift_symbols(7)'
  29. sender=43 generation=0 signal=0 say='shift_symbols(2)'
  30. sender=44 generation=0 signal=0 say='shift_symbols(3)'
  31. sender=46 generation=0 signal=0 say='shift_symbols(5)'
  32. sender=47 generation=0 signal=0 say='shift_symbols(6)'
  33. sender=49 generation=0 signal=0 say='shift_symbols(1)'
  34. sender=50 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
  35. sender=52 generation=0 signal=0 say='shift_symbols(4)'
  36. sender=53 generation=0 signal=0 say='shift_symbols(5)'
  37. sender=55 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
  38. sender=56 generation=0 signal=0 say='shift_symbols(1)'
  39. sender=58 generation=0 signal=0 say='shift_symbols(3)'
  40. sender=59 generation=0 signal=0 say='shift_symbols(4)'
  41. sender=61 generation=0 signal=0 say='shift_symbols(6)'
  42. sender=62 generation=0 signal=0 say='shift_symbols(7)'
  43. sender=64 generation=0 signal=0 say='shift_symbols(2)'
  44. sender=65 generation=0 signal=0 say='shift_symbols(3)'
  45. sender=67 generation=0 signal=0 say='shift_symbols(5)'
  46. sender=68 generation=0 signal=0 say='shift_symbols(6)'
  47. sender=70 generation=0 signal=0 say='shift_symbols(1)'
  48. sender=71 generation=0 signal=0 say='shift_symbols(2)'
  49. sender=73 generation=0 signal=0 say='shift_symbols(4)'
  50. sender=74 generation=0 signal=0 say='shift_symbols(5)'
  51. sender=76 generation=0 signal=0 say='shift_symbols(7)'
  52. sender=77 generation=0 signal=0 say='shift_symbols(1)'
  53. sender=79 generation=0 signal=0 say='shift_symbols(3)'
  54. sender=80 generation=0 signal=0 say='shift_symbols(4)'
  55. sender=82 generation=0 signal=0 say='shift_symbols(6)'
  56. sender=83 generation=0 signal=0 say='shift_symbols(7)'
  57. sender=85 generation=0 signal=0 say='shift_symbols(2)'
  58. sender=86 generation=0 signal=0 say='shift_symbols(3)'
  59. sender=88 generation=0 signal=0 say='shift_symbols(5)'
  60. sender=89 generation=0 signal=0 say='shift_symbols(6)'
  61. sender=91 generation=0 signal=0 say='shift_symbols(1)'
  62. sender=92 generation=0 signal=0 say='shift_symbols(2)'
  63. sender=94 generation=0 signal=0 say='shift_symbols(4)'
  64. sender=95 generation=0 signal=0 say='shift_symbols(5)'
  65. sender=97 generation=0 signal=0 say='shift_symbols(7)'
  66. sender=98 generation=0 signal=0 say='shift_symbols(1)'
```

## R8c — after engine filter (same senders)

### cell 1

```
Visible messages (8 slots):
  1. empty
  2. empty
  3. empty
  4. empty
  5. empty
  6. empty
  7. empty
  8. empty
```

### cell 2

```
Visible messages (8 slots):
  1. empty
  2. empty
  3. empty
  4. empty
  5. empty
  6. empty
  7. empty
  8. empty
```

### cell 4

```
Visible messages (8 slots):
  1. empty
  2. empty
  3. empty
  4. sender=77 generation=0 signal=0 say='shift_symbols(1)'
  5. sender=56 generation=0 signal=0 say='shift_symbols(1)'
  6. sender=5 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
  7. sender=98 generation=0 signal=0 say='shift_symbols(1)'
  8. sender=50 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
```

## Allc — after engine filter (same senders)

### cell 1

```
Visible messages (4 slots):
  1. sender=0 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
  2. sender=5 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
  3. sender=50 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
  4. sender=55 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
```

### cell 2

```
Visible messages (4 slots):
  1. sender=0 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
  2. sender=5 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
  3. sender=50 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
  4. sender=55 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
```

### cell 4

```
Visible messages (14 slots):
  1. sender=0 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
  2. sender=5 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
  3. sender=7 generation=0 signal=0 say='shift_symbols(1)'
  4. sender=14 generation=0 signal=0 say='shift_symbols(1)'
  5. sender=28 generation=0 signal=0 say='shift_symbols(1)'
  6. sender=35 generation=0 signal=0 say='shift_symbols(1)'
  7. sender=49 generation=0 signal=0 say='shift_symbols(1)'
  8. sender=50 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
  9. sender=55 generation=0 signal=0 say='shift_symbols(1);swap(2,3)'
  10. sender=56 generation=0 signal=0 say='shift_symbols(1)'
  11. sender=70 generation=0 signal=0 say='shift_symbols(1)'
  12. sender=77 generation=0 signal=0 say='shift_symbols(1)'
  13. sender=91 generation=0 signal=0 say='shift_symbols(1)'
  14. sender=98 generation=0 signal=0 say='shift_symbols(1)'
```

