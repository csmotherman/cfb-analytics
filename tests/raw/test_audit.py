import json
from pathlib import Path

from cfb_analytics.raw.audit import audit_partition
from cfb_analytics.raw.storage import store_response
from cfb_analytics.sources.cfbd.client import CfbdResponse


def _response(payload):
    raw = json.dumps(payload, separators=(",", ":")).encode()
    return CfbdResponse("https://example.test", 200, payload, raw, {})


def test_audit_valid_partition(tmp_path: Path):
    games = [{"id": 1, "homeClassification": "fbs", "awayClassification": "fbs"}]
    drives = [{"id": 10, "gameId": 1}]
    plays = [{"id": 100, "gameId": 1, "driveId": 10}]
    for entity, payload in (("games", games), ("drives", drives), ("plays", plays)):
        store_response(tmp_path, season=2025, season_type="regular", week=1, entity=entity, response=_response(payload))
    result = audit_partition(tmp_path, 2025, "regular", 1)
    assert result["status"] == "PASS"
    assert result["checks"]["fbs_vs_fbs_only"]
    assert result["coverage"]["games_without_plays"] == 0
    assert result["orphans"]["play_drive_ids_missing_from_drives"] == []
