# Prediction Model v1 Benchmark Contract

**Status:** LOCKED RESEARCH BENCHMARK  
**Purpose:** stable reference model for future feature/model ablations; not a claim of final production optimality.

## Model

Prediction v1 is the current **VOLUME + OLS** research leader.

Feature groups:

```text
BASE = Iterative Ratings + SRS
MWDR = home_MWDR_OffenseEdge + home_MWDR_DefenseEdge
STABLE = BASE + MWDR + mwdrXExpectedPossessions
VOLUME ENGINE = successVolumeEdge + explosiveVolumeEdge + turnoverVolumeEdge
PREDICTION V1 = STABLE + VOLUME ENGINE
```

Interaction definitions:

```text
mwdrXExpectedPossessions
  = (home_MWDR_OffenseEdge + home_MWDR_DefenseEdge)
    * expectedPossessionsPerTeam

successVolumeEdge
  = netSuccessRateEdge * expectedPossessionsPerTeam

explosiveVolumeEdge
  = netExplosiveRateEdge * expectedPossessionsPerTeam

turnoverVolumeEdge
  = netTurnoverPressureEdge * expectedPossessionsPerTeam
```

Estimator:

- ordinary least squares
- signed final margin target
- equal training weight by game
- all prior available seasons in each walk-forward holdout
- identical common sample for ablations
- no current/future game information in pregame features

## Why lock the benchmark now

Research has already tested linear regularization, robust losses, median regression and blends, tree ensembles, recency weighting, rolling windows, two-stage win/magnitude architectures, and multiple mechanism families. None has established a sufficiently stable recent-era advantage to replace VOLUME + OLS.

The benchmark is therefore frozen so profile/identity development can proceed without silently changing the prediction target.

## Challenger policy

A new predictive feature or architecture does **not** enter Prediction v1 merely because it is football-plausible or improves one season.

It must be evaluated against this exact benchmark using:

1. identical leakage-safe walk-forward samples;
2. paired MAE and RMSE as primary metrics;
3. winner accuracy as secondary context;
4. per-holdout results, not only pooled averages;
5. special attention to recent holdouts for forward use;
6. no promotion based on tuning against the test holdout.

If a challenger earns promotion, create a new version rather than silently mutating Prediction v1.

## Integrity re-audit before Prediction v2 work

Recent drive-state forensics exposed two dependencies that must be quantified before adding more model complexity:

1. current stored game targets were originally oriented from canonical play score state, while raw CFBD `games.json` contains the authoritative final game result;
2. MWDR ultimately depends on the legacy derived-drive `_points(d)` score-delta helper.

This does **not** invalidate Prediction v1. It creates a mandatory diagnostic gate before future promotion work.

Run:

```bash
python -m cfb_analytics.analytics.prediction_v1_integrity_audit
```

The audit is saved-data only and performs three steps:

```text
TARGET INTEGRITY
  raw CFBD final score
  vs stored model home/away score + margin

MWDR DEPENDENCY
  CURRENT FULL
  vs NO_MWDR
  vs MWDR_NO_INTERACTION

FEATURE STABILITY
  standardized coefficient signs
  + leave-one-feature-out OOS deltas
  + largest pairwise feature correlations
```

The target gate is strict: every stored model row must match raw home team, away team, home score, away score, and final margin before the default command proceeds to feature diagnostics.

See `docs/PREDICTION_V1_INTEGRITY_AUDIT.md` for the full contract and interpretation rules.

## Drive PPD status

Opponent-adjusted Drive PPD remains **RESEARCH ONLY**. Initial ablation shows useful incremental signal in some formulations, but season-by-season stability is not yet sufficient to add it to the locked benchmark.

PPD remains available for team profiles, drive grades, diagnostics, and future prediction challenges without changing Prediction v1.
