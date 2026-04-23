#!/bin/bash
# 🔐 RMI Platform - Master Environment File
# This file sources all individual API key files
# Usage: source /root/rmi/.secrets/master_env.sh

SECRETS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔐 Loading RMI API secrets..."
echo ""

# ===== CORE APIs =====
echo "📦 CORE APIs:"
source "$SECRETS_DIR/solana_apis.sh" 2>/dev/null && echo "  ✓ Solana (PRIMARY)" || echo "  ⬜ Solana not configured"
source "$SECRETS_DIR/blockchain_apis.sh" 2>/dev/null && echo "  ✓ Other Blockchains" || echo "  ⬜ Other chains not configured"
source "$SECRETS_DIR/ai_apis.sh" 2>/dev/null && echo "  ✓ AI/LLM" || echo "  ⬜ AI not configured"
source "$SECRETS_DIR/scraping_apis.sh" 2>/dev/null && echo "  ✓ Scraping" || echo "  ⬜ Scraping not configured"

# ===== ADVANCED INTEL =====
echo ""
echo "🕵️  ADVANCED INTEL:"
source "$SECRETS_DIR/advanced_intel.sh" 2>/dev/null && echo "  ✓ Arkham/Nansen/Chainalysis" || echo "  ⬜ Advanced intel not configured"
source "$SECRETS_DIR/mev_analysis.sh" 2>/dev/null && echo "  ✓ MEV Analysis" || echo "  ⬜ MEV not configured"
source "$SECRETS_DIR/graph_analysis.sh" 2>/dev/null && echo "  ✓ Graph Analysis" || echo "  ⬜ Graph not configured"

# ===== ML & ANALYTICS =====
echo ""
echo "🧠 ML & ANALYTICS:"
source "$SECRETS_DIR/ml_analytics.sh" 2>/dev/null && echo "  ✓ Santiment/IntoTheBlock" || echo "  ⬜ ML analytics not configured"
source "$SECRETS_DIR/ai_infrastructure.sh" 2>/dev/null && echo "  ✓ Pinecone/Cohere" || echo "  ⬜ AI infra not configured"

# ===== THREAT INTEL =====
echo ""
echo "🛡️  THREAT INTEL:"
source "$SECRETS_DIR/threat_intel.sh" 2>/dev/null && echo "  ✓ PhishLabs/VirusTotal" || echo "  ⬜ Threat intel not configured"
source "$SECRETS_DIR/code_analysis.sh" 2>/dev/null && echo "  ✓ Code Analysis" || echo "  ⬜ Code analysis not configured"
source "$SECRETS_DIR/security_audits.sh" 2>/dev/null && echo "  ✓ CertiK/Forta" || echo "  ⬜ Security audits not configured"

# ===== FORENSICS =====
echo ""
echo "🔍 FORENSICS:"
source "$SECRETS_DIR/media_forensics.sh" 2>/dev/null && echo "  ✓ Deepfake/Image Analysis" || echo "  ⬜ Media forensics not configured"
source "$SECRETS_DIR/infra_intel.sh" 2>/dev/null && echo "  ✓ Shodan/Censys" || echo "  ⬜ Infra intel not configured"
source "$SECRETS_DIR/social_osint.sh" 2>/dev/null && echo "  ✓ Social OSINT" || echo "  ⬜ Social OSINT not configured"

# ===== SCAM DETECTION =====
echo ""
echo "🎭 SCAM DETECTION:"
source "$SECRETS_DIR/honeypot_tools.sh" 2>/dev/null && echo "  ✓ Token Sniffer/Honeypot" || echo "  ⬜ Honeypot tools not configured"

# ===== BOT & WORKFLOW =====
echo ""
echo "🤖 BOT & WORKFLOW:"
source "$SECRETS_DIR/telegram_bot.sh" 2>/dev/null && echo "  ✓ Telegram Bot" || echo "  ⬜ Telegram not configured"
source "$SECRETS_DIR/n8n_config.sh" 2>/dev/null && echo "  ✓ n8n" || echo "  ⬜ n8n not configured"
source "$SECRETS_DIR/notification_apis.sh" 2>/dev/null && echo "  ✓ Notifications" || echo "  ⬜ Notifications not configured"
source "$SECRETS_DIR/monitoring_apis.sh" 2>/dev/null && echo "  ✓ Monitoring" || echo "  ⬜ Monitoring not configured"

echo ""
echo "✅ All secrets loaded!"
echo ""

# ===== STATUS SUMMARY =====
echo "📊 CONFIGURATION STATUS:"
echo ""
echo "CRITICAL (Solana Focus):"
[ -n "$HELIUS_API_KEY" ] && echo "  ✅ Helius API" || echo "  ⬜ Helius API (NEED)"
[ -n "$GROQ_API_KEY" ] && echo "  ✅ Groq API" || echo "  ⬜ Groq API (NEED)"
[ -n "$TELEGRAM_BOT_TOKEN" ] && echo "  ✅ Telegram Bot" || echo "  ⬜ Telegram Bot (NEED)"

echo ""
echo "ADVANCED INTEL:"
[ -n "$ARKHAM_API_KEY" ] && echo "  ✅ Arkham Intel" || echo "  ⬜ Arkham (INVITE-ONLY)"
[ -n "$NANSEN_API_KEY" ] && echo "  ✅ Nansen Pro" || echo "  ⬜ Nansen ($150/mo)"
[ -n "$SHODAN_API_KEY" ] && echo "  ✅ Shodan" || echo "  ⬜ Shodan ($59/mo)"
[ -n "$VIRUSTOTAL_API_KEY" ] && echo "  ✅ VirusTotal" || echo "  ⬜ VirusTotal (FREE)"
[ -n "$TINEYE_API_KEY" ] && echo "  ✅ TinEye" || echo "  ⬜ TinEye (PAID)"

echo ""
echo "ML & AI INFRA:"
[ -n "$PINECONE_API_KEY" ] && echo "  ✅ Pinecone" || echo "  ⬜ Pinecone"
[ -n "$COHERE_API_KEY" ] && echo "  ✅ Cohere" || echo "  ⬜ Cohere"
[ -n "$HUGGINGFACE_API_TOKEN" ] && echo "  ✅ HuggingFace" || echo "  ⬜ HuggingFace"

echo ""
echo "SCAM DETECTION:"
[ -n "$TOKENSNIFFER_API_KEY" ] && echo "  ✅ Token Sniffer" || echo "  ⬜ Token Sniffer"
[ -n "$DEXSCREENER_API_ENDPOINT" ] && echo "  ✅ DexScreener" || echo "  ⬜ DexScreener"
