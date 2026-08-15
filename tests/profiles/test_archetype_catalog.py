from cfb_analytics.profiles.archetype_catalog import CATALOG
from cfb_analytics.profiles.match_archetypes import match_history, match_snapshot


def test_catalog_contains_exactly_2000_unique_named_candidates():
    assert len(CATALOG) == 2000
    assert len({x.id for x in CATALOG}) == 2000
    assert len({x.name for x in CATALOG}) == 2000
    assert all(x.targets for x in CATALOG)


def test_run_or_die_shape_matches_run_or_die_family():
    row = {
        "identity_rushing_attack": 72.0,
        "identity_passing_attack": 20.0,
        "current_rush_rate_percentile": 92.0,
        "identity_one_dimensionality": 55.0,
        "identity_scheme_constraint": 70.0,
        "identity_offense_quality": 48.0,
    }
    top = match_snapshot(row, top_n=10)
    assert top
    assert any(x["rootName"] == "Run or Die" for x in top)


def test_defense_or_bust_shape_matches_defense_led_family():
    row = {
        "identity_offense_quality": 25.0,
        "identity_defense_quality": 86.0,
        "identity_offense_vs_defense": -61.0,
        "identity_rushing_defense": 82.0,
        "identity_passing_defense": 84.0,
    }
    top = match_snapshot(row, top_n=10)
    assert top
    assert any(x["rootName"] == "Defense or Bust" for x in top)


def test_historical_matcher_excludes_2025_when_default_seasons_are_requested():
    base = {
        "team": "Example",
        "seasonType": "regular",
        "week": 8,
        "throughGameId": "g8",
        "gamesPlayed": 8,
        "identity_rushing_attack": 72.0,
        "identity_passing_attack": 20.0,
        "current_rush_rate_percentile": 92.0,
        "identity_one_dimensionality": 55.0,
        "identity_offense_quality": 48.0,
    }
    rows = [dict(base, season=2024), dict(base, season=2025, throughGameId="g9")]
    report = match_history(rows)
    assert report["snapshotCount"] == 1
    assert report["matches"][0]["season"] == 2024
    assert 2025 not in report["seasons"]
