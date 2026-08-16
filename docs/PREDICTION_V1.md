# Prediction Model v1 Benchmark Contract

**Status:** SUPERSEDED BY PREDICTION V2 RESEARCH BENCHMARK  
**Purpose:** preserve the corrected VOLUME + OLS predecessor benchmark and its post-repair research history.

## Model

Prediction v1 is the corrected **VOLUME + OLS** predecessor architecture.

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

- ordinary least squares;
- signed final margin target;
- equal training weight by game;
- all prior available seasons in each walk-forward holdout;
- identical common sample for ablations;
- no current/future game information in pregame features.

## Authoritative target repair

The integrity audit found that the historical model targets were not always equal to the authoritative CFBD game result.

Original finding on the 2014–2019 and 2021–2025 corpus:

```text
model rows             8,510
exact final scores     8,215
exact final margins    8,218
margin mismatches        292
```

The problem came from using final score state reconstructed from canonical play records. That score state was not authoritative enough for a final-game target.

This mattered twice:

1. the regression target itself was wrong for affected games;
2. SRS was fit from those same historical margins, so a model input was also contaminated.

The non-score Iterative rating families remained reusable because they do not consume final score.

## Corrected target contract

The model feature store now uses raw CFBD `games.json` final scores as the only authoritative source for:

```text
target_homeScore
target_awayScore
target_margin
target_homeWin
```

The corrected feature-store rebuild reuses cached Iterative football ratings, applies authoritative game targets, and recomputes SRS from corrected margins.

The post-rebuild integrity audit passed:

```text
model rows              8,510
home/away team matches  8,510 / 8,510
exact final scores      8,510 / 8,510
exact final margins     8,510 / 8,510
```

## Corrected MWDR / feature stability finding

On the corrected data:

- SRS was the strongest drop-one feature;
- removing the entire MWDR family worsened recent MAE in all 6 min3/min4 2023–2025 folds;
- `mwdrXExpectedPossessions` was strongly supported by the 14-fold drop-one screen;
- several individual terms looked redundant, but that did not imply that they could be removed together safely.

The MWDR family remained in v1. Individual MWDR coefficient signs are not interpreted causally because the raw MWDR edges are highly collinear with `mwdrXExpectedPossessions`.

## Volume-engine revalidation

Corrected FULL was rechecked against STABLE on the six recent 2023–2025 min3/min4 folds.

```text
STABLE - FULL
mean MAE delta   +0.0053
mean RMSE delta  +0.0067
STABLE MAE wins   2/6
STABLE RMSE wins  1/6
```

Positive `STABLE - FULL` deltas mean FULL was better. The volume block therefore survived corrected-target revalidation.

## Challengers screened after correction

### LEAN feature-pruning challenger

A development-only rule selected four features for removal using 2018–2022 folds, then froze that 15-feature model for 2023–2025 validation.

```text
LEAN - FULL recent 6
mean MAE delta   +0.0205
mean RMSE delta  +0.0217
MAE better        2/6
RMSE better       1/6
```

**Decision:** not promoted.

### SYMMETRIC / net reparameterization

A fixed 12-feature net-edge model reduced redundant home/away degrees of freedom.

```text
ALL 14
mean MAE delta   -0.0246
mean RMSE delta  -0.0143
MAE better       10/14
RMSE better       7/14

RECENT 6
mean MAE delta   -0.0141
mean RMSE delta  -0.0108
MAE better        4/6
RMSE better       3/6
```

Pooled errors improved, but the predeclared fold-stability gate failed.

**Decision:** not promoted.

### SITE-AWARE SRS / HFA challenger

A raw CFBD site-context audit found complete coverage:

```text
model rows            8,510
parseable site rows   8,510 (100.00%)
neutral-site games      685
non-neutral games     7,825
field                 neutralSite
```

The fixed challenger estimated season-local home-field advantage leakage-safely from prior partitions:

```text
margin ~= rating(home)
          - rating(away)
          + HFA * nonNeutral
```

and replaced only `srsEdge` with `siteAwareSrsMargin`.

Result:

```text
ALL 14
mean MAE delta   -0.0021
mean RMSE delta  -0.0024
MAE better        8/14
RMSE better       8/14

RECENT 6
mean MAE delta   -0.0035
mean RMSE delta  -0.0174
MAE better        4/6
RMSE better       6/6
```

The challenger passed every predeclared promotion condition.

**Decision:** promoted as **Prediction v2**.

Prediction v1 remains preserved as the corrected predecessor benchmark. New game-margin research should compare against Prediction v2 rather than v1.

See `docs/PREDICTION_V2.md` and `docs/PREDICTION_V1_SITE_AWARE_CHALLENGER.md`.

## Challenger policy

The history of v1 established the project rule that a new predictive feature or architecture does not enter the benchmark merely because it is football-plausible, improves pooled averages, or improves one season.

Future work should continue using:

1. identical leakage-safe walk-forward samples;
2. paired MAE and RMSE as primary metrics;
3. winner accuracy as secondary context;
4. per-holdout results, not only pooled averages;
5. special attention to recent holdouts;
6. predeclared promotion rules before inspecting challenger results.

## Drive PPD status

Opponent-adjusted Drive PPD remains **RESEARCH ONLY**. Initial ablation showed useful incremental signal in some formulations, but season-by-season stability was not sufficient to add it to the benchmark.

PPD remains available for team profiles, drive grades, diagnostics, and future prediction challenges without changing the benchmark.
