# HumanEval Runs File (Initial 164-Task Sweep, Attempt-Level)

Date generated: 2026-03-16

## 1) Scope and Selection Rule
- Source: `episodes/humaneval_runs/runs_summary.jsonl` + per-run attempt artifacts.
- Selection rule: for each `HumanEval/<id>`, use the **earliest run timestamp** in `runs_summary.jsonl`.
- Coverage: `164` tasks (`HumanEval/0` to `HumanEval/163`).

## 2) Core Metrics (Initial Sweep)
- Total tasks: `164`
- Final PASS: `68`
- Final FAIL: `96`
- PASS winner = SLM: `68`
- PASS winner = LLM fallback: `0`
- FAIL winner = NONE: `96`

Second-attempt SLM recoveries (explicitly verified):
- Count: `4`
- Tasks: `HumanEval/10, HumanEval/105, HumanEval/118, HumanEval/121`

## 3) Status Legend
- `PASS`: tests passed
- `SLM_TIMEOUT`/`TIMEOUT`: timeout signatures
- `ASSERT_FAIL`, `NAME_ERROR`, `TYPE_ERROR`, etc.: normalized failure classes from `result.json.failure_summary`
- `none` in fallback column: no fallback attempts recorded for that selected run

## 4) Task-Level Attempt Status (All 164)
| Task ID | Selected run dir | Final | Winner | Winner attempt | SLM attempts | LLM fallback attempts |
|---|---|---|---|---:|---|---|
| HumanEval/0 | `20260201_180812_HumanEval_0` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/1 | `20260201_180950_HumanEval_1` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/2 | `20260201_181202_HumanEval_2` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/3 | `20260201_181211_HumanEval_3` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/4 | `20260201_181311_HumanEval_4` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/5 | `20260201_181457_HumanEval_5` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/6 | `20260201_211005_HumanEval_6` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/7 | `20260201_211200_HumanEval_7` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/8 | `20260201_211309_HumanEval_8` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/9 | `20260201_211446_HumanEval_9` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/10 | `20260201_211622_HumanEval_10` | PASS | SLM | 2 | `attempt_01:ASSERT_FAIL; attempt_02:PASS` | `none` |
| HumanEval/11 | `20260201_211734_HumanEval_11` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/12 | `20260201_211746_HumanEval_12` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/13 | `20260201_211910_HumanEval_13` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/14 | `20260201_211922_HumanEval_14` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/15 | `20260201_212020_HumanEval_15` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/16 | `20260201_212029_HumanEval_16` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/17 | `20260201_212039_HumanEval_17` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/18 | `20260201_212244_HumanEval_18` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/19 | `20260201_164813_HumanEval_19` | FAIL | NONE | - | `attempt_01:SYNTAX_ERROR; attempt_02:SYNTAX_ERROR` | `none` |
| HumanEval/20 | `20260202_040331_HumanEval_20` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/21 | `20260202_040436_HumanEval_21` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/22 | `20260202_040609_HumanEval_22` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/23 | `20260202_040711_HumanEval_23` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/24 | `20260202_040726_HumanEval_24` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/25 | `20260202_040748_HumanEval_25` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/26 | `20260202_040929_HumanEval_26` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/27 | `20260202_041041_HumanEval_27` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/28 | `20260202_041057_HumanEval_28` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/29 | `20260202_041127_HumanEval_29` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/30 | `20260202_041206_HumanEval_30` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/31 | `20260202_041216_HumanEval_31` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/32 | `20260202_041250_HumanEval_32` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:INDENT_ERROR` | `none` |
| HumanEval/33 | `20260202_041439_HumanEval_33` | FAIL | NONE | - | `attempt_01:TYPE_ERROR; attempt_02:TYPE_ERROR` | `none` |
| HumanEval/34 | `20260201_175614_HumanEval_34` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/35 | `20260202_041538_HumanEval_35` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/36 | `20260202_041547_HumanEval_36` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/37 | `20260202_041605_HumanEval_37` | FAIL | NONE | - | `attempt_01:INDEX_ERROR; attempt_02:TYPE_ERROR` | `none` |
| HumanEval/38 | `20260202_041641_HumanEval_38` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/39 | `20260202_041752_HumanEval_39` | FAIL | NONE | - | `attempt_01:TIMEOUT; attempt_02:TIMEOUT` | `none` |
| HumanEval/40 | `20260202_041902_HumanEval_40` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/41 | `20260202_041923_HumanEval_41` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/42 | `20260202_041933_HumanEval_42` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/43 | `20260202_041943_HumanEval_43` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/44 | `20260202_041957_HumanEval_44` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/45 | `20260202_042016_HumanEval_45` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/46 | `20260202_042025_HumanEval_46` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:SYNTAX_ERROR` | `none` |
| HumanEval/47 | `20260202_042151_HumanEval_47` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/48 | `20260202_042209_HumanEval_48` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/49 | `20260202_042217_HumanEval_49` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/50 | `20260202_042246_HumanEval_50` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `none` |
| HumanEval/51 | `20260202_042322_HumanEval_51` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/52 | `20260202_042334_HumanEval_52` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/53 | `20260202_042347_HumanEval_53` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/54 | `20260202_042356_HumanEval_54` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/55 | `20260202_042450_HumanEval_55` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/56 | `20260202_042505_HumanEval_56` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/57 | `20260201_180042_HumanEval_57` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/58 | `20260201_180055_HumanEval_58` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/59 | `20260202_042522_HumanEval_59` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/60 | `20260202_042556_HumanEval_60` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/61 | `20260202_042607_HumanEval_61` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/62 | `20260202_042623_HumanEval_62` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/63 | `20260202_042634_HumanEval_63` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/64 | `20260202_042658_HumanEval_64` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/65 | `20260202_042817_HumanEval_65` | FAIL | NONE | - | `attempt_01:TYPE_ERROR; attempt_02:TYPE_ERROR` | `none` |
| HumanEval/66 | `20260202_042901_HumanEval_66` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/67 | `20260202_042911_HumanEval_67` | FAIL | NONE | - | `attempt_01:VALUE_ERROR; attempt_02:VALUE_ERROR` | `none` |
| HumanEval/68 | `20260202_042940_HumanEval_68` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/69 | `20260202_043006_HumanEval_69` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/70 | `20260202_043047_HumanEval_70` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/71 | `20260202_043115_HumanEval_71` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/72 | `20260202_043154_HumanEval_72` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/73 | `20260202_043208_HumanEval_73` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/74 | `20260202_043227_HumanEval_74` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/75 | `20260202_043303_HumanEval_75` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/76 | `20260202_043340_HumanEval_76` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:UNBOUNDLOCAL_ERROR` | `none` |
| HumanEval/77 | `20260202_043502_HumanEval_77` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/78 | `20260202_043527_HumanEval_78` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/79 | `20260202_043543_HumanEval_79` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/80 | `20260202_043636_HumanEval_80` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/81 | `20260202_043649_HumanEval_81` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:KEY_ERROR` | `none` |
| HumanEval/82 | `20260202_043745_HumanEval_82` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/83 | `20260202_043802_HumanEval_83` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/84 | `20260202_043836_HumanEval_84` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/85 | `20260202_043846_HumanEval_85` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/86 | `20260202_043858_HumanEval_86` | FAIL | NONE | - | `attempt_01:TYPE_ERROR; attempt_02:TYPE_ERROR` | `none` |
| HumanEval/87 | `20260202_043921_HumanEval_87` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/88 | `20260202_043939_HumanEval_88` | FAIL | NONE | - | `attempt_01:INDEX_ERROR; attempt_02:INDEX_ERROR` | `none` |
| HumanEval/89 | `20260202_044046_HumanEval_89` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/90 | `20260202_044105_HumanEval_90` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/91 | `20260202_044134_HumanEval_91` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/92 | `20260202_044221_HumanEval_92` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/93 | `20260202_044237_HumanEval_93` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/94 | `20260202_044327_HumanEval_94` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/95 | `20260202_044358_HumanEval_95` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/96 | `20260202_044420_HumanEval_96` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/97 | `20260202_044444_HumanEval_97` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/98 | `20260202_044455_HumanEval_98` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/99 | `20260202_044507_HumanEval_99` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/100 | `20260202_044522_HumanEval_100` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/101 | `20260202_044534_HumanEval_101` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/102 | `20260202_044558_HumanEval_102` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/103 | `20260202_044658_HumanEval_103` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/104 | `20260202_044732_HumanEval_104` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/105 | `20260202_044744_HumanEval_105` | PASS | SLM | 2 | `attempt_01:TYPE_ERROR; attempt_02:PASS` | `none` |
| HumanEval/106 | `20260202_044854_HumanEval_106` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/107 | `20260202_044929_HumanEval_107` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/108 | `20260202_044955_HumanEval_108` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/109 | `20260202_045028_HumanEval_109` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/110 | `20260202_045050_HumanEval_110` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/111 | `20260202_045215_HumanEval_111` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/112 | `20260202_045243_HumanEval_112` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/113 | `20260202_045315_HumanEval_113` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/114 | `20260202_045405_HumanEval_114` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/115 | `20260202_045425_HumanEval_115` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/116 | `20260202_045525_HumanEval_116` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/117 | `20260202_045552_HumanEval_117` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/118 | `20260202_045727_HumanEval_118` | PASS | SLM | 2 | `attempt_01:ASSERT_FAIL; attempt_02:PASS` | `none` |
| HumanEval/119 | `20260202_133710_HumanEval_119` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/120 | `20260202_050203_HumanEval_120` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/121 | `20260202_050258_HumanEval_121` | PASS | SLM | 2 | `attempt_01:ASSERT_FAIL; attempt_02:PASS` | `none` |
| HumanEval/122 | `20260202_050403_HumanEval_122` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/123 | `20260202_134111_HumanEval_123` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/124 | `20260202_134512_HumanEval_124` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/125 | `20260202_053859_HumanEval_125` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/126 | `20260202_134913_HumanEval_126` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/127 | `20260202_135315_HumanEval_127` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/128 | `20260202_073517_HumanEval_128` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/129 | `20260202_074309_HumanEval_129` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/130 | `20260202_135716_HumanEval_130` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/131 | `20260202_140117_HumanEval_131` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/132 | `20260202_140519_HumanEval_132` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/133 | `20260202_083147_HumanEval_133` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/134 | `20260202_140920_HumanEval_134` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/135 | `20260202_141322_HumanEval_135` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/136 | `20260202_110209_HumanEval_136` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/137 | `20260202_131707_HumanEval_137` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/138 | `20260202_132135_HumanEval_138` | PASS | SLM | 1 | `attempt_01:PASS; attempt_02:-` | `none` |
| HumanEval/139 | `20260202_110210_HumanEval_139` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/140 | `20260202_131707_HumanEval_140` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `none` |
| HumanEval/141 | `20260202_110048_HumanEval_141` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/142 | `20260202_110048_HumanEval_142` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/143 | `20260202_131543_HumanEval_143` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/144 | `20260202_132011_HumanEval_144` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/145 | `20260202_132412_HumanEval_145` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/146 | `20260202_132812_HumanEval_146` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/147 | `20260202_133213_HumanEval_147` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/148 | `20260202_133614_HumanEval_148` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/149 | `20260202_134015_HumanEval_149` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/150 | `20260202_134416_HumanEval_150` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/151 | `20260202_134816_HumanEval_151` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/152 | `20260202_135218_HumanEval_152` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/153 | `20260202_135619_HumanEval_153` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/154 | `20260202_140020_HumanEval_154` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/155 | `20260202_140422_HumanEval_155` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/156 | `20260202_140823_HumanEval_156` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/157 | `20260202_141225_HumanEval_157` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/158 | `20260202_141626_HumanEval_158` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/159 | `20260202_142028_HumanEval_159` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/160 | `20260202_142430_HumanEval_160` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/161 | `20260202_142831_HumanEval_161` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/162 | `20260202_143233_HumanEval_162` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |
| HumanEval/163 | `20260202_143635_HumanEval_163` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `none` |

## 5) Terminal Failure Taxonomy (96 Final Fails)
- `SLM_TIMEOUT`: `37`
- `ASSERT_FAIL`: `26`
- `NAME_ERROR`: `21`
- `TYPE_ERROR`: `4`
- `SYNTAX_ERROR`: `2`
- `INDENT_ERROR`: `1`
- `INDEX_ERROR`: `1`
- `KEY_ERROR`: `1`
- `TIMEOUT`: `1`
- `UNBOUNDLOCAL_ERROR`: `1`
- `VALUE_ERROR`: `1`

## 6) Notes for Thesis Reporting
- This table is aligned to the initial sweep methodology used in prior HumanEval SLM analysis in this workspace.
- The “4 tasks passed in SLM attempt-2” statement is preserved and explicitly listed above.

## 7) Appendix Deep-Dive: The 4 SLM Attempt-2 Recoveries

These are the only tasks where attempt-1 failed but attempt-2 passed (no fallback used in selected initial runs):

1. `HumanEval/10` (`make_palindrome`)
2. `HumanEval/105` (`by_length`)
3. `HumanEval/118` (`get_closest_vowel`)
4. `HumanEval/121` (`solution`)

Observed pattern across all 4:
- Attempt-1 failed with a concrete test/runtime signal (`ASSERT_FAIL` or `TYPE_ERROR`).
- Attempt-2 fixed a localized logic issue and reached `PASS`.
- This is consistent with iterative self-correction behavior where explicit prior error context improves the second generation.

Task-specific short notes:
- `HumanEval/10`: `ASSERT_FAIL -> PASS` (edge-case palindrome completion corrected).
- `HumanEval/105`: `TYPE_ERROR -> PASS` (collection/indexing misuse corrected).
- `HumanEval/118`: `ASSERT_FAIL -> PASS` (vowel-selection rule corrected).
- `HumanEval/121`: `ASSERT_FAIL -> PASS` (constraint/logic alignment corrected).

## 8) Appendix Coverage: Outcome Groups Across All 164 Tasks

This grouped appendix ensures complete coverage of all tasks in compact narrative form.

### 8.1 SLM Pass on Attempt-1 (64 tasks)

Task IDs:
`2, 11, 13, 15, 16, 18, 23, 24, 27, 30, 31, 34, 35, 36, 40, 41, 42, 43, 44, 45, 47, 48, 49, 51, 52, 53, 55, 56, 57, 58, 59, 60, 61, 62, 63, 66, 68, 72, 73, 78, 80, 82, 84, 85, 87, 89, 92, 94, 95, 96, 97, 98, 99, 100, 104, 107, 109, 111, 114, 116, 122, 125, 128, 138`

Interpretation:
- These tasks were solved without requiring retry or fallback in the selected initial sweep run.

### 8.2 SLM Pass on Attempt-2 (4 tasks)

Task IDs:
`10, 105, 118, 121`

Interpretation:
- These are the explicit second-attempt recoveries and represent positive iterative-correction signal.

### 8.3 Final Fail: `SLM_TIMEOUT` (37 tasks)

Task IDs:
`119, 123, 124, 126, 127, 130, 131, 132, 133, 134, 135, 136, 137, 139, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163`

Interpretation:
- Largest failure group; primary blocker is generation timeout rather than semantic mismatch.

### 8.4 Final Fail: `ASSERT_FAIL` (26 tasks)

Task IDs:
`54, 64, 69, 70, 71, 74, 75, 77, 79, 83, 90, 91, 93, 101, 102, 103, 106, 108, 110, 112, 113, 115, 117, 120, 129, 140`

Interpretation:
- Code executed but did not satisfy expected behavior in one or more tests.

### 8.5 Final Fail: `NAME_ERROR` (21 tasks)

Task IDs:
`0, 1, 3, 4, 5, 6, 7, 8, 9, 12, 14, 17, 20, 21, 22, 25, 26, 28, 29, 38, 50`

Interpretation:
- Frequent missing symbol/import context in early selected runs (notably type-hint/module misses).

### 8.6 Final Fail: `TYPE_ERROR` (4 tasks)

Task IDs:
`33, 37, 65, 86`

Interpretation:
- Runtime type misuse; likely recoverable with stronger type-consistency prompting.

### 8.7 Final Fail: `SYNTAX_ERROR` (2 tasks)

Task IDs:
`19, 46`

Interpretation:
- Minor fraction of failures are compile-level syntax breaks.

### 8.8 Final Fail: Single-Task Buckets

- `INDENT_ERROR`: task `32`
- `INDEX_ERROR`: task `88`
- `KEY_ERROR`: task `81`
- `TIMEOUT`: task `39`
- `UNBOUNDLOCAL_ERROR`: task `76`
- `VALUE_ERROR`: task `67`

Interpretation:
- These are isolated edge/runtime signatures compared with the dominant timeout/assertion/name-error clusters.

## 9) Final Alignment Note

This file now contains the same structural elements used in QuixBugs/BigCodeBench run files:
- full attempt-level task table,
- explicit recovery accounting,
- failure taxonomy,
- appendix narrative coverage for the whole task set.

## 10) RAG-Enabled Runs (v2) Added for Analysis/Results Reporting

This section captures the later HumanEval v2 phase where retrieval (`--rag_enabled 1`) was used before fallback LLM generation.

Evidence source:
- `episodes/humaneval_runs/*_HumanEval_*/slm_attempt_*/rag_query.txt`
- `episodes/humaneval_runs/*_HumanEval_*/slm_attempt_*/rag_hits.json`
- `episodes/humaneval_runs/*_HumanEval_*/slm_attempt_*/rag_context.txt`
- `episodes/humaneval_runs/*_HumanEval_*/fallback_attempt_*/prompt.txt`

Snapshot files generated for thesis reporting:
- `reports/rag_humaneval_runs_snapshot.json` (all detected RAG runs)
- `reports/rag_humaneval_latest_per_task.json` (latest RAG run per task)

### 10.1 Coverage Summary

All RAG run directories found in history:
- RAG run directories: `187`
- Unique HumanEval task IDs with at least one RAG run: `67`
- Total RAG attempt artifact sets (`rag_query/rag_hits/rag_context`): `371`
- Runs with fallback attempt directories: `184`
- Runs with fallback prompt artifacts: `184`
- Final outcomes across these 187 runs: `69 PASS`, `118 FAIL`

Latest-per-task view (67 tasks, one latest RAG run per task):
- Final PASS: `42`
- Final FAIL: `25`
- Final PASS by SLM: `2` (`HumanEval/148`, `HumanEval/149`)
- Final PASS by fallback LLM: `40`
- Final FAIL after fallback/non-pass: `25`
- Tasks with fallback prompts recorded: `65`
- LLM passes by attempt: `38` on fallback attempt-1, `2` on fallback attempt-2

### 10.2 Tasks That Had RAG Runs (Unique Task IDs)

`HumanEval/14, HumanEval/26, HumanEval/28, HumanEval/29, HumanEval/32, HumanEval/38, HumanEval/39, HumanEval/46, HumanEval/50, HumanEval/65, HumanEval/74, HumanEval/76, HumanEval/79, HumanEval/81, HumanEval/83, HumanEval/86, HumanEval/88, HumanEval/90, HumanEval/91, HumanEval/93, HumanEval/101, HumanEval/102, HumanEval/103, HumanEval/106, HumanEval/108, HumanEval/110, HumanEval/112, HumanEval/113, HumanEval/115, HumanEval/117, HumanEval/119, HumanEval/120, HumanEval/123, HumanEval/124, HumanEval/126, HumanEval/127, HumanEval/129, HumanEval/130, HumanEval/131, HumanEval/132, HumanEval/133, HumanEval/134, HumanEval/135, HumanEval/136, HumanEval/137, HumanEval/139, HumanEval/140, HumanEval/141, HumanEval/142, HumanEval/143, HumanEval/144, HumanEval/145, HumanEval/146, HumanEval/147, HumanEval/148, HumanEval/149, HumanEval/150, HumanEval/151, HumanEval/152, HumanEval/153, HumanEval/154, HumanEval/155, HumanEval/156, HumanEval/157, HumanEval/160, HumanEval/162, HumanEval/163`

### 10.3 Exactly What RAG Data Was Captured Before Fallback LLM

For each failed SLM attempt in v2, the runner writes:
- `slm_attempt_XX/rag_query.txt`
  - composed from `entry_point`, normalized `error_type`, `error_summary`, and full task prompt.
- `slm_attempt_XX/rag_hits.json`
  - top-k retrieved cases (here k=3), with fields such as:
    - `id`, `case_id`, `task_id`, `dataset`, `entry_point`
    - `slm_failure_type`, `slm_failure_summary`
    - `fix_actions`, `llm_code`, `fix_diff`, `prompt`, `run_dir`, `timestamp`
    - retrieval `score`
- `slm_attempt_XX/rag_context.txt`
  - formatted prompt-ready hint block built from hits:
    - case id/task
    - failure type
    - fix actions
    - retrieval score
    - optional import hints from diff
    - truncated diff excerpts

Before fallback attempt, `fallback_attempt_XX/prompt.txt` includes:
- previous SLM/fallback failures,
- self-debug notes (if generated),
- `RAG hints:` section from `rag_context.txt`.

### 10.4 Concrete Artifact Example (HumanEval/101)

Run directory:
- `episodes/humaneval_runs/20260222_182120_HumanEval_101`

Observed artifacts:
- `slm_attempt_01/rag_query.txt`
  - contains `entry_point: words_string`, `error_type: AssertionError`, full failure tail, and task prompt text.
- `slm_attempt_01/rag_hits.json`
  - contains exactly 3 retrieved cases with similarity scores.
- `slm_attempt_01/rag_context.txt`
  - includes structured cases and diff-based hints.
- `fallback_attempt_01/prompt.txt`
  - includes explicit `RAG hints:` section before final task prompt.

In this run, retrieval artifacts were successfully written before fallback prompting and the final status is `PASS` via fallback LLM.
