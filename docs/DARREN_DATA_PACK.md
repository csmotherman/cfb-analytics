# Darren numerical scouting pack

This workflow generates a creator-ready **numbers-only** scouting packet from the repository's locked published team-game data and schedule-adjusted model.

It is designed to answer the quantitative portion of an opponent/team outlook before any staff, roster, scheme, transfer, injury, or depth-chart research is added.

## Model guardrails

Primary strength claims use the five historically validated opponent-adjusted metrics:

- success rate
- rush success rate
- pass success rate
- explosive-play rate
- yards per play

The pack also fits a clearly labeled **research-only** opponent-adjusted layer for:

- rush explosive-play rate
- pass explosive-play rate
- rush yards per attempt
- net pass yards per dropback
- standard-down success rate
- passing-down success rate
- third-down conversion rate
- sack rate allowed / generated through the offense-facing model
- havoc rate allowed / generated through the offense-facing model

Research-only metrics use the same locked team-game definitions and schedule-adjusted architecture, but they have not completed the same historical validation suite as the primary five. They should support a claim, not be the only evidence for one.

Default model penalties remain frozen at:

- team ridge: `40`
- home-field ridge: `20`

## Run it

From the repository root:

```bash
source .venv/bin/activate
pip install -e ".[models]"
git pull

cfb-darren-pack \
  --season 2025 \
  --team western-michigan \
  --compare michigan
```

Equivalent module command:

```bash
python -m cfb_analytics.analytics.schedule_adjusted.darren_data_pack \
  --season 2025 \
  --team western-michigan \
  --compare michigan
```

The defaults resolve `data/published` and the output directory from the repository root, so the module command also works when the current terminal directory is `website/`.

For a quick full-season pass without the heavier leave-one-game-out loop:

```bash
cfb-darren-pack \
  --season 2025 \
  --team western-michigan \
  --compare michigan \
  --skip-game-poe
```

Replace `western-michigan` with any published FBS team name, slug, or team ID.

## Output

For Western Michigan 2025, files are written under:

```text
data/exports/darren/2025/western-michigan/
```

Generated files:

```text
darren-data-pack.md
darren-data-pack.json
tendencies.csv
adjusted-metrics.csv
game-poe.csv
schedule-strength.csv
```

### `darren-data-pack.md`

Human-readable number sheet containing:

- record and sample size
- raw play-volume and rush/dropback tendencies
- raw rush/pass success and explosiveness splits
- raw rush YPA and net pass yards/dropback
- third-down, sack and havoc context
- opponent-adjusted offense and defense values
- national offense and defense ranks
- Michigan side-by-side comparison
- validated-five offense, defense and overall composite context
- every opponent's adjusted offense/defense/overall rank
- strict leave-one-game-out game POE for the five validated metrics

### `adjusted-metrics.csv`

Best file for copying exact full-season opponent-adjusted numbers into another worksheet or creator document.

Each row identifies whether the metric is `validated` or `research-only` and includes:

- subject adjusted offense value/rank
- subject adjusted defense value/rank
- comparison adjusted offense value/rank
- comparison adjusted defense value/rank
- league-average raw value

### `tendencies.csv`

Raw weighted season tendencies and production. Rates are reconstructed from total locked numerators and denominators rather than averaging game percentages.

The rush/pass tendency definition is:

```text
rush decision rate = rushAttempts / (rushAttempts + dropbacks)
dropback rate      = dropbacks / (rushAttempts + dropbacks)
```

Dropbacks include sacks. Do not relabel this as official pass-attempt percentage.

### `game-poe.csv`

Strict leave-one-game-out actual, expected and performance-over-expected values for each target game and each validated metric.

The target game is removed before the expectation is fit. Positive POE is favorable for the selected team on both offense and defense.

### `schedule-strength.csv`

Game-by-game opponent context using the validated-five full-season composite:

- opponent adjusted offense rank/score
- opponent adjusted defense rank/score
- opponent adjusted overall rank/score
- location and score

FCS opponents may not have a complete FBS composite row and are left blank instead of being assigned an invented rank.

## What this runner intentionally does not do

It does **not** invent or infer 2026 personnel information from 2025 statistics.

Staff assignments, coaching changes, returning starters, portal additions/losses, injuries, expected depth chart, formation usage and scheme descriptions must be researched from dated external sources and kept separate from model-derived numbers.

That separation is deliberate: the numerical pack is reproducible from the repository, while the final Darren scouting dossier can cite current web research without contaminating or silently changing the model output.
