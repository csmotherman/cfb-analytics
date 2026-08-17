from __future__ import annotations

from cfb_analytics.prototypes import historical_unit_draft as v1
from cfb_analytics.prototypes.historical_unit_draft_v2 import (
    MAX_PASSES,
    MAX_SPINS,
    WHEEL_TOP_N_PER_SEASON,
    finalize_dataset,
    pass_aware_baseline,
    perfect_foresight_upper_bound,
)


def _row(name: str, rank: int, value: float) -> dict:
    return {
        "team": name,
        "season": 2019,
        "srsRank": rank,
        "categories": {
            category: {
                "z": value,
                "grade": 50.0 + 20.0 * value,
                "letter": "A" if value >= 2 else "B",
            }
            for category in v1.CATEGORY_ORDER
        },
    }


def _dataset() -> dict:
    pool = [_row(f"Team {i}", i % 12 + 1, 0.5 + i / 20.0) for i in range(100)]
    return {
        "schemaVersion": 1,
        "challengeVersion": "historical-unit-draft-v1",
        "status": "data-prototype-only",
        "wheelPool": pool,
        "wheelEligibility": {},
        "rules": {},
        "dataNotes": [],
        "strengthModel": {
            "categoryWeights": {category: 1 / 7 for category in v1.CATEGORY_ORDER},
            "intercept": 10.0,
            "scale": 10.0,
        },
        "marginCalibration": {"srsToMarginScale": 1.0, "residualSd": 14.0},
        "target": {"srs": 25.0},
    }


def test_finalize_dataset_locks_playable_rules() -> None:
    d = finalize_dataset(_dataset())
    assert d["challengeVersion"] == "historical-unit-draft-v2"
    assert d["rules"]["requiredUnits"] == 7
    assert d["rules"]["passes"] == MAX_PASSES == 3
    assert d["rules"]["maxSpins"] == MAX_SPINS == 10
    assert d["wheelEligibility"]["topSrsPerSeason"] == WHEEL_TOP_N_PER_SEASON == 10
    assert all(int(row["srsRank"]) <= 10 for row in d["wheelPool"])


def test_pass_aware_baseline_still_fills_all_seven_units() -> None:
    d = finalize_dataset(_dataset())
    spins = d["wheelPool"][:MAX_SPINS]
    selections, result, decisions = pass_aware_baseline(d, spins, pass_grade=99.0)
    assert len(selections) == 7
    assert len([x for x in decisions if x["action"] == "pass"]) <= 3
    assert len([x for x in decisions if x["action"] == "draft"]) == 7
    assert 0 <= result["winProbability"] <= 1


def test_perfect_foresight_is_at_least_as_strong_as_baseline() -> None:
    d = finalize_dataset(_dataset())
    spins = d["wheelPool"][:MAX_SPINS]
    _, baseline, _ = pass_aware_baseline(d, spins)
    _, oracle = perfect_foresight_upper_bound(d, spins)
    assert oracle["estimatedHybridSrs"] >= baseline["estimatedHybridSrs"]
    assert oracle["winProbability"] >= baseline["winProbability"]
