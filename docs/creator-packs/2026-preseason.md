# 2026 Preseason Creator Game Library

This document is the editorial companion to the public `/charts` route.

The page is intentionally organized **game by game**. A creator or viewer first chooses a Michigan game from 2025, then gets an audience-first opponent-adjusted dossier for that matchup.

The goal is not to show the most statistics. The goal is to answer the questions a viewer actually has:

1. How good was the opponent?
2. What should Michigan have done against that opponent?
3. What did Michigan actually do?
4. How far above or below expectation was the performance?
5. How well did the opponent play relative to Michigan's own strength?
6. What is the one football story the audience should remember?

## Analytical basis

- Season basis: 2025.
- Full-season team context uses schedule-adjusted offense and defense ratings with ridge 40 and home ridge 20.
- Game-level expectations use leave-one-game-out fitting: the target game is removed before expected performance is calculated.
- The same game is graded from both directions:
  - Michigan offense versus opponent defense.
  - Opponent offense versus Michigan defense.
- Validated core metrics:
  - Success rate
  - Rush success rate
  - Pass success rate
  - Explosive-play rate
  - Yards per play
- The public page avoids unexplained analyst shorthand. `pp` should not be the primary audience label. Use **percentage points**.

## Public language rules

### Percentage points

If actual success rate is 45% and expected success rate is 40%, the public chart says:

> 5 percentage points better than expected.

It should not say “+5 pp” without an explanation, and it should not call that a 5% increase.

### Expected

Public definition:

> What the schedule-adjusted matchup model expected this team to produce after accounting for the strength of both teams. The target game itself is removed before the expectation is calculated.

### Difference from expected

Public definition:

> Actual minus expected. It answers whether the unit played better or worse than the level the matchup called for.

## Game dossier structure

### 1. Matchup context

Before showing performance, establish the level of competition:

- Michigan adjusted offense rank.
- Opponent adjusted defense rank.
- Michigan adjusted defense rank.
- Opponent adjusted offense rank.
- Opponent overall adjusted rank.

These full-season ranks are context. They are not the game grade itself.

### 2. Metric-by-metric strength table

For each validated metric show:

- Michigan offense national rank.
- Opponent defense national rank.
- Michigan defense national rank.
- Opponent offense national rank.

The audience should know whether Michigan was facing an elite run defense, weak passing offense, explosive offense, etc. before seeing the game result.

### 3. Michigan offense: actual versus expected

For Success Rate, Rush Success Rate, Pass Success Rate, and Explosive Play Rate, show actual and expected side by side.

This answers:

> Did Michigan's offense perform better than this opponent's defense should have allowed?

### 4. Yards per play

Yards per play gets its own visualization because it has a different unit and can sometimes contradict success rate.

That contradiction is often a useful football story. A team can average acceptable yards per play because of a few large gains while still losing most downs.

### 5. Opponent offense: actual versus expected

Repeat the same process from the other side.

This answers:

> Did the opponent's offense perform better than Michigan's defensive strength should have allowed?

This is essential. The audience should not hear only that Michigan's defense played poorly. They should see whether the opponent actually exceeded an expectation that already knew Michigan's defense was strong or weak.

### 6. Two-way performance relative to expectation

Put Michigan offense and opponent offense on the same chart, metric by metric.

For example:

- Michigan Success Rate: 8 percentage points below expectation.
- Opponent Success Rate: 6 percentage points above expectation.

That immediately explains which team imposed itself on the matchup beyond what team strength alone predicted.

### 7. Plain-English takeaway

Each dossier ends with deterministic, data-backed sentences describing:

- Michigan's largest rate over/underperformance.
- Opponent's largest rate over/underperformance.
- Michigan yards-per-play versus expectation.
- Opponent yards-per-play versus expectation.
- A warning when success rate and yards-per-play point in opposite directions.

The takeaway should never invent causality. It should say what happened statistically and leave scheme/personnel causality for film or further analysis.

## Creator use

A creator should be able to open `/charts`, click one game, and build a segment from top to bottom without needing a separate spreadsheet.

Suggested flow in a video:

1. Show opponent strength context.
2. Show Michigan offense actual versus expected.
3. Show opponent offense actual versus expected.
4. Use the two-way chart to summarize who exceeded expectations.
5. Move to film to explain why.

Every exported chart should remain useful to an audience who has never heard terms like ridge regression, latent offense effect, or performance over expectation.
