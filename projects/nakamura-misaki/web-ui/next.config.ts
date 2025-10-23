import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Standalone output for Nix deployment
  output: 'standalone',

  // Proxy API requests to FastAPI backend (port 10000)
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:10000/api/:path*',
      },
    ];
  },
};

export default nextConfig;
