# Task A — agent spike (Qwen3-8B as a prompted framework agent, real L1/L2 tools)

Run 2026-11-01 on one A40 (46 GB), vLLM, `python -m mosaic agent-spike --n 10` (30 conversations: 10 template events
per school, item seed 7) with and without `--thinking`. Outputs: `runs/agent-spike/{non-thinking,thinking}/`
(not versioned). No prompt was tuned; this is the starting point of the A-agent.

| | non-thinking | thinking |
|---|---|---|
| conversations | 30 | 30 |
| passing all checks | 0 / 30 | 0 / 30 |
| protocol (episode tool → macro tool → answer, one call per message) | 0 / 30 | 0 / 30 |
| proof block valid | 0 / 30 | 5 / 30 (16.7 %) |
| text filters | 0 / 30 | 5 / 30 (16.7 %) |
| malformed tool calls (unparsable) | 0 | 0 |
| seconds (whole run) | 530 | 557 |

Problems counted (summed over conversations; each conversation can have several):

| problem | non-thinking | thinking |
|---|---|---|
| signal missing or malformed (6 assets per conversation) | 180 (all 30) | 150 (25) |
| protocol / message does not start with [Think] | 30 | 52 messages (25 conversations) |
| 0 scenario probabilities found | 30 | 25 |
| proof has no L1 / L2 / L3 / L5 step | 30 / 28 / 30 / 30 | 23 / 21 / 25 / 25 |
| 0 proof steps (4–7 required) | 28 | 21 |
| two tool calls in one message (turn order wrong) | 0 | 5 conversations |
| fewer than 2 dated analog episodes | 1 | 0 |

Reading: the model calls both tools with valid JSON in almost every conversation (0 malformed calls), so the tool
interface works. It fails the *format* contract: the final answer lacks the leading [Think], the signals are not
written in the required form, and the proof lines do not use `- Lk [ref]: claim` with a returned ref. Thinking mode
does not help the format (it helps the proof slightly, 5/30 vs 0/30, and puts both calls into one message in 5/30).
The per-problem counts come from `summary.json`; tool-error counts (e.g. unknown indicator names) are not a
separate field of the summary, so they are not reported here (see example 1).

deviation: the teacher pilot (qwen3.8-max, v4 smoke test: 1 conversation, passed every check after normalisation
fixes) is far above this; a prompted 8B agent with this contract is at 0 % without normalisation or training. The
gap is what agent SFT / rejection sampling must close; the spike gives no sign of a harness bug (tools execute, the
turns are recorded, failures are format failures visible in the transcripts).

## Examples (from `conversations.jsonl`)

1. **Joined indicator list → tool error, answer without [Think]** (non-thinking, `agent|keynesian|syn-k0000`).
   Second call: `get_macro_data({"indicators": ["US policy rate (%), US 2y yield (%), ... WTI oil ($/bbl)"]})`, one
   string with all 13 names; the tool answers "none of the requested names is available". The model then writes
   `[Output]` without a [Think], signals as `- Stocks: NEUTRAL (conviction: moderate)` (not the required form, and
   "Stocks"/"Real Estate" instead of the six named assets), and a proof with `- L1: US core PCE y/y (%): …` (no
   `[ref]`, no returned value), an `L4` line and no L5 bracket.
2. **Two tool calls in one message** (thinking, `agent|keynesian|syn-k0001`). Turn 1 is empty text plus
   `query_episode_db` and `get_macro_data` together; protocol check: `turns ['assistant','tool','tool','assistant']`.
   The answer starts at `[Output]`, uses the signal form `**Equities (LONG)**: …`, and the proof chains
   `L1 … → L2 … → Keynesian mechanism` on one line (also cites "L2 inverted yield curve", not a returned episode id).
3. **Ungrounded proof / no proof** (both modes, e.g. `agent|*|syn-*` with 0 proof steps in 28 and 21
   conversations): see `conversations.jsonl` rows with the problem "0 proof steps (4-7 required)".

## Worries for the human

- The checker is strict on exact line forms; some of the 180 "signal malformed" may be accepted by a laxer reader.
  I did not loosen it (the filters are the teacher's contract). A normaliser as for the teacher (`normalize()`) is the
  cheap first step before rejection-sampling fine-tuning; the human decides.
- Rule 3 of Task A: no prompt tuning here. Candidate changes for a later spike (not done): show one worked format
  example in the system note; state the signal line form literally; forbid parallel calls in the tool schema.
