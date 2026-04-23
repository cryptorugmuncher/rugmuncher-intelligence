#!/bin/bash
# 🔧 RMI System Configuration Script
# Usage: bash /root/rmi/scripts/setup/configure_system.sh

set -e

echo "═══════════════════════════════════════════════════════════"
echo "  🔧 RMI System Configuration"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}Note: Some operations may require sudo${NC}"
fi

echo "📋 Configuration Checklist:"
echo ""

# 1. Git Configuration
echo "1️⃣  Git Configuration"
read -p "Enter your email (cryptorugmuncher@gmail.com): " email
email=${email:-cryptorugmuncher@gmail.com}
read -p "Enter your name: " name
name=${name:-"Crypto Rug Muncher"}

git config --global user.email "$email"
git config --global user.name "$name"
echo -e "${GREEN}✅ Git configured: $email / $name${NC}"
echo ""

# 2. Supabase Configuration
echo "2️⃣  Supabase Configuration"
echo "   Get your credentials from: https://supabase.com/dashboard"
read -p "Supabase Project URL (https://...): " supabase_url
read -p "Supabase Anon Key: " supabase_anon_key
read -p "Supabase Service Role Key: " supabase_service_key

if [ -n "$supabase_url" ] && [ -n "$supabase_anon_key" ]; then
    # Update .env file
    sed -i "s|^SUPABASE_URL=.*|SUPABASE_URL=$supabase_url|" /root/rmi/.env
    sed -i "s|^SUPABASE_KEY=.*|SUPABASE_KEY=$supabase_anon_key|" /root/rmi/.env
    sed -i "s|^SUPABASE_KEY=.*|SUPABASE_SERVICE_KEY=$supabase_service_key|" /root/rmi/backend/.env 2>/dev/null || true
    echo -e "${GREEN}✅ Supabase configured${NC}"
else
    echo -e "${YELLOW}⚠️  Supabase credentials not provided - skipped${NC}"
fi
echo ""

# 3. API Keys Configuration
echo "3️⃣  API Keys Configuration"
echo "   You'll need API keys from:"
echo "   - Helius: https://helius.xyz (100k requests/month free)"
echo "   - Groq: https://groq.com (fast LLM inference)"
echo "   - Telegram: https://t.me/BotFather"
echo ""

# Helius
read -p "Helius API Key: " helius_key
if [ -n "$helius_key" ]; then
    echo "export HELIUS_API_KEY=\"$helius_key\"" >> /root/rmi/.secrets/solana_apis.sh
    echo -e "${GREEN}✅ Helius API key saved${NC}"
fi

# Groq
read -p "Groq API Key: " groq_key
if [ -n "$groq_key" ]; then
    echo "export GROQ_API_KEY=\"$groq_key\"" >> /root/rmi/.secrets/ai_apis.sh
    echo "export OPENROUTER_API_KEY=\"$groq_key\"" >> /root/rmi/.secrets/ai_apis.sh
    echo -e "${GREEN}✅ Groq API key saved${NC}"
fi

# Telegram
read -p "Telegram Bot Token: " telegram_token
if [ -n "$telegram_token" ]; then
    echo "export TELEGRAM_BOT_TOKEN=\"$telegram_token\"" >> /root/rmi/.secrets/telegram_bot.sh
    echo -e "${GREEN}✅ Telegram Bot token saved${NC}"
fi

echo ""

# 4. n8n Configuration
echo "4️⃣  n8n Configuration (optional)"
read -p "n8n Webhook URL (leave blank to skip): " n8n_url
if [ -n "$n8n_url" ]; then
    echo "export N8N_WEBHOOK_URL=\"$n8n_url\"" >> /root/rmi/.secrets/n8n_config.sh
    echo -e "${GREEN}✅ n8n configured${NC}"
fi
echo ""

# 5. Load all secrets
echo "5️⃣  Loading Secrets..."
if [ -f /root/rmi/.secrets/master_env.sh ]; then
    source /root/rmi/.secrets/master_env.sh
    echo -e "${GREEN}✅ Secrets loaded${NC}"
else
    echo -e "${YELLOW}⚠️  Master env script not found${NC}"
fi
echo ""

# 6. Create backend .env if needed
echo "6️⃣  Backend Environment Setup"
if [ ! -f /root/rmi/backend/.env ]; then
    echo "Creating backend/.env..."
    cat > /root/rmi/backend/.env << EOF
SUPABASE_URL=$supabase_url
SUPABASE_SERVICE_KEY=$supabase_service_key
SECRET_KEY=$(openssl rand -hex 32)
EOF
    echo -e "${GREEN}✅ Backend .env created${NC}"
fi
echo ""

# 7. Test Python imports
echo "7️⃣  Testing Python Imports..."
cd /root/rmi/backend
python3 -c "from config.settings import settings; print('Settings loaded')" 2>/dev/null && echo -e "${GREEN}✅ Backend imports working${NC}" || echo -e "${YELLOW}⚠️  Some imports may need attention${NC}"
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "  ✅ Configuration Complete!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Start the backend: cd /root/rmi/backend && python3 -m uvicorn main:app --reload"
echo "2. Test API: curl http://localhost:8000/api/v1/health"
echo "3. Configure GitHub: git remote add origin https://github.com/YOURUSERNAME/rmi.git"
echo ""
echo "For help, see: SYSTEM_VERIFICATION_REPORT.md"
