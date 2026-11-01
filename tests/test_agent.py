"""The agent loop: tool calls parsed from Qwen-format replies, executed, fed back; scored with the v4 checks."""

import json
import re

from mosaic.agent import run_agents, score, spike_jobs
from mosaic.backends import Backend


class ScriptedQwen(Backend):
    """Plays a compliant agent: query_episode_db, then get_macro_data, then an answer citing what came back."""

    model_id = "scripted"

    def _generate(self, reqs):
        out = []
        for r in reqs:
            assert r.tools and r.tools[0]["function"]["name"] == "query_episode_db"
            tools = [m["content"] for m in r.messages if m["role"] == "tool"]
            if not tools:
                text = ('[Think]\nBad news for growth.\n<tool_call>\n{"name": "query_episode_db", "arguments": '
                        '{"query": "demand shock recession easing"}}\n</tool_call>')
            elif len(tools) == 1:
                text = ('[Think]\nThe 2001 episode fits.\n<tool_call>\n{"name": "get_macro_data", "arguments": '
                        '{"indicators": ["US unemployment rate (%)", "US CPI inflation y/y (%)"]}}\n</tool_call>')
            else:
                from tests.test_teacher_v4 import FINAL

                ep = re.findall(r"\[(EP-[^\]]+)\]", tools[0])[0]
                name = next(s for s in ("Keynesian", "Austrian", "Monetarist") if s.lower() in r.messages[0]["content"].lower())
                text = FINAL.format(ep=ep, ind="US unemployment rate (%)", school=name)
            out.append({"text": text, "usage": {}, "seconds": 0.0})
        return out


def test_agent_loop_runs_tools_and_passes_the_v4_checks():
    pairs = spike_jobs(1, seed=7)
    jobs = run_agents(ScriptedQwen({}), [j for _, j in pairs])
    assert all([t["role"] for t in j.turns] == ["assistant", "tool", "assistant", "tool", "assistant"] for j in jobs)
    assert "L2 episodes" in jobs[0].turns[1]["content"] and "L1 indicators" in jobs[0].turns[3]["content"]
    assert json.loads(jobs[0].turns[2]["tool_calls"][0]["function"]["arguments"])["indicators"]
    s = score(pairs)
    assert s["n"] == 3 and s["all_checks"] == 1.0 and s["malformed_tool_calls"] == 0, s


def test_agent_without_tool_calls_stops_and_fails_the_protocol():
    class Silent(Backend):
        model_id = "silent"

        def _generate(self, reqs):
            return [{"text": "[Think]\nNo tools.\n<tool_call>{bad json}</tool_call>", "usage": {}} for _ in reqs]

    pairs = spike_jobs(1, seed=7)
    jobs = run_agents(Silent({}), [j for _, j in pairs])
    assert all(len(j.turns) == 1 and j.done and j.malformed == 1 for j in jobs)
    s = score(pairs)
    assert s["protocol"] == 0.0 and s["malformed_tool_calls"] == 3


def test_spike_prompts_drop_the_placeholder_line_and_the_backdrop():
    item, job = spike_jobs(1, seed=7)[0]
    assert "<<PLACEHOLDER" not in job.messages[0]["content"]
    assert "Macro context" not in job.messages[1]["content"] and item.event.text in job.messages[1]["content"]
