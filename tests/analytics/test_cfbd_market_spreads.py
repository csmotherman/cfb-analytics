import math

import pytest

from cfb_analytics.analytics.cfbd_market_spreads import (
    parse_spread_text,
    select_first_market_spread,
)


def _game(lines):
    return {
        "id": 123,
        "season": 2025,
        "seasonType": "postseason",
        "week": 1,
        "homeTeam": "Ohio",
        "awayTeam": "UNLV",
        "lines": lines,
    }


def test_parse_spread_home_favorite_is_positive():
    assert parse_spread_text("Ohio -6.5", "Ohio", "UNLV") == 6.5


def test_parse_spread_away_favorite_is_negative():
    assert parse_spread_text("UNLV -6.5", "Ohio", "UNLV") == -6.5


def test_parse_spread_rejects_nonfinite_values():
    assert parse_spread_text("Ohio NaN", "Ohio", "UNLV") is None
    assert parse_spread_text("Ohio inf", "Ohio", "UNLV") is None
    assert parse_spread_text("Ohio -inf", "Ohio", "UNLV") is None


def test_parse_spread_rejects_ambiguous_team_text():
    assert parse_spread_text("Miami -4", "Miami (FL)", "Florida State") is None


def test_select_first_parseable_provider_matches_verified_getter():
    selected = select_first_market_spread(
        _game(
            [
                {"provider": "BadBook", "formattedSpread": None},
                {"provider": "DraftKings", "formattedSpread": "UNLV -6.5"},
                {"provider": "Bovada", "formattedSpread": "Ohio -1.0"},
            ]
        )
    )
    assert selected is not None
    assert selected["provider"] == "DraftKings"
    assert selected["providerIndex"] == 1
    assert selected["marketSpread"] == -6.5
    assert math.isfinite(selected["marketSpread"])


def test_select_returns_none_when_no_provider_parses():
    assert (
        select_first_market_spread(
            _game(
                [
                    {"provider": "A", "formattedSpread": None},
                    {"provider": "B", "formattedSpread": "Something Else -7"},
                ]
            )
        )
        is None
    )
