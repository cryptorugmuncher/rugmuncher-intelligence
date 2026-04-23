# n8n Detection Alert Workflows - Setup Guide

## Overview
These workflows route detection alerts from the RMI backend to Telegram channels based on severity and tier.

## Workflows Created

### 1. `detection-emergency-alert.json`
**Triggers:** `POST http://localhost:5678/webhook/detection-emergency`

**Actions:**
- Sends to @rmi_alpha_alerts (paid tier)
- Sends to @rugmunchbot_admin (admin channel)
- Auto-blacklists honeypots
- Logs to Supabase

**For:** EMERGENCY severity alerts (honeypots, god mode, timebombs)

### 2. `detection-critical-alert.json`
**Triggers:** `POST http://localhost:5678/webhook/detection-critical`

**Actions:**
- Routes by tier to appropriate channels
- Beginner → @rmi_alerts_bot (free)
- Intermediate → @munchscans_bot (whale)
- Advanced → @alpha_scanner_bot (deep scan)
- Always sends to @rmi_alpha_alerts (paid)
- Logs to Supabase

**For:** CRITICAL severity alerts

## Setup Instructions

### Step 1: Start n8n
```bash
cd /root/rmi/n8n-workflows
docker-compose up -d n8n
# or
n8n start
```

### Step 2: Import Workflows
1. Open n8n at `http://localhost:5678`
2. Click "Add Workflow"
3. Select "Import from File"
4. Import `detection-emergency-alert.json`
5. Import `detection-critical-alert.json`
6. Activate both workflows

### Step 3: Configure Telegram Bots
1. Get bot tokens from @BotFather
2. In n8n, open Telegram nodes
3. Add credentials for each bot:
   - @rmi_alpha_alerts_bot
   - @rmi_alerts_bot
   - @munchscans_bot
   - @alpha_scanner_bot

### Step 4: Configure Supabase
1. In n8n, open Supabase nodes
2. Add Supabase credentials
3. Set project URL and service key

### Step 5: Test
```bash
# Test emergency alert
curl -X POST http://localhost:8002/api/v1/detection/alert/n8n/test

# Send test alert
curl -X POST http://localhost:8002/api/v1/detection/alert/n8n/send \
  -H "Content-Type: application/json" \
  -d '{
    "type": "TEST_ALERT",
    "severity": "emergency",
    "tier": "beginner",
    "title": "Test Emergency Alert",
    "description": "This is a test of the n8n integration",
    "token_mint": "TestToken1111111111111111111111111111111",
    "recommendation": "TEST: Ignore this message"
  }'
```

## Routing Logic

| Severity | Tier | Telegram Channels |
|----------|------|-------------------|
| EMERGENCY | Any | @rmi_alpha_alerts + @rugmunchbot_admin |
| CRITICAL | Beginner | @rmi_alpha_alerts + @rmi_alerts_bot |
| CRITICAL | Intermediate | @rmi_alpha_alerts + @munchscans_bot |
| CRITICAL | Advanced | @rmi_alpha_alerts + @alpha_scanner_bot |
| WARNING | Beginner | @rmi_alerts_bot |
| WARNING | Intermediate | @munchscans_bot |
| WARNING | Advanced | @alpha_scanner_bot |
| INFO | Any | Dashboard only |

## Backend → n8n Flow

```
Helius Webhook
     ↓
RMI Backend Detection
     ↓
Critical Alert Found
     ↓
POST to n8n Webhook
     ↓
n8n Routes by Severity/Tier
     ↓
Telegram Channels Notified
```

## API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /api/v1/detection/webhook/helius` | Receive Helius webhooks |
| `POST /api/v1/detection/scan/{token}` | Scan token, auto-send critical alerts |
| `POST /api/v1/detection/alert/n8n/test` | Test n8n connection |
| `POST /api/v1/detection/alert/n8n/send` | Manually send alert |
| `POST /api/v1/detection/auto-blacklist` | Blacklist honeypot tokens |

## Monitoring

Check alert delivery:
```bash
# View recent alerts
GET /api/v1/detection/alerts/recent?severity=emergency

# View detection stats
GET /api/v1/detection/stats
```

## Troubleshooting

### n8n webhook not receiving
- Check n8n is running: `docker ps | grep n8n`
- Verify webhook URL in backend matches n8n
- Test with manual curl to n8n directly

### Telegram messages not sending
- Check bot tokens are valid
- Verify bots are admin in channels
- Check bot hasn't hit rate limits

### Database not updating
- Verify Supabase credentials in n8n
- Check table permissions
- Review n8n execution logs
