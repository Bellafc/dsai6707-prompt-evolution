"""Qwen-Scope SAE reader (exp06, early reading of gate S0).

Checkpoint `layer{n}.sae.pt`: dict W_enc (d_sae, d_model), W_dec (d_model, d_sae), b_enc, b_dec; TopK encoder; hook
point = residual stream output of decoder layer n (`model.model.layers[n]`). The model card encodes as
`topk(x @ W_enc.T + b_enc)`; `center` (subtract b_dec first) is the common alternative and is compared in the gate.

Gate quantities, on response tokens (position 0 excluded: attention-sink outlier):
  FVU          sum |x - x_hat|^2 / sum |x - mean(x)|^2
  CE recovered 1 - (CE_splice - CE_clean) / (CE_meanablate - CE_clean)
"""

from __future__ import annotations

import json
from pathlib import Path


def load_sae(repo: str, layer: int, device: str = "cuda"):
    import torch
    from huggingface_hub import hf_hub_download

    d = torch.load(hf_hub_download(repo, f"layer{layer}.sae.pt"), map_location="cpu")
    return {k: v.to(device=device, dtype=torch.float32) for k, v in d.items()}


def encode(sae: dict, x, k: int = 50, center: bool = False):
    """x (..., d_model) float32 → sparse (..., d_sae): TopK of the pre-activations."""
    import torch

    xin = x - sae["b_dec"] if center else x
    pre = xin @ sae["W_enc"].T + sae["b_enc"]
    vals, idx = pre.topk(k, dim=-1)
    return torch.zeros_like(pre).scatter_(-1, idx, vals)


def decode(sae: dict, acts):
    return acts @ sae["W_dec"].T + sae["b_dec"]


def fvu_parts(x, x_hat):
    """(residual sum of squares, total sum of squares) over rows of (n, d)."""
    return ((x - x_hat) ** 2).sum().item(), ((x - x.mean(0, keepdim=True)) ** 2).sum().item()


def ce_recovered(ce_clean: float, ce_splice: float, ce_mean: float) -> float:
    return 1.0 - (ce_splice - ce_clean) / (ce_mean - ce_clean)


def public_paragraphs(n: int = 200, min_words: int = 60, max_words: int = 200) -> list[str]:
    """Neutral public text: paragraphs of WikiText-103 (test split), no economics selection."""
    from datasets import load_dataset

    out = []
    ds = load_dataset("Salesforce/wikitext", "wikitext-103-raw-v1", split="test")
    for row in ds:
        t = row["text"].strip()
        if t and not t.startswith("=") and min_words <= len(t.split()) <= max_words:
            out.append(t.replace(" @-@ ", "-").replace(" @,@ ", ",").replace(" @.@ ", "."))
        if len(out) >= n:
            break
    return out


def gate(model_id: str, repo: str, layers: list[int], texts: list[str], chat: bool, k: int = 50,
         out_path: Path | None = None) -> dict:
    """FVU and CE recovered per layer for one model reading `texts` (plain text, or as an assistant reply in the Qwen3
    chat format with the empty think block, loss/FVU on reply tokens only)."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.bfloat16, device_map={"": 0}).eval()
    saes = {L: load_sae(repo, L) for L in layers}
    cap: dict[int, torch.Tensor] = {}
    mode = {"kind": "capture"}  # capture | splice | mean
    means: dict[int, torch.Tensor] = {}
    target = {"L": None}

    def make_hook(L):
        def hook(_m, _i, output):
            h = output[0] if isinstance(output, tuple) else output
            if mode["kind"] == "capture":
                cap[L] = h.detach()
                return None
            if target["L"] != L:
                return None
            if mode["kind"] == "splice":
                new = decode(saes[L], encode(saes[L], h.float(), k, CENTER)).to(h.dtype)
            else:
                new = means[L].to(h.dtype).expand_as(h)
            return (new, *output[1:]) if isinstance(output, tuple) else new
        return hook

    handles = [model.model.layers[L].register_forward_hook(make_hook(L)) for L in layers]

    def prepare(text):
        if not chat:
            ids = tok(text, return_tensors="pt", add_special_tokens=False)["input_ids"][:, :512]
            return ids.to("cuda"), 1
        prompt = tok.apply_chat_template([{"role": "user", "content": "Write a short informative paragraph."}],
                                         add_generation_prompt=True, tokenize=True, enable_thinking=False)
        if not isinstance(prompt, list):
            prompt = prompt["input_ids"]
        body = tok(text + tok.eos_token, add_special_tokens=False)["input_ids"][:512]
        return torch.tensor([prompt + body], device="cuda"), len(prompt)

    def ce(logits, ids, start):
        lg = logits[0, start - 1:-1].float()
        return torch.nn.functional.cross_entropy(lg, ids[0, start:], reduction="sum").item(), ids.shape[1] - start

    res = {}
    for CENTER in (False, True):
        stats = {L: {"rss": 0.0, "tss": 0.0, "sum": None, "n": 0} for L in layers}
        ce_sum, ce_n = 0.0, 0
        mode["kind"] = "capture"
        # pass 1: clean CE, FVU, token mean of the residual
        xs = {L: [] for L in layers}
        for t in texts:
            ids, start = prepare(t)
            with torch.no_grad():
                logits = model(ids).logits
            c, n = ce(logits, ids, start)
            ce_sum, ce_n = ce_sum + c, ce_n + n
            for L in layers:
                x = cap[L][0, start:].float()
                rss, tss = fvu_parts(x, decode(saes[L], encode(saes[L], x, k, CENTER)))
                stats[L]["rss"] += rss
                stats[L]["sum"] = x.sum(0) if stats[L]["sum"] is None else stats[L]["sum"] + x.sum(0)
                stats[L]["n"] += x.shape[0]
                xs[L].append(x.mean(0))
        # total sum of squares uses the global mean, so recompute exactly with a second capture pass
        for L in layers:
            means[L] = (stats[L]["sum"] / stats[L]["n"]).view(1, 1, -1)
        for t in texts:
            ids, start = prepare(t)
            with torch.no_grad():
                model(ids)
            for L in layers:
                x = cap[L][0, start:].float()
                stats[L]["tss"] += ((x - means[L].view(1, -1)) ** 2).sum().item()
        ce_clean = ce_sum / ce_n
        for L in layers:
            ces = {}
            for kind in ("splice", "mean"):
                mode["kind"], target["L"] = kind, L
                s, n = 0.0, 0
                for t in texts:
                    ids, start = prepare(t)
                    with torch.no_grad():
                        logits = model(ids).logits
                    c, m = ce(logits, ids, start)
                    s, n = s + c, n + m
                ces[kind] = s / n
            res[f"{'center' if CENTER else 'card'}|L{L}"] = {
                "fvu": stats[L]["rss"] / stats[L]["tss"], "ce_clean": ce_clean, "ce_splice": ces["splice"],
                "ce_mean_ablate": ces["mean"],
                "ce_recovered": ce_recovered(ce_clean, ces["splice"], ces["mean"]), "tokens": stats[L]["n"]}
            print(model_id, "chat" if chat else "plain", "center" if CENTER else "card", f"L{L}", res[f"{'center' if CENTER else 'card'}|L{L}"], flush=True)
    for h in handles:
        h.remove()
    if out_path:
        out_path.write_text(json.dumps(res, indent=2), encoding="utf-8")
    return res
