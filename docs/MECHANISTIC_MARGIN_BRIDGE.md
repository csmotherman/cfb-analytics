# Mechanistic Margin Bridge

**Status:** RESEARCH ONLY  
**Version:** `mechanistic-margin-bridge-v1-neutral-drive-stack`

## Purpose

The selected possession-outcome engine is the validated FLAT FULL 9-class drive model. The next question is not whether it predicts possessions well; that has already been established. The next question is whether the drive model carries useful **game-level matchup information** beyond Prediction v1.

This module is deliberately cheaper than a full possession-by-possession simulator. It builds a standardized, leakage-safe pregame drive signal first, then performs a recent-outer stacking screen before the project pays for more simulator mechanics.

Prediction v1 remains unchanged.

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

The game bridge then uses the existing leakage-safe expected possessions per team from Football Mechanisms:

```text
mechanistic expected home score
mechanistic expected away score
mechanistic expected home margin
mechanistic expected total
```

This is a standardized pregame bridge, not yet a full state-transition simulator.

## Runtime / cache contract

Runtime is intentionally bounded.

For each requested outer season, the module fits exactly **one** converged FULL drive-outcome model using only earlier seasons. The resulting per-game mechanistic features are cached under:

```text
data/processed/derived/mechanistic_margin_bridge/season=YYYY/
```

Later runs reuse the cached game features unless `--refresh-bridge` is passed.

The cache is invalidated by the bridge version, drive-outcome model version, Drive State Research version, Football Mechanisms version, or model-feature-store version.

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

For each recent outer season, Prediction v1 is refit on all prior eligible seasons exactly as in the existing research harness.

The bridge does **not** immediately append the mechanistic margin to that same all-history OLS, because doing that properly would require leakage-safe mechanistic features for every earlier training season and therefore many additional expensive drive-model fits.

Instead, the first incremental test uses leakage-safe stacking across already-out-of-sample recent seasons:

```text
BASE  = Prediction v1 margin
RECAL = prior outer-season BASE margin recalibration
STACK = RECAL + mechanistic margin
```

The scientific comparison is:

```text
STACK vs RECAL
```

not STACK vs raw BASE. This prevents simple temporal recalibration of Prediction v1 from being incorrectly credited to the mechanistic signal.

## Fast screening workflow

Start with two outer seasons so only two drive models are fit:

```bash
python -m cfb_analytics.analytics.mechanistic_margin_bridge --test-seasons 2023,2024
```

That produces one stacking holdout (2024) for minimum-prior-games 3 and 4.

If the mechanistic signal looks useful, extend to 2025:

```bash
python -m cfb_analytics.analytics.mechanistic_margin_bridge --test-seasons 2023,2024,2025
```

The 2023 and 2024 bridge features are reused from cache, so only the new 2025 drive model must be fit.

To precompute/reuse bridge features without running the stack:

```bash
python -m cfb_analytics.analytics.mechanistic_margin_bridge --test-seasons 2023,2024 --prepare-only
```

## Promotion rule

This is a screen, not a Prediction v2 lock.

A mechanistic game signal earns broader historical integration only if `STACK` improves both MAE and RMSE versus `RECAL` with stable direction across the available recent outer tests. Winner accuracy is secondary.

If the signal fails this screen, keep Prediction v1 as the margin model and use the drive model only for future explanatory/simulation work.

If the signal passes, the next step is to materialize a broader leakage-safe mechanistic feature history and perform a full same-sample Prediction-v1 ablation before changing the main prediction contract.

## What this is not

This is not yet a full regulation simulator. It does not sequence possessions, sample next field position, decrement the game clock, or model overtime.

Those mechanisms should be built only after the cheap game-level bridge shows that the validated drive probabilities contain useful information at the game level.