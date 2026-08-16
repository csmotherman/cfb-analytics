# Mechanistic Margin Bridge

**Status:** SCREENED — NOT PROMOTED TO PREDICTION  
**Version:** `mechanistic-margin-bridge-v1-neutral-drive-stack-batched`

## Purpose

The selected possession-outcome engine is the validated FLAT FULL 9-class drive model. This bridge tested whether those drive probabilities carry useful **game-level matchup information** beyond Prediction v1.

The bridge was intentionally cheaper than a full possession-by-possession simulator: standardized pregame drive probabilities were converted to football-valid expected points, scaled by leakage-safe expected possessions, and then evaluated as a recent-outer stacking signal.

Prediction v1 remained unchanged throughout the experiment.

## Neutral possession bridge

For each team in a pregame matchup, the validated drive model is evaluated at the same standardized football state:

```text
period              = Q1
clock                = 7:30
score                = tied
start yards to goal  = 66.277
```

The 66.277 yards-to-goal value corresponds to the locked Field Position v1 corpus mean possession start of own 33.723.

The only matchup-specific inputs are the leakage-safe pregame offense and opposing-defense quality values plus the home-offense indicator. This isolates team/matchup quality rather than leaking observed in-game field position, score, or clock.

## Football-valid point mapping

The bridge never uses raw drive scoreboard deltas. Those failed the earlier drive-score reconciliation audit.

Predicted outcome probabilities are converted to scoreboard expectation using fixed football values:

```text
TOUCHDOWN          +7 offense
FIELD_GOAL         +3 offense
RETURN_TOUCHDOWN   +7 opponent
SAFETY             +2 opponent
all other classes   0
```

For a home offensive possession:

```text
net expected points = expected home offensive points
                    - expected opponent return/safety points
```

The away possession is symmetric.

The game bridge then uses the existing leakage-safe expected possessions per team from Football Mechanisms to create:

```text
mechanistic expected home score
mechanistic expected away score
mechanistic expected home margin
mechanistic expected total
```

This is a standardized pregame bridge, not a full state-transition simulator.

## Runtime / cache contract

For each requested outer season, the module fits exactly one converged FULL drive-outcome model using only earlier seasons. All standardized home/away possession rows for that season are scored in one batched `predict_proba` call.

The resulting per-game mechanistic features are cached under:

```text
data/processed/derived/mechanistic_margin_bridge/season=YYYY/
```

Later runs reuse the cached game features unless `--refresh-bridge` is passed.

No profile rebuild, snapshot rebuild, PBP replay, or hierarchy fitting is required.

## Prediction-v1 comparison

The game-level screen uses the frozen Prediction v1 feature contract:

```text
Iterative + SRS
MWDR
MWDR x expected possessions
success volume edge
explosive volume edge
turnover volume edge
```

The incremental test uses leakage-safe stacking across already-out-of-sample recent seasons:

```text
BASE  = Prediction v1 margin
RECAL = prior outer-season BASE margin recalibration
STACK = RECAL + mechanistic margin
```

The scientific comparison is `STACK vs RECAL`, not STACK vs raw BASE. This prevents simple temporal recalibration of Prediction v1 from being incorrectly credited to the mechanistic signal.

## Quick-screen result

The two-season bridge materialization created cached 2023 and 2024 mechanistic game features. The stacking holdout was 2024, evaluated at both minimum-prior-games thresholds used by Prediction v1 research.

```text
min3 2024
  BASE MAE        12.228
  RECAL MAE       12.220
  STACK MAE       12.252   (+0.033 vs RECAL)
  RMSE delta                +0.010
  Winner delta              -0.17 pp
  MECH standalone MAE       12.804

min4 2024
  BASE MAE        12.377
  RECAL MAE       12.388
  STACK MAE       12.412   (+0.025 vs RECAL)
  RMSE delta                +0.012
  Winner delta              +0.79 pp
  MECH standalone MAE       12.911

SCREEN DECISION
  STACK vs RECAL MAE better   0/2
  STACK vs RECAL RMSE better  0/2
  mean MAE delta             +0.0288
  mean RMSE delta            +0.0110
```

The mechanistic margin failed the predeclared gate: it worsened both MAE and RMSE in both min-games screens. The standalone mechanistic margin was also clearly weaker than Prediction v1 on this holdout.

## Decision

Do **not** add the mechanistic neutral-drive margin to Prediction v1 and do not spend additional compute extending this exact bridge to 2025 or to a broader historical stack.

The result does not invalidate the possession-level drive model. The FLAT FULL drive-outcome model remains a validated possession-probability research engine. What failed is the specific attempt to collapse one standardized neutral-drive expectation into an incremental pregame game-margin feature.

Current modeling decision:

```text
MAIN GAME MARGIN MODEL
  -> keep Prediction v1 unchanged

DRIVE OUTCOME MODEL
  -> keep for possession-level probability research
  -> keep available for explanatory / simulator work
  -> do not use this neutral-drive bridge as a Prediction-v2 feature
```

## What comes next

Do not force a full regulation simulator merely to rescue the failed stacking feature. Future simulator work should have a distinct purpose such as calibrated score distributions, game-flow explanation, or state-dependent scenario analysis.

If the project revisits game-level mechanistic prediction, it should be a materially different experiment rather than more tuning of this neutral-state bridge. Examples include explicitly integrating distributions over starting field position/state or modeling true possession transitions, with a new predeclared validation gate.

The cached 2023/2024 bridge files can remain as reproducible research artifacts; there is no need to regenerate them.