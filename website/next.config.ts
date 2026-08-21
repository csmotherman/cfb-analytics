import path from "node:path";
import type { NextConfig } from "next";

const repositoryRoot=path.resolve(process.cwd(),"..");

const nextConfig: NextConfig = {
  // Keep repository-owned contributor instructions stable during local development.
  agentRules: false,

  // The Next app lives in /website while production data lives at repo root.
  // Vercel/Next output tracing must be allowed to follow files outside /website.
  outputFileTracingRoot: repositoryRoot,

  // Only ship the production-facing slice of published data. Do not bundle
  // data/published/directory_history (the large research/archive tree).
  outputFileTracingIncludes: {
    "/*": [
      "../data/published/2026/**/*.json",
      "../data/published/20*/analytics/ridge-overview.json",
      "../data/published/20*/teams/michigan/*.json",
      "../data/published/20*/national/teams.json",
      "../data/published/20*/national/rankings.json",
      "../src/cfb_analytics/config/*.json"
    ]
  }
};

export default nextConfig;
