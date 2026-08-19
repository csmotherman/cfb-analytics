import json
from pathlib import Path

import pytest

from cfb_analytics.pipelines.publish_predictions import (
    american_implied_probability,
    no_vig_two_way_probability,
    publish_game_predictions,
    publish_market_outlook,
)


def test_american_and_no_vig_probability() -> None:
    assert american_implied_probability(260) == pytest.approx(100 / 360)
    assert american_implied_probability(-325) == pytest.approx(325 / 425)
    assert no_vig_two_way_probability(260, -325) == pytest.approx(0.2664576802507837)


def test_publish_game_predictions_filters_team_and_preserves_no_probability(tmp_path: Path) -> None:
    snapshot = tmp_path / "week-01.json"
    snapshot.write_text(json.dumps({
        "freezeVersion": "prediction-v2-2026-prospective-freeze-v1",
        "week": 1,
        "asOf": "2026-08-18T12:00:00-04:00",
        "predictions": [
            {"gameId": "1", "season": 2026, "week": 1, "homeTeam": "Michigan", "awayTeam": "Western Michigan", "predictedWinner": "Michigan", "predictedMargin": 21.5, "freezeVersion": "prediction-v2-2026-prospective-freeze-v1"},
            {"gameId": "2", "season": 2026, "week": 1, "homeTeam": "A", "awayTeam": "B", "predictedWinner": "A", "predictedMargin": 3.0, "freezeVersion": "prediction-v2-2026-prospective-freeze-v1"},
        ],
    }))
    output = tmp_path / "published.json"

    result = publish_game_predictions([snapshot], output)

    assert len(result["games"]) == 1
    assert result["games"][0]["teamPredictedMargin"] == 21.5
    assert result["games"][0]["winProbability"] is None
    assert json.loads(output.read_text()) == result


def test_publish_market_outlook_is_labeled_benchmark(tmp_path: Path) -> None:
    result = publish_market_outlook(
        tmp_path / "outlook.json", team="Michigan", as_of="2026-08-18T08:14:00-04:00",
        yes_odds=260, no_odds=-325, source_name="BetMGM", source_url="https://example.test/odds",
    )
    assert result["valueType"] == "BENCHMARK"
    assert result["cfp"]["noVigImpliedProbability"] == pytest.approx(0.2664576802507837)
