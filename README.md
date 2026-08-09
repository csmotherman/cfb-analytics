# CFB Analytics

Reliability-first college football data foundation.

## Current phase

Acquire and preserve **raw games, drives, and play-by-play** week by week for:

`2014–2019, 2021–2025`

No cleaning, classifications, metrics, ratings, or modeling belong in this phase.

## Why direct REST JSON

The ingestion layer calls CFBD's REST API directly instead of deserializing through the generated Python models. This preserves the source JSON response as our evidence layer and avoids coupling historical raw storage to a client-model version.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
export CFBD_API_KEY='...'
```

## Commands

Audit the calendar without downloading football records:

```bash
cfb-raw calendar --season 2025
```

Download one partition:

```bash
cfb-raw week --season 2025 --season-type regular --week 1
```

Download one season using CFBD's calendar:

```bash
cfb-raw season --season 2025
```

Backfill the configured historical corpus:

```bash
cfb-raw backfill
```

Use `--refresh` only when intentionally replacing an already verified local partition.

Raw artifacts live under `data/raw/cfbd/` and are ignored by Git.

See `docs/acquisition-plan.md` and `docs/raw-data-contract.md` before changing ingestion behavior.
