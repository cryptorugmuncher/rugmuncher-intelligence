#!/bin/bash
# 🔧 RMI n8n Workflow Bulk Import
# Imports all 7 workflows automatically via API
# Usage: bash bulk-import.sh <your-n8n-api-key>

set -e

N8N_HOST="http://167.86.116.51:5678"
WORKFLOWS_DIR="/root/rmi/n8n-workflows"
API_KEY="${1:-}"

echo "═══════════════════════════════════════════════════════════"
echo "  🐲 RMI n8n Workflow Bulk Import"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check if API key provided
if [ -z "$API_KEY" ]; then
    echo "❌ N8N_API_KEY required"
    echo ""
    echo "Get your API key:"
    echo "  1. Open http://167.86.116.51:5678"
    echo "  2. Click your profile (top right)"
    echo "  3. Settings → API → Create API Key"
    echo "  4. Copy the key and run:"
    echo ""
    echo "  bash bulk-import.sh n8n_api_xxxxxxxx"
    echo ""
    exit 1
fi

# Check n8n is running
echo "🔍 Checking n8n..."
if ! curl -s "${N8N_HOST}/healthz" > /dev/null 2>&1; then
    echo "❌ n8n is not running at ${N8N_HOST}"
    exit 1
fi
echo "✅ n8n is running"
echo ""

# List workflows to import
WORKFLOWS=(
    "rmi_investigation_webhook.json:Investigation Webhook Handler"
    "rmi_scam_alert_flow.json:RMI Scam Alert Flow"
    "rmi_daily_intelligence.json:Daily Intelligence Report"
    "scam-alert-workflow-fixed.json:Scam Alert System"
    "badge-unlock-workflow-fixed.json:Badge Unlock Notifications"
    "high-risk-alert.json:High Risk Alert"
    "whale-alert.json:Whale Alert"
)

echo "📦 Importing ${#WORKFLOWS[@]} workflows..."
echo ""

IMPORTED=0
FAILED=0

for item in "${WORKFLOWS[@]}"; do
    IFS=':' read -r file name <<< "$item"
    filepath="${WORKFLOWS_DIR}/${file}"

    if [ ! -f "$filepath" ]; then
        echo "⚠️  Skipping $name - file not found"
        ((FAILED++))
        continue
    fi

    echo "⬆️  Importing: $name"

    response=$(curl -s -w "\n%{http_code}" -X POST "${N8N_HOST}/api/v1/workflows" \
        -H "Content-Type: application/json" \
        -H "X-N8N-API-KEY: ${API_KEY}" \
        -d "@${filepath}" 2>/dev/null)

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ]; then
        echo "   ✅ Imported successfully"
        ((IMPORTED++))
    elif echo "$body" | grep -q "already exists"; then
        echo "   ⚠️  Already exists (skipping)"
        ((IMPORTED++))
    else
        echo "   ❌ Failed (HTTP $http_code)"
        ((FAILED++))
    fi
done

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  📊 Import Summary"
echo "═══════════════════════════════════════════════════════════"
echo "  ✅ Imported: $IMPORTED"
echo "  ❌ Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 All workflows imported!"
    echo ""
    echo "Next steps:"
    echo "  1. Go to ${N8N_HOST}/workflows"
    echo "  2. Activate each workflow (toggle switch)"
    echo "  3. Configure credentials in Settings → Credentials"
else
    echo "⚠️  Some workflows failed. Check errors above."
fi

echo ""
