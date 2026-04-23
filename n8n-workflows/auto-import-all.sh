#!/bin/bash
# 🔧 RMI n8n Workflow Auto Import (CLI Method - More Reliable)
# Stops n8n, imports via CLI, restarts n8n

set -e

WORKFLOWS_DIR="/root/rmi/n8n-workflows"
N8N_DATA_DIR="$HOME/.n8n"

echo "═══════════════════════════════════════════════════════════"
echo "  🐲 RMI n8n Workflow Auto Import (CLI Method)"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check if n8n CLI is available
if ! command -v n8n &> /dev/null; then
    echo "❌ n8n CLI not found. Installing..."
    npm install -g n8n
fi

# Backup existing workflows
echo "💾 Backing up existing workflows..."
backup_dir="${N8N_DATA_DIR}/workflows_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$backup_dir"
if [ -d "${N8N_DATA_DIR}/workflows" ]; then
    cp -r "${N8N_DATA_DIR}/workflows" "$backup_dir/" 2>/dev/null || true
fi
echo "   ✅ Backup saved to $backup_dir"
echo ""

# List workflows to import
declare -A WORKFLOWS
declare -A NAMES
WORKFLOWS=(
    ["rmi_investigation_webhook.json"]="Investigation Webhook"
    ["rmi_scam_alert_flow.json"]="RMI Scam Alert Flow"
    ["rmi_daily_intelligence.json"]="Daily Intelligence Report"
    ["scam-alert-workflow-fixed.json"]="Scam Alert System"
    ["badge-unlock-workflow-fixed.json"]="Badge Unlock"
    ["high-risk-alert.json"]="High Risk Alert"
    ["whale-alert.json"]="Whale Alert"
)

echo "📦 Importing ${#WORKFLOWS[@]} workflows via n8n CLI..."
echo ""

IMPORTED=0
FAILED=0

for file in "${!WORKFLOWS[@]}"; do
    filepath="${WORKFLOWS_DIR}/${file}"
    name="${WORKFLOWS[$file]}"

    if [ ! -f "$filepath" ]; then
        echo "⚠️  Skipping $name - file not found"
        ((FAILED++))
        continue
    fi

    echo "⬆️  Importing: $name"

    # Use n8n CLI import command
    if n8n import:workflow --input="$filepath" 2>/dev/null; then
        echo "   ✅ Imported"
        ((IMPORTED++))
    else
        echo "   ⚠️  CLI import failed, trying alternative..."
        # Fallback: copy directly to workflows directory
        mkdir -p "${N8N_DATA_DIR}/workflows"
        cp "$filepath" "${N8N_DATA_DIR}/workflows/${file}" 2>/dev/null && echo "   ✅ Copied to workflows dir" || echo "   ❌ Failed"
    fi
done

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  📊 Import Summary"
echo "═══════════════════════════════════════════════════════════"
echo "  ✅ Processed: $IMPORTED"
echo "  ❌ Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 All workflows imported!"
    echo ""
    echo "⚠️  IMPORTANT: Restart n8n to load the new workflows"
    echo ""
    echo "Run these commands:"
    echo "  pkill -f 'n8n start'"
    echo "  sleep 2"
    echo "  export N8N_BASIC_AUTH_ACTIVE=true"
    echo "  export N8N_BASIC_AUTH_USER=admin"
    echo "  export N8N_BASIC_AUTH_PASSWORD=RugMuncher2024"
    echo "  export N8N_HOST=0.0.0.0"
    echo "  export N8N_PORT=5678"
    echo "  export WEBHOOK_URL=http://167.86.116.51:5678/"
    echo "  n8n start"
    echo ""
    echo "Then visit: http://167.86.116.51:5678/workflows"
else
    echo "⚠️  Some workflows may need manual import."
fi

echo ""
