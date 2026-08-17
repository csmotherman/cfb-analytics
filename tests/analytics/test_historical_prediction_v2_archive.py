import cfb_analytics.analytics.historical_prediction_v2_archive as module


def test_combined_predictions_preserve_stored_mature_on_overlap():
    mature = {
        "g1": {
            "gameId": "g1",
            "homeTeam": "Home",
            "awayTeam": "Away",
            "modelHomeMargin": 3.0,
        }
    }
    early = {
        "g1": {
            "gameId": "g1",
            "homeTeam": "Home",
            "awayTeam": "Away",
            "modelHomeMargin": 7.0,
            "predictionSource": module.EARLY_ARCHIVE_SOURCE,
        },
        "g2": {
            "gameId": "g2",
            "homeTeam": "Other Home",
            "awayTeam": "Other Away",
            "modelHomeMargin": -2.0,
            "predictionSource": module.EARLY_ARCHIVE_SOURCE,
        },
    }

    combined, counts = module.combine_historical_oos_predictions(mature, early)

    assert combined["g1"]["modelHomeMargin"] == 3.0
    assert combined["g1"]["predictionSource"] == module.MATURE_ARCHIVE_SOURCE
    assert combined["g2"]["modelHomeMargin"] == -2.0
    assert counts == {
        "mature": 1,
        "earlyGenerated": 2,
        "earlyOverlap": 1,
        "earlySupplement": 1,
        "combined": 2,
    }


def test_early_prior_reconstruction_trains_only_on_earlier_seasons(monkeypatch, tmp_path):
    monkeypatch.setattr(module, "TEST_SEASONS", (2018,))
    monkeypatch.setattr(module, "PREDICTION_V2_FEATURES", ("f",))

    blend = {
        2015: [{"gameId": "15", "season": 2015, "f": 1.0, "target_margin": 1.0}],
        2016: [{"gameId": "16", "season": 2016, "f": 2.0, "target_margin": 2.0}],
        2017: [{"gameId": "17", "season": 2017, "f": 3.0, "target_margin": 3.0}],
        2018: [
            {
                "gameId": "18",
                "season": 2018,
                "seasonType": "regular",
                "week": 1,
                "homeTeam": "Home",
                "awayTeam": "Away",
                "f": 4.0,
                "target_margin": 99.0,
                "priorWeightHome": 1.0,
                "priorWeightAway": 1.0,
            }
        ],
    }
    monkeypatch.setattr(
        module,
        "build_datasets",
        lambda raw_root, processed_root: {
            "blend": blend,
            "priorMap": {2015: 2014, 2016: 2015, 2017: 2016, 2018: 2017},
        },
    )

    seen_training_seasons = []

    def fake_fit(rows):
        seen_training_seasons.extend(int(row["season"]) for row in rows)
        return {"fake": True}

    monkeypatch.setattr(module, "_fit_early_model", fake_fit)
    monkeypatch.setattr(module, "predict_generic", lambda model, row: float(row["f"]) * 2.0)

    result = module.build_early_prior_oos_predictions(tmp_path / "raw", tmp_path / "processed")

    assert seen_training_seasons == [2015, 2016, 2017]
    assert 2018 not in seen_training_seasons
    assert result["18"]["modelHomeMargin"] == 8.0
    assert result["18"]["trainingSeasons"] == [2015, 2016, 2017]
    assert result["18"]["predictionSource"] == module.EARLY_ARCHIVE_SOURCE
