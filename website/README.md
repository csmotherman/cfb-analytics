# Beat the Model Website

The consumer product is now **Beat the Model**:

> Pick the winners of the 15 biggest college football games of the week, then see if you can beat The Model.

There are no public betting odds, spreads, EV labels, bankrolls, or ATS scorecards. The historical market/ATS artifacts remain in the repository only as internal model-audit evidence.

## Product loop

1. **Rank every FBS team** before the week begins.
2. **Select the Official 15** biggest eligible matchups from those rankings.
3. **Users make winner picks** before seeing The Model's answer.
4. **The Model is revealed** after each user pick.
5. **Correct winner = 1 point.** User and Model are scored on the same games.
6. **Archive the slate and result** permanently.

Primary navigation:

- Play
- Rankings
- Archive
- How it works

Private friend pools and public pools can be layered onto this same card later without changing the core scoring rules.

## Weekly power rankings

Power rankings are deliberately separate from Prediction v2.

They answer:

> How strong is this team right now on a neutral field?

The ranking uses the existing site-aware opponent-adjusted SRS team rating. It is a strength ranking, not a résumé poll.

### Week 1

Week 1 is exactly the previous season's final **numeric power rating** sorted from strongest to weakest.

For 2026 Week 1:

```text
final 2025 BTM power ratings
        ↓
2026 Week 1 BTM rankings
```

No AP poll, recruiting ranking, transfer ranking, or Prediction-v2 confidence is used.

### First four games

The previous-season power rating fades using the same fixed evidence-window philosophy as the frozen early-season model:

```text
games played before matchup    previous season    current season
0                              100%                0%
1                               75%               25%
2                               50%               50%
3                               25%               75%
4+                               0%              100%
```

The blend is applied to the **numeric rating**, never to ordinal rank positions. Teams are reranked after the blended rating is calculated.

2020 remains excluded, so 2021 is never silently seeded from 2019.

## Official 15 selection

Normal regular-season weeks target 15 games.

A game is eligible when:

- it is a regular-season game;
- both teams have a published BTM ranking;
- Prediction v2 has a valid pregame call so The Model can participate.

The ordering itself never uses the model prediction, confidence, market line, ATS result, or final score.

Current matchup score:

```text
matchup score = average(home rank, away rank)
              + 0.25 × absolute rank difference
```

**Lower is better.**

The 15 lowest-scoring eligible matchups become the Official 15.

This means two strong, closely ranked teams rise above a highly ranked team playing a much weaker opponent.

## Current game data

The website reads:

```text
website/data/beat-the-model/current.json
```

Current contract:

```json
{
  "schemaVersion": 1,
  "version": "beat-the-model-v1",
  "season": 2026,
  "week": 1,
  "updatedAt": null,
  "status": "awaiting-slate",
  "slateSize": 15,
  "rankingVersion": "btm-site-aware-srs-four-game-carryover-v1",
  "selectionVersion": "btm-top-15-power-matchups-v1",
  "modelVersion": "prediction-v2-2026-prospective-freeze-v1",
  "games": []
}
```

Once `website/data/predictions.json` contains the live frozen Prediction-v2 slate, the publisher joins it to the BTM rankings and writes the top 15 eligible matchups into this file.

The browser stores solo picks locally for now. The Model's pick is hidden until the user makes their own choice. Pool persistence/accounts can be added later without changing the weekly data contract.

## Rankings data

The publisher writes:

```text
website/data/beat-the-model/rankings/season=2026/week=1.json
```

For Week 1, this file is generated directly from the final 2025 power ratings.

Historical archive weeks are also decorated with:

- home rank
- away rank
- home/away power rating
- matchup score
- Official 15 selection flag
- Official 15 slot
- Beat the Model weekly model record/accuracy/MAE

The historical raw market and ATS fields can remain inside the generated JSON for internal audit reproducibility, but the public Beat the Model components do not render them.

## Publish website data

From the repository root:

```bash
python -m cfb_analytics.analytics.publish_website_archive
```

The command still validates the frozen historical research universe, then additionally:

1. builds weekly BTM power rankings;
2. decorates historical weeks with the Official 15;
3. writes the 2026 Week 1 rankings from final 2025 ratings;
4. writes the current Beat the Model game dataset.

Generated deployable data lives under:

```text
website/data/archive/
website/data/beat-the-model/
```

After publishing:

```bash
git add website/data/archive website/data/beat-the-model
git commit -m "data: publish Beat the Model website data"
git push origin agent/website-predictions-clean
```

## Fairness rules

- The Model never gets to choose the games it has to predict.
- Rankings/slate selection happen independently of model confidence or prediction direction.
- Users pick before seeing The Model's answer.
- Live model calls lock before kickoff.
- Correct winner = 1 point; wrong winner = 0.
- Historical model picks are never reconstructed with future information.
- 2020 remains excluded from the comparable model/ranking universe.
- Market/ATS research is internal evidence, not the public game.

## Stadium Midnight design system

The site keeps the Stadium Midnight palette:

- Canvas `#0B0F17`
- Dark slate surfaces
- Cyan for rankings/model identity
- Mint for correct/success
- Amber for disagreement/attention
- Crimson for incorrect results
- Steel gray secondary text
- Inter UI type
- JetBrains Mono scores/ranks/numerics

## Run locally

```bash
python -m cfb_analytics.analytics.publish_website_archive
cd website
npm install
npm run typecheck
npm run dev
```

Open `http://localhost:3000`.
