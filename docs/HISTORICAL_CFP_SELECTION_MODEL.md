# Historical CFP Resume Model

**Status:** Published retrospective model  
**Version:** `historical-cfp-resume-v1`

## What it answers

For each completed CFP-era regular season in the supported corpus, the model estimates how likely that final resume was to receive a CFP berth. It is intended for historical comparison on season pages.

It does **not** answer a preseason or in-season question. It does not simulate future games, conference standings, automatic qualifiers, or the 2026 bracket.

## Inputs

The model uses only fan-readable final regular-season resume features:

- win percentage;
- losses;
- strength of schedule, defined as the mean final win percentage of opponents played;
- quality wins, defined as wins over teams with a final win percentage of at least `.700`;
- scoring margin per game;
- conference championship.

The selection target comes from the teams present in source-backed CFP postseason games. Conference champions come from source-backed conference championship games.

## Evaluation and probability contract

Every season is scored by a logistic model trained on all other supported seasons (leave-one-season-out evaluation). The held-out season never trains its own scores. An intercept adjustment constrains the season's probabilities to sum to the actual field size: four berths through 2023 and 12 beginning in 2024.

This is retrospective cross-validation. Because older seasons can be trained using newer seasons, the score must be labeled **Final resume** or **Retrospective** in public surfaces. It must never be labeled preseason, live, or simulated.

## Coverage

- Modeled: 2014–2019 and 2021–2025.
- Not applicable: 2010–2013, before the CFP.
- Unavailable: 2020, which is absent from the repository's analytical corpus.

Published artifacts live under `data/published/cfp_history/`; Michigan-specific website artifacts live at `data/published/michigan_history/{season}/cfp-outlook.json`.
