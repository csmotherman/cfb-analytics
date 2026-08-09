import json
from pathlib import Path

from cfb_analytics.raw.census import raw_census
from cfb_analytics.raw.storage import store_response
from cfb_analytics.sources.cfbd.client import CfbdResponse


def _response(payload):
    raw = json.dumps(payload, separators=(",", ":")).encode()
    return CfbdResponse("https://example.test", 200, payload, raw, {})


def test_census_profiles_source_categories(tmp_path: Path):
    games = [{"id": 1, "season": 2025, "week": 1, "seasonType": "regular", "homeClassification": "fbs", "awayClassification": "fbs"}]
    drives = [{"id": 10, "gameId": 1, "driveResult": "PUNT", "plays": 3, "yards": 12}]
    plays = [
        {"id": 100, "gameId": 1, "driveId": 10, "playType": "Rush", "down": 1, "distance": 10, "yardsGained": 5},
        {"id": 101, "gameId": 1, "driveId": 10, "playType": "Pass Reception", "down": 2, "distance": 5, "yardsGained": 7},
    ]
    for entity, payload in (("games", games), ("drives", drives), ("plays", plays)):
        store_response(tmp_path, season=2025, season_type="regular", week=1, entity=entity, response=_response(payload))

    result = raw_census(tmp_path, seasons=(2025,))
    assert result["totals"] == {"games": 1, "drives": 1, "plays": 2}
    assert result["play_types"] == {"Rush": 1, "Pass Reception": 1}
    assert result["drive_results"] == {"PUNT": 1}
    assert result["observed_ranges"]["plays.down"] == {"min": 1, "max": 2}
