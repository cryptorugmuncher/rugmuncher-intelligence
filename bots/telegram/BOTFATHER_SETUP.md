# 🤖 BotFather Setup Guide - RMI Telegram Bots

## Open Telegram and Message @BotFather

Search for **@BotFather** in Telegram and click **START**

---

## Bot 1: Rug Munch Bot (Contract/Analysis)

### Step 1: Create the Bot
```
/newbot
```

BotFather asks for a name:
```
Rug Munch Bot
```

BotFather asks for a username (must end in 'bot'):
```
rugmunch_analysis_bot
```

✅ **Success!** BotFather gives you a token like:
```
123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
```

### Step 2: Set Description
```
/setdescription
```
Select your bot from the list, then type:
```
🔍 RMI Contract Analysis Bot

Analyzes crypto contracts for scams, honeypots, and red flags.

Commands:
/analyze <contract> - Analyze token contract
/scan <address> - Scan wallet address
/report <token> - Report suspicious token
```

### Step 3: Set About Text
```
/setabouttext
```
```
Official RMI Rug Muncher analysis bot. Protecting degen investments since 2024.
```

### Step 4: Set Bot Commands
```
/setcommands
```
```
analyze - Analyze a token contract (e.g. /analyze 0x123...)
scan - Scan wallet for risk (e.g. /scan wallet_address)
report - Report scam token
help - Show help message
```

---

## Bot 2: RMI Backend Bot

### Step 1: Create
```
/newbot
```

Name:
```
RMI Backend Bot
```

Username:
```
rmi_backend_bot
```

✅ **Save the token!**

### Step 2: Description
```
/setdescription
```
```
🔧 RMI Backend System Bot

Internal notifications for investigation updates, case alerts, and system status.

Admin use only.
```

---

## Bot 3: Crypto Intelligence (Alerts/Alpha)

### Step 1: Create
```
/newbot
```

Name:
```
Crypto Intelligence
```

Username:
```
rmi_intelligence_bot
```

✅ **Save the token!**

### Step 2: Description
```
/setdescription
```
```
🚨 RMI Crypto Intelligence

Real-time alerts for:
🐋 Whale movements
🚨 Scams & exploits
⚠️ High-risk tokens
📊 Market alpha

Join @RMI_Intel_Channel
```

---

## Get Your Chat ID (For Channel)

### Option 1: Via Bot
1. Create a channel in Telegram
2. Add your bot as **Administrator**
3. Send a test message in the channel
4. Visit this URL in browser:
```
https://api.telegram.org/bot[YOUR_BOT_TOKEN]/getUpdates
```

Look for:
```json
"chat":{"id":-1001234567890,
```

The `-1001234567890` is your **Channel ID**

### Option 2: Via @userinfobot
1. Message **@userinfobot**
2. Forward a message from your channel
3. It will show the channel ID

---

## Commands Quick Reference

| Command | Purpose |
|---------|---------|
| `/newbot` | Create new bot |
| `/token` | Get bot token (if lost) |
| `/revoke` | Revoke old token, get new one |
| `/setname` | Change bot name |
| `/setdescription` | Set long description |
| `/setabouttext` | Set short about text |
| `/setcommands` | Set command list |
| `/setuserpic` | Set bot avatar |
| `/deletebot` | Delete bot |

---

## What to Send Me Next

After creating all 3 bots, send me:

```
Bot 1 (Rug Munch): 123456789:ABC...
Bot 2 (Backend):   987654321:DEF...
Bot 3 (Intel):     456789123:GHI...

Channel ID: -1001234567890
```

Then I'll configure all the workflows!
