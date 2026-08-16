# Prediction v2 Early-Season Prior Feasibility Audit

**Status:** PRE-CHALLENGER COVERAGE AUDIT  
**Version:** `prediction-v2-early-prior-audit-v1`

## Purpose

Prediction v2 is the locked research benchmark for established-season game-margin prediction, but its benchmark sample requires at least 3 or 4 current-season games for both teams.

The next research family is previous-season carryover for early-season games. Before choosing a carryover strength or decay formula, this audit answers a narrower question:

> Can the already-saved artifacts provide a complete previous-season prior for every information family Prediction v2 needs, and how many early games could that prior actually cover?

No game-margin challenger is fit by this command. No carryover weight is tuned.

## Adjacent-season rule

A prior is allowed only when the immediately preceding season exists in the historical corpus.

Eligible transitions are therefore:

```text
2015 <- 2014
2016 <- 2015
2017 <- 2016
2018 <- 2017
2019 <- 2018
2022 <- 2021
2023 <- 2022
2024 <- 2023
2025 <- 2024
```

The audit deliberately excludes:

```text
2014: no earlier corpus season
2021: 2020 is absent
```

It never substitutes 2019 as a 2021 prior.

## Prior-state families

The audit reconstructs final prior-season state from saved artifacts only.

### Iterative ratings

Refit the six final previous-season opponent-adjusted offense/defense rating families from saved derived team-game rows:

```text
Success
Explosive
YardsPerPlay
YardsPerPossession
Finishing
FieldPosition
```

A team has complete Iterative prior state only if offense and defense values are finite for all six families.

### Football Mechanisms required by Prediction v2

Prediction v2's volume and possession interactions require these prior-season team states:

```text
OffSuccessRate
DefSuccessRateAllowed
OffExplosiveRate
DefExplosiveRateAllowed
OffGiveawayRate
DefTakeawayRate
OffPossessionsPerGame
DefPossessionsPerGame
```

They are reconstructed from additive saved team-game counts.

### MWDR

Final prior-season MWDR offense and defense ratings are recomputed from the saved `sandbox_components` team-game cache.

The audit does not replay canonical plays or drives to create this cache.

### Site-aware SRS / HFA

Final prior-season site-aware SRS ratings and HFA are fit from the corrected authoritative game targets plus raw `neutralSite` flags.

The previous season is already complete at the point it is used as a new-season prior, so using its final state does not leak information from the new season.

## Complete prior team

A team is considered prior-ready only when it has finite state for all four required families:

```text
Iterative
Football Mechanisms
MWDR
site-aware SRS
```

A current-season game is prior-coverable only when both teams are prior-ready.

## Early-season coverage definition

For this feasibility audit, early games are regular-season games with source week <= 4, including week 0 when present.

The command reports:

- total early games;
- games with complete prior state for both teams;
- early games currently below the Prediction-v2 min3 history threshold;
- how many of those min3-unavailable games are prior-coverable;
- the same quantities for min4.

This is a coverage diagnostic, not a prediction comparison.

## Why decay is not chosen yet

Choosing a previous-season weight before confirming coverage risks designing a model around a sample that does not exist consistently.

After this audit passes, the next challenger should predeclare a development-only carryover/decay rule and then evaluate it against Prediction v2 without tuning on the recent validation folds.

The intended evaluation slices are:

```text
Weeks 1-2
Weeks 3-4
Week 5+
```

The exact carryover mechanism and promotion gate should be committed before inspecting its game-margin results.

## Runtime

This command reads saved corrected feature stores, derived team-game rows, sandbox component caches, and raw game-site flags. It performs only lightweight rating/state reconstruction.

It does **not** replay PBP, rebuild profiles, rebuild the full model feature store, or fit drive-outcome models.

Run:

```bash
python -m cfb_analytics.analytics.prediction_v2_early_prior_audit
```

## Decision rule

If the audit reports `READY`, use its observed state coverage to design the fixed early-season carryover challenger.

If it reports `REVIEW`, resolve the missing state/cache or continuity problem before fitting an early-season model.
