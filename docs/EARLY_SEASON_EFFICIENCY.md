# Early-season efficiency rankings v1

Research-only descriptive rankings for 2026. The user's scope is all completed games involving FBS teams, including FCS opponents, without opponent adjustment. The September 8 snapshot contains 99 games, all source Week 1. This analysis extends the drive-points report without replacing it or the historical early-season signal study.

## Ranking contract

`early-season-efficiency-v1` reports nine metric families, each with offense, defense-allowed and net values, competition ranks, average-rank percentiles and cohort sizes:

- Success rate, pass success rate, rush success rate: locked Success Rate v1.
- Explosive-play rate, pass explosive rate, rush explosive rate: locked Explosiveness v1.
- EPA/play, EPA/pass, EPA/rush: independent SOAR EPA research, with the explicitly versioned ranking cohort below.

Offensive rates are higher-is-better; defensive allowance rates are lower-is-better. Net is offensive rate minus defensive allowance. Numerators and denominators are pooled across games. No averaging of game averages, opponent adjustment, preseason prior, or additional garbage-time filter is used. Only FBS teams enter rank/percentile cohorts; the opponent can be FCS. Ties share competition ranks (1, 1, 3) and receive the mean percentile of their tied positions. Unavailable values stay null. Rates are ranked before display rounding. Net success/explosive rates are percentage-point differences.

The **EPA-inclusive composite** is 50% success-rate percentile, 25% explosive-play-rate percentile, and 25% EPA/play percentile on each side. Overall is the arithmetic mean of the offensive and defensive scores. Defensive percentiles reward lower allowance. All six components use the same complete-case team cohort. Scores run from 0 to 100; these are weighted percentile scores, not win probabilities or calibrated power ratings. EPA/pass and EPA/rush are separate diagnostic rankings and are not added again to the overall score. Total points, PPD and number of possessions have no direct weight.

The **process-only companion** is 50% success-rate percentile and 50% explosive-play-rate percentile on each side, averaging offense and defense for overall. It uses its own complete-case cohort and remains available when EPA is withheld. No composite silently drops or reweights a missing component.

Weights are explicit analyst choices, not trained coefficients. These metrics overlap, particularly EPA and success rate; the blend is not evidence of independent predictive contributions. One-game schedules, FCS matchups, backup usage, field position and turnovers can still dominate observed rates. Without opponent adjustment, this cannot establish which team is intrinsically better.

## EPA model and cohort

Expected points use the existing `NextScoreExpectedPoints` / `epa-v2-research-next-score` model: hierarchical empirical estimates from down, distance, field position and time remaining in the half, with minimum count 50 and the existing fallback hierarchy. The model is fit on 2021–2025 canonical historical FBS-versus-FBS partitions. No 2026 play contributes to model training. CFBD PPA is neither a training target nor a requirement for a play to receive EPA.

The model artifact stores all sufficient statistics, training seasons, source hashes, EP source-code fingerprint and minimum count. Fitting proceeds partition by partition to avoid loading the entire corpus simultaneously. The saved fit can be reused while ranking/report code evolves, provided its training inputs and model implementation match.

`epa-v2-ranking-transitions-v1` is a new, research-only application of that EP surface, distinct from the earlier matched EPA/PPA benchmark cohort:

1. Canonical chronology remains drive number, play number, play ID. Source-identifiable passes, sacks, interceptions (including return records), rushes, and fumble/recovery records with explicit pass/sack/rush/run evidence form the candidate cohort. No-play contexts are excluded. Source-labeled quarterback runs remain rushing; no scramble/design inference is made.
2. Standalone recoveries without identifiable offensive action are not assigned to a family. Special-teams plays and conversions are not independently included. EPA/pass is therefore a research source-record denominator, not a redefinition of locked Dropbacks v1. Locked success/explosiveness continue to use their own classifiers and denominators, including their existing modifier exclusions.
3. Candidate records sharing drive, offense, period, clock, down, distance and field position are withheld as duplicate/disputed start states. Neither record is guessed to be authoritative. This safeguard does not modify the locked success/explosiveness classifiers.
4. A play must have a valid regulation EP state. Expected points after the play use the next eligible canonical state, oriented to the current offense. At a half boundary or after the last eligible state, future EP is zero rather than carrying value into the next half. Overtime has no trained state surface and is excluded.
5. Observed points are score changes entering the current record from the immediately preceding canonical record, oriented to the current offense. Negative scoreboard corrections, changes above eight points, simultaneous scoring by both teams, and changes on nonscoring records are withheld. Offensive touchdown deltas must be +6/+7/+8; interception/fumble return TD deltas must be -6/-7/-8. Scoring without a prior scoreboard state is unresolved.
6. EPA = oriented observed points + oriented next-state EP − current-state EP. Sacks/interceptions count against passing; an opponent return touchdown is negative offensive value and an equivalent negative allowance for the defense. A turnover at halftime has no future-possession EP beyond that half.
7. The prior drive-points audit identified unreconciled scoring in UAB–Illinois and Ole Miss–Louisville. Those games retain success and explosiveness, but EPA is withheld for both teams. Those four teams also have null EPA-inclusive composite ranks. No points or source records are manually changed.

Raw candidate counts, scored counts, split counts and exclusion counts are preserved. Coverage is relative to this source-identifiable candidate cohort, not to official box-score attempts. The historical EPA-v2 benchmark figures in the metric registry do **not** validate the extended cohort or transition guards. State coverage, special-team boundary behavior, source ambiguity and early-season variance remain research limitations.

## Artifacts and validation

Run from the repository root:

```bash
.venv/bin/python -m cfb_analytics.analytics.early_season_efficiency
```

This is an explicit 2026 snapshot analysis, not a live-refresh publisher. Inputs are the isolated broad-scope canonical plays and completed-game/scoring audit from `unadjusted_drive_rankings/2026`. Outputs live in `data/research/early_season_efficiency/2026/`:

- `report.md`: overview, full overall composite table and all nine offensive/defensive/net EPA views.
- `composite.md`, `process.md`: separate overall, offense and defense rankings.
- `success.md`, `passSuccess.md`, `rushSuccess.md`, `explosive.md`, `passExplosive.md`, `rushExplosive.md`, `epa.md`, `passEpa.md`, `rushEpa.md`: full metric rankings, with play denominators.
- `coverage.md`: offensive and defensive EPA candidate/scored coverage by team.
- `rankings.json`: machine-readable ranks, values, percentiles, sample counts, game aggregates, scored EPA plays, exclusions, provenance and audit checks.
- `epa_model.json`: reproducible historical model sufficient statistics and provenance.

Checks require unique game/team rows, unique scored EPA plays, completed-game play coverage, exact offense/defense mirrors including FCS rows, EPA pass/rush denominator and numerator reconciliation, candidate/scored/excluded reconciliation, and season totals matching game totals. Tests cover direction and ties, pooled rates, FCS inclusion, missing EPA handling, score guards, terminal-half treatment, turnover orientation, sack/pass classification, duplicate states, and independence from PPA.
