# 2026 Preseason Creator Chart Pack

This document is the editorial companion to the public `/charts` route.

The goal is not to hand creators a spreadsheet of metrics. The goal is to give them a small set of original, defensible stories that can be used in a video, podcast, article, or social post.

## Analytical basis

- Season basis: 2025.
- Full-season team profiles: schedule-adjusted offense and defense ratings using ridge 40 and home ridge 20.
- Game-level performance over expectation (POE): the target game is removed from the fit before the expected value is calculated.
- Validated core metrics used for the main charts:
  - Success rate
  - Rush success rate
  - Pass success rate
  - Explosive-play rate
  - Yards per play
- Positive POE means the selected unit performed better than the schedule-adjusted expectation.
- These charts describe 2025 performance and coaching fingerprints. They are not direct 2026 projections.

## Chart 1 — Michigan game-by-game POE

**Best use:** season retrospectives, Michigan 2026 setup videos, identifying games worth taking to film.

The public chart lets the creator switch between offense/defense and all five validated metrics. Each game is graded against an expectation that excludes that game from the rating fit.

### Talking points

- Ohio State was not merely a difficult matchup. Michigan still performed 17.4 percentage points below offensive success-rate expectation, 16.2 points below rush-success expectation, and 19.1 points below pass-success expectation.
- USC was the clearest defensive collapse through the air. Michigan's pass-success defense finished 22.7 percentage points worse than expectation even after USC's offensive strength was accounted for.
- Wisconsin was Michigan's cleanest across-the-board offensive game among the validated core metrics: +9.8 pp success, +6.2 pp rush success, +15.2 pp pass success, +3.2 pp explosive rate, and +1.27 yards/play versus expectation.
- Washington was a strong example of Michigan beating a quality matchup: +3.0 pp success, +7.8 pp pass success, +3.7 pp explosive rate, and +0.50 yards/play on offense.

## Chart 2 — Oklahoma: efficiency without consistency

**Best use:** Darren Talks Ball-style film breakdown or any segment explaining why box-score efficiency can mislead.

Michigan's offense against Oklahoma:

- Success-rate POE: -13.3 pp
- Rush-success POE: -11.4 pp
- Pass-success POE: -16.6 pp
- Explosive-play POE: -2.8 pp
- Yards-per-play POE: +0.50

The story is that a few productive plays can keep yards per play afloat while an offense repeatedly loses the down-to-down battle. This is exactly why SOAR should show multiple opponent-adjusted dimensions rather than a single efficiency rank.

## Chart 3 — Michigan offense vs Utah offense

**Best use:** Jason Beck transition discussion.

The chart compares Michigan and Utah by national percentile across the five validated opponent-adjusted offensive metrics.

The correct framing is not “Michigan becomes Utah.” It is:

> What statistical traits repeatedly showed up in the offense Beck operated, and which of Michigan's existing strengths or weaknesses are most compatible with that system?

Pair the chart with film on run structure, quarterback involvement, passing answers, and how the offense creates explosive plays without sacrificing down-to-down efficiency.

## Chart 4 — Michigan defense vs BYU defense

**Best use:** Jay Hill transition discussion.

The chart compares Michigan and BYU by national percentile across the five validated opponent-adjusted defensive metrics.

The correct framing is not “Michigan inherits BYU's ranking.” It is:

> Where did Hill's defense separate itself statistically, and which of those differences look system-driven versus personnel-driven?

The USC game is an obvious supporting case study because Michigan's pass-success defense was 22.7 percentage points worse than opponent-adjusted expectation.

## Chart 5 — Big Ten power map

**Best use:** College Football with Sam-style Big Ten tiers, power rankings, schedule discussions, and playoff-path videos.

The map plots every Big Ten team using:

- X-axis: 2025 opponent-adjusted offense score
- Y-axis: 2025 opponent-adjusted defense score

Top-right represents teams that were strong on both sides of the ball. This gives more context than a one-dimensional power ranking because a creator can immediately distinguish offense-led, defense-led, complete, and flawed teams.

A full Big Ten table is included under the visual with national offense, defense, and overall ranks.

## Suggested creator use

### Darren-style packet

1. Michigan game-by-game POE
2. Oklahoma efficiency-without-consistency chart
3. Michigan vs Utah offensive fingerprint
4. Michigan vs BYU defensive fingerprint
5. USC pass-defense talking point

### Sam-style packet

1. Big Ten power map
2. Big Ten opponent-adjusted ranking table
3. Michigan game-by-game POE
4. Michigan vs Utah / BYU coaching handoff charts
5. Washington and Ohio State opponent-adjusted case studies

## Public-route behavior

`/charts` is designed so a creator can:

- understand the chart without opening methodology first;
- see the exact talking point directly below the visual;
- download the desktop chart as an SVG for use in editing software;
- use a mobile-friendly fallback when viewing on a phone;
- distinguish full-season adjusted team strength from leave-one-game-out game POE.

The route should never imply creator endorsement, partnership, or affiliation unless one is explicitly established.
