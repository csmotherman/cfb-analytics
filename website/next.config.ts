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

  // Keep the public Game Room URL clean while one dynamic route handles both
  // the list view (sentinel "all") and individual game breakdowns.
  async rewrites() {
    return [
      { source: "/creator-hub/:creatorSlug/games", destination: "/creator-hub/:creatorSlug/games/all" }
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
  outputFileTracingExcludes: {
    "/analytics": [
      "../data/published/**/*"
    ],
    "/players/*": [
      "../data/published/**/*"
    ]
  }
};

export default nextConfig;
