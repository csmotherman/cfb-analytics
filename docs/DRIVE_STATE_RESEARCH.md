# Drive-State Research Contract

**Status:** RESEARCH ONLY  
**Version:** `drive-state-research-v2-raw-drive-outcomes-regulation`

## Why this exists

The third-down residual experiments found that special team-specific third-down skill is either absent or too small/unstable to justify carrying as a permanent simulator rating. Situational football state still matters, but it should first enter the simulator as part of the possession mechanism rather than as a collection of noisy permanent team ratings.

The first drive-state prototype exposed two important source-contract failures:

1. derived drive `start*` fields were based on the first source event in a drive group, which was often a kickoff, return, timeout, or penalty rather than the first offensive state;
2. subtracting derived or raw start/end offense-score fields did not reconcile cleanly enough to define possession points.

The dedicated raw CFBD drive endpoint was substantially cleaner for possession identity and start state, and its direct `driveResult` label tracked football outcomes much better than reconstructed score deltas.

Version 2 therefore models:

```text
raw drive-start state + pregame team quality -> categorical drive outcome
```

## 2023 forensic evidence that motivated v2

The 2023 raw-drive audit found:

- 19,060 raw drive rows and 19,060 derived drive rows;
- every derived drive ID matched a raw drive ID;
- all 18,828 validated derived possessions matched a raw drive;
- only 51 validated possessions disagreed on raw vs derived ownership;
- raw drive score deltas had no negatives, but game-level reconstruction still matched final scores in only 70.14% of regulation-only games;
- `driveResult` was highly coherent with football semantics: PUNT was overwhelmingly `(0,0)`, TD overwhelmingly `(7,0)/(6,0)/(8,0)`, FG overwhelmingly `(3,0)`, INT/FUMBLE overwhelmingly no offensive score, and return-touchdown labels overwhelmingly opponent scores.

The conclusion is deliberately conservative: use raw drive **start state and direct outcome label**, but do not use raw score deltas as a training target.

## Leakage contract

Each research row is one derived-validated possession whose raw and derived offense/defense identities agree.

Predictors may use only:

- information present on the raw drive record at the start of that possession;
- team-quality states snapshotted before the current weekly partition.

Current-drive outcomes, later drives, game-final scores, and future partitions are never predictors.

## Possession eligibility

A v2 row requires:

- derived `isPossessionDrive == True`;
- derived `driveValidationStatus == PASS`;
- non-null offense and defense;
- exact raw/derived offense agreement;
- exact raw/derived defense agreement;
- a matching pregame football-mechanism matchup row.

The default v2 corpus excludes overtime possessions. College overtime is structurally different enough that it should receive a separate model later rather than be mixed into the regulation possession process.

`--include-overtime` exists only for research inspection.

## Pregame team quality

The materializer reuses saved `football_mechanisms/.../matchups.json` files. Those states are cumulative through the prior partition only.

For the offense, v2 retains only offensive quality:

- yards per possession;
- success rate;
- explosive rate;
- scoring-opportunity rate;
- points per opportunity;
- early-down success;
- giveaway rate.

For the opposing defense, v2 retains only defensive quality:

- yards per possession allowed;
- success rate allowed;
- explosive rate allowed;
- scoring-opportunity rate allowed;
- points per opportunity allowed;
- early-down success allowed;
- takeaway rate.

This avoids feeding irrelevant same-team defensive fields into an offensive possession model.

## Raw drive-start state

The authoritative start state now comes directly from the raw CFBD drive record:

- start period;
- start clock seconds;
- start yards to goal;
- start offense-minus-defense score margin;
- start score state (leading/tied/trailing);
- home/away offense indicator.

`startDown` and `startDistance` are intentionally removed from the drive-level contract. They were artifacts of trying to recover the first offensive snap and are not necessary for the initial possession-outcome model.

## Target

The target is the raw drive `driveResult`, retained exactly as `targetDriveResult` and also collapsed into `targetOutcomeFamily`:

```text
TOUCHDOWN
FIELD_GOAL
PUNT
TURNOVER
DOWNS
MISSED_FIELD_GOAL
PERIOD_END
RETURN_TOUCHDOWN
SAFETY
OTHER
```

Examples:

- `TD` -> `TOUCHDOWN`
- `FG` -> `FIELD_GOAL`
- `INT`, `FUMBLE` -> `TURNOVER`
- `MISSED FG`, `BLOCKED FG` -> `MISSED_FIELD_GOAL`
- `INT TD`, `FUMBLE RETURN TD`, `PUNT RETURN TD`, etc. -> `RETURN_TOUCHDOWN`
- `SF` -> `SAFETY`

Raw start/end score deltas are deliberately omitted from the v2 research rows so they cannot accidentally be reused as labels.

## Why categorical outcomes first

The raw-drive forensic table showed that drive-result categories carry much cleaner football meaning than reconstructed numeric score deltas. The natural next statistical challengers are therefore categorical possession-outcome models rather than ordinary least squares on drive points.

The immediate workflow is:

```text
materialize v2 -> audit class/coverage distribution -> choose model -> walk-forward validate -> aggregate possessions into games -> compare with Prediction v1
```

Likely first challengers include multinomial logistic regression and a tree-based probability model, evaluated with proper scoring rules and calibration. No model is promoted without leakage-safe out-of-sample evidence.

## Commands

Validate one season first:

```bash
python -m cfb_analytics.analytics.drive_state_research --season 2023
```

After that schema/audit is accepted:

```bash
python -m cfb_analytics.analytics.drive_state_research --all
```

Optional overtime inspection:

```bash
python -m cfb_analytics.analytics.drive_state_research --season 2023 --include-overtime
```

This materializer reads existing raw drives, existing derived drive validation, and existing pregame football-mechanism matchups. It does not regenerate profiles, snapshots, or canonical play-by-play.

## Prediction v1 and current simulator

Prediction v1 remains locked and unchanged.

The existing historical simulator remains unchanged. Drive-state v2 is an independent mechanistic research challenger. It may eventually replace the simulator's crude points-per-possession layer only if it demonstrates stable out-of-sample value.
