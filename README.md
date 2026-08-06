# CFB Analytics

College football data ingestion and analytics using the CollegeFootballData (CFBD) API, pandas, Parquet, and DuckDB.

## Setup

1. Create a virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root:

```env
CFBD_API_KEY=your_collegefootballdata_api_key
```

CFBD requests use `https://api.collegefootballdata.com` with Bearer-token authentication.

## Download a season

```bash
python scripts/download_2025.py
```

Raw CFBD response bundles are saved under `data/raw/cfbd/<season>/`.

## API mapping

- Schedules and game metadata: `GET /games`
- Drives: `GET /drives`
- Play-by-play: `GET /plays`

The ingestion layer combines those flat CFBD responses into the existing project tables: `games`, `periods`, `drives`, and `plays`. The old SportsRadar-only child tables remain present but empty because CFBD play records do not expose the same nested `statistics`, `details`, and event-player structures.

## Important migration note

Existing SportsRadar raw files and DuckDB tables should not be mixed with CFBD data. Rebuild the database after switching providers so columns and identifiers come from one source consistently.
