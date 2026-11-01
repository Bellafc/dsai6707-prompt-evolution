"""Teacher prompt version 4: real tools through function calling, the [Proof] block and the two export formats."""

import importlib.util
import json
import re
from pathlib import Path

import pytest

from mosaic import teacher
from mosaic.tools import EpisodeTable

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("teacher_api", ROOT / "scripts/teacher_api.py")
api = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(api)

FINAL = """[Think]
The data confirm slack, so weaker spending feeds on itself before policy reacts.
[Output]
Causal chain: shock -> lower spending -> lower income -> wider slack -> lower rates
Scenarios:
S1 (slow growth; growth down, inflation down): 0.47
S2 (recession; growth down, inflation down): 0.33
S3 (quick rebound; growth up, inflation up): 0.20
Signals:
equities: SHORT (conviction 2) - S2 recession risk outweighs the S3 rebound
government bonds: LONG (3) - rates fall as slack widens in S1 and S2
US dollar: NEUTRAL (conviction 1) - no clear relative rate path across scenarios
gold: NEUTRAL (conviction 1) - real rates fall but stress stays low
oil: SHORT (conviction 2) - weaker demand for energy in S1 and S2
credit: SHORT (conviction 2) - defaults rise in S2
[Proof]
- L2 [{ep}]: a comparable shock deepened the slowdown before policy responded.
- L1 [{ind}]: the indicator shows how much slack there is.
- L3 [{school}]: the school's mechanism links lower spending to lower income.
- L5 [S1]: slow growth is the most likely outcome.
Confidence: moderate; weakest link: the analog only partly fits the event.
"""


def fake_send(final: str = FINAL, first_tool: str = "query_episode_db"):
    """A scripted teacher: [Think] + one tool call, [Think] + the other, then the final answer citing what came back."""
    state = {"n": 0}

    def send(body):
        state["n"] += 1
        msgs = body["messages"]
        assert body["tools"] and all(m["role"] != "tool" or m["content"] for m in msgs)
        msg = {"content": "[Think]\nBad news for growth and mildly good news for inflation."}
        if state["n"] == 1:
            args = {"query": "demand shock recession easing"} if first_tool == "query_episode_db" else \
                {"indicators": ["US unemployment rate (%)"]}
            msg["tool_calls"] = [{"id": "c1", "type": "function",
                                  "function": {"name": first_tool, "arguments": json.dumps(args)}}]
        elif state["n"] == 2:
            msg["content"] = "[Think]\nThe 2001 episode fits best; unemployment and inflation decide between readings."
            msg["tool_calls"] = [{"id": "c2", "type": "function", "function": {
                "name": "get_macro_data",
                "arguments": '{"indicators": ["US unemployment rate (%)", "US CPI inflation y/y (%)"]}'}}]
        else:
            tools = [m["content"] for m in msgs if m["role"] == "tool"]
            eps = re.findall(r"\[(EP-[^\]]+)\]", "\n".join(tools)) or ["EP-1994-02"]
            ep = eps[0]
            ind = re.search(r"^- (US unemployment rate \(%\)):", tools[-1], re.M).group(1)
            school = re.search(r"School: (\w+)\.", msgs[1]["content"]).group(1)
            msg["content"] = final.format(ep=ep, ind=ind, school=school)
        return {"model": "qwen-test", "usage": {"prompt_tokens": 100, "completion_tokens": 50},
                "choices": [{"message": msg}]}

    return send


def run_jobs(jobs: Path, send_factory=fake_send, n: int = 1) -> list[dict]:
    teacher.export_jobs(n, 0, "qwen-test", jobs)
    lines = []
    for raw in (jobs / "requests.jsonl").read_text().splitlines():
        job = json.loads(raw)
        turns, info = api.converse(job, send_factory())
        lines.append({"custom_id": job["custom_id"], "model": info["model"], "turns": turns, "usage": info})
    (jobs / "results.jsonl").write_text("".join(json.dumps(x) + "\n" for x in lines))
    return lines


def test_v4_requests_carry_tools_and_backdrop_but_no_values_in_the_prompt(tmp_path):
    teacher.export_jobs(2, 0, "qwen-test", tmp_path)
    req = json.loads((tmp_path / "requests.jsonl").read_text().splitlines()[0])
    assert req["protocol"] == 4 and req["body"]["tools"][0]["function"]["name"] == "query_episode_db"
    prompt = req["body"]["messages"][1]["content"]
    assert "US policy rate (%)" in prompt  # the names are given ...
    assert not any(f"{k}: {v}" in prompt for k, v in req["backdrop"].items())  # ... the values are not
    man = json.loads((tmp_path / "manifest.json").read_text())
    assert man["prompt_version"] == 4 and man["episodes"]["sha256"]


def test_converse_runs_the_tools_and_import_writes_both_formats(tmp_path):
    jobs, out = tmp_path / "jobs", tmp_path / "out"
    lines = run_jobs(jobs)
    assert [t["role"] for t in lines[0]["turns"]] == teacher.V4_TURNS
    assert lines[0]["usage"]["completion_tokens"] == 150  # summed over the three replies
    counts = teacher.import_results(jobs, jobs / "results.jsonl", out)
    assert counts["rejected"] == 0 and all(counts[s] == 1 for s in teacher.SCHOOLS), counts
    single = json.loads((out / "keynesian.jsonl").read_text())
    text = single["messages"][-1]["content"]
    assert single["format"] == "single" and "Macro context" in single["messages"][1]["content"]
    assert "[Proof]" not in text and "(conviction 3)" in text  # proof dropped, signals normalised
    order = [text.find(m) for m in ("[ToolCall: query_episode_db]", "[Observe]\nL2 episodes", "[ToolCall: get_macro_data]",
                                    "[Observe]\nL1 indicators", "[Output]")]
    assert -1 not in order and order == sorted(order)
    agent = json.loads((out / "agent" / "austrian.jsonl").read_text())
    roles = [m["role"] for m in agent["messages"]]
    assert agent["format"] == "agent" and roles == ["system", "user", *teacher.V4_TURNS]
    assert "get_macro_data returns indicator values" in agent["messages"][0]["content"]
    assert "Macro context" not in agent["messages"][1]["content"] and agent["tools"] == teacher.TOOL_SPECS
    assert "[Proof]" in agent["messages"][-1]["content"]
    assert agent["messages"][2]["tool_calls"][0]["function"]["arguments"].startswith('{"query"')


def test_v4_rejects_ungrounded_proofs_tampered_results_and_wrong_protocol(tmp_path):
    item = teacher.make_items(1)[0]
    episodes = EpisodeTable.load()
    job = {"body": {"model": "x", "messages": teacher.teacher_messages_v4(item, teacher.load_templates()),
                    "tools": teacher.TOOL_SPECS}, "backdrop": item.event.macro_context}
    good, _ = api.converse(job, fake_send())
    assert teacher.check_v4(item, good, episodes)[0] == []
    bad_proof, _ = api.converse(job, fake_send(FINAL.replace("- L2 [{ep}]", "- L2 [EP-1066-10]")))
    assert any("did not return" in p for p in teacher.check_v4(item, bad_proof, episodes)[0])
    no_proof, _ = api.converse(job, fake_send(FINAL.split("[Proof]")[0]))
    assert "missing [Proof] block" in teacher.check_v4(item, no_proof, episodes)[0]
    tampered = [dict(t) for t in good]
    tampered[3]["content"] = tampered[3]["content"].replace(": ", ": 9", 1)
    assert any("differs from a re-run" in p for p in teacher.check_v4(item, tampered, episodes)[0])
    swapped, _ = api.converse(job, fake_send(first_tool="get_macro_data"))
    assert any(p.startswith("protocol") for p in teacher.check_v4(item, swapped, episodes)[0])
    assert teacher.check_v4(item, good[:3], episodes)[0][0].startswith("protocol")


def test_import_refuses_an_episode_table_changed_since_the_run(tmp_path):
    jobs = tmp_path / "jobs"
    run_jobs(jobs)
    man = json.loads((jobs / "manifest.json").read_text())
    man["episodes"]["sha256"] = "0" * 64
    (jobs / "manifest.json").write_text(json.dumps(man))
    with pytest.raises(SystemExit, match="changed since"):
        teacher.import_results(jobs, jobs / "results.jsonl", tmp_path / "out")


def test_streamed_tool_call_fragments_are_merged():
    calls: dict = {}
    api.merge_tool_deltas(calls, [{"index": 0, "id": "c1", "function": {"name": "get_macro_data", "arguments": '{"ind'}}])
    api.merge_tool_deltas(calls, [{"index": 0, "function": {"arguments": 'icators": ["VIX"]}'}}])
    assert calls[0] == {"id": "c1", "type": "function",
                        "function": {"name": "get_macro_data", "arguments": '{"indicators": ["VIX"]}'}}


def test_flatten_keeps_the_confirmation_marker_order():
    turns = [{"role": "assistant", "content": "[Think]\na", "tool_calls": [
                 {"function": {"name": "query_episode_db", "arguments": '{"query":  "x"}'}}]},
             {"role": "tool", "content": "L2 episodes:\n- [EP-1] 1990-01-01, US: e. w."},
             {"role": "assistant", "content": "[Think]\nb", "tool_calls": [
                 {"function": {"name": "get_macro_data", "arguments": {"indicators": ["VIX"]}}}]},
             {"role": "tool", "content": "L1 indicators:\n- VIX: 20"},
             {"role": "assistant", "content": "[Think]\nc\n[Output]\nd\n[Proof]\n- L1 [VIX]: e"}]
    flat = teacher.flatten(turns)
    assert flat.startswith('[Think]\na\n[ToolCall: query_episode_db]\n{"query": "x"}\n[Observe]\nL2 episodes')
    assert flat.endswith("[Output]\nd") and "[Proof]" in teacher.flatten(turns, proof=True)


def test_scenario_placeholder_and_multi_ref_proof_steps():
    assert teacher.normalize("S1 (contain; growth down, inflation down): p 0.50\nS2 (x; growth up, inflation up): "
                             "probability = .5") == ("S1 (contain; growth down, inflation down): 0.50\n"
                                                     "S2 (x; growth up, inflation up): .5")
    item = teacher.make_items(1)[0]
    job = {"body": {"model": "x", "messages": teacher.teacher_messages_v4(item, teacher.load_templates()),
                    "tools": teacher.TOOL_SPECS}, "backdrop": item.event.macro_context}
    two = FINAL.replace("- L1 [{ind}]:", "- L1 [{ind}] with [US CPI inflation y/y (%)]:")
    turns, _ = api.converse(job, fake_send(two))
    assert teacher.check_v4(item, turns, EpisodeTable.load())[0] == []
    ungrounded = FINAL.replace("- L1 [{ind}]:", "- L1 [{ind}] and [VIX]:")  # VIX was not requested
    turns, _ = api.converse(job, fake_send(ungrounded))
    assert "proof cites an indicator the tool did not return: VIX" in teacher.check_v4(item, turns, EpisodeTable.load())[0]


def test_proof_refs_joined_in_one_bracket_are_split():
    item = teacher.make_items(1)[0]
    job = {"body": {"model": "x", "messages": teacher.teacher_messages_v4(item, teacher.load_templates()),
                    "tools": teacher.TOOL_SPECS}, "backdrop": item.event.macro_context}
    joined = FINAL.replace("- L1 [{ind}]:", "- L1 [{ind}, US CPI inflation y/y (%)]:")
    turns, _ = api.converse(job, fake_send(joined))
    assert teacher.check_v4(item, turns, EpisodeTable.load())[0] == []
    turns, _ = api.converse(job, fake_send(FINAL.replace("- L1 [{ind}]:", "- L1 [{ind}, VIX]:")))
    assert "proof cites an indicator the tool did not return: VIX" in teacher.check_v4(item, turns, EpisodeTable.load())[0]


def test_proof_ref_variants_and_scenario_layout_seen_in_pilot_v4():
    assert teacher.normalize("S1 (contained recap): growth down, inflation flat: 0.38") == \
        "S1 (contained recap; growth down, inflation flat): 0.38"
    item = teacher.make_items(1)[0]
    job = {"body": {"model": "x", "messages": teacher.teacher_messages_v4(item, teacher.load_templates()),
                    "tools": teacher.TOOL_SPECS}, "backdrop": item.event.macro_context}
    variants = ["- L1 [{ind} 5.1 vs US CPI inflation y/y (%) 3.2]:", "- L1 [{ind} / US CPI inflation y/y (%)]:",
                "- L1 {ind}:"]
    for v in variants:
        turns, _ = api.converse(job, fake_send(FINAL.replace("- L1 [{ind}]:", v)))
        assert teacher.check_v4(item, turns, EpisodeTable.load())[0] == [], v
    turns, _ = api.converse(job, fake_send(FINAL.replace("- L1 [{ind}]:", "- L1 [US 2s10s spread (bp)]:")))
    assert any("2s10s" in p for p in teacher.check_v4(item, turns, EpisodeTable.load())[0])
