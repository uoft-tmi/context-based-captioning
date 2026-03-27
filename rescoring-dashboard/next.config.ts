import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',              // optimize for vercel
  poweredByHeader: false,            // remove x-powered-by header
  compress: true,                    // enable compression
  images: {
    remotePatterns: [],              // add any external image domains if needed
    formats: ['image/avif', 'image/webp'],
  },
  experimental: {
    optimizeCss: true,
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-DNS-Prefetch-Control', value: 'on' },
          { key: 'Strict-Transport-Security', value: 'max-age=63072000' },
          { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Referrer-Policy', value: 'origin-when-cross-origin' },
        ],
      },
    ]
  }
};

export default nextConfig;
