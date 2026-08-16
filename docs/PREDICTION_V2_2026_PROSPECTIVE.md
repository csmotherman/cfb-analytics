# Prediction v2 — 2026 Prospective Freeze Workflow

**Status:** PRESEASON DEPLOYMENT CONTRACT  
**Frozen early-prior rule:** `prediction-v2-early-prior-four-game-linear-v1`  
**Prospective feature version:** `prediction-v2-2026-outcome-free-features-v1`  
**Freeze artifact version:** `prediction-v2-2026-prospective-freeze-v1`  
**Guarded pipeline version:** `prediction-v2-2026-prospective-pipeline-v1`

The historical early-season challenger has already passed its predeclared gate. The next job is not more tuning. The job is to preserve a genuinely prospective 2026 test.

This workflow separates four things that must not be conflated:

1. the frozen 19-feature architecture and `1.00/0.75/0.50/0.25/0.00` prior decay;
2. outcome-free 2026 feature materialization from information available strictly before the target partition;
3. the final model coefficients fit once from eligible pre-2026 historical rows;
4. immutable weekly 2026 prediction snapshots created before outcomes are known.

## Why a separate prospective path is required

The historical challenger is an evaluation program. It refits models inside walk-forward folds and its historical row eligibility requires known targets. The historical model feature store is also target-oriented: it repairs authoritative final-score targets and rebuilds score-dependent SRS for completed games. That is correct for backtesting but is not a valid input path for future matchups.

The prospective path therefore does **not** pass fake targets through the historical evaluator. It reconstructs current-season state from strictly earlier completed partitions, takes the upcoming matchup identity/site from the raw games schedule, and applies the already-frozen early-prior blend without consulting a 2026 outcome field.

## 1. Freeze the coefficient artifact once

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

## 2. Run the guarded weekly pipeline

The recommended production entrypoint is the guarded wrapper, not the lower-level feature/scoring commands.

After completed prior-week data and normal derived artifacts are updated, but before any game in the target partition has a result, run:

```bash
python -m cfb_analytics.analytics.prediction_v2_2026_pipeline \
  --model prospective/2026/prediction-v2-2026-frozen.json \
  --week 1 \
  --as-of 2026-08-29T09:00:00-04:00 \
  --features-output prospective/2026/features/week-01.json \
  --audit-output prospective/2026/audits/week-01.json \
  --predictions-output prospective/2026/predictions/week-01.json
```

The guarded pipeline first proves that the raw scored-game history used for current-season site-aware SRS/HFA is the exact same game set as the completed two-team derived history. A raw final score that exists without the corresponding completed derived game—or a derived game without the matching raw final score—causes a hard failure rather than silently changing the SRS sample.

It then materializes the 19-feature rows and scores them with the already-frozen coefficient artifact. All validation and prediction computation happens before the first output file is written.

The pipeline fails closed if:

- the target raw schedule partition already contains a numeric score;
- prior raw score history and completed two-team derived history do not match exactly;
- the model manifest does not match the frozen version, feature list, prior weights, or training-season contract;
- any prospective row contains an outcome-bearing target value;
- any of the 19 frozen features is missing or non-finite;
- a row carries the wrong prospective feature version or `as-of` timestamp;
- a game ID is missing or duplicated;
- a row belongs to a different week;
- any feature, audit, or prediction output path already exists.

The prediction output contains predicted margin and winner only. It does **not** manufacture a win probability from an uncalibrated margin regression.

Games without a complete frozen feature vector are excluded explicitly rather than receiving invented zero values. Inspect every exclusion before treating the snapshot as official.

## Lower-level diagnostic commands

`prediction_v2_2026_features` and the `score` subcommand of `prediction_v2_2026_freeze` remain available for unit tests and forensic debugging. They are not the preferred weekly production entrypoint because the guarded wrapper adds the cross-source history-alignment check and preflights all three immutable outputs together.

## Weekly operating sequence

```text
1. Update/download the raw schedule and completed prior-week data.
2. Rebuild the normal saved derived artifacts for completed partitions only.
3. Run prediction_v2_2026_pipeline for the target week.
4. Inspect the history-alignment result, exclusions, and row counts.
5. Commit/push the feature, audit, and prediction artifacts before kickoff.
6. Do not refit or overwrite anything after results arrive.
```

## Validation contract

The prospective implementation has three dedicated test modules covering:

- the one-time freeze/training-season/model-manifest contract;
- exact 19-feature equivalence between the outcome-free builder and frozen historical blend math on the same state;
- target leakage rejection, immutable writes, offset-aware timestamps, and exact history-sample alignment.

Before creating the official freeze artifact in a new environment, run the dedicated tests and then the full suite with both development and model dependencies installed.

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
