"""Teacher pipeline (Change 5): templates, items, filters and the data-contract records; offline."""

import json

from mosaic import teacher

GOOD = """[Think]
Bad news for growth and mildly good news for inflation: a demand shock worth about half a percent of GDP.
[ToolCall: query_episode_db]
{"query": "demand shock and policy response"}
[Observe]
1. United States, 2001: demand fell for two quarters after the investment bust.
2. Euro area, 2008: credit and spending contracted together.
[Think]
The output gap widens and the multiplier works in reverse.
[ToolCall: get_macro_data]
{"indicators": ["US unemployment rate (%)", "US CPI inflation y/y (%)"]}
[Observe]
US unemployment rate (%): 6.1; US CPI inflation y/y (%): 2.0
[Think]
Fiscal support is needed while the gap is negative.
[Output]
Causal chain: shock -> lower spending -> multiplier -> output gap -> lower rates
Scenarios:
S1 (soft landing; growth down, inflation down): 0.5
S2 (recession; growth down, inflation down): 0.3
S3 (stagflation; growth down, inflation up): 0.2
Signals:
equities: SHORT (conviction 3) - S2 recession risk cuts earnings
government bonds: LONG (conviction 4) - rates fall as the gap widens
US dollar: NEUTRAL (conviction 2) - no clear relative rate path
gold: LONG (conviction 2) - easing lowers real yields
oil: SHORT (conviction 2) - weaker demand for energy
credit: SHORT (conviction 3) - defaults rise in S2
"""


class Stub:
    """Returns GOOD for every request, except a leaking reply for the second one."""

    def generate(self, reqs):
        return [{"text": GOOD if i != 1 else GOOD.replace("2001", "June 2025")} for i, _ in enumerate(reqs)]


def test_templates_match_the_confirmation_design():
    cfg = teacher.load_templates()
    temps = teacher.template_list(cfg)
    assert len(temps) == 107 and len(cfg["category"]) == 14  # Confirmation Sec. 4.2.1
    assert len({t[0] for t in temps}) == 107
    assert set(cfg["school"]) == set(teacher.SCHOOLS)


def test_items_are_seeded_and_cover_all_templates_before_repeating():
    a = teacher.make_items(120, seed=3)
    b = teacher.make_items(10, seed=3)
    k = [it for it in a if it.school == "keynesian"]
    assert len(k) == 120 and len({it.template_id for it in k[:107]}) == 107
    assert [it.event.text for it in b if it.school == "keynesian"] == [it.event.text for it in k[:10]]
    assert "{" not in k[0].event.text and isinstance(k[0].event.macro_context, dict)


def test_validate_and_leakage_filter():
    assert teacher.validate(GOOD) == []
    assert any("missing" in p for p in teacher.validate(GOOD.replace("[ToolCall: get_macro_data]", "")))
    assert any("sum to" in p for p in teacher.validate(GOOD.replace("inflation up): 0.2", "inflation up): 0.4")))
    assert teacher.leaks("as in March 2025 and in 2019") == []
    assert teacher.leaks("since June 2025") and teacher.leaks("by 2026") and teacher.leaks("in 2025 overall")
    assert teacher.leaks("analog episodes before 2025, pre-2025 cycles, prior to 2025") == []  # the boundary itself
    assert teacher.leaks("before 2026") and teacher.leaks("after 2025")


def test_generate_writes_the_data_contract_with_inference_prompts(tmp_path):
    cfg = teacher.load_templates()
    items = teacher.make_items(2, cfg=cfg)
    counts = teacher.generate(Stub(), items, cfg, "stub-model", tmp_path)
    assert counts["rejected"] == 1 and sum(counts[s] for s in teacher.SCHOOLS) == 5
    rec = json.loads((tmp_path / "keynesian.jsonl").read_text().splitlines()[0])
    roles = [m["role"] for m in rec["messages"]]
    assert roles == ["system", "user", "assistant"] and rec["teacher"] == "stub-model"
    from mosaic.prompts import build_messages, read_prompt
    from mosaic.data import Event
    ev = Event(**{k: v for k, v in rec["event"].items()}, template_id=rec["template_id"])
    inference = build_messages("A", "keynesian", ev, system=read_prompt("keynesian.system.txt"),
                               user_template=read_prompt("user_template.txt"))
    assert rec["messages"][:2] == inference  # training prompt == arm A/C prompt at inference
    rej = json.loads((tmp_path / "rejects.jsonl").read_text().splitlines()[0])
    assert any("leakage" in p for p in rej["problems"])


def test_export_and_import_round_trip_for_a_hosted_api_run(tmp_path):
    jobs, out = tmp_path / "jobs", tmp_path / "out"
    assert teacher.export_jobs(3, 0, "qwen-test", jobs) == 9
    reqs = [json.loads(x) for x in (jobs / "requests.jsonl").read_text().splitlines()]
    assert reqs[0]["url"] == "/v1/chat/completions" and reqs[0]["body"]["model"] == "qwen-test"
    lines = [{"custom_id": r["custom_id"], "model": "qwen-test", "content": GOOD} for r in reqs[:-2]]
    lines.append({"custom_id": reqs[-2]["custom_id"],  # OpenAI Batch output shape, with a reasoning block
                  "response": {"body": {"model": "qwen-test", "choices": [{"message": {"content": "<think>x</think>"
                                                                                       + GOOD}}]}}})
    (jobs / "results.jsonl").write_text("".join(json.dumps(x) + "\n" for x in lines))
    counts = teacher.import_results(jobs, jobs / "results.jsonl", out)
    assert counts["missing"] == 1 and counts["rejected"] == 1 and sum(counts[s] for s in teacher.SCHOOLS) == 8
    assert json.loads((out / "austrian.jsonl").read_text().splitlines()[0])["teacher"] == "qwen-test"


def test_import_refuses_a_claude_teacher(tmp_path):
    import pytest

    jobs = tmp_path / "jobs"
    teacher.export_jobs(1, 0, "qwen-test", jobs)
    (jobs / "results.jsonl").write_text(json.dumps({"custom_id": "keynesian|syn-k0000", "model": "claude-x",
                                                    "content": GOOD}) + "\n")
    with pytest.raises(SystemExit, match="Claude"):
        teacher.import_results(jobs, jobs / "results.jsonl", tmp_path / "out")



def test_v2_rules_reject_the_problems_the_opus_review_found():
    v = teacher.validate
    assert any("JSON" in p for p in v(GOOD.replace('{"query": "demand shock and policy response"}', "query: demand")))
    assert any("dated analog" in p for p in v(GOOD.replace("United States, 2001", "Various episodes")))
    assert any("malformed: gold" in p for p in v(GOOD.replace("gold: LONG (conviction 2)", "gold: LONG")))
    assert any("without a reason: oil" in p for p in v(GOOD.replace(" - weaker demand for energy", "")))
    assert any("instructions" in p for p in v(GOOD.replace("Fiscal support", "As instructed, fiscal support")))
    cfg = teacher.load_templates()
    item = next(it for it in teacher.make_items(3, cfg=cfg) if it.school == "austrian")
    assert any("another school: keynesian" in p for p in v(GOOD.replace("multiplier", "Keynesian multiplier"), item))
    vals = teacher.early_values(item)[:2]
    early = GOOD.replace("half a percent of GDP.", f"half a percent of GDP; backdrop {vals[0]} and {vals[1]}.")
    assert any("before get_macro_data" in p for p in v(early, item)) and v(GOOD, item) == []


def test_backdrop_hangs_together():
    import random

    for i in range(200):
        m = teacher.macro_snapshot(random.Random(i))
        assert m["US 2y-10y spread (bp)"] == round((m["US 10y yield (%)"] - m["US 2y yield (%)"]) * 100)
        assert 3.3 <= m["US unemployment rate (%)"] <= 10 and 11 <= m["VIX"] <= 60
        assert all(k.startswith(("US ", "VIX", "DXY", "WTI")) for k in m)  # labelled as a US/global backdrop


def test_signal_report_warns_when_one_direction_dominates():
    rec = {"messages": [{"role": "assistant", "content": GOOD}]}
    rep = teacher.signal_report({"keynesian": [rec] * 10, "austrian": [], "monetarist": []})
    assert rep["shares"]["keynesian"]["equities"]["SHORT"] == 10
    assert "keynesian: equities SHORT in 10/10" in rep["warnings"]


def test_import_refuses_jobs_made_with_another_prompt_version(tmp_path):
    import pytest

    jobs = tmp_path / "jobs"
    teacher.export_jobs(1, 0, "qwen-test", jobs)
    man = json.loads((jobs / "manifest.json").read_text())
    assert man["prompt_version"] == teacher.PROMPT_VERSION
    (jobs / "manifest.json").write_text(json.dumps(dict(man, prompt_version=1)))
    (jobs / "results.jsonl").write_text("")
    with pytest.raises(SystemExit, match="prompt version"):
        teacher.import_results(jobs, jobs / "results.jsonl", tmp_path / "out")
