# CFB Analytics

This repository is intentionally starting from zero.

## Current objective

Establish a trustworthy college-football data foundation before calculating any derived or advanced statistic.

We will validate the source data and its relationships in this order:

1. Games
2. Drives
3. Play-by-play
4. Cross-table relationships
5. Clean canonical datasets
6. Team-game data
7. Season data
8. Advanced metrics and ratings

No derived football logic belongs in this repository until the underlying raw data has been inspected and validated against real games.

## Principles

- Raw source data is preserved without transformation.
- A transformation is not accepted because it "looks right"; it must be defined and tested.
- Games, drives, and plays each have an explicit grain and primary key.
- Every cleaned field must trace back to source fields or a documented derivation.
- Structural validation must fail loudly.
- Advanced metrics are downstream consumers, never part of ingestion or cleaning.

See `docs/rebuild-plan.md` for the development sequence and `docs/source-audit.md` for the first validation work.
