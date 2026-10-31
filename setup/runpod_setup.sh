#!/usr/bin/env bash
# One-time setup on a RunPod GPU pod (PyTorch template, CUDA 12.x). Persistent files go to /workspace.
# Recommended GPU: 48 GB (A6000 / L40S / A40) — few-shot prompts are long. A 24 GB card (4090) works for arms A/C;
# for arm B set [model] max_model_len = 12288 in configs/exp01.toml.
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

echo "== base model weights (cached in /workspace/hf)"
python - <<'PY'
from huggingface_hub import snapshot_download
snapshot_download("Qwen/Qwen2.5-7B-Instruct", allow_patterns=["*.json", "*.safetensors", "*.txt", "*.model"])
PY

echo "== offline tests and doctor"
cd "$REPO_DIR" && python -m pytest -q
mosaic doctor --arms A,B,C,D || true
cat <<MSG

Next:
  1. Copy your assets (see data/README.md): data/events/{dev,test}.jsonl, data/trajectories/*.jsonl,
     adapters/{keynesian,austrian,monetarist}/, optionally data/legacy/*.jsonl.
  2. Restore the original prompts (configs/prompts/) and keyword lists (configs/lexicons.toml).
  3. On your own computer run `claude setup-token`, then on the pod:
       echo 'export CLAUDE_CODE_OAUTH_TOKEN=<token>' >> ~/.bashrc && source ~/.bashrc
     Do NOT set ANTHROPIC_API_KEY here (it would override your subscription).
     Optional, for arm T only: export OPENAI_API_KEY=...
  4. mosaic doctor --arms A,B,C,D   until it says "ready"
  5. tmux new -s ar 'bash scripts/autoresearch.sh'
MSG
