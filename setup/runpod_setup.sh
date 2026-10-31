#!/usr/bin/env bash
# One-time setup on a RunPod GPU pod (PyTorch template, CUDA 12.x). Persistent files go to /workspace
# (put it on a network volume, >= 200 GB, so models and caches survive stopping the pod).
# GPU: one 80 GB card (A100 80GB / H100) for the first-day spikes, which include Qwen3.5-27B (bf16 LoRA needs
# ~56 GB). Qwen3-8B work alone (exp01, exp03, exp06) runs on 48 GB (A6000 / L40S / A40).
# Optional: EXTRA_MODELS="Qwen/Qwen3-8B-Base Qwen/Qwen3.5-27B" bash setup/runpod_setup.sh
set -euo pipefail
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
export HF_HOME=/workspace/hf
grep -q HF_HOME ~/.bashrc 2>/dev/null || echo 'export HF_HOME=/workspace/hf' >> ~/.bashrc

echo "== system packages"
apt-get update -qq && apt-get install -y -qq tmux jq git curl > /dev/null

echo "== python venv (/workspace/venv)"
[ -d /workspace/venv ] || python3 -m venv /workspace/venv
source /workspace/venv/bin/activate
grep -q workspace/venv ~/.bashrc 2>/dev/null || echo 'source /workspace/venv/bin/activate' >> ~/.bashrc
pip install -q --upgrade pip
pip install -q -r "$REPO_DIR/setup/requirements.txt"
pip install -q -e "$REPO_DIR[dev]"

echo "== Claude Code"
if ! command -v claude >/dev/null; then
  curl -fsSL https://claude.ai/install.sh | bash || {
    echo "native installer failed, trying npm"; apt-get install -y -qq nodejs npm > /dev/null && npm install -g @anthropic-ai/claude-code; }
fi
grep -q '.local/bin' ~/.bashrc 2>/dev/null || echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
export PATH="$HOME/.local/bin:$PATH"
claude --version || echo "WARNING: claude not on PATH yet; open a new shell"

echo "== model weights (cached in /workspace/hf): Qwen/Qwen3-8B ${EXTRA_MODELS:-}"
MODELS="Qwen/Qwen3-8B ${EXTRA_MODELS:-}" python - <<'PY'
import os
from huggingface_hub import snapshot_download
for m in os.environ["MODELS"].split():
    print("  downloading", m)
    snapshot_download(m, allow_patterns=["*.json", "*.safetensors", "*.txt", "*.model", "*.jinja"])
PY
# Qwen-Scope SAEs (exp06) take 1-2 GB per layer, so the agent downloads only the layers it needs, e.g.
#   snapshot_download("Qwen/SAE-Res-Qwen3-8B-Base-W64K-L0_50", allow_patterns=["layer18.sae.pt", "*.md"])

echo "== offline tests and doctor"
cd "$REPO_DIR" && python -m pytest -q
mosaic doctor --arms A,B,C,D || true
cat <<MSG

Next:
  1. Copy your assets (see data/README.md): data/events/{dev,test}.jsonl, data/trajectories/*.jsonl (the SFT
     data; adapters are retrained on the pod with `mosaic train`), optionally data/legacy/*.jsonl.
     Without them the agent can still do Task S (spikes) and Task 2 (exp03 data) in program.md.
  2. Restore the original prompts (configs/prompts/) and keyword lists (configs/lexicons.toml).
  3. On your own computer run `claude setup-token`, then on the pod:
       echo 'export CLAUDE_CODE_OAUTH_TOKEN=<token>' >> ~/.bashrc && source ~/.bashrc
     Do NOT set ANTHROPIC_API_KEY here (it would override your subscription).
     Optional, for arm T only: export OPENAI_API_KEY=...
  4. mosaic doctor --arms A,B,C,D   until it says "ready"
  5. tmux new -s ar 'bash scripts/autoresearch.sh'
MSG
