# CFB Analytics Metric Registry

Checkpoint updated 2026-08-13.

This registry records production status, not merely whether a field exists in source data.

## Foundation

- Canonical play/drive chronology — LOCKED
- Team-game feature rows — LOCKED (17,020 rows / 8,510 games)
- Team-season feature rows — LOCKED (1,438 rows)

## Production metrics

- Success Rate v1 — LOCKED
- Explosiveness v1 — LOCKED
- Standard-down / Passing-down efficiency — LOCKED
- Third-down / Fourth-down conversions — LOCKED
- Red-zone / Goal-to-go play efficiency — LOCKED
- Tackles for Loss v1 — LOCKED
- Havoc v1 — LOCKED
- Turnover counts / margin — LOCKED
- Drive Efficiency v1 — LOCKED
- Red-zone possession efficiency — LOCKED
- Possession Yardage v1 — LOCKED
- Three-and-Out v1 counts — LOCKED; rate intentionally not produced
- First-Down Generation v1 counts — LOCKED; rate intentionally not produced
- Dropbacks / Sack Rate v1 — LOCKED
  - 553,899 dropbacks
  - 33,368 sacks
  - 6.02% corpus sack rate
- PPA / EPA — SOURCE DATA AVAILABLE
  - CFBD labels the expected-points-added value as PPA (Predicted Points Added).
  - Treat PPA as the repository's source EPA signal rather than listing EPA as missing.
  - Production aggregation, eligibility, reconciliation, and opponent-adjusted use still require their own audit before being labeled LOCKED.

## Current checkpoint

### Basic Yardage Efficiency — IN FORENSICS

Target families to establish from the canonical corpus before propagation:

- offensive / defensive yards per play
- rush yards per attempt / allowed
- pass yards per attempt or per dropback / allowed (denominator semantics must be explicit)
- yards per possession already exists through Possession Yardage v1 and must reconcile rather than be reimplemented
- game and season offense/defense mirrors

### Next after yardage

- Pace / plays per possession
- Starting field position
- Scoring-opportunity efficiency
- Early-down efficiency
- Stuff / short-yardage metrics if source semantics validate
- Raw Metrics v1 freeze
- Pregame historical snapshots
- Opponent Adjustment v1
- Prediction feature store and walk-forward models
