from cfb_analytics.analytics.website_prediction_archive import (
    ARCHIVE_SEASONS,
    archive_record,
    summarize_week,
)


def test_archive_seasons_intentionally_exclude_covid_2020():
    assert 2020 not in ARCHIVE_SEASONS
    assert ARCHIVE_SEASONS == (2014, 2015, 2016, 2017, 2018, 2019, 2021, 2022, 2023, 2024, 2025)


def test_archive_record_keeps_historical_slate_truthful_without_prediction():
    row = archive_record(
        season=2014,
        season_type="regular",
        week=1,
        game_id="g1",
        context={"homeTeam": "Home", "awayTeam": "Away", "homeScore": 31.0, "awayScore": 24.0},
        prediction=None,
        market={"gameId": "g1", "homeTeam": "Home", "awayTeam": "Away", "marketSpread": 5.0},
    )
    assert row["evidenceStatus"] == "historical-slate"
    assert "predictedWinner" not in row
    assert row["actualHomeMargin"] == 7.0
    assert row["marketHomeMargin"] == 5.0


def test_archive_record_attaches_model_market_and_correctness():
    row = archive_record(
        season=2025,
        season_type="regular",
        week=7,
        game_id="g2",
        context={"homeTeam": "Home", "awayTeam": "Away", "homeScore": 21.0, "awayScore": 28.0},
        prediction={
            "gameId": "g2",
            "homeTeam": "Home",
            "awayTeam": "Away",
            "modelHomeMargin": -4.25,
            "marketHomeMargin": -2.0,
        },
        market={"gameId": "g2", "homeTeam": "Home", "awayTeam": "Away", "marketSpread": -2.0},
    )
    assert row["evidenceStatus"] == "official-oos"
    assert row["predictedWinner"] == "Away"
    assert row["modelHomeMargin"] == -4.25
    assert row["winnerCorrect"] is True
    assert row["modelAtsSide"] == "AWAY"
    assert row["atsCorrect"] is True
    assert row["atsResult"] == "WIN"


def test_archive_record_grades_wrong_winner_and_ats_without_rewriting_pick():
    row = archive_record(
        season=2024,
        season_type="regular",
        week=4,
        game_id="g3",
        context={"homeTeam": "Home", "awayTeam": "Away", "homeScore": 35.0, "awayScore": 17.0},
        prediction={
            "gameId": "g3",
            "homeTeam": "Home",
            "awayTeam": "Away",
            "modelHomeMargin": -2.0,
            "marketHomeMargin": 3.0,
        },
        market={"gameId": "g3", "homeTeam": "Home", "awayTeam": "Away", "marketSpread": 3.0},
    )
    assert row["predictedWinner"] == "Away"
    assert row["winnerCorrect"] is False
    assert row["modelAtsSide"] == "AWAY"
    assert row["atsCorrect"] is False
    assert row["atsResult"] == "LOSS"


def test_recommended_bet_is_separate_from_model_margin_ats_call():
    row = archive_record(
        season=2025,
        season_type="regular",
        week=8,
        game_id="g4",
        context={"homeTeam": "Home", "awayTeam": "Away", "homeScore": 30.0, "awayScore": 27.0},
        prediction={
            "gameId": "g4",
            "homeTeam": "Home",
            "awayTeam": "Away",
            "modelHomeMargin": 4.0,
            "marketHomeMargin": 2.5,
        },
        market={"gameId": "g4", "homeTeam": "Home", "awayTeam": "Away", "marketSpread": 2.5},
        recommended_bet={
            "gameId": "g4",
            "homeTeam": "Home",
            "awayTeam": "Away",
            "pickedSide": "HOME",
            "confidence": 0.61,
            "result": "WIN",
        },
    )
    assert row["recommendedBet"] is True
    assert row["recommendedBetTeam"] == "Home"
    assert row["recommendedBetConfidence"] == 0.61
    assert row["recommendedBetResult"] == "WIN"


def test_week_summary_reports_requested_public_metrics_and_minus_110_units():
    games = [
        {
            "modelHomeMargin": 6.0,
            "modelAbsoluteError": 2.0,
            "winnerCorrect": True,
            "atsResult": "WIN",
            "marketHomeMargin": 3.0,
            "recommendedBet": True,
            "recommendedBetResult": "WIN",
        },
        {
            "modelHomeMargin": -1.0,
            "modelAbsoluteError": 4.0,
            "winnerCorrect": False,
            "atsResult": "LOSS",
            "marketHomeMargin": 1.5,
            "recommendedBet": True,
            "recommendedBetResult": "LOSS",
        },
        {
            "marketHomeMargin": 7.0,
            "recommendedBet": False,
        },
    ]
    result = summarize_week(games, recommended_source_present=True)
    assert result["modelMae"] == 3.0
    assert result["winnerAccuracy"] == 0.5
    assert (result["atsWins"], result["atsLosses"], result["atsPushes"]) == (1, 1, 0)
    assert result["atsAccuracy"] == 0.5
    assert result["recommendedBets"] == 2
    assert result["recommendedBetWins"] == 1
    assert result["recommendedBetLosses"] == 1
    assert abs(result["recommendedBetUnits"] - (100.0 / 110.0 - 1.0)) < 1e-12
