# Current State Audit

Audit date: 2026-08-18. Baseline scope: the repository as found before the national publishing refactor.

## Inventory

The Python package contained 254 modules: `analytics` (177), `canonical` (17), `derived` (19), `profiles` (23), `prototypes` (3), `raw` (9), `site` (2), and `sources` (3). There was no standalone `scripts/` directory. The test suite contained raw, canonical, derived, analytics, profile, prototype, and site tests plus numerous executable research/ablation harnesses under `tests/analytics`.

The data tree contained 2,498 files: 2,496 JSON, one CSV, and one `.gitkeep`. No Parquet files or notebooks existed. Raw CFBD games, drives, and plays are partitioned by season/type/week for 2014–2019 and 2021–2025; six 2026 source files support prospective work. Processed layers include canonical plays, derived drives, team-games, team-seasons, pregame snapshots, opponent-adjusted outputs, iterative ratings, model feature stores, prediction/model outputs, and market benchmarks. Generated web build state also existed under `website/.next`; that site is outside this refactor.

## Existing pipeline and grains

`raw` fetches CFBD JSON and writes checksummed manifests. `canonical` normalizes and audits play evidence and state transitions. `derived.drives` reconstructs validated possessions. `derived.games` creates one row per team/game. `derived.seasons` aggregates those rows to team/season. Analytics then adds locked metrics, situational systems, opponent adjustments, ratings, profiles, and prediction experiments.

Major grains were: raw source record; canonical play; validated possession drive; team-game; team-season; pregame team-game snapshot; one game model row; team profile; and model/benchmark summary. Existing team-game keys used `(gameId, team name)` and already audited exactly two rows per retained game. Stable team IDs, source schedule fields, season-aware conference, score, and home/away fields were not carried through that derived contract.

## Validated analytics contracts

- Success v1: clean offensive scrimmage plays; first down 50%, second down 70%, third/fourth down 100% of distance. Modified/no-play contexts are excluded.
- Explosiveness v1: rush at least 10 yards or pass at least 20 yards; successful-play explosiveness separately uses yards per successful play.
- Finishing drives v2, field position v1, turnovers v1, TFL v1, havoc v1, drive efficiency v1, possession yardage v1, situational and red-zone families aggregate reconstructible counts.
- `iterative_ratings.py` contains the constrained least-squares SRS and weighted offense/defense opponent-adjusted rating solver. `opponent_adjustment.py` builds leakage-safe, pregame-only residual adjustments.
- MWDR, ECI, SMR, DDR, and GPI live in `cfb_sandbox_systems.py` with reconstruction audits in `cfb_sandbox_forensics.py`; DDR excludes overtime and GPI uses close second-half drives.

These implementations remain in place. Their passing forensic tests are contracts.

## Risks and duplication

The 177-module `analytics` namespace mixes production metrics, CLI wrappers, forensic investigations, challenger models, propagation audits, and website publishing. Many `_cli`, `_forensics`, `_residual`, `_candidate`, and versioned publisher modules intentionally duplicate orchestration while preserving research history. Moving them wholesale would create high regression risk.

Hard-coded season tuples occur in raw CLI, model validation, archives, research harnesses, and prospective 2026 code. Defaults of 2025 occur in several CLIs. Michigan and Ohio State occur mainly as test fixtures; production metric calculations are national and team-agnostic. Static paths occur throughout model and website publishers. These are migration debt unless part of the new national pipeline.

The most important policy conflict was in `raw.acquire`: source responses were reduced to FBS-vs-FBS games before persistence. That prevents FCS contamination in the prediction corpus but also discards FBS-vs-FCS source evidence. Existing partitions are preserved as a validated historical baseline; future general ingestion must store the broad fact layer and apply analytical-universe policy downstream.

Duplicate team-games can arise whenever play/drive identities resolve more than two teams, or when independently produced team-game rows are concatenated. Existing audits detect name-key duplicates. The new contract additionally fails closed on `(game_id, team_id)`, source-game existence, exactly-two symmetry, scores, and opponent IDs.

## Incremental migration decision

The refactor adds configuration, identity, canonical enrichment, rankings, conference aggregation, validation, source adapters, and publishing interfaces. It does not relocate locked formulas, research history, or prediction models. The repository direction was subsequently clarified: the existing `website/` is being converted into the Michigan-focused application in this repository, with an internal published-data boundary rather than a separate consumer repository.
