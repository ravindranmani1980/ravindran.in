#!/bin/sh
# cloudflare-build.sh
# Build step for Cloudflare Pages (Build command: sh cloudflare-build.sh, Build output directory: dist).
# Copies the site into dist/ and leaves out files that belong in the repository but not on the live site.
set -e
rm -rf dist
mkdir dist
for f in * .[!.]*; do
  [ -e "$f" ] || continue
  case "$f" in
    dist|_tools|_templates|.git|.github|.gitignore|README.md|CNAME|LICENSE|cloudflare-build.sh|.DS_Store|functions|package.json|package-lock.json|node_modules|wrangler.toml) continue ;;
  esac
  cp -R "$f" dist/
done
echo "Copied site to dist/: $(find dist -type f | wc -l) files"

# The apps moved to apps.ravindran.in (repo ravindran-apps) on 27 Oct 2026.
