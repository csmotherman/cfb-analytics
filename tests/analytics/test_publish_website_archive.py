import json

import cfb_analytics.analytics.publish_website_archive as publish_module


def test_publish_manifest_counts_rows_market_and_combined_model(tmp_path, monkeypatch):
    monkeypatch.setattr(publish_module, "ARCHIVE_SEASONS", (2025,))
    monkeypatch.setattr(publish_module, "EXPECTED_HISTORICAL_GAMES", 2)
    monkeypatch.setattr(publish_module, "EXPECTED_STORED_MATURE_OOS_MODEL_GAMES", 1)
    monkeypatch.setattr(publish_module, "EXPECTED_CLEAN_MARKET_ROWS", 3)
    monkeypatch.setattr(publish_module, "EXPECTED_RECOMMENDED_BETS", 1)

    season_dir = tmp_path / "season=2025"
    season_dir.mkdir(parents=True)
    (season_dir / "week=1.json").write_text(
        json.dumps(
            {
                "season": 2025,
                "week": 1,
                "games": [
                    {
                        "id": "g1",
                        "homeTeam": "Home",
                        "awayTeam": "Away",
                        "marketHomeMargin": 5.0,
                        "modelHomeMargin": 7.0,
                    },
                    {
                        "id": "g2",
                        "homeTeam": "Other Home",
                        "awayTeam": "Other Away",
                        "marketHomeMargin": None,
                        "modelHomeMargin": -2.0,
                        "predictionSource": "prediction-v2-early-prior-walk-forward-oos",
                    },
                ],
            }
        )
    )

    report = {
        "version": "test",
        "games": 2,
        "officialOosModelGames": 2,
        "matureOosModelGames": 1,
        "earlyPriorGeneratedGames": 1,
        "earlyPriorOverlapGames": 0,
        "earlyPriorSupplementGames": 1,
        "combinedOosModelGames": 2,
        "marketSourcePresent": True,
        "marketRows": 3,
        "recommendedBets": 1,
        "seasonSummaries": [
            {
                "season": 2025,
                "earlyPriorModelGames": 1,
            }
        ],
    }
    manifest = publish_module._validate_and_manifest(tmp_path, report)

    assert manifest["historicalGames"] == 2
    assert manifest["marketGames"] == 1
    assert manifest["missingMarketGames"] == 1
    assert manifest["storedMatureOosModelGames"] == 1
    assert manifest["earlyPriorSupplementGames"] == 1
    assert manifest["officialOosModelGames"] == 2
    assert manifest["recommendedBets"] == 1
    assert manifest["seasons"] == [
        {
            "season": 2025,
            "weeks": [1],
            "games": 2,
            "marketGames": 1,
            "modelGames": 2,
            "earlyPriorModelGames": 1,
        }
    ]
    missing = json.loads((tmp_path / "missing-market-lines.json").read_text())
    assert missing == [
        {
            "season": 2025,
            "week": 1,
            "gameId": "g2",
            "homeTeam": "Other Home",
            "awayTeam": "Other Away",
        }
    ]


def test_publish_manifest_rejects_partial_historical_universe(tmp_path, monkeypatch):
    monkeypatch.setattr(publish_module, "EXPECTED_HISTORICAL_GAMES", 2)
    report = {
        "version": "test",
        "games": 1,
        "officialOosModelGames": 2,
        "matureOosModelGames": publish_module.EXPECTED_STORED_MATURE_OOS_MODEL_GAMES,
        "earlyPriorGeneratedGames": 1,
        "earlyPriorOverlapGames": 0,
        "earlyPriorSupplementGames": 1,
        "combinedOosModelGames": publish_module.EXPECTED_STORED_MATURE_OOS_MODEL_GAMES + 1,
        "marketSourcePresent": True,
        "marketRows": publish_module.EXPECTED_CLEAN_MARKET_ROWS,
        "recommendedBets": publish_module.EXPECTED_RECOMMENDED_BETS,
        "seasonSummaries": [{"season": 2025, "earlyPriorModelGames": 1}],
    }

    try:
        publish_module._validate_and_manifest(tmp_path, report)
    except ValueError as exc:
        assert "Refusing partial website archive" in str(exc)
    else:
        raise AssertionError("partial archive should fail closed")


def test_prediction_count_validation_rejects_missing_early_supplement(monkeypatch):
    monkeypatch.setattr(publish_module, "EXPECTED_STORED_MATURE_OOS_MODEL_GAMES", 3)
    report = {
        "matureOosModelGames": 3,
        "earlyPriorGeneratedGames": 2,
        "earlyPriorOverlapGames": 2,
        "earlyPriorSupplementGames": 0,
        "combinedOosModelGames": 3,
        "officialOosModelGames": 3,
        "seasonSummaries": [{"season": 2025, "earlyPriorModelGames": 0}],
    }

    try:
        publish_module._validate_prediction_counts(report)
    except ValueError as exc:
        assert "did not fill any previously blank" in str(exc)
    else:
        raise AssertionError("missing early supplement should fail closed")
