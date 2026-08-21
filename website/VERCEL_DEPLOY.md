# Vercel deployment

This Next.js app is deployed from the `website` directory. Production builds create a compact `.published-data` bundle from repository-owned football data before `next build` runs.

## Vercel project settings

When importing `csmotherman/cfb-analytics` into Vercel:

- Framework Preset: **Next.js**
- Root Directory: **website**
- Include files outside the root directory in the Build Step: **Enabled**
- Install Command: leave default (`npm install`)
- Build Command: leave default (`npm run build`)
- Output Directory: leave default (`.next`)
- Production Branch: **main**

The outside-root build option is required only so `scripts/prepare-deploy-data.mjs` can read `../data/published` while building. Runtime server functions read the generated `website/.published-data` bundle and do not depend on the repository-level data tree.

## Local deployment check

From the repository root:

```bash
cd website
npm run typecheck
npm run build
npm run start
```

The build should print a line similar to:

```text
Prepared <N> deployment JSON files (<size> MB) in .../website/.published-data
```

Then verify at least:

- `/`
- `/analytics?year=2025`
- `/analytics/offense?year=2025`
- `/analytics/defense?year=2025`
- `/team/roster`
- `/schedule`
- `/recruiting`

## Data policy

Do not copy `data/published/directory_history` into Vercel. It is archive/research data and is intentionally excluded from the deployment bundle.

The deployment bundle currently contains:

- the complete `data/published/2026` JSON tree;
- historical Michigan team JSON;
- historical national `teams.json`, `rankings.json`, and `conferences.json`;
- historical `analytics/ridge-overview.json`;
- small repository-owned analytics config JSON.

`.published-data` is generated and ignored by Git. Never commit it.
