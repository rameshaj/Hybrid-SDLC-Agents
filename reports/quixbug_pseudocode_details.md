# QuixBugs v5 Implementation Details (Latest Code Only)

Generated on: 2026-03-08  
Project root: `/Users/ajayramesh/Documents/AIML/Masteers/ThesisImplementation/thesis-hybrid-sdlc-agent`

## 1) Scope (Latest Code Only)

This document analyzes only the latest QuixBugs repair pipeline implementation:

- `src/step6_orchestrator_quixbugs_v5_attempts.py`

Supporting runtime modules used by v5:

- `src/quixbugs/run_quixbugs_python.py`
- `src/llm_fallback_openai.py`
- `data/quixbugs_tasks_v2.jsonl`

This note does not rely on older v3/v4 behavior except where needed for context.

## 2) What v5 Does (One-Line Summary)

For one QuixBugs task, v5 runs:

1. baseline test,
2. iterative SLM patch attempts (`attempt_01..N`),
3. optional LLM fallback attempts (`fallback_01..M`) if SLM fails,
4. writes `final_status.txt` as `PASS`, `FAIL`, or `ALREADY_PASS`.

## 3) Detailed Execution Pseudocode (v5)

```python
def main():
    args = parse_cli_args(
        tasks_path,
        task_index,
        llama_path,
        gguf_model_path,
        max_attempts=5,
        slm_timeout_s=900,
        slm_max_output_mb=8,
        skip_rollback=False,
        fallback_model="",
        fallback_max_attempts=2,
        fallback_timeout_s=120,
        fallback_max_new_tokens=1200,
        fallback_temp=0.0,
        repo_root=".",
    )

    # 1) Load selected task row from JSONL
    task = read_jsonl_line(args.tasks_path, args.task_index)
    test_cmd = task["test_cmd"]
    test_timeout = max(int(task.get("test_timeout_s", 3)), 10)
    qb_repo = Path(task["quixbugs_dir"]).resolve()
    buggy_abs = repo_root / task["buggy_path"]

    run_dir = episodes/quixbugs_runs/attempts/<timestamp>_<algo>
    mkdir(run_dir)

    # 2) Fallback guard
    if args.fallback_model and OPENAI_API_KEY not set:
        write(run_dir/"fallback_status.txt", "ERROR_NO_OPENAI_API_KEY")
        return 2

    # 3) Baseline test (no patch yet)
    rc0, out0, err0 = run_cmd(test_cmd, timeout=test_timeout)
    write(run_dir/"test_before.txt", out0+err0)
    if rc0 == 0:
        write(run_dir/"final_status.txt", "ALREADY_PASS")
        return 0

    prev_status = "INIT"
    slm_attempt_summaries = []

    # 4) SLM loop
    for k in range(1, max_attempts+1):
        ad = run_dir / f"attempt_{k:02d}"
        mkdir(ad)

        if not skip_rollback:
            run_cmd(qb_rollback(task), timeout=30)

        rc_pre, o_pre, e_pre = run_cmd(test_cmd, timeout=test_timeout)
        write(ad/"test_pre.txt", o_pre+e_pre)

        prompt = build_prompt(
            task=task,
            buggy=read_text(buggy_abs),
            failing=o_pre+e_pre,
            attempt=k,
            max_attempts=max_attempts,
            prev=prev_status,
        )
        write(ad/"prompt.txt", prompt)

        # SLM generation
        rc_slm, dt = run_slm(
            llama_path, gguf_model_path, ad/"prompt.txt",
            timeout=slm_timeout_s, max_output_mb=slm_max_output_mb
        )
        # raw/error are written to slm_raw.txt and slm_err.txt

        diff = extract_slm_diff(read(ad/"slm_raw.txt"))
        if not diff:
            prev_status = "BAD_DIFF"
            slm_attempt_summaries.append(f"attempt_{k:02d}: {prev_status}")
            continue

        diff, sanitized, err = sanitize_slm_diff(diff)
        if not diff:
            prev_status = f"BAD_DIFF_FORMAT: {err}"
            slm_attempt_summaries.append(f"attempt_{k:02d}: {prev_status}")
            continue
        if sanitized:
            write(ad/"diff_sanitized.txt", diff)

        ok, method, reason = apply_patch(
            diff=diff,
            repo=qb_repo,
            target_rel=qb_relpath(task),
            out_dir=ad,
            repair=True,
            validate_context=True,
        )
        if not ok:
            prev_status = f"PATCH_APPLY_FAIL: {reason}"
            slm_attempt_summaries.append(f"attempt_{k:02d}: {prev_status}")
            continue

        rc_post, o_post, e_post = run_cmd(test_cmd, timeout=test_timeout)
        write(ad/"test_after.txt", o_post+e_post)

        if rc_post == 0:
            write(run_dir/"final_status.txt", "PASS")
            return 0

        prev_status = "FAIL: <tail_of_test_output>"
        slm_attempt_summaries.append(f"attempt_{k:02d}: {prev_status}")

    # 5) Optional fallback loop
    if args.fallback_model:
        fallback_attempt_summaries = []
        for fk in range(1, fallback_max_attempts+1):
            fd = run_dir / f"fallback_{fk:02d}"
            mkdir(fd)

            if not skip_rollback:
                run_cmd(qb_rollback(task), timeout=30)

            rc_pre, o_pre, e_pre = run_cmd(test_cmd, timeout=test_timeout)
            write(fd/"test_pre.txt", o_pre+e_pre)

            fb_prompt = build_fallback_prompt(
                task=task,
                buggy=read_text(buggy_abs),
                failing=o_pre+e_pre,
                slm_attempt_summaries=slm_attempt_summaries,
                fallback_attempt_summaries=fallback_attempt_summaries,
            )
            write(fd/"prompt.txt", fb_prompt)

            try:
                llm_out, meta = openai_chat_completion(
                    fb_prompt,
                    model=fallback_model,
                    temperature=fallback_temp,
                    max_tokens=fallback_max_new_tokens,
                    timeout_s=fallback_timeout_s,
                )
                write(fd/"llm_raw.txt", llm_out)
            except Exception as e:
                status = f"FALLBACK_ERROR: {type(e).__name__}: {e}"
                write(fd/"status.txt", status)
                fallback_attempt_summaries.append(f"fallback_{fk:02d}: {status}")
                continue

            diff, sanitized, err = extract_fallback_diff(llm_out)
            if not diff:
                status = f"FALLBACK_BAD_DIFF_FORMAT: {err}"
                write(fd/"status.txt", status)
                fallback_attempt_summaries.append(f"fallback_{fk:02d}: {status}")
                continue
            if sanitized:
                write(fd/"diff_sanitized.txt", diff)

            ok, method, reason = apply_patch(
                diff=diff,
                repo=qb_repo,
                target_rel=qb_relpath(task),
                out_dir=fd,
                repair=False,
                validate_context=False,
            )
            if not ok:
                status = f"FALLBACK_PATCH_APPLY_FAIL: {reason}"
                write(fd/"status.txt", status)
                fallback_attempt_summaries.append(f"fallback_{fk:02d}: {status}")
                continue

            rc_post, o_post, e_post = run_cmd(test_cmd, timeout=test_timeout)
            write(fd/"test_after.txt", o_post+e_post)
            if rc_post == 0:
                write(run_dir/"final_status.txt", "PASS")
                return 0

            status = "FALLBACK_FAIL"
            write(fd/"status.txt", status)
            fallback_attempt_summaries.append(f"fallback_{fk:02d}: {status}")

    # 6) If no pass
    write(run_dir/"final_status.txt", "FAIL")
    return 1
```

## 4) Core Internal Algorithms (v5)

### 4.1 Diff extraction and cleanup

`extract_slm_diff()` and `extract_fallback_diff()` enforce a strict patch pipeline:

1. locate `diff --git` segment,
2. normalize hunk structure,
3. fix malformed hunk lines,
4. remove no-op hunks,
5. recompute hunk line counts,
6. validate hunk format.

This is intentionally defensive because raw model output is often noisy or incomplete.

### 4.2 Patch application strategy

`apply_patch()` tries, in order:

1. `git apply --3way`
2. `git apply`
3. `patch -p1`
4. `patch -p0`

In SLM mode, v5 can attempt context-aware patch repair if direct apply fails.

### 4.3 Rollback strategy

Before each attempt (unless `--skip_rollback`), v5 restores the buggy file with:

- `git -C <quixbugs_dir> checkout -- <relative_buggy_file>`

This ensures each attempt starts from the same buggy baseline.

## 5) How It Is Run (Exact)

### 5.1 Prerequisites

- QuixBugs checked out at `data/external/QuixBugs`
- task manifest available (recommended): `data/quixbugs_tasks_v2.jsonl`
- local GGUF model file present (example):
  - `models/gguf/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf`
- llama binary path available:
  - preferred: `/usr/local/bin/llama-completion`

If using fallback:

- `OPENAI_API_KEY` must be set

### 5.2 Single task, SLM-only

```bash
python src/step6_orchestrator_quixbugs_v5_attempts.py \
  --tasks_path data/quixbugs_tasks_v2.jsonl \
  --task_index 0 \
  --llama_path /usr/local/bin/llama-completion \
  --gguf_model_path models/gguf/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf \
  --max_attempts 3 \
  --slm_timeout_s 400 \
  --repo_root .
```

### 5.3 Single task, SLM + fallback

```bash
OPENAI_API_KEY=... \
python src/step6_orchestrator_quixbugs_v5_attempts.py \
  --tasks_path data/quixbugs_tasks_v2.jsonl \
  --task_index 0 \
  --llama_path /usr/local/bin/llama-completion \
  --gguf_model_path models/gguf/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf \
  --max_attempts 3 \
  --slm_timeout_s 400 \
  --fallback_model gpt-4.1 \
  --fallback_max_attempts 2 \
  --fallback_timeout_s 120 \
  --repo_root .
```

### 5.4 Multi-task batch (shell loop)

```bash
for i in $(seq 0 40); do
  python src/step6_orchestrator_quixbugs_v5_attempts.py \
    --tasks_path data/quixbugs_tasks_v2.jsonl \
    --task_index "$i" \
    --llama_path /usr/local/bin/llama-completion \
    --gguf_model_path models/gguf/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf \
    --max_attempts 3 \
    --slm_timeout_s 400 \
    --fallback_model gpt-4.1 \
    --fallback_max_attempts 2
done
```

## 6) Output Artifact Contract (v5)

Run root:

- `episodes/quixbugs_runs/attempts/<timestamp>_<algo>/`

Top-level files:

- `test_before.txt`
- `final_status.txt` (`ALREADY_PASS`, `PASS`, `FAIL`)
- optional `fallback_status.txt` (for missing API key guard)

SLM attempt folder (`attempt_01`, etc):

- `prompt.txt`
- `slm_raw.txt`, `slm_err.txt`
- `test_pre.txt`, `test_after.txt`
- optional patch diagnostics:
  - `diff_sanitized.txt`
  - `applied_diff_actual.diff`
  - `patch_apply_err.txt`
  - `diff_repaired.txt`

Fallback folder (`fallback_01`, etc):

- `prompt.txt`
- `llm_raw.txt`
- `status.txt`
- `test_pre.txt`, `test_after.txt`
- optional patch diagnostics as above

## 7) Inspiration Mapping (Inferred from Code Behavior)

This section is based on implementation behavior; these papers are not explicitly cited inside the source code.

1. **Generate-and-Validate APR paradigm**  
   Why: v5 iterates candidate patches and validates by running tests each attempt.

2. **Iterative self-repair with feedback (Reflexion / Self-Refine / Self-Debug style)**  
   Why: attempt prompts include previous failure summaries; later attempts condition on test outcomes.

3. **Cascade routing (small model first, stronger fallback second)**  
   Why: SLM is primary repair path; cloud fallback is only invoked after SLM failure.

4. **Agentic tool loop (ReAct/SWE-agent style pattern)**  
   Why: model generation is tightly coupled with external tools (`git`, patch application, test runner).

Primary references often used for this framing:

- Reflexion: `https://arxiv.org/abs/2303.11366`
- Self-Refine: `https://arxiv.org/abs/2303.17651`
- Self-Debugging: `https://arxiv.org/abs/2304.05128`
- ReAct: `https://arxiv.org/abs/2210.03629`
- SWE-agent: `https://arxiv.org/abs/2405.15793`
- FrugalGPT (cascade perspective): `https://arxiv.org/abs/2305.05176`

## 8) Practical Clarification

This document is implementation-level and independent of historical result counts.  
In the current workspace snapshot, old `episodes/quixbugs_runs` results are not present, so this file captures **how v5 runs**, not retrospective pass/fail statistics.

