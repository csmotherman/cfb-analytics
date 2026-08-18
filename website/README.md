<<<<<<< HEAD
# SOAR Analytics Website

This is the public product layer for **SOAR Analytics**.

The original website was intentionally built as a plain functional pilot so the project could validate fan flows, data contracts, team profiles, rankings, comparisons, simulations, archetypes, and metric explanations before investing in product design. That validation phase is complete enough to begin productization.

The website is now moving toward a premium interactive sports-analytics experience.

## Source of truth for product work

Before major frontend or UX work, read:

```text
../AGENTS.md
AGENTS.md
../docs/SOAR_ANALYTICS_WEBSITE_VISION.md
```

`docs/SOAR_ANALYTICS_WEBSITE_VISION.md` defines the target product experience, design language, Team DNA Universe, page-level goals, implementation phases, and acceptance criteria.

## Existing functionality

Current flows include:

- landing page;
- historical team browser and team-season pages;
- cross-era power rankings;
- two-team comparison;
- browser-based historical game simulator;
- dynamic identity/archetype exploration;
- situational exploration;
- fan-language metric glossary.

These flows are the starting point. Their current visual presentation is not the final design standard.

## Data architecture

The website reads generated data from the repository's local `data/processed` tree. It does not duplicate authoritative analytics logic in JavaScript.

Preferred direction:

```text
Python analytics artifact
  -> website/lib adapter
  -> typed UI view model
  -> SOAR React component
```

Do not invent values when an artifact is unavailable.

## Prepare local data

From the repository root:

```bash
pytest
python -m cfb_analytics.profiles.historical_tournament
python -m cfb_analytics.profiles.game_simulator --prepare
python -m cfb_analytics.profiles.layered_archetypes
```

The archetype command targets the supported historical assignment range. If that artifact is absent, other site flows should still degrade gracefully.

## Run the website

```bash
=======
# Michigan Football Analytics

The website is the Michigan-focused consumer application for the analytics produced by this repository. It presents Michigan's season, schedule, national ranks, opponent comparisons, and supporting methodology while using the full FBS population as context.

## Data boundary

The application reads versioned artifacts from `../data/published/{season}` through `lib/michigan.ts`. Python owns football calculations and publication; the website may select, rank, count, and format published values, but it must not redefine analytics in TypeScript.

Required published artifacts:

- `teams/michigan/season.json`
- `teams/michigan/games.json`
- `national/teams.json`
- `national/conferences.json`

If those artifacts are missing, publish them from the repository root before building the website.

## Local development

```bash
>>>>>>> 28a9c53 (new design)
cd website
npm install
npm run dev
```

Open `http://localhost:3000`.

<<<<<<< HEAD
The simulator API uses the repository virtual environment at `../.venv/bin/python`. Override it when needed:

```bash
CFB_PYTHON=/path/to/python npm run dev
```

## Validate frontend changes

At minimum:

```bash
=======
## Verification

```bash
cd website
>>>>>>> 28a9c53 (new design)
npm run typecheck
npm run build
```

<<<<<<< HEAD
Visual work should also be checked at desktop and mobile widths when browser tooling is available.

## Product rule

SOAR should not become a prettier spreadsheet.

Every major surface should help fans understand strength, identity, difference, similarity, trajectory, or matchup context. Prefer one strong, meaningful visualization over a wall of generic cards. Preserve the rigor of the Python analytics layer while making the public experience dramatically easier and more memorable to explore.
=======
The production build currently exposes:

- `/` and `/michigan` — current 2026 preseason Michigan dashboard
- `/football/2010` through `/football/2026` — season-aware Michigan routes
- `/schedule` — current-season schedule state without fabricated results
- `/rankings` — national team context
- `/compare` — Michigan versus another published FBS team
- `/metrics` — methodology and interpretation
- `/teams` and `/teams/[team]/[season]` — supporting national team profiles

See `../docs/architecture/MICHIGAN_CONSUMER_CONTRACT.md` for the application contract.

Historical national facts are acquired independently and resumably from the repository root:

```bash
python -m cfb_analytics.pipelines.ingest_history --start 2010 --end 2025
```

Completed seasons are skipped unless `--force` is supplied. Core ingestion completion does not imply that downstream canonical metrics have been published for the website; unavailable historical seasons remain explicit in the UI.
>>>>>>> 28a9c53 (new design)
