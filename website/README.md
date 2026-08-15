# CFB Analytics Pilot Website

This is the functional product pilot. It is intentionally plain. The goal is to validate fan flows and data contracts before visual design work.

## What works

- landing page with data readiness
- historical team browser and team-season pages
- cross-era power rankings
- two-team comparison
- browser-based historical game simulator
- archetype explorer
- fan-language metric glossary

The site reads generated data from the repository's local `data/processed` tree. It does not duplicate analytics logic in JavaScript.

## Prepare local data

From the repository root:

```bash
pytest
python -m cfb_analytics.profiles.historical_tournament
python -m cfb_analytics.profiles.game_simulator --prepare
python -m cfb_analytics.profiles.layered_archetypes
```

The archetype command currently targets the supported historical assignment range. If that artifact is absent, the rest of the pilot still runs.

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

## Pilot rule

Do not spend time polishing visuals yet. Test these questions first:

1. Can a fan find a team quickly?
2. Do the rankings make sense?
3. Does the team page answer useful football questions?
4. Is comparing eras understandable?
5. Does the simulator feel fast and believable?
6. Do archetype labels match what fans watched?
7. Which data is confusing or missing?

Once those flows and outputs are trustworthy, redesign the interface around the strongest interactions.
