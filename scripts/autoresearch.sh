#!/usr/bin/env bash
# Start (or resume) an unattended auto-research session. Run inside tmux on the pod:
#   tmux new -s ar 'bash scripts/autoresearch.sh'
# Auth: your Claude subscription (CLAUDE_CODE_OAUTH_TOKEN from `claude setup-token`, or `claude auth login`).
# Do NOT export ANTHROPIC_API_KEY on the pod: `claude -p` would then bill the API instead of your plan.
# BUDGET_USD caps the session by Claude Code's own cost estimate (a usage guard on a subscription).
set -euo pipefail
cd "$(dirname "$0")/.."
source /workspace/venv/bin/activate 2>/dev/null || true
mkdir -p logs
BUDGET="${BUDGET_USD:-25}"
LOG="logs/session-$(date -u +%Y%m%dT%H%M%SZ).jsonl"
TASK_HINT=""
if [ -n "${MOSAIC_TASK:-}" ]; then  # set by `mosaic pod create` (ops/ORCHESTRATOR.md)
  TASK_HINT=" This pod session is for program.md Task ${MOSAIC_TASK} only (hard limit ${MOSAIC_MAX_HOURS:-?} h). \
Commit after every logged step; the bootstrap script pushes your commits when the session ends."
fi
echo "session log: $LOG  (agent budget ${BUDGET} USD)"
# The rules of .claude/settings.json, passed on the command line as well: on the pods the project file's allow list
# was not applied and `claude -p` denied every Bash call ("requires approval").
mapfile -t PERMS < <(python3 -m mosaic.runpod)
claude -p "Read CLAUDE.md, program.md and research/LOG.md. Continue the auto-research loop from where the log stops, \
following program.md exactly.${TASK_HINT} Stop at the hand-off, when a program.md budget is reached, or when only \
the human can unblock you (write what you need under 'For the human' in research/LOG.md)." \
  --permission-mode acceptEdits "${PERMS[@]}" \
  --max-budget-usd "$BUDGET" \
  --output-format stream-json --verbose | tee "$LOG"
