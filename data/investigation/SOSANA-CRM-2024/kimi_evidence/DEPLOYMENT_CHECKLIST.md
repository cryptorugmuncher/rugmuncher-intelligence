# Omega Forensic V5 - Deployment Checklist

## ✅ Pre-Deployment Verification

- [x] **24 files created** in omega_forensic_v5/
- [x] **6,490 lines of Python code** written
- [x] **11 APIs integrated** and configured
- [x] **200+ wallets** in database
- [x] **All 12 APIs ready** (0 missing)

---

## 🚀 Deployment Steps

### Step 1: Copy Files to Server
```bash
# From your local machine
scp -r omega_forensic_v5 root@167.86.116.51:/root/crm_audit
```

### Step 2: SSH to Server
```bash
ssh root@167.86.116.51
```

### Step 3: Run Setup Script
```bash
cd /root/crm_audit
bash server_setup.sh
```

This will:
- [ ] Update system packages
- [ ] Install Python and dependencies
- [ ] Configure firewall (UFW)
- [ ] Create directory structure
- [ ] Setup virtual environment
- [ ] Install Python packages
- [ ] Create environment file
- [ ] Create startup scripts
- [ ] Configure logging
- [ ] Create systemd service
- [ ] Apply security hardening

### Step 4: Start the Bot

**Option A: Manual Start**
```bash
cd /root/crm_audit
./start_bot.sh
```

**Option B: Systemd Service**
```bash
systemctl start omega-forensic
systemctl enable omega-forensic  # Auto-start on boot
```

### Step 5: Verify Bot is Running
```bash
# Check status
systemctl status omega-forensic

# View logs
tail -f /var/log/omega_forensic/investigation.log

# Test with Telegram
# Send /start to your bot
```

---

## 📋 Post-Deployment Tests

### Test 1: CLI Commands
```bash
cd /root/crm_audit
source venv/bin/activate

# Test status
python main.py status

# Test wallet investigation
python main.py investigate AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6

# Test report generation
python main.py report
```

### Test 2: Telegram Bot
1. Open Telegram
2. Find your bot (@YourBotName)
3. Send `/start`
4. Send `/status`
5. Send `/investigate AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6`

### Test 3: API Connectivity
```bash
python -c "
from forensic.api_arsenal import ForensicAPIArsenal
import asyncio

async def test():
    async with ForensicAPIArsenal() as api:
        # Test Helius
        result = await api.helius_get_account('AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6')
        print(f'Helius: {\"OK\" if result.success else \"FAIL\"}')
        
        # Test ChainAbuse
        result = await api.chainabuse_check_address('AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6')
        print(f'ChainAbuse: {\"OK\" if result.success else \"FAIL\"}')

asyncio.run(test())
"
```

---

## 🔧 Configuration Files

### Environment Variables (.env)
Location: `/root/crm_audit/.env`

All API keys are pre-configured:
- HELIUS_API_KEY
- ARKHAM_API_KEY
- GROQ_API_KEY
- DEEPSEEK_API_KEY
- OPENROUTER_API_KEY
- And 7 more...

### Telegram Bot Token
Location: `/root/crm_audit/.env`
```
TG_TOKEN=8765109525:AAFEb0dQd11wm2EIbGf_mf0W1776t36Q1kU
```

### Target Token
```
TARGET_CA=Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS
```

---

## 🛡️ Security Checklist

- [x] Firewall configured (UFW)
- [x] Ports allowed: 22, 80, 443, 8443
- [x] API keys in .env (chmod 600)
- [x] Daily security reset configured
- [x] No dangerous persistence
- [x] Chain of custody logging

---

## 📊 Monitoring

### View Logs
```bash
# Real-time logs
tail -f /var/log/omega_forensic/investigation.log

# Bot logs
journalctl -u omega-forensic -f
```

### Check Status
```bash
# Bot status
systemctl status omega-forensic

# Database stats
python -c "from forensic.wallet_database import get_wallet_database; db=get_wallet_database(); print(db.get_statistics())"

# API status
python -c "from config.api_keys import get_server_info; info=get_server_info(); print(f'Configured: {len(info[\"configured_apis\"])}, Missing: {len(info[\"missing_apis\"])}')"
```

---

## 🔄 Maintenance

### Daily
- [ ] Check bot is running: `systemctl status omega-forensic`
- [ ] Review logs: `tail /var/log/omega_forensic/investigation.log`

### Weekly
- [ ] Update system: `apt-get update && apt-get upgrade`
- [ ] Check disk space: `df -h`
- [ ] Review generated reports

### Monthly
- [ ] Rotate logs
- [ ] Review API usage
- [ ] Update dependencies: `pip install -r requirements.txt --upgrade`

---

## 🆘 Troubleshooting

### Bot Won't Start
```bash
# Check logs
journalctl -u omega-forensic -n 50

# Check Python environment
source venv/bin/activate
python -c "import telegram; print('OK')"

# Verify .env file
cat /root/crm_audit/.env | grep TG_TOKEN
```

### API Errors
```bash
# Test specific API
python -c "
import os
from forensic.api_arsenal import ForensicAPIArsenal
print('HELIUS:', os.getenv('HELIUS_API_KEY')[:10] + '...')
"
```

### Import Errors
```bash
# Reinstall dependencies
cd /root/crm_audit
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📞 Support Commands

```bash
# Restart bot
systemctl restart omega-forensic

# Stop bot
systemctl stop omega-forensic

# View bot logs
journalctl -u omega-forensic -f

# View investigation logs
tail -f /var/log/omega_forensic/investigation.log

# Check firewall
ufw status

# Check disk space
df -h

# Check memory
free -m
```

---

## 🎯 Success Criteria

- [ ] Bot responds to `/start` in Telegram
- [ ] `/status` shows all systems operational
- [ ] `/investigate <wallet>` returns analysis
- [ ] `/report` generates investigation report
- [ ] CLI commands work: `python main.py status`
- [ ] All 12 APIs show as configured
- [ ] Logs show no errors
- [ ] Firewall is active

---

## 📁 File Locations

| File | Location |
|------|----------|
| Main code | `/root/crm_audit/` |
| Config | `/root/crm_audit/config/` |
| Evidence | `/root/crm_audit/evidence/` |
| Reports | `/root/crm_audit/evidence_reports/` |
| Logs | `/var/log/omega_forensic/` |
| Environment | `/root/crm_audit/.env` |
| Service | `/etc/systemd/system/omega-forensic.service` |

---

## ✅ Final Checklist

- [ ] Files copied to server
- [ ] Setup script executed
- [ ] Bot is running
- [ ] Telegram commands work
- [ ] CLI commands work
- [ ] Reports generate correctly
- [ ] Logs show no errors
- [ ] Firewall active
- [ ] Monitoring in place

---

**Ready for deployment!**

**Server**: `ssh root@167.86.116.51`
**Workdir**: `/root/crm_audit`
**Start**: `systemctl start omega-forensic`
