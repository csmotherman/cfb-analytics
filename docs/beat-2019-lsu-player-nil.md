# Can a SOAR NIL Budget Beat the 2019 LSU Tigers?

This branch replaces the earlier team-unit draft experiment with a **player-based historical roster game**. It is a separate game engine and does not alter Prediction-v2, the 2026 frozen model snapshots, or Beat the Model.

## Roster

The user must sign seven historical player-seasons:

- QB
- RB
- WR
- FLEX (RB / WR / TE)
- DL / EDGE
- LB
- DB

The 2019 LSU target is also represented by seven actual 2019 LSU player-seasons selected by the same player-rating system.

## Player grades

`/stats/player/season` is aggregated into player-team-season records. Each roster slot has fixed production metrics and weights. Metrics are percentile-ranked against players at the same slot in the same season, which controls for era and scoring environment. Those era-adjusted scores are then percentile-ranked across all supported seasons to create the displayed 1–99 SOAR grade and a cross-era `powerZ` used by the game engine.

Grades are production ratings, not film/scouting grades. Defensive ratings are especially important to describe this way because they use recorded tackles, TFL, sacks, interceptions, passes defended, and forced fumbles rather than assignment-level coverage or trench film.

## Fictional NIL asks

Every player receives a **SOAR NIL Ask** in millions of game dollars. It blends:

1. the player’s highest SOAR grade,
2. a fixed position-price band, and
3. a raw production/star-volume percentile.

The third term prevents price from being a simple one-to-one copy of grade and creates possible value signings.

These values are fictional gameplay currency. They are **not** estimates of historical NIL earnings, real market value, or what pre-NIL-era players would have earned.

## Portal mechanic

Each roster slot has up to two portal offers. The first can be signed or passed; if the player passes the first offer for a slot, the second offer is final for that slot. This produces at most 14 offers and at least 7 signings. The shared NIL budget makes elite-player accumulation expensive.

The public UI should prevent duplicate player-seasons in the final roster and should surface remaining budget plus a reserve requirement for still-open positions.

## Matchup probability

The engine does not reuse the old team-unit SRS regression.

For every historical team-season with enough player data, it builds the best unique seven-player roster using the same seven slots. A weighted player-roster composite is then calibrated directly to completed FBS game margins. The final neutral-field rule is:

`expected margin = historical roster-power margin scale × (user roster power − 2019 LSU roster power)`

The expected margin is converted to a win probability using the historical residual distribution. Equal roster power therefore maps to exactly 50% on a neutral field.

## Difficulty and budget

The budget is selected **before user testing** from a fixed sweep of candidate budgets. Thousands of random two-offer-per-slot portal boards are simulated. For each budget the engine records:

- board feasibility,
- a simple sequential strategy,
- a perfect-information upper bound,
- mean win probability, and
- maximum observed probability.

The chosen budget is the candidate nearest a 10% perfect-information win rate among budgets with at least 85% perfect-information roster feasibility. This keeps the game difficult without tuning from observed user outcomes.

## Historical support

Supported seasons: 2014–2019 and 2021–2025. 2020 remains excluded to match the rest of the current SOAR historical support policy.

## Build

```bash
python -m cfb_analytics.prototypes.historical_player_nil_draft \
  --build \
  --output data/prototypes/beat-2019-lsu/player-nil-v1.json \
  --simulations 5000

python -m cfb_analytics.prototypes.historical_player_nil_draft \
  --demo \
  --output data/prototypes/beat-2019-lsu/player-nil-v1.json \
  --seed 42
```

The build requires `CFBD_API_KEY`. The generated JSON is the only artifact intended to be mirrored into the SOAR `Prediction-models` repository.
