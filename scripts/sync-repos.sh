#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# RMI Repo Sync — Backend manages the project
# ═══════════════════════════════════════════════════════════════════
# Usage: ./scripts/sync-repos.sh
# 1. Pushes backend/main → backend-origin (private repo)
# 2. Fast-forwards frontend/main → backend/main
# 3. Pushes frontend/main → frontend-origin (public repo)
# ═══════════════════════════════════════════════════════════════════
set -e

cd "$(dirname "$0")/.."

echo "🔧 RMI Repo Sync — Backend is the source of truth"
echo "==================================================="

# Ensure we're on backend/main
git checkout backend/main

# Pull latest backend (in case another machine pushed)
echo "📥 Pulling backend/main..."
git pull backend-origin backend/main || true

# Push backend to private repo
echo "📤 Pushing backend/main → backend-origin..."
git push backend-origin backend/main

# Fast-forward frontend/main to backend/main
echo "🔄 Fast-forwarding frontend/main → backend/main..."
git checkout frontend/main
git merge backend/main --ff-only

# Push frontend to public repo
echo "📤 Pushing frontend/main → frontend-origin..."
git push frontend-origin frontend/main

# Return to backend/main as the working branch
git checkout backend/main

echo "✅ Sync complete. Both repos are aligned at:"
git log --oneline -1 backend/main
