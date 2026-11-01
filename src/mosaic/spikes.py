"""Task S spikes (program.md): GPU paths proven on dummy data under scratch/ (never data/events/).

  mosaic spike env      package versions and GPU
  mosaic spike dummy    write scratch/events.jsonl (3 events) and scratch/traj/<school>.jsonl (50 each)
  mosaic spike serve    S1: Qwen3-8B through VLLMBackend, non-thinking, tokens/s, no <think> block
"""

from __future__ import annotations

import importlib
import json
import time
from pathlib import Path

from mosaic import SCHOOLS
from mosaic.backends import FakeBackend, Request, VLLMBackend
from mosaic.config import ROOT
from mosaic.data import Event, read_jsonl, write_jsonl
from mosaic.prompts import build_messages, read_prompt

SCRATCH = ROOT / "scratch"

PUBLIC_TOPICS = [
    "The central bank raises its policy rate by 25 basis points while inflation runs above target.",
    "A government announces a large fiscal stimulus package after two quarters of falling output.",
    "Oil prices double within a year after a supply disruption in a major producing region.",
]


def versions() -> dict:
    out = {}
    for m in ("torch", "vllm", "transformers", "peft", "trl", "accelerate", "datasets", "safetensors", "bitsandbytes",
              "flash_attn"):
        try:
            out[m] = getattr(importlib.import_module(m), "__version__", "?")
        except Exception as e:  # noqa: BLE001
            out[m] = f"missing ({type(e).__name__})"
    try:
        import torch
        if torch.cuda.is_available():
            out["gpu"] = torch.cuda.get_device_name(0)
    except Exception:  # noqa: BLE001
        pass
    return out


def dummy_events(n: int = 3) -> list[Event]:
    return [Event(id=f"dummy-{i}", text=t, category="monetary" if i == 0 else "fiscal" if i == 1 else "commodity")
            for i, t in enumerate(PUBLIC_TOPICS[:n])]


def make_dummy(n_traj: int = 50) -> None:
    ev = dummy_events()
    write_jsonl(SCRATCH / "events.jsonl", [{"id": e.id, "text": e.text, "category": e.category} for e in ev])
    tmpl = read_prompt("user_template.txt")
    fake = FakeBackend({})
    for s in SCHOOLS:
        system = read_prompt(f"{s}.system.txt")
        rows = []
        for i in range(n_traj):
            e = Event(id=f"dummy-traj-{i}", text=f"{PUBLIC_TOPICS[i % 3]} (variant {i})", category="dummy")
            msgs = build_messages("A", s, e, system=system, user_template=tmpl)
            text = fake.generate([Request(msgs)])[0]["text"]
            rows.append({"messages": msgs + [{"role": "assistant", "content": text}]})
        write_jsonl(SCRATCH / "traj" / f"{s}.jsonl", rows)
    print(f"wrote {SCRATCH}/events.jsonl and {n_traj} trajectories per school")


def serve(model: str = "Qwen/Qwen3-8B", adapters: dict[str, str] | None = None, tag: str = "S1",
          gpu_util: float = 0.90, engine_kwargs: dict | None = None) -> dict:
    """Generate for the dummy events with arm A messages (or arm C when adapters are given)."""
    from mosaic.data import load_events

    events = load_events(SCRATCH / "events.jsonl")
    be = VLLMBackend({"temperature": 0.7, "top_p": 0.9, "max_tokens": 1024, "seed": 20261030}, None,
                     base_model=model, adapters=adapters or {}, max_model_len=8192, max_lora_rank=32,
                     gpu_memory_utilization=gpu_util, engine_kwargs=engine_kwargs,
                     chat_template_kwargs={"enable_thinking": False})
    tmpl = read_prompt("user_template.txt")
    schools = sorted(adapters) if adapters else list(SCHOOLS)
    reqs = [Request(build_messages("C" if adapters else "A", s, e, system=read_prompt(f"{s}.system.txt"),
                                   user_template=tmpl), adapter=s if adapters else None, tag=f"{tag}|{s}|{e.id}")
            for s in schools for e in events]
    be._engine()  # load outside the timer
    t0 = time.time()
    res = be.generate(reqs)
    wall = time.time() - t0
    toks = sum(r["usage"]["completion_tokens"] for r in res)
    summary = {"tag": tag, "model": model, "requests": len(res), "completion_tokens": toks, "wall_s": round(wall, 2),
               "tokens_per_s": round(toks / wall, 1), "with_think_block": sum("<think>" in r["text"] or "reasoning" in r
                                                                              for r in res),
               "with_output_marker": sum("[Output]" in r["text"] for r in res)}
    out = SCRATCH / f"{tag}_outputs.jsonl"
    write_jsonl(out, [{"tag": r["tag"], "text": r["text"], "usage": r["usage"]} for r in res])
    print(json.dumps(summary, indent=2))
    print("--- first output ---\n" + res[0]["text"][:1500])
    return summary


def rename_adapter(src: Path, dst: Path, old: str, new: str) -> int:
    """Copy a PEFT adapter, renaming weight keys containing `old` to `new` (e.g. trained on the text-only class
    Qwen3_5ForCausalLM, served by vLLM as the multimodal Qwen3_5ForConditionalGeneration, whose text layers live under
    `model.language_model`)."""
    import shutil

    from safetensors.torch import load_file, save_file

    dst.mkdir(parents=True, exist_ok=True)
    for f in ("adapter_config.json",):
        shutil.copy(src / f, dst / f)
    w = load_file(str(src / "adapter_model.safetensors"))
    out = {k.replace(old, new, 1): v for k, v in w.items()}
    save_file(out, str(dst / "adapter_model.safetensors"), metadata={"format": "pt"})
    n = sum(k != k2 for k, k2 in zip(w, out))
    print(f"renamed {n}/{len(w)} keys: {old} -> {new}")
    return n


def main(args) -> int:
    if args.spike_cmd == "env":
        print(json.dumps(versions(), indent=2))
    elif args.spike_cmd == "hf-ls":
        from huggingface_hub import HfApi, hf_hub_download
        info = HfApi().model_info(args.repo, files_metadata=True)
        for s in info.siblings:
            print(s.rfilename, s.size)
        try:
            print(Path(hf_hub_download(args.repo, "README.md")).read_text(encoding="utf-8")[:6000])
        except Exception as e:  # noqa: BLE001
            print("no README:", e)
    elif args.spike_cmd == "sae":
        from mosaic import sae
        texts = sae.public_paragraphs(args.n)
        print(len(texts), "paragraphs")
        sae.gate(args.model, args.repo, [int(x) for x in args.layers.split(",")], texts, args.chat,
                 out_path=SCRATCH / f"S3_{args.tag}.json")
    elif args.spike_cmd == "adapter-rename":
        rename_adapter(Path(args.src), Path(args.dst), args.old, args.new)
    elif args.spike_cmd == "dummy":
        make_dummy()
    elif args.spike_cmd == "serve":
        adapters = None
        if args.adapters_dir:
            adapters = {s: str(Path(args.adapters_dir) / s) for s in SCHOOLS if (Path(args.adapters_dir) / s).is_dir()}
        serve(args.model, adapters, args.tag, args.gpu_util,
              {"max_num_batched_tokens": args.max_batched_tokens, "max_num_seqs": 16}
              if args.max_batched_tokens else None)
    return 0


__all__ = ["main", "versions", "make_dummy", "serve", "read_jsonl"]
