# Rebuild Plan

## Why this repository was reset

The previous implementation accumulated ingestion, cleaning, feature engineering, ratings, and tests before the base datasets had been proven correct. That makes downstream results impossible to trust.

This rebuild starts before cleaning.

## Phase 0 — Source audit

Goal: understand exactly what the source returns.

For a small set of known games, inspect raw game, drive, and play records field-by-field. Record:

- field names and data types
- null behavior
- identifiers
- team naming and IDs
- clock representation
- field-position representation
- drive linkage
- play ordering
- scoring representation
- penalties
- sacks
- turnovers
- overtime
- administrative plays

No cleaning code is written in this phase.

## Phase 1 — Raw ingestion

Build the smallest possible fetch layer that saves source responses without changing football meaning.

Required outputs:

- `data/raw/<season>/games.*`
- `data/raw/<season>/drives.*`
- `data/raw/<season>/plays.*`

The raw layer must preserve source fields and source identifiers.

## Phase 2 — Raw validation

Validate source structure before transformation:

- game IDs are unique
- drive IDs are unique within their documented scope
- play IDs/order are understood
- every drive maps to a known game
- every play maps to a known game
- every play-drive relationship is understood
- home/away participants agree across tables
- counts can be reconciled against manually inspected games

## Phase 3 — Canonical games

Define one row per game. Only fields we understand are normalized. Keep raw source values available for traceability.

## Phase 4 — Canonical drives

Define one row per drive. Do not infer outcomes until source semantics have been manually verified.

## Phase 5 — Canonical play-by-play

Define one row per source play/event. Initially normalize names/types only. Add derived football flags one at a time, each with:

- written definition
- source fields
- edge cases
- real-game examples
- unit tests
- regression tests

## Phase 6 — Cross-table validation

Prove games, drives, and plays reconcile correctly.

## Phase 7 — Team-game dataset

Only after the canonical tables are trustworthy, aggregate to one row per team per game.

## Phase 8 — Season dataset

Aggregate validated team-game metrics into team-season data.

## Phase 9 — Advanced metrics

Success rate, explosiveness, havoc, finishing drives, opponent adjustment, SOAR ratings, projections, and other advanced features belong here—not earlier.
