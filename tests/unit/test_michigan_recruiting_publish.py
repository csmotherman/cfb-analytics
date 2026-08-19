import json
from pathlib import Path

from cfb_analytics.pipelines.publish_michigan_recruiting import (
    LINEUP_DEFINITION_VERSION,
    projected_lineup,
    prospect_grade,
    publish,
    publish_national,
    publish_projected_lineup_from_artifacts,
)
from cfb_analytics.sources.cfbd.client import CfbdResponse


def _response(url: str, payload: list[dict]) -> CfbdResponse:
    return CfbdResponse(url=url, status_code=200, payload=payload, raw_bytes=b"[]", headers={})


class FakeClient:
    def recruiting_players(self, season: int, team: str | None = None) -> CfbdResponse:
        row = {"id": str(season), "year": season, "name": "Test Recruit", "rating": .995, "stars": 5, "ranking": 1}
        return _response(f"https://example.test/recruits/{season}", [row])

    def recruiting_team(self, season: int, team: str | None = None) -> CfbdResponse:
        return _response("https://example.test/rank", [{"year": season, "team": team, "rank": 1, "points": 300}])


def test_prospect_grade_boundaries() -> None:
    assert prospect_grade(.995) == "S+"
    assert prospect_grade(.98) == "S"
    assert prospect_grade(.95) == "A"
    assert prospect_grade(.90) == "B"
    assert prospect_grade(.85) == "C"
    assert prospect_grade(.80) == "D"
    assert prospect_grade(.79) == "F"
    assert prospect_grade(None) is None


def test_publish_recruiting_and_roster_grades(tmp_path: Path) -> None:
    target = tmp_path / "2026" / "michigan"
    target.mkdir(parents=True)
    (target / "roster.json").write_text(json.dumps([{"id": "9", "firstName": "Current", "lastName": "Player", "recruitIds": ["2025"], "position": "QB"}]))

    manifest = publish(FakeClient(), tmp_path)

    recruiting = json.loads((target / "recruiting.json").read_text())
    grades = json.loads((target / "player-grades.json").read_text())
    lineup = json.loads((target / "projected-lineup.json").read_text())
    assert manifest["recruitRows"] == 1
    assert manifest["gradedPlayers"] == 1
    assert recruiting["recruits"][0]["grade"] == "S+"
    assert grades[0]["grade"] == "S+"
    assert grades[0]["basis"] == "CFBD recruiting composite"
    assert manifest["version"] == "michigan-recruiting-v2"
    assert manifest["lineupDefinitionVersion"] == LINEUP_DEFINITION_VERSION
    assert lineup["version"] == LINEUP_DEFINITION_VERSION
    assert lineup["valueType"] == "PROJECTED"
    assert lineup["offense"] == [{"label": "QB", "playerId": "9"}]


def test_projected_lineup_uses_published_grade_then_experience() -> None:
    roster = [
        {"id": "veteran", "position": "QB", "year": 4, "jersey": 9, "lastName": "Veteran"},
        {"id": "elite", "position": "QB", "year": 1, "jersey": 12, "lastName": "Elite"},
        {"id": "older", "position": "RB", "year": 3, "jersey": 22, "lastName": "Older"},
        {"id": "younger", "position": "RB", "year": 1, "jersey": 2, "lastName": "Younger"},
    ]
    grades = [
        {"playerId": "veteran", "grade": "B"},
        {"playerId": "elite", "grade": "A"},
        {"playerId": "older", "grade": "C"},
        {"playerId": "younger", "grade": "C"},
    ]

    lineup = projected_lineup(roster, grades, season=2026, team="Michigan")

    assert lineup["offense"][:2] == [
        {"label": "QB", "playerId": "elite"},
        {"label": "RB", "playerId": "older"},
    ]


def test_lineup_only_republishes_existing_artifacts(tmp_path: Path) -> None:
    target = tmp_path / "2026" / "michigan"
    target.mkdir(parents=True)
    (target / "roster.json").write_text(json.dumps([{"id": "qb", "position": "QB", "year": 2, "jersey": 7}]))
    (target / "player-grades.json").write_text(json.dumps([{"playerId": "qb", "grade": "A"}]))
    (target / "recruiting-manifest.json").write_text(json.dumps({"version": "michigan-recruiting-v1", "artifacts": {}}))

    artifact = publish_projected_lineup_from_artifacts(tmp_path)

    assert artifact["offense"] == [{"label": "QB", "playerId": "qb"}]
    assert json.loads((target / "projected-lineup.json").read_text()) == artifact
    manifest = json.loads((target / "recruiting-manifest.json").read_text())
    assert manifest["version"] == "michigan-recruiting-v2"
    assert manifest["lineupDefinitionVersion"] == LINEUP_DEFINITION_VERSION
    assert "projected-lineup.json" in manifest["artifacts"]


def test_publish_complete_national_class(tmp_path: Path) -> None:
    manifest = publish_national(FakeClient(), tmp_path)
    target = tmp_path / "2026" / "recruiting"
    players = json.loads((target / "players.json").read_text())
    teams = json.loads((target / "teams.json").read_text())
    assert manifest["playerRows"] == 1
    assert manifest["teamRows"] == 1
    assert players[0]["grade"] == "S+"
    assert players[0]["valueType"] == "BENCHMARK"
    assert teams[0]["rank"] == 1
