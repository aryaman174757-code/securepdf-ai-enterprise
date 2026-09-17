/** @type {import('next').NextConfig} */
const isGhPages = process.env.BUILD_FOR_GH_PAGES === "true";
const repoName = "securepdf-ai-enterprise";

const nextConfig = {
  output: isGhPages ? "export" : undefined,
  basePath: isGhPages ? `/${repoName}` : "",
  assetPrefix: isGhPages ? `/${repoName}/` : "",
  trailingSlash: true,
  reactStrictMode: true,
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
