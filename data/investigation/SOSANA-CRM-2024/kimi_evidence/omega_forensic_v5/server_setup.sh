#!/bin/bash
# Omega Forensic V5 - Server Setup Script
# ========================================
# Sets up Contabo VPS for forensic investigation
# Firewall, dependencies, directory structure

set -e  # Exit on error

echo "=========================================="
echo "OMEGA FORENSIC V5 - SERVER SETUP"
echo "=========================================="
echo ""

# Configuration
SERVER_IP="167.86.116.51"
SERVER_USER="root"
WORKDIR="/root/crm_audit"

echo "📋 Configuration:"
echo "  Server: $SERVER_USER@$SERVER_IP"
echo "  Workdir: $WORKDIR"
echo ""

# ============================================
# STEP 1: UPDATE SYSTEM
# ============================================
echo "🔄 Step 1: Updating system packages..."
apt-get update -y
apt-get upgrade -y
echo "  ✓ System updated"
echo ""

# ============================================
# STEP 2: INSTALL DEPENDENCIES
# ============================================
echo "📦 Step 2: Installing dependencies..."

# Python and pip
apt-get install -y python3 python3-pip python3-venv

# System utilities
apt-get install -y curl wget git unzip

# Firewall
apt-get install -y ufw

# Database (SQLite is built-in, but install tools)
apt-get install -y sqlite3

echo "  ✓ Dependencies installed"
echo ""

# ============================================
# STEP 3: SETUP FIREWALL
# ============================================
echo "🔥 Step 3: Configuring firewall..."

# Reset UFW
ufw --force reset

# Default policies
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (critical!)
ufw allow 22/tcp

# Allow HTTP/HTTPS (for web interface if needed)
ufw allow 80/tcp
ufw allow 443/tcp

# Allow Telegram webhook (if using webhooks)
ufw allow 8443/tcp

# Enable firewall
ufw --force enable

echo "  ✓ Firewall configured"
echo "  Allowed ports: 22 (SSH), 80 (HTTP), 443 (HTTPS), 8443 (Telegram)"
echo ""

# ============================================
# STEP 4: CREATE DIRECTORY STRUCTURE
# ============================================
echo "📁 Step 4: Creating directory structure..."

mkdir -p $WORKDIR
cd $WORKDIR

# Create subdirectories
mkdir -p {config,core,forensic,bots,telegram,utils,data,evidence_reports,github_intel,evidence}
mkdir -p evidence/{telegram,transactions,chats,json,raw,processed}
mkdir -p logs

echo "  ✓ Directories created"
echo ""

# ============================================
# STEP 5: SETUP PYTHON VIRTUAL ENVIRONMENT
# ============================================
echo "🐍 Step 5: Setting up Python virtual environment..."

python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip

# Core dependencies
pip install requests aiohttp

# Data processing
pip install pandas numpy

# Telegram bot
pip install python-telegram-bot

# Utilities
pip install python-dotenv

echo "  ✓ Python environment ready"
echo ""

# ============================================
# STEP 6: CREATE ENVIRONMENT FILE
# ============================================
echo "🔑 Step 6: Creating environment file..."

cat > $WORKDIR/.env << 'EOF'
# Omega Forensic V5 - API Keys
# =============================

# Division 1: Identity & AML
ARKHAM_API_KEY=bbbebc4f-0727-4157-87cc-42f8991a58ca
MISTTRACK_API_KEY=ynX083xAuSk4WKEsaHpOFw5DYd91ZlmI
CHAINABUSE_API_KEY=ca_VDBVeWVTT3F5TGRPeFVyb1Y4cVhWNnpFLktJYVNHZUVXa0QvZmIxNXVuektaNUE9PQ

# Division 2: On-Chain Autopsy
HELIUS_API_KEY=771413f9-60c9-4714-94d6-33851d1e6d88
QUICKNODE_SOL_RPC=https://wandering-rough-butterfly.solana-mainnet.quiknode.pro/875fa003546494c35631050925b5e966baa4b81d/
SOLSCAN_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3NDM3Mjk5NzY0MjUsImVtYWlsIjoiamF5dHJhbmNlQGdtYWlsLmNvbSIsImFjdGlvbiI6InRva2VuLWFwaSIsImFwaVZlcnNpb24iOjIsImlhdCI6MTc0MzcyOTk3Nn0.4MpOu1mE24T6XqQJ7zJ-0iLrPE6jQpbjxw33RwAiVOE

# Division 3: Token Mechanics
BIRDEYE_API_KEY=58c5b02e9e484c73b02691687379673a
LUNARCRUSH_API_KEY=mu5cf8zde098q1hti2t8tmfrsgmnh3ifzxpad14y9

# Division 4: Real World OSINT
SERPER_API_KEY=faee04c161280c9e83ed2fed949d175b4fbb3222

# AI/LLM APIs
GROQ_API_KEY=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
DEEPSEEK_API_KEY=sk-a86c88e9f6224ffba9d866f032225eb6
OPENROUTER_API_KEY=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

# Telegram
TG_TOKEN=8765109525:AAFEb0dQd11wm2EIbGf_mf0W1776t36Q1kU

# Target
TARGET_CA=Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS
EOF

chmod 600 $WORKDIR/.env

echo "  ✓ Environment file created"
echo ""

# ============================================
# STEP 7: CREATE STARTUP SCRIPTS
# ============================================
echo "🚀 Step 7: Creating startup scripts..."

# Main bot startup script
cat > $WORKDIR/start_bot.sh << 'EOF'
#!/bin/bash
cd /root/crm_audit
source venv/bin/activate
export $(cat .env | xargs)
python -m telegram.bot_handler
EOF
chmod +x $WORKDIR/start_bot.sh

# Quick investigation script
cat > $WORKDIR/investigate.py << 'EOF'
#!/usr/bin/env python3
"""Quick investigation script."""
import sys
sys.path.insert(0, '/root/crm_audit')

from bots.investigator_bot import investigate

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python investigate.py <wallet_address>")
        sys.exit(1)
    
    wallet = sys.argv[1]
    result = investigate(wallet)
    print(json.dumps(result, indent=2, default=str))
EOF
chmod +x $WORKDIR/investigate.py

# Report generation script
cat > $WORKDIR/generate_report.py << 'EOF'
#!/usr/bin/env python3
"""Generate investigation report."""
import sys
sys.path.insert(0, '/root/crm_audit')

from forensic.report_generator import generate_final_report
import json

if __name__ == "__main__":
    report = generate_final_report()
    
    # Save to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"/root/crm_audit/evidence_reports/OMEGA_REPORT_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"Report saved to: {filename}")
    print(f"Wallets: {report['executive_summary']['enterprise_control']['wallets_identified']}")
    print(f"CRM Controlled: {report['executive_summary']['enterprise_control']['crm_controlled']:,.0f}")
EOF
chmod +x $WORKDIR/generate_report.py

echo "  ✓ Startup scripts created"
echo ""

# ============================================
# STEP 8: SETUP LOGGING
# ============================================
echo "📝 Step 8: Setting up logging..."

mkdir -p /var/log/omega_forensic
chmod 755 /var/log/omega_forensic

cat > $WORKDIR/logging.conf << 'EOF'
[loggers]
keys=root,omega

[handlers]
keys=fileHandler,consoleHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_omega]
level=INFO
handlers=fileHandler,consoleHandler
qualname=omega
propagate=0

[handler_fileHandler]
class=FileHandler
level=INFO
formatter=simpleFormatter
args=('/var/log/omega_forensic/investigation.log', 'a')

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
datefmt=%Y-%m-%d %H:%M:%S
EOF

echo "  ✓ Logging configured"
echo ""

# ============================================
# STEP 9: CREATE SYSTEMD SERVICE (OPTIONAL)
# ============================================
echo "⚙️ Step 9: Creating systemd service..."

cat > /etc/systemd/system/omega-forensic.service << EOF
[Unit]
Description=Omega Forensic V5 Investigation Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$WORKDIR
Environment=PYTHONPATH=$WORKDIR
ExecStart=$WORKDIR/venv/bin/python -m telegram.bot_handler
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload

echo "  ✓ Systemd service created"
echo "  Start with: systemctl start omega-forensic"
echo "  Enable auto-start: systemctl enable omega-forensic"
echo ""

# ============================================
# STEP 10: SECURITY HARDENING
# ============================================
echo "🔒 Step 10: Security hardening..."

# Disable password authentication (use keys only)
# sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
# systemctl restart sshd

# Set file permissions
chmod 700 $WORKDIR
chmod 600 $WORKDIR/.env

echo "  ✓ Security hardening complete"
echo ""

# ============================================
# STEP 11: FINAL SUMMARY
# ============================================
echo "=========================================="
echo "SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "📋 Summary:"
echo "  Server: $SERVER_USER@$SERVER_IP"
echo "  Workdir: $WORKDIR"
echo "  SSH: ssh $SERVER_USER@$SERVER_IP"
echo ""
echo "📁 Directory Structure:"
echo "  $WORKDIR/"
echo "  ├── config/        # API keys and settings"
echo "  ├── core/          # Core modules"
echo "  ├── forensic/      # Forensic analysis"
echo "  ├── bots/          # Bot implementations"
echo "  ├── telegram/      # Telegram handler"
echo "  ├── utils/         # Utilities"
echo "  ├── data/          # Database files"
echo "  ├── evidence/      # Evidence storage"
echo "  ├── evidence_reports/  # Generated reports"
echo "  └── github_intel/  # GitHub intelligence"
echo ""
echo "🚀 Quick Start:"
echo "  1. Copy Omega Forensic V5 code to $WORKDIR"
echo "  2. Start bot: ./start_bot.sh"
echo "  3. Or use systemd: systemctl start omega-forensic"
echo ""
echo "📊 Monitoring:"
echo "  Logs: tail -f /var/log/omega_forensic/investigation.log"
echo "  Status: systemctl status omega-forensic"
echo ""
echo "🔥 Firewall Status:"
ufw status

echo ""
echo "=========================================="
echo "OMEGA FORENSIC V5 IS READY"
echo "=========================================="
