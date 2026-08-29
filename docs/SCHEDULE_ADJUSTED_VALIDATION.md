# Schedule-Adjusted Ratings Validation v1

**Status:** RESEARCH ONLY  
**Validation version:** `schedule-adjusted-walk-forward-v1`  
**Model under test:** `schedule-adjusted-ratings-v1`

## Purpose

The schedule-adjusted model is only useful if the recursive opponent adjustment improves estimates of future game performance. Rankings that merely "look right" are not sufficient evidence.

This validation is a strict week-forward backtest. For every checkpoint in a season, the model is fit using only games that occurred before that checkpoint. Games from the target week are never included in the fit that predicts them.

## Compared methods

Every method is scored on the exact same eligible team-game observations.

### 1. Raw offense

The offense's prior-season-to-date aggregate for the metric:

```text
raw_offense = prior numerator / prior denominator
```

This ignores the quality of defenses faced.

### 2. Simple matchup baseline

A non-recursive combination of the offense's prior raw performance and the defense's prior raw allowed performance, centered on the prior national average.

For continuous metrics:

```text
expected = offense_raw + defense_allowed_raw - league_average
```

For binomial rate metrics, the same identity is applied on the log-odds scale so the result remains a valid probability:

```text
logit(expected)
  = logit(offense_raw)
  + logit(defense_allowed_raw)
  - logit(league_average)
```

This is the key baseline for testing whether recursive schedule adjustment adds value. It accounts for both teams, but it does **not** adjust either team's history for the quality of the opponents that produced that history.

### 3. Schedule-adjusted matchup

The research model fits all prior offense and defense effects simultaneously over the connected schedule graph and predicts the target matchup from those fitted effects.

## Eligibility

Default validation requires at least **3 prior games** for:

- the target offense's offensive history; and
- the target defense's defensive history.

This avoids pretending Week 2 estimates have the same support as midseason estimates. The threshold is configurable.

Rows with failed game validation are excluded by default. A metric with a zero denominator is omitted for that observation rather than imputed.

Regular-season checkpoints precede postseason checkpoints. Games within the same checkpoint never train on one another.

## Error metrics

For each model the harness reports:

- **MAE** — mean absolute error per team-game;
- **RMSE** — root mean squared error;
- **weighted MAE** — absolute error weighted by the metric's opportunity denominator;
- **bias** — mean signed prediction error.

MAE is the primary ridge-selection statistic because the intended product use is estimating a team's expected performance in a single game.

For rate metrics, MAE is displayed as percentage points in the terminal report.

## Ridge selection

The default ridge grid is:

```text
5, 10, 20, 40, 80
```

A best ridge is reported separately for every metric.

A cross-metric research recommendation is also reported using the mean:

```text
adjusted MAE / simple-matchup MAE
```

This ratio makes metrics with different units comparable without mixing yards, points and rates directly. Lower is better. A ratio below `1.0` means the recursive model beats the simple non-recursive matchup baseline on average.

The cross-metric recommendation is research guidance, not a production lock. Different metric families may ultimately need different ridge strengths.

## Run the 2025 validation

```bash
python -m cfb_analytics.analytics.schedule_adjusted.validation_cli \
  --season 2025 \
  --output data/research/schedule-adjusted-validation-2025.json
```

Validate only the most stable high-volume metrics first:

```bash
python -m cfb_analytics.analytics.schedule_adjusted.validation_cli \
  --season 2025 \
  --metric successRate \
  --metric rushSuccessRate \
  --metric passSuccessRate \
  --metric explosivePlayRate \
  --metric yardsPerPlay \
  --ridge 5 \
  --ridge 10 \
  --ridge 20 \
  --ridge 40 \
  --ridge 80
```

Change the early-season evidence threshold:

```bash
python -m cfb_analytics.analytics.schedule_adjusted.validation_cli \
  --season 2025 \
  --min-prior-games 4
```

## Interpreting the result

The recursive model earns promotion only if it shows repeatable out-of-sample value.

Strong evidence would look like:

- adjusted MAE lower than raw offense MAE;
- adjusted MAE lower than the simple matchup baseline;
- improvement present across multiple stable metrics rather than one metric;
- ridge selection reasonably stable instead of jumping to an extreme boundary;
- no large systematic bias;
- similar conclusions when the minimum-prior-games threshold changes.

A poor result is useful too. If the simple matchup baseline performs as well as or better than the recursive model, the extra complexity has not yet earned its place.

## What this does not prove

One good 2025 backtest does not establish a production-quality "true strength" rating.

Before production lock, repeat the week-forward test across multiple seasons, test early-season priors, quantify uncertainty, inspect calibration by week, and confirm that any chosen ridge/generalization rule holds out of sample.

The purpose of this first backtest is narrower: determine whether the recursive schedule network adds measurable value before using it as the backbone of Game Room talking points.
