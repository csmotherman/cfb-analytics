from cfb_analytics.analytics import publish_beat_the_model_schedule as base
from cfb_analytics.analytics import publish_beat_the_model_schedule_v3 as v3


def test_positive_cfbd_spread_means_away_favorite_without_moneylines():
    raw = {
        "id": 1,
        "homeTeam": "Stanford",
        "awayTeam": "Miami",
        "lines": [
            {
                "provider": "Book A",
                "spread": 23.5,
                "formattedSpread": "Stanford +23.5",
            },
            {
                "provider": "Book B",
                "spread": 22.5,
                "formattedSpread": "Stanford +22.5",
            },
        ],
    }

    market = v3.market_consensus(raw)
    assert market is not None
    assert market["marketFavorite"] == "Miami"
    assert market["marketSpread"] == 23.0
    assert market["marketLine"] == "Miami -23"


def test_negative_cfbd_spread_means_home_favorite_without_moneylines():
    raw = {
        "id": 2,
        "homeTeam": "USC",
        "awayTeam": "Fresno State",
        "lines": [
            {"provider": "Book A", "spread": -23.0},
            {"provider": "Book B", "spread": -24.0},
        ],
    }

    market = v3.market_consensus(raw)
    assert market is not None
    assert market["marketFavorite"] == "USC"
    assert market["marketSpread"] == 23.5
    assert market["marketLine"] == "USC -23.5"


def test_paired_moneylines_drive_no_vig_probability_and_favorite():
    raw = {
        "id": 3,
        "homeTeam": "Home",
        "awayTeam": "Away",
        "lines": [
            {
                "provider": "Book A",
                "spread": -3.0,
                "homeMoneyline": -150,
                "awayMoneyline": 130,
            }
        ],
    }

    market = v3.market_consensus(raw)
    assert market is not None
    assert market["marketFavorite"] == "Home"
    assert 0.55 < market["marketHomeWinProbability"] < 0.60
    assert 0.40 < market["marketAwayWinProbability"] < 0.45


def test_close_games_outrank_elite_blowout_when_filling_official_15():
    rankings = {
        "teams": [
            {"rank": rank, "team": f"T{rank}", "rating": 200 - rank}
            for rank in range(1, 80)
        ]
    }

    schedule = [
        {
            "id": "elite-blowout",
            "season": 2026,
            "week": 1,
            "homeTeam": "T1",
            "awayTeam": "T2",
            "kickoff": None,
            "completed": False,
            "actualHomeScore": None,
            "actualAwayScore": None,
        }
    ]
    market = {
        "elite-blowout": {
            "marketSpread": 28.0,
            "marketSource": v3.MARKET_SOURCE_VERSION,
            "marketProviderCount": 1,
            "marketFavorite": "T1",
            "marketLine": "T1 -28",
        }
    }

    # Fifteen lower-ranked but legitimately competitive games should fill the
    # Official 15 before a famous 28-point mismatch.
    for index in range(15):
        home_rank = 30 + index * 2
        away_rank = home_rank + 1
        gid = f"close-{index}"
        schedule.append(
            {
                "id": gid,
                "season": 2026,
                "week": 1,
                "homeTeam": f"T{home_rank}",
                "awayTeam": f"T{away_rank}",
                "kickoff": None,
                "completed": False,
                "actualHomeScore": None,
                "actualAwayScore": None,
            }
        )
        market[gid] = {
            "marketSpread": 6.0,
            "marketSource": v3.MARKET_SOURCE_VERSION,
            "marketProviderCount": 1,
            "marketFavorite": f"T{home_rank}",
            "marketLine": f"T{home_rank} -6",
        }

    selected = base.select_slate(
        schedule,
        rankings,
        existing_current={},
        model_by_id={},
        market_by_id=market,
        market_snapshot_at="2026-08-17T19:00:00+00:00",
    )

    assert len(selected) == 15
    assert "elite-blowout" not in {game["id"] for game in selected}
    assert all(game["marketSpread"] == 6.0 for game in selected)
