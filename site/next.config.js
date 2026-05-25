/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: { unoptimized: true },
  // Empty by default. For deploys to a sub-path on github.io (no custom domain),
  // override at build time:  BASE_PATH=/ib-maths-bank pnpm build
  basePath: process.env.BASE_PATH || '',
  assetPrefix: process.env.BASE_PATH || '',
};

module.exports = nextConfig;
