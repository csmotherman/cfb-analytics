import json
from pathlib import Path

from cfb_analytics.pipelines.publish_longitudinal_directory import publish as publish_history
from cfb_analytics.pipelines.publish_national_directory import publish, slugify
from cfb_analytics.sources.cfbd.client import CfbdResponse


def response(name: str, payload: list[dict]) -> CfbdResponse:
    return CfbdResponse(url=f"https://example.test/{name}",status_code=200,payload=payload,raw_bytes=b"[]",headers={})


class DirectoryClient:
    def fbs_teams(self, season: int): return response("teams",[{"id":130,"school":"Michigan","conference":"Big Ten"}])
    def national_roster(self, season: int): return response("roster",[{"id":"1","firstName":"Test","lastName":"Player","team":"Michigan","position":"OT","recruitIds":["9"]}])
    def get_json(self, path: str, params: dict): return response("games",[{"id":2,"homeTeam":"Michigan","awayTeam":"Ohio State","completed":False,"startDate":"2099-01-01"}])
    def transfer_portal(self, season: int): return response("portal",[{"origin":"Michigan","destination":"Ohio State"}])
    def coaches(self, season: int): return response("coaches",[{"id":3,"seasons":[{"year":season,"school":"Michigan"}]}])
    def recruiting_players(self, season: int): return response("recruits",[{"id":"9","name":"Test Player","committedTo":"Michigan","rating":.95,"ranking":100}])
    def recruiting_team(self, season: int): return response("recruiting-teams",[{"year":season,"team":"Michigan","rank":1}])


def test_slugify_is_stable() -> None:
    assert slugify("Texas A&M") == "texas-a-m"
    assert slugify("  UL Monroe  ") == "ul-monroe"


def test_national_directory_writes_joined_team_bundle(tmp_path: Path) -> None:
    result=publish(DirectoryClient(),tmp_path/"raw",tmp_path/"published",2026)
    bundle=json.loads((tmp_path/"published"/"2026"/"directory"/"teams"/"michigan.json").read_text())
    assert result["audit"]["status"] == "PASS"
    assert bundle["roster"][0]["teamId"] == 130
    assert bundle["roster"][0]["positionGroup"] == "OL"
    assert bundle["roster"][0]["recruiting"]["grade"] == "A"


class HistoryClient:
    def recruiting_players(self, season: int): return response("recruits",[{"id":"9","year":season,"name":"Test","committedTo":"Michigan","rating":.95}])
    def recruiting_team(self, season: int): return response("teams",[{"year":season,"team":"Michigan","rank":1}])
    def national_roster(self, season: int): return response("roster",[{"id":"1","firstName":"Test","team":"Michigan","position":"OT","recruitIds":["9"]},{"id":"1","firstName":"Test","team":"Ohio State","position":"OT","recruitIds":["9"]}])
    def transfer_portal(self, season: int): return response("portal",[])


def test_history_preserves_same_season_multi_team_appearances(tmp_path: Path) -> None:
    audit=publish_history(HistoryClient(),tmp_path/"raw",tmp_path/"published",recruiting_start=2026,roster_start=2026,end=2026)
    conflicts=json.loads((tmp_path/"published"/"directory_history"/"players"/"same-season-multi-team.json").read_text())
    assert audit["status"] == "PASS"
    assert audit["counts"]["sameSeasonMultiTeamPlayers"] == 1
    assert conflicts == [{"playerId":"1","season":2026,"teams":["Michigan","Ohio State"]}]
