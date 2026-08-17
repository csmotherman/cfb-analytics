import pytest

from cfb_analytics.analytics.prediction_v2_market_benchmark import (
    join_predictions_to_market,
    normalize_market_games,
    parse_formatted_spread,
    select_market_line,
    summarize_edge_buckets,
    summarize_matched,
)


def _game(lines):
    return {
        "id": 123,
        "season": 2024,
        "seasonType": "regular",
        "week": 1,
        "homeTeam": "Georgia Tech",
        "awayTeam": "Florida State",
        "lines": lines,
    }


def test_parse_formatted_spread_uses_home_margin_sign():
    assert parse_formatted_spread(
        "Georgia Tech -3.5", "Georgia Tech", "Florida State"
    ) == 3.5
    assert parse_formatted_spread(
        "Florida State -10.5", "Georgia Tech", "Florida State"
    ) == -10.5
    assert parse_formatted_spread("PK", "Georgia Tech", "Florida State") == 0.0
    assert parse_formatted_spread(
        "Miami -4", "Miami (FL)", "Florida State"
    ) is None


def test_select_market_line_prefers_consensus_and_crosschecks_numeric_sign():
    selected = select_market_line(
        _game(
            [
                {
                    "provider": "DraftKings",
                    "spread": 11.0,
                    "formattedSpread": "Florida State -11",
                },
                {
                    "provider": "consensus",
                    "spread": 10.5,
                    "spreadOpen": 12.5,
                    "formattedSpread": "Florida State -10.5",
                },
            ]
        )
    )
    assert selected is not None
    assert selected["selection"] == "consensus"
    assert selected["provider"] == "consensus"
    assert selected["marketHomeMargin"] == -10.5
    assert selected["marketOpenHomeMargin"] == -12.5


def test_select_market_line_uses_median_fallback_not_first_provider():
    selected = select_market_line(
        _game(
            [
                {"provider": "A", "spread": 8.0},
                {"provider": "B", "spread": 10.0},
                {"provider": "C", "spread": 9.0},
            ]
        )
    )
    assert selected is not None
    assert selected["selection"] == "median-fallback"
    assert selected["marketHomeMargin"] == -9.0

    assert (
        select_market_line(
            _game([{"provider": "A", "spread": 8.0}]),
            fallback_median=False,
        )
        is None
    )


def test_spread_sign_conflict_is_rejected():
    selected = select_market_line(
        _game(
            [
                {
                    "provider": "consensus",
                    "spread": -10.5,
                    "formattedSpread": "Florida State -10.5",
                }
            ]
        )
    )
    assert selected is None


def test_normalize_market_games_rejects_duplicate_game_ids():
    game = _game([{"provider": "consensus", "spread": 3.0}])
    with pytest.raises(ValueError, match="Duplicate market gameId"):
        normalize_market_games([game, dict(game)])


def test_join_predictions_requires_home_away_identity_match():
    predictions = [
        {
            "gameId": "123",
            "minGames": 3,
            "season": 2024,
            "homeTeam": "Georgia Tech",
            "awayTeam": "Florida State",
            "modelHomeMargin": -7.0,
            "actualHomeMargin": 3.0,
        }
    ]
    market = [
        {
            "gameId": "123",
            "homeTeam": "Florida State",
            "awayTeam": "Georgia Tech",
            "marketHomeMargin": -10.5,
        }
    ]
    with pytest.raises(ValueError, match="home-away identity mismatch"):
        join_predictions_to_market(predictions, market)


def test_summary_compares_model_market_and_ats_side():
    rows = [
        {
            "actualHomeMargin": 7.0,
            "modelHomeMargin": 6.0,
            "marketHomeMargin": 3.0,
        },
        {
            "actualHomeMargin": -3.0,
            "modelHomeMargin": -1.0,
            "marketHomeMargin": 2.0,
        },
        {
            "actualHomeMargin": 1.0,
            "modelHomeMargin": -2.0,
            "marketHomeMargin": -1.0,
        },
        {
            "actualHomeMargin": 3.0,
            "modelHomeMargin": 6.0,
            "marketHomeMargin": 3.0,
        },
    ]
    result = summarize_matched(rows)
    assert result["n"] == 4
    assert result["modelMae"] == pytest.approx(2.25)
    assert result["marketMae"] == pytest.approx(2.75)
    assert result["deltaMae"] == pytest.approx(-0.5)
    assert result["atsWins"] == 2
    assert result["atsLosses"] == 1
    assert result["atsPushes"] == 1
    assert result["atsAccuracy"] == pytest.approx(2 / 3)


def test_edge_buckets_are_nested_by_minimum_disagreement():
    rows = [
        {
            "actualHomeMargin": 7.0,
            "modelHomeMargin": 8.0,
            "marketHomeMargin": 3.0,
        },
        {
            "actualHomeMargin": 1.0,
            "modelHomeMargin": 1.5,
            "marketHomeMargin": 1.0,
        },
    ]
    buckets = summarize_edge_buckets(rows, thresholds=(0.0, 3.0))
    assert buckets[0]["n"] == 2
    assert buckets[1]["n"] == 1
