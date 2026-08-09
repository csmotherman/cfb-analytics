# CFB Analytics

A clean, validated data foundation for college-football analytics.

The project intentionally starts with **data correctness before advanced metrics**. Raw API responses are stored unchanged, then games, drives, and play-by-play are cleaned independently into canonical schemas. Validation is a required gate before any downstream team-game, season, opponent-adjusted, or SOAR rating dataset is built.

## Data lineage

```text
CFBD API
  -> data/raw/{season}/games.parquet
  -> data/raw/{season}/drives.parquet
  -> data/raw/{season}/plays.parquet

raw games  -> clean games  ----\
raw drives -> clean drives -----+-> derived team-game -> season -> adjusted -> ratings
raw plays  -> clean plays  ----/
```

## Canonical grains

- `games`: one row per game. Primary key: `game_id`.
- `drives`: one row per drive. Primary key: `drive_id`; foreign key: `game_id`.
- `plays`: one row per play. Primary key: `play_id`; foreign keys: `game_id`, `drive_id`.
- `team_game` (future): one row per team per game. Exactly two rows for every eligible game.
- `team_season` (future): one row per team per season.

## Current scope

The current rebuild implements and tests the foundation only:

1. Canonical column normalization for games, drives, and plays.
2. Deterministic play classification and context flags.
3. Success-rate and explosive-play flags with explicit definitions.
4. Drive outcome flags.
5. Structural, range, and cross-table validation.
6. A pipeline that refuses to publish cleaned data when validation fails.

Advanced metrics are intentionally not implemented until this layer is trusted.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,api]'
cp .env.example .env
pytest
```

## Build cleaned season data

After raw Parquet files exist under `data/raw/<season>/`:

```bash
python -m cfb_analytics.pipeline.build_clean --season 2025
```

See `docs/data-model.md` and `docs/cleaning-rules.md` before adding new derived fields.
