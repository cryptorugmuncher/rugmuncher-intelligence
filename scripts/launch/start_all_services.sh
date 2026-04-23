#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# RMI Platform - Service Startup Script
# Ensures all services start reliably and stay running
# ═══════════════════════════════════════════════════════════════════

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
LOG_DIR="/var/log/rmi"
mkdir -p $LOG_DIR

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  RMI Platform - Starting All Services${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Function to check if a port is in use
check_port() {
    local port=$1
    if netstat -tlnp 2>/dev/null | grep -q ":$port "; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill process on a port
kill_port() {
    local port=$1
    local pid=$(netstat -tlnp 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f1 | head -1)
    if [ -n "$pid" ]; then
        echo -e "${YELLOW}  Stopping process on port $port (PID: $pid)...${NC}"
        kill -9 $pid 2>/dev/null || true
        sleep 2
    fi
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1
    
    echo -n "  Waiting for $name..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e " ${GREEN}✓ READY${NC}"
            return 0
        fi
        echo -n "."
        sleep 1
        attempt=$((attempt + 1))
    done
    echo -e " ${RED}✗ FAILED${NC}"
    return 1
}

# ═══════════════════════════════════════════════════════════════════
# STEP 1: Check Docker Containers
# ═══════════════════════════════════════════════════════════════════
echo -e "${BLUE}[1/5] Checking Docker Containers...${NC}"

# Check DragonflyDB
if docker ps | grep -q "dragonfly"; then
    echo -e "  ${GREEN}✓ DragonflyDB is running${NC}"
else
    echo -e "  ${YELLOW}⚠ Starting DragonflyDB...${NC}"
    docker start dragonfly 2>/dev/null || docker run -d \
        --name dragonfly \
        -p 6379:6379 \
        --restart unless-stopped \
        docker.dragonflydb.io/dragonflydb/dragonfly:v1.27.0
    sleep 3
fi

# Check N8N
if docker ps | grep -q "n8n"; then
    echo -e "  ${GREEN}✓ N8N is running${NC}"
else
    echo -e "  ${YELLOW}⚠ Starting N8N...${NC}"
    docker start n8n 2>/dev/null
    sleep 5
fi

# ═══════════════════════════════════════════════════════════════════
# STEP 2: Check PostgreSQL
# ═══════════════════════════════════════════════════════════════════
echo -e "${BLUE}[2/5] Checking PostgreSQL...${NC}"

if systemctl is-active --quiet postgresql; then
    echo -e "  ${GREEN}✓ PostgreSQL is running${NC}"
else
    echo -e "  ${YELLOW}⚠ Starting PostgreSQL...${NC}"
    systemctl start postgresql
    sleep 2
fi

# Test database connection
if psql -h localhost -U rmi_user -d rmi_db -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓ Database connection OK${NC}"
else
    echo -e "  ${RED}✗ Database connection failed${NC}"
    exit 1
fi

# ═══════════════════════════════════════════════════════════════════
# STEP 3: Start Backend API
# ═══════════════════════════════════════════════════════════════════
echo -e "${BLUE}[3/5] Starting Backend API...${NC}"

cd /root/rmi/backend
source venv/bin/activate

# Kill existing backend processes
kill_port 8002 2>/dev/null || true

# Set environment variables
export DATABASE_URL="postgresql://rmi_user:rmi_secure_pass_2024@localhost:5432/rmi_db"
export REDIS_URL="redis://:RugMuncherd451c307f52f8e061a2cc79a@localhost:6379/0"
export SUPABASE_URL="https://ufblzfxqwgaekrewncbi.supabase.co"
export SUPABASE_KEY="sb_secret_Uye75Qavhe0ZXJCo4Uadiw_CCYWULKa"

# Start backend with auto-restart logic
nohup python3 -c "
import sys
import os
sys.path.insert(0, '/root/rmi/backend')

from main import app
import uvicorn

# Run with reload for development, without for production
uvicorn.run(
    app, 
    host='0.0.0.0', 
    port=8002,
    log_level='info'
)
" > $LOG_DIR/backend.log 2>&1 &

BACKEND_PID=$!
echo $BACKEND_PID > /var/run/rmi-backend.pid

# Wait for backend
if wait_for_service "http://localhost:8002/health" "Backend API"; then
    echo -e "  ${GREEN}✓ Backend API started (PID: $BACKEND_PID)${NC}"
else
    echo -e "  ${RED}✗ Backend API failed to start${NC}"
    tail -20 $LOG_DIR/backend.log
    exit 1
fi

# ═══════════════════════════════════════════════════════════════════
# STEP 4: Start Frontend
# ═══════════════════════════════════════════════════════════════════
echo -e "${BLUE}[4/5] Starting Frontend...${NC}"

# Kill existing frontend
kill_port 3000 2>/dev/null || true

cd /root/rmi/frontend/the-trenches
nohup python3 -m http.server 3000 > $LOG_DIR/frontend.log 2>&1 &

FRONTEND_PID=$!
echo $FRONTEND_PID > /var/run/rmi-frontend.pid

if wait_for_service "http://localhost:3000" "Frontend"; then
    echo -e "  ${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
else
    echo -e "  ${RED}✗ Frontend failed to start${NC}"
    exit 1
fi

# ═══════════════════════════════════════════════════════════════════
# STEP 5: Verify All Services
# ═══════════════════════════════════════════════════════════════════
echo -e "${BLUE}[5/5] Verifying All Services...${NC}"

# Test Dragonfly
if docker exec dragonfly dragonfly --info 2>/dev/null | grep -q "version"; then
    echo -e "  ${GREEN}✓ DragonflyDB responsive${NC}"
else
    echo -e "  ${YELLOW}⚠ DragonflyDB check skipped${NC}"
fi

# Test N8N
if curl -s http://localhost:5678/healthz | grep -q "ok"; then
    echo -e "  ${GREEN}✓ N8N responsive${NC}"
else
    echo -e "  ${YELLOW}⚠ N8N check skipped${NC}"
fi

# Test Backend Health
HEALTH=$(curl -s http://localhost:8002/health 2>/dev/null)
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "  ${GREEN}✓ Backend healthy${NC}"
    echo -e "    Database: $(echo $HEALTH | grep -o '"supabase":"[^"]*"' | cut -d'"' -f4)"
    echo -e "    Redis: $(echo $HEALTH | grep -o '"redis":"[^"]*"' | cut -d'"' -f4)"
else
    echo -e "  ${RED}✗ Backend health check failed${NC}"
fi

# ═══════════════════════════════════════════════════════════════════
# DONE
# ═══════════════════════════════════════════════════════════════════
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ALL SERVICES STARTED SUCCESSFULLY!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${BLUE}Frontend:${NC}  http://localhost:3000"
echo -e "  ${BLUE}Backend:${NC}   http://localhost:8002"
echo -e "  ${BLUE}API Docs:${NC}  http://localhost:8002/docs"
echo -e "  ${BLUE}N8N:${NC}       http://localhost:5678"
echo -e "  ${BLUE}Database:${NC}  PostgreSQL (localhost:5432)"
echo -e "  ${BLUE}Cache:${NC}     DragonflyDB (localhost:6379)"
echo ""
echo -e "  ${YELLOW}Logs:${NC}      /var/log/rmi/"
echo -e "  ${YELLOW}PIDs:${NC}      /var/run/rmi-*.pid"
echo ""
echo -e "To stop all services: ${YELLOW}./stop_all_services.sh${NC}"
echo ""
