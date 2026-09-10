# Unadjusted drive rankings v1

Descriptive FBS team-season rankings, using all completed games involving FBS teams in the explicitly acquired snapshot, including FCS opponents and opening-week games. This broader research universe is kept separate from the production FBS-versus-FBS corpus. No production definitions or existing historical research are changed.

Offense pools adjudicated offensive points over resolved offensive possessions. Defense pools the opponent's adjudicated offensive points over resolved defensive possessions; lower is better. Net subtracts defensive allowance from offense. Reuses `drive_ppd.build_team_game_drive_rows`, Drive Efficiency v1 and Finishing Drives v2, without calling any opponent-adjustment fitting code. No preseason priors, shrinkage, minimum-game threshold or additional garbage-time exclusion. Defensive and special-teams return scores are not offensive drive points. Unresolved point outcomes and validation-review groups are disclosed and excluded under the existing contracts.

Exact fractional values determine competition ranks, with alphabetical presentation within ties. Only FBS teams are ranked. Teams missing either side's drive evidence for a completed game remain unranked rather than receiving a partial-season ranking. A scoreboard upper-bound check quarantines both teams in a game if adjudicated offensive points exceed either team's final score. The September 8 snapshot flags UAB (24 versus 23) and Ole Miss (42 versus 41); UAB, Illinois, Ole Miss and Louisville remain unranked pending source investigation. No locked scoring logic or source evidence is altered. Games not marked completed and games starting after the as-of date are excluded. The as-of argument filters the supplied snapshot; it cannot reconstruct historical completion states from a later snapshot.

The September 8, 2026 acquisition checked the full regular-season CFBD schedule: all 99 completed FBS-involving games were source Week 1. Raw games, plays and drives are preserved with request timestamps and hashes in an isolated acquisition root. The generated JSON carries those manifests, game-level numerators/denominators, completed games, excluded review groups and coverage. Rankings are not estimates of underlying team quality; opponent quality is intentionally uncontrolled.

Reproduce the report from the preserved snapshot:

```bash
.venv/bin/python -m cfb_analytics.analytics.unadjusted_drive_rankings \
  --season 2026 --as-of 2026-09-08 \
  --raw-root data/raw/unadjusted_drive_rankings_2026_20260908 \
  --processed-root data/processed/unadjusted_drive_rankings_2026_20260908 \
  --output data/research/unadjusted_drive_rankings/2026
```

For a refresh, acquire every completed season/week partition into a new isolated raw root and run with that root and a corresponding isolated processed root. Do not use the historical acquisition helper that intentionally filters out FCS games. Verify the completed game IDs against a fresh whole-season schedule before claiming all-games coverage.
