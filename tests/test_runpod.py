"""The RunPod client builds safe requests; no network is used."""

import io
import json
from datetime import datetime, timezone

import pytest

import mosaic.runpod as rp
from mosaic.cli import main

NOW = datetime(2026, 11, 1, 9, 30, tzinfo=timezone.utc)


def test_payload_uses_runpod_secrets_and_agent_branch():
    body = rp.create_payload("S", gpus=rp.GPU_CLASSES["80gb"], hours=4, volume_id="vol123", now=NOW)
    env = body["env"]
    assert env["CLAUDE_CODE_OAUTH_TOKEN"] == "{{ RUNPOD_SECRET_claude_oauth_token }}"
    assert env["GITHUB_TOKEN"] == "{{ RUNPOD_SECRET_github_token }}"
    assert "HF_TOKEN" not in env and "ANTHROPIC_API_KEY" not in env
    assert env["MOSAIC_PUSH_BRANCH"] == "agent/task-S-20261101-0930" and env["MOSAIC_MAX_HOURS"] == "4"
    assert "Qwen/Qwen3.5-27B" in env["EXTRA_MODELS"]  # Task S includes the 27B spike
    assert body["networkVolumeId"] == "vol123" and "volumeInGb" not in body
    cmd = body["dockerStartCmd"][-1]
    assert "pod_bootstrap.sh" in cmd and "http.extraHeader" in cmd and "sleep infinity" in cmd
    assert "x-access-token:%s" in cmd and "$GITHUB_TOKEN@" not in cmd  # token never written into a URL


def test_payload_limits():
    with pytest.raises(ValueError, match="hours"):
        rp.create_payload("1", gpus=["NVIDIA L40S"], hours=24)
    with pytest.raises(ValueError, match="agent/"):
        rp.create_payload("1", gpus=["NVIDIA L40S"], hours=2, push_branch="main")
    body = rp.create_payload("2", gpus=["NVIDIA L40S"], hours=2, with_hf=True, now=NOW)
    assert body["volumeInGb"] == 200 and body["env"]["HF_TOKEN"] == "{{ RUNPOD_SECRET_hf_token }}"
    assert body["env"]["EXTRA_MODELS"] == ""


class FakeResp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_request_sends_key_only_when_given():
    seen = []

    def opener(req, timeout):
        seen.append(req)
        return FakeResp(b'[{"id": "p1", "name": "x", "desiredStatus": "RUNNING", "env": {"GITHUB_TOKEN": "t"}}]')

    rp.request("GET", "/pods", key="", opener=opener)
    rp.request("GET", "/pods", key="k123", opener=opener)
    assert seen[0].get_header("Authorization") is None  # left to the Claude Code network secret
    assert seen[1].get_header("Authorization") == "Bearer k123"
    assert seen[0].full_url == "https://rest.runpod.io/v1/pods"


def test_redact_hides_tokens():
    p = {"id": "p1", "env": {"GITHUB_TOKEN": "ghp_secret", "MOSAIC_TASK": "S"}}
    assert rp.redact(p)["env"] == {"GITHUB_TOKEN": "<hidden>", "MOSAIC_TASK": "S"}


def test_cli_dry_run_and_refusal_inside_a_pod(monkeypatch, capsys):
    assert main(["pod", "create", "--task", "S", "--hours", "3", "--dry-run"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["gpuTypeIds"] == rp.GPU_CLASSES["80gb"] and out["env"]["GITHUB_TOKEN"] == "<hidden>"
    monkeypatch.setenv("RUNPOD_POD_ID", "abc")
    with pytest.raises(SystemExit, match="orchestrator"):
        main(["pod", "stop", "abc"])


def test_pod_shell_scripts_have_no_command_substitution_in_heredocs():
    """An unquoted heredoc runs `...` in its text: `claude setup-token` in setup's closing message once blocked
    every pod forever, before the agent session started."""
    import re
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    for script in [*root.glob("setup/*.sh"), *root.glob("scripts/*.sh")]:
        lines = script.read_text().splitlines()
        for i, line in enumerate(lines):
            m = re.search(r"<<-?\s*([A-Za-z_]+)\b", line)  # unquoted delimiter: body is expanded
            if not m:
                continue
            body = []
            for nxt in lines[i + 1:]:
                if nxt.strip() == m.group(1):
                    break
                body.append(nxt)
            assert not any("`" in b or "$(" in b for b in body), f"{script.name}:{i + 1}: quote the heredoc"


def test_pod_heartbeat_pushes_masked_logs_to_an_agent_branch():
    from pathlib import Path

    src = (Path(__file__).resolve().parents[1] / "scripts" / "pod_bootstrap.sh").read_text()
    assert 'HEAD:refs/heads/agent/log-${POD}' in src  # pods push only to agent/... branches
    assert "<github_token>" in src and "<claude_token>" in src  # token values are masked before the push
    assert src.index("heartbeat running") < src.index("bash setup/runpod_setup.sh")  # covers a hanging setup


def test_pod_bootstrap_bounds_setup_and_lifetime():
    from pathlib import Path

    src = (Path(__file__).resolve().parents[1] / "scripts" / "pod_bootstrap.sh").read_text()
    assert "timeout 90m bash setup/runpod_setup.sh </dev/null" in src  # a hanging setup cannot run forever
    assert src.index("WATCHDOG") < src.index("FATAL")  # the lifetime cap is armed before anything can hang
