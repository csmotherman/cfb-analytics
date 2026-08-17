# Beat the Model Website

The consumer product is **Beat the Model**:

> Pick the winners of the 15 biggest college football games of the week, then see if you can beat The Model.

There are no public betting odds, spreads, EV labels, bankrolls, or ATS scorecards. The historical market/ATS artifacts remain in the repository only as internal model-audit evidence.

## Product loop

1. **Rank every FBS team** before the week begins.
2. **Select the Official 15** biggest matchups from those rankings.
3. **Freeze and attach The Model's calls.** Picking does not open until this is complete.
4. **Users make winner picks** before seeing The Model's answer.
5. **The Model is revealed** after each user pick.
6. **Correct winner = 1 point.** User and Model are scored on the same games.
7. **Archive the slate and result** permanently.

Primary navigation:

- Play
- Pools
- Rankings
- Archive
- How it works

Private friend pools and public pools use the same Official 15 and scoring rules.

## Weekly power rankings

Power rankings are deliberately separate from Prediction v2. They answer:

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

No AP poll, recruiting ranking, transfer ranking, market information, or Prediction-v2 confidence is used.

### First four games

The previous-season power rating fades using the fixed evidence window:

```text
games played before matchup    previous season    current season
0                              100%                0%
1                               75%               25%
2                               50%               50%
3                               25%               75%
4+                               0%              100%
```

The blend is applied to the **numeric rating**, never to ordinal rank positions. Teams are reranked after the blended rating is calculated.

For the live scheduler, Week 2+ current-season strength uses completed FBS-vs-FBS games strictly before the target week. Week 0 results may therefore inform Week 2+, but the published Week 1 ranking remains exactly the final 2025 seed.

2020 remains excluded from the historical comparable universe, so historical 2021 is never silently seeded from 2019.

## Official 15 selection

Normal regular-season weeks target 15 games.

A live game can enter the ranking pool when:

- it is a CFBD regular-season FBS-vs-FBS game; and
- both teams have a published BTM ranking.

**Prediction v2 is not an eligibility or ordering input.** The Official 15 is selected first. The Model must then produce a valid frozen pregame call for every selected game before user picking opens.

Current matchup score:

```text
matchup score = average(home rank, away rank)
              + 0.25 × absolute rank difference
```

**Lower is better.** The 15 lowest-scoring matchups become the Official 15.

This means two strong, closely ranked teams rise above a highly ranked team playing a much weaker opponent. Model direction, confidence, market lines, ATS results, and final scores never influence the selection order.

## Automatic weekly schedule publisher

Live matchup population is handled by:

```bash
python -m cfb_analytics.analytics.publish_beat_the_model_schedule
```

The command uses the CFBD **games endpoint only**. It does not need play-by-play to select the slate.

To publish 2026 Week 1 now:

```bash
python -m cfb_analytics.analytics.publish_beat_the_model_schedule \
  --season 2026 \
  --week 1
```

To refresh the current week and automatically advance after the current Official 15 is final:

```bash
python -m cfb_analytics.analytics.publish_beat_the_model_schedule \
  --season 2026 \
  --advance
```

The scheduler:

1. fetches the target FBS-vs-FBS schedule from CFBD;
2. loads or generates the pre-week BTM rankings;
3. deterministically selects the Official 15 from rank only;
4. attaches an already-published frozen model call when available;
5. writes `current.json`;
6. refreshes final scores on later runs;
7. permanently snapshots a completed slate under `website/data/beat-the-model/slates/`.

Before The Model is attached, the website status is `awaiting-model`: fans can see the selected matchups but cannot submit picks. Once all 15 model calls exist, status becomes `open` and the selected game IDs are frozen.

### GitHub Actions schedule

`.github/workflows/beat-the-model-weekly.yml` runs at **9:15 AM America/Detroit every Monday from August through December**. It refreshes or advances the current regular-season slate and commits changed files under `website/data/beat-the-model/`.

Repository Actions must have a secret named:

```text
CFBD_API_KEY
```

Do not commit the key. With GitHub CLI, it can be entered securely with:

```bash
gh secret set CFBD_API_KEY
```

GitHub `schedule` and `workflow_dispatch` triggers require the workflow file to exist on the repository's **default branch**. Therefore the production cron/manual Actions entrypoint becomes available after this workflow is merged to the default branch. Until then, publish Week 1 from the local checkout with the Python command above.

After the workflow is on the default branch, an explicit manual Week 1 dispatch can use:

```bash
gh workflow run beat-the-model-weekly.yml \
  -f season=2026 \
  -f week=1
```

## Current game data

The website reads:

```text
website/data/beat-the-model/current.json
```

Current live contract:

```json
{
  "schemaVersion": 2,
  "version": "beat-the-model-v1",
  "season": 2026,
  "week": 1,
  "updatedAt": "...",
  "status": "awaiting-model",
  "slateSize": 15,
  "selectedGames": 15,
  "rankingVersion": "btm-site-aware-srs-four-game-carryover-v1",
  "selectionVersion": "btm-top-15-power-matchups-v1",
  "modelVersion": "prediction-v2-2026-prospective-freeze-v1",
  "modelReady": false,
  "selectionFrozen": false,
  "games": []
}
```

Valid live statuses are:

```text
awaiting-slate
awaiting-model
open
locked
final
```

The browser stores solo picks locally for now. The Model's pick is hidden until the user makes their own choice. Picks are disabled while a slate is `awaiting-model` so users never pick against a model call that has not yet been frozen.

## Model snapshots are a separate production boundary

The weekly schedule job deliberately does **not** fit or alter Prediction v2. It only attaches model calls that have already been published in either:

```text
website/data/predictions.json
website/data/beat-the-model/model-snapshots/season=YYYY/week=N.json
```

This separation prevents the matchup selector from changing the model and prevents model confidence from changing the matchup selector.

The existing guarded 2026 Prediction-v2 pipeline remains the authority for model calls. Its raw/processed football feature artifacts are intentionally gitignored, so automating that heavier pipeline on a clean GitHub runner requires a separate deployment-grade frozen state/artifact source. The schedule workflow never invents a missing model pick.

## Rankings data

Weekly rankings live under:

```text
website/data/beat-the-model/rankings/season=YYYY/week=N.json
```

For 2026 Week 1, the committed file is generated directly from final 2025 power ratings. Week 2+ files are generated automatically from the prior seed plus completed current-season games using the fixed four-game fade.

Historical archive weeks are also decorated with home/away ranks, power ratings, matchup score, Official 15 selection metadata, and model performance. Historical market/ATS fields remain available only for internal audit reproducibility.

## Historical website data publisher

The broader historical/BTM build remains:

```bash
python -m cfb_analytics.analytics.publish_website_archive
```

It validates the frozen historical research universe, builds historical BTM rankings/slates, and seeds the current-season Week 1 rankings.

Generated deployable data lives under:

```text
website/data/archive/
website/data/beat-the-model/
```

## Fairness rules

- The Model never gets to choose the games it has to predict.
- Rankings/slate selection happen independently of model confidence or prediction direction.
- The Official 15 is selected before model availability can affect the user experience.
- User picking stays closed until all selected model calls are frozen.
- Users pick before seeing The Model's answer.
- Live model calls lock before kickoff.
- Correct winner = 1 point; wrong winner = 0.
- Historical model picks are never reconstructed with future information.
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
python -m cfb_analytics.analytics.publish_beat_the_model_schedule --season 2026 --week 1
cd website
npm install
npm run typecheck
npm run dev
```

Open `http://localhost:3000`.
