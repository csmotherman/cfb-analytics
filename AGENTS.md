# Codex Repository Guide

## Product identity

This repository powers **SOAR Analytics**, a college-football analytics product. User-facing website work must use the SOAR Analytics name. Do not present the product as “CFB Analytics Pilot,” “prediction-models,” or a generic dashboard.

SOAR’s job is to make advanced football analytics feel understandable, explorable, and visually memorable without weakening the underlying methodology.

## Start here

Before changing code, read the documents that match the task.

### Website / product / design work

1. `docs/SOAR_ANALYTICS_WEBSITE_VISION.md` — product and experience source of truth.
2. `website/AGENTS.md` — scoped frontend implementation rules.
3. `website/README.md` — local setup and current website status.
4. `docs/TEAM_PROFILES.md` — team-profile semantics when editing team-facing surfaces.
5. `docs/METRIC_REGISTRY.md` — authoritative metric definitions and readiness.

### Analytics / model work

1. `README.md` — repository checkpoint and architecture.
2. `docs/METRIC_REGISTRY.md` — authoritative metric contracts.
3. Relevant design/research document under `docs/` before changing a model or definition.

## Architecture contract

The Python analytics system is the source of truth for football calculations. The website consumes generated artifacts; it must not silently recreate or reinterpret metric logic in TypeScript.

Current high-level flow:

```text
CFBD raw evidence
  -> canonical games / drives / plays
  -> derived team-game analytics
  -> team-season / profile artifacts
  -> predictive and identity research artifacts
  -> website data adapters
  -> SOAR Analytics UI
```

Do not invent values when an artifact or metric is unavailable. Missing data should produce an intentional empty state, not fabricated statistics.

## Reliability rules

- Preserve raw source evidence.
- Do not silently change locked denominators, metric directions, rating equations, or semantic definitions.
- Version research definitions when behavior materially changes.
- Keep public-facing language simpler than the implementation while preserving the underlying meaning.
- Prefer a small, testable change over an unexplained rewrite of analytics logic.

## Validation

For Python changes, run the narrowest relevant tests and then the broader suite when practical:

```bash
pytest
```

For website changes:

```bash
cd website
npm run typecheck
npm run build
```

If browser/visual tooling is available, also inspect the changed routes at desktop and mobile widths. A UI task is not complete merely because TypeScript compiles.

## Website quality bar

The website is no longer an intentionally plain prototype. It is being productized as SOAR Analytics.

For visual or UX work:

- Read `docs/SOAR_ANALYTICS_WEBSITE_VISION.md` first.
- Build an authored sports product, not a generic SaaS/admin dashboard.
- Make important interactions visually dominant; do not turn every data point into an identical card.
- Use motion and 3D only where they communicate hierarchy, relationship, movement, or identity.
- Keep team colors contextual; they should not destroy the global SOAR visual system.
- Design responsive states intentionally.
- Preserve keyboard accessibility and reduced-motion behavior.
- Do not expose repository paths, build commands, missing-artifact instructions, or developer diagnostics as primary public content.

## Change discipline

When a task changes a public product contract, update the corresponding documentation in the same change. If code and documentation disagree, investigate rather than guessing which one is current.

For large website work, implement one documented phase or surface at a time, validate it, and leave the next phase clearly separable. Avoid broad “redesign everything” patches that are impossible to review.
