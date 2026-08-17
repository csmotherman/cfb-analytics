from __future__ import annotations

import math

from cfb_analytics.analytics.full_ats_meta_gate import (
    BASELINE_THRESHOLD,
    GATE_FEATURES,
    GATE_THRESHOLD,
    GATE_VARIANTS,
    META_OUTPUT_FEATURES,
    OD_FEATURES,
    OOF_SOURCE_SEASONS,
    _candidate,
    _fit_gate,
    _gate_bet_record,
    _gate_target,
    _predict_gate,
    cumulative_rank_curve,
    quality_curve,
)
from cfb_analytics.analytics.market_edge_model_zoo import BREAK_EVEN_MINUS_110, MODEL_FEATURES
from cfb_analytics.analytics.prediction_v1_site_aware_challenger import TEST_SEASONS


def _row(seed: int, target: int = 1) -> dict:
    row = {name: float((seed % 7) - 3) / 3.0 for name in GATE_FEATURES}
    row.update(
        {
            "season": 2018 + seed % 3,
            "seasonType": "regular",
            "week": 5 + seed % 4,
            "gameId": str(seed),
            "homeTeam": "H",
            "awayTeam": "A",
            "marketHomeMargin": 3.5,
            "target_margin": 7.0 if target else 0.0,
            "actualCoverSign": 1 if target else -1,
            "baselineProbabilityHomeCover": 0.60,
            "baselineConfidence": 0.60,
            "baselinePickedSideSign": 1,
            "baselineResult": "WIN" if target else "LOSS",
            "gateTarget": target,
            "homeGamesPlayedBefore": 4.0,
            "awayGamesPlayedBefore": 4.0,
        }
    )
    return row


def test_gate_feature_contract_is_unique_and_pregame_safe():
    assert len(GATE_FEATURES) == len(set(GATE_FEATURES))
    assert tuple(GATE_FEATURES[: len(MODEL_FEATURES)]) == tuple(MODEL_FEATURES)
    assert len(OD_FEATURES) == 9
    assert len(META_OUTPUT_FEATURES) == 5
    forbidden = ("target_", "actual", "result", "score")
    assert not any(any(token.lower() in name.lower() for token in forbidden) for name in GATE_FEATURES)


def test_gate_threshold_is_minus_110_break_even_and_candidate_is_fixed():
    assert math.isclose(GATE_THRESHOLD, BREAK_EVEN_MINUS_110)
    assert BASELINE_THRESHOLD == 0.575
    row = _row(1)
    row["baselineConfidence"] = 0.575
    assert _candidate(row)
    row["baselineConfidence"] = 0.574999
    assert not _candidate(row)


def test_gate_target_means_existing_baseline_side_was_correct():
    row = _row(1, target=1)
    assert _gate_target(row) == 1
    row["actualCoverSign"] = -1
    assert _gate_target(row) == 0
    row["actualCoverSign"] = 0
    assert _gate_target(row) is None


def test_both_predeclared_gate_models_fit_and_return_probabilities():
    rows = [_row(i, target=i % 2) for i in range(120)]
    test = [_row(200 + i, target=i % 2) for i in range(10)]
    for variant in GATE_VARIANTS:
        model = _fit_gate(rows, variant)
        probs = _predict_gate(model, test)
        assert probs.shape == (10,)
        assert all(0.0 <= float(p) <= 1.0 for p in probs)


def test_gate_never_changes_the_first_stage_side():
    row = _row(1, target=1)
    row["baselinePickedSideSign"] = -1
    row["baselineResult"] = "LOSS"
    record = _gate_bet_record(row, "META_LOGISTIC", 0.70)
    assert record["pickedSideSign"] == -1
    assert record["pickedSide"] == "AWAY"
    assert record["result"] == "LOSS"
    assert record["gateAccepted"] is True


def test_quality_diagnostics_account_for_every_gate_record():
    rows = []
    for i, p in enumerate((0.44, 0.48, 0.51, 0.53, 0.56, 0.59, 0.63)):
        row = _gate_bet_record(_row(i, target=i % 2), "META_LOGISTIC", p)
        rows.append(row)
    buckets = quality_curve(rows)
    assert sum(r["bets"] for r in buckets) == len(rows)
    cumulative = cumulative_rank_curve(rows)
    assert cumulative[-1]["bets"] == len(rows)
    assert cumulative[-1]["topFraction"] == 1.0


def test_cross_fit_source_and_test_season_contract():
    assert min(OOF_SOURCE_SEASONS) > 2014
    assert set(TEST_SEASONS).issubset(set(OOF_SOURCE_SEASONS))
    for test_season in TEST_SEASONS:
        prior_sources = [season for season in OOF_SOURCE_SEASONS if season < test_season]
        assert prior_sources
        assert all(season < test_season for season in prior_sources)
