import path from "node:path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Keep repository-owned contributor instructions stable during local development.
  agentRules: false,

  // Legacy/parked URLs resolve at the routing layer instead of creating
  // server-rendered pages/functions on Vercel.
  async redirects() {
    return [
      { source: "/stories/:slug", destination: "/articles/:slug", permanent: true },
      { source: "/polls", destination: "/more", permanent: false },
      { source: "/recruiting/national", destination: "/new-additions", permanent: true },
      { source: "/recruiting/players/:id", destination: "/new-additions", permanent: true },
      { source: "/recruiting/teams/:team", destination: "/new-additions", permanent: true },
      { source: "/football/:season", destination: "/analytics?year=:season", permanent: true },
      { source: "/teams/:team/:season", destination: "/analytics?year=:season", permanent: true },
      { source: "/creator-hub/:creatorSlug/research", destination: "/creator-hub/:creatorSlug/library/research", permanent: false },
      { source: "/creator-hub/:creatorSlug/visuals", destination: "/creator-hub/:creatorSlug/library/visuals", permanent: false },
      { source: "/creator-hub/:creatorSlug/notes", destination: "/creator-hub/:creatorSlug/library/notes", permanent: false },
      { source: "/creator-hub/:creatorSlug/library", destination: "/creator-hub/:creatorSlug/library/research", permanent: false }
    ];
  },

  // Turbopack's file tracer rejects exclude/include globs that navigate
  // above the project root via "..". Rooting tracing one level up (at the
  // repository root) lets every glob stay root-relative instead.
  outputFileTracingRoot: path.join(process.cwd(), ".."),

  // Attach only the compact route-specific runtime bundle to server functions.
  // The canonical data/published tree is build input, not runtime output.
  outputFileTracingIncludes: {
    "/analytics": [
      ".published-data/**/*.json"
    ],
    "/players/*": [
      ".published-data/2026/michigan/*.json",
      ".published-data/directory_history/players/current-by-team/michigan.json"
    ]
  },
  //
  // This must apply to every route, not just the ones that read published
  // data directly: lib/server-data.ts's readJson() resolves its local-dev
  // fallback path via path.join(process.cwd(), "..", "data", "published", ...)
  // with a dynamic tail, which defeats Next's static file tracer. The tracer
  // falls back to conservatively bundling the entire ../data/published tree
  // (3,651 files, ~480MB) into any route that transitively imports it — and
  // 19 routes do, including the homepage. Left unexcluded, each of those
  // routes' serverless functions traces and packages that whole tree,
  // which is what was driving multi-minute Vercel builds.
  outputFileTracingExcludes: {
    "**": [
      "../data/published/**/*"
    ]
  }
};

export default nextConfig;
