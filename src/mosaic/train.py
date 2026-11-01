"""`mosaic train`: LoRA SFT of one school adapter (recipe: research/prereg_drafts/exp01_amendment_4_DRAFT.md, Change 2).

Formatting is explicit, not left to a trainer: the prompt is the chat template applied to the conversation up to the
last user turn with `add_generation_prompt=True` and the same template options as at inference (Qwen3:
enable_thinking=False, which puts an empty think block into the generation prompt); the completion is the assistant
reply plus the end-of-turn token. Labels are -100 on the prompt, so loss is on assistant tokens only, and training sees
exactly the token sequence that inference continues from.

PEFT + the transformers Trainer are used (TRL's SFTTrainer adds nothing once masking is explicit).

Agent records (C-agent; a `tools` field and several assistant turns) give one example per assistant turn: the prompt
is what the agent loop (`mosaic.agent`) sends at that turn, i.e. the conversation so far rendered with the tools and
`add_generation_prompt=True`; the completion is the turn as the Qwen chat template writes it (content, then a
<tool_call> block per call) plus the end token. Tool results only ever appear in prompts, so they carry no loss.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

IGNORE = -100

RECIPE = dict(r=32, lora_alpha=64, lora_dropout=0.05, target_modules="all-linear", epochs=3, lr=2e-4,
              warmup_ratio=0.03, batch=16, max_len=4096, seed=20261030)


def split_conversation(messages: list[dict]) -> tuple[list[dict], str]:
    """(prompt messages, assistant reply). The last message must be the assistant's."""
    if not messages or messages[-1]["role"] != "assistant":
        raise ValueError("a training conversation must end with an assistant message")
    return messages[:-1], messages[-1]["content"]


def encode_example(tok, messages: list[dict], *, max_len: int = RECIPE["max_len"],
                   template_kwargs: dict | None = None, end_token: str | None = None) -> dict | None:
    """{input_ids, labels, attention_mask} or None if the example is longer than max_len (dropped, not truncated:
    a truncated trajectory would teach the model to stop mid-answer)."""
    prompt_msgs, reply = split_conversation(messages)
    prompt_ids = tok.apply_chat_template(prompt_msgs, add_generation_prompt=True, tokenize=True,
                                         **(template_kwargs or {}))
    if isinstance(prompt_ids, dict) or hasattr(prompt_ids, "input_ids"):  # transformers 5 may return a mapping
        prompt_ids = prompt_ids["input_ids"]
    end = end_token if end_token is not None else tok.eos_token
    comp_ids = tok(reply + end, add_special_tokens=False)["input_ids"]
    ids = list(prompt_ids) + list(comp_ids)
    if len(ids) > max_len:
        return None
    return {"input_ids": ids, "labels": [IGNORE] * len(prompt_ids) + list(comp_ids), "attention_mask": [1] * len(ids)}


def render_assistant(turn: dict) -> str:
    """An assistant turn as the Qwen3 chat template writes it: the content, then one <tool_call> block per call
    (a newline between blocks, and after non-empty content)."""
    content = turn.get("content") or ""
    out = content
    for i, c in enumerate(turn.get("tool_calls") or []):
        fn = c.get("function", c)
        args = fn.get("arguments", {})
        args = args if isinstance(args, str) else json.dumps(args, ensure_ascii=False)
        if i > 0 or content:
            out += "\n"
        out += '<tool_call>\n{"name": "' + fn["name"] + '", "arguments": ' + args + '}\n</tool_call>'
    return out


def _ids(x) -> list[int]:
    if isinstance(x, dict) or hasattr(x, "input_ids"):  # transformers 5 may return a mapping
        x = x["input_ids"]
    return list(x)


def encode_agent_example(tok, messages: list[dict], *, tools: list[dict], max_len: int = RECIPE["max_len"],
                         template_kwargs: dict | None = None, end_token: str | None = None,
                         check_template: bool = False) -> list[dict]:
    """One {input_ids, labels, attention_mask} per assistant turn (see the module docstring), or [] if any of them is
    longer than max_len (the conversation is dropped whole). With check_template, the turn rendered by the tokenizer's
    own template must end with the completion built here, so a template the renderer does not match fails loudly."""
    end = end_token if end_token is not None else tok.eos_token
    kw = dict(template_kwargs or {})
    out = []
    for k, m in enumerate(messages):
        if m["role"] != "assistant":
            continue
        prompt_ids = _ids(tok.apply_chat_template(messages[:k], tools=tools, add_generation_prompt=True,
                                                  tokenize=True, **kw))
        completion = render_assistant(m)
        if check_template:
            full = tok.apply_chat_template(messages[:k + 1], tools=tools, tokenize=False, **kw)
            if not full.rstrip().endswith((completion + end).rstrip()):
                raise ValueError(f"the chat template renders assistant turn {k} differently from render_assistant")
        comp_ids = _ids(tok(completion + end, add_special_tokens=False))
        ids = prompt_ids + comp_ids
        if len(ids) > max_len:
            return []
        out.append({"input_ids": ids, "labels": [IGNORE] * len(prompt_ids) + comp_ids, "attention_mask": [1] * len(ids)})
    return out


def load_records(path: str | Path) -> list[dict]:
    """Training records: {"messages": [...], "tools": [...] (agent format only)}."""
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if "messages" not in r:
                r = {"messages": [{"role": "user", "content": r["prompt"]},
                                  {"role": "assistant", "content": r["response"]}]}
            out.append(r)
    return out


def load_conversations(path: str | Path) -> list[list[dict]]:
    return [r["messages"] for r in load_records(path)]


def encode_records(tok, records: list[dict], *, max_len: int, template_kwargs: dict | None,
                   check_template: bool = False) -> tuple[list[dict], int]:
    """(examples, conversations dropped as too long). Agent records give one example per assistant turn."""
    rows, dropped = [], 0
    for i, r in enumerate(records):
        if r.get("tools"):
            ex = encode_agent_example(tok, r["messages"], tools=r["tools"], max_len=max_len,
                                      template_kwargs=template_kwargs, check_template=check_template and i < 3)
            rows += ex
            dropped += not ex
        else:
            e = encode_example(tok, r["messages"], max_len=max_len, template_kwargs=template_kwargs)
            if e:
                rows.append(e)
            else:
                dropped += 1
    return rows, dropped


def collate(batch: list[dict], pad_id: int) -> dict:
    import torch

    n = max(len(b["input_ids"]) for b in batch)
    ids = torch.full((len(batch), n), pad_id, dtype=torch.long)
    lab = torch.full((len(batch), n), IGNORE, dtype=torch.long)
    att = torch.zeros((len(batch), n), dtype=torch.long)
    for i, b in enumerate(batch):
        k = len(b["input_ids"])
        ids[i, :k], lab[i, :k], att[i, :k] = (torch.tensor(b["input_ids"]), torch.tensor(b["labels"]),
                                              torch.tensor(b["attention_mask"]))
    return {"input_ids": ids, "labels": lab, "attention_mask": att}


def train(*, base: str, data: str, out: str, template_kwargs: dict | None = None, max_steps: int = -1,
          epochs: float = RECIPE["epochs"], bits: int = 16, batch: int = RECIPE["batch"], micro_batch: int = 4,
          max_len: int = RECIPE["max_len"], seed: int = RECIPE["seed"]) -> dict:
    import torch
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from transformers import (AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments)

    tok = AutoTokenizer.from_pretrained(base)
    records = load_records(data)
    rows, dropped = encode_records(tok, records, max_len=max_len, template_kwargs=template_kwargs,
                                   check_template=True)
    if not rows:
        raise SystemExit("no trainable examples")
    kw: dict = {"dtype": torch.bfloat16}
    if bits == 4:
        from transformers import BitsAndBytesConfig
        kw["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                                       bnb_4bit_compute_dtype=torch.bfloat16)
    model = AutoModelForCausalLM.from_pretrained(base, device_map={"": 0}, **kw)
    if bits == 4:
        model = prepare_model_for_kbit_training(model)
    model.config.use_cache = False
    model = get_peft_model(model, LoraConfig(r=RECIPE["r"], lora_alpha=RECIPE["lora_alpha"],
                                             lora_dropout=RECIPE["lora_dropout"],
                                             target_modules=RECIPE["target_modules"], task_type="CAUSAL_LM"))
    if hasattr(model, "enable_input_require_grads"):
        model.enable_input_require_grads()
    micro = min(micro_batch, batch)
    total = max_steps if max_steps > 0 else int(-(-len(rows) // batch) * epochs)
    warmup = max(1, round(RECIPE["warmup_ratio"] * total))  # transformers 5 has no warmup_ratio
    args = TrainingArguments(output_dir=str(Path(out) / "_trainer"), per_device_train_batch_size=micro,
                             gradient_accumulation_steps=max(1, batch // micro), num_train_epochs=epochs,
                             max_steps=max_steps, learning_rate=RECIPE["lr"], lr_scheduler_type="cosine",
                             warmup_steps=warmup, bf16=True, logging_steps=1, save_strategy="no",
                             seed=seed, report_to=[], gradient_checkpointing=True, remove_unused_columns=False)
    pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    trainer = Trainer(model=model, args=args, train_dataset=rows, data_collator=lambda b: collate(b, pad))
    torch.cuda.reset_peak_memory_stats()
    t0 = time.time()
    res = trainer.train()
    secs = time.time() - t0
    model.save_pretrained(out)
    info = {"base": base, "data": str(data), "conversations": len(records), "examples": len(rows),
            "dropped_too_long": dropped,
            "steps": trainer.state.global_step, "train_loss": res.training_loss, "seconds": round(secs, 1),
            "peak_mem_gib": round(torch.cuda.max_memory_allocated() / 2**30, 1), "bits": bits,
            "template_kwargs": template_kwargs or {}, "recipe": RECIPE}
    (Path(out) / "train_info.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
    print(json.dumps(info, indent=2))
    return info
