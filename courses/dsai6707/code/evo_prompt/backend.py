"""Concurrent OpenAI-compatible backend on top of mosaic.backends.Backend (same cache keys and cache file format).

The HTTP client is standard library only (streamed chat completions, as scripts/teacher_api.py does, because the API
gateway cuts non-streamed replies that take longer than about 30 s). No key is written anywhere: if OPENAI_API_KEY is
set in the environment it is sent as a Bearer header, otherwise the sandbox proxy adds the credential for the host.
A shared Ledger enforces the USD budget across backends and records token usage for every real API call.
"""

from __future__ import annotations

import json
import os
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from mosaic.backends import Backend


class BudgetExceeded(RuntimeError):
    pass


class Ledger:
    def __init__(self, budget_usd: float, price_in: float, price_out: float):
        self.budget = budget_usd
        self.price = (price_in, price_out)
        self.spent = 0.0
        self.calls = 0
        self.tok_in = 0
        self.tok_out = 0
        self.lock = threading.Lock()

    def exhausted(self) -> bool:
        return self.spent >= self.budget

    def add(self, prompt_tokens: int, completion_tokens: int) -> None:
        with self.lock:
            self.calls += 1
            self.tok_in += prompt_tokens
            self.tok_out += completion_tokens
            self.spent += (prompt_tokens * self.price[0] + completion_tokens * self.price[1]) / 1e6


class OfflineBackend(Backend):
    """Deterministic, no network. Used by the offline tests and by `--offline` dry runs."""

    model_id = "offline-deterministic"

    def __init__(self, sampling: dict, cache, ledger: Ledger):
        super().__init__(sampling, cache)
        self.ledger = ledger

    def _generate(self, reqs):
        import hashlib
        import random

        from mosaic.teacher import ASSETS

        out = []
        for r in reqs:
            h = hashlib.sha256(json.dumps(r.messages, sort_keys=True).encode()).digest()
            rng = random.Random(int.from_bytes(h[:8], "big"))
            lines = "\n".join(f"{a}: {rng.choice(['LONG', 'SHORT', 'NEUTRAL'])} (conviction {rng.randint(1, 5)}) - synthetic"
                              for a in ASSETS)
            text = ("[Think]\nSynthetic reasoning.\n[Output]\nCausal chain: shock -> demand -> prices.\n"
                    "Scenarios:\nS1 (base case; growth up, inflation flat): 0.5\n"
                    "S2 (slowdown; growth down, inflation down): 0.3\n"
                    "S3 (overheating; growth up, inflation up): 0.2\nSignals:\n" + lines + "\n")
            self.ledger.add(0, 0)
            out.append({"text": text, "usage": {"prompt_tokens": 0, "completion_tokens": 0}, "seconds": 0.0})
        return out


class HTTPBackend(Backend):
    chunk_size = 64  # the cache is written after each chunk, so a budget stop or crash keeps every finished call

    def __init__(self, sampling: dict, cache, *, ledger: Ledger, model: str, base_url: str, workers: int = 16,
                 timeout: float = 300.0):
        super().__init__(sampling, cache)
        self.model_id = model
        self.ledger = ledger
        self.base_url = base_url.rstrip("/")
        self.workers = workers
        self.timeout = timeout

    def _send(self, r) -> dict:
        s = self.sampling
        body = {"model": self.model_id, "messages": r.messages, "temperature": s.get("temperature", 0.7),
                "top_p": s.get("top_p", 0.9), "max_tokens": s.get("max_tokens", 1024), "seed": s.get("seed", 0),
                "stream": True, "stream_options": {"include_usage": True}}
        if "enable_thinking" in s:
            body["enable_thinking"] = bool(s["enable_thinking"])
        headers = {"Content-Type": "application/json", "User-Agent": "macro-mosaic-dsai6707/1.0"}
        key = os.environ.get("OPENAI_API_KEY")
        if key:
            headers["Authorization"] = f"Bearer {key}"
        req = urllib.request.Request(self.base_url + "/chat/completions", data=json.dumps(body).encode(),
                                     headers=headers)
        for attempt in range(5):
            try:
                parts: list[str] = []
                usage: dict = {}
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    for raw in resp:
                        line = raw.decode("utf-8", errors="replace").strip()
                        if not line.startswith("data:") or line.endswith("[DONE]"):
                            continue
                        chunk = json.loads(line[5:])
                        usage = chunk.get("usage") or usage
                        for ch in chunk.get("choices") or []:
                            parts.append((ch.get("delta") or {}).get("content") or "")
                return {"text": "".join(parts),
                        "usage": {"prompt_tokens": usage.get("prompt_tokens", 0),
                                  "completion_tokens": usage.get("completion_tokens", 0)}}
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503, 504) and attempt < 4:
                    time.sleep(2 ** attempt * 3)
                    continue
                raise RuntimeError(f"API HTTP {e.code}") from None
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                if attempt < 4:
                    time.sleep(2 ** attempt * 3)
                    continue
                raise
        raise RuntimeError("unreachable")

    def _one(self, r) -> dict:
        if self.ledger.exhausted():
            raise BudgetExceeded(f"API budget {self.ledger.budget} USD spent ({self.ledger.spent:.2f})")
        t0 = time.time()
        res = self._send(r)
        u = res["usage"]
        self.ledger.add(u["prompt_tokens"], u["completion_tokens"])
        return {"text": res["text"], "usage": u, "seconds": time.time() - t0}

    def _generate(self, reqs):
        out: list = [None] * len(reqs)
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            futs = {pool.submit(self._one, r): i for i, r in enumerate(reqs)}
            for f, i in futs.items():
                out[i] = f.result()
        return out


class AnthropicBackend(Backend):
    """Claude models through the official Anthropic SDK (reads ANTHROPIC_API_KEY from the environment; no key is
    written anywhere). System messages are passed as the top-level system prompt. Only max_tokens and the thinking
    setting are sent; any other sampling entry (e.g. the seed) only distinguishes cache keys."""

    chunk_size = 64

    def __init__(self, sampling: dict, cache, *, ledger: Ledger, model: str, workers: int = 8):
        super().__init__(sampling, cache)
        import anthropic

        self.model_id = model
        self.ledger = ledger
        self.workers = workers
        self.client = anthropic.Anthropic(max_retries=6)

    def _one(self, r) -> dict:
        if self.ledger.exhausted():
            raise BudgetExceeded(f"API budget {self.ledger.budget} USD spent ({self.ledger.spent:.2f})")
        system = "\n\n".join(m["content"] for m in r.messages if m["role"] == "system")
        msgs = [{"role": m["role"], "content": m["content"]} for m in r.messages if m["role"] != "system"]
        kw = {"model": self.model_id, "max_tokens": self.sampling.get("max_tokens", 1024), "messages": msgs,
              "thinking": {"type": self.sampling.get("thinking", "disabled")}}
        if system:
            kw["system"] = system
        t0 = time.time()
        resp = self.client.messages.create(**kw)
        text = "".join(b.text for b in resp.content if b.type == "text")
        u = {"prompt_tokens": resp.usage.input_tokens, "completion_tokens": resp.usage.output_tokens}
        self.ledger.add(u["prompt_tokens"], u["completion_tokens"])
        return {"text": text, "usage": u, "seconds": time.time() - t0, "stop_reason": resp.stop_reason}

    def _generate(self, reqs):
        out: list = [None] * len(reqs)
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            futs = {pool.submit(self._one, r): i for i, r in enumerate(reqs)}
            for f, i in futs.items():
                out[i] = f.result()
        return out
