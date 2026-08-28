# Schedule-Adjusted Offense / Defense Ratings v1

**Status:** RESEARCH ONLY  
**Definition version:** `schedule-adjusted-ratings-v1`  
**Primary use:** game-story discovery and performance-over-expectation research

## Goal

A raw opponent baseline such as "Oregon allows a 39% success rate" does not answer the real question if Oregon played an unusually weak or strong schedule. This model estimates every offense and every defense **simultaneously over the complete connected schedule graph**. There is no arbitrary stopping point at opponent, opponent's opponent, or opponent's opponent's opponent: all connected games contribute to the fitted effects in one system.

The model is intentionally research-only. It is not yet a production-locked SOAR rating, and the website must not present it as such until the regularization and out-of-sample calibration are validated.

## Core equation

For each team-as-offense game observation:

```text
oriented_performance = league_average + offense_effect - defense_effect + home_field_effect * venue + error
```

`venue` is `+1` for the home offense, `-1` for the away offense, and `0` at a neutral site.

Every metric is internally oriented so **larger means better for the offense**. Therefore:

- positive `offense_effect` always means a stronger offense;
- positive `defense_effect` always means a stronger defense (more suppression);
- a positive game `performance_over_expected` always means the offense beat expectation;
- for a defense-perspective game evaluation, the sign is reversed so positive means the defense beat expectation.

Lower-is-better offensive metrics such as sack rate allowed, havoc rate allowed, and average starting yards to goal are transformed only for fitting/orientation. Public/raw expected values are converted back to their normal units.

## Two model families

### 1. Binomial logistic schedule adjustment

Used when a metric is a count of positive events out of eligible opportunities, for example success rate, explosive-play rate, third-down conversion rate, red-zone TD rate, sack rate, and havoc rate.

For higher-is-better offensive rates:

```text
successes ~ Binomial(trials, p)
logit(p) = league_average + offense_effect - defense_effect + home_field_effect * venue
```

For lower-is-better offensive rates, the model fits the complementary good-offense event. Example: sack rate fits `non_sacks = dropbacks - sacks_allowed`, then converts the expected probability back to raw sack rate.

This avoids taking a logit of a displayed game rate and correctly preserves the game denominator. A 35/70 success-rate game carries more information than a 4/8 game even though both display 50%.

The implementation uses Newton/IRLS on the aggregated binomial likelihood with ridge penalties on team effects.

### 2. Denominator-weighted ridge least squares

Used for continuous ratio metrics such as yards per play, yards per attempt, net pass yards per dropback, points per possession, and points per opportunity.

The response is reconstructed from the locked numerator and denominator:

```text
value = numerator / denominator
```

The regression is weighted by the denominator so larger-opportunity samples carry more information. Team effects receive ridge regularization; the intercept is not penalized.

## Why ridge regularization is required

College football schedules are sparse and unbalanced, especially early in the season. Ridge regularization:

- makes the offense/defense system identifiable and numerically stable;
- shrinks teams with little evidence toward average;
- prevents one or two games from creating extreme ratings;
- allows sparsely connected FCS or non-core opponents to remain in the graph without pretending they are precisely known.

The default `ridge=20.0` and `home_ridge=20.0` are **research defaults, not calibrated production constants**. Before promotion from RESEARCH ONLY, they should be selected using season-held-out or week-forward out-of-sample validation.

## Strict leave-one-game-out game evaluation

When evaluating a specific game, **both team-game rows from that game are removed before fitting**. The target game therefore cannot improve or worsen either team's own adjusted rating before its expectation is calculated.

For an offense perspective:

```text
expected = model(team_offense, opponent_defense, venue)
performance_over_expected = oriented(actual - expected)
```

For a defense perspective, the opponent's offense-facing row is evaluated and the performance-over-expected sign is reversed.

This is the number the Creator Hub should eventually use for statements such as:

> Michigan's rushing success rate was 11.4 percentage points better than the matchup expectation after adjusting both teams through the full schedule network.

The UI should still show the underlying sample size and never describe a research estimate as literal ground truth.

## Current metric registry

The v1 code registry lives in `src/cfb_analytics/analytics/schedule_adjusted/specs.py`. It fits one offense-facing model per concept; the fitted defense effect is the corresponding defensive rating, so mirror `Allowed` fields do not require a duplicate model.

### Default Creator Hub research set

- overall success rate
- rush success rate
- pass success rate
- explosive-play rate
- yards per play
- points per resolved possession
- points per scoring opportunity
- third-down conversion rate
- red-zone possession TD rate
- sack rate allowed
- havoc rate allowed

### Extended supported set

The same framework also includes standard/passing-down success, down-specific success, rush/pass explosiveness, goal-to-go/red-zone play success, scoring-opportunity and touchdown rates, empty scoring opportunities, rush yards/attempt, net pass yards/dropback, successful-play yardage, yards/possession, red-zone points, and average starting field position.

Only metrics with an explicit numerator/denominator pair are registered. Raw counts such as turnovers are intentionally not forced into this model until a stable opportunity denominator and volatility policy are defined. EPA is also not added here until an authoritative EPA metric is part of the Python metric contract.

## Interpreting ratings

`offense_effect` and `defense_effect` are the model coefficients. For binomial metrics they are on the log-odds scale; for Gaussian metrics they are on the oriented metric scale. **Do not compare coefficient magnitudes across different metrics.**

For human-facing use, prefer:

- `adjusted_offense_value(team)` — expected raw value vs an average neutral defense;
- `adjusted_defense_value(team)` — expected raw value an average neutral offense would produce vs that defense;
- `performance_over_expected` — the target game's leave-one-out deviation from matchup expectation;
- `exposure` — denominator/opportunity volume supporting the team effect.

## Data rules

- Input grain is the existing team-game contract: one team in one game.
- Both mirrored team rows are legitimate observations because each represents a different offense facing the opposing defense.
- Exact duplicate `(game_id, team_id)` rows are de-duplicated.
- The registered numerator/denominator counts are authoritative; stored display rates are ignored when fitting.
- Rows with a non-`PASS` `gameValidationStatus` are excluded by default.
- Zero-denominator metric observations are omitted rather than imputed.
- Neutral-site games receive no home-field term.
- Missing/unknown teams in a prediction are treated as average only when explicitly requested by the result helper; fitting itself uses the observed schedule graph.

## Files

```text
src/cfb_analytics/analytics/schedule_adjusted/
  __init__.py
  specs.py       metric registry and orientation
  model.py       ridge WLS + aggregated-binomial IRLS
  dataset.py     team-game adapters, full-season fitting, strict LOO game evaluation
  cli.py         local research runner

tests/analytics/test_schedule_adjusted_ratings.py
```

## Local validation

Install the normal model/test extras:

```bash
pip install -e '.[dev,models,publish]'
```

Run the focused tests first:

```bash
pytest tests/analytics/test_schedule_adjusted_ratings.py -q
```

Then run the full suite:

```bash
pytest
```

The focused tests cover:

1. recovery of known offense/defense effects on a connected synthetic schedule;
2. recursive schedule propagation (two identical raw performances separate once opponent quality is learned through the rest of the graph);
3. aggregated-binomial offense/defense ordering;
4. correct orientation of lower-is-better metrics;
5. count-based reconstruction instead of trusting displayed rates;
6. strict leave-one-game-out leakage prevention;
7. offense/defense perspective sign symmetry;
8. numerator/denominator registry reconciliation against the real 2025 Michigan published game artifact.

## Local research run

Fit the default Creator Hub metric set for a published season:

```bash
python -m cfb_analytics.analytics.schedule_adjusted.cli \
  --season 2025 \
  --output data/research/schedule-adjusted-2025.json
```

Fit selected metrics only:

```bash
python -m cfb_analytics.analytics.schedule_adjusted.cli \
  --season 2025 \
  --metric successRate \
  --metric rushSuccessRate \
  --metric yardsPerPlay \
  --output data/research/schedule-adjusted-2025-core.json
```

## Before production use

Do not wire these ratings into public claims until the following are completed:

1. tune ridge strength with week-forward / season-held-out validation;
2. quantify calibration and stability by week of season;
3. decide whether early-season prior-year/preseason priors improve out-of-sample performance;
4. test FBS-only ranking presentation while retaining useful non-FBS schedule information in the fit;
5. benchmark venue treatment and whether one home-field term is sufficient by metric;
6. add uncertainty intervals or a documented exposure-based confidence treatment;
7. validate each extended metric family across the full national corpus, not only Michigan.

Until then, `schedule-adjusted-ratings-v1` is a research foundation for finding better game stories, not a claim that the fitted number is the unknowable literal "true" team strength.
