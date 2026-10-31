"""RunPod pods for the orchestrator session (`mosaic pod ...`), standard library only.

The orchestrator (a Claude Code cloud session on this repository, see ops/ORCHESTRATOR.md) starts one GPU pod per
work package. The pod clones the repository, runs `scripts/pod_bootstrap.sh` (setup, one auto-research session
for the requested program.md task under a hard time limit, push to an `agent/...` branch, stop itself).

Credentials never pass through this module or the repository:
  * RunPod API key: a network secret on the Claude Code cloud environment for host rest.runpod.io (the agent
    proxy adds the header), or RUNPOD_API_KEY in the environment when run elsewhere.
  * Tokens the pod needs (Claude subscription, GitHub, Hugging Face): RunPod secrets, referenced in the pod's
    environment as {{ RUNPOD_SECRET_<name> }} and substituted by RunPod when the pod starts.
REST reference: https://docs.runpod.io/api-reference (v1, https://rest.runpod.io/v1).
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone

API = "https://rest.runpod.io/v1"
REPO = "Bellafc/macro-mosaic"
# Official template runpod-torch-v280 (torch 2.8.0, CUDA 12.8.1, Ubuntu 24.04, Python 3.12, uv preinstalled).
# setup/runpod_setup.sh builds its own venv on the volume; vLLM brings a matching torch into it.
DEFAULT_IMAGE = "runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404"
GPU_CLASSES = {  # RunPod gpuTypeIds (enum of the v1 PodCreateInput); RunPod picks by availability
    "80gb": ["NVIDIA H100 80GB HBM3", "NVIDIA H100 PCIe", "NVIDIA A100 80GB PCIe", "NVIDIA A100-SXM4-80GB",
             "NVIDIA H100 NVL"],
    "48gb": ["NVIDIA L40S", "NVIDIA RTX 6000 Ada Generation", "NVIDIA RTX A6000", "NVIDIA A40", "NVIDIA L40"],
}
SECRETS = {"CLAUDE_CODE_OAUTH_TOKEN": "claude_oauth_token", "GITHUB_TOKEN": "github_token"}
OPTIONAL_SECRETS = {"HF_TOKEN": "hf_token", "JUPYTER_PASSWORD": "jupyter_password"}  # Jupyter runs only if set
TASK_EXTRA_MODELS = {"S": "Qwen/Qwen3-8B-Base Qwen/Qwen3.5-27B"}  # program.md Task S needs the 27B spike
MAX_HOURS = 12
# Cloudflare in front of rest.runpod.io rejects urllib's default "Python-urllib/x.y" agent (error 1010).
USER_AGENT = "macro-mosaic-orchestrator/1.0"


class RunPodError(RuntimeError):
    pass


def request(method: str, path: str, body: dict | None = None, *, key: str | None = None,
            opener=urllib.request.urlopen, timeout: float = 60) -> dict | list:
    """One REST call. Without a key the request carries no Authorization header, so that the Claude Code agent
    proxy can attach the network secret configured for rest.runpod.io."""
    key = key if key is not None else os.environ.get("RUNPOD_API_KEY")
    headers = {"Content-Type": "application/json", "Accept": "application/json", "User-Agent": USER_AGENT}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method, headers=headers)
    try:
        with opener(req, timeout=timeout) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:500]
        hint = (" (no key reached RunPod: add the API key as a network secret for rest.runpod.io on the cloud "
                "environment, or export RUNPOD_API_KEY)") if e.code == 401 else ""
        raise RunPodError(f"{method} {path}: HTTP {e.code} {detail}{hint}") from None
    return json.loads(raw) if raw.strip() else {}


def start_command() -> list[str]:
    """Container start command: keep RunPod's own services (SSH, Jupyter), fetch the repository without writing
    the token to disk, then hand over to scripts/pod_bootstrap.sh. `sleep infinity` keeps a finished pod from
    restarting the container in a loop; the bootstrap stops the pod itself."""
    script = (
        'if [ -x /start.sh ]; then (/start.sh > /var/log/runpod-start.log 2>&1 &); fi; '
        'command -v git >/dev/null || (apt-get update -qq && apt-get install -y -qq git); '
        'mkdir -p /workspace && cd /workspace; '
        'AUTH="Authorization: Basic $(printf "x-access-token:%s" "$GITHUB_TOKEN" | base64 -w0)"; '
        'if [ -d polyu/.git ]; then '
        'git -C polyu -c http.extraHeader="$AUTH" fetch -q origin "$MOSAIC_BRANCH" '
        '&& git -C polyu checkout -q -B "$MOSAIC_BRANCH" FETCH_HEAD; '
        'else git -c http.extraHeader="$AUTH" clone -q -b "$MOSAIC_BRANCH" '
        '"https://github.com/$MOSAIC_REPO.git" polyu; fi; '
        'bash polyu/scripts/pod_bootstrap.sh 2>&1 | tee -a /workspace/bootstrap.log; '
        'sleep infinity'
    )
    return ["bash", "-lc", script]


def create_payload(task: str, *, gpus: list[str], hours: float, branch: str = "main", push_branch: str | None = None,
                   volume_id: str | None = None, volume_gb: int = 200, data_center: str | None = None,
                   image: str = DEFAULT_IMAGE, cloud: str = "SECURE", container_disk_gb: int = 80,
                   with_hf: bool = False, jupyter: bool = False, template_id: str | None = None,
                   extra_models: str | None = None, name: str | None = None, now: datetime | None = None) -> dict:
    if not 0 < hours <= MAX_HOURS:
        raise ValueError(f"hours must be in (0, {MAX_HOURS}]: a pod never runs unattended for longer")
    stamp = (now or datetime.now(timezone.utc)).strftime("%Y%m%d-%H%M")
    push_branch = push_branch or f"agent/task-{task}-{stamp}"
    if not push_branch.startswith("agent/"):
        raise ValueError("pods push only to agent/... branches; the human merges")
    env = {
        "MOSAIC_TASK": task, "MOSAIC_BRANCH": branch, "MOSAIC_PUSH_BRANCH": push_branch,
        "MOSAIC_MAX_HOURS": f"{hours:g}", "MOSAIC_REPO": REPO, "HF_HOME": "/workspace/hf",
        "EXTRA_MODELS": extra_models if extra_models is not None else TASK_EXTRA_MODELS.get(task, ""),
    }
    secrets = dict(SECRETS)
    if with_hf:
        secrets["HF_TOKEN"] = OPTIONAL_SECRETS["HF_TOKEN"]
    if jupyter:
        secrets["JUPYTER_PASSWORD"] = OPTIONAL_SECRETS["JUPYTER_PASSWORD"]
    if not template_id:  # a template made in the RunPod console may carry the secret references instead
        env.update({var: "{{ RUNPOD_SECRET_%s }}" % name_ for var, name_ in secrets.items()})
    body = {
        "name": name or f"mosaic-{task}-{stamp}", "imageName": image, "gpuTypeIds": gpus, "gpuCount": 1,
        "cloudType": cloud, "containerDiskInGb": container_disk_gb, "volumeMountPath": "/workspace",
        "ports": ["22/tcp", "8888/http"], "env": env, "dockerStartCmd": start_command(),
    }
    if volume_id:
        body["networkVolumeId"] = volume_id
    else:
        body["volumeInGb"] = volume_gb
    if data_center:
        body["dataCenterIds"] = [data_center]
    if template_id:
        body["templateId"] = template_id
    return body


def list_pods(**kw) -> list[dict]:
    out = request("GET", "/pods", **kw)
    return out if isinstance(out, list) else out.get("pods", [])


def create(task: str, *, allow_parallel: bool = False, dry_run: bool = False, **kw) -> dict:
    if os.environ.get("RUNPOD_POD_ID") and not dry_run:
        raise RunPodError("refusing to create pods from inside a pod (only the orchestrator starts pods)")
    body = create_payload(task, **kw)
    if dry_run:
        return body
    running = [p for p in list_pods() if p.get("desiredStatus") == "RUNNING"]
    if running and not allow_parallel:
        names = ", ".join(f"{p.get('name')} ({p.get('id')})" for p in running)
        raise RunPodError(f"pods already running: {names}. Stop them first or pass --allow-parallel")
    return request("POST", "/pods", body)


def redact(p: dict) -> dict:
    """A pod record safe to print: environment values other than MOSAIC_* and HF_HOME are hidden."""
    q = dict(p)
    if isinstance(q.get("env"), dict):
        q["env"] = {k: (v if k.startswith("MOSAIC_") or k in ("HF_HOME", "EXTRA_MODELS") else "<hidden>")
                    for k, v in q["env"].items()}
    return q


def permission_flags(settings_path: str = ".claude/settings.json") -> list[str]:
    """The project's permission rules as `claude` command-line flags for the pod's unattended session. On the pods
    the allow list in .claude/settings.json was not applied (every Bash call "requires approval", and `-p` cannot
    ask anyone), so scripts/autoresearch.sh passes the same rules on the command line, in both rule spellings."""
    perms = json.loads(open(settings_path).read())["permissions"]

    def spell(rules: list[str]) -> list[str]:
        out = []
        for r in rules:
            out.append(r)
            if r.startswith("Bash(") and r.endswith("*)") and not r.endswith(":*)"):
                out.append(r[:-2].rstrip() + ":*)")  # legacy prefix syntax: Bash(git add:*)
        return out

    return ["--allowedTools", *spell(perms.get("allow", [])), "--disallowedTools", *spell(perms.get("deny", []))]


def summary(p: dict) -> str:
    gpu = (p.get("machine") or {}).get("gpuTypeId") or ",".join(p.get("gpuTypeIds") or []) or "?"
    cost = p.get("costPerHr")
    env = p.get("env") or {}
    return "\t".join(str(x) for x in (p.get("id"), p.get("name"), p.get("desiredStatus"), gpu,
                                      f"${cost}/h" if cost is not None else "", env.get("MOSAIC_PUSH_BRANCH", "")))


if __name__ == "__main__":  # one argument per line, for scripts/autoresearch.sh
    print("\n".join(permission_flags()))
