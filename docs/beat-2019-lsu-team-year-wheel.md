# Team-Year NIL Wheel: Beat the 2019 LSU Tigers

This is the release mechanic for the SOAR preseason challenge. It replaces the earlier two-offer-per-position prototype while retaining the same historical player grading, fictional NIL pricing, 2019 LSU target, and two-stage matchup calibration.

## User loop

1. SOAR deals seven hidden, distinct historical team-seasons.
2. The user spins to reveal one team + year.
3. The full game-eligible roster for that team-season is shown with historical production stats, SOAR grade, and fictional SOAR NIL ask.
4. The user signs exactly one player from that spin into one open slot.
5. Repeat for seven spins.
6. The completed roster must fill QB, RB, WR, FLEX, DL/EDGE, LB, and DB exactly once and stay under one shared NIL cap.
7. SOAR calculates the user's neutral-field probability against 2019 LSU.
8. SOAR then solves the same seven spins with perfect information and displays the **best possible roster**, its spend, and its win probability next to the user's roster.

The flow intentionally mirrors the simple appeal of a team-season roster wheel: draw a historical team-season, shop that roster, make one irreversible signing, and live with the consequences.

## Playable-board rule

A seven-team draw is accepted only if at least one legal seven-player roster can be completed under the published cap. If the hidden board is mathematically impossible to finish, it is redrawn before the first spin. The user never sees rejected boards.

During play, a signing is disabled if it would leave no legal way to complete the remaining hidden spins under the cap. This check does not reveal future teams or players.

## 1-in-1,000 difficulty target

Difficulty is based on the **oracle**, not on average user behavior.

For every simulated seven-spin board, the engine solves the exact budget-constrained optimization problem:

- choose exactly one player from every drawn team-season;
- use every roster slot exactly once;
- stay under the candidate NIL cap;
- maximize the seven-player roster-power composite.

The bankroll is selected before any user outcomes so that, among playable boards, approximately **0.10% (1 in 1,000)** have an oracle roster with a neutral-field win probability above 50% against 2019 LSU.

This is intentionally much harder than targeting a 0.1% *user* win rate. If a board is not oracle-beatable, no sequence of user decisions can make it beat LSU. If it is oracle-beatable, the user still has to find the right players and slot assignment without knowing future spins.

## Exact best-possible comparison

After the seventh signing, the site reruns the same optimization on the user's exact seven team-seasons at the published cap. This produces the answer key shown to the user:

- best legal player for each of the seven slots;
- best legal NIL spend;
- best possible expected margin;
- best possible neutral-field win probability.

No post-game tuning is performed from the user's result.

## Player and NIL model

Player grades remain era-adjusted historical production ratings. They are not film/scouting grades. Defensive ratings are production proxies based on recorded defensive statistics.

SOAR NIL asks remain fictional gameplay currency. They are not historical NIL earnings, NIL estimates, or claims about real-world market value. The price model blends grade, position premium, and production/star-volume percentile to create cap tradeoffs.

## Matchup model

This challenge remains separate from Prediction-v2.

The game-strength proxy uses the existing two-stage historical calibration:

1. seven-player historical roster power -> historical team SRS;
2. historical SRS difference -> completed FBS game margin.

The final neutral-field expected margin is monotone in roster-power difference. Equal roster power maps to exactly 50%.

## Historical support

Supported seasons currently remain 2014–2019 and 2021–2025, with 2020 excluded to match the current SOAR historical support policy. The first team-year wheel uses complete team-seasons from the bounded historical player acquisition pool; expanding the wheel to more FBS team-seasons is a data-coverage improvement, not a change to the game rules.

## Build

```bash
python -m cfb_analytics.prototypes.historical_player_team_year_wheel \
  --build \
  --output data/prototypes/beat-2019-lsu/team-year-wheel-v2.json \
  --simulations 50000 \
  --seed 7319
```

The build requires `CFBD_API_KEY`. The generated JSON is the public artifact intended for the SOAR `Prediction-models` repository.
