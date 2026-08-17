# CFB Model Website

The website now has one product promise:

> See what the model predicts this week, then see exactly why.

The old analytics experiments still exist in the codebase, but they are intentionally removed from the primary navigation. The public product loop is deliberately small:

1. **Predictions** bring users in.
2. **Why** explains each prediction in three fan-readable reasons.
3. **Results** keep the model accountable and give users a reason to come back.

Primary navigation is only:

- Predictions
- Results
- How it works

## Prediction data contract

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

Each game should contain:

```json
{
  "id": "2026-week-1-away-at-home",
  "season": 2026,
  "week": 1,
  "kickoff": "2026-08-29T19:30:00-04:00",
  "homeTeam": "Home Team",
  "awayTeam": "Away Team",
  "predictedWinner": "Home Team",
  "homeWinProbability": 0.67,
  "projectedHomeScore": 31,
  "projectedAwayScore": 24,
  "reasons": [
    {"eyebrow": "EFFICIENCY", "title": "Reason one", "detail": "Fan-readable explanation."},
    {"eyebrow": "MATCHUP", "title": "Reason two", "detail": "Fan-readable explanation."},
    {"eyebrow": "STRENGTH", "title": "Reason three", "detail": "Fan-readable explanation."}
  ],
  "risk": "The clearest path to the upset.",
  "lockedAt": "2026-08-29T12:00:00-04:00",
  "status": "upcoming"
}
```

Final games move into `results` and add `actualHomeScore`, `actualAwayScore`, and `correct`.

## Product rules

- Never fabricate a prediction to make the UI look populated.
- Predictions lock before kickoff.
- The original prediction remains visible after the game.
- The fan sees one pick, one probability, three reasons, and one upset path.
- Advanced metrics stay under the hood unless they make the explanation clearer.
- Do not add new homepage modules unless they directly strengthen the prediction → explanation → result loop.

## Run locally

```bash
cd website
npm install
npm run typecheck
npm run dev
```

Open `http://localhost:3000`.
