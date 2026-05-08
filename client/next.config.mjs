import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable React strict mode for development best practices
  reactStrictMode: true,

  turbopack: {
    root: __dirname,
  },

  // Optimize images from external sources if needed
  images: {
    unoptimized: true,
  },

  // Production source maps for debugging
  productionBrowserSourceMaps: false,

  // Ensure API calls work in production
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
    return [
      {
        source: "/api/proxy/:path*",
        destination: `${apiUrl}/:path*`,
      },
    ];
  },

  // Security headers
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-DNS-Prefetch-Control", value: "on" },
        ],
      },
    ];
  },
};

export default nextConfig;
