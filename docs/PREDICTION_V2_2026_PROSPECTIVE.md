# Prediction v2 — 2026 Prospective Freeze Workflow

**Status:** PRESEASON DEPLOYMENT CONTRACT  
**Frozen early-prior rule:** `prediction-v2-early-prior-four-game-linear-v1`  
**Prospective feature version:** `prediction-v2-2026-outcome-free-features-v1`  
**Freeze artifact version:** `prediction-v2-2026-prospective-freeze-v1`

The historical early-season challenger has already passed its predeclared gate. The next job is not more tuning. The job is to preserve a genuinely prospective 2026 test.

This workflow separates four things that must not be conflated:

1. the frozen 19-feature architecture and `1.00/0.75/0.50/0.25/0.00` prior decay;
2. outcome-free 2026 feature materialization from information available strictly before the target partition;
3. the final model coefficients fit once from eligible pre-2026 historical rows;
4. immutable weekly 2026 prediction snapshots created before outcomes are known.

## Why a separate prospective path is required

The historical challenger is an evaluation program. It refits models inside walk-forward folds and its historical row eligibility requires known targets. The historical model feature store is also target-oriented: it repairs authoritative final-score targets and rebuilds score-dependent SRS for completed games. That is correct for backtesting but is not a valid input path for future matchups.

The prospective path therefore does **not** pass fake targets through the historical evaluator. It reconstructs current-season state from strictly earlier completed partitions, takes the upcoming matchup identity/site from the raw games schedule, and applies the already-frozen early-prior blend without consulting a 2026 outcome field.

## 1. Freeze the coefficient artifact

A prospective season needs one final coefficient set. The 2026 freeze fits the already-selected 19-feature architecture once on the complete eligible early-prior corpus from:

```text
2015 2016 2017 2018 2019 2022 2023 2024 2025
```

That exact season list is hard-coded. If the available early-prior season map changes, the freeze command fails rather than silently changing the training sample.

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

Using all of these pre-2026 rows for the final deployment fit is not another model-selection experiment. The architecture, features, carryover weights, and evaluation gate were already selected. No 2026 outcome may be used to alter the fit after this artifact is frozen.

If the output already exists, the command fails. There is intentionally no overwrite flag.

`data/processed/**` is gitignored. The recommended `prospective/2026/` path is outside that ignored tree so the freeze artifact can be committed and timestamped in Git. That commit is the evidentiary boundary for the coefficient set.

## 2. Materialize outcome-free weekly features

Before any game in the target partition has a result, materialize the upcoming feature rows:

```bash
python -m cfb_analytics.analytics.prediction_v2_2026_features \
  --week 1 \
  --as-of 2026-08-29T09:00:00-04:00 \
  --output prospective/2026/features/week-01.json
```

The materializer uses:

- raw 2026 games schedule rows for target `gameId`, home/away orientation, and neutral-site status;
- saved derived team-game rows from partitions strictly before the target week for current Iterative and Football Mechanisms state;
- saved Sandbox component rows from partitions strictly before the target week for current MWDR state;
- authoritative raw final scores and site flags from strictly earlier partitions for current site-aware SRS/HFA state;
- final 2025 state for the frozen adjacent-season prior.

It then applies the unchanged four-game blend at team-state level and reconstructs the same 19 Prediction-v2 matchup features.

The target partition is rejected if its raw games file already contains a numeric score. This is intentional: a weekly snapshot created after outcomes begin is not prospective evidence.

The feature file is created once using exclusive-create semantics. A companion `week-01.audit.json` records schedule coverage, prior-history row counts, and exclusions. Games without the complete frozen feature vector are excluded explicitly rather than receiving invented zero values.

A unit-level equivalence contract compares the outcome-free builder with the historical frozen `_build_variant_row` on the same synthetic state and requires all 19 feature values to match to numerical tolerance. The only intended difference is that prospective rows contain no target fields.

## 3. Score and freeze the weekly predictions

Score the just-created feature rows with the already-frozen coefficient artifact:

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

Commit the feature audit and prediction snapshot before the games it covers. Do not regenerate a snapshot after outcomes are observed. Corrections, if ever necessary, should be additive and explicitly documented rather than replacing the original evidence.

## Weekly operating sequence

```text
1. Update/download the raw schedule and completed prior-week data.
2. Rebuild the normal saved derived artifacts for completed partitions only.
3. Materialize the target week's outcome-free feature file + audit.
4. Score with the frozen 2026 coefficient artifact.
5. Inspect exclusions and row counts.
6. Commit/push the feature audit and prediction snapshot before kickoff.
7. Do not refit or overwrite anything after results arrive.
```

## Non-negotiable 2026 rules

- Do not change the four-game prior weights after seeing 2026 outcomes.
- Do not change the 19-feature architecture after seeing 2026 outcomes and still call the result the same prospective model.
- Do not refit the frozen coefficient artifact during the season.
- Do not use the target game's score, PBP, drives, or derived team-game state when creating its features.
- Do not pass dummy targets through the historical evaluator as a shortcut.
- Do not overwrite feature files, audits, or weekly prediction snapshots.
- Do not backfill a pregame snapshot after a game starts and count it as prospective evidence.
- Keep experimental 2026 models in separate versioned artifacts; never silently mutate the frozen benchmark.

At the end of the season, evaluate the committed frozen predictions exactly as they existed pregame. That is the evidence that can support a future Prediction-v3 promotion decision.
