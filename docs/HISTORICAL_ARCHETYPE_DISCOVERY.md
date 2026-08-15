# Historical Archetype Discovery

**Status:** RESEARCH ONLY  
**Definition version:** `historical-archetype-discovery-v1-research`

## Goal

Discover the recurring ways college-football teams actually look during seasons from 2014 through 2025 (2020 absent from the corpus), rather than inventing a fixed list of nicknames from full-season averages.

A team can change identity during a season. The historical discovery pool therefore uses **in-season snapshots** instead of one row per team-season.

## Snapshot design

For every team appearance after four games, the system creates:

- **baseline state:** season-to-date metrics through that game;
- **current state:** rolling last-four-game metrics;
- **trajectory:** current percentile minus baseline percentile.

This means a team that starts slowly and becomes explosive later in the year contributes both states to the historical identity library.

Early-season states are normalized only against teams in the same season/partition. A Week 5 profile is not ranked against another team's final-season profile.

## Discovery-safe dimensions

The first discovery pass uses only fields with explicit reconstructable denominators from the current team-game stores:

- offensive run success efficiency;
- offensive pass success efficiency;
- overall offensive success;
- offensive explosiveness;
- finishing points per resolved scoring opportunity;
- third-down offensive efficiency;
- run-defense suppression;
- pass-defense suppression;
- explosive-play prevention;
- finishing defense;
- third-down defense;
- run/pass tendency;
- plays per possession.

Dimensions are automatically excluded when coverage falls below the configured threshold.

Opponent-adjusted Drive PPD, havoc, aggressiveness, turnover tendency, tempo, and direct drive-consistency measures can join later when their snapshot adapters/denominators are deliberately defined. The archetype pipeline must not invent missing analytics.

## Unsupervised discovery

`profiles.discovery` fits K-Means over the historical current-state percentiles, optionally adding downweighted trajectory features.

It evaluates a range of cluster counts (default 6 through 24) and selects the strongest silhouette score. The output stores:

- every tested `k` and silhouette score;
- selected cluster count;
- cluster prevalence;
- percentile center for every football dimension;
- strongest signature traits;
- five closest historical snapshot exemplars;
- assignment for every historical snapshot.

**Clusters are intentionally unnamed.** The data discovers the football shapes first. We inspect those shapes and only then assign fan-facing names such as `Air It Out`, `Rock Fight`, or new identities we did not anticipate.

This avoids forcing historical teams into a preconceived taxonomy.

## Why recent form and baseline are separate

The archetype itself should describe what the team looks like **now**. Season-to-date baseline answers what the team has been overall. The difference between the two supports trajectory tags later, for example:

- Surging
- Fading
- Reinvented
- Stabilizing
- Volatile

Those should be secondary tags, not replacements for the core football archetype.

## Build

```bash
python -m cfb_analytics.profiles.snapshots
python -m cfb_analytics.profiles.discovery
```

Outputs:

```text
data/processed/derived/profiles/
    identity_snapshots_v1.json
    archetype_discovery_v1.json
```

The discovery report printed to the terminal lists each anonymous cluster, prevalence, strongest traits, and representative historical team-weeks. That report is the evidence we will use to create the first real archetype catalog.

## Next stage

After the first historical run:

1. inspect selected cluster count and silhouette curve;
2. inspect exemplars and signature traits for every cluster;
3. identify duplicate/split clusters that are football-equivalent;
4. decide whether offense, defense, and overall identity need separate clustering layers;
5. add opponent-adjusted PPD and other mature dimensions;
6. assign fan-facing names only after the statistical shapes are stable;
7. use cluster distance/probability-like confidence for current team profiles;
8. use the same snapshot library for top-three historical-team comparisons.
