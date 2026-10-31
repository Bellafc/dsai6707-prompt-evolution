#!/usr/bin/env bash
# HUMAN ONLY. Freeze an experiment and run its one-shot confirmatory test. Usage: bash scripts/final.sh exp01
set -euo pipefail
cd "$(dirname "$0")/.."
source /workspace/venv/bin/activate 2>/dev/null || true
EXP="${1:?usage: scripts/final.sh <exp>}"
echo "== 1/5 checks"; mosaic doctor --arms A,B,C,D
echo "== 2/5 read research/${EXP}_dev_summary.md before continuing"; read -rp "Press Enter when done… "
echo "== 3/5 freeze"; mosaic freeze --exp "$EXP"
git add locks/ && git commit -m "${EXP}: freeze before final test run"
echo "== 4/5 final runs (local arms, then the API teacher)"
mosaic run --exp "$EXP" --arms A,B,C --split test --final --note "final"
mosaic run --exp "$EXP" --arms D --split test --final --note "final"
echo "== 5/5 report"; mosaic report --exp "$EXP" --split test
git add -A experiments/ reports/ locks/ research/ && git commit -m "${EXP}: final test results"
echo "done: push with 'git push' when you have read the report"
