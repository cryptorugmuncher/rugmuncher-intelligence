#!/bin/bash
# RMI Infrastructure Deployment Script
# =====================================

set -e

echo "🚀 RMI Infrastructure Deployment"
echo "================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please copy .env.example to .env and fill in your values"
    exit 1
fi

# Load environment variables
export $(grep -v '^#' .env | xargs)

echo ""
echo "📦 Step 1: Creating Docker volumes..."
docker volume create rmi_redis_data 2>/dev/null || true
docker volume create rmi_nocodb_data 2>/dev/null || true
docker volume create rmi_baserow_data 2>/dev/null || true
docker volume create rmi_backend_logs 2>/dev/null || true
echo -e "${GREEN}✓ Volumes created${NC}"

echo ""
echo "🔄 Step 2: Pulling latest images..."
docker-compose pull
echo -e "${GREEN}✓ Images pulled${NC}"

echo ""
echo "🏗️  Step 3: Building backend..."
docker-compose build rmi-backend
echo -e "${GREEN}✓ Backend built${NC}"

echo ""
echo "🚀 Step 4: Starting services..."
docker-compose up -d redis
echo "  ✓ Redis started"

sleep 2

docker-compose up -d nocodb
echo "  ✓ NocoDB started (Port 8080)"

docker-compose up -d baserow
echo "  ✓ Baserow started (Port 8081)"

docker-compose up -d rmi-backend
echo "  ✓ RMI Backend started (Port 8000)"

echo ""
echo "⏳ Step 5: Waiting for services to be healthy..."
sleep 10

# Check health
echo ""
echo "🏥 Step 6: Health checks..."

# Check Redis
if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
    echo -e "  ${GREEN}✓ Redis is healthy${NC}"
else
    echo -e "  ${RED}✗ Redis failed${NC}"
fi

# Check Backend
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo -e "  ${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "  ${YELLOW}⚠ Backend starting...${NC}"
fi

echo ""
echo "================================="
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo "================================="
echo ""
echo "🌐 Services:"
echo "  • NocoDB (Spreadsheet):    http://localhost:8080"
echo "  • Baserow (Team DB):       http://localhost:8081"
echo "  • RMI Backend API:         http://localhost:8000"
echo "  • Redis:                   localhost:6379"
echo ""
echo "📚 Next steps:"
echo "  1. Configure NocoDB to connect to Supabase"
echo "  2. Set up Nginx reverse proxy (optional)"
echo "  3. Configure SSL with Let's Encrypt"
echo ""
echo "🔧 Useful commands:"
echo "  View logs:    docker-compose logs -f"
echo "  Stop all:     docker-compose down"
echo "  Restart:      docker-compose restart"
echo "  Update:       docker-compose pull && docker-compose up -d"
echo ""
