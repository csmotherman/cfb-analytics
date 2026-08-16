# Prediction Model v1 Benchmark Contract

**Status:** REVALIDATION REQUIRED — AUTHORITATIVE TARGET FIX  
**Purpose:** preserve the current VOLUME + OLS architecture as the reference candidate while rebuilding its historical targets and SRS from authoritative CFBD game results.

## Model

Prediction v1 is the current **VOLUME + OLS** research leader architecture.

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

## Why the architecture was frozen

Research had already tested linear regularization, robust losses, median regression and blends, tree ensembles, recency weighting, rolling windows, two-stage win/magnitude architectures, and multiple mechanism families. None established a sufficiently stable recent-era advantage to replace VOLUME + OLS.

That justified freezing the architecture as the reference benchmark. It did **not** exempt the underlying data contract from future forensic review.

## Challenger policy

A new predictive feature or architecture does **not** enter Prediction v1 merely because it is football-plausible or improves one season.

It must be evaluated against this exact architecture using:

1. identical leakage-safe walk-forward samples;
2. paired MAE and RMSE as primary metrics;
3. winner accuracy as secondary context;
4. per-holdout results, not only pooled averages;
5. special attention to recent holdouts for forward use;
6. no promotion based on tuning against the test holdout.

If a challenger earns promotion after the corrected benchmark is revalidated, create a new version rather than silently mutating Prediction v1.

## Authoritative target finding

The integrity audit found that the historical model targets were not always equal to the authoritative CFBD game result.

Observed on the 2014–2019 and 2021–2025 corpus:

```text
model rows             8,510
exact final scores     8,215
exact final margins    8,218
margin mismatches        292
```

The problem came from using final score state reconstructed from canonical play records. That score state is not authoritative enough for a final-game target.

This matters twice:

1. the regression target itself was wrong for affected games;
2. SRS was fit from those same historical margins, so a model input was also contaminated.

The non-score Iterative rating families remain reusable because they do not consume final score.

## Corrected target contract

The model feature store now uses raw CFBD `games.json` final scores as the only authoritative source for:

```text
target_homeScore
target_awayScore
target_margin
target_homeWin
```

The feature-store rebuild reuses cached Iterative football ratings, applies authoritative game targets, and recomputes SRS from the corrected margins. It does not require a PBP replay or expensive drive-outcome refit.

Rebuild once:

```bash
python -m cfb_analytics.analytics.model_feature_store --all
```

Then rerun the integrity/stability gate:

```bash
python -m cfb_analytics.analytics.prediction_v1_integrity_audit
```

The target gate is strict: every stored model row must match raw home team, away team, home score, away score, and final margin before model diagnostics proceed.

## Revalidation sequence

Do not quote the old Prediction-v1 benchmark metrics as current until this sequence is complete:

```text
1. rebuild authoritative-target model feature stores
2. require TARGET INTEGRITY = PASS
3. rerun Prediction-v1 / volume benchmark on corrected targets + corrected SRS
4. rerun MWDR dependency and feature-stability diagnostics
5. decide whether the same VOLUME + OLS architecture remains the leader
```

The architecture remains the incumbent candidate during revalidation; its old numeric benchmark results are superseded until reproduced on the corrected data.

See `docs/PREDICTION_V1_INTEGRITY_AUDIT.md` for the audit contract and interpretation rules.

## Drive PPD status

Opponent-adjusted Drive PPD remains **RESEARCH ONLY**. Initial ablation showed useful incremental signal in some formulations, but season-by-season stability was not sufficient to add it to the benchmark.

PPD remains available for team profiles, drive grades, diagnostics, and future prediction challenges without changing the reference architecture.
