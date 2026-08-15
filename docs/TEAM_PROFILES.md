# Team Profile & Identity System

**Status:** RESEARCH SYSTEM  
**Definition version:** `team-profile-v2-oa-identity-research`

## Product goal

Build fan-facing profiles that answer four different questions without mixing them together:

1. **Quality — how good are you?**
2. **Style — how do you choose to play?**
3. **Identity — what unusual combination of strengths, weaknesses and tendencies defines you?**
4. **Form — how different are you right now from your season baseline?**

Prediction remains separate and continues to use the locked Prediction Model v1 benchmark.

## Historical profile corpus

Profile snapshots use every eligible in-season team state from the available 2014–2025 corpus. The repository has no 2020 season, so it is intentionally absent. A team contributes snapshots after the configured minimum number of games rather than only one final-season average.

Each v3 snapshot contains:

- season-to-date baseline;
- rolling recent-game state (default last four games);
- opponent-adjusted quality ratings;
- broader rushing/passing attack and defense composites;
- descriptive style measures;
- scheme diagnostics;
- current-vs-baseline trajectory;
- derived identity contrasts.

This allows the same team-season to move between identities as it evolves.

## Opponent-adjusted quality contract

Every performance/quality dimension used by profile identity work is opponent-adjusted.

The generic model is:

```text
Observed metric(team offense vs opponent defense)
    = league mean
    + offense effect(team)
    - defense effect(opponent)
```

Team-game observations are weighted by their actual opportunity denominator and shrunk toward average. Current adjusted families include:

- run success efficiency;
- pass success efficiency;
- run explosiveness;
- pass explosiveness;
- yards on successful run plays;
- yards on successful pass plays;
- overall success;
- overall explosiveness;
- third-down efficiency;
- finishing / points per scoring opportunity.

The snapshot layer combines the run components into **Rushing Attack** and the pass components into **Passing Attack**, with parallel rushing/passing defense composites.

The dedicated opponent-adjusted Drive PPD model remains a separate research metric and can be added after its snapshot integration is deliberately wired.

## Style and scheme

Behavioral dimensions such as rush rate describe what a team chooses to do, not whether it succeeds against a difficult opponent. They remain descriptive and are normalized within context rather than opponent-adjusted.

Current safe style/scheme fields include:

- rush tendency;
- pass tendency;
- plays per possession;
- predictability;
- one-dimensionality;
- playcalling fit;
- scheme constraint.

Tempo, aggressiveness, drive consistency and drive volatility remain partial/planned until their historical definitions are complete.

## Bad teams are valid archetypes

Archetypes are not awards. A team can be historically distinctive because it is:

- excellent at running and terrible at passing;
- strong against the pass and weak against the run;
- explosive but inefficient down-to-down;
- good on offense and terrible on defense;
- poor on offense but difficult to score against;
- broadly bad but unusually one-dimensional;
- structurally constrained by a broken complementary attack.

The identity layer therefore keeps absolute opponent-adjusted quality information **and** relative-shape information.

## Identity contrasts

The snapshot layer derives fields including:

```text
Rushing Attack
Passing Attack
Rushing Defense
Passing Defense
Run-vs-pass offensive quality
Run-vs-pass defensive quality
Explosive-vs-methodical offense
Finishing-vs-foundation offense
Offense-vs-defense balance
Rush-vs-pass tendency
Predictability
One-dimensionality
Playcalling fit
Scheme constraint
Overall offensive quality
Overall defensive quality
```

These help separate “how good” from “what kind of team.”

## Two complementary archetype systems

The repository now has two different research mechanisms that answer different questions.

### 1. Unsupervised discovery

`profiles.discovery` finds anonymous recurring statistical shapes from historical snapshots. These clusters remain useful for discovering whether the data contains identities we did not anticipate.

The old v1 global clustering naturally collapsed to six broad quality neighborhoods. v2 therefore uses hierarchical broad-family -> sub-archetype discovery and equal total weight per team-season.

Anonymous clusters (`F00-A00`, etc.) should not automatically become fan names.

### 2. 2,000-name archetype ontology

`profiles.archetype_catalog` creates exactly **2,000 unique candidate build names**. Every candidate has an explicit target attribute signature rather than being a random phrase.

Examples of root identities include:

```text
Ground & Pound
Run or Die
Trench Warfare
Air It Out
Air Raid
Bombs Away
Broken Passing Game
Death by a Thousand Cuts
Boom or Bust
Playcalling Prison
Run Wall
Run Funnel
Open Highway
No Fly Zone
Pass Funnel
Open Skies
Brick Wall
Rock Fight
Defense or Bust
Outscore the Problem
```

Football modifiers such as `Elite`, `Broken`, `Predictable`, `Defense-Led`, `Run-Dependent`, `High-Ceiling`, `Miscast`, and `Well-Fit` alter the target profile in explicit ways. The result is a large fan-facing vocabulary capable of describing good, bad, asymmetric and unusual builds.

The 2,000 names are a **candidate vocabulary**, not 2,000 forced classes.

## Historical attribute matching: 2014–2024

`profiles.match_archetypes` scores each eligible v3 team-state snapshot against all 2,000 candidate signatures.

The default historical matching window is:

```text
2014, 2015, 2016, 2017, 2018, 2019,
2021, 2022, 2023, 2024
```

2020 is absent from the repository corpus and 2025 is deliberately excluded from this historical matching calibration pass.

The matcher currently uses available dimensions such as:

- rushing attack;
- passing attack;
- rushing defense;
- passing defense;
- overall offense quality;
- overall defense quality;
- rush tendency;
- plays per possession;
- explosive-vs-methodical shape;
- run/pass offensive and defensive splits;
- offense-vs-defense balance;
- predictability;
- one-dimensionality;
- playcalling fit;
- scheme constraint.

Each candidate receives a normalized weighted-distance score. The result exposes:

- top five candidate archetypes per team-week by default;
- similarity score;
- attributes that matched most closely;
- largest mismatches;
- dominant archetype for each team-season;
- final archetype for each team-season;
- dominant-share stability across the season.

This lets historical evidence determine which names are useful and which names never correspond to real college-football states.

## Form / modifier layer

Trajectory remains separate from the base build. Future presentation can combine them:

```text
AIR IT OUT — SURGING
ROCK FIGHT — VOLATILE
GROUND & POUND — FADING
```

A team is not forced into a new base archetype merely because it had a short hot or cold stretch.

## Turnover discipline

Production turnover counts are valid, but no turnover-rate denominator is locked. Therefore the profile matcher does **not** invent turnover avoidance or turnover creation rates. Those dimensions remain deferred until their opportunity denominator is independently validated.

The same rule applies to any future fan-facing metric: missing semantics are surfaced, not guessed.

## Historical DNA

The eventual current-team card can expose three closest historical team states or team-season profiles. Comparison uses season/context-relative normalized fingerprints so different scoring eras remain comparable.

Two similarity modes remain useful:

- **Overall DNA:** quality + identity + style.
- **Style DNA:** behavior/shape with much less weight on absolute quality.

## Research commands

Build v3 attack/scheme snapshots:

```bash
python -m cfb_analytics.profiles.snapshots
```

Output:

```text
data/processed/derived/profiles/identity_snapshots_v3_attack_scheme.json
```

Run anonymous historical discovery:

```bash
python -m cfb_analytics.profiles.discovery
```

Run the 2,000-name historical matcher for 2014–2024:

```bash
python -m cfb_analytics.profiles.match_archetypes
```

Output:

```text
data/processed/derived/profiles/historical_archetype_matches_2014_2024.json
```

The historical matcher output is the main artifact for evaluating which fan-facing names actually correspond to repeatable college-football team builds.
