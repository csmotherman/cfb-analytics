import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Keep repository-owned contributor instructions stable during local development.
  agentRules: false,

  // prepare-deploy-data.mjs creates this compact, website-only bundle before
  // every production build. Explicit tracing makes it available to dynamic
  // server-rendered routes on Vercel without shipping the 477 MB archive tree.
  outputFileTracingIncludes: {
    "/*": [".published-data/**/*.json"]
  }
};

export default nextConfig;
