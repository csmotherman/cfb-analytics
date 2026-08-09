# Source Audit

This is the next task. Do not build advanced metrics before completing it.

## Initial sample

Use a deliberately small collection of real games that exposes different edge cases. The first audit should include at least:

- one normal regulation game
- one overtime game
- one game with multiple turnovers
- one game with defensive scoring
- one game with unusual special-teams events

## For each game

### Game record

Compare the source record to the official final result and confirm:

- participants
- home/away designation
- week and season
- scores
- game status
- conference/classification fields if used

### Drives

Manually inspect the drive chart and confirm:

- number of drives
- offense/defense
- ordering
- start/end field position
- start/end score
- stated result
- relationship to plays

### Plays

Walk the play sequence and confirm:

- ordering
- period/clock
- offense/defense
- down/distance
- field position
- yards gained
- play type
- scoring marker
- drive linkage
- text description

## Documentation rule

Before deriving a field such as `is_success`, `is_run`, `is_pass`, `is_goal_to_go`, or `is_turnover`, add its exact definition to a future cleaning specification and include at least one real play that proves the rule.

## Acceptance criterion

We do not move from raw data into canonical cleaned data until we can explain every field we intend to depend on and reconcile sample games end-to-end.
