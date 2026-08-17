# Market Edge Research Program

**Status:** exploratory research program. Prediction v2 remains frozen for 2026.

The goal is not to manufacture a historical betting system by trying arbitrary
thresholds until one looks profitable. The goal is to search broad, defensible
model families under a single leakage-safe evaluation contract, identify any
signal that survives across seasons, and then freeze a small number of
challengers for confirmation and prospective testing.

## Primary question

Can information available before kickoff predict either:

1. the market's signed margin error,
2. the probability that the home side covers the spread, or
3. a better calibrated distribution of final margin than the market itself?

The clean CFBD spread convention is:

- positive = home team favored,
- negative = away team favored.

For a game:

```text
cover_margin = actual_home_margin - market_home_margin
```

Positive cover margin means the home side covered. Negative means the away side
covered. Zero is a push.

## Research-integrity rules

1. Outer test seasons are chronological and use only earlier seasons for model fitting.
2. No target game may contribute to its own pregame football features.
3. Market lines are joined strictly by game ID with home/away identity checks.
4. The frozen Prediction v2 implementation is not mutated by this program.
5. Many-model screens are discovery evidence only.
6. Hyperparameters or thresholds chosen after seeing an outer test result must be
   frozen and evaluated in a separate confirmation stage; do not relabel the
   discovery result as confirmatory evidence.
7. Report all tested variants, not only winners.
8. At -110 pricing, ATS break-even is 52.38095%; 50% is not the profitability threshold.
9. Report sample size, pushes, season stability, and ROI together with ATS percentage.
10. The untouched 2026 prospective predictions remain the strongest final check against historical overfitting.

## Phase A — market-aware supervised model zoo

Implemented in:

```bash
python -m cfb_analytics.analytics.market_edge_model_zoo --overwrite
```

The feature vector contains the frozen Prediction v2 pregame football features
plus pregame market context:

- market spread,
- absolute spread,
- spread squared,
- home-favorite indicator,
- pick'em indicator,
- week,
- neutral-site indicator.

### A1. Fixed model-market shrinkage

```text
prediction = market + lambda * (PredictionV2 - market)
```

with lambda frozen at 0.10, 0.25, 0.50, and 0.75 before the screen.

### A2. Predict the market residual

Target:

```text
actual_margin - market_margin
```

Families in the first registry:

- Ridge
- ElasticNet
- Huber robust regression
- median quantile regression
- Bayesian Ridge
- Gradient Boosting
- Histogram Gradient Boosting
- Random Forest
- Extra Trees
- k-nearest-neighbor regression
- RBF support-vector regression
- multilayer perceptron

The final margin prediction is market spread plus the predicted residual.

### A3. Predict final margin directly with the market as a feature

Initial representatives:

- Ridge
- Histogram Gradient Boosting
- Extra Trees

This lets the algorithm estimate how much to trust the market instead of fixing
the market coefficient at one.

### A4. Direct ATS classification

Target:

```text
home covers vs away covers
```

Training pushes are excluded. Families:

- logistic regression
- gradient boosting classifier
- histogram gradient boosting classifier
- random forest classifier
- extra-trees classifier
- multilayer perceptron classifier

Every classifier is evaluated at predeclared confidence thresholds 0.50, 0.55,
0.575, and 0.60. These thresholds are a discovery screen, not permission to
select the best-looking threshold retroactively as a final betting rule.

## Phase B — dynamic team-strength models

To build after Phase A:

- classic Elo
- margin-of-victory Elo
- generalized/discretized-margin Elo
- Glicko / Glicko-2 uncertainty-aware ratings
- Kalman-filter/state-space latent team strength
- Bayesian dynamic offense/defense ratings
- time-decayed SRS / least squares
- rolling-window SRS
- separate offensive and defensive scoring-strength state models
- possession-level latent offense/defense state models

All dynamic states must be updated strictly after games finish and before the
next target partition.

## Phase C — score and margin distribution models

Rather than predict only a point estimate:

- Gaussian margin with heteroskedastic variance
- Student-t / heavy-tailed margin regression
- separate home/away score regressions
- hierarchical score models with offense and defense latent effects
- negative-binomial / count-inspired score models where empirically defensible
- mixture distributions for blowout vs competitive-game regimes
- quantile regression at multiple quantiles
- conformal prediction intervals around predicted margin

A distribution model can support probability-of-cover estimates and selective
betting without treating a 1-point and a 10-point model edge as equally certain.

## Phase D — matchup and regime models

Possible pregame regimes:

- favorite size / underdog size
- home favorite vs home underdog
- neutral vs non-neutral
- conference vs nonconference
- same-conference familiarity
- early season vs mature season
- ranked vs unranked / large strength mismatch
- expected pace / possessions
- offensive style interaction
- run/pass asymmetry
- explosive-offense vs explosive-defense matchup
- finishing / red-zone interaction
- turnover-pressure interaction
- close-game vs blowout-prone teams

Use mixture-of-experts or interactions only if the split is defined from pregame
information and the gating rule is trained without outer-test outcomes.

## Phase E — richer information not currently in Prediction v2

Candidate data families:

- recruiting talent and roster talent composite
- returning production
- transfer-portal gains/losses
- quarterback continuity / starter changes
- coaching changes and coordinator changes
- injuries and availability
- rest days / bye weeks
- travel distance and time zones
- altitude
- weather: wind, precipitation, temperature
- surface / stadium context
- tempo and no-huddle tendencies
- garbage-time filtered efficiency
- special teams
- penalties
- fourth-down decision quality
- kicking quality
- sack-adjusted passing measures
- opponent-adjusted explosive-play distributions
- drive-start field position
- starting field-position asymmetry

These require data-quality audits before entering any betting test.

## Phase F — market microstructure and line-information models

The current clean snapshot is a reproducible selected spread, not a guaranteed
true closing consensus. A stronger market study should preserve time and provider
when available:

- opening spread
- midweek spread
- closing spread
- consensus vs individual books
- dispersion across books
- line movement
- reverse line movement
- stale-book deviations
- opening-to-close movement conditional on our model
- team totals
- game total
- moneyline
- implied home and away team totals

This allows the model to ask not merely whether Vegas is wrong, but *when the
market is still incorporating information*.

## Phase G — ensembles and stacking

Candidates:

- arithmetic average of independent models
- inverse-error weighting from prior seasons only
- ridge stacker
- nonnegative constrained stacker
- market-anchored stacker
- stacking separate margin, score, and ATS models
- mixture-of-experts by market regime
- Bayesian model averaging

Every stacker must use cross-fitted predictions for its training rows. Never
train a meta-model on base-model in-sample predictions.

## Phase H — selective betting and uncertainty

A model does not need to bet every game. Evaluate selection rules based on
quantities estimated before the game:

- predicted cover probability
- predicted residual magnitude
- ensemble disagreement
- predictive interval excluding zero cover margin
- model uncertainty
- market-provider dispersion
- agreement among independent model families

Selection thresholds must be learned/frozen inside training data or predeclared
before an outer test.

## Phase I — market-bias hypotheses

Test explicitly rather than data-mining silently:

- favorite-longshot bias
- home-underdog effects
- very large spreads
- public/high-profile teams
- conference-tier mismatch
- market score censoring / implied team-total effects
- behavioral overreaction / momentum

Each hypothesis gets its own named report with all tested seasons and denominators.

## Required scorecard for every candidate

At minimum:

```text
N
MAE
RMSE
Delta MAE vs market
Delta RMSE vs market
Straight-up accuracy
ATS W-L-P
ATS percentage
ROI at -110
Season-by-season ATS
Season-by-season margin deltas
```

For probability models also report calibration, Brier/log loss, probability-bin
reliability, and the number of bets at every predeclared confidence threshold.

## Promotion standard

No universal numerical gate is declared for this exploratory zoo. A challenger
worth a dedicated confirmation test should at least show:

- economically meaningful improvement, not a few thousandths of a point;
- consistency across multiple seasons;
- no dependence on one tiny bucket;
- ATS performance plausibly above the -110 break-even rate if the intended use is betting;
- enough decisions to distinguish signal from noise;
- a football/statistical rationale that existed before seeing the result.

Only after a candidate survives that screen should we freeze its exact feature
set, hyperparameters, thresholds, and evaluation protocol for a separately named
confirmation run.
