# CFB Model Website

The website has one product promise:

> See what the model predicts, then see exactly why.

The public product loop stays deliberately small:

1. **Predictions** bring users in.
2. **Why** explains each supported prediction in fan-readable language.
3. **Archive** lets fans go back to a supported season/week and audit the model against the market.
4. **Results** keep the model accountable and give users a reason to come back.

Primary navigation is:

- Predictions
- Archive
- Results
- How it works

The archive picker also lives directly on the home screen.

## Stadium Midnight design system

The public site uses a restrained dark research/sports theme:

- Canvas: `#0B0F17`
- Surfaces: dark slate / translucent `#161F30`
- Model / projection: `#06B6D4` cyan
- Positive / correct: `#10B981` mint
- Recommended-bet attention: `#F59E0B` amber
- Negative / incorrect: `#F43F5E` crimson
- Secondary text: `#94A3B8`
- UI typography: Inter
- Scores, spreads, percentages, and units: JetBrains Mono with tabular numerals

## Live prediction data contract

The website reads `website/data/predictions.json` (or `data/predictions.json` when the website directory is the deployment root).

```json
{
  "season": 2026,
  "week": 1,
  "updatedAt": "2026-08-28T16:00:00-04:00",
  "modelVersion": "prediction-v2-2026-prospective-freeze-v1",
  "current": [],
  "results": []
}
```

Each live game should contain the matchup, projected score, predicted winner, win probability, exactly three reasons, one upset path, and a pre-kickoff lock timestamp.

## Historical archive: 2014-2025, excluding 2020

Supported archive seasons are:

```text
2014, 2015, 2016, 2017, 2018, 2019, 2021, 2022, 2023, 2024, 2025
```

The COVID-disrupted 2020 season is intentionally excluded from the comparable historical archive and model universe.

Each generated week is a table with:

- year
- week
- home team
- away team
- historical CFBD reference spread, formatted with the favored team (for example `Michigan -5`)
- Prediction-v2 model line
- ATS correct indicator
- winner correct indicator
- an amber `BET` marker when the previously selected FULL ATS logistic min3/.575 model recommended that game

The **Results** tab for the selected season/week shows:

- model MAE
- straight-up winner accuracy
- ATS record and ATS percentage for the model margin versus the reference spread
- betting units from only the selected FULL ATS recommended bets

Units use the same research convention as the ATS audits: flat **1 unit risked at -110**, so a win is `+0.9091u`, a loss is `-1u`, and a push is `0u`.

### Archive sources

The exporter reads:

```text
data/processed/market_benchmark/prediction-v2-vs-clean-market-games.json
data/raw/market_lines/cfbd-market-spreads-2014-2025.json
data/processed/market_benchmark/full-ats-meta-gate-games.json
```

The last source is used only for its exact `FULL_BASELINE` rows—the 495 historical FULL ATS logistic min3/.575 recommendations. The experimental meta-gate decisions are not used by the website. If that file is unavailable, the exporter can fall back to `ats-logistic-deep-audit-games.json` and apply the already-fixed `.575` threshold.

The archive loader checks generated files at:

```text
data/processed/website/prediction_archive/season=YYYY/week=N.json
```

It also accepts deployable copies at:

```text
website/data/archive/season=YYYY/week=N.json
website/data/archive/YYYY/week-N.json
```

Generate the deployable archive from the repository root with:

```bash
python -m cfb_analytics.analytics.website_prediction_archive \
  --output-root website/data/archive \
  --overwrite
```

The exporter never manufactures a historical model pick, ATS recommendation, or explanation after seeing the result. Early seasons can still show the historical slate and market line even when no official Prediction-v2 OOS call exists.

## Product rules

- Never fabricate a prediction to make the UI look populated.
- Live predictions lock before kickoff.
- The original prediction remains visible after the game.
- Historical pages never invent a missing prediction or post-hoc recommendation.
- 2020 stays excluded because the COVID-disrupted season is outside the comparable archive/model contract.
- Advanced metrics stay under the hood unless they make the prediction easier to understand.
- Archive is part of the same prediction → explanation → result product, not a second analytics dashboard.

## Run locally

```bash
python -m cfb_analytics.analytics.website_prediction_archive \
  --output-root website/data/archive \
  --overwrite
cd website
npm install
npm run typecheck
npm run dev
```

Open `http://localhost:3000`.
