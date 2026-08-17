from cfb_analytics.analytics.website_prediction_archive import archive_record


def test_archive_record_keeps_historical_slate_truthful_without_prediction():
    row = archive_record(
        season=2014,
        season_type="regular",
        week=1,
        game_id="g1",
        context={"homeTeam": "Home", "awayTeam": "Away", "homeScore": 31.0, "awayScore": 24.0},
        prediction=None,
    )
    assert row["evidenceStatus"] == "historical-slate"
    assert "predictedWinner" not in row
    assert row["actualHomeMargin"] == 7.0


def test_archive_record_attaches_only_stored_oos_model_call():
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
        },
    )
    assert row["evidenceStatus"] == "official-oos"
    assert row["predictedWinner"] == "Away"
    assert row["modelHomeMargin"] == -4.25
    assert row["correct"] is True


def test_archive_record_grades_wrong_winner_without_rewriting_pick():
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
        },
    )
    assert row["predictedWinner"] == "Away"
    assert row["correct"] is False
