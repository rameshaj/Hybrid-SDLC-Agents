# QuixBugs Initial Sweep Deep Analysis (SLM Attempt-1 vs Attempt-2)

Generated on: 2026-03-09  
Workspace: `/Users/ajayramesh/Documents/AIML/Masteers/ThesisImplementation/thesis-hybrid-sdlc-agent`

## 1) What This Analysis Covers

This report mirrors the HumanEval SLM-attempt analysis format and answers:

1. How many QuixBugs tasks passed on SLM attempt-1 and attempt-2?
2. What kinds of tasks passed vs failed?
3. What failure types dominated?
4. Did attempt-2 recover additional tasks?
5. How does this align with Reflexion-style iterative repair?

## 2) Data and Method

Intended primary sources:

- `episodes/quixbugs_runs/attempts/<timestamp>_<algo>/...`
- `final_status.txt`, `attempt_01/*`, `attempt_02/*`, ...

Current availability check:

- `episodes/quixbugs_runs/attempts` is currently missing.
- `reports/session_summary.md` explicitly records deletion of `episodes/quixbugs_runs`.

Still available supporting sources:

- `data/quixbugs_tasks_v2.jsonl` (41-task manifest)
- `src/step6_orchestrator_quixbugs_v5_attempts.py` (latest runtime logic)

Coverage currently observable:

- Unique tasks in manifest: **41**
- `test_timeout_s` distribution: **32 tasks at 3s**, **9 tasks at 10s**
- Validation mode mix:
  - **32** tasks via `src/quixbugs/run_quixbugs_python.py`
  - **9** tasks via dedicated `python_programs/*_test.py` drivers

Important note:

- Because run artifacts were deleted, attempt-level PASS/FAIL metrics are not reconstructable from local evidence at this time.

## 3) Core Results (Current Artifact State)

Outcome by first run per task (n=41 expected):

- PASS via SLM attempt 1: **N/A (missing run artifacts)**
- PASS via SLM attempt 2: **N/A (missing run artifacts)**
- FAIL after SLM attempts: **N/A (missing run artifacts)**

Attempt-2 salvage rate:

- **N/A until `episodes/quixbugs_runs/attempts` is restored or regenerated**

## 4) Failure Taxonomy (Grouped)

### 4.1 Attempt-1 failure types

- **N/A (no surviving QuixBugs attempt logs)**

### 4.2 Attempt-2 terminal failure types

- **N/A (no surviving QuixBugs attempt logs)**

### 4.3 What is still inferable from code

From `src/step6_orchestrator_quixbugs_v5_attempts.py`, SLM attempt failures can arise from:

- `BAD_DIFF`
- `BAD_DIFF_FORMAT`
- `PATCH_APPLY_FAIL: ...`
- post-test functional failure (`FAIL: ...` tail)
- generation timeout / subprocess timeout behavior in SLM call

## 5) “Was Most Code Proper but Minor Issues Broke It?”

This cannot be measured empirically right now because we do not have `attempt_*/slm_raw.txt`, `diff_sanitized.txt`, and `test_after.txt` artifacts for QuixBugs runs.

What the pipeline design suggests:

1. It separates non-code failures (`BAD_DIFF`, patch apply failures) from executable-but-wrong code (`FAIL: ...` after post-test).
2. It records enough per-attempt data to answer this exactly once runs are available.

## 6) Task-Type Grouping (Heuristic, from Manifest)

Using algorithm-name heuristics over `data/quixbugs_tasks_v2.jsonl`:

- DP/Combinatorics: **11**
- Graph/Traversal: **9**
- Math/Numeric/Other: **8**
- Sorting/Selection: **7**
- String/Parsing/List: **6**

Interpretation:

- The benchmark mix is broad and includes structurally harder graph tasks (the 9 tasks configured with dedicated test drivers and longer timeout).

## 7) Deep Dive: The Attempt-2 Recovered Tasks

Recovered-on-attempt-2 task list:

- **N/A (run folders deleted, so exact recovered task IDs cannot be confirmed from local artifacts)**

Evidence gap detail:

- No `episodes/quixbugs_runs/attempts/<run>/attempt_01` and `attempt_02` directories are present to compare first-fail vs second-pass transitions.

## 8) Positive Signal First: Why Attempt-2 Recovery Is Still Expected

Even without surviving QuixBugs logs, the v5 implementation is explicitly iterative:

1. Attempt-N failure is summarized in `prev_status`.
2. Attempt-N+1 prompt includes that prior failure summary.
3. This is a direct Reflexion-style retry loop.

So the design is capable of attempt-2 recovery; the missing piece is the deleted evidence needed to quantify it.

## 9) Data-Backed View of What We Can Confirm Today

Confirmed now (artifact-backed):

- Task universe: **41**
- Timeout shaping: **3s (32 tasks)**, **10s (9 tasks)**
- Driver split: **custom runner 32**, **dedicated driver 9**
- Orchestrator supports configurable attempts (`--max_attempts`, default 5; can be set to 2 for HumanEval-style comparison)

Not confirmable now:

- Attempt-1 pass count
- Attempt-2 incremental pass count
- Per-error recovery rates

## 10) Why Tasks Typically Fail on Attempt-2 (Code-Informed Risk Model)

Based on v5 control flow, persistent failures usually come from:

1. Diff quality failures (no valid unified diff or malformed hunks).
2. Patch apply failures (context mismatch even after sanitization/repair).
3. Algorithmic mismatch that remains after one retry (post-test still failing).
4. Time-budget pressure on harder graph/object tasks.

## 11) Deep Interpretation for Thesis Narrative

For thesis reporting, the safe claim from current evidence is:

1. QuixBugs pipeline implements a bona-fide iterative SLM repair loop.
2. It is instrumented for attempt-level evaluation.
3. Quantitative SLM attempt-1 vs attempt-2 outcomes are currently unavailable due artifact deletion, not due missing instrumentation.

## 12) Design Implications from Available Evidence

1. Keep attempt-2 retry enabled because pipeline already carries structured failure feedback.
2. Preserve run artifacts (`episodes/quixbugs_runs/attempts`) before cleanup; they are the only source for rigorous attempt-level analysis.
3. Maintain the v2 task manifest timeout split; graph tasks need longer budget.
4. For strict comparability with HumanEval SLM report, run QuixBugs with `--max_attempts 2` and archive summaries immediately.

## 13) Literature Mapping (Primary Sources)

1. Reflexion: Language Agents with Verbal Reinforcement Learning  
   `https://arxiv.org/abs/2303.11366`
2. Self-Refine: Iterative Refinement with Self-Feedback  
   `https://arxiv.org/abs/2303.17651`
3. Teaching Large Language Models to Self-Debug  
   `https://arxiv.org/abs/2304.05128`
4. ReAct: Synergizing Reasoning and Acting in Language Models  
   `https://arxiv.org/abs/2210.03629`
5. SWE-agent: Agent-computer interface patterns for software tasks  
   `https://arxiv.org/abs/2405.15793`

## 14) Final Thesis-Ready Summary

QuixBugs SLM attempt analysis is structurally prepared and methodologically aligned with your HumanEval analysis format, but numeric attempt-1 vs attempt-2 outcomes are currently **not recoverable** from local artifacts because `episodes/quixbugs_runs` was deleted.

What is confirmed now:

- 41-task QuixBugs task universe (`data/quixbugs_tasks_v2.jsonl`)
- mixed timeout/test-driver design for harder graph tasks
- iterative failure-aware retry logic in v5 orchestrator

What is pending:

- empirical pass/fail and recovery statistics from regenerated or restored run artifacts.

## 15) Appendix: Evidence Pointers + Repro Steps

Primary evidence files used now:

- `reports/session_summary.md`
- `data/quixbugs_tasks_v2.jsonl`
- `src/step6_orchestrator_quixbugs_v5_attempts.py`

Current artifact-state check used:

```bash
python - <<'PY'
from pathlib import Path
p = Path("episodes/quixbugs_runs/attempts")
print("exists", p.exists())
print("run_dirs", sum(1 for x in p.iterdir() if x.is_dir()) if p.exists() else 0)
PY
```

Recommended regeneration command (HumanEval-style 2-attempt SLM comparison):

```bash
for i in $(seq 0 40); do
  python src/step6_orchestrator_quixbugs_v5_attempts.py \
    --tasks_path data/quixbugs_tasks_v2.jsonl \
    --task_index "$i" \
    --llama_path /usr/local/bin/llama-completion \
    --gguf_model_path models/gguf/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf \
    --max_attempts 2 \
    --fallback_model ""
done
```

Minimal metrics extraction once runs exist:

```bash
python - <<'PY'
from pathlib import Path
from collections import Counter
root = Path("episodes/quixbugs_runs/attempts")
if not root.exists():
    raise SystemExit("No quixbugs runs found")
rows = []
for run in sorted([p for p in root.iterdir() if p.is_dir()]):
    final = (run / "final_status.txt").read_text(encoding="utf-8", errors="replace").strip() if (run / "final_status.txt").exists() else "MISSING"
    slm_attempts = sorted([p for p in run.iterdir() if p.is_dir() and p.name.startswith("attempt_")])
    fb_attempts = sorted([p for p in run.iterdir() if p.is_dir() and p.name.startswith("fallback_")])
    if final == "PASS" and not fb_attempts and slm_attempts:
        winner = f"SLM_ATTEMPT_{slm_attempts[-1].name.split('_')[-1]}"
    elif final == "PASS" and fb_attempts:
        winner = "FALLBACK_PASS"
    else:
        winner = "FAIL_OR_OTHER"
    rows.append((run.name, final, winner))

c = Counter(w for _,_,w in rows)
print("total_runs:", len(rows))
print("winners:", dict(c))
PY
```
