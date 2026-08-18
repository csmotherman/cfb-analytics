# Data Ownership

## Source facts

CFBD is authoritative for stable game/team IDs, season-aware team and conference observations, schedules, scores, venues, raw plays, raw drives, rosters, recruiting, player and transfer metadata. Source payloads must remain namespaced and checksummed. Corrections belong in an explicit canonical correction layer, never by silently editing raw bytes.

## SOAR-derived truth

This repository is authoritative for play eligibility, success, explosiveness, situational efficiency, possession reconstruction, drive and finishing metrics, SRS, opponent adjustment, offense/defense/composite ratings, matchup calculations, and ranks/percentiles derived from those metrics. Existing definition-version fields identify the governing formula.

## External benchmarks

CFBD advanced stats, PPA, adjusted metrics/WEPA, Elo, FPI, SP+, CORE, and CFBD SRS are challengers. They live under `benchmarks` and `data/benchmarks` with `cfbd_` or other source namespaces. They must never populate `soar_` fields or replace locked numerators and denominators.

