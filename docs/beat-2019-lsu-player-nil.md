# Can $22M in NIL Beat the 2019 LSU Tigers?

This branch replaces the earlier team-unit draft experiment with a **player-based historical roster game**. It is a separate game engine and does not alter Prediction-v2, the 2026 frozen model snapshots, or Beat the Model.

## Frozen release contract

The pre-user simulation selected the following gameplay contract:

- fictional SOAR NIL cap: **$22M**;
- seven required historical player-seasons;
- two portal offers per roster slot;
- the first offer may be signed or passed once, while the second is final;
- neutral-field win probability must be **strictly greater than 50%** to beat 2019 LSU.

No user outcomes were used to select the cap or pricing bands.

## Roster

The user must sign:

- QB
- RB
- WR
- FLEX (RB / WR / TE)
- DL / EDGE
- LB
- DB

The 2019 LSU target is also represented by seven unique actual 2019 LSU player-seasons selected by the same player-rating system.

## Player grades

CFBD `/stats/player/season` rows are aggregated into player-team-season records. Each roster slot has fixed production metrics and weights. Metrics are percentile-ranked against players at the same slot in the same season, which controls for era and scoring environment. Those era-adjusted scores are then percentile-ranked across supported seasons to create the displayed 1–99 SOAR grade and a cross-era `powerZ` used by the game engine.

Grades are production ratings, not film/scouting grades. Defensive ratings use recorded tackles, TFL, sacks, interceptions, passes defended, and forced fumbles rather than assignment-level coverage or trench film.

The release portal is sourced from the top 10 SRS FBS teams in each supported season. Final pool sizes are:

- QB: 110
- RB: 110
- WR: 110
- FLEX: 110
- DL: 90
- LB: 90
- DB: 90

## Fictional NIL asks

Every player receives a **SOAR NIL Ask** in millions of game dollars. It blends the player grade, a fixed position-price band, and a raw production/star-volume percentile. That third term prevents price from being a simple one-to-one copy of grade and allows value signings.

Release price bands:

- QB: $1.0M–$5.5M
- RB: $0.4M–$2.8M
- WR: $0.6M–$3.8M
- TE: $0.4M–$2.5M
- DL: $0.6M–$3.4M
- LB: $0.5M–$2.8M
- DB: $0.5M–$3.2M

These values are fictional gameplay currency. They are **not** estimates of historical NIL earnings, real market value, or what pre-NIL-era players would have earned.

## Matchup estimate

The engine does not reuse Prediction-v2 or the old team-unit SRS regression.

The release calibration is two-stage:

1. historical seven-player roster power is fitted to historical team SRS using team-seasons with complete player lineups;
2. historical SRS difference is fitted to completed FBS game margin using the broad game sample.

Because only roster-power differences enter the final game, the stage-one intercept cancels. The neutral-field rule is:

`expected margin = rosterPowerToMargin × (user roster power − 2019 LSU roster power)`

The expected margin is translated to a win probability from the historical residual distribution. Equal roster power therefore maps to exactly 50% on a neutral field.

Release calibration:

- 85 historical team-seasons with complete seven-player lineups;
- 8,506 completed FBS games for the SRS-to-margin layer;
- roster-power -> SRS development R²: **0.1363**.

The low R² is important context. This is an interactive historical game-strength proxy, not a scouting model and not a claim that seven player stat lines explain most of team quality.

## Difficulty

The release budget was selected **before user testing** from a fixed sweep of candidate caps. In 5,000 random two-offer-per-slot portal boards at the selected $22M cap:

- board feasibility: **100%**;
- simple sequential strategy win rate: **0.88%**;
- perfect-information upper-bound win rate: **9.08%**;
- best simulated perfect-information win probability: **55.73%**.

The perfect-information result is an upper bound because it is allowed to see both offers at every position before choosing the best affordable roster. A real player makes decisions sequentially.

## Historical support

Supported seasons: 2014–2019 and 2021–2025. 2020 remains excluded to match the rest of the current SOAR historical support policy.

## Build

The production data build uses the bounded acquisition/two-stage calibration runner plus the frozen release pricing contract:

```bash
python -m cfb_analytics.prototypes.historical_player_nil_draft_release \
  --build \
  --output data/prototypes/beat-2019-lsu/player-nil-v1.json \
  --simulations 5000

python -m cfb_analytics.prototypes.historical_player_nil_draft_release \
  --demo \
  --output data/prototypes/beat-2019-lsu/player-nil-v1.json \
  --seed 42
```

The build requires `CFBD_API_KEY`. The validated generated JSON is mirrored into SOAR at `frontend/prediction-model/public/data/cfb/challenges/beat-2019-lsu/player-nil-v1.json`.
