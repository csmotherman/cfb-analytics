# ATS Logistic 2026 Prospective Freeze

Status: artifact builder ready; final coefficient artifact must be built and committed before any 2026 outcomes are used.

Frozen research rule:

- version: `ats-logistic-full-min3-0575-prospective-v1`
- model: `StandardScaler + LogisticRegression(C=0.5, max_iter=2000, random_state=42)`
- feature family: Prediction v2 FULL football features plus market context
- eligibility: `minGames=3`
- betting threshold: `max(P(home cover), P(away cover)) >= 0.575`
- target during fitting: home cover vs away cover
- historical pushes: excluded from model fitting
- market line convention: positive = home favored; negative = away favored
- market source semantics: first parseable `formattedSpread` in CFBD provider order

Historical discovery evidence is not confirmatory evidence. The selected rule produced 265-220 with 10 pushes in the min3 discovery screen at the 0.575 threshold. That result was used to select this challenger, so it must not be reused as an untouched confirmation set.

## Build the immutable artifact

Run once on the complete pre-2026 local corpus:

```bash
python -m cfb_analytics.analytics.ats_logistic_prospective_freeze --overwrite
```

This writes:

```text
data/processed/market_benchmark/ats-logistic-full-min3-0575-prospective-v1.json
data/processed/market_benchmark/ats-logistic-full-min3-0575-prospective-v1.sha256
```

The JSON stores the exact feature order, scaler means/scales, logistic coefficients, intercept, training seasons, training row count, and frozen research boundary. The SHA file is computed from a canonical JSON representation.

After generation:

1. run the verifier,
2. inspect the training seasons/count,
3. commit both files,
4. record the commit SHA,
5. only then begin 2026 scoring.

Verification:

```bash
python -m cfb_analytics.analytics.ats_logistic_prospective_freeze --verify
```

## Research-integrity boundary

Once the artifact is committed, do not use 2026 results to alter any of the following under the same version:

- feature list or feature construction,
- `minGames=3`,
- `C=0.5`,
- scaler parameters,
- logistic coefficients/intercept,
- `0.575` confidence threshold,
- market-line selection semantics.

Any change becomes a separately named challenger.

## Prospective scoring guard

`score_prospective()` refuses rows containing finite target/final-score fields. It reconstructs only the market-context transformations from the supplied pregame spread and then applies the committed scaler and coefficients manually.
