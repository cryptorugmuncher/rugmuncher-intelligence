#!/bin/bash
# 🧹 Cleanup duplicate workflows in n8n
# Keeps only the latest version of each workflow

N8N_HOST="http://167.86.116.51:5678"
API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2MWZmMjVkYi02NTkzLTRlZGEtOGU0OC0wY2Y0YjJmYWVhYjUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiYTlkNWQ2MTMtYmFhZS00ZjkwLWJlMWEtZTAyOTNhM2I3M2RkIiwiaWF0IjoxNzc2MDE1ODMwfQ.xH40uXQ6watIXgdJIh_Nrhw6EtMgcXiqC1oa_g-HnsY"

echo "🧹 Cleaning up duplicate workflows..."
echo ""

# Get all workflows
workflows=$(curl -s "${N8N_HOST}/api/v1/workflows" \
  -H "X-N8N-API-KEY: ${API_KEY}")

# List all workflow names and IDs
echo "📋 Current workflows:"
echo "$workflows" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for w in data.get('data', []):
    print(f\"  - {w['name']} (ID: {w['id']}, Active: {w['active']})\")
" 2>/dev/null || echo "$workflows" | grep -o '"name":"[^"]*"' | sed 's/"name":"/  - /;s/"//'

echo ""
echo "⚠️  To delete duplicates, you need to do this manually in the n8n UI:"
echo "   1. Go to ${N8N_HOST}/workflows"
echo "   2. Click the duplicate workflow"
echo "   3. Click the 3 dots (⋯) menu → Delete"
echo ""
echo "💡 Keep only ONE of each:"
echo "   - Whale Alert System (keep the one with nodes)"
echo "   - Scam Alert System (keep the latest)"
echo ""
