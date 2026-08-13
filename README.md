# CFB Analytics

Reliability-first college football analytics built from preserved CollegeFootballData play-by-play.

## Current checkpoint

Historical corpus: `2014–2019, 2021–2025`.

Validated derived foundation:

- 8,510 games
- 17,020 team-game rows
- 1,438 team-season rows
- canonical games, drives, plays, and possession chronology
- production audits requiring offense/defense and team-game/team-season reconciliation

The authoritative metric contract is `docs/METRIC_REGISTRY.md`.

## Architecture

```text
CFBD REST JSON
    -> raw evidence
    -> canonical games / drives / plays
    -> validated possessions and event semantics
    -> team-game analytics
    -> team-season analytics
    -> production audits and metric registry
```

Raw source records remain immutable evidence. Canonical and derived layers add explicit, versioned football semantics.

## Production metric families

Locked or production-safe families include Success Rate, Explosiveness, Basic Yardage, Dropbacks / Sack Rate, Standard / Passing Downs, Third / Fourth Down conversions, Red-Zone / Goal-to-Go play efficiency, Tackles for Loss, Havoc, Team-Facing Turnovers, Drive Efficiency, Red-Zone Possession Efficiency, Possession Yardage, Three-and-Out counts, and First-Down Generation counts.

A field is not considered production-locked merely because it exists. See `docs/METRIC_REGISTRY.md` for definitions, exclusions, corpus totals, and reconciliation guarantees.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
export CFBD_API_KEY='...'
```

Raw acquisition commands remain available through `cfb-raw`. Raw artifacts live under `data/raw/cfbd/` and are ignored by Git.

## EPA research phase

CFBD exposes play-level `ppa`. We treat that as an external benchmark, not as training truth.

```text
historical canonical game state
    -> our Expected Points model
    -> our play-level EPA
    -> independent comparison against CFBD PPA
```

Before fitting or locking EPA v1 we must validate regulation state coverage, score timing semantics, possession transitions, scoring alignment, PPA coverage, and leakage-safe train/validation splits.

PPA must not be used as a feature or target in our EPA model. It is reserved for post-model comparison and error analysis.

## Near-term roadmap

1. Lock remaining already-built field-position and finishing-drive families.
2. Build Expected Points / EPA v1 from historical state and outcomes.
3. Compare EPA v1 against source PPA on identical eligible plays.
4. Add pace and situational metrics.
5. Freeze Raw Metrics v1.
6. Build leakage-safe pregame snapshots.
7. Add opponent adjustment and walk-forward predictive models.

## Change-control rule

Do not silently change a locked denominator or metric meaning. Investigate uncertain source semantics first, version definitions, propagate only after reconciliation, and update the metric registry.