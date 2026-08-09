import json
from pathlib import Path

from cfb_analytics.raw.storage import partition_dir, store_response, verify_manifest
from cfb_analytics.sources.cfbd.client import CfbdResponse


def test_store_and_verify(tmp_path: Path):
    raw = b'[{"id":1,"name":"example"}]'
    response = CfbdResponse(
        url="https://api.collegefootballdata.com/plays?year=2025&week=1",
        status_code=200,
        payload=json.loads(raw),
        raw_bytes=raw,
        headers={},
    )
    manifest = store_response(
        tmp_path,
        season=2025,
        season_type="regular",
        week=1,
        entity="plays",
        response=response,
    )
    directory = partition_dir(tmp_path, 2025, "regular", 1)
    assert manifest["record_count"] == 1
    assert (directory / "plays.json").read_bytes() == raw
    assert verify_manifest(directory, "plays")
