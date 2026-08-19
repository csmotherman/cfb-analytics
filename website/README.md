# SOAR Analytics Website

This is the Michigan-football-first experience within SOAR Analytics, backed by the national analytics engine in the repository root.

## Product boundary

Python and published artifacts own calculations. `website/lib/` turns those artifacts into typed product objects. React components present them and never invent grades, ranks, predictions, player images, depth order, or performance.

Every displayed number is labeled as one of `ACTUAL`, `PROJECTED`, `PRESEASON`, or `BENCHMARK`.

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
