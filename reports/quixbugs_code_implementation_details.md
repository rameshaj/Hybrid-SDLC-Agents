# QuixBugs Code Implementation Details (Orchestrator + Fallback)

Generated on: 2026-03-08  
Project root: `/Users/ajayramesh/Documents/AIML/Masteers/ThesisImplementation/thesis-hybrid-sdlc-agent`

## 1) Scope

This note captures the **detailed pseudocode-level implementation** for QuixBugs in this repository, including:

- SLM attempt loop
- LLM fallback loop
- diff extraction/sanitization/patch-apply flow
- test execution contract
- run artifact structure

This is the QuixBugs equivalent of the HumanEval implementation documentation.

## 2) Main QuixBugs Implementation Files

- `src/step6_orchestrator_quixbugs_v3_attempts.py`
- `src/step6_orchestrator_quixbugs_v4_attempts.py`
- `src/step6_orchestrator_quixbugs_v5_attempts.py`
- `src/quixbugs/run_quixbugs_python.py`
- `tools/summarize_quixbugs_attempt_run.py`

Related task manifests:

- `data/quixbugs_tasks.jsonl`
- `data/quixbugs_tasks_v2.jsonl`

## 3) Versioned Flow (What Each Orchestrator Adds)

### v3 (`step6_orchestrator_quixbugs_v3_attempts.py`)

- Multi-attempt SLM patch loop
- diff extraction and patch apply
- previous failure details fed into next SLM prompt
- **no cloud fallback loop**

### v4 (`step6_orchestrator_quixbugs_v4_attempts.py`)

- v3 behavior plus:
  - cloud LLM fallback loop after SLM attempts fail
  - stronger diff sanitization/validation/repair
  - fallback prompt with SLM + fallback failure summaries

### v5 (`step6_orchestrator_quixbugs_v5_attempts.py`)

- v4 behavior plus:
  - auto-resolve `llama-completion` binary when available
  - avoid `-no-cnv` flag issues from older llama-cli invocation patterns

For thesis documentation, v5 is the most complete operational specification.

## 4) Detailed Pseudocode: QuixBugs v5 Orchestrator

```python
def main():
    args = parse_args(
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

    task = read_jsonl_line(tasks_path, task_index)
    qb_repo = Path(task["quixbugs_dir"])
    buggy_abs = repo_root / task["buggy_path"]
    test_cmd = task["test_cmd"]
    test_timeout = max(task.get("test_timeout_s", 3), 10)

    run_dir = episodes/quixbugs_runs/attempts/<timestamp>_<algo>
    save metadata/log roots

    # Optional fallback guard
    if fallback_model is set and OPENAI_API_KEY missing:
        write run_dir/fallback_status.txt = ERROR_NO_OPENAI_API_KEY
        exit(2)

    # ---------- BASELINE ----------
    rc0, out0, err0 = run_cmd(test_cmd, timeout=test_timeout)
    write run_dir/test_before.txt
    if rc0 == 0:
        write run_dir/final_status.txt = ALREADY_PASS
        exit(0)

    prev_status = "INIT"
    slm_attempt_summaries = []

    # ---------- SLM LOOP ----------
    for k in 1..max_attempts:
        ad = run_dir/attempt_<k>
        if not skip_rollback:
            run_cmd(qb_rollback(task))

        rc_pre, out_pre, err_pre = run_cmd(test_cmd)
        write ad/test_pre.txt

        buggy = load_text(buggy_abs)
        prompt = build_prompt(
            task=task,
            buggy=buggy,
            failing=(out_pre + err_pre),
            attempt=k,
            max_attempts=max_attempts,
            prev=prev_status,
        )
        write ad/prompt.txt

        rc_slm, dt = run_slm(
            llama_path, gguf_model_path, prompt_file=ad/prompt.txt,
            timeout=slm_timeout_s, output_cap=slm_max_output_mb
        )
        write ad/slm_raw.txt, ad/slm_err.txt

        diff = extract_slm_diff(slm_raw)
        if no diff:
            prev_status = "BAD_DIFF"
            slm_attempt_summaries += f"attempt_{k}: BAD_DIFF"
            continue

        diff, sanitized, err = sanitize_slm_diff(diff)
        if invalid format:
            prev_status = f"BAD_DIFF_FORMAT: {err}"
            slm_attempt_summaries += ...
            continue
        if sanitized:
            write ad/diff_sanitized.txt

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
            slm_attempt_summaries += ...
            continue

        rc_post, out_post, err_post = run_cmd(test_cmd)
        write ad/test_after.txt

        if rc_post == 0:
            write run_dir/final_status.txt = PASS
            exit(0)
        else:
            prev_status = "FAIL: <tail_of_test_output>"
            slm_attempt_summaries += ...

    # ---------- FALLBACK LOOP ----------
    if fallback_model is set:
        fallback_attempt_summaries = []
        for fk in 1..fallback_max_attempts:
            fd = run_dir/fallback_<fk>
            if not skip_rollback:
                run_cmd(qb_rollback(task))

            rc_pre, out_pre, err_pre = run_cmd(test_cmd)
            write fd/test_pre.txt

            fb_prompt = build_fallback_prompt(
                task=task,
                buggy=load_text(buggy_abs),
                failing=(out_pre + err_pre),
                slm_attempt_summaries=slm_attempt_summaries,
                fallback_attempt_summaries=fallback_attempt_summaries,
            )
            write fd/prompt.txt

            try:
                llm_out = openai_chat_completion(
                    prompt=fb_prompt,
                    model=fallback_model,
                    temperature=fallback_temp,
                    max_tokens=fallback_max_new_tokens,
                    timeout_s=fallback_timeout_s,
                )
                write fd/llm_raw.txt
            except Exception as e:
                status = f"FALLBACK_ERROR: {type(e).__name__}: {e}"
                write fd/status.txt
                fallback_attempt_summaries += status
                continue

            diff, sanitized, err = extract_fallback_diff(llm_out)
            if no valid diff:
                status = f"FALLBACK_BAD_DIFF_FORMAT: {err}"
                write fd/status.txt
                fallback_attempt_summaries += status
                continue

            if sanitized:
                write fd/diff_sanitized.txt

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
                write fd/status.txt
                fallback_attempt_summaries += status
                continue

            rc_post, out_post, err_post = run_cmd(test_cmd)
            write fd/test_after.txt
            if rc_post == 0:
                write run_dir/final_status.txt = PASS
                exit(0)

            write fd/status.txt = FALLBACK_FAIL
            fallback_attempt_summaries += FALLBACK_FAIL

    # ---------- FINAL ----------
    write run_dir/final_status.txt = FAIL
    exit(1)
```

## 5) Detailed Subsystems (Behavioral Notes)

### 5.1 Prompt strategy

`build_prompt(...)` includes:

- exact target file path (`a/...` and `b/...`)
- attempt counter and previous status
- buggy code context (full file or line-window around failing line)
- failing test output

`build_fallback_prompt(...)` includes:

- strict unified-diff rules
- cumulative SLM attempt summaries
- cumulative fallback summaries
- full buggy file content
- latest failing output

### 5.2 Diff extraction and sanitation

The pipeline does not trust raw model output directly:

1. extract probable `diff --git ...` segment (`extract_slm_diff` / `extract_fallback_diff`)
2. sanitize malformed hunks:
   - fix line prefixes
   - trim trailing context noise
   - drop no-op hunks
   - recompute hunk counts
3. validate hunk format
4. optionally reconstruct repaired patch from file text if context mismatch

### 5.3 Patch application strategy

Tries multiple methods in order:

1. `git apply --3way`
2. `git apply`
3. `patch -p1`
4. `patch -p0`

On success, stores actual file diff:

- `applied_diff_actual.diff`

### 5.4 Test execution strategy

Each attempt has:

- pre-test (`test_pre.txt`) before patch
- post-test (`test_after.txt`) after patch apply

This enables learning feedback for next attempt and audit traceability.

## 6) QuixBugs Test Runner Pseudocode (`run_quixbugs_python.py`)

```python
def run_quixbugs_python(algo, quixbugs_dir, max_cases=0):
    load testcase lines from json_testcases/<algo>.json
    for each testcase:
        test_in = normalize_inputs_to_list(testcase)
        good = call(correct_python_programs.<algo>, test_in)
        bad  = call(python_programs.<algo>, test_in)
        compare normalized outputs
        print FAIL case details if mismatch
    exit 0 if no mismatches else 1
```

Important behavior:

- supports both callable function and object namespace patterns
- converts generators to list for stable comparison
- catches exceptions and converts them to tuple marker `("__EXC__", repr(...))`

## 7) Task Manifest Contract (`quixbugs_tasks_v2.jsonl`)

Each row contains:

- `dataset`, `language`, `task_id`, `algo`
- `buggy_path`, `quixbugs_dir`
- `test_cmd`, `test_timeout_s`

The orchestrator runs exactly one row selected by `--task_index`.

## 8) Run Artifact Layout (Expected)

Per run:

- `episodes/quixbugs_runs/attempts/<timestamp>_<algo>/`
  - `final_status.txt`
  - `test_before.txt`
  - `attempt_01/`, `attempt_02/`, ...
  - optional `fallback_01/`, `fallback_02/`, ...

Per SLM attempt folder typically contains:

- `prompt.txt`, `slm_raw.txt`, `slm_err.txt`
- `test_pre.txt`, `test_after.txt`
- optional `diff_sanitized.txt`, `applied_diff_actual.diff`, `patch_apply_err.txt`

Per fallback folder typically contains:

- `prompt.txt`, `llm_raw.txt`, `status.txt`
- `test_pre.txt`, `test_after.txt`
- optional diff/patch diagnostics as above

## 9) Practical Note for Your Current Workspace

In this repository snapshot, prior QuixBugs run artifacts under:

- `episodes/quixbugs_runs`

are no longer present (deleted earlier), so this file documents **implementation behavior** rather than historical pass/fail counts.

## 10) Literature-Inspired Framing (for Thesis Writing)

This orchestration design aligns with:

1. Reflexion-style iterative repair (failure text reused in next attempt)
2. Self-debug style execution-feedback loop
3. Cascade strategy (local SLM first, cloud fallback second)
4. Agentic software loop pattern (generate -> apply -> test -> reflect)

