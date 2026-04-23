#!/usr/bin/env python3
"""
RMI n8n Configuration Script
Sets up Telegram credentials and configures workflows
"""

import json
import os
import sys

# Load secrets
os.environ['RUG_MUNCH_BOT_TOKEN'] = "8720275246:AAHaQWZlQZybgVyJ50YFl7707AAjEjDFDhU"
CHANNELS = {
    "main": "-1002056885429",
    "intel": "-1003818352164",
    "alpha": "-1003762675055",
    "backend": "-1003991061445",
    "scans": "-1003924326210"
}

# Workflow configurations
WORKFLOW_CONFIG = {
    "Whale Alert System": {
        "channel": CHANNELS["alpha"],
        "description": "Posts whale movement alerts to RMI Alpha Intel"
    },
    "Scam Alert System": {
        "channel": CHANNELS["alpha"],
        "description": "Posts high-risk scam alerts to RMI Alpha Intel"
    },
    "Badge Unlock Notifications": {
        "channel": CHANNELS["main"],
        "description": "Posts badge unlocks to main channel"
    },
    "Daily Intelligence Report": {
        "channel": CHANNELS["intel"],
        "description": "Posts daily reports to RMI Intel Alerts"
    },
    "High Risk Alert": {
        "channel": CHANNELS["alpha"],
        "description": "Posts immediate high-risk alerts"
    },
    "RMI Investigation Webhook": {
        "channel": CHANNELS["backend"],
        "description": "Sends system notifications to backend channel"
    },
    "RMI Scam Alert Flow": {
        "channel": CHANNELS["alpha"],
        "description": "Advanced scam alert with multi-channel support"
    }
}

def print_setup_instructions():
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    RMI n8n Configuration Instructions                        ║
╚═══════════════════════════════════════════════════════════════════════════════╝

STEP 1: Add Telegram Credential in n8n UI
─────────────────────────────────────────
1. Open: http://167.86.116.51:5678
2. Click Settings (gear icon) → Credentials → Add Credential
3. Search: "Telegram Bot"
4. Fill in:
   • Name: Rug Munch Bot
   • Bot Token: 8720275246:AAHaQWZlQZybgVyJ50YFl7707AAjEjDFDhU
5. Click Save

STEP 2: Channel ID Reference
────────────────────────────
Use these Chat IDs in your Telegram nodes:

┌─────────────────────────┬──────────────────┬──────────────────────┐
│ Channel                 │ Chat ID          │ Use For              │
├─────────────────────────┼──────────────────┼──────────────────────┤
│ @cryptorugmuncher       │ -1002056885429   │ Main news, X posts   │
│ @rmi_alerts             │ -1003818352164   │ Free intel tier      │
│ @rmi_alpha_alerts       │ -1003762675055   │ Paid alpha alerts    │
│ @munchscans             │ -1003924326210   │ Community scans      │
│ RMI Backend (private)   │ -1003991061445   │ Admin notifications  │
└─────────────────────────┴──────────────────┴──────────────────────┘

STEP 3: Import/Update Workflows
───────────────────────────────
Import these workflows from /root/rmi/n8n-workflows/:
1. Whale Alert System → Set channel to: -1003762675055
2. Scam Alert System → Set channel to: -1003762675055
3. Badge Unlock → Set channel to: -1002056885429
4. Daily Intelligence → Set channel to: -1003818352164
5. High Risk Alert → Set channel to: -1003762675055
6. Investigation Webhook → Set channel to: -1003991061445

STEP 4: New Workflows to Create
───────────────────────────────
1. X → Telegram Auto-Post
   • Trigger: X (Twitter) new tweet
   • Action: Post to @cryptorugmuncher (-1002056885429)

2. Scan Results → Community Channel
   • Trigger: Contract scan completion
   • Action: Post formatted result to @munchscans (-1003924326210)

3. Backend Health Monitor
   • Trigger: System error/webhook failure
   • Action: Post to RMI Backend (-1003991061445)

═══════════════════════════════════════════════════════════════════════════════
""")

    # Save channel mapping for easy reference
    with open('/root/rmi/n8n-workflows/CHANNEL_MAPPING.txt', 'w') as f:
        f.write("RMI Telegram Channel Mapping\n")
        f.write("=" * 50 + "\n\n")
        f.write("Bot: @rugmunchbot\n")
        f.write("Token: 8720275246:AAHaQWZlQZybgVyJ50YFl7707AAjEjDFDhU\n\n")
        f.write("Channels:\n")
        for name, id in CHANNELS.items():
            f.write(f"  {name}: {id}\n")

    print("✓ Channel mapping saved to: /root/rmi/n8n-workflows/CHANNEL_MAPPING.txt")

if __name__ == "__main__":
    print_setup_instructions()
