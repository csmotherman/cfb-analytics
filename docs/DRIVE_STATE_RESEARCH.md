# Drive-State Research Contract

**Status:** RESEARCH ONLY  
**Version:** `drive-state-research-v1-pregame-context-contract`

## Why this exists

The third-down residual experiments found that special team-specific third-down skill is either absent or too small/unstable to justify carrying as a permanent simulator rating. The strongest nested diagnostic selected heavy shrinkage and produced only microscopic proper-score gains.

That does **not** mean situational football state is unimportant. It means situational context should first be modeled as part of the football mechanism itself rather than converted into many noisy team-specific ratings.

This module establishes the next research layer:

```text
drive-start state + pregame team quality -> realized drive points
```

It deliberately stops at a validated research dataset and audit. The statistical outcome model is chosen only after the target and context distributions are inspected.

## Leakage contract

Each research row is one validated possession drive with a resolvable point outcome.

Predictors may use only:

- information known at the **start of that drive**;
- team-quality states that were snapshotted **before the current weekly partition**.

Current-drive outcomes, later plays, later drives, final score, and future partitions are not predictors.

The realized drive points are the target only.

## Pregame team-quality source

The materializer reuses the saved `football_mechanisms/.../matchups.json` files. Those team states are cumulative through the prior partition only.

The initial compact quality set includes:

- yards per possession;
- success rate;
- explosive rate;
- scoring-opportunity rate;
- points per opportunity;
- early-down success;
- giveaway/takeaway rates;

for both the offense and opponent defense.

These are broad ability/context controls, not special situational ratings.

## Drive-start state

The first contract retains:

- start period;
- start yards to goal;
- start down;
- start distance;
- start score margin;
- start score state;
- overtime indicator.

The audit will determine whether every field has sufficient coverage and whether some drive-start values are structurally unusual enough to need separate treatment.

## Target

The target uses the existing resolved-drive point definition already used in the sandbox component system:

```text
points = clamp(end offense score observed - start offense score, 0, 8)
```

No interpretation is imposed yet. The materializer records the exact point outcome bucket (`0` through `8`, or `other`) so the corpus can tell us what the correct statistical target family should be.

For example, we should not assume the derived-drive scoring representation is simply `{0, 3, 7}` until the audit confirms the actual distribution.

## Why dataset first

A drive simulator can be built in several ways:

1. regression on drive points;
2. hurdle model: score/no-score, then points conditional on scoring;
3. multinomial drive-outcome model;
4. state-transition model within drives.

Choosing among them before inspecting the actual drive target distribution would be premature. The reliability-first workflow is therefore:

```text
materialize -> audit -> choose target model -> walk-forward validate -> simulator
```

## Command

Start with one season:

```bash
python -m cfb_analytics.analytics.drive_state_research --season 2023
```

The command reads existing derived drives and existing pregame football-mechanism matchups. It does not regenerate profiles, snapshots, or play-by-play metrics.

After the schema/distribution audit passes, the full corpus can be materialized with:

```bash
python -m cfb_analytics.analytics.drive_state_research --all
```

## Prediction v1 and current simulator

Prediction v1 remains locked and unchanged.

The existing historical simulator also remains unchanged. This research layer is intended to become an independent mechanistic challenger, which can later be compared against the macro margin model and potentially blended only if out-of-sample evidence supports it.
