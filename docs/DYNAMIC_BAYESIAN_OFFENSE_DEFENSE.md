# Dynamic Bayesian Offense/Defense v1

Status: exploratory post-discovery model-family screen. This work does **not** modify the frozen 2026 ATS logistic artifact.

## Research question

Does representing each team with separate evolving offense and defense states add information beyond the existing FULL Prediction-v2 + market ATS logistic model?

Unlike Elo/Glicko/Kalman-strength experiments, this family does not compress a team to one scalar strength. For each metric it maintains separate latent offensive and defensive Gaussian states.

Observation model:

```text
observed metric = fixed center + offense(team) - defense(opponent) + noise
```

A stronger offense raises the expected observation; a stronger defense lowers the opponent observation.

## Predeclared state families

No family below was selected after seeing its result.

- `POINTS_OD`: points scored offense vs points allowed defense
- `YPP_OD`: yards/play offense vs yards/play defense
- `SUCCESS_OD`: success-rate offense vs success-rate defense
- `MULTI_OD`: all three families together

Each single-metric family exports exactly three pregame features:

- home offensive matchup expectation
- away offensive matchup expectation
- combined state/observation uncertainty

`MULTI_OD` concatenates those nine features. Redundant hand-created margin differences are intentionally omitted because a linear/logistic layer can form them from home and away matchup features.

## Frozen state parameters for this screen

Common:

- offseason mean carry: 50%
- all games in a rating period are scored before any result from that period updates state
- current-period updates are computed from a common pre-period snapshot

`POINTS_OD`:

- fixed center: 28 points
- initial state variance: 100
- process variance per rating period: 4
- observation variance: `14^2`
- fixed non-neutral home-field adjustment: 2.5 points, split `+/-1.25` out of the two scoring observations before state update

`YPP_OD`:

- fixed center: 5.5 yards/play
- initial variance: 1.0
- process variance: 0.04
- observation variance: 4.0

`SUCCESS_OD`:

- fixed center: 0.42
- initial variance: 0.01
- process variance: 0.0004
- observation variance: 0.0144

These values are fixed scale-aware priors/noise assumptions, not historical optimizer outputs.

### Yards/play semantic note

`YPP_OD` intentionally uses the repository's existing derived team-game `offensiveYards / offensivePlays` semantics, matching the existing iterative YardsPerPlay family. It does **not** silently switch to the separately frozen Basic Yardage v1 denominator.

## Leakage contract

For every season and rating period:

1. apply process uncertainty drift,
2. generate every current-period pregame O/D signal,
3. only after all signals are recorded, consume the current-period final scores / YPP / success observations,
4. update state for the next rating period.

At season boundaries, latent means are shrunk 50% toward zero and uncertainty is increased.

For the official outer test seasons, every Ridge or logistic calibration model is trained only on eligible seasons strictly earlier than the target season.

## Evaluation contract

To reduce historical selection multiplicity, this family uses one fixed eligibility/betting contract:

- `minGames=3`
- direct ATS threshold `0.575`
- `StandardScaler + LogisticRegression(C=0.5, max_iter=2000, random_state=42)`

Each family is evaluated three ways.

### 1. Standalone margin diagnostic

`StandardScaler + Ridge(alpha=10)` maps only the dynamic O/D state features to final home margin. It is compared with the historical CFBD market on MAE/RMSE.

### 2. Standalone direct ATS

Dynamic O/D state features + the existing seven market/context features predict home-cover probability.

### 3. Primary incremental test

The existing 26-feature FULL ATS logistic baseline is compared with the exact same architecture plus only the predeclared O/D state features.

The script refuses to proceed unless the historical baseline exactly reproduces the already-observed discovery record:

```text
495 bets
265 wins
220 losses
10 pushes
```

For each augmentation it reports pooled ATS/ROI/Brier, 2018-2025 season folds, 2023-2025 results, bet-selection overlap, and added standardized coefficient stability.

## Run

```bash
python -m cfb_analytics.analytics.dynamic_bayesian_offense_defense --overwrite
```

Outputs:

```text
data/processed/market_benchmark/dynamic-bayesian-offense-defense.json
data/processed/market_benchmark/dynamic-bayesian-offense-defense-games.json
```

## Interpretation boundary

2018-2025 outcomes have already been used throughout model discovery. Therefore even a positive result here is exploratory/post-discovery evidence, not untouched confirmation evidence. The committed 2026 ATS logistic model remains frozen regardless of this screen. A worthwhile survivor must become a separately named future/prospective challenger rather than rewriting the frozen baseline.
