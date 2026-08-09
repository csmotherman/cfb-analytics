# Architecture

## Current scope

Phase 1 is raw acquisition only.

We are intentionally not implementing cleaning, derived football concepts, advanced metrics, ratings, simulations, or machine learning yet.

## Long-term lineage

```text
SOURCE APIs
    |
    v
RAW DATA                         <- Phase 1
    |-- games
    |-- drives
    `-- plays
    |
    v
CANONICAL / CLEAN DATA           <- Phase 2
    |
    v
TEAM-GAME + TEAM-WEEK DATA       <- later
    |
    v
METRICS / HISTORICAL MODELS      <- later
    |
    v
FAN INSIGHTS / WEBSITE           <- later
```

Every downstream value must be traceable to immutable source records.

## Repository boundaries

- `src/cfb_analytics/sources/`: source-specific acquisition code only.
- `src/cfb_analytics/raw/`: orchestration, manifests, storage, and raw-data validation only.
- `config/`: declarative acquisition scope. No football metric definitions.
- `data/raw/`: local raw artifacts. Never committed.
- `docs/`: contracts and decisions that must exist before implementation.
- `tests/raw/`: tests for acquisition/storage integrity only.

Do not add `clean/`, `metrics/`, `models/`, `ratings/`, or website code during Phase 1.

## Raw storage grain

Raw data is partitioned by source, season, season type, week, and entity:

```text
data/raw/cfbd/
  season=2025/
    season_type=regular/
      week=01/
        games/
        drives/
        plays/
        manifest.json
```

Postseason data should use explicit source season-type/week semantics rather than being silently mixed with regular-season partitions.

## Why week-by-week

Historical team-week snapshots and future leakage-safe models require us to know exactly what information existed after each week. Acquisition therefore preserves the source week instead of downloading a season into one undifferentiated table.
