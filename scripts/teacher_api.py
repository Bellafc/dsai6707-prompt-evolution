#!/usr/bin/env python3
"""Run the teacher requests through any OpenAI-compatible chat API, on your own computer (standard library only).

  export TEACHER_API_KEY=...            # your provider's key; never commit it
  python3 scripts/teacher_api.py research/teacher_runs/pilot --n 20 --base-url https://.../v1 --model <model id>

With --n and no <jobs>/requests.jsonl yet, it first writes the requests (n per school, the same items as
`mosaic teacher-export`) and <jobs>/manifest.json. It sends up to --workers requests at once and appends one line per
finished request to <jobs>/results.jsonl; re-running skips requests that already have a result, so an interrupted run
resumes. Then commit <jobs>/manifest.json and <jobs>/results.jsonl; the orchestrator imports them with
`mosaic teacher-import`, which applies the Change 5 filters. Claude models are not allowed as teacher.

Version 4 requests (prompt version 4, real tools) are conversations: the runner sends the tool specs, executes each
tool call the teacher makes with `mosaic.tools` (the item's backdrop for get_macro_data, the episode table for
query_episode_db), returns the result as a tool message and asks again, up to --max-rounds replies. The result line
holds the turns after the prompt.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def call(base_url: str, key: str, body: dict, timeout: float, retries: int = 5) -> dict:
    """One chat completion, streamed: gateways cut non-streamed replies that take longer than ~30 s (HTTP 502), and
    a thinking teacher needs minutes. Returns an OpenAI-shaped response with the joined content and the usage."""
    headers = {"Content-Type": "application/json", "User-Agent": "macro-mosaic-teacher/1.0"}
    if key:  # without a key the Claude Code network secret for the API host adds the header
        headers["Authorization"] = f"Bearer {key}"
    body = dict(body, stream=True, stream_options={"include_usage": True})
    req = urllib.request.Request(base_url.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(),
                                 headers=headers)
    for attempt in range(retries):
        try:
            parts, usage, model, calls = [], {}, body.get("model", ""), {}
            with urllib.request.urlopen(req, timeout=timeout) as r:
                for raw in r:
                    line = raw.decode("utf-8", errors="replace").strip()
                    if not line.startswith("data:") or line.endswith("[DONE]"):
                        continue
                    chunk = json.loads(line[5:])
                    usage = chunk.get("usage") or usage
                    model = chunk.get("model") or model
                    for ch in chunk.get("choices") or []:
                        delta = ch.get("delta") or {}
                        parts.append(delta.get("content") or "")  # reasoning_content is dropped
                        merge_tool_deltas(calls, delta.get("tool_calls") or [])
            msg = {"content": "".join(parts)}
            if calls:
                msg["tool_calls"] = [calls[i] for i in sorted(calls)]
            return {"model": model, "usage": usage, "choices": [{"message": msg}]}
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(2 ** attempt * 5)
                continue
            raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='replace')[:300]}") from None
        except (urllib.error.URLError, TimeoutError):
            if attempt < retries - 1:
                time.sleep(2 ** attempt * 5)
                continue
            raise
    raise RuntimeError("unreachable")


def merge_tool_deltas(calls: dict, deltas: list[dict]) -> None:
    """Accumulate streamed tool-call fragments (OpenAI format: id and name once, arguments in pieces) by index."""
    for d in deltas:
        c = calls.setdefault(d.get("index", 0), {"id": "", "type": "function",
                                                 "function": {"name": "", "arguments": ""}})
        c["id"] = d.get("id") or c["id"]
        fn = d.get("function") or {}
        c["function"]["name"] = fn.get("name") or c["function"]["name"]
        c["function"]["arguments"] += fn.get("arguments") or ""


def converse(job: dict, send, max_rounds: int = 4) -> tuple[list[dict], dict]:
    """Run one version-4 job: send(body) -> OpenAI-shaped response; every tool call is executed locally and returned
    as a tool message. Returns (turns after the prompt, summed usage)."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from mosaic.tools import EpisodeTable, MacroFacts, ToolBox  # standard library only

    box = ToolBox(MacroFacts(job["backdrop"]), EpisodeTable.load())
    body = dict(job["body"])
    msgs, turns, usage, model = list(body["messages"]), [], {}, body.get("model", "")
    for _ in range(max_rounds):
        resp = send(dict(body, messages=msgs))
        model = resp.get("model") or model
        for k, v in (resp.get("usage") or {}).items():
            if isinstance(v, int):
                usage[k] = usage.get(k, 0) + v
        msg = resp["choices"][0]["message"]
        turn = {"role": "assistant", "content": msg.get("content") or ""}
        if msg.get("tool_calls"):
            turn["tool_calls"] = msg["tool_calls"]
        turns.append(turn)
        msgs.append(turn)
        if not msg.get("tool_calls"):
            break
        for c in msg["tool_calls"]:
            res = box.execute(c["function"]["name"], c["function"].get("arguments") or "{}")
            tool = {"role": "tool", "tool_call_id": c.get("id", ""), "name": c["function"]["name"], "content": res.text}
            turns.append(tool)
            msgs.append(tool)
    return turns, {"model": model, **usage}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("jobs", type=Path, help="directory with requests.jsonl")
    ap.add_argument("--base-url", required=True, help="OpenAI-compatible endpoint ending in /v1 (or similar)")
    ap.add_argument("--model", required=True, help="the provider's model id; overrides the one in requests.jsonl")
    ap.add_argument("--key-env", default="TEACHER_API_KEY", help="environment variable that holds the API key")
    ap.add_argument("--network-secret", action="store_true",
                    help="send no key: a Claude Code cloud session adds it from a network secret for the API host")
    ap.add_argument("--workers", type=int, default=16, help="requests in flight at once")
    ap.add_argument("--timeout", type=float, default=600)
    ap.add_argument("--limit", type=int, default=0, help="only the first N requests (0 = all)")
    ap.add_argument("--n", type=int, default=0, help="write the requests first: trajectories per school")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-rounds", type=int, default=4, help="version 4: teacher replies per conversation")
    ap.add_argument("--extra", default="", help='extra JSON merged into every request body, e.g. \'{"enable_thinking": true}\'')
    a = ap.parse_args()
    if a.model.lower().startswith(("claude", "anthropic")):
        sys.exit("Claude models are not allowed as teacher (amendment 4 Change 5)")
    key = os.environ.get(a.key_env)
    if not key and not a.network_secret:
        sys.exit(f"set {a.key_env} to your API key first (or pass --network-secret in a Claude Code cloud session)")
    if not (a.jobs / "requests.jsonl").exists():
        if not a.n:
            sys.exit(f"{a.jobs}/requests.jsonl not found: pass --n to create it")
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
        from mosaic.teacher import export_jobs  # standard library only

        print(f"wrote {export_jobs(a.n, a.seed, a.model, a.jobs)} requests to {a.jobs}")
    jobs = [json.loads(x) for x in (a.jobs / "requests.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    out = a.jobs / "results.jsonl"
    done = set()
    if out.exists():
        done = {json.loads(x)["custom_id"] for x in out.read_text(encoding="utf-8").splitlines() if x.strip()}
    todo = [j for j in jobs if j["custom_id"] not in done][: a.limit or None]
    print(f"{len(jobs)} requests, {len(done)} already done, {len(todo)} to send with {a.workers} workers")
    lock = threading.Lock()
    tokens = [0, 0]

    extra = json.loads(a.extra) if a.extra else {}

    def one(job: dict) -> str:
        body = dict(job["body"], model=a.model, **extra)
        if job.get("protocol", 3) >= 4:
            turns, info = converse(dict(job, body=body), lambda b: call(a.base_url, key, b, a.timeout), a.max_rounds)
            model = info.pop("model", a.model)
            usage = info
            line = {"custom_id": job["custom_id"], "model": model, "turns": turns, "usage": usage}
        else:
            resp = call(a.base_url, key, body, a.timeout)
            msg = resp["choices"][0]["message"]
            usage = resp.get("usage") or {}
            line = {"custom_id": job["custom_id"], "model": resp.get("model", a.model),
                    "content": msg.get("content") or "", "usage": usage}
        with lock:
            with out.open("a", encoding="utf-8") as f:
                f.write(json.dumps(line, ensure_ascii=False) + "\n")
            tokens[0] += usage.get("prompt_tokens", 0)
            tokens[1] += usage.get("completion_tokens", 0)
        return job["custom_id"]

    failed = 0
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        futs = {pool.submit(one, j): j["custom_id"] for j in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                f.result()
            except Exception as e:  # keep going; a re-run retries what failed
                failed += 1
                print(f"  failed {futs[f]}: {e}", file=sys.stderr)
            if i % 20 == 0 or i == len(todo):
                print(f"  {i}/{len(todo)} done, tokens in {tokens[0]:,} out {tokens[1]:,}, failed {failed}")
    print(f"results in {out}" + (f"; {failed} failed, run the same command again to retry them" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
