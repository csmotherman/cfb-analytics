# Data Lineage

Published metrics follow a deterministic path:

CFBD source JSON and checksum manifest → canonical play normalization/evidence → validated possession drives → locked team-game numerators and denominators → team-season aggregation → optional SOAR opponent adjustment/rating → FBS-universe national and conference ranking → published team, conference, and national artifacts.

Each source partition carries request URL, retrieval time, fields, record count, and SHA-256. Derived manifests carry input and output hashes plus schema/definition versions. Published manifests carry row counts, quality-gate results, metric registry, and an artifact hash. For example, Michigan offensive success rate traces to `successfulPlays / successEligiblePlays`; its ranks are computed only after the season membership filter.

