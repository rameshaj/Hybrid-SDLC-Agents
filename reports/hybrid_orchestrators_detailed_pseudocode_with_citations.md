# Hybrid SDLC Agent - Detailed Pseudocode (QuixBugs, Defects4J, HumanEval, BigCodeBench)

## 1) Scope and Code Versions Analyzed
This document captures detailed pseudocode from the latest/selected orchestrator implementations in this project:

- **QuixBugs**: `src/step6_orchestrator_quixbugs_v5_attempts.py` and `src/step6_orchestrator_quixbugs_v6_attempts.py`
- **Defects4J**: `src/step6_orchestrator_run_v3.py` (+ `src/step6_2_patchgen_slm.py`, `src/step6_2_git_apply.py`)
- **HumanEval (latest)**: `src/humaneval/run_humaneval_hybrid_v2.py`
- **BigCodeBench (latest)**: `src/bigcodebench/run_bigcodebench_hybrid.py`

The architecture is described using two agents:
- **Coder Agent**: generates candidate code/diff.
- **Patch-Fixer Agent**: repairs candidate formatting/syntax/anchoring issues, enforces structure/policy, and maximizes apply/testability.

---

## 2) Shared Design Pattern Across Datasets

### 2.1 Coder Agent (shared concept)
Responsibilities:
1. Read task/problem prompt and prior failure signals.
2. Generate candidate solution (either full code or unified diff).
3. Return output under strict format constraints.

Typical implementation:
- Local SLM first (llama.cpp).
- Optional cloud fallback LLM if SLM attempts fail.
- Multi-attempt loop with failure history injected into next prompt.

### 2.2 Patch-Fixer Agent (shared concept)
Responsibilities:
1. Normalize generated output into executable/applicable artifact.
2. Repair malformed output (syntax or diff formatting/context mismatch).
3. Enforce file/path/rule constraints.
4. Support robust application/execution before testing.

Typical implementation:
- For **patch tasks** (QuixBugs/Defects4J): sanitize diff, validate hunks/paths, attempt robust apply, repair hunks/context when needed.
- For **code tasks** (HumanEval/BigCodeBench): extract code, trim prompt echoes, reinject required preamble/imports, syntax-repair pass, then test.

### 2.3 Execution Principle (Generate -> Validate -> Iterate)
All four flows follow a generate-and-validate loop:
1. Generate candidate.
2. Validate via tests.
3. Capture failure summary.
4. Feed summary into next attempt.
5. Stop on pass or budget exhaustion.

This aligns with established automated repair loops in the literature [1], [10].

---

## 3) QuixBugs Pseudocode (v5/v6)

## 3.1 High-level Behavior
QuixBugs is **patch-oriented**. The Coder Agent emits unified diffs against one buggy Python file.  
Patch-Fixer Agent performs diff extraction, sanitization, context validation, repair, multi-method apply, and test verification.

v6 improves v5 with:
- stronger feedback loop (recent failure diagnostics + prior diff summaries),
- duplicate diff suppression across SLM attempts,
- richer failure capture for better next-attempt prompts.

## 3.2 Detailed Pseudocode
```text
PROCEDURE QUIXBUGS_RUN(task_index, max_attempts, fallback_max_attempts):
    task <- read task row from tasks JSONL
    run_dir <- create timestamped attempt folder
    IF fallback_model configured AND OPENAI_API_KEY missing:
        write fallback_status = ERROR_NO_OPENAI_API_KEY
        EXIT

    baseline_result <- run test_cmd on buggy file
    save test_before.txt
    IF baseline_result passes:
        write final_status = ALREADY_PASS
        EXIT SUCCESS

    initialize:
        prev_status = INIT
        slm_attempt_summaries = []
        slm_failure_details = []            # v6-rich history
        slm_diff_summaries = []             # v6 diff memory
        seen_slm_diff_hashes = {}           # v6 duplicate suppression

    FOR k in 1..max_attempts:
        create attempt_k directory
        rollback buggy file (unless skip_rollback)
        run test_pre and save output
        buggy_code <- load buggy file

        failure_history <- last 3 entries from slm_failure_details (v6)
        diff_history <- last 2 entries from slm_diff_summaries (v6)
        prompt <- build_prompt(task, buggy_code, test_pre_output, k, max_attempts,
                               prev_status, failure_history, diff_history)
        save prompt.txt

        raw_slm <- run local SLM with timeout/output cap
        save slm_raw.txt, slm_err.txt

        diff <- extract_slm_diff(raw_slm)
        IF no diff:
            prev_status = BAD_DIFF
            record summary/detail
            CONTINUE

        diff, sanitized_flag, sanitize_err <- sanitize_slm_diff(diff)
        IF sanitize failed:
            prev_status = BAD_DIFF_FORMAT(+reason)
            record summary/detail
            CONTINUE
        IF sanitized_flag: save diff_sanitized.txt

        diff_hash <- hash(diff)
        IF diff_hash seen before:                    # v6 only
            prev_status = DUPLICATE_DIFF: same_as_attempt_X
            record summary/detail
            CONTINUE
        mark diff_hash as seen
        append slm_diff_summaries with compact diff preview

        # Patch-Fixer Agent path:
        ok, method, reason <- apply_patch(
            diff,
            validate_context = TRUE,
            repair = TRUE,                           # repair hunks against live file
            methods = [git apply --3way, git apply, patch -p1, patch -p0]
        )
        IF apply failed:
            prev_status = PATCH_APPLY_FAIL(+reason)
            record summary/detail
            CONTINUE

        post_result <- run test_cmd
        save test_after.txt
        IF post_result passes:
            write final_status = PASS
            EXIT SUCCESS
        ELSE:
            prev_status = FAIL(+tail_of_test_output)
            record summary/detail

    # Fallback Coder Agent (cloud) after SLM budget exhausted
    IF fallback_model configured:
        initialize fallback_attempt_summaries = []
        FOR fk in 1..fallback_max_attempts:
            create fallback_fk directory
            rollback (unless skipped)
            run/save test_pre
            buggy_code <- load file
            fb_prompt <- build_fallback_prompt(
                task, buggy_code, failing_output,
                slm_attempt_summaries, fallback_attempt_summaries
            )
            llm_out <- openai_chat_completion(fb_prompt)
            save llm_raw.txt

            diff <- extract_fallback_diff(llm_out)
            IF invalid:
                record FALLBACK_BAD_DIFF(_FORMAT)
                CONTINUE
            IF sanitized: save diff_sanitized.txt

            ok, method, reason <- apply_patch(diff, validate_context=TRUE, repair=TRUE)
            IF apply failed:
                record FALLBACK_PATCH_APPLY_FAIL
                CONTINUE

            post_result <- run test_cmd
            save test_after.txt
            IF post_result passes:
                write final_status = PASS
                EXIT SUCCESS
            ELSE:
                record FALLBACK_FAIL

    write final_status = FAIL
    EXIT FAILURE
```

## 3.3 Why This Was Done
- QuixBugs tasks are single-line bug-fix style; strict diff generation + test validation is natural [2].
- Robust patch application was added because model patches often contain near-correct logic but weak hunk anchors (practical APR failure mode).
- Multi-attempt summaries operationalize trial-and-error with textual feedback (similar to Reflexion/Self-Refine style loops) [7], [8].
- Duplicate patch suppression in v6 avoids wasted retries on identical outputs and improves exploration efficiency.

---

## 4) Defects4J Pseudocode (v3)

## 4.1 High-level Behavior
Defects4J flow is **Java patch-oriented** with strict safety:
- checkout buggy revision,
- run tests to get failing signal,
- retrieve Java snippets via local RAG (grep),
- generate one-file Java diff,
- sanitize + policy guard (`source/*.java` only),
- apply patch,
- rerun tests.

## 4.2 Detailed Pseudocode
```text
PROCEDURE DEFECTS4J_RUN_SLM_PATCH(task_index):
    logger <- create episode logger + trace logger
    task <- load from tasks_path
    project, bug_id <- parse task
    buggy_ver <- normalize to "<id>b"

    write steps_why metadata:
        checkout, tests_before, rag, slm, sanitize, policy, apply, tests_after

    checkout buggy version into isolated workdir/source
    run defects4j test before patch
    save full raw outputs + parsed failing test list

    rag_snippets <- local_rag_grep(
        roots = [source/, tests/],
        file_glob = *.java,
        query = rag_query,
        top_k = rag_k
    )
    save rag query and hits

    # Coder Agent:
    slm_client <- llama.cpp wrapper
    repo_hint <- strict instructions:
        output unified diff only,
        modify one file only,
        path must be source/*.java
    patch_res <- generate_patch_with_slm(
        task_id, failing_test_output, rag_snippets, repo_hint
    )
    save raw model text + raw diff + prompt
    IF patch generation failed:
        finalize episode with patchgen_failed
        EXIT FAILURE

    # Patch-Fixer Agent:
    san <- sanitize_unified_diff(raw_diff, repo_root=source checkout)
    save sanitize metadata + sanitized diff
    IF sanitize failed:
        finalize episode with diff_sanitize_failed
        EXIT FAILURE

    enforce policy guard:
        touched files must all satisfy:
            startswith("source/") and endswith(".java")
    IF policy violated:
        finalize with diff_policy_reject
        EXIT FAILURE

    app <- git_apply(sanitized_diff)
    save apply outputs and metadata
    IF apply failed:
        finalize with git_apply_failed
        EXIT FAILURE

    run defects4j test after patch
    save outputs + parsed failing tests
    success <- (failing_tests_after count == 0)
    finalize episode with success flag
    EXIT SUCCESS if success else FAILURE
```

## 4.3 Why This Was Done
- Defects4J is the de-facto controlled real-bug Java benchmark for reproducible repair experiments [3].
- Generate-and-validate with test suites is canonical in APR pipelines [1], [10].
- Policy guard restricting edits to `source/*.java` reduces unsafe/noisy edits and keeps patches within intended repair scope.
- Local RAG over source/tests helps keep edits grounded in project-specific API/context [6].

---

## 5) HumanEval Pseudocode (latest: v2)

## 5.1 High-level Behavior
HumanEval flow is **function synthesis** (not file patching):
- Coder Agent generates function code from prompt.
- Patch-Fixer Agent handles code extraction/cleaning/trimming + optional self-debug hints + optional RAG hints.
- If SLM attempts fail, fallback LLM tries same task.

## 5.2 Detailed Pseudocode
```text
PROCEDURE HUMANEVAL_RUN_TASK(task, slm_attempts, fallback_attempts):
    run_dir <- create timestamped folder
    save task.json

    initialize:
        slm_failures = []
        fallback_failures = []
        rag_context = ""
        self_debug_notes = ""
        slm_best = None
        router = RuleBasedRouter(pass_threshold)

    FOR k in 1..slm_attempts:
        create slm_attempt_k directory

        prompt_k <- build_prompt(
            task_prompt, entry_point,
            prev_failures = slm_failures,
            rag_context,
            self_debug_notes
        )
        save prompt

        raw <- run local SLM
        save slm_raw

        code <- extract_code(raw)
        code <- clean_code_blob(code)
        code <- trim_to_entry_point(code, entry_point)
        save code.py

        IF no code:
            res <- NO_CODE_EXTRACTED
        ELSE:
            res <- execute candidate code + HumanEval tests with timeout

        save result.json + stdout/stderr
        append slm_failures with failure_summary

        IF self_debug enabled AND code exists AND fail:
            debug_prompt <- ask model for 1-3 minimal fix bullets
            debug_raw <- run local SLM on debug prompt
            self_debug_notes <- cleaned bullets
            save debug artifacts

        IF rag enabled AND fail:
            rag_query <- build from entry_point + failure type + summary + prompt
            rag_hits <- retrieve top-k similar historical fix cases
            rag_context <- compact hints (including added import hints)
            save rag artifacts

        update slm_best by score
        action <- router.decide(score, attempts_left)
        IF action == ACCEPT:
            write final_status PASS model=SLM
            RETURN PASS

    FOR k in 1..fallback_attempts:
        create fallback_attempt_k directory
        fb_prompt <- build_prompt(with all prior failures + current rag/self-debug context)
        raw <- openai_chat_completion_codegen(fb_prompt, system_prompt=code_only)
        save llm_raw

        code <- extract/clean/trim as above
        IF no code: res <- NO_CODE_EXTRACTED
        ELSE: res <- run tests
        save artifacts
        append fallback_failures

        IF pass:
            write final_status PASS model=LLM
            RETURN PASS

    write final_status FAIL (best_slm + failure histories)
    RETURN FAIL
```

## 5.3 Why This Was Done
- HumanEval is a functional-correctness benchmark with executable tests, so pass/fail loop is straightforward and robust [4].
- Self-debug notes turn failure into actionable natural-language guidance for the next attempt (iterative self-feedback pattern) [8].
- Optional RAG injects prior solved-case heuristics (especially useful for recurring error types) [6].
- Rule-based SLM->LLM escalation is a practical cost/quality routing strategy and aligns with routing literature motivation [9].

---

## 6) BigCodeBench Pseudocode (latest)

## 6.1 High-level Behavior
BigCodeBench flow is function synthesis with stronger structural controls:
- Coder Agent generates code from `complete_prompt`/`instruct_prompt`.
- Patch-Fixer Agent repairs output into executable code by:
  - removing prompt echo,
  - reinjecting required imports and preamble,
  - syntax-check and syntax-repair sub-loop (SLM/LLM),
  - then test execution.

## 6.2 Detailed Pseudocode
```text
PROCEDURE BIGCODEBENCH_RUN_TASK(task, slm_attempts, fallback_attempts):
    run_dir <- create timestamped folder
    save task.json

    extract:
        entry_point
        code_prompt
        main_prompt (complete_prompt > instruct_prompt > code_prompt)
        unit_tests

    initialize:
        slm_failures = []
        fallback_failures = []
        slm_best = None
        router = RuleBasedRouter

    FOR k in 1..slm_attempts:
        create slm_attempt_k dir
        prompt_k <- build_prompt(main_prompt, entry_point, slm_failures)
        raw <- run local SLM
        save slm_raw

        code <- extract_code(raw)
        code <- clean_code_blob(code)
        code <- trim_prompt_echo(code, entry_point)
        code <- inject_required_imports(code, code_prompt)
        code <- inject_required_preamble(code, code_prompt, entry_point)
        save code.py

        IF no code:
            res <- NO_CODE_EXTRACTED
        ELSE:
            syn <- syntax_error_summary(code)
            IF syn exists:
                repair_prompt <- build_syntax_repair_prompt(code, entry_point, code_prompt, syn)
                raw_fix <- run local SLM(repair_prompt)
                repaired <- extract/clean/trim + inject imports/preamble
                IF repaired valid syntax:
                    code <- repaired
                ELSE:
                    res <- syntax failure
            IF no syntax failure:
                res <- run unittest-based tests with timeout

        save result artifacts
        append slm_failures
        update slm_best
        IF router accepts: write final_status PASS model=SLM; RETURN PASS

    FOR k in 1..fallback_attempts:
        create fallback_attempt_k dir
        fb_prompt <- build_prompt(main_prompt, entry_point, slm_failures + fallback_failures)
        raw <- openai_chat_completion_codegen(fb_prompt, code-only system prompt)
        save llm_raw

        code <- trim_to_entry_point(clean_code_blob(extract_code(raw)), entry_point)
        code <- inject_required_imports(code, code_prompt)
        code <- inject_required_preamble(code, code_prompt, entry_point)
        save code.py

        IF no code:
            res <- NO_CODE_EXTRACTED
        ELSE:
            syn <- syntax_error_summary(code)
            IF syn exists:
                repair_prompt <- build_syntax_repair_prompt(...)
                raw_fix <- openai_chat_completion_codegen(repair_prompt)
                repaired <- extract/clean/trim + inject imports/preamble
                IF repaired valid syntax:
                    code <- repaired
                ELSE:
                    res <- syntax failure
            IF no syntax failure:
                res <- run tests

        save result artifacts
        append fallback_failures
        IF pass: write final_status PASS model=LLM; RETURN PASS

    write final_status FAIL (best_slm + failure lists)
    RETURN FAIL
```

## 6.3 Why This Was Done
- BigCodeBench tasks require diverse function/library usage and complex instructions; preserving scaffold imports/preamble is critical [5].
- Syntax-repair sub-loop acts as a Patch-Fixer Agent for code-generation artifacts (truncation/format drift/syntax corruption).
- SLM-first + fallback preserves low-cost first-pass behavior while enabling stronger rescue path on hard tasks [9].

---

## 7) Cross-Dataset Agent Mapping

### 7.1 Coder Agent
- QuixBugs: emits unified diff patch.
- Defects4J: emits one-file Java unified diff patch.
- HumanEval: emits function code for `entry_point`.
- BigCodeBench: emits function code respecting tool/library scaffold.

### 7.2 Patch-Fixer Agent
- QuixBugs:
  - diff extraction/sanitization,
  - hunk repair to current file state,
  - robust apply pipeline,
  - context validation before apply.
- Defects4J:
  - diff sanitize + touched-file policy check,
  - guarded `git apply`,
  - strict scope control (`source/*.java` only).
- HumanEval:
  - code extraction/cleanup/trimming,
  - optional self-debug notes generation,
  - optional RAG hint injection.
- BigCodeBench:
  - prompt-echo trimming,
  - import/preamble reinjection,
  - syntax repair sub-loop (SLM/LLM),
  - then test execution.

---

## 8) Why This Architecture Is Coherent for a Hybrid SDLC Agent

1. **Generate-and-validate loop** keeps objective correctness grounded in executable tests [1], [10].  
2. **Textual failure feedback across attempts** improves iterative behavior without retraining model weights [7], [8].  
3. **Fallback routing** balances cost vs quality by escalating only when needed [9].  
4. **RAG/context retrieval** improves grounding to repository/task-specific evidence [6].  
5. **Strict patch/code normalization stage** addresses practical model-output defects that are unrelated to core logic quality (format, anchors, syntax, boilerplate drift).  

---

## 9) References (Citations)

[1] Weimer et al., *Automatically Finding Patches Using Genetic Programming* (ICSE 2009).  
Link: https://web.eecs.umich.edu/~weimerw/p/weimer-icse2009-genprog.pdf

[2] Lin et al., *QuixBugs: A Multi-Lingual Program Repair Benchmark Set Based on the Quixey Challenge* (SPLASH Companion 2017).  
Link: https://dblp.org/rec/conf/oopsla/LinKCS17.html

[3] Just et al., *Defects4J: A database of existing faults to enable controlled testing studies for Java programs* (ISSTA 2014).  
Link: https://homes.cs.washington.edu/~rjust/publ/JustJE2014-abstract.html

[4] Chen et al., *Evaluating Large Language Models Trained on Code* (introduces HumanEval), arXiv:2107.03374.  
Link: https://arxiv.org/abs/2107.03374

[5] Zhuo et al., *BigCodeBench: Benchmarking Code Generation with Diverse Function Calls and Complex Instructions*, arXiv:2406.15877.  
Link: https://arxiv.org/abs/2406.15877

[6] Lewis et al., *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*, arXiv:2005.11401 / NeurIPS 2020.  
Link: https://arxiv.org/abs/2005.11401

[7] Shinn et al., *Reflexion: Language Agents with Verbal Reinforcement Learning*, arXiv:2303.11366.  
Link: https://arxiv.org/abs/2303.11366

[8] Madaan et al., *Self-Refine: Iterative Refinement with Self-Feedback*, arXiv:2303.17651.  
Link: https://arxiv.org/abs/2303.17651

[9] Ong et al., *RouteLLM: Learning to Route LLMs with Preference Data*, arXiv:2406.18665.  
Link: https://arxiv.org/abs/2406.18665

[10] Martinez et al., *Astor: Exploring the design space of generate-and-validate program repair beyond GenProg* (JSS 2019).  
Link: https://doi.org/10.1016/j.jss.2019.01.069

---

## 10) Notes for Thesis Use
- The citations above are used as **methodological inspiration mapping**, not as claims that the code is a direct reimplementation of each paper.
- The pseudocode is intentionally implementation-near, based on the exact local scripts listed in Section 1.

