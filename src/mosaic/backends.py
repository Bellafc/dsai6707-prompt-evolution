"""Generation backends with a shared on-disk cache.

Every generation is keyed by sha256(model, adapter, messages, sampling); a rerun with the same key reads the cache
instead of the GPU/API, so re-scoring or re-reporting never regenerates. The cache is append-only JSONL under
cache/ (not versioned; large).

  fake    deterministic, offline, for tests and dry runs
  vllm    Qwen2.5-7B-Instruct with optional LoRA adapters (one engine, adapters switched per request)
  openai  API teacher (arm D); stops when the run's dollar budget is spent
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

from mosaic.config import stable_hash


@dataclass
class Request:
    messages: list[dict]
    adapter: str | None = None  # school name for arm C, else None
    tag: str = ""  # free text, e.g. "A|keynesian|evt-12"


class Cache:
    def __init__(self, path: Path):
        self.path = path
        self.mem: dict[str, dict] = {}
        if path.exists():
            with open(path, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        r = json.loads(line)
                        self.mem[r["key"]] = r

    def get(self, key: str) -> dict | None:
        return self.mem.get(key)

    def put(self, key: str, rec: dict) -> None:
        rec = {"key": key, **rec}
        self.mem[key] = rec
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


class Backend:
    model_id = "base"
    chunk_size = 512

    def __init__(self, sampling: dict, cache: Cache | None = None):
        self.sampling = sampling
        self.cache = cache

    def key(self, r: Request) -> str:
        return stable_hash({"model": self.model_id, "adapter": r.adapter, "messages": r.messages,
                            "sampling": self.sampling})

    def generate(self, reqs: list[Request]) -> list[dict]:
        """[{text, cached, usage, seconds}] in request order."""
        keys = [self.key(r) for r in reqs]
        out: list[dict | None] = [None] * len(reqs)
        todo = []
        for i, k in enumerate(keys):
            hit = self.cache.get(k) if self.cache else None
            if hit:
                out[i] = {**hit, "cached": True}
            else:
                todo.append(i)
        # chunked so that a crash or budget stop keeps everything generated so far in the cache
        for c in range(0, len(todo), self.chunk_size):
            part = todo[c:c + self.chunk_size]
            fresh = self._generate([reqs[i] for i in part])
            for i, rec in zip(part, fresh):
                rec = {**rec, "model": self.model_id, "adapter": reqs[i].adapter, "tag": reqs[i].tag}
                if self.cache:
                    self.cache.put(keys[i], rec)
                out[i] = {**rec, "key": keys[i], "cached": False}
        return out  # type: ignore[return-value]

    def _generate(self, reqs: list[Request]) -> list[dict]:
        raise NotImplementedError


class FakeBackend(Backend):
    """Echoes a well-formed trajectory whose vocabulary depends on the school named in the system prompt;
    adapter requests get 'purer' vocabulary than prompt-only requests, so tests can see an effect."""

    model_id = "fake"
    VOCAB = {
        "keynesian": "aggregate demand multiplier output gap fiscal",
        "austrian": "malinvestment capital structure time preference",
        "monetarist": "money supply MV=PQ quantity theory M2",
    }

    def _generate(self, reqs):
        out = []
        for r in reqs:
            sys = r.messages[0]["content"].lower()
            school = next((s for s in self.VOCAB if s in sys), "keynesian")
            words = self.VOCAB[school]
            leak = "" if r.adapter else " aggregate demand" if school != "keynesian" else " malinvestment"
            direction = {"keynesian": "LONG", "austrian": "SHORT", "monetarist": "NEUTRAL"}[school]
            text = (f"[Think] Considering {words}{leak}.\n[ToolCall: query_episode_db]\n[Observe] analogues\n"
                    f"[Think] Causal chain: shock -> {words.split()[0]} -> prices.\n"
                    f"[Output]\nCausal chain: shock -> {words.split()[0]} -> asset prices\n"
                    f"Scenarios:\n- Soft landing: 0.5\n- Recession: 0.3\n- Overheating: 0.2\n"
                    f"Signals:\n- SPX: {direction} (conviction 0.6)\n- UST10Y: LONG (conviction 0.4)\n"
                    f"- GOLD: {'LONG' if school == 'austrian' else 'NEUTRAL'} (conviction 0.5)\n")
            out.append({"text": text, "usage": {"prompt_tokens": 0, "completion_tokens": 0}, "seconds": 0.0})
        return out


class VLLMBackend(Backend):
    def __init__(self, sampling: dict, cache: Cache | None, *, base_model: str, adapters: dict[str, str],
                 max_model_len: int = 16384, gpu_memory_utilization: float = 0.90, max_lora_rank: int = 32):
        super().__init__(sampling, cache)
        self.model_id = base_model
        self.adapters = adapters
        self._llm = None
        self._opts = dict(max_model_len=max_model_len, gpu_memory_utilization=gpu_memory_utilization,
                          max_lora_rank=max_lora_rank)

    def _engine(self):
        if self._llm is None:
            from vllm import LLM  # imported lazily: not installed on CPU machines

            self._llm = LLM(model=self.model_id, enable_lora=bool(self.adapters), max_loras=max(1, len(self.adapters)),
                            max_lora_rank=self._opts["max_lora_rank"], max_model_len=self._opts["max_model_len"],
                            gpu_memory_utilization=self._opts["gpu_memory_utilization"], seed=self.sampling.get("seed", 0))
        return self._llm

    def _generate(self, reqs):
        from vllm import SamplingParams
        from vllm.lora.request import LoRARequest

        llm = self._engine()
        sp = SamplingParams(temperature=self.sampling.get("temperature", 0.7), top_p=self.sampling.get("top_p", 0.9),
                            max_tokens=self.sampling.get("max_tokens", 2048), seed=self.sampling.get("seed", 0))
        out: list[dict | None] = [None] * len(reqs)
        groups: dict[str | None, list[int]] = {}
        for i, r in enumerate(reqs):
            groups.setdefault(r.adapter, []).append(i)
        for adapter, idx in groups.items():
            lora = None
            if adapter:
                lora = LoRARequest(adapter, sorted(self.adapters).index(adapter) + 1, self.adapters[adapter])
            t0 = time.time()
            res = llm.chat([reqs[i].messages for i in idx], sp, lora_request=lora, use_tqdm=True)
            dt = (time.time() - t0) / max(1, len(idx))
            for i, r in zip(idx, res):
                o = r.outputs[0]
                out[i] = {"text": o.text, "seconds": dt,
                          "usage": {"prompt_tokens": len(r.prompt_token_ids), "completion_tokens": len(o.token_ids)}}
        return out  # type: ignore[return-value]


class BudgetExceeded(RuntimeError):
    pass


class OpenAIBackend(Backend):
    chunk_size = 1

    def __init__(self, sampling: dict, cache: Cache | None, *, model: str, usd_per_mtok_in: float,
                 usd_per_mtok_out: float, budget_usd: float):
        super().__init__(sampling, cache)
        self.model_id = model
        self.price = (usd_per_mtok_in, usd_per_mtok_out)
        self.budget = budget_usd
        self.spent = 0.0

    def _generate(self, reqs):
        from openai import OpenAI

        client = OpenAI()
        out = []
        for r in reqs:
            if self.spent >= self.budget:
                raise BudgetExceeded(f"API budget {self.budget} USD spent ({self.spent:.2f})")
            t0 = time.time()
            for attempt in range(4):
                try:
                    resp = client.chat.completions.create(
                        model=self.model_id, messages=r.messages, temperature=self.sampling.get("temperature", 0.7),
                        top_p=self.sampling.get("top_p", 0.9), max_tokens=self.sampling.get("max_tokens", 2048),
                        seed=self.sampling.get("seed", 0))
                    break
                except Exception:  # noqa: BLE001
                    if attempt == 3:
                        raise
                    time.sleep(2 ** attempt * 5)
            u = resp.usage
            self.spent += (u.prompt_tokens * self.price[0] + u.completion_tokens * self.price[1]) / 1e6
            out.append({"text": resp.choices[0].message.content or "", "seconds": time.time() - t0,
                        "usage": {"prompt_tokens": u.prompt_tokens, "completion_tokens": u.completion_tokens}})
        return out


class ClaudeUnavailable(RuntimeError):
    pass


class ClaudeCLIBackend(Backend):
    """Claude through `claude -p`, billed to whatever the CLI is logged in with (a Claude subscription via
    `claude auth login` or CLAUDE_CODE_OAUTH_TOKEN from `claude setup-token`).

    The call is made as close to a bare model call as the CLI allows: the system prompt is replaced entirely
    (--system-prompt-file), all tools and MCP servers are off, customizations are not loaded (--safe-mode), one
    turn, run from an empty directory, nothing persisted. Sampling cannot be set through the CLI (no temperature
    or top-p): the model's defaults apply and the reasoning effort is fixed by config. This is a documented
    deviation in prereg/exp01_amendment_1.md. Usage-limit or auth errors stop the run; the cache keeps every
    response already received, so rerunning the same command resumes.
    """

    chunk_size = 1

    def __init__(self, sampling: dict, cache: Cache | None, *, model: str, effort: str | None = None,
                 timeout_s: int = 900, executable: str = "claude"):
        super().__init__(sampling, cache)
        self.model = model
        self.effort = effort
        self.timeout_s = timeout_s
        self.executable = executable
        self.model_id = f"claude-cli:{model}:effort={effort or 'default'}"
        self.spent = 0.0  # the CLI's own cost estimate; on a subscription nothing is billed per call

    def command(self, system_file: str) -> list[str]:
        cmd = [self.executable, "-p", "--model", self.model, "--system-prompt-file", system_file,
               "--tools", "", "--disallowedTools", "mcp__*", "--strict-mcp-config", "--safe-mode",
               "--no-session-persistence", "--max-turns", "1", "--output-format", "json"]
        if self.effort:
            cmd += ["--effort", self.effort]
        return cmd

    def _generate(self, reqs):
        import subprocess
        import tempfile

        out = []
        for r in reqs:
            if len(r.messages) != 2 or r.messages[0]["role"] != "system":
                raise ValueError("ClaudeCLIBackend takes exactly [system, user] (arms D/T, not few-shot)")
            with tempfile.TemporaryDirectory(prefix="mosaic-claude-") as tmp:
                sys_file = f"{tmp}/system.txt"
                with open(sys_file, "w", encoding="utf-8") as f:
                    f.write(r.messages[0]["content"])
                t0 = time.time()
                try:
                    proc = subprocess.run(self.command(sys_file), input=r.messages[1]["content"], cwd=tmp,
                                          capture_output=True, text=True, timeout=self.timeout_s)
                except FileNotFoundError as e:
                    raise ClaudeUnavailable("`claude` not found on PATH (run setup/runpod_setup.sh)") from e
                except subprocess.TimeoutExpired as e:
                    raise ClaudeUnavailable(f"claude -p timed out after {self.timeout_s}s ({r.tag})") from e
            try:
                res = json.loads(proc.stdout)
            except json.JSONDecodeError as e:
                raise ClaudeUnavailable(f"unreadable claude output (exit {proc.returncode}): "
                                        f"{(proc.stdout or proc.stderr)[:300]}") from e
            if res.get("is_error") or proc.returncode != 0 or res.get("subtype", "success") != "success":
                raise ClaudeUnavailable(f"claude -p failed ({res.get('subtype')}): {str(res.get('result'))[:300]} "
                                        "— usage limit or login? Progress so far is cached; rerun to resume.")
            u = res.get("usage") or {}
            self.spent += float(res.get("total_cost_usd") or 0.0)
            out.append({"text": res.get("result") or "", "seconds": time.time() - t0,
                        "usage": {"prompt_tokens": u.get("input_tokens", 0),
                                  "completion_tokens": u.get("output_tokens", 0)}})
        return out
