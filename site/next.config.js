/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: { unoptimized: true },
  // GitHub Pages serves under /<repo>/. Override at build time:
  //   BASE_PATH=/ib-maths-bank pnpm build
  basePath: process.env.BASE_PATH || '',
  assetPrefix: process.env.BASE_PATH || '',
};

module.exports = nextConfig;
