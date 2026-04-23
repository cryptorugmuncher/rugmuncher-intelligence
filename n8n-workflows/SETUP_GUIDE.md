# RMI n8n Setup Guide
## Complete Configuration for Telegram Workflows

### 📋 Prerequisites

1. **n8n running** at http://167.86.116.51:5678
2. **Telegram Bot**: @rugmunchbot (already created)
3. **5 Channels** with bot as admin (already done)

---

## Step 1: Add Telegram Credential

1. Open http://167.86.116.51:5678
2. **Settings** (gear icon) → **Credentials** → **Add Credential**
3. Search: **"Telegram Bot"**
4. Fill in:
   - **Name**: `Rug Munch Bot`
   - **Bot Token**: `8720275246:AAHaQWZlQZybgVyJ50YFl7707AAjEjDFDhU`
5. Click **Save**

---

## Step 2: Import Workflows

Go to **Workflows** → **Add Workflow** → **Import from File**

Import these 10 workflows:

| # | Workflow File | Purpose | Target Channel |
|---|--------------|---------|----------------|
| 1 | `whale-alert.json` | Whale movement alerts | @rmi_alpha_alerts |
| 2 | `scam-alert-workflow-fixed.json` | Scam notifications | @rmi_alpha_alerts |
| 3 | `badge-unlock-workflow-fixed.json` | Badge achievements | @cryptorugmuncher |
| 4 | `rmi_daily_intelligence.json` | Daily reports | @rmi_alerts |
| 5 | `high-risk-alert.json` | Immediate threats | @rmi_alpha_alerts |
| 6 | `rmi_investigation_webhook.json` | Case management | Backend |
| 7 | `rmi_scam_alert_flow.json` | Advanced alerts | @rmi_alpha_alerts |
| 8 | **NEW** `x-to-telegram.json` | X posts → TG | @cryptorugmuncher |
| 9 | **NEW** `scan-results-to-channel.json` | Community scans | @munchscans |
| 10 | **NEW** `backend-health-monitor.json` | System alerts | Backend (private) |

---

## Step 3: Configure Each Workflow

### For Telegram Nodes in Each Workflow:

1. Click the **Telegram node**
2. **Credential**: Select `Rug Munch Bot`
3. **Chat ID**: Enter the appropriate channel ID from below

### Channel ID Reference

| Channel | Chat ID | Usage |
|---------|---------|-------|
| @cryptorugmuncher | `-1002056885429` | Main news, X auto-posts |
| @rmi_alerts | `-1003818352164` | Free intel tier |
| @rmi_alpha_alerts | `-1003762675055` | Paid alpha alerts |
| @munchscans | `-1003924326210` | Community scan results |
| RMI Backend | `-1003991061445` | Admin notifications (private) |

---

## Step 4: Add X (Twitter) Credential (For X→Telegram)

1. Go to https://developer.twitter.com
2. Create app → Get API Key + Secret
3. In n8n: **Settings** → **Credentials** → **Add Credential**
4. Search: **"Twitter"**
5. Enter your API credentials
6. In `x-to-telegram.json` workflow, select this credential

---

## Step 5: Activate Workflows

For each workflow:
1. Open the workflow
2. Toggle **Active** switch (top right) → **ON**
3. Click **Save**

**Priority Order:**
1. Backend Health Monitor (most important)
2. X to Telegram (if using)
3. Scam Alert workflows
4. Whale Alert
5. Others

---

## Webhook URLs

Your backend can trigger these workflows:

| Workflow | Webhook URL |
|----------|-------------|
| Whale Alert | `http://167.86.116.51:5678/webhook/whale-alert` |
| Scam Alert | `http://167.86.116.51:5678/webhook/scam-alert` |
| Scan Result | `http://167.86.116.51:5678/webhook/scan-result` |
| Backend Alert | `http://167.86.116.51:5678/webhook/backend-alert` |
| Investigation | `http://167.86.116.51:5678/webhook/investigation` |

---

## Testing

**Test Telegram Post:**
```bash
curl -X POST "https://api.telegram.org/bot8720275246:AAHaQWZlQZybgVyJ50YFl7707AAjEjDFDhU/sendMessage" \
  -d "chat_id=-1002056885429" \
  -d "text=🧪 Test from n8n setup"
```

**Test Webhook:**
```bash
curl -X POST "http://167.86.116.51:5678/webhook/scan-result" \
  -H "Content-Type: application/json" \
  -d '{
    "contract_address": "0x1234567890abcdef",
    "token_name": "TestToken",
    "risk_score": 7,
    "issues": ["No liquidity locked", "Owner is contract"],
    "username": "testuser"
  }'
```

---

## Single Bot Setup ✅

All workflows use **@rugmunchbot** with these channel mappings:

```
┌─────────────────────┬─────────────────┬──────────────────────┐
│ Workflow            │ Bot             │ Channel              │
├─────────────────────┼─────────────────┼──────────────────────┤
│ Whale Alert         │ @rugmunchbot    │ @rmi_alpha_alerts    │
│ Scam Alert          │ @rugmunchbot    │ @rmi_alpha_alerts    │
│ Badge Unlock        │ @rugmunchbot    │ @cryptorugmuncher    │
│ Daily Intel         │ @rugmunchbot    │ @rmi_alerts          │
│ X → Telegram        │ @rugmunchbot    │ @cryptorugmuncher    │
│ Scan Results        │ @rugmunchbot    │ @munchscans          │
│ Backend Health      │ @rugmunchbot    │ RMI Backend (priv)   │
└─────────────────────┴─────────────────┴──────────────────────┘
```

---

## Files Location

- **Workflows**: `/root/rmi/n8n-workflows/*.json`
- **Secrets**: `/root/rmi/.secrets/telegram_bots.sh`
- **Channel IDs**: `/root/rmi/n8n-workflows/CHANNEL_MAPPING.txt`
- **This Guide**: `/root/rmi/n8n-workflows/SETUP_GUIDE.md`

---

## Next Steps

1. ✅ Delete 3 redundant bots in @BotFather
2. ✅ Add Telegram credential in n8n
3. ✅ Import all 10 workflows
4. ✅ Configure channel IDs
5. ✅ Activate workflows
6. ⬜ Add X API credentials (if using X→TG)
7. ⬜ Test webhooks from backend

Questions? Check the channel mapping file for IDs.
