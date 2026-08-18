import json
from pathlib import Path

from cfb_analytics.ingestion.facts import acquire_fact_week
from cfb_analytics.ingestion.audit import audit_fact_season
from cfb_analytics.ingestion.storage import fact_partition_dir, store_fact_response, verify_fact_manifest
from cfb_analytics.raw.storage import store_response
from cfb_analytics.sources.cfbd.client import CfbdResponse


class FakeClient:
    calls = 0

    @staticmethod
    def _response(entity, payload):
        FakeClient.calls += 1
        raw = json.dumps(payload, separators=(",", ":")).encode()
        return CfbdResponse(f"https://example.test/{entity}", 200, payload, raw, {})

    def games(self, season, week, season_type):
        return self._response("games", [
            {"id": 1, "season": season, "week": week, "seasonType": season_type, "homeClassification": "fbs", "awayClassification": "fcs"},
            {"id": 2, "season": season, "week": week, "seasonType": season_type, "homeClassification": "fbs", "awayClassification": "fbs"},
            {"id": 3, "season": season, "week": week, "seasonType": season_type, "homeClassification": "fcs", "awayClassification": "fcs"},
        ])

    def drives(self, season, week, season_type):
        return self._response("drives", [{"id": 10, "gameId": 1}, {"id": 20, "gameId": 2}, {"id": 30, "gameId": 3}])

    def plays(self, season, week, season_type):
        return self._response("plays", [{"id": 100, "gameId": 1}, {"id": 200, "gameId": 2}, {"id": 300, "gameId": 3}])


def test_fact_ingestion_is_isolated_filtered_and_idempotent(tmp_path: Path):
    FakeClient.calls = 0
    first = acquire_fact_week(FakeClient(), tmp_path, 2025, "regular", 1)
    directory = fact_partition_dir(tmp_path, 2025, "regular", 1)
    assert first["fbs_vs_non_fbs_games"] == 1
    assert first["fbs_vs_fbs_games"] == 1
    assert {row["id"] for row in json.loads((directory / "games.json").read_text())} == {1, 2}
    assert all(verify_fact_manifest(directory, entity) for entity in ("games", "drives", "plays"))
    assert not (tmp_path / "cfbd").exists()
    assert FakeClient.calls == 3
    second = acquire_fact_week(FakeClient(), tmp_path, 2025, "regular", 1)
    assert second["status"] == "REUSED"
    assert FakeClient.calls == 3


def test_season_audit_proves_legacy_containment_and_membership(tmp_path: Path):
    broad_games = [
        {"id": 1, "season": 2025, "week": 1, "seasonType": "regular", "homeId": 10, "homeTeam": "A", "homeClassification": "fbs", "homeConference": "X", "awayId": 11, "awayTeam": "FCS", "awayClassification": "fcs", "awayConference": "FCS"},
        {"id": 2, "season": 2025, "week": 1, "seasonType": "regular", "homeId": 10, "homeTeam": "A", "homeClassification": "fbs", "homeConference": "X", "awayId": 20, "awayTeam": "B", "awayClassification": "fbs", "awayConference": "Y"},
    ]
    entity_rows = {"games": broad_games, "drives": [{"id": 1, "gameId": 1}, {"id": 2, "gameId": 2}], "plays": [{"id": 1, "gameId": 1}, {"id": 2, "gameId": 2}]}
    for entity, rows in entity_rows.items():
        store_fact_response(tmp_path, season=2025, season_type="regular", week=1, entity=entity, response=FakeClient._response(entity, rows))
    legacy = tmp_path / "legacy"
    for entity, rows in {**entity_rows, "games": [broad_games[1]], "drives": [entity_rows["drives"][1]], "plays": [entity_rows["plays"][1]]}.items():
        store_response(legacy, season=2025, season_type="regular", week=1, entity=entity, response=FakeClient._response(entity, rows))
    audit = audit_fact_season(tmp_path, legacy, 2025)
    assert audit["status"] == "PASS"
    assert audit["legacy_comparison"]["additional_games"] == 1
    assert audit["fbs_teams"] == 2
    assert {row["team"] for row in audit["membership"]} == {"A", "B"}
