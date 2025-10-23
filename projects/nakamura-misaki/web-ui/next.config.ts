import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Standalone output for Nix deployment
  output: 'standalone',

  // Proxy API requests to FastAPI backend
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:3001/api/:path*',
      },
    ];
  },
};

export default nextConfig;
