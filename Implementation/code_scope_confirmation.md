# Implementation Code Scope Confirmation (QuixBugs, HumanEval, BigCodeBench)

Date captured: 2026-03-14

## Confirmed Canonical Scripts for Thesis Implementation Section

### QuixBugs
- Primary scripts used in latest runs/analysis:
  - `src/step6_orchestrator_quixbugs_v5_attempts.py`
  - `src/step6_orchestrator_quixbugs_v6_attempts.py`
- Related runner/helper:
  - `src/quixbugs/run_quixbugs_python.py`
- Older variants present in repo (not canonical for final section):
  - `src/step6_orchestrator_quixbugs_v1.py`
  - `src/step6_orchestrator_quixbugs_v2_attempts.py`
  - `src/step6_orchestrator_quixbugs_v3_attempts.py`
  - `src/step6_orchestrator_quixbugs_v4_attempts.py`

### HumanEval
- Latest script to use/capture:
  - `src/humaneval/run_humaneval_hybrid_v2.py`
- Older script also present:
  - `src/humaneval/run_humaneval_hybrid.py`
- Version confirmation:
  - `v2` exists and is the latest in this repo.
  - `v3` script is **not** present in this repo.

### BigCodeBench
- Primary script used in runs/analysis:
  - `src/bigcodebench/run_bigcodebench_hybrid.py`
- Alternative/older variant present:
  - `src/bigcodebench/run_bigcodebench_hybrid_v2.py`

## Quick Verification Notes
- Repository evidence for recent documentation alignment:
  - `reports/hybrid_orchestrators_detailed_pseudocode_with_citations.md` references:
    - QuixBugs: v5 + v6
    - HumanEval: v2 (latest)
    - BigCodeBench: `run_bigcodebench_hybrid.py`
  - `reports/quixbug_runs_file.md` references QuixBugs v5/v6 runs.
  - `reports/humaneval_code_implementation_details.md` references HumanEval v2.
  - `reports/bigcode_runs_file.md` references `run_bigcodebench_hybrid.py`.

## Conclusion
- Your understanding is correct for QuixBugs: use `v5/v6`.
- For HumanEval, use **latest `v2`** (not `v3`).
- For BigCodeBench, use `run_bigcodebench_hybrid.py` as the primary implementation script.
