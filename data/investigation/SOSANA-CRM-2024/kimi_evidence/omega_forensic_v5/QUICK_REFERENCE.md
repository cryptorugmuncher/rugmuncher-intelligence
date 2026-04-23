# Omega Forensic V5 - Quick Reference

## 🚀 Quick Commands

```bash
# Start Telegram bot
python main.py bot

# Investigate a wallet (3 layers deep)
python main.py investigate AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6

# Generate full investigation report
python main.py report

# Deep scan multiple wallets
python main.py scan wallet1 wallet2 wallet3 --layers 3

# Hunt KYC vectors
python main.py kyc CNSob1LwXvDRmjioxyjm78tDb2S7nzFK6K8t3VmuhKpn

# Check system status
python main.py status
```

## 📱 Telegram Commands

| Command | Usage | Description |
|---------|-------|-------------|
| `/start` | `/start` | Welcome & menu |
| `/help` | `/help` | Command list |
| `/investigate` | `/investigate <wallet> [depth]` | Deep analysis |
| `/wallet` | `/wallet <wallet>` | Quick lookup |
| `/kyc` | `/kyc <wallet>` | KYC vector hunt |
| `/crossproject` | `/crossproject [p1] [p2]` | Cross-project analysis |
| `/report` | `/report` | Generate report |
| `/status` | `/status` | Bot status |
| `/leads` | `/leads` | New leads |

## 🔑 Critical Wallets (Always Use Full Address)

```
AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6  # Botnet Commander (970 wallets)
CNSob1LwXvDRmjioxyjm78tDb2S7nzFK6K8t3VmuhKpn  # Root Funder (MoonPay KYC)
HLnpSz9h2S4hiLQ4uN3vGYAHJqDmbFCwkx9prSXkdPMc  # Master Feeder (81M CRM, DELETED)
8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj  # CRM/PBTC Nexus (SMOKING GUN)
F4HGHWyaCvDkUF88svvCHhSMpR9YzHCYSNmojaKQtRSB  # SOSANA Treasury
ASTyfSima4LLAdDgoFGkgqoKowG1LZFDr9fAQrg7iaJZ  # Nuclear Treasury (33K SOL)
```

## 🎯 Human Suspects

| Name | Role | Wallets | Confidence |
|------|------|---------|------------|
| Mark Ross | Project Creator | MarkRoss001XyZ... | Medium |
| Brian Lyles | Developer | BrianLyle002XyZ... | Medium |
| Tracy Silver | Marketing | TracySilv003XyZ... | Low |
| David Track | Liquidity | DavidTrac004XyZ... | Low |

## 📡 API Status Check

```bash
python -c "from config.api_keys import get_server_info; import json; info=get_server_info(); print(json.dumps(info, indent=2))"
```

## 🔥 Server Setup

```bash
# SSH to server
ssh root@167.86.116.51

# Run setup
cd /root/crm_audit
bash server_setup.sh

# Start bot
./start_bot.sh

# Or use systemd
systemctl start omega-forensic
systemctl enable omega-forensic  # Auto-start
```

## 📊 Evidence Tiers

- **Tier 1 (Direct)**: On-chain proof, verified connections
- **Tier 2 (Strong)**: Strong circumstantial evidence
- **Tier 3 (Circumstantial)**: Supporting evidence
- **Tier 4 (Suspicious)**: Requires verification
- **Tier 5 (Unverified)**: Investigation leads

## 🕵️ Investigator Bot Personality

The Investigator is:
- **Matter-of-fact**: Direct, no fluff
- **Thorough**: Digs multiple layers deep
- **Relentless**: Always finds the answer
- **Self-healing**: Learns from mistakes
- **Self-learning**: Improves continuously
- **Security-first**: Daily reset, no dangerous persistence

## 💰 Cost Optimization

| Task | Model | Cost |
|------|-------|------|
| Quick replies | Groq Llama | Cheap |
| Deep analysis | DeepSeek Reasoner | Cheap |
| Code generation | DeepSeek Chat | Cheap |
| General chat | OpenRouter (free) | Free |

## 📁 File Ingestion

Drop files in `evidence/` directory:
- `evidence/telegram/` - Telegram exports (HTML)
- `evidence/transactions/` - Transaction data (CSV, JSON)
- `evidence/chats/` - Chat logs (TXT)
- `evidence/json/` - JSON exports
- `evidence/raw/` - Raw files

## 🔍 Python API Usage

```python
from bots.investigator_bot import investigate, find_kyc
from forensic.report_generator import generate_final_report
from forensic.deep_scanner import deep_scan

# Investigate wallet
result = investigate("AFXigaYu...", depth=3)

# Hunt KYC
kyc_result = find_kyc("CNSob1Lw...")

# Generate report
report = generate_final_report()

# Deep scan
analysis = deep_scan("8eVZa7b...", layers=3)
```

## 🛡️ Security

- Firewall: UFW configured (ports 22, 80, 443, 8443)
- Daily reset: No dangerous persistence
- API keys: Stored in `.env` (chmod 600)
- Chain of custody: Immutable audit logging

## 📈 Monitoring

```bash
# View logs
tail -f /var/log/omega_forensic/investigation.log

# Check bot status
systemctl status omega-forensic

# View database stats
python -c "from forensic.wallet_database import get_wallet_database; db=get_wallet_database(); print(db.get_statistics())"
```

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Bot won't start | Check `TG_TOKEN` in `.env` |
| API errors | Verify API keys in `config/api_keys.py` |
| Import errors | Run `pip install -r requirements.txt` |
| Permission denied | `chmod +x server_setup.sh` |

## 📞 Support

For investigation coordination and evidence submission.

---

**Omega Forensic V5** - *The truth is in the chain.*
