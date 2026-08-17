# CFB Model Website

The website has one product promise:

> See what the model predicts, then see exactly why.

The public product loop stays deliberately small:

1. **Predictions** bring users in.
2. **Why** explains each supported prediction in fan-readable language.
3. **Archive** lets fans go back to any supported season/week from 2014 through 2025 without changing the product focus.
4. **Results** keep the model accountable and give users a reason to come back.

Primary navigation is:

- Predictions
- Archive
- Results
- How it works

The archive picker also lives directly on the home screen so a fan can jump from the current slate to any supported historical season/week in one action.

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

The COVID-disrupted 2020 season is intentionally excluded from the comparable historical archive and model universe. It should not appear in the website season selector or archive exporter output.

The archive loader checks generated files first at:

```text
data/processed/website/prediction_archive/season=YYYY/week=N.json
```

It also accepts deployable copies at:

```text
website/data/archive/season=YYYY/week=N.json
website/data/archive/YYYY/week-N.json
```

Build the historical archive from the repository root with:

```bash
python -m cfb_analytics.analytics.website_prediction_archive --overwrite
```

The exporter reconstructs the historical game slate from canonical data for every supported archive season. If this file exists:

```text
data/processed/market_benchmark/prediction-v2-vs-clean-market-games.json
```

then stored `minGames=3` official out-of-sample Prediction-v2 calls are attached to the matching historical games. Other games remain labeled as historical slate entries. The exporter never manufactures a model pick, probability, or explanation after seeing the result.

This distinction matters for the early seasons and any season outside the official Prediction-v2 OOS contract: fans can still browse the week, matchup, and final score, but the UI only says “model pick” when a supported historical prediction exists.

## Product rules

- Never fabricate a prediction to make the UI look populated.
- Live predictions lock before kickoff.
- The original prediction remains visible after the game.
- Historical pages never invent a missing prediction or a post-hoc explanation.
- 2020 stays excluded because the COVID-disrupted season is outside the comparable archive/model contract.
- Advanced metrics stay under the hood unless they make the explanation clearer.
- Archive is part of the same prediction → explanation → result product, not a second analytics dashboard.

## Run locally

```bash
python -m cfb_analytics.analytics.website_prediction_archive --overwrite
cd website
npm install
npm run typecheck
npm run dev
```

Open `http://localhost:3000`.
