#!/usr/bin/env bash
# Runs on a RunPod pod started by `python -m mosaic pod create` (ops/ORCHESTRATOR.md); the pod's start command
# clones the repository into /workspace/polyu and calls this script.
#   1. checks the RunPod secrets arrived (CLAUDE_CODE_OAUTH_TOKEN, GITHUB_TOKEN) and that no API key would bill
#   2. setup (idempotent: venv, vLLM, Claude Code, model weights on the volume)
#   3. one auto-research session for program.md task $MOSAIC_TASK, killed after $MOSAIC_MAX_HOURS hours
#   4. commits whatever is left and pushes to $MOSAIC_PUSH_BRANCH (an agent/... branch; the human merges)
#   5. stops the pod (the network volume keeps models, caches and data)
# The agent itself cannot push (git push is denied in .claude/settings.json); only this script does, at the end.
set -uo pipefail
cd "$(dirname "$0")/.."
POD="${RUNPOD_POD_ID:-local}"
DONE="/workspace/.mosaic_done_${POD}"
log() { echo "[bootstrap $(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }

stop_pod() {
  [ "$POD" = "local" ] && return 0
  log "stopping pod $POD"
  if command -v runpodctl >/dev/null; then
    runpodctl pod stop "$POD" >/dev/null 2>&1 && return 0
    runpodctl stop pod "$POD" >/dev/null 2>&1 && return 0
  fi
  if [ -n "${RUNPOD_API_KEY:-}" ]; then
    curl -fsS -X POST -H "Authorization: Bearer ${RUNPOD_API_KEY}" \
      "https://rest.runpod.io/v1/pods/${POD}/stop" >/dev/null 2>&1 && return 0
  fi
  log "WARNING: the pod could not stop itself; the orchestrator must run: python -m mosaic pod stop $POD"
}

if [ -f "$DONE" ]; then log "this pod already finished ($DONE)"; stop_pod; exit 0; fi
for v in CLAUDE_CODE_OAUTH_TOKEN GITHUB_TOKEN MOSAIC_TASK MOSAIC_PUSH_BRANCH MOSAIC_MAX_HOURS; do
  val="${!v:-}"
  if [ -z "$val" ] || [[ "$val" == "{{"* ]]; then
    log "FATAL: $v is missing or the RunPod secret was not substituted (create the RunPod secrets, see ops/ORCHESTRATOR.md)"
    touch "$DONE"; stop_pod; exit 1
  fi
done
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  log "FATAL: ANTHROPIC_API_KEY is set; Claude Code would bill the API instead of the subscription"
  touch "$DONE"; stop_pod; exit 1
fi
case "$MOSAIC_PUSH_BRANCH" in agent/*) ;; *) log "FATAL: push branch must start with agent/"; touch "$DONE"; stop_pod; exit 1;; esac

AUTH="Authorization: Basic $(printf 'x-access-token:%s' "$GITHUB_TOKEN" | base64 -w0)"
git config user.name "mosaic-pod"
git config user.email "mosaic-pod@users.noreply.github.com"
git checkout -q -B "$MOSAIC_PUSH_BRANCH"

# RunPod's REST API exposes no logs, so the orchestrator could not see a pod that hangs. Every 10 minutes the
# pod force-pushes the tail of its log (lines cut to 400 chars, token values masked) to agent/log-<pod>, a
# branch written from a separate repository, so the agent's own commits are never touched.
HB_DIR=/tmp/mosaic-heartbeat
heartbeat() {
  mkdir -p "$HB_DIR" && git -C "$HB_DIR" init -q 2>/dev/null
  {
    echo "pod $POD · task $MOSAIC_TASK · $(date -u +%Y-%m-%dT%H:%M:%SZ) · $*"
    nvidia-smi --query-gpu=name,utilization.gpu,memory.used --format=csv,noheader 2>/dev/null
    tail -n 300 /workspace/bootstrap.log 2>/dev/null | cut -c1-400 \
      | sed -e "s|${GITHUB_TOKEN}|<github_token>|g" -e "s|${CLAUDE_CODE_OAUTH_TOKEN}|<claude_token>|g"
  } > "$HB_DIR/status.log"
  git -C "$HB_DIR" add status.log
  git -C "$HB_DIR" -c user.name=mosaic-pod -c user.email=mosaic-pod@users.noreply.github.com \
    commit -q --allow-empty -m "pod ${POD}: heartbeat" >/dev/null
  git -C "$HB_DIR" -c http.extraHeader="$AUTH" push -q -f "https://github.com/${MOSAIC_REPO}.git" \
    "HEAD:refs/heads/agent/log-${POD}" >/dev/null 2>&1 || log "WARNING: heartbeat push failed"
}
( while true; do heartbeat running; sleep 600; done ) &
HB_PID=$!

# Assets the human uploaded to the network volume (/workspace/assets/{events,trajectories,episodes,legacy}) are
# linked into data/ (not versioned). Trained adapters, caches and runs live in this checkout on the volume.
if [ -d /workspace/assets ]; then
  for d in /workspace/assets/*/; do
    n="$(basename "$d")"
    [ -e "data/$n" ] || ln -s "${d%/}" "data/$n"
  done
fi

log "setup (EXTRA_MODELS='${EXTRA_MODELS:-}')"
EXTRA_MODELS="${EXTRA_MODELS:-}" bash setup/runpod_setup.sh </dev/null || log "setup reported problems (see above)"
# shellcheck disable=SC1091
source /workspace/venv/bin/activate 2>/dev/null || true
export PATH="$HOME/.local/bin:$PATH"

if [ "$MOSAIC_TASK" = "H" ]; then
  # A pod for the human (freeze, final runs, ratings need a terminal): no agent; stops after the time limit.
  log "human pod: open the RunPod web terminal or SSH; this pod stops after ${MOSAIC_MAX_HOURS} h"
  sleep "${MOSAIC_MAX_HOURS}h"
else
  log "agent session: task ${MOSAIC_TASK}, hard limit ${MOSAIC_MAX_HOURS} h, pushes to ${MOSAIC_PUSH_BRANCH}"
  timeout --signal=INT --kill-after=120 "${MOSAIC_MAX_HOURS}h" bash scripts/autoresearch.sh
  log "agent session ended (status $?)"
fi

git add -A
git commit -q -m "pod ${POD}: end of session for task ${MOSAIC_TASK}" || true
if git -c http.extraHeader="$AUTH" push -q origin "HEAD:refs/heads/${MOSAIC_PUSH_BRANCH}"; then
  log "pushed to ${MOSAIC_PUSH_BRANCH}"
else
  log "WARNING: push failed; the commits stay in /workspace/polyu on the volume"
fi
touch "$DONE"
kill "$HB_PID" 2>/dev/null
heartbeat "session over, stopping"
stop_pod
