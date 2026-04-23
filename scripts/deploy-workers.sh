#!/bin/bash
# Deploy RugMuncher Cloudflare Workers
set -euo pipefail

cd "$(dirname "$0")/../workers/api-gateway"
echo "🚀 Deploying API Gateway Worker..."
npx wrangler deploy

cd "../frontend-edge"
echo "🚀 Deploying Frontend Edge Worker..."
npx wrangler deploy

echo "✅ Workers deployed"
echo ""
echo "Next steps:"
echo "1. Add routes in Cloudflare dashboard or via wrangler:"
echo "   wrangler route add 'api.rugmunch.io/*' rmi-api-gateway"
echo "   wrangler route add 'rugmunch.io/*' rmi-frontend-edge"
echo "   wrangler route add 'app.rugmunch.io/*' rmi-frontend-edge"
echo "2. Enable caching rules in Cloudflare dashboard for extra speed"
