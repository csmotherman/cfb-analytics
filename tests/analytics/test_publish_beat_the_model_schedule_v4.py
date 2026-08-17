from cfb_analytics.analytics.publish_beat_the_model_schedule_v4 import (
    enrich_rankings,
    enrich_selected_games,
    team_metadata_from_payload,
)


def test_team_metadata_filters_to_fbs_and_uses_first_logo():
    payload = [
        {
            "id": 1,
            "school": "Alpha",
            "classification": "fbs",
            "abbreviation": "ALP",
            "conference": "Test",
            "color": "#111111",
            "alternateColor": "#eeeeee",
            "logos": ["https://example.com/alpha.png", "https://example.com/alpha-2.png"],
        },
        {
            "id": 2,
            "school": "Beta",
            "classification": "fcs",
            "logos": ["https://example.com/beta.png"],
        },
    ]

    actual = team_metadata_from_payload(payload)

    assert list(actual) == ["Alpha"]
    assert actual["Alpha"]["teamId"] == 1
    assert actual["Alpha"]["logo"] == "https://example.com/alpha.png"
    assert actual["Alpha"]["conference"] == "Test"


def test_enrich_rankings_does_not_change_rank_or_rating():
    rankings = {
        "season": 2026,
        "week": 1,
        "teams": [{"rank": 1, "team": "Alpha", "rating": 12.5}],
    }
    metadata = {
        "Alpha": {
            "teamId": 1,
            "abbreviation": "ALP",
            "conference": "Test",
            "color": "#111111",
            "alternateColor": "#eeeeee",
            "logo": "https://example.com/alpha.png",
        }
    }

    actual = enrich_rankings(rankings, metadata)
    row = actual["teams"][0]

    assert row["rank"] == 1
    assert row["rating"] == 12.5
    assert row["logo"] == "https://example.com/alpha.png"
    assert actual["teamMetadataStatus"] == "ok"


def test_selected_games_receive_home_and_away_logos():
    rankings = {
        "teams": [
            {"rank": 1, "team": "Alpha", "rating": 12.5, "teamId": 1, "logo": "https://example.com/alpha.png"},
            {"rank": 2, "team": "Beta", "rating": 11.0, "teamId": 2, "logo": "https://example.com/beta.png"},
        ]
    }
    games = [
        {
            "id": "g1",
            "homeTeam": "Alpha",
            "awayTeam": "Beta",
            "homeRank": 1,
            "awayRank": 2,
        }
    ]

    actual = enrich_selected_games(games, rankings)

    assert actual[0]["homeTeamId"] == 1
    assert actual[0]["awayTeamId"] == 2
    assert actual[0]["homeLogo"] == "https://example.com/alpha.png"
    assert actual[0]["awayLogo"] == "https://example.com/beta.png"
