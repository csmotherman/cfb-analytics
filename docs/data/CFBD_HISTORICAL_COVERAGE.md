# CFBD Historical Coverage

Status values describe observed repository evidence, not theoretical API availability:

- `FULL` — the endpoint/source was acquired for the complete season scope and passed local integrity checks;
- `PARTIAL` — saved results exist but do not satisfy the complete-season scope;
- `NONE` — a tested request returned no usable records;
- `NOT_TESTED` — no complete, audited result is currently persisted.

The table must be updated from saved response manifests and coverage audits. Documentation claims alone are not evidence. As of 2026-08-18, the core broad all-FBS fact corpus is complete and audited for every completed season from 2010 through 2025. Older legacy research partitions do not automatically count as coverage for the new national contract.

| Source / endpoint | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FBS teams / season membership | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | NOT_TESTED |
| Games | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | NOT_TESTED |
| Plays | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | NOT_TESTED |
| Drives | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | FULL | NOT_TESTED |
| Roster | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| Team season stats | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| Player stats | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| Recruiting | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| Team talent | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| Advanced team stats | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| PPA / WEPA | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| Ratings (SRS, Elo, SP+, FPI, CORE) | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED |

## Provenance notes

- 2010 core facts: `data/raw/cfbd_facts/season=2010`, 16 verified partitions, 808 games, 20,134 drives, 141,506 plays, and 120 season-specific FBS memberships. The persisted season state is `COMPLETE` with a passing audit.
- 2011–2024 core facts: each season has its own `COMPLETE` progress record and passing audit. The 2020 calendar produced 29 observed calendar partitions and only 570 games; that difference is retained rather than normalized to a typical season.
- 2025 core facts: `data/raw/cfbd_facts/season=2025`, 17 verified partitions, 934 games, with checksummed request manifests and a passing season audit.
- Membership is reconstructed from each season's saved game facts, so conference affiliation is season-specific. A modern conference list is never applied retroactively.
- 2026 legacy/preseason files are not counted as complete national coverage and must never be interpreted as played-game evidence.
- Optional benchmarks must not block core games/plays/drives ingestion. Their coverage will be recorded independently when audited.
- The current environment does not install `cfbd-python`; production acquisition uses `CfbdClient`, the repository's thin HTTP adapter. The current upstream generated client documents `TeamsApi.get_fbs_teams(year=...)` and `ConferencesApi.get_conferences()`, but those signatures are not labeled locally verified until that exact package/version is pinned and inspected in the environment.
