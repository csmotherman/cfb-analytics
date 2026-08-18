# CFBD Source Boundary

Base URL: `https://api.collegefootballdata.com`. Authentication is read from `CFBD_API_KEY` in the process environment, falling back to `CFBD_API_KEY` in the repository `.env`; an exported value takes priority. Credentials are never written to manifests or outputs, and `.env` is ignored by Git. The existing acquisition adapter uses bearer-authenticated HTTP against the documented API and retains checksummed response manifests. The official generated `cfbd-python` client remains the interface reference; replacing the thin legacy transport with generated model objects is migration debt because doing so inside the forensic baseline would add serialization and version risk without changing the source contract.

Used for the historical baseline: calendar, games, drives, and plays. Also used by product-specific legacy code: teams, season stats, advanced season stats, and lines. Prepared adapters: rosters, recruiting team rankings, CFBD SRS/Elo benchmarks, account info, and usage. Advanced stats, adjusted metrics, PPA, CORE, FPI, SP+, and other ratings remain benchmark-only and are not fetched by the national build.

Caching is partition- and checksum-aware. Verified immutable partitions are reused; `--force` intentionally refreshes them. Manifests record request URL, HTTP status, retrieval time, fields, row count, checksum, and file. `/info/usage` and `/info` methods provide future quota and remaining-call monitoring without a dashboard.

The historical `data/raw/cfbd` corpus is FBS-vs-FBS only. The additive `data/raw/cfbd_facts` ingestion path stores FBS-vs-FCS games before analytical filtering and never overwrites the regression corpus. Its season audit proves legacy containment before producing an FBS membership snapshot.
