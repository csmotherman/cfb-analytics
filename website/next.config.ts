import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Keep repository-owned contributor instructions stable during local development.
  agentRules: false,

  // Legacy URLs resolve at the routing layer instead of creating server-rendered
  // pages/functions. Historical Michigan season URLs now land on the matching
  // Analytics year because the old History section no longer exists.
  async redirects() {
    return [
      { source: "/stories/:slug", destination: "/articles/:slug", permanent: true },
      { source: "/recruiting/national", destination: "/new-additions", permanent: true },
      { source: "/recruiting/players/:id", destination: "/new-additions", permanent: true },
      { source: "/recruiting/teams/:team", destination: "/new-additions", permanent: true },
      { source: "/football/:season", destination: "/analytics?year=:season", permanent: true },
      { source: "/teams/:team/:season", destination: "/analytics?year=:season", permanent: true }
    ];
  },

  // Attach data only to the functions that read it at request time. The compact
  // runtime bundle is ~2 MB, so use simple Turbopack-safe globs rather than
  // year-range character classes that its glob parser rejects.
  outputFileTracingIncludes: {
    "/analytics": [
      ".published-data/**/*.json"
    ],
    "/players/*": [
      ".published-data/2026/michigan/*.json",
      ".published-data/directory_history/players/current-by-team/michigan.json"
    ]
  }
};

export default nextConfig;
