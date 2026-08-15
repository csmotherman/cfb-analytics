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

## Historical discovery corpus

Archetype discovery uses every eligible in-season team state from the available 2014–2025 corpus. The repository has no 2020 season, so it is intentionally absent. A team contributes snapshots after the configured minimum number of games rather than only one final-season average.

Each snapshot contains:

- season-to-date baseline;
- rolling recent-game state (default last four games);
- opponent-adjusted quality ratings;
- descriptive style measures;
- current-vs-baseline trajectory;
- derived identity contrasts.

This allows the same team-season to move between identities as it evolves.

## Opponent-adjusted quality contract

Every performance/quality dimension used by v2 archetype discovery is opponent-adjusted.

The generic model is:

```text
Observed metric(team offense vs opponent defense)
    = league mean
    + offense effect(team)
    - defense effect(opponent)
```

Team-game observations are weighted by their actual opportunity denominator and shrunk toward average. The current v2 adjusted families are:

- run efficiency;
- pass efficiency;
- overall success;
- explosiveness;
- third-down efficiency;
- finishing / points per scoring opportunity.

Higher offensive effect means better offense. Higher defensive effect means better suppression.

The dedicated opponent-adjusted Drive PPD model remains a separate research metric and can be added to the profile adapter after its snapshot integration is deliberately wired.

## Style is not opponent-adjusted

Behavioral dimensions such as rush rate and pass rate describe what a team chooses to do, not whether it succeeds against a difficult opponent. They therefore remain descriptive and are normalized within context rather than opponent-adjusted.

Current safe style fields:

- rush tendency;
- pass tendency;
- plays per possession.

Tempo, aggressiveness, drive consistency and drive volatility remain partial/planned until their historical definitions are complete.

## Bad teams are valid archetypes

Archetypes are not awards. A team can be historically distinctive because it is:

- excellent at running and terrible at passing;
- strong against the pass and weak against the run;
- explosive but inefficient down-to-down;
- good on offense and terrible on defense;
- poor on offense but difficult to score against;
- effective between the 20s but bad at finishing;
- broadly bad but unusually one-dimensional.

The discovery layer therefore keeps absolute opponent-adjusted quality information **and** relative-shape information.

## Identity contrasts

The snapshot layer derives shape fields including:

```text
Run-vs-pass offensive quality
Run-vs-pass defensive quality
Explosive-vs-methodical offense
Finishing-vs-foundation offense
Offense-vs-defense balance
Rush-vs-pass tendency
Overall offensive quality
Overall defensive quality
```

These help separate “how good” from “what kind of team.”

## Hierarchical archetype discovery

The old v1 pass allowed silhouette score to select one global cluster count and naturally collapsed the corpus to six broad quality neighborhoods. Those six groups are not treated as final fan archetypes.

v2 uses two levels:

```text
Broad family
    -> multiple sub-archetypes
```

Default discovery:

- 6 broad families;
- 2–5 sub-archetypes inside each family;
- approximately 12–30 final archetypes depending on historical support;
- each team-season receives equal total clustering weight even if it contributes a different number of weekly snapshots.

The subcluster selector considers silhouette separation, minimum cluster size and a small complexity reward so the system does not always collapse toward the fewest possible groups.

Clusters remain anonymous (`F00-A00`, etc.) until their signature traits and representative historical team-weeks are inspected. Fan names such as **Air It Out**, **Possession Vampire**, **Rock Fight**, **Boom or Bust**, or entirely new names are attached only after the football shape is understood.

## Form / modifier layer

Trajectory is separate from the base archetype. Future presentation can combine them:

```text
AIR IT OUT — SURGING
ROCK FIGHT — VOLATILE
GROUND & POUND — FADING
```

A team is not forced into a new base archetype merely because it had a short hot or cold stretch.

## Turnover discipline

Production turnover counts are valid, but no turnover-rate denominator is locked. Therefore v2 does **not** invent turnover avoidance or turnover creation rates for profile clustering. Those dimensions remain deferred until their opportunity denominator is independently validated.

The same rule applies to any future fan-facing metric: missing semantics are surfaced, not guessed.

## Historical DNA

The eventual current-team card will expose three closest historical team states or team-season profiles. Comparison will use season/context-relative normalized fingerprints so different scoring eras remain comparable.

Two similarity modes remain useful:

- **Overall DNA:** quality + identity + style.
- **Style DNA:** behavior/shape with much less weight on absolute quality.

## Research outputs

Build snapshots:

```bash
python -m cfb_analytics.profiles.snapshots
```

Output:

```text
data/processed/derived/profiles/identity_snapshots_v2_oa.json
```

Discover historical archetypes:

```bash
python -m cfb_analytics.profiles.discovery
```

Output:

```text
data/processed/derived/profiles/archetype_discovery_v2_oa.json
```

The first useful review artifact is the concise terminal report showing every broad family, its final sub-archetypes, strongest traits, and representative historical team-weeks.
