#!/usr/bin/env bash
# RugMuncher GitHub Random Sync
# Pushes frontend (public) and backend (private) at random intervals

set -euo pipefail

LOG_FILE="/var/log/rmi-github-sync.log"
REPO_DIR="/root/rmi"
RAND_DELAY=$(( RANDOM % 300 ))  # 0-300s random delay before push

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Random chance to skip this run (roughly 40% skip rate = ~10 pushes/day if hourly)
RAND_CHANCE=$(( RANDOM % 100 ))
if [ "$RAND_CHANCE" -lt 40 ]; then
    log "SKIP: Random chance roll ($RAND_CHANCE/100) below threshold. No push this cycle."
    exit 0
fi

log "START: Random sync triggered (delay=${RAND_DELAY}s, chance=$RAND_CHANCE)"
sleep "$RAND_DELAY"

cd "$REPO_DIR"

# Commit any uncommitted changes with realistic messages
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
    git add -A
    MSG=$(shuf -n 1 <<'EOF'
chore: routine platform update
dev: iterative improvements
fix: minor adjustments
chore: sync state
dev: backend refinements
ui: frontend polish
chore: dependency bumps
EOF
)
    git commit -m "$MSG ($(date +%H:%M))" || true
    log "COMMIT: $MSG"
else
    log "STATUS: Working tree clean"
fi

# Update split branches
if git rev-parse --verify backend/main >/dev/null 2>&1; then
    git checkout backend/main 2>/dev/null || true
    git merge main --no-edit --allow-unrelated-histories 2>/dev/null || true
    # Rebuild backend branch from backend/ directory
    git branch -D backend-sync-tmp 2>/dev/null || true
    if git subtree split --prefix=backend -b backend-sync-tmp 2>/dev/null; then
        git push backend-private backend-sync-tmp:main 2>&1 | tail -3 | while read line; do log "BACKEND: $line"; done
        git branch -D backend-sync-tmp 2>/dev/null || true
    else
        # Fallback: if subtree split fails, use existing backend/main branch
        git push backend-private backend/main:main 2>&1 | tail -3 | while read line; do log "BACKEND: $line"; done
    fi
    git checkout main 2>/dev/null || true
else
    log "BACKEND: backend/main branch missing, skipping"
fi

if git rev-parse --verify frontend/main >/dev/null 2>&1; then
    git checkout frontend/main 2>/dev/null || true
    git merge main --no-edit --allow-unrelated-histories 2>/dev/null || true
    git branch -D frontend-sync-tmp 2>/dev/null || true
    if git subtree split --prefix=frontend -b frontend-sync-tmp 2>/dev/null; then
        git push frontend-public frontend-sync-tmp:main 2>&1 | tail -3 | while read line; do log "FRONTEND: $line"; done
        git branch -D frontend-sync-tmp 2>/dev/null || true
    else
        git push frontend-public frontend/main:main 2>&1 | tail -3 | while read line; do log "FRONTEND: $line"; done
    fi
    git checkout main 2>/dev/null || true
else
    log "FRONTEND: frontend/main branch missing, skipping"
fi

log "DONE: Sync cycle complete"
