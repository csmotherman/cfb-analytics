# Cleaning Rules

These rules are definitions, not implementation details. Changes require tests.

## Raw data

Raw API data is never edited in place. Source values are retained in raw Parquet and converted into canonical snake_case fields in the clean layer.

## Play family

A play is classified into one primary family: `run`, `pass`, `punt`, `kickoff`, `field_goal`, `penalty`, `administrative`, `turnover`, or `other`. Sacks are treated as pass plays for dropback-style analysis. Kneels and spikes remain identifiable but are excluded from `is_competitive_offensive_play`.

## Success rate

For a competitive offensive play:

- 1st down: gain at least 50% of yards needed.
- 2nd down: gain at least 70% of yards needed.
- 3rd or 4th down: gain at least 100% of yards needed.

Plays with invalid/missing down or distance are not marked successful.

## Explosive plays

Initial thresholds:

- run: at least 12 yards
- pass: at least 16 yards

Thresholds live in settings so they can be changed explicitly.

## Standard / passing downs

Standard down:

- all 1st downs
- 2nd and 7 or fewer
- 3rd/4th and 4 or fewer

Passing down is the complement only for valid competitive offensive downs.

## Red zone

A play is a red-zone play when the offense begins at 20 or fewer yards from the opponent goal line.

## Goal-to-go

Goal-to-go is inferred when `distance >= yards_to_goal` with positive, non-null values. This handles goal-to-go after penalties beyond the 10-yard line and avoids the previous incorrect `distance <= yards_to_goal` rule. Because this is inferred from source down-distance fields, it must be spot-checked against real games.

## Field position

`field_position = 100 - yards_to_goal`, where 0 is the offense's own goal line and 100 is the opponent goal line.

## Drive outcomes

Drive points are calculated as `end_offense_score - start_offense_score`. Outcome flags are based on source score change plus normalized drive-result text.

## Validation philosophy

Errors stop the pipeline. Warnings identify plausible source anomalies that require review but are not necessarily invalid. No validation function merely prints a failure and continues.
