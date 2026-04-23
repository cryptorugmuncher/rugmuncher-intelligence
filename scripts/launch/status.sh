#!/bin/bash
# RMI Platform Status Check

echo "═══════════════════════════════════════════════════════════════"
echo "  RMI Platform - Service Status"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check each service
check_service() {
    local name=$1
    local url=$2
    
    if curl -s "$url" > /dev/null 2>&1; then
        echo "✅ $name - RUNNING"
    else
        echo "❌ $name - DOWN"
    fi
}

echo "Services:"
check_service "Backend API" "http://localhost:8002/health"
check_service "Frontend" "http://localhost:3000"
check_service "N8N" "http://localhost:5678/healthz"

echo ""
echo "Docker Containers:"
docker ps --format "  {{.Names}}: {{.Status}}" | grep -E "dragonfly|n8n" || echo "  No containers running"

echo ""
echo "Database:"
if pg_isready -h localhost > /dev/null 2>&1; then
    echo "✅ PostgreSQL - RUNNING"
else
    echo "❌ PostgreSQL - DOWN"
fi

echo ""
echo "Redis/Dragonfly:"
if redis-cli -a "RugMuncherd451c307f52f8e061a2cc79a" ping > /dev/null 2>&1; then
    echo "✅ DragonflyDB - RUNNING"
else
    echo "❌ DragonflyDB - DOWN"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Quick Links:"
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:8002"
echo "  API Docs:  http://localhost:8002/docs"
echo "  N8N:       http://localhost:5678"
echo ""
