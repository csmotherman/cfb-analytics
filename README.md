# CFB Analytics

Reliability-first college football analytics built from preserved CollegeFootballData play-by-play.

## Current checkpoint

Historical corpus: `2014–2019, 2021–2025`.

Validated derived foundation:

- 8,510 games
- 17,020 team-game rows
- 1,438 team-season rows
- canonical games, drives, plays, and possession chronology
- production audits requiring offense/defense and team-game/team-season reconciliation

The authoritative production metric contract is `docs/METRIC_REGISTRY.md`.

Predictive research now also includes leakage-safe pregame snapshots, directional matchup features, iterative offense/defense ratings, and least-squares SRS. These predictive features are versioned research artifacts and are not production-locked merely because their audits pass.

## Predictive research checkpoint

Current model-feature direction contract: `model-feature-direction-v1`.

Current schedule-adjusted research systems:

- `iterative-ratings-v2-directional`
- `srs-v1-least-squares`
- versioned enriched model cache with source-data fingerprinting

The iterative system fits six opponent-adjusted metric families: Success, Explosiveness, Yards Per Play, Yards Per Possession, Finishing Drives, and Field Position. Higher iterative offense means better offense; higher iterative defense means stronger defense. Matchup edges therefore use offense minus opposing defensive strength.

SRS is a separate scoreboard-strength feature. Each completed game contributes a `+1/-1` team-opponent equation against home-minus-away scoring margin, and all team ratings are solved simultaneously by least squares subject to zero-centered connected schedule components. Pregame SRS snapshots use only completed partitions strictly before the game being predicted.

For learning, SRS currently contributes the non-redundant feature:

```text
srsEdge = homeSrs - awaySrs
```

### 2025 enriched-model audit checkpoint

The validated 2025 cache produced:

- 1,616 team-game source rows
- 808 model rows
- 586 rows eligible with 3+ prior games for both teams
- 519 rows eligible with 4+ prior games for both teams
- 725 rows with an SRS edge
- maximum SRS normal-equation residual: `7.459e-09`
- maximum connected-component mean absolute rating: `1.184e-15`

All audited checks passed, including unique game rows, source reconciliation, version checks, iterative convergence, SRS convergence, prior-game counts, SRS edge arithmetic, normal-equation reconciliation, connected-component centering, finite SRS values, and valid targets.

The enriched dataset is cached by season. The cache is reused only when the source team-game fingerprint and feature-version contract match; otherwise it is regenerated and re-audited.

```bash
python -m cfb_analytics.analytics.iterative_ratings --season 2025
```

A first valid build reports `Cache: WRITTEN`; an unchanged repeat reports `Cache: REUSED`.

## Architecture

```text
CFBD REST JSON
    -> raw evidence
    -> canonical games / drives / plays
    -> validated possessions and event semantics
    -> team-game analytics
    -> team-season analytics
    -> leakage-safe pregame features
    -> iterative ratings + SRS
    -> cached enriched model rows
    -> walk-forward predictive evaluation
```

Raw source records remain immutable evidence. Canonical and derived layers add explicit, versioned football semantics.

## Production metric families

Locked or production-safe families include Success Rate, Explosiveness, Basic Yardage, Dropbacks / Sack Rate, Standard / Passing Downs, Third / Fourth Down conversions, Red-Zone / Goal-to-Go play efficiency, Tackles for Loss, Havoc, Team-Facing Turnovers, Drive Efficiency, Red-Zone Possession Efficiency, Possession Yardage, Three-and-Out counts, and First-Down Generation counts.

A field is not considered production-locked merely because it exists. See `docs/METRIC_REGISTRY.md` for definitions, exclusions, corpus totals, and reconciliation guarantees.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
export CFBD_API_KEY='...'
```

Raw acquisition commands remain available through `cfb-raw`. Raw artifacts live under `data/raw/cfbd/` and are ignored by Git.

## EPA research phase

CFBD exposes play-level `ppa`. We treat that as an external benchmark, not as training truth.

```text
historical canonical game state
    -> our Expected Points model
    -> our play-level EPA
    -> independent comparison against CFBD PPA
```

Before fitting or locking EPA v1 we must validate regulation state coverage, score timing semantics, possession transitions, scoring alignment, PPA coverage, and leakage-safe train/validation splits.

PPA must not be used as a feature or target in our EPA model. It is reserved for post-model comparison and error analysis.

## Near-term roadmap

1. Materialize and audit the enriched historical cache across all supported seasons.
2. Benchmark SRS alone and SRS combined with iterative and raw directional features on identical walk-forward samples.
3. Investigate regular-season versus postseason predictive behavior separately.
4. Evaluate feature-family stability without tuning against final holdout seasons.
5. Build Expected Points / EPA v1 from historical state and outcomes.
6. Add pace and additional situational metrics.

## Change-control rule

Do not silently change a locked denominator, feature direction, rating equation, or metric meaning. Investigate uncertain source semantics first, version definitions, propagate only after reconciliation, invalidate stale caches when contracts change, and update the relevant registry or checkpoint documentation.