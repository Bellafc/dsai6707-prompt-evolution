"""Cache-key and output handling of the local-model backend (no vLLM needed: generation is never called)."""

import json

import mosaic.locks as locks
from mosaic import SCHOOLS
from mosaic.backends import Request, VLLMBackend, adapter_fingerprint, split_reasoning

SAMPLING = {"temperature": 0.7, "top_p": 0.9, "max_tokens": 16, "seed": 1}
MSGS = [{"role": "system", "content": "You are a Keynesian."}, {"role": "user", "content": "Event"}]


def make_adapter(d, weights=b"w1"):
    d.mkdir(parents=True, exist_ok=True)
    (d / "adapter_config.json").write_text(json.dumps({"r": 32, "lora_alpha": 64}))
    (d / "adapter_model.safetensors").write_bytes(weights)
    return d


def test_retrained_adapter_changes_the_cache_key(tmp_path):
    ad = make_adapter(tmp_path / "keynesian")
    before = VLLMBackend(SAMPLING, None, base_model="Qwen/Qwen3-8B", adapters={"keynesian": str(ad)})
    k1 = before.key(Request(MSGS, adapter="keynesian"))
    make_adapter(ad, weights=b"w2")  # same name, new weights
    after = VLLMBackend(SAMPLING, None, base_model="Qwen/Qwen3-8B", adapters={"keynesian": str(ad)})
    assert after.key(Request(MSGS, adapter="keynesian")) != k1
    # prompt-only requests do not depend on adapter files
    assert before.key(Request(MSGS)) == after.key(Request(MSGS))
    assert adapter_fingerprint(tmp_path / "missing") is None


def test_chat_template_options_change_the_key():
    plain = VLLMBackend(SAMPLING, None, base_model="Qwen/Qwen3-8B", adapters={})
    nothink = VLLMBackend(SAMPLING, None, base_model="Qwen/Qwen3-8B", adapters={},
                          chat_template_kwargs={"enable_thinking": False})
    think = VLLMBackend(SAMPLING, None, base_model="Qwen/Qwen3-8B", adapters={},
                        chat_template_kwargs={"enable_thinking": True})
    keys = {b.key(Request(MSGS)) for b in (plain, nothink, think)}
    assert len(keys) == 3


def test_split_reasoning():
    assert split_reasoning("<think>\nweigh demand\n</think>\n\n[Output]\n- SPX: LONG") == (
        "weigh demand", "[Output]\n- SPX: LONG")
    assert split_reasoning("[Output] no thinking") == ("", "[Output] no thinking")


def test_freeze_tracks_adapter_files(tmp_path, monkeypatch):
    root = tmp_path / "adapters" / "qwen3-8b"
    for s in SCHOOLS:
        make_adapter(root / s)
    monkeypatch.setattr(locks, "paths", lambda: {"events_dir": tmp_path / "events", "adapters_dir": root})
    files = {str(f) for f in locks.tracked_files("exp01")}
    for s in SCHOOLS:
        assert str(root / s / "adapter_config.json") in files
        assert str(root / s / "adapter_model.safetensors") in files
