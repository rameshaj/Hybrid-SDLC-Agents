#!/usr/bin/env bash
set -euo pipefail

MODEL="models/gguf/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"

RAW="reports/slm_smoke_basic.raw.txt"
CLEAN="reports/slm_smoke_basic.txt"
ERR="reports/slm_smoke_basic.stderr.txt"

PROMPT='You are a coding assistant. Explain in 5 bullet points how to interpret a Java stack trace.
Keep it short and concrete.'

# 1) Run model: stdout -> RAW, stderr -> ERR
llama-cli -m "$MODEL" \
  -p "$PROMPT" \
  -n 220 \
  --seed 42 \
  --temp 0.2 \
  --top-p 0.95 \
  --repeat-penalty 1.05 \
  --simple-io \
  > "$RAW" 2> "$ERR"

# 2) Sanitize RAW -> CLEAN (remove control chars, keep tabs/newlines)
#    This removes ASCII control chars except \t \n \r.
python - << 'PY'
import re, pathlib
raw = pathlib.Path("reports/slm_smoke_basic.raw.txt").read_bytes()
# keep: tab(9), LF(10), CR(13). remove others <32 and DEL(127)
clean = bytes(b for b in raw if (b in (9,10,13) or 32 <= b <= 126) )
pathlib.Path("reports/slm_smoke_basic.txt").write_bytes(clean)
PY

echo "Wrote RAW  : $RAW"
echo "Wrote CLEAN: $CLEAN"
echo "Wrote STDERR: $ERR"
