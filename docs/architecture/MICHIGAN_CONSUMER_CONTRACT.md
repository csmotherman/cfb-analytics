# Michigan Application Contract

## Repository boundary

`cfb-analytics` is both the national analytics engine and the Michigan-focused application. The application lives under `website/`; it is not a separate repository and does not own football calculations.

```text
CFBD source facts
→ canonical national datasets
→ SOAR metrics and ratings
→ data/published/{season}
→ website server-side data adapters
→ Michigan-focused pages
```

Python owns ingestion, reconstruction, metrics, ratings, aggregation, validation, and publishing. Next.js owns loading published contracts, selecting Michigan context, formatting, explanation, navigation, and interaction.

## Required application reads

For season `{season}`, the application reads:

- `data/published/{season}/teams/michigan/season.json` for Michigan's team-season profile and ranks;
- `data/published/{season}/teams/michigan/games.json` for Michigan's game log;
- `data/published/{season}/national/teams.json` for national and conference comparison populations;
- `data/published/{season}/national/conferences.json` for denominator-weighted conference summaries;
- opponent team artifacts when a matchup needs deeper context.
- `data/published/{season}/michigan/projected-lineup.json` for the explicitly labeled preseason lineup projection.
- `data/published/{season}/michigan/game-predictions.json` for immutable frozen-model game margins.
- `data/published/{season}/michigan/outlook.json` for timestamped, sourced market benchmarks such as CFP qualification odds.

The server-side adapter in `website/lib/michigan.ts` resolves the latest published season and exposes typed application data. Browser components must not read raw or processed research files directly.

## Stable identifiers and calculations

Application joins use `season`, `team_id`, and `game_id`. Slugs are deterministic URL identifiers, not relational keys. The website may sort, select, filter, format, and explain published values. It must not reconstruct success rate, explosiveness, possessions, SRS, opponent adjustments, conference summaries, ranks, or percentiles. Missing analytics must be added to the publisher rather than recreated in TypeScript.

Small presentation summaries, such as counting wins from canonical game rows, are permitted because they do not redefine a football metric.

Preseason lineup order is also owned by Python. The `michigan-preseason-lineup-v1` artifact selects within roster position groups using published prospect grade, then roster class year, then jersey number. It is labeled `PROJECTED`, is not an official depth chart, and must render as unavailable rather than being reconstructed by the website when absent.

Game predictions preserve the frozen 2026 prospective model contract. They may expose predicted margin and winner, but no win probability until a separate probability calibration passes validation. Season-level market probabilities use `BENCHMARK`, retain their source and timestamp, and must never be presented as SOAR model output. CFP format facts and market benchmarks do not authorize an invented expected-wins or selection-committee simulation.

## Product focus

Michigan is the default experience. National and conference data answer Michigan questions with honest context: how good Michigan is nationally and in the Big Ten, what it does well or poorly, how it performed by game, and how it compares with rivals and national leaders.

Legacy prediction-game and archive interfaces have been removed from the application. National tools remain only where they provide useful context for Michigan: rankings, team profiles, schedule results, and direct comparisons.

## Season architecture

The public Michigan window is 2010–2026. The default product season is 2026; the latest completed analytics season is 2025. These are intentionally separate concepts. Season routes use `/football/{season}` and must resolve lifecycle state before presenting data.

Published observed rows carry `value_type=ACTUAL`; projected and preseason values must use `PROJECTED` or `PRESEASON` and cannot share an unlabeled presentation. In August 2026, the application renders 2026 as `PRESEASON` with a 0–0 observed record and no performance metrics. Missing historical publication produces an unavailable state rather than a modern comparison population or fabricated values.

Historical national ingestion is resumable per season. Completion of one season is persisted independently, and conference membership comes from that season's source facts. Coverage claims are maintained in `docs/data/CFBD_HISTORICAL_COVERAGE.md`.

Coaching context is independent metadata in `src/cfb_analytics/config/michigan_staff.json`; it is not embedded in metric calculations. The table is sourced to official Michigan records and preserves interim-coach notes rather than rewriting a season's analytical identity.

## Failure behavior

If published artifacts are absent or malformed, the application shows a build-required state. It must not silently fall back to CFBD calculated metrics, stale tournament data, or invented values. Publication quality gates remain upstream of the UI.
