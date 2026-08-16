# Prediction Model v2 Research Benchmark Contract

**Status:** LOCKED RESEARCH BENCHMARK  
**Version:** `prediction-v2-site-aware-srs-hfa-v1`  
**Purpose:** forward reference model for future game-margin challengers after authoritative-target repair and site-aware SRS promotion. This is a research benchmark, not a claim of production optimality.

## What changed from Prediction v1

Prediction v2 keeps the corrected Prediction-v1 VOLUME + OLS architecture and changes exactly one feature:

```text
Prediction v1
  srsEdge

Prediction v2
  siteAwareSrsMargin
```

All other model terms, target definitions, training weights, outer-season protocol, and eligibility rules remain unchanged.

## Feature contract

Prediction v2 uses 19 features:

```text
ITERATIVE RATINGS
  home_iterativeSuccessEdge
  away_iterativeSuccessEdge
  home_iterativeExplosiveEdge
  away_iterativeExplosiveEdge
  home_iterativeYardsPerPlayEdge
  away_iterativeYardsPerPlayEdge
  home_iterativeYardsPerPossessionEdge
  away_iterativeYardsPerPossessionEdge
  home_iterativeFinishingEdge
  away_iterativeFinishingEdge
  home_iterativeFieldPositionEdge
  away_iterativeFieldPositionEdge

SITE-AWARE SRS
  siteAwareSrsMargin

MWDR
  home_MWDR_OffenseEdge
  home_MWDR_DefenseEdge
  mwdrXExpectedPossessions

VOLUME ENGINE
  successVolumeEdge
  explosiveVolumeEdge
  turnoverVolumeEdge
```

## Site-aware SRS / HFA

Within each season and before each partition, fit strictly prior games to:

```text
margin ~= rating(home)
          - rating(away)
          + HFA * nonNeutral
```

where `nonNeutral=1` for true home/away games and `0` for neutral-site games.

The feature used by Prediction v2 is:

```text
siteAwareSrsMargin
  = siteAwareSrsEdge
    + siteAwareSrsHfaBefore * nonNeutral
```

The current game's result is never used in its own SRS or HFA estimate. Team ratings are centered within disconnected schedule components. Site coverage is complete for all 8,510 corrected model rows.

## Target contract

Targets come only from authoritative raw CFBD `games.json` final scores:

```text
target_homeScore
target_awayScore
target_margin
target_homeWin
```

The corrected corpus passes exact reconciliation for all 8,510 model rows.

## Estimator / training contract

- ordinary least squares;
- signed final home margin target;
- equal weight by game;
- all prior available seasons for each outer holdout;
- identical common sample for ablations;
- minimum prior games 3 and 4 for benchmark evaluation;
- 2020 omitted from the historical corpus;
- season reset preserved;
- regular-season partitions ordered before postseason partitions;
- no current/future game information in pregame features.

## Promotion evidence

Prediction v2 was promoted from the fixed site-aware challenger under a predeclared gate.

```text
ALL 14 FOLDS
Prediction v2 - corrected Prediction v1
  mean MAE delta     -0.0021
  mean RMSE delta    -0.0024
  winner delta       +0.13 pp
  MAE better           8/14
  RMSE better          8/14

RECENT 6 FOLDS (2023-2025 x min3/min4)
  mean MAE delta     -0.0035
  mean RMSE delta    -0.0174
  winner delta       +0.38 pp
  MAE better           4/6
  RMSE better          6/6
```

The challenger passed all predeclared broad and recent MAE/RMSE requirements.

The improvement is **small**. Prediction v2 is promoted because it adds a football-valid, fully observed context variable, preserves model size and sample, corrects a structural limitation of legacy SRS, and met the predefined OOS stability gate. It should not be described as a large accuracy jump.

## Pre-promotion alternatives that were rejected

After the authoritative target correction:

```text
LEAN pruning
  recent MAE delta   +0.0205
  recent RMSE delta  +0.0217
  -> not promoted

SYMMETRIC / net model
  all-14 MAE delta   -0.0246
  all-14 RMSE delta  -0.0143
  recent MAE delta   -0.0141
  recent RMSE delta  -0.0108
  recent RMSE wins     3/6
  -> failed stability gate; not promoted
```

Do not reopen those exact formulations by tuning against the already-inspected holdouts.

## Benchmark policy moving forward

Prediction v2 is now the comparison baseline for new game-margin research.

A challenger does not replace it because it is football-plausible or improves pooled error. Future work should preserve:

1. identical leakage-safe samples;
2. paired MAE and RMSE as primary metrics;
3. winner accuracy as secondary context;
4. per-season results;
5. recent-era stability;
6. predeclared promotion rules before inspecting challenger holdout results.

If a future challenger earns promotion, create Prediction v3 rather than silently mutating v2.

## 2026 prospective validation

Historical 2023–2025 folds have now been inspected repeatedly during development. They should not be treated as pristine unseen evidence indefinitely.

For 2026, freeze Prediction v2 before evaluating outcomes and save each weekly pregame prediction. Do not retune v2 against 2026 results during the season if the goal is to use 2026 as a prospective validation year.

## Next research priority

The most important remaining product/model limitation is early-season coverage. Current benchmark evaluation requires 3 or 4 prior games for both teams.

The next major research family should therefore be **previous-season / preseason priors with controlled decay into current-season evidence**, evaluated separately for Weeks 1–2, Weeks 3–4, and Week 5+.

Before choosing a carryover strength, run the saved-data-only feasibility audit in `docs/PREDICTION_V2_EARLY_PRIOR_AUDIT.md`. It reconstructs final previous-season Iterative, Football Mechanisms, MWDR, and site-aware SRS state and measures actual early-game coverage. Only immediately adjacent historical seasons are allowed; 2021 does not silently reach across the missing 2020 season to use 2019.

That work must be treated as a new information-source challenger to Prediction v2, not as hidden retuning of the site-aware benchmark.
