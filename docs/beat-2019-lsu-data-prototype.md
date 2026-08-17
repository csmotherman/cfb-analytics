# Can You Beat the 2019 LSU Tigers? — data prototype

This branch contains a **data/engine prototype only**. It does not change the public website, the 2026 Beat the Model schedule, or Prediction-v2.

## Game concept

The player is trying to build a seven-unit historical super-team with a greater than 50% estimated neutral-field chance to beat 2019 LSU.

The seven draftable units are:

1. Coach / Play Calling
2. Rushing Attack
3. Passing Attack
4. Offensive Line
5. Defensive Coverage
6. Defensive Line
7. Linebackers

The playable v2 wheel contains the top 10 SRS team-seasons from each supported season (2014–2019 and 2021–2025; 2020 remains excluded). The 2019 LSU target itself is excluded. There are 109 eligible team-seasons.

A playthrough has at most 10 spins. On each spin, the user may either draft one still-open unit from that team-season or spend one of three passes. When the number of remaining spins equals the number of open units, every remaining spin must be drafted. Each team-season can appear only once in a playthrough. The final build wins only if its estimated neutral-field win probability is **strictly greater than 50%** against 2019 LSU.

## Unit grades

Unit grades are historical full-season performance grades, not prospective predictions. Each metric is normalized within its own season before cross-era comparison. Category component z-scores are combined into a category score, then converted to a 1–99 within-season percentile grade and a letter grade.

The current v1/v2 grade definitions use CFBD advanced team statistics plus SP+ subcomponents where available. Coach metadata and target player season stats are also retained for future presentation layers.

Important limitation: offensive-line v1 uses line yards, stuff rate, power success, rushing success, and SP rushing context. Explicit sacks/TFL-allowed attribution is a planned refinement before a public website launch. Coverage, defensive-line, and linebacker grades are statistical unit proxies rather than individual scouting grades.

## Win probability

The game does not use Prediction-v2. The seven selected unit z-scores are combined using positive weights derived from their historical relationship with SRS. A monotone linear calibration maps that composite to an estimated hybrid-team SRS.

A separate historical calibration maps SRS difference to expected scoring margin using completed FBS games, then converts the neutral-field expected margin into a win probability from the historical residual distribution. Equal estimated SRS therefore corresponds to 50%.

The real-data build used 8,551 completed FBS games for the margin calibration. The seven-unit composite explained about 59.5% of historical SRS variance in the development sample.

## Difficulty research

The first research version used seven mandatory spins from the top 35 SRS teams per season. Simulation showed that was effectively unwinnable, so it was rejected before any user outcome testing.

The fixed playable-v2 contract uses top-10 team-seasons plus three passes / ten maximum spins. In 10,000 simulated wheels:

- simple sequential A-minus pass strategy: **0.64%** win rate, 23.29% mean final win probability;
- perfect-foresight upper bound: **8.75%** win rate, 35.48% mean final win probability;
- best observed perfect-foresight build in that simulation: **73.63%** win probability.

The perfect-foresight result is an upper bound because it assigns units after seeing all ten spins. A real player cannot systematically outperform it. This makes the target difficult but demonstrably beatable.

## Generated artifacts

- `data/prototypes/beat-2019-lsu/challenge-v1.json` — broad research/audit dataset.
- `data/prototypes/beat-2019-lsu/challenge-v2.json` — fixed playable candidate dataset.

## Local test/demo

```bash
pytest -q \
  tests/prototypes/test_historical_unit_draft.py \
  tests/prototypes/test_historical_unit_draft_v2.py

python -m cfb_analytics.prototypes.historical_unit_draft_v2 \
  --demo \
  --output data/prototypes/beat-2019-lsu/challenge-v2.json \
  --seed 42
```

Change `--seed` to generate a different deterministic wheel for testing.

## What is intentionally not done yet

- No SOAR/website UI has been added.
- Beat the Model has not been disabled for Weeks 1–3.
- No user-outcome tuning has been performed.
- No database/user state has been added.
- Player cards for every wheel team-season are not yet materialized; the current unit engine is team-season based.
