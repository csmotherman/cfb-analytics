import json
from pathlib import Path

import pytest

from cfb_analytics.pipelines.publish_michigan_preseason import publish
from cfb_analytics.sources.cfbd.client import CfbdResponse


def _response(url: str, payload: list[dict]) -> CfbdResponse:
    return CfbdResponse(url=url, status_code=200, payload=payload, raw_bytes=b"[]", headers={})


class FakeClient:
    def __init__(self, games: list[dict]) -> None:
        self._games = games

    def roster(self, season: int, team: str) -> CfbdResponse:
        assert (season, team) == (2026, "Michigan")
        return _response("https://example.test/roster", [{"id": "1", "firstName": "Test"}])

    def team_games(self, season: int, team: str) -> CfbdResponse:
        assert (season, team) == (2026, "Michigan")
        return _response("https://example.test/games", self._games)


def test_publish_labels_source_only_preseason_contracts(tmp_path: Path) -> None:
    client = FakeClient([{"id": 10, "startDate": "2099-09-05T23:30:00Z", "completed": False}])

    manifest = publish(client, tmp_path, season=2026)

    target = tmp_path / "2026" / "michigan"
    roster = json.loads((target / "roster.json").read_text())
    schedule = json.loads((target / "schedule.json").read_text())
    saved_manifest = json.loads((target / "manifest.json").read_text())
    assert manifest["seasonState"] == "PRESEASON"
    assert saved_manifest["valueType"] == "PRESEASON"
    assert saved_manifest["rosterRows"] == 1
    assert saved_manifest["scheduleRows"] == 1
    assert roster[0]["teamId"] == 130
    assert roster[0]["valueType"] == "PRESEASON"
    assert schedule[0]["valueType"] == "PRESEASON"
    assert set(saved_manifest["artifacts"]) == {"roster.json", "schedule.json"}


def test_publish_refuses_started_or_completed_season(tmp_path: Path) -> None:
    client = FakeClient([{"id": 10, "completed": True, "homePoints": 31, "awayPoints": 7}])

    with pytest.raises(ValueError, match="refused season state COMPLETE"):
        publish(client, tmp_path, season=2026)

