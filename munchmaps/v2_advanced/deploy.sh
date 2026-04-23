#!/bin/bash
# MunchMaps V2 - One-Command Deployment Script
# Deploys full stack for zero-cost operation

set -e

echo "🚀 MunchMaps V2 - Zero-Cost Deployment"
echo "========================================"

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker required"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose required"; exit 1; }

# Configuration
echo ""
echo "📋 Configuration"
echo "---------------"
read -p "Domain name (e.g., munchmaps.io): " DOMAIN
read -p "Admin email: " ADMIN_EMAIL
read -sp "JWT Secret (generate random): " JWT_SECRET
echo ""

# Create environment file
cat > .env << ENVFILE
# MunchMaps V2 Environment
DOMAIN=$DOMAIN
ADMIN_EMAIL=$ADMIN_EMAIL
JWT_SECRET=$JWT_SECRET

# Database
DATABASE_URL=postgresql://munchmaps:password@postgres:5432/munchmaps
REDIS_URL=redis://redis:6379

# API Keys (Free tiers - create multiple accounts for rotation)
ETHERSCAN_KEY_1=${ETHERSCAN_KEY_1:-}
ETHERSCAN_KEY_2=${ETHERSCAN_KEY_2:-}
BSCSCAN_KEY_1=${BSCSCAN_KEY_1:-}
POLYGONSCAN_KEY_1=${POLYGONSCAN_KEY_1:-}
HELIUS_KEY=${HELIUS_KEY:-}
TRONGRID_KEY=${TRONGRID_KEY:-}

# Stripe (for billing)
STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY:-}
STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLISHABLE_KEY:-}

# Optional: Sentry for error tracking
SENTRY_DSN=${SENTRY_DSN:-}
ENVFILE

echo "✅ Environment file created"

# Build and start
echo ""
echo "🔨 Building containers..."
cd deploy
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services
echo ""
echo "⏳ Waiting for services..."
sleep 10

# Health check
echo ""
echo "🏥 Health Check"
curl -s http://localhost:8000/api/health | jq . || echo "⚠️  API not responding yet"

# Setup complete
echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo "======================="
echo ""
echo "🌐 URLs:"
echo "   Website: http://localhost (or https://$DOMAIN)"
echo "   API: http://localhost:8000/api"
echo "   API Docs: http://localhost:8000/docs"
echo "   Admin: http://localhost/admin/dashboard.html"
echo ""
echo "📊 Default Admin Login:"
echo "   Email: admin@munchmaps.io"
echo "   Password: changeme-immediately"
echo ""
echo "💰 Free Tier Limits:"
echo "   - 5 wallet lookups per day per user"
echo "   - 10 requests per minute"
echo ""
echo "🔄 To update: docker-compose pull && docker-compose up -d"
echo "🛑 To stop: docker-compose down"
echo "📜 Logs: docker-compose logs -f"
echo ""
echo "🎉 Ready to catch scammers!"
