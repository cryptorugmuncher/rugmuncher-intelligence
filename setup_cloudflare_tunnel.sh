#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# Cloudflare Tunnel Setup — RMI Intelligence Platform
# ═══════════════════════════════════════════════════════════════════════
#
# This script:
# 1. Authenticates with Cloudflare (you'll get a URL to visit)
# 2. Creates a named tunnel "rmi-intelligence"
# 3. Configures DNS routes for all services
# 4. Sets up systemd service for auto-start
#
# Prerequisites: cloudflared installed, Cloudflare account with
#                rugmunch.io (or your domain) added
#
# Run: bash /root/rmi/setup_cloudflare_tunnel.sh
# ═══════════════════════════════════════════════════════════════════════

set -e

TUNNEL_NAME="rmi-intelligence"
DOMAIN="rugmunch.io"
CONFIG_DIR="/root/.cloudflared"
CONFIG_FILE="$CONFIG_DIR/config.yml"

echo "═══════════════════════════════════════════════════════════════"
echo "  RMI Cloudflare Tunnel Setup"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# ─── Step 1: Authenticate ────────────────────────────────────────────
if [ ! -f "$CONFIG_DIR/cert.pem" ]; then
    echo "Step 1: Authenticating with Cloudflare..."
    echo "You'll see a URL. Open it in your browser and select your domain."
    echo ""
    cloudflared tunnel login
    echo ""
    echo "✓ Authentication complete"
else
    echo "✓ Already authenticated with Cloudflare"
fi

# ─── Step 2: Create tunnel ───────────────────────────────────────────
echo ""
echo "Step 2: Creating tunnel '$TUNNEL_NAME'..."

if cloudflared tunnel list | grep -q "$TUNNEL_NAME"; then
    echo "✓ Tunnel '$TUNNEL_NAME' already exists"
    TUNNEL_ID=$(cloudflared tunnel list | grep "$TUNNEL_NAME" | awk '{print $1}')
else
    cloudflared tunnel create "$TUNNEL_NAME"
    TUNNEL_ID=$(cloudflared tunnel list | grep "$TUNNEL_NAME" | awk '{print $1}')
    echo "✓ Tunnel created: $TUNNEL_ID"
fi

echo "  Tunnel ID: $TUNNEL_ID"

# ─── Step 3: Write config ────────────────────────────────────────────
echo ""
echo "Step 3: Writing tunnel configuration..."

mkdir -p "$CONFIG_DIR"

cat > "$CONFIG_FILE" << CONFIG
tunnel: $TUNNEL_ID
credentials-file: $CONFIG_DIR/$TUNNEL_ID.json

# Auto-update and metrics
metrics: 0.0.0.0:45678

# Ingress rules — processed top-to-bottom
ingress:
  # API — Backend FastAPI
  - hostname: api.$DOMAIN
    service: http://rmi_backend:8000
    originRequest:
      connectTimeout: 30s
      noTLSVerify: true

  # Frontend — React Dashboard
  - hostname: app.$DOMAIN
    service: http://localhost:8080
    originRequest:
      connectTimeout: 10s

  # N8N — Workflow Automation
  - hostname: n8n.$DOMAIN
    service: http://rmi_n8n:5678
    originRequest:
      connectTimeout: 10s

  # Helius Webhook — On-chain events
  - hostname: helius.$DOMAIN
    service: http://rmi_backend:8000
    path: /webhook/helius
    originRequest:
      connectTimeout: 30s

  # Telegram Webhook — Bot updates
  - hostname: bot.$DOMAIN
    service: http://rmi-telegram-bot:8080
    path: /webhook/telegram
    originRequest:
      connectTimeout: 10s

  # Status — Health check
  - hostname: status.$DOMAIN
    service: http://rmi_backend:8000
    path: /health
    originRequest:
      connectTimeout: 5s

  # WebSocket — Real-time data
  - hostname: ws.$DOMAIN
    service: http://rmi_backend:8000
    originRequest:
      connectTimeout: 30s
      noTLSVerify: true

  # Fallback
  - service: http_status:404
CONFIG

echo "✓ Config written to $CONFIG_FILE"

# ─── Step 4: Route DNS ───────────────────────────────────────────────
echo ""
echo "Step 4: Creating DNS routes..."

for subdomain in api app n8n helius bot status ws; do
    HOSTNAME="$subdomain.$DOMAIN"
    if cloudflared tunnel route dns "$TUNNEL_NAME" "$HOSTNAME" 2>/dev/null; then
        echo "  ✓ $HOSTNAME → tunnel"
    else
        echo "  ⚠ $HOSTNAME may already exist or failed"
    fi
done

# ─── Step 5: Install systemd service ─────────────────────────────────
echo ""
echo "Step 5: Installing systemd service..."

cloudflared service install 2>/dev/null || true

# Create override to use our config
mkdir -p /etc/systemd/system/cloudflared.service.d/
cat > /etc/systemd/system/cloudflared.service.d/override.conf << SERVICE
[Service]
ExecStart=
ExecStart=/usr/local/bin/cloudflared tunnel --config $CONFIG_FILE run $TUNNEL_ID
SERVICE

systemctl daemon-reload
systemctl enable cloudflared
systemctl restart cloudflared

echo "✓ Systemd service installed and started"

# ─── Step 6: Verify ──────────────────────────────────────────────────
echo ""
echo "Step 6: Verifying tunnel status..."
sleep 3
cloudflared tunnel info "$TUNNEL_NAME" 2>/dev/null || echo "Run 'cloudflared tunnel info $TUNNEL_NAME' to check"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ Cloudflare Tunnel Setup Complete"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  Tunnel:     $TUNNEL_NAME ($TUNNEL_ID)"
echo "  Domain:     $DOMAIN"
echo ""
echo "  Routes:"
echo "    https://api.$DOMAIN      → Backend API"
echo "    https://app.$DOMAIN      → Frontend Dashboard"
echo "    https://n8n.$DOMAIN      → n8n Workflows"
echo "    https://helius.$DOMAIN   → Helius Webhooks"
echo "    https://bot.$DOMAIN      → Telegram Webhook"
echo "    https://status.$DOMAIN   → Health Check"
echo "    https://ws.$DOMAIN       → WebSocket"
echo ""
echo "  Service:    systemctl status cloudflared"
echo "  Logs:       journalctl -u cloudflared -f"
echo "  Config:     $CONFIG_FILE"
echo ""
