#!/bin/bash
# 🔄 n8n Workflow Automation
# File permissions: 600 (owner only)

# Server IP for external access
SERVER_IP="167.86.116.51"

# n8n Webhook Base URL (External Access)
export N8N_WEBHOOK_URL="http://${SERVER_IP}:5678/webhook/"

# n8n API Key (generated in n8n UI after first start)
# Get from: n8n → Settings → API → Create API Key
export N8N_API_KEY=""

# n8n Base URL (for admin operations)
export N8N_BASE_URL="http://${SERVER_IP}:5678"

# Basic Auth credentials (default: admin / RugMuncher2024)
export N8N_USERNAME="admin"
export N8N_PASSWORD="RugMuncher2024"
