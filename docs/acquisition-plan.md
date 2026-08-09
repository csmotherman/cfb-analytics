# Historical Raw Acquisition Plan

## Target window

Acquire 11 seasons:

`2014–2019, 2021–2025`

2020 is intentionally excluded from the initial historical corpus because the pandemic season had materially abnormal schedules and participation. We can ingest it later as a separately flagged era if useful.

## Required entities

For every available week/season-type partition:

1. Games
2. Drives
3. Plays

## Implementation order

### Step 1 — Source audit

Before writing a bulk downloader, inspect the current CFBD API documentation and real responses for games, drives, and plays. Record endpoint parameters, pagination/limits, season-type behavior, week behavior, ID relationships, missingness, and schema differences across old/new seasons.

### Step 2 — One known game

Acquire one known game and save source responses without transformation. Verify that game, drive, and play identifiers relate as expected.

### Step 3 — One complete week

Acquire a complete historical week. Build manifests and verify reruns are idempotent.

### Step 4 — One complete season

Acquire one season week by week. Audit counts, missing partitions, duplicates, schema drift, and relationship anomalies.

### Step 5 — Historical backfill

Backfill the remaining target seasons only after the one-season audit passes.

## Completeness ledger

The downloader should eventually maintain a machine-readable ledger with one row per expected acquisition unit:

`source + season + season_type + week + entity`

Each unit has a status such as `pending`, `complete`, `empty_confirmed`, or `failed` plus counts/checksums. This prevents us from mistaking a missing API response for a legitimately empty week.

## Rate limits and retries

Bulk acquisition must be resumable. It should use bounded retries/backoff and skip already verified partitions unless an explicit refresh is requested.

## Historical reproducibility

The raw layer should make it possible to answer: "Exactly which source records did this later metric/model use?" A future model trained on Week 8 data must be reproducible from partitions available through Week 8 only.
