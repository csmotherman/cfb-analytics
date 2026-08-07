# SOAR Rating System Specification

Version: 1.0

---

# Vision

SOAR is not designed to be another advanced statistics website.

Most analytics answer:

> "What happened?"

SOAR answers:

> "Who is this football team?"

Every rating should tell a story that any fan can understand while still being rooted in advanced football analytics.

Every score should be:

- Explainable
- Opponent Adjusted
- Stable
- Predictive
- Transparent

Users should never need to understand EPA, PPA, or Success Rate in order to understand SOAR.

Instead they should see ratings like:

- Ground Power
- Air Attack
- Aggressiveness
- Consistency
- Discipline
- Game Control

Each rating can then be clicked to reveal exactly how it was calculated.

---

# SOAR Philosophy

Raw statistics never become ratings.

Instead:

Raw Stats

↓

Derived Metrics

↓

Opponent Adjusted Metrics

↓

Standardized Scores

↓

SOAR Ratings

↓

Overall SOAR Rating

Every component is adjusted BEFORE being combined.

---

# Rating Framework

Every rating must contain six sections.

## 1. Purpose

What question does this rating answer?

---

## 2. Inputs

Which metrics are used?

---

## 3. Formula

How are the metrics combined?

---

## 4. Sanity Checks

Which teams should score highly?

Which teams should score poorly?

What should NOT influence this rating?

---

## 5. Opponent Adjustment

How is schedule strength incorporated?

---

## 6. Website Explanation

Plain English explanation shown to users.

---

# =====================================================
# CORE RATINGS
# =====================================================

---

# Overall SOAR

Purpose

Overall team strength.

Built From

- Offensive Rating
- Defensive Rating
- Special Teams
- Discipline
- Game Control

---

# Offensive Rating

Purpose

Overall offensive quality.

Built From

- Efficiency
- Ground Power
- Air Attack
- Explosiveness
- Finishing
- Consistency
- Aggressiveness

---

# Defensive Rating

Purpose

Overall defensive quality.

Built From

- Resistance
- Run Defense
- Pass Defense
- Disruption
- Containment
- Red Zone Defense
- Consistency

---

# =====================================================
# OFFENSIVE RATINGS
# =====================================================

---

# Efficiency

Purpose

Can the offense consistently stay ahead of schedule?

Inputs

- Success Rate
- PPA/Play
- Yards/Play
- Standard Down Success
- Passing Down Success

---

# Ground Power

Purpose

Can the offense run the football regardless of situation?

Inputs

- Rush Success
- Rush PPA
- Yards per Carry
- Stuff Rate
- Goal Line Success
- Power Success
- Explosive Run Rate

---

# Air Attack

Purpose

How effective is the passing game?

Inputs

- Pass Success
- Pass PPA
- Yards per Attempt
- Sack Rate
- Explosive Pass Rate
- Interception Rate

---

# Explosiveness

Purpose

How dangerous is every snap?

Inputs

- Explosive Run Rate
- Explosive Pass Rate
- Explosive Drive Rate
- PPA Distribution

---

# Consistency

Purpose

How repeatable is offensive success?

Inputs

- Drive-to-drive variance
- Game-to-game variance
- Three-and-Out Rate
- Success Rate variance
- Scoring Drive variance

---

# Finishing

Purpose

How well does the offense convert opportunities into points?

Inputs

- Points per Drive
- Points per Opportunity
- Red Zone TD Rate
- Goal-to-Go Success

---

# Aggressiveness

Purpose

How willing is the offense to create high-risk/high-reward situations?

Inputs

- Fourth Down Attempts
- Tempo
- Explosive Play Rate
- Early Down Passing
- Deep Pass Rate

---

# Physicality

Purpose

Can the offense impose itself?

Inputs

- Stuff Rate
- Power Success
- Goal Line Success
- Short Yardage Success
- Rush Success

---

# =====================================================
# DEFENSIVE RATINGS
# =====================================================

---

# Resistance

Purpose

Overall defensive efficiency.

Inputs

- Success Allowed
- PPA Allowed
- Yards per Play Allowed

---

# Run Defense

Purpose

Ability to stop the run.

Inputs

- Rush Success Allowed
- Rush PPA Allowed
- Stuff Rate
- Explosive Runs Allowed

---

# Pass Defense

Purpose

Ability to stop the pass.

Inputs

- Pass Success Allowed
- Pass PPA Allowed
- Explosive Pass Allowed
- Sack Rate

---

# Disruption

Purpose

Ability to create negative plays.

Inputs

- Havoc
- Sacks
- Tackles for Loss
- Interceptions
- Forced Fumbles

---

# Containment

Purpose

Ability to eliminate explosive plays.

Inputs

- Explosive Plays Allowed
- Long Drive Prevention
- Big Play Prevention

---

# Red Zone Defense

Purpose

Can the defense force field goals?

Inputs

- Red Zone TD Allowed
- Points per Opportunity Allowed

---

# Defensive Consistency

Purpose

How often does the defense avoid collapsing?

Inputs

- Drive variance
- Success variance
- Explosive variance

---

# =====================================================
# TEAM TRAITS
# =====================================================

---

# Discipline

Purpose

Avoid self-inflicted mistakes.

Inputs

- Penalties
- Penalty Yards
- Turnovers
- Negative Plays

---

# Game Control

Purpose

How much does a team dictate the game?

Inputs

- Field Position Margin
- Success Margin
- Points per Drive Margin
- Possession Advantage

---

# Resilience

Purpose

Performance after adversity.

Inputs

- Response after turnover
- Response after opponent score
- Performance while trailing
- Comeback ability

---

# Closing Ability

Purpose

Performance while leading.

Inputs

- Offensive Success While Leading
- Defensive Success While Leading
- Clock Control
- Turnover Avoidance

---

# Clutch

Purpose

Performance in high leverage moments.

Inputs

- Fourth Quarter
- One-score games
- Third Downs
- Red Zone
- Final Possessions

---

# Momentum

Purpose

Ability to completely change games.

Inputs

- Scoring Runs
- Defensive Stop Runs
- Win Probability Swings

---

# Adaptability

Purpose

Ability to adjust.

Inputs

- Second Half Improvement
- Counter-adjustments
- Performance vs different defensive styles

---

# Decision Quality

Purpose

Evaluate football decisions.

Inputs

- Fourth Down Decisions
- Punt Decisions
- Field Goal Decisions
- Expected Points Added
- Win Probability Added

---

# =====================================================
# OPPONENT ADJUSTMENT
# =====================================================

Every component should be adjusted individually.

Example

Raw Rush Success

↓

Opponent Adjusted Rush Success

NOT

Raw Rating

↓

Opponent Adjusted Rating

Opponent adjustment happens BEFORE ratings are calculated.

---

# =====================================================
# WEBSITE DESIGN
# =====================================================

Every rating should be clickable.

Example

Ground Power

92

↓

Ground Power

Overall Rating

92

Built From

Rush Success ............ 95
Rush PPA ................ 91
Yards/Carry ............. 88
Stuff Rate .............. 90
Power Success ........... 94
Goal Line ............... 92
Explosive Runs .......... 81

Opponent Adjusted

YES

National Rank

#6

Confidence

97%

Description

Michigan consistently creates positive rushing plays, converts short-yardage situations at an elite rate, and rarely allows defenses to generate negative rushing plays.

---

# =====================================================
# DEVELOPMENT ORDER
# =====================================================

Phase 1

✓ Team Game Stats

Phase 2

- Rushing Metrics
- Passing Metrics
- Situational Metrics
- Tempo
- Havoc
- Finishing Drives

Phase 3

- Team Season Stats

Phase 4

- Opponent Adjustment

Phase 5

- Core SOAR Ratings

Phase 6

- Advanced Ratings

Phase 7

- Historical Comparisons

Phase 8

- Projections

---

# GOAL

Every fan should be able to answer:

How good is this team?

Why are they good?

What style do they play?

What are they elite at?

What are they weak at?

How do they compare to everyone else?

without ever needing to understand advanced football analytics.