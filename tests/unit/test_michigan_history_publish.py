from pathlib import Path

from cfb_analytics.pipelines.publish_michigan_history import publish
from cfb_analytics.sources.cfbd.client import CfbdResponse


def response(payload: list[dict]) -> CfbdResponse:
    return CfbdResponse(url="https://example.test", status_code=200, payload=payload, raw_bytes=b"", headers={})


class FakeClient:
    def roster(self, season: int, team: str) -> CfbdResponse:
        return response([{"id": "1", "firstName": "Test", "lastName": "Player", "team": team}])

    def get_json(self, path: str, params: dict) -> CfbdResponse:
        return response([{"season": params["year"], "team": params["team"], "statName": "totalYards", "statValue": 4000}])

    def team_games(self, season: int, team: str) -> CfbdResponse:
        return response([{"id": 1, "season": season, "week": 1, "homeTeam": team, "awayTeam": "Opponent", "completed": True}])


def test_publish_writes_each_historical_surface(tmp_path: Path) -> None:
    result = publish(FakeClient(), tmp_path / "raw", tmp_path / "published", start=2010, end=2010)
    root = tmp_path / "published" / "michigan_history" / "2010"
    assert result["rosterCounts"] == {"2010": 1}
    assert (root / "roster.json").is_file()
    assert (root / "stats.json").is_file()
    assert (root / "games.json").is_file()
    assert (tmp_path / "raw" / "season=2010" / "michigan_roster.json").is_file()
