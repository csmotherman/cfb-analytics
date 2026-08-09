# Phase 2 — Canonical Data Plan

## Goal

Turn the validated raw CFBD corpus into stable, typed, analysis-ready tables **without changing the football meaning of a record**.

Phase 2 is deliberately split into two layers:

```text
RAW SOURCE RECORDS
      |
      v
CANONICAL DATA        structural normalization only
      |
      v
DERIVED FOOTBALL DATA run/pass, success, explosiveness, game state, etc.
```

The canonical layer must be trustworthy before any derived football concept is implemented.

## Canonical grains

### games
One row per CFBD game ID.

### drives
One row per CFBD drive ID. `game_id` is a foreign key to canonical games.

### plays
One row per CFBD play/event ID. `game_id` and `drive_id` retain the source relationships.

Raw IDs are never replaced with locally generated IDs.

## Canonical changes that are allowed

- deterministic field renaming (for example `gameId` -> `game_id`)
- stable data types
- explicit parsing of source timestamps/clocks while retaining the source value
- standardized null representation
- adding provenance columns such as source, source season/week partition, and raw checksum
- stable column ordering
- Parquet storage for efficient downstream querying

## Changes that are NOT canonicalization

These belong in a later derived layer and must not be added while building canonical tables:

- deciding whether a record is a competitive snap
- run/pass classification
- success rate
- explosiveness
- garbage time
- havoc
- turnover attribution beyond the literal source field/text
- red-zone/goal-to-go inference
- expected points
- win probability
- opponent adjustments
- ratings

## Validation standard

Canonicalization must be lossless with respect to source meaning. For every partition we should prove:

1. canonical row count equals raw row count for each entity
2. canonical source IDs are unique wherever raw source IDs are unique
3. every canonical row retains a traceable source partition
4. game -> drive -> play relationships reconcile exactly
5. no source record is silently removed
6. no source null is silently imputed
7. deterministic rebuilds produce the same canonical output
8. all type/coercion failures are reported explicitly

## Implementation order

1. Run a corpus-wide source census.
2. Freeze the observed raw field/value catalog.
3. Define canonical schemas for games, drives, and plays.
4. Canonicalize one known game.
5. Reconcile that game manually and automatically.
6. Canonicalize one complete week.
7. Canonicalize 2025.
8. Backfill the remaining validated raw corpus.
9. Only then begin derived football classifications.

## Storage layout

```text
data/canonical/
  season=2025/
    season_type=regular/
      week=01/
        games.parquet
        drives.parquet
        plays.parquet
        manifest.json
```

The raw directory is immutable input. Canonical builds may be deleted and rebuilt from raw data at any time.
