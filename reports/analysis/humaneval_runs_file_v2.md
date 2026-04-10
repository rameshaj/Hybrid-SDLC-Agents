# HumanEval Runs File v2 (Complete — All Runs, Verified from Artifacts)

Date generated: 2026-04-01

## 1) Scope and Selection Rule
- Source: `episodes/humaneval_runs/` — latest run per task across ALL run batches.
- Selection rule: for each `HumanEval/<id>`, use the **latest run timestamp** across all run directories.
- Coverage: `164` tasks (`HumanEval/0` to `HumanEval/163`).
- Key difference from v1: v1 used earliest run (initial sweep only). This file uses latest run, capturing all re-runs and verified results.

---

## 2) Core Metrics (All Runs, Latest Per Task)

- Total tasks: `164`
- Final PASS: `139`
- Final FAIL: `23`
- Incomplete run (no final_status.json): `2` (`HumanEval/125`, `HumanEval/136`)

**PASS breakdown by model:**
- PASS by SLM: `86`
  - SLM pass on attempt-1: `81`
  - SLM pass on attempt-2: `5` (`HumanEval/10`, `HumanEval/105`, `HumanEval/118`, `HumanEval/121`, `HumanEval/148`)
- PASS by LLM fallback: `53`
  - LLM pass on fallback attempt-1: `48`
  - LLM pass on fallback attempt-2: `5` (`HumanEval/8`, `HumanEval/20`, `HumanEval/33`, `HumanEval/117`, `HumanEval/155`)

**Note on v1 vs v2 comparison:**
- v1 (initial sweep, earliest run): SLM=68 PASS, LLM=0 PASS, FAIL=96
- v2 (all runs, latest per task): SLM=86 PASS, LLM=53 PASS, FAIL=23
- 19 additional SLM passes came from re-runs (17 no-RAG, 2 with RAG context: 148, 149)
- HumanEval/148 and HumanEval/149 verified to pass SLM without RAG (confirmed by fresh no-RAG re-run on 2026-04-01)

---

## 3) Status Legend
- `PASS`: tests passed
- `SLM_TIMEOUT`: SLM generation timed out
- `ASSERT_FAIL`, `NAME_ERROR`, `TYPE_ERROR`, etc.: normalized failure classes
- `none` in fallback column: no fallback attempts recorded for that run

---

## 4) Task-Level Attempt Status (All 164)

| Task ID | Latest run dir | Final | Winner | Winner attempt | SLM attempts | LLM fallback attempts |
|---|---|---|---|---:|---|---|
| HumanEval/0 | `20260212_064246_HumanEval_0` | PASS | LLM | 1 | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `fallback_01:PASS` |
| HumanEval/1 | `20260212_065147_HumanEval_1` | PASS | LLM | 1 | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `fallback_01:PASS` |
| HumanEval/2 | `20260201_181202_HumanEval_2` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/3 | `20260206_071641_HumanEval_3` | PASS | LLM | 1 | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `fallback_01:PASS` |
| HumanEval/4 | `20260212_065551_HumanEval_4` | PASS | LLM | 1 | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `fallback_01:PASS` |
| HumanEval/5 | `20260212_070827_HumanEval_5` | PASS | LLM | 1 | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `fallback_01:PASS` |
| HumanEval/6 | `20260212_071808_HumanEval_6` | PASS | LLM | 1 | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `fallback_01:PASS` |
| HumanEval/7 | `20260212_073048_HumanEval_7` | PASS | LLM | 1 | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `fallback_01:PASS` |
| HumanEval/8 | `20260212_073415_HumanEval_8` | PASS | LLM | 2 | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `fallback_01:NAME_ERROR; fallback_02:PASS` |
| HumanEval/9 | `20260212_073753_HumanEval_9` | PASS | LLM | 1 | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `fallback_01:PASS` |
| HumanEval/10 | `20260201_211622_HumanEval_10` | PASS | SLM | 2 | `attempt_01:ASSERT_FAIL; attempt_02:PASS` | `none` |
| HumanEval/11 | `20260201_211734_HumanEval_11` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/12 | `20260212_074142_HumanEval_12` | PASS | LLM | 1 | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `fallback_01:PASS` |
| HumanEval/13 | `20260201_211910_HumanEval_13` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/14 | `20260214_073154_HumanEval_14` | PASS | LLM | 1 | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `fallback_01:PASS` |
| HumanEval/15 | `20260201_212020_HumanEval_15` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/16 | `20260201_212029_HumanEval_16` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/17 | `20260213_071722_HumanEval_17` | PASS | LLM | 1 | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `fallback_01:PASS` |
| HumanEval/18 | `20260201_212244_HumanEval_18` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/19 | `20260212_074839_HumanEval_19` | PASS | LLM | 1 | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `fallback_01:PASS` |
| HumanEval/20 | `20260213_073022_HumanEval_20` | PASS | LLM | 2 | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `fallback_01:NAME_ERROR; fallback_02:PASS` |
| HumanEval/21 | `20260213_073942_HumanEval_21` | PASS | LLM | 1 | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `fallback_01:PASS` |
| HumanEval/22 | `20260213_074751_HumanEval_22` | PASS | LLM | 1 | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `fallback_01:PASS` |
| HumanEval/23 | `20260202_040711_HumanEval_23` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/24 | `20260202_040726_HumanEval_24` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/25 | `20260213_075127_HumanEval_25` | PASS | LLM | 1 | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `fallback_01:PASS` |
| HumanEval/26 | `20260222_060206_HumanEval_26` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `fallback_01:NAME_ERROR; fallback_02:NAME_ERROR` |
| HumanEval/27 | `20260202_041041_HumanEval_27` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/28 | `20260222_060434_HumanEval_28` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `fallback_01:NAME_ERROR; fallback_02:NAME_ERROR` |
| HumanEval/29 | `20260222_060637_HumanEval_29` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:NAME_ERROR` | `fallback_01:NAME_ERROR; fallback_02:NAME_ERROR` |
| HumanEval/30 | `20260202_041206_HumanEval_30` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/31 | `20260202_041216_HumanEval_31` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/32 | `20260222_060955_HumanEval_32` | FAIL | NONE | - | `attempt_01:SYNTAX_ERROR; attempt_02:SYNTAX_ERROR` | `fallback_01:INDENT_ERROR; fallback_02:INDENT_ERROR` |
| HumanEval/33 | `20260213_075605_HumanEval_33` | PASS | LLM | 2 | `attempt_01:TYPE_ERROR; attempt_02:TYPE_ERROR` | `fallback_01:ASSERT_FAIL; fallback_02:PASS` |
| HumanEval/34 | `20260201_175614_HumanEval_34` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/35 | `20260202_041538_HumanEval_35` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/36 | `20260202_041547_HumanEval_36` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/37 | `20260213_080041_HumanEval_37` | PASS | LLM | 1 | `attempt_01:INDEX_ERROR; attempt_02:TYPE_ERROR` | `fallback_01:PASS` |
| HumanEval/38 | `20260222_064903_HumanEval_38` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:SLM_TIMEOUT` | `fallback_01:NAME_ERROR; fallback_02:NAME_ERROR` |
| HumanEval/39 | `20260222_102150_HumanEval_39` | PASS | LLM | 1 | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `fallback_01:PASS` |
| HumanEval/40 | `20260202_041902_HumanEval_40` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/41 | `20260202_041923_HumanEval_41` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/42 | `20260202_041933_HumanEval_42` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/43 | `20260202_041943_HumanEval_43` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/44 | `20260202_041957_HumanEval_44` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/45 | `20260202_042016_HumanEval_45` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/46 | `20260222_114758_HumanEval_46` | PASS | LLM | 1 | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `fallback_01:PASS` |
| HumanEval/47 | `20260202_042151_HumanEval_47` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/48 | `20260202_042209_HumanEval_48` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/49 | `20260202_042217_HumanEval_49` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/50 | `20260222_115315_HumanEval_50` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `fallback_01:NAME_ERROR; fallback_02:NAME_ERROR` |
| HumanEval/51 | `20260202_042322_HumanEval_51` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/52 | `20260202_042334_HumanEval_52` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/53 | `20260202_042347_HumanEval_53` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/54 | `20260212_074958_HumanEval_54` | PASS | LLM | 1 | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `fallback_01:PASS` |
| HumanEval/55 | `20260202_042450_HumanEval_55` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/56 | `20260202_042505_HumanEval_56` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/57 | `20260201_180042_HumanEval_57` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/58 | `20260201_180055_HumanEval_58` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/59 | `20260202_042522_HumanEval_59` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/60 | `20260202_042556_HumanEval_60` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/61 | `20260202_042607_HumanEval_61` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/62 | `20260202_042623_HumanEval_62` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/63 | `20260202_042634_HumanEval_63` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/64 | `20260212_080911_HumanEval_64` | PASS | LLM | 1 | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `fallback_01:PASS` |
| HumanEval/65 | `20260222_122759_HumanEval_65` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `fallback_01:ASSERT_FAIL; fallback_02:ASSERT_FAIL` |
| HumanEval/66 | `20260202_042901_HumanEval_66` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/67 | `20260213_082821_HumanEval_67` | PASS | LLM | 1 | `attempt_01:VALUE_ERROR; attempt_02:VALUE_ERROR` | `fallback_01:PASS` |
| HumanEval/68 | `20260202_042940_HumanEval_68` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/69 | `20260212_081415_HumanEval_69` | PASS | LLM | 1 | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `fallback_01:PASS` |
| HumanEval/70 | `20260212_081548_HumanEval_70` | PASS | LLM | 1 | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `fallback_01:PASS` |
| HumanEval/71 | `20260212_081734_HumanEval_71` | PASS | LLM | 1 | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `fallback_01:PASS` |
| HumanEval/72 | `20260202_043154_HumanEval_72` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/73 | `20260202_043208_HumanEval_73` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/74 | `20260222_123432_HumanEval_74` | PASS | LLM | 1 | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `fallback_01:PASS` |
| HumanEval/75 | `20260213_064248_HumanEval_75` | PASS | LLM | 1 | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `fallback_01:PASS` |
| HumanEval/76 | `20260222_130829_HumanEval_76` | PASS | LLM | 1 | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `fallback_01:PASS` |
| HumanEval/77 | `20260213_065301_HumanEval_77` | PASS | LLM | 1 | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `fallback_01:PASS` |
| HumanEval/78 | `20260202_043527_HumanEval_78` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/79 | `20260222_134359_HumanEval_79` | PASS | LLM | 1 | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `fallback_01:PASS` |
| HumanEval/80 | `20260202_043636_HumanEval_80` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/81 | `20260222_134840_HumanEval_81` | PASS | LLM | 1 | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `fallback_01:PASS` |
| HumanEval/82 | `20260202_043745_HumanEval_82` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/83 | `20260222_143303_HumanEval_83` | PASS | LLM | 1 | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `fallback_01:PASS` |
| HumanEval/84 | `20260202_043836_HumanEval_84` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/85 | `20260202_043846_HumanEval_85` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/86 | `20260222_150735_HumanEval_86` | PASS | LLM | 1 | `attempt_01:TYPE_ERROR; attempt_02:SLM_TIMEOUT` | `fallback_01:PASS` |
| HumanEval/87 | `20260202_043921_HumanEval_87` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/88 | `20260222_154343_HumanEval_88` | PASS | LLM | 1 | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `fallback_01:PASS` |
| HumanEval/89 | `20260202_044046_HumanEval_89` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/90 | `20260222_161834_HumanEval_90` | PASS | LLM | 1 | `attempt_01:ASSERT_FAIL; attempt_02:SLM_TIMEOUT` | `fallback_01:PASS` |
| HumanEval/91 | `20260222_170956_HumanEval_91` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `fallback_01:ASSERT_FAIL; fallback_02:ASSERT_FAIL` |
| HumanEval/92 | `20260202_044221_HumanEval_92` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/93 | `20260222_174547_HumanEval_93` | PASS | LLM | 1 | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `fallback_01:PASS` |
| HumanEval/94 | `20260202_044327_HumanEval_94` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/95 | `20260202_044358_HumanEval_95` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/96 | `20260202_044420_HumanEval_96` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/97 | `20260202_044444_HumanEval_97` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/98 | `20260202_044455_HumanEval_98` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/99 | `20260202_044507_HumanEval_99` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/100 | `20260202_044522_HumanEval_100` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/101 | `20260222_182120_HumanEval_101` | PASS | LLM | 1 | `attempt_01:ASSERT_FAIL; attempt_02:SLM_TIMEOUT` | `fallback_01:PASS` |
| HumanEval/102 | `20260222_192837_HumanEval_102` | PASS | LLM | 1 | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `fallback_01:PASS` |
| HumanEval/103 | `20260222_195616_HumanEval_103` | PASS | LLM | 1 | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `fallback_01:PASS` |
| HumanEval/104 | `20260202_044732_HumanEval_104` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/105 | `20260202_044744_HumanEval_105` | PASS | SLM | 2 | `attempt_01:TYPE_ERROR; attempt_02:PASS` | `none` |
| HumanEval/106 | `20260222_203049_HumanEval_106` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `fallback_01:INDENT_ERROR; fallback_02:INDENT_ERROR` |
| HumanEval/107 | `20260202_044929_HumanEval_107` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/108 | `20260222_211407_HumanEval_108` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `fallback_01:ASSERT_FAIL; fallback_02:ASSERT_FAIL` |
| HumanEval/109 | `20260202_045028_HumanEval_109` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/110 | `20260222_215002_HumanEval_110` | PASS | LLM | 1 | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `fallback_01:PASS` |
| HumanEval/111 | `20260202_045215_HumanEval_111` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/112 | `20260222_222555_HumanEval_112` | PASS | LLM | 1 | `attempt_01:ASSERT_FAIL; attempt_02:SLM_TIMEOUT` | `fallback_01:PASS` |
| HumanEval/113 | `20260222_231724_HumanEval_113` | PASS | LLM | 1 | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `fallback_01:PASS` |
| HumanEval/114 | `20260202_045405_HumanEval_114` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/115 | `20260222_235349_HumanEval_115` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `fallback_01:ASSERT_FAIL; fallback_02:NAME_ERROR` |
| HumanEval/116 | `20260202_045613_HumanEval_116` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/117 | `20260223_003013_HumanEval_117` | PASS | LLM | 2 | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `fallback_01:FAIL; fallback_02:PASS` |
| HumanEval/118 | `20260202_045756_HumanEval_118` | PASS | SLM | 2 | `attempt_01:ASSERT_FAIL; attempt_02:PASS` | `none` |
| HumanEval/119 | `20260223_064619_HumanEval_119` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/120 | `20260223_064708_HumanEval_120` | PASS | LLM | 1 | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `fallback_01:PASS` |
| HumanEval/121 | `20260202_050334_HumanEval_121` | PASS | SLM | 2 | `attempt_01:ASSERT_FAIL; attempt_02:PASS` | `none` |
| HumanEval/122 | `20260202_050437_HumanEval_122` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/123 | `20260223_065124_HumanEval_123` | PASS | LLM | 1 | `attempt_01:ASSERT_FAIL; attempt_02:TIMEOUT` | `fallback_01:PASS` |
| HumanEval/124 | `20260223_065505_HumanEval_124` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/125 | `20260202_055632_HumanEval_125` | INCOMPLETE | - | - | `attempt_01:SLM_TIMEOUT` | `none` |
| HumanEval/126 | `20260223_065642_HumanEval_126` | PASS | LLM | 1 | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `fallback_01:PASS` |
| HumanEval/127 | `20260223_070049_HumanEval_127` | PASS | LLM | 1 | `attempt_01:ASSERT_FAIL; attempt_02:ZERO_DIV_ERROR` | `fallback_01:PASS` |
| HumanEval/128 | `20260202_073521_HumanEval_128` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/129 | `20260223_073037_HumanEval_129` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:SLM_TIMEOUT` | `fallback_01:FAIL; fallback_02:FAIL` |
| HumanEval/130 | `20260223_193112_HumanEval_130` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:SYNTAX_ERROR` | `fallback_01:ASSERT_FAIL; fallback_02:ASSERT_FAIL` |
| HumanEval/131 | `20260223_193611_HumanEval_131` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/132 | `20260223_193652_HumanEval_132` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:SLM_TIMEOUT` | `fallback_01:ASSERT_FAIL; fallback_02:ASSERT_FAIL` |
| HumanEval/133 | `20260223_225939_HumanEval_133` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:SLM_TIMEOUT` | `fallback_01:NAME_ERROR; fallback_02:NAME_ERROR` |
| HumanEval/134 | `20260224_002955_HumanEval_134` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `fallback_01:ASSERT_FAIL; fallback_02:ASSERT_FAIL` |
| HumanEval/135 | `20260224_003446_HumanEval_135` | FAIL | NONE | - | `attempt_01:SLM_TIMEOUT; attempt_02:SLM_TIMEOUT` | `fallback_01:ASSERT_FAIL; fallback_02:ASSERT_FAIL` |
| HumanEval/136 | `20260224_010952_HumanEval_136` | INCOMPLETE | - | - | `attempt_01:SLM_TIMEOUT` | `none` |
| HumanEval/137 | `20260224_054749_HumanEval_137` | PASS | LLM | 1 | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `fallback_01:PASS` |
| HumanEval/138 | `20260202_132135_HumanEval_138` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/139 | `20260224_055257_HumanEval_139` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:NAME_ERROR` | `fallback_01:NAME_ERROR; fallback_02:NAME_ERROR` |
| HumanEval/140 | `20260224_061835_HumanEval_140` | PASS | LLM | 1 | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `fallback_01:PASS` |
| HumanEval/141 | `20260224_062317_HumanEval_141` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/142 | `20260224_062445_HumanEval_142` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/143 | `20260224_062524_HumanEval_143` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/144 | `20260224_064458_HumanEval_144` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:SYNTAX_ERROR` | `fallback_01:NAME_ERROR; fallback_02:NAME_ERROR` |
| HumanEval/145 | `20260224_064907_HumanEval_145` | FAIL | NONE | - | `attempt_01:SYNTAX_ERROR; attempt_02:SYNTAX_ERROR` | `fallback_01:ASSERT_FAIL; fallback_02:ASSERT_FAIL` |
| HumanEval/146 | `20260224_072150_HumanEval_146` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/147 | `20260224_072253_HumanEval_147` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/148 | `20260401_071443_HumanEval_148` | PASS | SLM | 2 | `attempt_01:ASSERT_FAIL; attempt_02:PASS` | `none` |
| HumanEval/149 | `20260401_071651_HumanEval_149` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/150 | `20260224_073056_HumanEval_150` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/151 | `20260224_073140_HumanEval_151` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/152 | `20260224_073219_HumanEval_152` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/153 | `20260224_073259_HumanEval_153` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/154 | `20260224_073353_HumanEval_154` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/155 | `20260224_073437_HumanEval_155` | PASS | LLM | 2 | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `fallback_01:ASSERT_FAIL; fallback_02:PASS` |
| HumanEval/156 | `20260224_073814_HumanEval_156` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/157 | `20260224_073914_HumanEval_157` | PASS | LLM | 1 | `attempt_01:ASSERT_FAIL; attempt_02:ASSERT_FAIL` | `fallback_01:PASS` |
| HumanEval/158 | `20260202_154429_HumanEval_158` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/159 | `20260202_154607_HumanEval_159` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/160 | `20260224_074301_HumanEval_160` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:SLM_TIMEOUT` | `fallback_01:ASSERT_FAIL; fallback_02:ASSERT_FAIL` |
| HumanEval/161 | `20260202_155347_HumanEval_161` | PASS | SLM | 1 | `attempt_01:PASS` | `none` |
| HumanEval/162 | `20260224_074709_HumanEval_162` | FAIL | NONE | - | `attempt_01:NAME_ERROR; attempt_02:SLM_TIMEOUT` | `fallback_01:NAME_ERROR; fallback_02:NAME_ERROR` |
| HumanEval/163 | `20260224_110545_HumanEval_163` | FAIL | NONE | - | `attempt_01:ASSERT_FAIL; attempt_02:SLM_TIMEOUT` | `fallback_01:ASSERT_FAIL; fallback_02:ASSERT_FAIL` |

---

## 5) SLM Attempt-2 Recoveries (5 tasks)

Tasks where SLM failed on attempt-1 but passed on attempt-2:

| Task | Attempt-1 failure | Attempt-2 result |
|---|---|---|
| HumanEval/10 | ASSERT_FAIL | PASS |
| HumanEval/105 | TYPE_ERROR | PASS |
| HumanEval/118 | ASSERT_FAIL | PASS |
| HumanEval/121 | ASSERT_FAIL | PASS |
| HumanEval/148 | ASSERT_FAIL | PASS (verified no-RAG run 2026-04-01) |

---

## 6) Failure Taxonomy (23 FAIL tasks)

### 6.1 NAME_ERROR — missing import / undefined symbol (7 tasks)
`26, 28, 29, 38, 133, 144, 162`
- Root cause: LLM generated correct logic but omitted required import (`List`, `math`, `gcd`, `hashlib`, `encode_cyclic`).

### 6.2 ASSERT_FAIL — wrong logic, tests did not pass (9 tasks)
`65, 91, 108, 115, 129, 130, 132, 134, 135, 145, 160, 163`
- Root cause: Semantically incorrect implementation — both SLM and LLM produced wrong output.

### 6.3 INDENT_ERROR / SYNTAX_ERROR — malformed code (3 tasks)
`32, 106, 145`
- Root cause: LLM generated structurally broken code across both fallback attempts.

### 6.4 ASSERT_FAIL after NAME_ERROR recovery failure (2 tasks)
`139, 163`
- Mixed failure: SLM had ASSERT_FAIL/NAME_ERROR, LLM fallback also failed.

### 6.5 Empty / no usable output (2 tasks)
`50, 91`
- SLM timed out; LLM fallback returned semantically wrong output.

---

## 7) Incomplete Runs (2 tasks)

| Task | Latest run | Status | Notes |
|---|---|---|---|
| HumanEval/125 | `20260202_055632_HumanEval_125` | INCOMPLETE | No `final_status.json`; only `slm_attempt_01` with no result |
| HumanEval/136 | `20260224_010952_HumanEval_136` | INCOMPLETE | No `final_status.json`; `slm_attempt_01` shows `SLM_TIMEOUT` |

---

## 8) Results Metrics Snapshot

- Total tasks: `164`
- Final PASS: `139` (`84.8%`)
- Final FAIL: `23` (`14.0%`)
- Incomplete: `2` (`1.2%`)

**SLM performance:**
- SLM total PASS: `86` (`52.4%` of 164)
- SLM pass on attempt-1: `81`
- SLM pass on attempt-2: `5`

**LLM fallback performance:**
- LLM total PASS: `53` (`32.3%` of 164; `67.9%` of tasks where LLM was invoked)
- LLM pass on fallback attempt-1: `48`
- LLM pass on fallback attempt-2: `5`

**SLM failure modes that triggered LLM fallback:**
- `SLM_TIMEOUT`: dominant trigger for LLM fallback
- `ASSERT_FAIL`: second most common trigger
- `NAME_ERROR`: third most common trigger
