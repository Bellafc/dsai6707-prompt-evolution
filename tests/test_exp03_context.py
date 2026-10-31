from mosaic import exp03_context as c

CSV = ("observation_date,UNRATE_20250904,UNRATE_20250910\n"
       "2025-06-01,4.1,4.1\n2025-07-01,4.2,4.2\n2025-08-01,,4.3\n2025-09-01,,.\n")


def test_parse_vintages_drops_missing():
    v = c.parse_vintages(CSV, "UNRATE")
    assert v["2025-09-04"] == [("2025-06-01", 4.1), ("2025-07-01", 4.2)]
    assert v["2025-09-10"][-1] == ("2025-08-01", 4.3)


def test_fetch_asof_uses_latest_vintage_not_after_t(tmp_path):
    calls = []

    def get(url):
        calls.append(url)
        return CSV

    out = c.fetch_asof("UNRATE", ["2025-09-04", "2025-09-12", "2025-08-01"], cache=tmp_path, get=get, pause=0)
    assert out["2025-09-04"]["obs"][-1] == ("2025-07-01", 4.2)  # August not yet published on the 4th
    assert out["2025-09-12"]["vintage"] == "2025-09-10" and out["2025-09-12"]["obs"][-1][1] == 4.3
    assert out["2025-08-01"] == {"vintage": None, "obs": []}  # before the first vintage in the response
    c.fetch_asof("UNRATE", ["2025-09-04", "2025-09-12", "2025-08-01"], cache=tmp_path, get=get, pause=0)
    assert len(calls) == 1  # second call served from the cache


def test_indicator_panel_has_35_unique_ids():
    ids = [i["id"] for i in c.load_indicators()]
    assert len(ids) == 35 and len(set(ids)) == 35
