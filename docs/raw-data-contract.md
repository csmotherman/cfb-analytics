# Raw Data Contract

Raw means **raw**.

## Non-negotiable rules

1. Preserve source payload fields and values without football reinterpretation.
2. Never overwrite a successful historical partition in place.
3. Record acquisition metadata separately from source records.
4. Keep games, drives, and plays as separate source entities.
5. Preserve source IDs exactly so relationships can be audited later.
6. Never silently drop records because they look strange.
7. Never fill missing source values with inferred values in the raw layer.
8. Never rename a source field for convenience in the raw layer.
9. Any source/API/schema anomaly is logged, not repaired here.
10. Raw files are not committed to Git.

## Required partition manifest

Every acquisition unit must eventually produce a manifest containing at least:

- source
- season
- season_type
- week
- entity
- endpoint/request identity
- requested_at_utc
- completed_at_utc
- HTTP/result status
- record_count
- source field names/schema fingerprint
- content checksum
- writer/code version
- retry/error information

## Validation in Phase 1

Validation asks only whether acquisition is complete and internally auditable. It does not decide whether a play was a rush, successful, explosive, garbage time, etc.

Examples of valid raw checks:

- file can be read
- payload is structurally valid
- expected partition manifest exists
- record count is recorded
- IDs required by the source payload are preserved
- duplicate source IDs are reported
- drive game IDs can be audited against acquired games
- play game/drive IDs can be audited where supplied by the source
- checksum matches stored content

A raw validation failure must never be fixed by silently modifying source values.
