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
cd website
npm install
npm run dev
```

Open `http://localhost:3000`.

The simulator API uses the repository virtual environment at `../.venv/bin/python`. Override it when needed:

```bash
CFB_PYTHON=/path/to/python npm run dev
```

## Validate frontend changes

At minimum:

```bash
npm run typecheck
npm run build
```

Visual work should also be checked at desktop and mobile widths when browser tooling is available.

## Product rule

SOAR should not become a prettier spreadsheet.

Every major surface should help fans understand strength, identity, difference, similarity, trajectory, or matchup context. Prefer one strong, meaningful visualization over a wall of generic cards. Preserve the rigor of the Python analytics layer while making the public experience dramatically easier and more memorable to explore.
