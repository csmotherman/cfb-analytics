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

  // Only /analytics reads published JSON at request time. All finite Michigan
  // routes are prerendered, so attaching the data bundle globally would duplicate
  // it across Vercel functions and dramatically slow deployment packaging.
  outputFileTracingIncludes: {
    "/analytics": [".published-data/**/*.json"]
  }
};

export default nextConfig;
