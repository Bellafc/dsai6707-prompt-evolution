"""Offline tests for `mosaic train` formatting and loss masking (fake tokenizer, no torch needed for encoding)."""

import pytest

from mosaic.train import IGNORE, collate, encode_example, split_conversation


class FakeTok:
    """Character-level tokenizer with a ChatML-like template; mimics Qwen3's empty think block in the generation
    prompt when enable_thinking=False."""

    eos_token = "<|im_end|>"

    def _render(self, msgs, gen, enable_thinking=True):
        s = "".join(f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n" for m in msgs)
        if gen:
            s += "<|im_start|>assistant\n" + ("" if enable_thinking else "<think>\n\n</think>\n\n")
        return s

    def apply_chat_template(self, msgs, add_generation_prompt=False, tokenize=True, **kw):
        s = self._render(msgs, add_generation_prompt, **kw)
        return [ord(c) for c in s] if tokenize else s

    def __call__(self, text, add_special_tokens=False):
        return {"input_ids": [ord(c) for c in text]}


MSGS = [{"role": "system", "content": "SYS"}, {"role": "user", "content": "Q?"},
        {"role": "assistant", "content": "[Think] a\n[Output] b"}]


def decode(ids):
    return "".join(chr(i) for i in ids)


def test_loss_only_on_assistant_tokens():
    ex = encode_example(FakeTok(), MSGS, template_kwargs={"enable_thinking": False})
    trained = decode([i for i, l in zip(ex["input_ids"], ex["labels"]) if l != IGNORE])
    assert trained == "[Think] a\n[Output] b<|im_end|>"
    assert all(l == IGNORE for l in ex["labels"][:len(ex["labels"]) - len(trained)])
    assert [l for l in ex["labels"] if l != IGNORE] == [i for i, l in zip(ex["input_ids"], ex["labels"]) if l != IGNORE]


def test_prompt_matches_inference_in_non_thinking_mode():
    ex = encode_example(FakeTok(), MSGS, template_kwargs={"enable_thinking": False})
    text = decode(ex["input_ids"])
    assert "<|im_start|>assistant\n<think>\n\n</think>\n\n[Think] a" in text
    infer = FakeTok().apply_chat_template(MSGS[:-1], add_generation_prompt=True, tokenize=False, enable_thinking=False)
    assert text.startswith(infer)


def test_too_long_example_is_dropped_not_truncated():
    assert encode_example(FakeTok(), MSGS, max_len=10) is None


def test_conversation_must_end_with_assistant():
    with pytest.raises(ValueError):
        split_conversation(MSGS[:-1])


def test_collate_pads_labels_with_ignore():
    torch = pytest.importorskip("torch")
    a = encode_example(FakeTok(), MSGS)
    b = encode_example(FakeTok(), MSGS[:1] + [{"role": "user", "content": "longer question here"}, MSGS[2]])
    out = collate([a, b], pad_id=0)
    assert out["input_ids"].shape == out["labels"].shape == out["attention_mask"].shape
    short = 0 if len(a["input_ids"]) < len(b["input_ids"]) else 1
    n = len(([a, b][short])["input_ids"])
    assert (out["labels"][short, n:] == IGNORE).all() and (out["attention_mask"][short, n:] == 0).all()
    assert isinstance(out["input_ids"], torch.Tensor)
