import type { NextConfig } from "next";

import path from "path";

const nextConfig: NextConfig = {
  /* config options here */
  turbopack: {
    root: path.resolve(__dirname),
  },
  async redirects() {
    return [
      { source: '/investigations', destination: '/investigation-board', permanent: true },
      { source: '/alerts', destination: '/alert-center', permanent: true },
      { source: '/suspects', destination: '/knowledge-graph', permanent: true },
      { source: '/officers', destination: '/officer-workspace', permanent: true },
      { source: '/copliot', destination: '/copilot', permanent: true },
    ];
  },
};

export default nextConfig;
