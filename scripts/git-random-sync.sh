#!/bin/bash
# RugMuncher random-interval auto-sync script
# Runs from /root/rmi, commits changes, re-splits subtrees, and pushes to remotes.

set -euo pipefail

LOG_FILE="/var/log/rugmuncher-sync.log"
REPO_DIR="/root/rmi"

# Ensure log file exists and is writable
touch "$LOG_FILE" 2>/dev/null || true

# Redirect all output to log
exec >> "$LOG_FILE" 2>&1

echo "=== $(date -Iseconds) sync started ==="
cd "$REPO_DIR"

# Random chance: only proceed ~35% of the time
RAND=$((RANDOM % 100))
if [ "$RAND" -ge 35 ]; then
    echo "Skipped due to random chance (rand=$RAND)"
    echo "=== $(date -Iseconds) sync finished ==="
    exit 0
fi

# Commit any local changes (staged or unstaged)
if git diff --quiet && git diff --cached --quiet; then
    echo "No local changes to commit"
else
    git add -A
    git commit -m "auto: routine sync $(date -Iseconds)"
    echo "Committed local changes"
fi

# Re-split frontend subtree
echo "Splitting frontend subtree..."
git subtree split --prefix=rmi-frontend --branch=frontend/main

# Re-split backend subtree
echo "Splitting backend subtree..."
git subtree split --prefix=backend --branch=backend/main

# Push to remotes
echo "Pushing to remotes..."
git push frontend-origin frontend/main:main
git push backend-origin backend/main:main

echo "=== $(date -Iseconds) sync finished successfully ==="
