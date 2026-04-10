#!/usr/bin/env bash
set -euo pipefail

MODEL="models/gguf/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"

RAW="reports/slm_smoke_patch.raw.txt"
CLEAN="reports/slm_smoke_patch.txt"
ERR="reports/slm_smoke_patch.stderr.txt"
ANS="reports/slm_smoke_patch.answer.diff"

PROMPT='You are a software repair assistant.
Given this Java test failure:
"java.lang.AssertionError: expected:<3> but was:<2> at FooTest.testBar(FooTest.java:42)"

Task:
- Propose a minimal patch to Foo.java.
- Return ONLY a unified diff. No explanations.

Constraints for output:
- Must include lines starting with --- and +++
- Must include at least one @@ hunk header
- Do not include Markdown fences.'

# 1) Run model
llama-cli -m "$MODEL" \
  -p "$PROMPT" \
  -n 260 \
  --seed 42 \
  --temp 0.2 \
  --top-p 0.95 \
  --repeat-penalty 1.05 \
  --simple-io \
  > "$RAW" 2> "$ERR"

# 2) Sanitize RAW -> CLEAN
python - << 'PY'
from pathlib import Path
raw = Path("reports/slm_smoke_patch.raw.txt").read_bytes()
clean = bytes(b for b in raw if (b in (9,10,13) or 32 <= b <= 126))
Path("reports/slm_smoke_patch.txt").write_bytes(clean)
PY

# 3) Extract diff-like answer into ANS:
#    Keep from first '---' line onwards.
python - << 'PY'
from pathlib import Path
lines = Path("reports/slm_smoke_patch.txt").read_text("utf-8", errors="ignore").splitlines()
start = None
for i, line in enumerate(lines):
    if line.startswith("--- "):
        start = i
        break
out = "\n".join(lines[start:]).strip() if start is not None else "\n".join(lines).strip()
Path("reports/slm_smoke_patch.answer.diff").write_text(out + "\n", "utf-8")
print("Wrote: reports/slm_smoke_patch.answer.diff")
PY

echo "Wrote RAW  : $RAW"
echo "Wrote CLEAN: $CLEAN"
echo "Wrote DIFF : $ANS"
echo "Wrote STDERR: $ERR"
