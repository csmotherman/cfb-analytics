# Prediction v1 Site-Aware SRS / HFA Challenger

**Status:** PASSED — PROMOTED TO PREDICTION V2 RESEARCH BENCHMARK  
**Version:** `prediction-v1-site-aware-srs-hfa-v1`

## Purpose

After the authoritative target repair, corrected FULL VOLUME + OLS remained the incumbent. Two attempts to improve stability by reorganizing the same information did not earn promotion:

- a development-selected LEAN pruning challenger failed recent validation;
- a fixed 19-to-12 symmetric/net reparameterization improved pooled error but failed the predeclared fold-stability gate.

The next challenger therefore introduced a genuinely different pregame information source: **game site**.

## Site-context audit

The raw CFBD `games.json` site audit passed with complete coverage of the corrected modeling corpus:

```text
model rows            8,510
matched raw games     8,510
parseable site rows   8,510 (100.00%)
neutral-site games      685
non-neutral games     7,825
neutral field         neutralSite
```

Every historical season in the 2014–2019 and 2021–2025 corpus has both neutral and non-neutral examples. No model row is dropped for missing site context.

## Site-aware SRS model

The challenger estimates:

```text
margin ~= rating(home)
          - rating(away)
          + HFA * nonNeutral
```

where:

```text
nonNeutral = 1 for a non-neutral game
nonNeutral = 0 for a neutral-site game
```

Team ratings are centered within each disconnected schedule component. A single HFA coefficient is estimated from the supplied season history.

The solver uses the same least-squares objective as SRS and jointly solves team ratings and HFA. Regression tests verify both a balanced synthetic HFA case and agreement with an explicit constrained least-squares reference solve.

## Leakage contract

Site-aware ratings are rebuilt within each season in partition order.

For every partition:

```text
fit team ratings + HFA from strictly prior partitions
        ->
score current partition
        ->
add current partition to history
```

Current-game margin is never used in its own rating or HFA estimate. Season reset and regular-before-postseason ordering are preserved.

## Feature contract

The challenger changes exactly one of the 19 corrected FULL features:

```text
REMOVE
  srsEdge

ADD
  siteAwareSrsMargin
```

with:

```text
siteAwareSrsEdge
  = site-aware rating(home) - site-aware rating(away)

siteAwareSrsMargin
  = siteAwareSrsEdge
    + siteAwareSrsHfaBefore * nonNeutral
```

All other corrected FULL features remain unchanged. Feature count remains **19 vs 19**.

## Same-sample requirement

The challenger requires the exact same FULL-eligible game IDs at min-prior-games 3 and 4. If any FULL-eligible row lacks a converged site-aware SRS margin, the script fails instead of changing the comparison sample.

## Evaluation protocol

Estimator and outer protocol remained unchanged:

- OLS;
- equal game weights;
- all prior available seasons for each outer test season;
- authoritative signed home-margin target;
- min-prior-games 3 and 4;
- 2020 omitted;
- identical game sample.

Outer seasons were 2018, 2019, 2021, 2022, 2023, 2024, and 2025 at min3/min4, for 14 folds. The recent subset was 2023–2025 at min3/min4, for 6 folds.

## Predeclared promotion gate

SITE-AWARE required all of the following:

1. mean MAE improves across all 14 folds;
2. mean RMSE improves across all 14 folds;
3. MAE improves in at least 8 of 14 folds;
4. RMSE improves in at least 8 of 14 folds;
5. recent mean MAE improves;
6. recent mean RMSE improves;
7. recent MAE improves in at least 4 of 6 folds;
8. recent RMSE improves in at least 4 of 6 folds.

Winner accuracy was secondary context.

## Result

```text
ALL 14
  mean MAE delta     -0.0021
  mean RMSE delta    -0.0024
  winner delta       +0.13 pp
  MAE better           8/14
  RMSE better          8/14

RECENT 6
  mean MAE delta     -0.0035
  mean RMSE delta    -0.0174
  winner delta       +0.38 pp
  MAE better           4/6
  RMSE better          6/6
```

Negative deltas are better. SITE-AWARE cleared every predeclared promotion condition.

The effect size is modest, especially in pooled MAE, and must not be exaggerated. The strongest evidence is the recent RMSE stability: site-aware SRS improved RMSE in all six 2023–2025 min3/min4 folds while preserving the same model size and exact comparison sample.

## Recent site slices

```text
neutral fold-observations
  n=348
  MAE delta   +0.0190
  RMSE delta  -0.0521

non-neutral fold-observations
  n=2,938
  MAE delta   -0.0060
  RMSE delta  -0.0129
```

The slices are mechanism diagnostics, not alternate promotion gates. Neutral-game MAE was slightly worse while neutral RMSE improved materially; non-neutral games improved both metrics.

## Leakage-safe HFA diagnostic

For min3-eligible rows, mean pregame HFA estimates were:

```text
2018  +2.442
2019  +3.031
2021  +1.892
2022  +2.323
2023  +2.244
2024  +2.540
2025  +3.134
```

These values are learned from prior partitions only. No HFA constant is hard-coded or tuned against a test season.

## Decision

**SITE-AWARE is promoted.**

The promoted research benchmark is named **Prediction v2** and uses the exact same corrected FULL VOLUME + OLS contract except for replacing `srsEdge` with `siteAwareSrsMargin`.

Do not continue tuning HFA constants, alternate neutral-site formulas, LEAN subsets, or symmetric parameterizations against the already-inspected holdouts.

Prediction v1 remains preserved as the corrected predecessor benchmark. Prediction v2 becomes the forward research reference.

See `docs/PREDICTION_V2.md`.
