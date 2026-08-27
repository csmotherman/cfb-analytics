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

`/creator-hub` is a private, non-indexed, multi-creator workspace organized
around video outlines — sections, talking points, attached research/visuals,
and a request loop between each creator and Carter. It intentionally does not
share the public site's nav, footer, or visual design system (see
`components/PublicChrome.tsx`, which renders the public chrome everywhere
except `/creator-hub/*`).

Each creator authenticates with a private 4-digit PIN (never a shared
password). PINs are salted and hashed at rest (`node:crypto` scrypt); a
successful unlock creates a real server-side session row in
`creator_sessions` and an HttpOnly cookie scoped to `/creator-hub`. See
`lib/creator-hub/` for the schema, typed data layer, and auth helpers.

**One-time setup:**

1. Attach a Postgres database to the Vercel project (Vercel's Neon
   integration). This populates `DATABASE_URL` / `POSTGRES_URL`
   automatically in the deployment environment; set the same variable
   locally (e.g. in `.env.local`) for `npm run dev`.
2. Run `lib/creator-hub/schema.sql` once against that database (Vercel's
   query editor, `psql`, or any Postgres client). It is safe to re-run —
   every statement is `if not exists`.
3. Seed each creator with a real PIN — never hardcode one in source:

   ```bash
   node scripts/seed-creator.mjs "Darren Talks Ball" darren-talks-ball 1234
   ```

Re-running the seed script for an existing slug updates that creator's PIN.

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
