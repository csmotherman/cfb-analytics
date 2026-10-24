"""The weekly refresh must not freeze an upcoming week in a verified raw cache."""
import json

from cfb_analytics.raw.acquire import acquire_season, cached_partition_has_unfinished_games
from cfb_analytics.raw.storage import partition_dir, verify_manifest
from cfb_analytics.sources.cfbd.client import CfbdResponse


def _response(entity, payload):
    raw = json.dumps(payload).encode("utf-8")
    return CfbdResponse(
        url=f"https://api.collegefootballdata.com/{entity}",
        status_code=200,
        payload=payload,
        raw_bytes=raw,
        headers={},
    )


class FakeCfbdClient:
    def __init__(self):
        self.final = False
        self.calls = []

    def calendar(self, season):
        assert season == 2026
        self.calls.append("calendar")
        return _response("calendar", [{"week": 8, "seasonType": "regular"}])

    def games(self, season, week, season_type):
        assert (season, week, season_type) == (2026, 8, "regular")
        self.calls.append("games")
        return _response("games", [{
            "id": 42, "completed": self.final,
            "homeClassification": "fbs", "awayClassification": "fbs",
            "homeTeam": "Michigan", "awayTeam": "Indiana",
        }])

    def drives(self, season, week, season_type):
        self.calls.append("drives")
        return _response("drives", [{"gameId": 42, "id": "drive-1"}] if self.final else [])

    def plays(self, season, week, season_type):
        self.calls.append("plays")
        return _response("plays", [{"gameId": 42, "id": "play-1"}] if self.final else [])


def test_refresh_replaces_pre_final_games_drives_and_plays(tmp_path):
    cfbd = FakeCfbdClient()
    folder = partition_dir(tmp_path, 2026, "regular", 8)

    acquire_season(cfbd, tmp_path, 2026)
    assert cfbd.calls == ["calendar", "games", "drives", "plays"]
    assert cached_partition_has_unfinished_games(tmp_path, 2026, "regular", 8)
    assert json.loads((folder / "drives.json").read_text()) == []

    cfbd.final = True
    cfbd.calls.clear()
    acquire_season(cfbd, tmp_path, 2026)
    assert cfbd.calls == ["calendar", "games", "drives", "plays"]
    assert json.loads((folder / "games.json").read_text())[0]["completed"] is True
    assert len(json.loads((folder / "drives.json").read_text())) == 1
    assert len(json.loads((folder / "plays.json").read_text())) == 1
    assert all(verify_manifest(folder, part) for part in ("games", "drives", "plays"))
    assert not cached_partition_has_unfinished_games(tmp_path, 2026, "regular", 8)

    # Final, manifest-verified weeks can reuse all three cached parts.
    cfbd.calls.clear()
    acquire_season(cfbd, tmp_path, 2026)
    assert cfbd.calls == ["calendar"]


def test_empty_cached_week_remains_open(tmp_path):
    folder = partition_dir(tmp_path, 2026, "regular", 8)
    from cfb_analytics.raw.storage import store_response
    store_response(
        tmp_path, season=2026, season_type="regular", week=8,
        entity="games", response=_response("games", []),
    )
    assert folder.exists()
    assert cached_partition_has_unfinished_games(tmp_path, 2026, "regular", 8)
