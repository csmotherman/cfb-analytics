# Prediction v2 — 2026 Prospective Freeze Workflow

**Status:** PRESEASON DEPLOYMENT CONTRACT  
**Frozen early-prior rule:** `prediction-v2-early-prior-four-game-linear-v1`  
**Freeze artifact version:** `prediction-v2-2026-prospective-freeze-v1`

The historical early-season challenger has already passed its predeclared gate. The next job is not more tuning. The job is to preserve a genuinely prospective 2026 test.

This workflow separates three things that must not be conflated:

1. the frozen feature architecture and `1.00/0.75/0.50/0.25/0.00` prior decay;
2. the final model coefficients fit once from eligible pre-2026 historical rows;
3. immutable weekly 2026 prediction snapshots created before outcomes are known.

## Why a separate freeze step is required

The historical challenger is an evaluation program. It refits models inside walk-forward folds and its historical row eligibility requires known targets. That is correct for backtesting but is not a sufficient production contract for future games.

A prospective season needs one final coefficient set. The 2026 freeze therefore fits the already-selected 19-feature architecture once on the complete eligible early-prior corpus from:

```text
2015 2016 2017 2018 2019 2022 2023 2024 2025
```

That exact season list is hard-coded. If the available early-prior season map changes, the freeze command fails rather than silently changing the training sample.

Using all of these pre-2026 rows for the final deployment fit is not another model-selection experiment. The architecture, features, carryover weights, and evaluation gate were already chosen before this final fit. No 2026 outcome may be used to alter the fit after the artifact is frozen.

## Freeze the coefficient artifact

Run this before using any 2026 result as development evidence:

```bash
python -m cfb_analytics.analytics.prediction_v2_2026_freeze freeze \
  --output prospective/2026/prediction-v2-2026-frozen.json
```

The command:

- rebuilds the passing historical early-prior datasets from saved artifacts;
- requires the exact predeclared pre-2026 training-season set;
- fits the 19-feature model once;
- records model, benchmark, feature, prior-weight, training-row, and version metadata;
- creates the JSON file using exclusive-create semantics.

If the output already exists, the command fails. There is intentionally no overwrite flag.

`data/processed/**` is gitignored in this repository. The recommended `prospective/2026/` path is outside that ignored tree so the freeze artifact can be committed and timestamped in Git.

After freezing, commit the artifact. That commit is the evidentiary boundary for the 2026 coefficient set.

## Weekly scoring contract

The scorer consumes already-materialized, outcome-free 2026 rows containing the exact 19 Prediction-v2 features.

```bash
python -m cfb_analytics.analytics.prediction_v2_2026_freeze score \
  --model prospective/2026/prediction-v2-2026-frozen.json \
  --features prospective/2026/features/week-01.json \
  --output prospective/2026/predictions/week-01.json \
  --week 1 \
  --as-of 2026-08-29T09:00:00-04:00
```

The scorer fails if:

- a row is not season 2026;
- any target/outcome field has a non-null value;
- any of the 19 frozen features is missing or non-finite;
- a game ID is missing or duplicated;
- a row belongs to a different week than the requested snapshot;
- the model manifest does not match the exact frozen version/features/weights;
- the output snapshot path already exists.

The output contains predicted margin and winner only. It does **not** manufacture a win probability from an uncalibrated margin regression.

Commit each weekly prediction snapshot before the games it covers. Do not regenerate a snapshot after outcomes are observed. Corrections, if ever necessary, should be additive and explicitly documented rather than replacing the original evidence.

## Remaining production dependency

The freeze/scoring contract deliberately does not solve one separate problem: materializing future 2026 early-prior feature rows without requiring historical target fields.

The current historical challenger builds the correct blended team state, but its evaluation path ends by requiring `target_margin` and `target_homeWin`. Future games do not have those values. Passing dummy targets through that gate would make the production pipeline brittle and would blur the leakage boundary.

Therefore the next implementation step is a dedicated outcome-free 2026 feature materializer that reuses the same frozen blend mathematics and proves historical equivalence to the challenger feature vector. Until that equivalence test exists, do not use fake targets as an adapter.

## Non-negotiable 2026 rules

- Do not change the four-game prior weights after seeing 2026 outcomes.
- Do not change the 19-feature architecture after seeing 2026 outcomes and still call the result the same prospective model.
- Do not refit the frozen coefficient artifact during the season.
- Do not overwrite weekly snapshots.
- Do not backfill a pregame snapshot after a game starts and count it as prospective evidence.
- Keep experimental 2026 models in separate versioned artifacts; never silently mutate the frozen benchmark.

At the end of the season, evaluate the committed frozen predictions exactly as they existed pregame. That is the evidence that can support a future Prediction-v3 promotion decision.
