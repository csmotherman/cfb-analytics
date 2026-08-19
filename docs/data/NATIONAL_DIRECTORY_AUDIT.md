# National directory audit — 2026 snapshot

This report summarizes the versioned machine-readable audits in `data/published/2026/directory/audit.json` and `data/published/directory_history/audit.json`.

## Current coverage

| Dataset | Rows |
|---|---:|
| FBS teams | 138 |
| Current roster players | 15,442 |
| FBS-relevant scheduled games | 888 |
| Transfer portal entries | 4,445 |
| Coach records | 138 |
| 2026 recruits | 3,987 |
| Recruiting team rows | 221 |

All 15,442 current player IDs are unique, all roster teams resolve to the FBS team directory, and every team has a published bundle. The current directory joins 2,221 players to the current recruiting class; the longitudinal exact-ID join raises current-player recruiting coverage to 9,791.

## Longitudinal coverage

| Dataset | Coverage | Result |
|---|---|---:|
| Recruiting classes | 2010–2026 | 65,137 unique recruits |
| Team recruiting trends | 2010–2026 | 266 team series |
| Rosters | 2021–2026 | 66,904 unique players |
| Transfer portal | 2021–2026 | 18,867 rows |
| Multi-season players | 2021–2026 | 36,575 |
| Multi-team careers | 2021–2026 | 13,222 |

## Identity findings

- No recruiting class contains duplicate recruit IDs.
- No roster season contains an exact duplicate `(playerId, team)` row.
- The source contains 210 repeated player-ID appearances within a season, representing 208 players listed for multiple teams. These records are preserved in `players/same-season-multi-team.json`; they are not silently discarded.
- Current Michigan coverage is 118 players, 89 exact recruiting joins, and 85 multi-season career timelines.

## Missingness that remains source truth

- 12,661 longitudinal recruiting records have no committed team. This includes uncommitted prospects and incomplete historical rows.
- 5,699 longitudinal recruiting records have no composite rating.
- Missing values remain null and do not receive inferred stars, grades, commitments, measurements, or biographies.

## Audit status

Both current and longitudinal publications report `PASS`. Rebuilds fail if team slugs collide, current roster teams do not resolve, exact player-team duplicates appear, requested seasons are absent, or game lifecycle labels contradict completion status.
