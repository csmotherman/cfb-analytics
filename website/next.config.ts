import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Keep repository-owned contributor instructions stable during local development.
  agentRules: false,

  // These legacy URLs now resolve at the routing layer instead of creating
  // server-rendered pages/functions on Vercel's Hobby plan.
  async redirects() {
    return [
      { source: "/stories/:slug", destination: "/articles/:slug", permanent: true },
      { source: "/recruiting/national", destination: "/new-additions", permanent: true },
      { source: "/recruiting/players/:id", destination: "/new-additions", permanent: true },
      { source: "/recruiting/teams/:team", destination: "/new-additions", permanent: true }
    ];
  },

  // prepare-deploy-data.mjs creates this compact, website-only bundle before
  // every production build. Explicit tracing makes it available to dynamic
  // server-rendered routes on Vercel without shipping the 477 MB archive tree.
  outputFileTracingIncludes: {
    "/*": [".published-data/**/*.json"]
  }
};

export default nextConfig;
