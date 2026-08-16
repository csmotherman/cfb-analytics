# Third-Down Residual Skill Research

**Status:** RESEARCH ONLY  
**Version:** `third-down-residual-skill-v1-partial-pooling`

## Question

The first situational-prediction experiment asked whether raw cumulative situation rates improved game-margin prediction. That formulation was intentionally rejected as a final design because raw rates confound general team quality, opponent quality, exact situation difficulty, and sample size.

This experiment asks a narrower question first:

> After controlling for the difficulty of the actual third-down situations and broad pregame team quality, does a team's excess third-down conversion ability persist into future games?

If the answer is no, there is little reason to put a special third-down skill term into a game simulator. If the answer is yes, that latent skill can become one mechanism in a later drive/game model.

## Data grain

One row per eligible third-down snap from validated possession drives.

The conversion target uses the same first-down evidence union already used by the situational split research:

- yards gained at least distance to go; or
- explicit offensive touchdown; or
- the next clean offensive snap resets to first down.

Only information available before the current weekly partition is used for team-quality covariates.

## Context model

The baseline estimates third-down conversion probability from:

- **exact yards to go**, represented with a continuous piecewise-linear spline basis rather than short/medium/long bins;
- yards to goal;
- score margin;
- quarter;
- score state;
- goal-to-go state;
- broad pregame offense success;
- broad pregame defense success allowed.

Broad offense/defense success rates are shrunk toward the pregame league rate with 100 pseudo-plays. Teams with no current-season history therefore receive the league prior rather than being dropped.

## Residual team layer

The challenger adds season-reset offense and defense-allowed residual effects:

```text
logit(P(convert))
  = context_logit
  + offense_residual(team)
  + defense_allow_residual(opponent)
```

The residual effects are estimated with ridge-penalized logistic likelihood, which is equivalent to mean-zero Gaussian partial pooling at the MAP level.

Default penalty:

```text
lambda = 20
prior SD ~= 1 / sqrt(20) = 0.224 log-odds
```

This means small samples remain close to zero automatically. There is **no minimum-attempt eligibility threshold** for the residual effect and no test play is discarded because a team has too little history.

The residual layer resets each season. Prior seasons train the global context model, but a team's special situational deviation must re-establish itself from current-season evidence.

## Validation

The persistence test is one-partition-ahead and leakage safe.

For each outer test season:

1. Train the context model on all earlier seasons plus earlier partitions of the current season.
2. Estimate current-season residual offense/defense effects using only earlier current-season third downs.
3. Predict every third-down attempt in the next partition.
4. Add that partition to history only after it is scored.

Default outer seasons:

```text
2021, 2022, 2023, 2024, 2025
```

Primary metrics:

- log loss;
- Brier score.

Secondary context:

- classification accuracy;
- predicted conversion rate vs observed conversion rate.

The important quantity is the paired difference between the context-only baseline and the residual-skill challenger on the exact same plays.

## Decision rule

Do **not** promote a third-down residual effect because it is football-plausible or because one season improves.

Evidence worth carrying forward should show:

- negative log-loss delta in most outer seasons;
- negative Brier delta in most outer seasons;
- negative pooled deltas;
- reasonable calibration;
- no dependence on dropping sparse teams or tiny samples.

If that test passes, the next step is not to add the raw residual directly to Prediction v1. The next step is to translate the persistent skill into a drive-continuation / expected-points mechanism for a semi-mechanistic simulator.

## Commands

Generate the compact cached third-down attempt files from already-canonicalized plays and existing pregame states:

```bash
python -m cfb_analytics.analytics.third_down_residual_skill --materialize --all
```

Then run the persistence test from the cached attempts:

```bash
python -m cfb_analytics.analytics.third_down_residual_skill --evaluate
```

Model dependencies are optional:

```bash
pip install -e ".[models]"
```

## Relationship to Prediction v1

Prediction v1 remains unchanged and locked as the macro game-margin research benchmark. This work is a mechanism-discovery experiment, not a benchmark mutation.
