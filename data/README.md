# Data contract (files here are not versioned)

| Path | Content | Used by |
|---|---|---|
| `data/events/test.jsonl` | the 96 held-out Confirmation events, one JSON per line: `{"id", "text", "difficulty", "category", "macro_context"?, "template_id"?}` | final test run only |
| `data/events/dev.jsonl` | 30–40 events disjoint from test, same fields. Recommended: historical episodes from the episode database (narrative as `text`, FRED snapshot as `macro_context`) | dev loop |
| `data/trajectories/<school>.jsonl` | the 500 SFT trajectories per school: `{"messages": [{"role","content"},…], "template_id"}` or `{"prompt","response","template_id"}` | arm B exemplars |
| `adapters/<school>/` | PEFT LoRA directories (`adapter_config.json`, `adapter_model.safetensors`) for keynesian, austrian, monetarist | arm C |
| `data/legacy/{base,sft}_<school>.jsonl` | optional: the Confirmation's saved generations, `{"text": …}` per line | Task 0 parity |

`mosaic doctor` checks all of this, including that dev and test share no ids or texts.
Upload from your machine with `runpodctl send <path>` / `runpodctl receive <code>`, or `scp` to the pod's SSH port.
