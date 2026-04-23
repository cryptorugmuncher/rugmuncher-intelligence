#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# RMI Platform - Service Stop Script
# ═══════════════════════════════════════════════════════════════════

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  RMI Platform - Stopping All Services${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Stop Backend
if [ -f /var/run/rmi-backend.pid ]; then
    PID=$(cat /var/run/rmi-backend.pid)
    if kill -0 $PID 2>/dev/null; then
        echo -e "  Stopping Backend (PID: $PID)..."
        kill -9 $PID 2>/dev/null || true
    fi
    rm -f /var/run/rmi-backend.pid
    echo -e "  ${GREEN}✓ Backend stopped${NC}"
fi

# Stop Frontend
if [ -f /var/run/rmi-frontend.pid ]; then
    PID=$(cat /var/run/rmi-frontend.pid)
    if kill -0 $PID 2>/dev/null; then
        echo -e "  Stopping Frontend (PID: $PID)..."
        kill -9 $PID 2>/dev/null || true
    fi
    rm -f /var/run/rmi-frontend.pid
    echo -e "  ${GREEN}✓ Frontend stopped${NC}"
fi

# Kill any remaining processes on ports
echo -e "  Cleaning up remaining processes..."
for port in 3000 8002; do
    PID=$(netstat -tlnp 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f1 | head -1)
    if [ -n "$PID" ]; then
        kill -9 $PID 2>/dev/null || true
    fi
done

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ALL SERVICES STOPPED${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
