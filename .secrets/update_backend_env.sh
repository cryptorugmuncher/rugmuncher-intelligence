#!/bin/bash
# 🔄 Update backend .env file from secrets

SECRETS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="/root/rmi/backend"
ENV_FILE="$BACKEND_DIR/.env"

echo "🔄 Updating backend .env file..."

# Source all secrets
source "$SECRETS_DIR/blockchain_apis.sh"
source "$SECRETS_DIR/ai_apis.sh"
source "$SECRETS_DIR/scraping_apis.sh"
source "$SECRETS_DIR/telegram_bot.sh"
source "$SECRETS_DIR/n8n_config.sh"
source "$SECRETS_DIR/notification_apis.sh"
source "$SECRETS_DIR/monitoring_apis.sh"

# Create .env file
cat > "$ENV_FILE" << ENVEOF
# RMI Backend Environment Variables
# Auto-generated from /root/rmi/.secrets/
# Last updated: $(date)

# App
DEBUG=false
ENVIRONMENT=production
SECRET_KEY=${SECRET_KEY:-$(openssl rand -hex 32)}

# Supabase
SUPABASE_URL=https://ufblzfxqwgaekrewncbi.supabase.co
SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY:-}
SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY:-}

# Database
REDIS_URL=${REDIS_URL:-redis://localhost:6379/0}

# Blockchain APIs
ETHEREUM_RPC=${ETHEREUM_RPC:-https://eth.llamarpc.com}
SOLANA_RPC=${SOLANA_RPC:-https://api.mainnet-beta.solana.com}
BSC_RPC=${BSC_RPC:-https://bsc-dataseed.binance.org/}

# AI/LLM APIs
GROQ_API_KEY=${GROQ_API_KEY:-}
OPENAI_API_KEY=${OPENAI_API_KEY:-}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}

# Scraping APIs
APIFY_API_KEY=${APIFY_API_KEY:-}
FIRECRAWL_API_KEY=${FIRECRAWL_API_KEY:-}
BRAVE_API_KEY=${BRAVE_API_KEY:-}

# Telegram
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-}

# n8n
N8N_WEBHOOK_URL=${N8N_WEBHOOK_URL:-}
N8N_API_KEY=${N8N_API_KEY:-}

# Notifications
SENDGRID_API_KEY=${SENDGRID_API_KEY:-}
TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID:-}
TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN:-}

# Monitoring
SENTRY_DSN=${SENTRY_DSN:-}
LOG_LEVEL=${LOG_LEVEL:-INFO}
ENVEOF

echo "✅ Backend .env file updated: $ENV_FILE"
echo ""
echo "📊 Configured APIs:"
grep -E "^[A-Z_]+=" "$ENV_FILE" | grep -v "=$" | wc -l | xargs echo "  Active:"
grep -E "^[A-Z_]+=$" "$ENV_FILE" | wc -l | xargs echo "  Missing:"
