# SOAR Analytics · Michigan Football Focus

SOAR Analytics is the public analytics product. Michigan Football Focus is its fan-first Michigan edition, backed by the national analytics engine in the repository root.

## Product boundary

Python and published artifacts own calculations. `website/lib/` turns those artifacts into typed product objects. React components present them and never invent grades, ranks, predictions, player images, depth order, or performance.

Every displayed number is labeled as one of `ACTUAL`, `PROJECTED`, `PRESEASON`, or `BENCHMARK`.

## Article publishing contract

`/articles` is the canonical editorial index and `/articles/[slug]` is the
shareable social landing page. Article records live in
`lib/michigan/stories.ts` and may carry multiple typed tags across `POSITION`,
`UNIT`, and `TOPIC`. Tags are intentionally many-to-many: one story can appear
in several filtered views.

Every article must provide at least one `dataLinks` entry pointing to the site
surface that supports or contextualizes its argument. Those links do not make
unsupported projections valid; displayed statistics still come from published
artifacts and retain their existing value-type labels. Reporting sources remain
separate from SOAR data links. Legacy `/stories` routes redirect to the
canonical article URLs.

## Private Creator Hub

`/creator-hub` is a private, non-indexed creator workspace. Access is checked on
the server and the password must never be committed to the repository.

Set this environment variable in the deployment environment:

```bash
CREATOR_HUB_PASSWORD=<your private password>
```

Successful access creates an HttpOnly, same-site cookie scoped to
`/creator-hub`. The session expires after two weeks and is invalidated
immediately when `CREATOR_HUB_PASSWORD` changes.

## Current real data

- 2026 Michigan roster: `data/published/2026/michigan/roster.json`
- 2026 Michigan schedule: `data/published/2026/michigan/schedule.json`
- 2026 projected lineup: `data/published/2026/michigan/projected-lineup.json`
- Frozen weekly game predictions: `data/published/2026/michigan/game-predictions.json`
- Sourced CFP market outlook: `data/published/2026/michigan/outlook.json`
- 2025 completed team and national analytics: `data/published/2025`

## Run locally

```bash
cd website
npm install
npm run dev
```

Validation:

```bash
npm run typecheck
npm run build
```
