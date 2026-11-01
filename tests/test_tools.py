import re

from mosaic.tools import TOOL_NAMES, EpisodeTable, MacroFacts, ToolBox, parse_tool_calls

BACKDROP = {"US policy rate (%)": 4.0, "US 2y yield (%)": 3.8, "US 10y yield (%)": 4.1, "US 2y-10y spread (bp)": 30,
            "US CPI inflation y/y (%)": 3.2, "VIX": 17}


def box(before: str = "") -> ToolBox:
    return ToolBox(MacroFacts(BACKDROP), EpisodeTable.load(), before=before)


def test_standin_table_is_dated_pre_2025_and_has_no_statistics():
    t = EpisodeTable.load()
    assert len(t.episodes) >= 60
    assert len({e.id for e in t.episodes}) == len(t.episodes)
    for e in t.episodes:
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", e.date) and e.date < "2025-01-01", e.id
        assert len(e.tags) >= 2 and e.name and e.what
        assert not re.search(r"[%$]|\bbp\b|\d+(?:\.\d+)? ?(?:percent|per cent|billion|trillion)", e.what), e.id


def test_episode_query_ranks_relevant_episodes_and_respects_the_date():
    r = box().execute("query_episode_db", {"query": "mid-sized bank run on uninsured deposits"})
    assert r.layer == "L2" and r.refs[0] == "EP-2023-03-10"
    assert r.text.splitlines()[0].startswith("L2 episodes") and "[EP-2023-03-10] 2023-03-10" in r.text
    early = box(before="2020-01-01").execute("query_episode_db", '{"query": "bank run uninsured deposits", "k": 5}')
    assert early.refs and all(ref < "EP-2020" for ref in early.refs)
    assert len(early.refs) <= 5


def test_episode_query_without_a_match_lists_the_tags():
    r = box().execute("query_episode_db", {"query": "zzz qqq"})
    assert r.refs == () and "no episode matched" in r.text


def test_macro_lookup_exact_substring_and_unknown_names():
    r = box().execute("get_macro_data", '{"indicators": ["US CPI inflation y/y (%)", "VIX", "policy rate", "10y", "GDP"]}')
    assert r.layer == "L1"
    assert r.refs == ("US CPI inflation y/y (%)", "VIX", "US policy rate (%)")
    assert "- US CPI inflation y/y (%): 3.2" in r.text and "- VIX: 17" in r.text
    assert "Unknown: 10y, GDP." in r.text and "Available: US policy rate (%)" in r.text  # "10y" is ambiguous


def test_toolbox_errors_are_results_not_exceptions():
    b = box()
    assert b.execute("get_macro_data", "{not json").layer == "error"
    assert b.execute("get_macro_data", {}).layer == "error"
    assert b.execute("query_episode_db", {"query": " "}).layer == "error"
    assert "unknown tool" in b.execute("get_news", {}).text
    assert b.execute("get_macro_data", {"indicators": "VIX"}).refs == ("VIX",)
    assert set(TOOL_NAMES) == {"get_macro_data", "query_episode_db"}


def test_parse_qwen_tool_calls():
    text = ('[Think]\nRates matter here.\n<tool_call>\n{"name": "get_macro_data", "arguments": {"indicators": ["VIX"]}}'
            '\n</tool_call>\n<tool_call>{"name": "query_episode_db", "arguments": {"query": "x"}}</tool_call>'
            '<tool_call>{broken}</tool_call>')
    content, calls = parse_tool_calls(text)
    assert content == "[Think]\nRates matter here."
    assert calls[0] == {"name": "get_macro_data", "arguments": {"indicators": ["VIX"]}}
    assert calls[1]["name"] == "query_episode_db" and "error" in calls[2]
    assert parse_tool_calls("no calls") == ("no calls", [])


def test_indicator_names_joined_in_one_string_are_split():
    r = box().execute("get_macro_data", {"indicators": ["US policy rate (%), VIX, US CPI inflation y/y (%)"]})
    assert r.refs == ("US policy rate (%)", "VIX", "US CPI inflation y/y (%)")
