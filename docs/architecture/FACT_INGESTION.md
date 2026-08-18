# Broad FBS-Team Fact Ingestion

## Purpose

The broad fact corpus retains every source game with at least one FBS participant. It is additive and does not replace the frozen `data/raw/cfbd` FBS-vs-FBS regression corpus.

```text
CFBD responses
  -> retain game when home classification is FBS OR away classification is FBS
  -> retain drives and plays only for those exact game IDs
  -> data/raw/cfbd_facts/season=.../season_type=.../week=...
  -> season audit and legacy-containment proof
  -> canonical FBS membership snapshot
```

Run:

```bash
python -m cfb_analytics.pipelines.ingest_facts --season 2025
```

Verified partitions are reused without source calls. `--force` intentionally refreshes a partition. Every manifest declares `namespace=cfbd_facts` and `universe=games_with_at_least_one_fbs_team`, preventing a broad partition from being mistaken for the legacy corpus.

## Quality gates

Ingestion fails when a retained game lacks a stable ID, game IDs repeat, a retained game has no FBS participant, or a play/drive falls outside the selected game IDs. The season audit additionally fails on cross-partition ID duplication, invalid checksums, loss of any frozen legacy game, conflicting team names for one ID, conflicting in-season conference membership, or slug collisions.

The season membership output contains only FBS teams. An FCS opponent remains present in games, drives, and plays but is not promoted into the FBS membership or ranking population.

## Migration boundary

Canonical play and drive processing still reads `data/raw/cfbd`; this preserves regression behavior. Promoting `cfbd_facts` into SOAR season totals requires a separate dual-universe reconstruction audit. Until that audit passes, broad facts are source evidence and membership truth, not a silent replacement for validated metric inputs.

