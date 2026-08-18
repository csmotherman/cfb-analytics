import json

import pytest

from cfb_analytics.canonical.membership import MembershipError, build_fbs_membership
from cfb_analytics.ingestion.games import classify_matchup, filter_fbs_team_games
from cfb_analytics.ingestion.validation import FactIntegrityError, compare_legacy_universe
from cfb_analytics.sources.cfbd.client import CfbdResponse


def response(payload):
    raw = json.dumps(payload, separators=(",", ":")).encode()
    return CfbdResponse("https://example.test", 200, payload, raw, {})


def game(game_id, home_class="fbs", away_class="fcs"):
    return {
        "id": game_id, "season": 2025, "week": 1, "seasonType": "regular",
        "homeId": 1, "homeTeam": "FBS A", "homeClassification": home_class, "homeConference": "League",
        "awayId": game_id + 10, "awayTeam": f"Away {game_id}", "awayClassification": away_class, "awayConference": "FCS" if away_class == "fcs" else "League",
    }


def test_source_universe_retains_fbs_vs_fcs_and_excludes_unrelated_games():
    filtered, ids = filter_fbs_team_games(response([game(1), game(2, "fbs", "fbs"), game(3, "fcs", "fcs")]))
    assert ids == {"1", "2"}
    assert [classify_matchup(row) for row in filtered.payload] == ["fbs_vs_non_fbs", "fbs_vs_fbs"]


def test_membership_contains_only_fbs_participants():
    rows = build_fbs_membership([game(1), game(2, "fbs", "fbs")], 2025)
    assert {row["team"] for row in rows} == {"FBS A", "Away 2"}
    assert all(row["classification"] == "fbs" for row in rows)


def test_membership_fails_on_in_season_conference_conflict():
    games = [game(1), game(2)]
    games[1]["homeConference"] = "Other"
    with pytest.raises(MembershipError, match="conflicting"):
        build_fbs_membership(games, 2025)


def test_broad_universe_must_contain_frozen_legacy_games():
    assert compare_legacy_universe([game(1)], [game(1), game(2)])["additional_games"] == 1
    with pytest.raises(FactIntegrityError, match="dropped"):
        compare_legacy_universe([game(1), game(2)], [game(1)])

