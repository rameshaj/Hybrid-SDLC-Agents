# HumanEval LLM Fallback Analysis (Network-Filtered, Task-Level)

Generated on: 2026-03-08
Method: remove infrastructure/network-access fallback failures when selecting evidence per task; if a task has network-failed fallback in one run, check other fallback runs for the same task and select best non-infra run.

## Task Universe
- Unique tasks found: **164** (HumanEval/0..HumanEval/163)
- Note: current artifacts contain 164 tasks, not 165/166.

## Selected Set: Tasks Where SLM Attempts Failed and Fallback Was Invoked
- Tasks in this set: **93**
- FALLBACK_PASS: **72**
- FALLBACK_FAIL_NON_INFRA: **21**
- FALLBACK_NO_RESULT_NON_INFRA: **0**
- FALLBACK_INFRA_ONLY: **0**

## All-Task Buckets (164 tasks)
- FALLBACK_FAIL_NON_INFRA: **21**
- FALLBACK_PASS: **72**
- NO_FALLBACK_SLM_PASS_ONLY: **71**

## Tasks Whose Latest Fallback Run Was Infra-Failed But Older Run Provided Usable Fallback Evidence
- Count: **1**
- HumanEval/129: latest=episodes/humaneval_runs/20260223_073037_HumanEval_129 -> chosen=episodes/humaneval_runs/20260221_074129_HumanEval_129 (FAIL, MISSING)

## Per-Task Results (SLM-failed + fallback-invoked set)
Columns: task_id | selected_run | slm1 | slm2 | fb1 | fb2 | final_bucket

- HumanEval/0 | episodes/humaneval_runs/20260212_064246_HumanEval_0 | NameError | NameError | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/1 | episodes/humaneval_runs/20260212_065147_HumanEval_1 | NameError | NameError | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/3 | episodes/humaneval_runs/20260206_071641_HumanEval_3 | NameError | NameError | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/4 | episodes/humaneval_runs/20260212_065551_HumanEval_4 | NameError | NameError | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/5 | episodes/humaneval_runs/20260212_070827_HumanEval_5 | NameError | NameError | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/6 | episodes/humaneval_runs/20260212_071808_HumanEval_6 | NameError | NameError | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/7 | episodes/humaneval_runs/20260212_073048_HumanEval_7 | NameError | NameError | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/8 | episodes/humaneval_runs/20260212_073415_HumanEval_8 | NameError | NameError | FAIL:NameError | PASS:PASS | FALLBACK_PASS
- HumanEval/9 | episodes/humaneval_runs/20260212_073753_HumanEval_9 | NameError | NameError | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/12 | episodes/humaneval_runs/20260212_074142_HumanEval_12 | NameError | NameError | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/14 | episodes/humaneval_runs/20260214_073154_HumanEval_14 | NameError | NameError | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/17 | episodes/humaneval_runs/20260213_071722_HumanEval_17 | NameError | NameError | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/19 | episodes/humaneval_runs/20260212_074839_HumanEval_19 | AssertionError|tail | AssertionError|tail | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/20 | episodes/humaneval_runs/20260213_073022_HumanEval_20 | NameError | NameError | FAIL:NameError | PASS:PASS | FALLBACK_PASS
- HumanEval/21 | episodes/humaneval_runs/20260213_073942_HumanEval_21 | NameError | NameError | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/22 | episodes/humaneval_runs/20260213_074751_HumanEval_22 | NameError | NameError | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/25 | episodes/humaneval_runs/20260213_075127_HumanEval_25 | NameError | NameError | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/26 | episodes/humaneval_runs/20260221_074016_HumanEval_26 | NO_CODE_EXTRACTED | NO_CODE_EXTRACTED | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/28 | episodes/humaneval_runs/20260222_060434_HumanEval_28 | NameError | NameError | FAIL:NameError | FAIL:NameError | FALLBACK_FAIL_NON_INFRA
- HumanEval/29 | episodes/humaneval_runs/20260222_060637_HumanEval_29 | NameError | NameError | FAIL:NameError | FAIL:NameError | FALLBACK_FAIL_NON_INFRA
- HumanEval/32 | episodes/humaneval_runs/20260222_060955_HumanEval_32 | SyntaxError | SyntaxError | FAIL:IndentationError | FAIL:IndentationError | FALLBACK_FAIL_NON_INFRA
- HumanEval/33 | episodes/humaneval_runs/20260213_075605_HumanEval_33 | TypeError | TypeError | FAIL:AssertionError|tail | PASS:PASS | FALLBACK_PASS
- HumanEval/37 | episodes/humaneval_runs/20260213_080041_HumanEval_37 | IndexError | TypeError | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/38 | episodes/humaneval_runs/20260222_064903_HumanEval_38 | NameError | SLM_TIMEOUT | FAIL:NameError | FAIL:NameError | FALLBACK_FAIL_NON_INFRA
- HumanEval/39 | episodes/humaneval_runs/20260222_102150_HumanEval_39 | SLM_TIMEOUT | SLM_TIMEOUT | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/46 | episodes/humaneval_runs/20260222_114758_HumanEval_46 | SLM_TIMEOUT | SLM_TIMEOUT | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/50 | episodes/humaneval_runs/20260222_115315_HumanEval_50 | SLM_TIMEOUT | SLM_TIMEOUT | FAIL:NameError | FAIL:NameError | FALLBACK_FAIL_NON_INFRA
- HumanEval/54 | episodes/humaneval_runs/20260212_074958_HumanEval_54 | AssertionError|tail | AssertionError|tail | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/64 | episodes/humaneval_runs/20260212_080911_HumanEval_64 | AssertionError | AssertionError | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/65 | episodes/humaneval_runs/20260222_122759_HumanEval_65 | SLM_TIMEOUT | SLM_TIMEOUT | FAIL:AssertionError|tail | FAIL:AssertionError|tail | FALLBACK_FAIL_NON_INFRA
- HumanEval/67 | episodes/humaneval_runs/20260213_082821_HumanEval_67 | ValueError | ValueError | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/69 | episodes/humaneval_runs/20260212_081415_HumanEval_69 | AssertionError|tail | AssertionError|tail | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/70 | episodes/humaneval_runs/20260212_081548_HumanEval_70 | AssertionError|tail | AssertionError|tail | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/71 | episodes/humaneval_runs/20260212_081734_HumanEval_71 | AssertionError | AssertionError | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/74 | episodes/humaneval_runs/20260222_123432_HumanEval_74 | SLM_TIMEOUT | SLM_TIMEOUT | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/75 | episodes/humaneval_runs/20260213_064248_HumanEval_75 | AssertionError|tail | AssertionError|tail | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/76 | episodes/humaneval_runs/20260222_130829_HumanEval_76 | SLM_TIMEOUT | SLM_TIMEOUT | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/77 | episodes/humaneval_runs/20260213_065301_HumanEval_77 | AssertionError | AssertionError | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/79 | episodes/humaneval_runs/20260222_134359_HumanEval_79 | SLM_TIMEOUT | SLM_TIMEOUT | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/81 | episodes/humaneval_runs/20260222_134840_HumanEval_81 | SLM_TIMEOUT | SLM_TIMEOUT | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/83 | episodes/humaneval_runs/20260222_143303_HumanEval_83 | SLM_TIMEOUT | SLM_TIMEOUT | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/86 | episodes/humaneval_runs/20260222_150735_HumanEval_86 | TypeError | SLM_TIMEOUT | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/88 | episodes/humaneval_runs/20260222_154343_HumanEval_88 | SLM_TIMEOUT | SLM_TIMEOUT | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/90 | episodes/humaneval_runs/20260222_161834_HumanEval_90 | AssertionError|tail | SLM_TIMEOUT | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/91 | episodes/humaneval_runs/20260222_170956_HumanEval_91 | SLM_TIMEOUT | SLM_TIMEOUT | FAIL:AssertionError | FAIL:AssertionError | FALLBACK_FAIL_NON_INFRA
- HumanEval/93 | episodes/humaneval_runs/20260222_174547_HumanEval_93 | SLM_TIMEOUT | SLM_TIMEOUT | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/101 | episodes/humaneval_runs/20260222_182120_HumanEval_101 | AssertionError|tail | SLM_TIMEOUT | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/102 | episodes/humaneval_runs/20260222_192837_HumanEval_102 | SLM_TIMEOUT | SLM_TIMEOUT | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/103 | episodes/humaneval_runs/20260222_195616_HumanEval_103 | SLM_TIMEOUT | SLM_TIMEOUT | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/106 | episodes/humaneval_runs/20260222_203049_HumanEval_106 | SLM_TIMEOUT | SLM_TIMEOUT | FAIL:IndentationError | FAIL:IndentationError | FALLBACK_FAIL_NON_INFRA
- HumanEval/108 | episodes/humaneval_runs/20260222_211407_HumanEval_108 | SLM_TIMEOUT | SLM_TIMEOUT | FAIL:AssertionError|tail | FAIL:AssertionError|tail | FALLBACK_FAIL_NON_INFRA
- HumanEval/110 | episodes/humaneval_runs/20260222_215002_HumanEval_110 | SLM_TIMEOUT | SLM_TIMEOUT | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/112 | episodes/humaneval_runs/20260222_222555_HumanEval_112 | AssertionError|tail | SLM_TIMEOUT | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/113 | episodes/humaneval_runs/20260222_231724_HumanEval_113 | SLM_TIMEOUT | SLM_TIMEOUT | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/115 | episodes/humaneval_runs/20260222_235349_HumanEval_115 | SLM_TIMEOUT | SLM_TIMEOUT | FAIL:AssertionError | FAIL:NameError | FALLBACK_FAIL_NON_INFRA
- HumanEval/117 | episodes/humaneval_runs/20260221_074112_HumanEval_117 | NO_CODE_EXTRACTED | NO_CODE_EXTRACTED | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/119 | episodes/humaneval_runs/20260221_074114_HumanEval_119 | NO_CODE_EXTRACTED | NO_CODE_EXTRACTED | FAIL:AssertionError|tail | MISSING:MISSING | FALLBACK_FAIL_NON_INFRA
- HumanEval/120 | episodes/humaneval_runs/20260223_064708_HumanEval_120 | AssertionError|tail | AssertionError|tail | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/123 | episodes/humaneval_runs/20260223_065124_HumanEval_123 | AssertionError|tail | TIMEOUT | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/124 | episodes/humaneval_runs/20260221_074120_HumanEval_124 | NO_CODE_EXTRACTED | NO_CODE_EXTRACTED | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/126 | episodes/humaneval_runs/20260223_065642_HumanEval_126 | AssertionError | AssertionError|tail | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/127 | episodes/humaneval_runs/20260223_070049_HumanEval_127 | AssertionError|tail | ZeroDivisionError | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/129 | episodes/humaneval_runs/20260221_074129_HumanEval_129 | NO_CODE_EXTRACTED | NO_CODE_EXTRACTED | FAIL:TIMEOUT | MISSING:MISSING | FALLBACK_FAIL_NON_INFRA
- HumanEval/130 | episodes/humaneval_runs/20260223_193112_HumanEval_130 | AssertionError|tail | SyntaxError | FAIL:AssertionError|tail | FAIL:AssertionError|tail | FALLBACK_FAIL_NON_INFRA
- HumanEval/131 | episodes/humaneval_runs/20260221_074139_HumanEval_131 | NO_CODE_EXTRACTED | NO_CODE_EXTRACTED | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/132 | episodes/humaneval_runs/20260223_193652_HumanEval_132 | AssertionError | SLM_TIMEOUT | FAIL:AssertionError|tail | FAIL:AssertionError|tail | FALLBACK_FAIL_NON_INFRA
- HumanEval/133 | episodes/humaneval_runs/20260223_225939_HumanEval_133 | NameError | SLM_TIMEOUT | FAIL:NameError | FAIL:NameError | FALLBACK_FAIL_NON_INFRA
- HumanEval/134 | episodes/humaneval_runs/20260224_002955_HumanEval_134 | SLM_TIMEOUT | SLM_TIMEOUT | FAIL:AssertionError|tail | FAIL:AssertionError|tail | FALLBACK_FAIL_NON_INFRA
- HumanEval/135 | episodes/humaneval_runs/20260224_003446_HumanEval_135 | SLM_TIMEOUT | SLM_TIMEOUT | FAIL:AssertionError|tail | FAIL:AssertionError|tail | FALLBACK_FAIL_NON_INFRA
- HumanEval/136 | episodes/humaneval_runs/20260221_074148_HumanEval_136 | NO_CODE_EXTRACTED | NO_CODE_EXTRACTED | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/137 | episodes/humaneval_runs/20260224_054749_HumanEval_137 | AssertionError|tail | AssertionError|tail | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/139 | episodes/humaneval_runs/20260221_074151_HumanEval_139 | NO_CODE_EXTRACTED | NO_CODE_EXTRACTED | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/140 | episodes/humaneval_runs/20260224_061835_HumanEval_140 | AssertionError | AssertionError | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/141 | episodes/humaneval_runs/20260221_074155_HumanEval_141 | NO_CODE_EXTRACTED | NO_CODE_EXTRACTED | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/142 | episodes/humaneval_runs/20260221_074157_HumanEval_142 | NO_CODE_EXTRACTED | NO_CODE_EXTRACTED | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/143 | episodes/humaneval_runs/20260221_074159_HumanEval_143 | NO_CODE_EXTRACTED | NO_CODE_EXTRACTED | FAIL:NameError | MISSING:MISSING | FALLBACK_FAIL_NON_INFRA
- HumanEval/144 | episodes/humaneval_runs/20260221_074202_HumanEval_144 | NO_CODE_EXTRACTED | NO_CODE_EXTRACTED | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/145 | episodes/humaneval_runs/20260224_064907_HumanEval_145 | SyntaxError | SyntaxError | FAIL:AssertionError|tail | FAIL:AssertionError|tail | FALLBACK_FAIL_NON_INFRA
- HumanEval/146 | episodes/humaneval_runs/20260221_074206_HumanEval_146 | NO_CODE_EXTRACTED | NO_CODE_EXTRACTED | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/147 | episodes/humaneval_runs/20260221_074209_HumanEval_147 | NO_CODE_EXTRACTED | NO_CODE_EXTRACTED | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/148 | episodes/humaneval_runs/20260221_074211_HumanEval_148 | NO_CODE_EXTRACTED | NO_CODE_EXTRACTED | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/149 | episodes/humaneval_runs/20260221_074214_HumanEval_149 | NO_CODE_EXTRACTED | NO_CODE_EXTRACTED | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/150 | episodes/humaneval_runs/20260221_074215_HumanEval_150 | NO_CODE_EXTRACTED | NO_CODE_EXTRACTED | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/151 | episodes/humaneval_runs/20260221_074217_HumanEval_151 | NO_CODE_EXTRACTED | NO_CODE_EXTRACTED | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/152 | episodes/humaneval_runs/20260221_074218_HumanEval_152 | NO_CODE_EXTRACTED | NO_CODE_EXTRACTED | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/153 | episodes/humaneval_runs/20260221_074220_HumanEval_153 | NO_CODE_EXTRACTED | NO_CODE_EXTRACTED | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/154 | episodes/humaneval_runs/20260221_074222_HumanEval_154 | NO_CODE_EXTRACTED | NO_CODE_EXTRACTED | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/155 | episodes/humaneval_runs/20260224_073437_HumanEval_155 | AssertionError|tail | AssertionError|tail | FAIL:AssertionError|tail | PASS:PASS | FALLBACK_PASS
- HumanEval/156 | episodes/humaneval_runs/20260221_074226_HumanEval_156 | NO_CODE_EXTRACTED | NO_CODE_EXTRACTED | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/157 | episodes/humaneval_runs/20260224_073914_HumanEval_157 | AssertionError|tail | AssertionError|tail | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/160 | episodes/humaneval_runs/20260221_074229_HumanEval_160 | NO_CODE_EXTRACTED | NO_CODE_EXTRACTED | PASS:PASS | MISSING:MISSING | FALLBACK_PASS
- HumanEval/162 | episodes/humaneval_runs/20260224_074709_HumanEval_162 | NameError | SLM_TIMEOUT | FAIL:NameError | FAIL:NameError | FALLBACK_FAIL_NON_INFRA
- HumanEval/163 | episodes/humaneval_runs/20260224_110545_HumanEval_163 | AssertionError | SLM_TIMEOUT | FAIL:AssertionError | FAIL:AssertionError | FALLBACK_FAIL_NON_INFRA
