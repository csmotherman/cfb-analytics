# National directory data contract

The directory is the product-facing identity and preseason context layer. It does not replace canonical game facts or calculated analytics.

## Current-season directory

`data/published/2026/directory/` contains:

- `team-index.json`: one compact row per FBS team;
- `player-index.json`: the cleaned national roster with stable player IDs, team IDs/slugs, normalized position groups, and exact recruiting joins;
- `games.json`: games involving at least one 2026 FBS team, explicitly labeled `PRESEASON` or `ACTUAL`;
- `portal.json`: the source portal feed;
- `teams/{slug}.json`: a complete team bundle containing metadata, venue/logo fields, roster, schedule, recruiting, incoming/outgoing portal rows, and coaches;
- `audit.json` and `manifest.json`: coverage, missingness, checksums, source URLs, and publication status.

The immutable source envelopes used to create it are under `data/raw/cfbd_directory/season=2026/`.

## Longitudinal directory

`data/published/directory_history/` contains:

- recruiting classes from 2010–2026;
- a global exact-ID recruit index and team class trends;
- national rosters and transfer portal feeds from 2021–2026;
- stable player timelines;
- current-player records enriched with career and recruiting history;
- current-player shards under `players/current-by-team/{slug}.json` for efficient website reads;
- an explicit list of same-season multi-team source appearances.

Source envelopes are replayable from `data/raw/cfbd_directory_history/`. Run the longitudinal publisher with `--reuse-snapshots` to rebuild and audit without network calls.

## Identity and quality rules

- `playerId`, team ID, and recruit ID are authoritative join keys. Names are never used as identity joins.
- Repeated player IDs on different teams in one season are preserved as source appearances and audited, not deleted.
- Exact duplicate `(playerId, team)` rows fail publication.
- Recruiting grades are a presentation mapping of the source composite and carry `BENCHMARK`; they are not performance grades.
- Missing values remain null. Publication does not infer height, weight, hometown, stars, commitment, role, performance, or potential.
- Website consumers should read team shards or current-team enrichment shards instead of loading global indexes into the browser.

## Rebuild commands

```bash
python -m cfb_analytics.pipelines.publish_national_directory --season 2026
python -m cfb_analytics.pipelines.publish_longitudinal_directory --recruiting-start 2010 --roster-start 2021 --end 2026
python -m cfb_analytics.pipelines.publish_longitudinal_directory --recruiting-start 2010 --roster-start 2021 --end 2026 --reuse-snapshots
```
