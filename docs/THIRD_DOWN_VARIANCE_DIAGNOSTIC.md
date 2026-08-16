# Third-Down Residual Variance Diagnostic

**Status:** RESEARCH ONLY  
**Version:** `third-down-residual-variance-v1-nested-predictive-shrinkage`

## Why this exists

The first latent third-down residual experiment used one fixed ridge penalty (`lambda = 20`) for both offense and defense effects. It failed cleanly out of sample: the residual challenger worsened log loss and Brier score in every 2021-2025 outer season.

That result is strong evidence against a stable special third-down skill layer, but one final diagnostic is justified before closing the question: allow the data to decide how much residual variance it supports, and let offense and defense have different amounts of shrinkage.

This diagnostic does **not** search the outer test season for a winning penalty. Penalty selection is nested and uses only earlier validation seasons.

## Statistical question

After controlling for exact third-down difficulty and broad pregame team quality:

> Is there a repeatable offense-specific or defense-specific third-down residual that improves prediction of future third-down outcomes?

The base context model remains the same as the prior experiment. The residual layer is:

```text
logit(P(convert))
  = context_logit
  + offense_residual(team)
  + defense_allow_residual(opponent)
```

but the two residual priors are now allowed to differ:

```text
offense_residual ~ Normal(0, tau_off^2)
defense_residual ~ Normal(0, tau_def^2)

lambda_off = 1 / tau_off^2
lambda_def = 1 / tau_def^2
```

Large `lambda` means strong shrinkage and very little supported special situational variance. Small `lambda` allows larger team-specific deviations.

## Penalty grid

Default grid:

```text
2, 5, 20, 100, 500, 5000
```

Equivalent prior standard deviations on the log-odds scale are approximately:

```text
0.707, 0.447, 0.224, 0.100, 0.045, 0.014
```

The wide grid is intentional. If the data repeatedly chooses the strongest shrinkage, that is meaningful evidence that the residual variance is effectively collapsing toward zero.

## Nested selection

For every outer season, offense and defense penalties are selected using only earlier validation seasons.

Example for outer 2023:

```text
inner validation: 2016, 2017, 2018, 2019, 2021, 2022
outer test:       2023
```

The outer 2023 plays are never used to choose `lambda_off` or `lambda_def`.

Selection criterion:

1. pooled inner-season log loss;
2. pooled inner-season Brier score as a tie-breaker;
3. stronger shrinkage if scores are numerically tied.

This prevents us from manufacturing a third-down effect by tuning directly against the seasons we report as evidence.

## Outer models

Each untouched outer season evaluates four models on the exact same third-down attempts:

```text
BASELINE
context model only

OFF only
context + offense residual

DEF only
context + defense residual

BOTH
context + offense residual + defense residual
```

The offense and defense penalties used in those models were chosen from prior validation seasons only.

Primary metrics:

- log loss;
- Brier score.

Secondary context:

- classification accuracy.

## Decision interpretation

Evidence for a real situational-skill layer would require repeatable outer-season improvement, not merely a finite selected penalty.

Strong evidence **against** carrying special third-down skill forward would look like one or more of the following:

- offense or defense repeatedly selects very large penalties;
- offense-only fails to improve future-play proper scores;
- defense-only fails to improve future-play proper scores;
- the combined model fails to improve most outer seasons;
- pooled outer log loss and Brier score are non-negative relative to baseline.

If that happens, the simulator should still use third-down **context** heavily, but not a persistent team-specific "clutch third-down" rating.

## Relationship to the future simulator

This experiment separates two concepts that should not be confused:

1. **football-state difficulty** — exact distance, field position, score state, quarter, general offense/defense quality;
2. **special situational team skill** — persistent residual performance above or below what the state model expects.

Even if #2 fails, #1 remains valuable for a state/drive simulator. A mechanistic simulator can estimate the probability of conversion in a particular matchup and situation without inventing a separate permanent third-down grade.

## Command

The diagnostic uses the compact cached third-down attempt files already created by the prior experiment. It does not replay the full profile/snapshot pipeline.

```bash
python -m cfb_analytics.analytics.third_down_variance_diagnostic
```

Optional custom grid:

```bash
python -m cfb_analytics.analytics.third_down_variance_diagnostic --penalties 2,10,50,250,1250
```

Optional outer seasons:

```bash
python -m cfb_analytics.analytics.third_down_variance_diagnostic --test-seasons 2023,2024,2025
```

Model dependencies remain optional:

```bash
pip install -e ".[models]"
```

## Prediction v1 status

Prediction v1 remains unchanged and locked as the macro benchmark. This diagnostic is mechanism research only.