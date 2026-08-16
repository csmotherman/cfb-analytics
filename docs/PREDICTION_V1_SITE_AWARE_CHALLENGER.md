# Prediction v1 Site-Aware SRS / HFA Challenger

**Status:** RESEARCH CHALLENGER — FIXED NEW-INFORMATION TEST  
**Version:** `prediction-v1-site-aware-srs-hfa-v1`

## Why this test exists

After the authoritative target repair, corrected FULL VOLUME + OLS remained the incumbent. Two attempts to improve stability by reorganizing the same information did not earn promotion:

- a development-selected LEAN pruning challenger failed recent validation;
- a fixed 19-to-12 symmetric/net reparameterization improved pooled error but failed the predeclared fold-stability gate.

The project therefore stopped rearranging the same predictors and moved to a genuinely different pregame information source: **game site**.

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

## Current SRS limitation

Current SRS models game margin as:

```text
margin ~= rating(home) - rating(away)
```

It does not explicitly distinguish a true home game from a neutral-site game.

The final OLS intercept can absorb an average home effect, but that does not prevent home-field advantage from bleeding into team ratings, and the same intercept applies to neutral games.

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

Team ratings are centered within each disconnected schedule component, matching the current SRS identifiability convention. A single HFA coefficient is estimated from the supplied season history.

The solver uses the same least-squares objective as SRS and jointly iterates the team-rating normal equations and the closed-form HFA update until convergence.

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

Current-game margin is never used in its own rating or HFA estimate.

The season reset and regular-before-postseason ordering are preserved.

## Challenger feature contract

The final Prediction-v1 challenger changes exactly one of the 19 FULL features:

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

All other corrected FULL features remain unchanged:

```text
12 Iterative matchup terms
2 raw MWDR edges
mwdrXExpectedPossessions
successVolumeEdge
explosiveVolumeEdge
turnoverVolumeEdge
```

Feature count remains **19 vs 19**.

## Same-sample requirement

The challenger requires the exact same FULL-eligible game IDs at min-prior-games 3 and 4. If any FULL-eligible row lacks a converged site-aware SRS margin, the script fails rather than silently changing the comparison sample.

## Evaluation protocol

Estimator and outer protocol remain unchanged:

- OLS;
- equal game weights;
- all prior available seasons for each outer test season;
- authoritative signed home-margin target;
- min-prior-games 3 and 4;
- 2020 omitted;
- identical game sample.

Outer seasons:

```text
2018
2019
2021
2022
2023
2024
2025
```

for 14 min3/min4 folds.

Recent subset:

```text
2023
2024
2025
```

for 6 folds.

## Predeclared promotion gate

SITE-AWARE advances only if all of the following hold:

1. mean MAE improves across all 14 folds;
2. mean RMSE improves across all 14 folds;
3. MAE improves in at least 8 of 14 folds;
4. RMSE improves in at least 8 of 14 folds;
5. recent mean MAE improves;
6. recent mean RMSE improves;
7. recent MAE improves in at least 4 of 6 folds;
8. recent RMSE improves in at least 4 of 6 folds.

Winner accuracy is secondary context.

The command also reports recent neutral and non-neutral error slices. Those slices are mechanism diagnostics, not alternate promotion criteria.

## HFA diagnostic

The command prints the mean leakage-safe pregame HFA and the final observed pregame HFA for each outer season. These values should be interpreted as diagnostics of the fitted site mechanism, not as independently tuned constants.

No HFA value is hard-coded or tuned against a test season.

## Runtime

This experiment reads saved corrected model rows and raw game-site flags. It recomputes only a lightweight season-local SRS/HFA system.

It does **not** replay PBP, rebuild profiles, regenerate sandbox metrics, refit drive-outcome models, or rebuild the model feature store.

Run:

```bash
python -m cfb_analytics.analytics.prediction_v1_site_aware_challenger
```

## Interpretation

If SITE-AWARE passes, it is a strong Prediction-v2 candidate because it adds real pregame context with no increase in final feature count and corrects a structural limitation of current SRS.

If it fails, retain corrected FULL and do not tune alternate HFA constants or site formulas against the inspected holdouts. The next major direction should be another genuinely different information source, with early-season priors / previous-season carryover among the highest-priority candidates.
