# Prediction v2 Adjusted Scoring Challenger

**Status:** research challenger only  
**Base model:** locked Prediction v2  
**Version:** `prediction-v2-adjusted-scoring-v1`

## Question

Does explicitly separating scoring offense and scoring defense improve out-of-sample
margin prediction beyond locked Prediction v2?

Prediction v2 already has site-aware SRS, which is an opponent-adjusted net margin
rating, but it does not contain separate points-per-game or points-allowed-per-game
features. This challenger tests whether those scoring dimensions add information that
net SRS and the existing efficiency features do not capture.

## Integrity rule

The frozen Prediction v2 model is not changed.

All challenger scoring features are built from games in **strictly earlier completed
partitions** than the target game. The target game's score is attached only after its
pregame feature row has been materialized.

Evaluation uses the same outer-season OOS test seasons and `minGames` settings as the
locked Prediction v2 benchmark. Every challenger variant must have the exact same
eligible `gameId` set as the base model or evaluation hard-fails.

## Raw scoring feature

For each team before a target game:

```text
PPG  = prior points scored / prior games
PPGA = prior points allowed / prior games
```

The raw matchup expectation is:

```text
homeExpected = (home PPG + away PPGA) / 2
awayExpected = (away PPG + home PPGA) / 2
rawScoringMargin = homeExpected - awayExpected
```

Positive means the home team is expected to win by that many points.

## Opponent-adjusted scoring model

Each prior completed game contributes two team-score observations.

For a team scoring against an opponent:

```text
score = basePoints
      + offense(team)
      - defense(opponent)
      + site * homeFieldAdvantage
```

where:

```text
site = +0.5 for the home team's score in a non-neutral game
site = -0.5 for the away team's score in a non-neutral game
site =  0.0 at a neutral site
```

Therefore the fitted home-field term contributes directly to expected scoring margin.

A tiny ridge penalty is applied only to offense and defense ratings. This makes the
system identifiable when the early-season schedule graph is disconnected without
penalizing the league scoring baseline or site effect.

For a target matchup:

```text
adjustedScoringOffenseEdge = home offense - away offense
adjustedScoringDefenseEdge = home defense - away defense

adjustedScoringMargin = adjustedScoringOffenseEdge
                      + adjustedScoringDefenseEdge
                      + site HFA
```

The model also records expected home and away points as diagnostics, but those totals
are not separate challenger inputs in v1.

## Predeclared variants

Three variants are evaluated before looking at results:

1. `raw-ppg-margin`
   - Prediction v2 + `rawScoringMargin`

2. `adjusted-scoring-margin`
   - Prediction v2 + `adjustedScoringMargin`

3. `adjusted-scoring-split`
   - Prediction v2 + `adjustedScoringOffenseEdge`
   - Prediction v2 + `adjustedScoringDefenseEdge`

The split variant tests whether separate scoring offense and scoring defense contain
matchup information that is lost when collapsed into one net scoring margin.

## Primary decision metrics

For each variant and each locked `minGames` setting:

```text
MAE
RMSE
straight-up winner accuracy
```

The primary comparison is challenger minus locked Prediction v2 on the exact same
outer-season OOS games.

```text
negative delta MAE  = challenger improved
negative delta RMSE = challenger improved
positive delta win  = challenger improved
```

No market-spread result is used to tune these scoring definitions.

## Run

```bash
python -m cfb_analytics.analytics.prediction_v2_adjusted_scoring_challenger \
  --overwrite
```

Outputs:

```text
data/processed/prediction_v2_adjusted_scoring_challenger.json
data/processed/prediction_v2_adjusted_scoring_challenger_games.json
```

## Interpretation

A challenger should not be promoted merely because one season or one metric improves.
The useful signal would be a repeatable pooled OOS reduction in margin error with
reasonable season-by-season stability.

Regardless of the result, the frozen 2026 Prediction v2 artifact remains unchanged.
Any future 2026 model using these scoring features must be separately named and frozen.
