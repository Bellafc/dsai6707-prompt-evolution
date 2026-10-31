import json
import os
import stat

import pytest

from mosaic.backends import Cache, ClaudeCLIBackend, ClaudeUnavailable, Request

FAKE = """#!/usr/bin/env python3
import json, os, sys
args = sys.argv[1:]
log = os.environ["FAKE_CLAUDE_LOG"]
user = sys.stdin.read()
system = open(args[args.index("--system-prompt-file") + 1]).read()
with open(log, "a") as f:
    f.write(json.dumps({"args": args, "system": system, "user": user, "cwd": os.getcwd()}) + "\\n")
if os.environ.get("FAKE_CLAUDE_LIMIT"):
    print(json.dumps({"type": "result", "subtype": "success", "is_error": True, "result": "usage limit reached"}))
    sys.exit(1)
print(json.dumps({"type": "result", "subtype": "success", "is_error": False,
                  "result": "[Output]\\n- SPX: LONG", "total_cost_usd": 0.01,
                  "usage": {"input_tokens": 12, "output_tokens": 34}}))
"""


@pytest.fixture
def fake_claude(tmp_path, monkeypatch):
    exe = tmp_path / "claude"
    exe.write_text(FAKE)
    exe.chmod(exe.stat().st_mode | stat.S_IEXEC)
    log = tmp_path / "calls.jsonl"
    monkeypatch.setenv("FAKE_CLAUDE_LOG", str(log))
    return str(exe), log


def msgs(i):
    return [{"role": "system", "content": "You are an Austrian macroeconomist."},
            {"role": "user", "content": f"Event {i}"}]


def test_clean_call_and_cache(fake_claude, tmp_path):
    exe, log = fake_claude
    be = ClaudeCLIBackend({"seed": 1}, Cache(tmp_path / "c.jsonl"), model="claude-opus-5-5", effort="medium",
                          executable=exe)
    out = be.generate([Request(msgs(1), tag="D|austrian|e1"), Request(msgs(2), tag="D|austrian|e2")])
    assert [o["text"] for o in out] == ["[Output]\n- SPX: LONG"] * 2
    assert out[0]["usage"] == {"prompt_tokens": 12, "completion_tokens": 34}
    calls = [json.loads(line) for line in open(log)]
    a = calls[0]["args"]
    assert a[a.index("--model") + 1] == "claude-opus-5-5" and a[a.index("--effort") + 1] == "medium"
    assert a[a.index("--tools") + 1] == "" and "--safe-mode" in a and "--strict-mcp-config" in a
    assert calls[0]["system"] == "You are an Austrian macroeconomist." and calls[0]["user"] == "Event 1"
    assert calls[0]["cwd"] != os.getcwd()  # empty temp dir, no project files visible
    # second time: served from cache, the CLI is not called again
    again = ClaudeCLIBackend({"seed": 1}, Cache(tmp_path / "c.jsonl"), model="claude-opus-5-5", effort="medium",
                             executable=exe).generate([Request(msgs(1))])
    assert again[0]["cached"] and len(open(log).readlines()) == 2


def test_usage_limit_stops_but_keeps_progress(fake_claude, tmp_path, monkeypatch):
    exe, _ = fake_claude
    cache = Cache(tmp_path / "c.jsonl")
    ClaudeCLIBackend({}, cache, model="claude-opus-5-5", executable=exe).generate([Request(msgs(1))])
    monkeypatch.setenv("FAKE_CLAUDE_LIMIT", "1")
    with pytest.raises(ClaudeUnavailable, match="usage limit"):
        ClaudeCLIBackend({}, cache, model="claude-opus-5-5", executable=exe).generate(
            [Request(msgs(1)), Request(msgs(2))])
    assert len(Cache(tmp_path / "c.jsonl").mem) == 1  # the earlier answer survived


def test_rejects_few_shot_messages(fake_claude, tmp_path):
    exe, _ = fake_claude
    m = msgs(1)[:1] + [{"role": "user", "content": "x"}, {"role": "assistant", "content": "y"}] + msgs(1)[1:]
    with pytest.raises(ValueError):
        ClaudeCLIBackend({}, None, model="claude-opus-5-5", executable=exe).generate([Request(m)])
