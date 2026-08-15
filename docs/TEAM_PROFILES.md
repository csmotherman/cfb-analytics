# Team Profile & Identity System

**Status:** RESEARCH SCAFFOLD  
**Definition version:** `team-profile-v1-research`

## Goal

Turn serious football analytics into a fan-facing team identity product without weakening the underlying metric discipline.

Each current team should eventually show:

- offense and defense grades;
- style/identity sliders;
- a primary and optional secondary archetype nickname;
- three closest historical team-season comparables;
- a similarity score plus reasons the teams match;
- strengths, weaknesses, and notable identity differences.

## Design principle

The profile layer is separate from the prediction engine.

Prediction answers:

> Who should win, and by how much?

Profiles answer:

> What kind of football team is this, what does watching it feel like, and which past teams resemble it?

## Profile sections

### Offense

- Run Efficiency
- Pass Efficiency
- Success Rate
- Explosiveness
- Drive Scoring Efficiency / opponent-adjusted PPD
- Finishing
- Turnover Avoidance
- Third-Down Efficiency
- future: early-down efficiency, red-zone detail, consistency

### Defense

- Run Defense
- Pass Defense
- Explosive Prevention
- Drive Suppression / opponent-adjusted PPD prevented
- Havoc
- Turnover Creation
- Third-Down Defense
- future: red-zone detail, drive consistency

### Style

- Run Tendency
- Pass Tendency
- Tempo
- Plays per Possession
- future: Aggressiveness
- future: Drive Consistency
- future: Drive Volatility

## Cross-era normalization

Historical comparison must not use raw values directly across seasons. Each profile metric is first converted into a **season-relative percentile**.

That means a 2014 passing efficiency profile and a 2025 passing efficiency profile are compared by how extreme each was relative to its own season environment.

Grades are also derived from these percentiles using the profile grading scale.

## Historical DNA

Every current team can be represented as a fingerprint vector of season-relative metric percentiles.

The similarity engine compares that vector against historical team-seasons and returns the top three nearest profiles.

The initial implementation uses transparent weighted Euclidean distance over percentile features. Similarity is an index, not a calibrated probability.

Two future comparison modes are planned:

1. **Overall similarity** — style + quality + offense + defense.
2. **Style similarity** — how similarly the teams play regardless of overall quality.

Each result should explain itself with the closest traits and biggest differences.

## Fan-facing archetypes

Archetypes are explainable rules over percentile traits, not manually assigned labels.

Initial examples include:

- Air It Out
- Ground & Pound
- Death by a Thousand Cuts
- Track Meet
- Rock Fight
- Boom or Bust
- Brick Wall
- Chaos Merchant
- Possession Vampire
- Red Zone Assassin
- Between-the-20s Merchant
- Metronome

A team may receive a primary and secondary archetype when multiple identities clearly apply.

Example:

```text
AIR IT OUT

Pass Tendency         95th percentile
Explosiveness         85th percentile
Turnover Avoidance    30th percentile
Drive Suppression     25th percentile

Pass-heavy, explosive and willing to live with chaos while the defense struggles to get stops.
```

## Metric statuses

Profile dimensions are intentionally labeled by maturity:

- `READY` — can be built from already validated metric families;
- `RESEARCH` — usable for profiles but still research-only analytically, such as opponent-adjusted Drive PPD;
- `PARTIAL` — concept exists but source semantics are not fully complete;
- `PLANNED` — profile contract reserves the dimension before implementation.

The fan layer must never silently invent missing metrics.

## Output vision

A future profile record should resemble:

```json
{
  "season": 2026,
  "team": "Example",
  "grades": {
    "run_efficiency_off": {"percentile": 88.2, "grade": "A-"},
    "pass_efficiency_off": {"percentile": 94.1, "grade": "A"}
  },
  "archetypes": [
    {"name": "Air It Out"}
  ],
  "historicalComparables": [
    {"season": 2021, "team": "Historical A", "similarity": 92.1},
    {"season": 2019, "team": "Historical B", "similarity": 89.4},
    {"season": 2018, "team": "Historical C", "similarity": 86.7}
  ]
}
```

## Current implementation

`src/cfb_analytics/profiles/` contains:

- `contract.py` — profile taxonomy and metric maturity;
- `grades.py` — season-relative percentiles and letter grades;
- `similarity.py` — explainable historical nearest-neighbor comparisons;
- `archetypes.py` — initial fan-facing identity rules.

This is the organizational foundation. The next implementation step is a profile adapter/materializer that maps actual team-season metric stores into the contract and produces historical fingerprints for every eligible team-season.
