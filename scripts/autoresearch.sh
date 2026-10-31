#!/usr/bin/env bash
# Start (or resume) an unattended auto-research session. Run inside tmux on the pod:
#   tmux new -s ar 'bash scripts/autoresearch.sh'
# Needs ANTHROPIC_API_KEY (or a prior `claude` login). BUDGET_USD caps the agent's own API spend for this session.
set -euo pipefail
cd "$(dirname "$0")/.."
source /workspace/venv/bin/activate 2>/dev/null || true
mkdir -p logs
BUDGET="${BUDGET_USD:-25}"
LOG="logs/session-$(date -u +%Y%m%dT%H%M%SZ).jsonl"
echo "session log: $LOG  (agent budget ${BUDGET} USD)"
claude -p "Read CLAUDE.md, program.md and research/LOG.md. Continue the auto-research loop from where the log stops, \
following program.md exactly. Stop at the hand-off, when a program.md budget is reached, or when only the human \
can unblock you (write what you need under 'For the human' in research/LOG.md)." \
  --permission-mode acceptEdits \
  --max-budget-usd "$BUDGET" \
  --output-format stream-json --verbose | tee "$LOG"
