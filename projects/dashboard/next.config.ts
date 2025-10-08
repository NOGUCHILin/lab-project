import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Build output directory can be separated per environment
  distDir: process.env.NEXT_DIST_DIR || '.next',
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  // Allow cross-origin requests from Tailscale domain during development
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Access-Control-Allow-Origin',
            value: 'https://home-lab-01.tail4ed625.ts.net',
          },
          {
            key: 'Access-Control-Allow-Methods',
            value: 'GET, POST, PUT, DELETE, OPTIONS',
          },
          {
            key: 'Access-Control-Allow-Headers',
            value: 'Content-Type, Authorization',
          },
        ],
      },
    ];
  },
  // Configure allowed dev origins for Tailscale access
  allowedDevOrigins: [
    'https://home-lab-01.tail4ed625.ts.net',
    'https://home-lab-01.tail4ed625.ts.net:3000',
  ],
};

export default nextConfig;
