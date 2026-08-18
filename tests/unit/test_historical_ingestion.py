from cfb_analytics.ingestion.season_progress import read_progress, write_progress
from cfb_analytics.pipelines.ingest_history import ingest_historical_seasons


def test_historical_ingestion_resumes_after_completed_season(tmp_path):
    raw = tmp_path / "raw"
    write_progress(raw / "cfbd_facts", 2010, "COMPLETE", partitions=15)
    calls = []

    def acquire(_client, _root, season, *, force=False):
        calls.append(season)
        return [{"season": season}]

    def audit(_root, _legacy, season):
        return {"status": "PASS", "season": season, "membership": [{"season": season, "team": "Michigan"}]}

    rows = ingest_historical_seasons(object(), raw, raw, tmp_path / "canonical", range(2010, 2012), acquire=acquire, audit=audit)
    assert calls == [2011]
    assert [row["action"] for row in rows] == ["SKIPPED", "INGESTED"]
    assert read_progress(raw / "cfbd_facts", 2011)["status"] == "COMPLETE"


def test_historical_ingestion_persists_failure_before_raising(tmp_path):
    raw = tmp_path / "raw"

    def fail(*_args, **_kwargs):
        raise RuntimeError("source unavailable")

    try:
        ingest_historical_seasons(object(), raw, raw, tmp_path / "canonical", range(2017, 2018), acquire=fail)
    except RuntimeError:
        pass
    else:
        raise AssertionError("failed season did not raise")
    assert read_progress(raw / "cfbd_facts", 2017)["status"] == "FAILED"
