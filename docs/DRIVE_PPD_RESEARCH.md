# Opponent-Adjusted Drive PPD Research Layer

**Status:** RESEARCH ONLY  
**Definition version:** `drive-ppd-v1-research`  
**Point foundation:** locked Drive Efficiency v1 + locked Finishing Drives v2 possession-point adjudication

## Purpose

This layer turns possession-level scoring into leakage-safe pregame offense/defense ratings and matchup expectations. It is intentionally separate from the production metric contract until broad walk-forward ablation demonstrates incremental predictive value.

## Possession points

Only validated possession drives are eligible:

- `isPossessionDrive == True`
- `driveValidationStatus == PASS`
- offense is known

Points are **not** inferred from final team score or raw start/end score deltas. Each possession is adjudicated with the repository's locked `finishing_drives.possession_outcome` logic:

- made field goal = resolved 3 points
- touchdown = locked scoreboard-adjudicated 6/7/8 points when resolvable
- empty possession = resolved 0 points
- unresolved touchdown score state remains unresolved
- ambiguous safety remains unresolved

This preserves the locked Drive Efficiency v1 semantics and prevents defensive/special-teams scoring from being credited to the offense.

## Raw team-game PPD

For team `i` against opponent `j`:

```text
Offensive PPD = adjudicated offensive possession points / point-resolved possessions
```

Unresolved point possessions are reported separately and are excluded from the PPD denominator rather than silently treated as zero.

## Opponent adjustment

The research rating model fits:

```text
Observed PPD(i vs j)
    = League Mean PPD
    + Offensive Strength(i)
    - Defensive Strength(j)
```

Team-game observations are weighted by point-resolved possessions. Early ratings are shrunk toward league average using a possession-equivalent prior (`25` resolved possessions by default).

Sign convention:

- higher offensive strength = better offense
- higher defensive strength = better defense / more points prevented

## Pregame leakage rule

Pregame snapshots for a partition are fit using **strictly earlier partitions only**. Current-partition outcomes never enter the snapshot used for that partition.

The snapshot exposes:

- raw offensive PPD before the game
- raw defensive PPD allowed before the game
- opponent-adjusted offensive PPD above average
- opponent-adjusted defensive PPD prevented above average
- expected offensive PPD versus an average defense
- expected defensive PPD allowed versus an average offense
- prior resolved possessions and games
- fit convergence diagnostics

## Matchup expected PPD

For home offense `H` against away defense `A`:

```text
Expected Home Offensive PPD
    = League Mean
    + Home Offensive Strength
    - Away Defensive Strength
```

The reverse direction is computed symmetrically.

The matchup store exposes:

- home expected offensive PPD
- away expected offensive PPD
- home expected defensive PPD allowed
- away expected defensive PPD allowed
- expected PPD edge

When paired with the separate possession model:

```text
Expected Team Points = Expected Offensive PPD × Expected Possessions
Expected Margin Proxy = Expected PPD Edge × Expected Possessions Per Team
```

This is a football-derived score projection, not yet a production forecast.

## Postgame residual diagnostics

Current-game outcomes are stored only in `postgame_diagnostics.json`:

```text
Offensive PPD Above Expectation
    = Actual Offensive PPD - Expected Offensive PPD

Defensive PPD Above Expectation
    = Expected Opponent PPD - Actual Opponent PPD
```

These fields are explicitly target-side diagnostics and must never be merged into pregame feature stores for the same game.

## Materialized outputs

For each season:

```text
data/processed/derived/drive_ppd/season=YYYY/
    team_games.json
    pregame.json
    matchups.json
    postgame_diagnostics.json
    manifest.json
```

Build with:

```bash
python -m cfb_analytics.analytics.drive_ppd --all
```

## Research validation

`tests/analytics/drive_ppd_ablation_harness.py` compares the new layer against the current Volume+OLS research benchmark on identical common samples. Candidate features include:

- expected PPD edge
- home and away expected offensive PPD components
- expected PPD edge × expected possessions (drive-model projected margin)

The layer remains **RESEARCH ONLY** regardless of coefficient size or football plausibility until walk-forward results show reliable incremental value.
