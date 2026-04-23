#!/bin/bash
# RMI Server Setup Script
# =======================
# Run this on your Contabo VPS to set up the complete RMI platform
# Server: 167.86.116.51

set -e

RMI_DIR="/root/rmi-platform"
DOMAIN="intel.cryptorugmunch.com"
SERVER_IP="167.86.116.51"

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                       ║"
echo "║   🔍 RMI - RugMunch Intelligence Platform Setup                       ║"
echo "║                                                                       ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Server: $SERVER_IP"
echo "Domain: $DOMAIN"
echo ""

# =============================================================================
# STEP 1: System Update & Dependencies
# =============================================================================
echo "📦 Step 1: Installing system dependencies..."

apt-get update
apt-get upgrade -y

# Install essential packages
apt-get install -y \
    build-essential \
    git \
    wget \
    curl \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    certbot \
    python3-certbot-nginx \
    ufw \
    fail2ban \
    htop \
    tmux \
    vim \
    unzip \
    supervisor

# =============================================================================
# STEP 2: Firewall Setup
# =============================================================================
echo "🔥 Step 2: Configuring firewall..."

ufw default deny incoming
ufw default allow outgoing

# Allow SSH, HTTP, HTTPS
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

# Allow app ports (internal only)
ufw allow from 127.0.0.1 to any port 5000
ufw allow from 127.0.0.1 to any port 8080:8090

# Enable firewall
echo "y" | ufw enable

ufw status

# =============================================================================
# STEP 3: Fail2Ban Setup
# =============================================================================
echo "🛡️  Step 3: Configuring fail2ban..."

cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
EOF

systemctl enable fail2ban
systemctl restart fail2ban

# =============================================================================
# STEP 4: Create RMI Directory Structure
# =============================================================================
echo "📁 Step 4: Creating directory structure..."

mkdir -p $RMI_DIR
cd $RMI_DIR

# Create subdirectories
mkdir -p {bots,config,core,forensic,telegram,web,data,logs,reports,static}

# =============================================================================
# STEP 5: Python Environment
# =============================================================================
echo "🐍 Step 5: Setting up Python environment..."

python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip

pip install \
    flask==3.0.0 \
    flask-cors==4.0.0 \
    python-telegram-bot==20.7 \
    aiohttp==3.9.1 \
    requests==2.31.0 \
    python-dotenv==1.0.0 \
    numpy==1.26.2 \
    pandas==2.1.4 \
    boto3==1.34.0 \
    google-generativeai==0.3.2

echo "Python packages installed"

# =============================================================================
# STEP 6: Create Environment File Template
# =============================================================================
echo "🔑 Step 6: Creating environment file template..."

cat > $RMI_DIR/.env.template << 'EOF'
# RMI Platform Environment Variables
# Copy this to .env and fill in your API keys

# ============================================
# BLOCKCHAIN APIs
# ============================================
HELIUS_API_KEY=your_helius_key_here
QUICKNODE_URL=your_quicknode_url_here
ARKHAM_API_KEY=your_arkham_key_here

# ============================================
# RISK & OSINT APIs
# ============================================
MISTTRACK_API_KEY=your_misttrack_key_here
CHAINABUSE_API_KEY=your_chainabuse_key_here

# ============================================
# TOKEN ANALYTICS APIs
# ============================================
BIRDEYE_API_KEY=your_birdeye_key_here
LUNARCRUSH_API_KEY=your_lunarcrush_key_here

# ============================================
# AI / LLM APIs
# ============================================
GROQ_API_KEY=your_groq_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here

# AWS (for Bedrock)
AWS_ACCESS_KEY_ID=your_aws_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_here
AWS_REGION=us-east-1

# ============================================
# TELEGRAM
# ============================================
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# ============================================
# SERVER CONFIG
# ============================================
DOMAIN=intel.cryptorugmunch.com
FLASK_PORT=5000
FLASK_ENV=production
EOF

echo "✅ Environment template created at: $RMI_DIR/.env.template"
echo "   Copy to .env and fill in your API keys!"

# =============================================================================
# STEP 7: Nginx Configuration
# =============================================================================
echo "🌐 Step 7: Configuring Nginx..."

# Remove default config
rm -f /etc/nginx/sites-enabled/default

# Create RMI config
cat > /etc/nginx/sites-available/rmi << EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    location /static {
        alias $RMI_DIR/static;
        expires 1d;
    }

    client_max_body_size 50M;
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/rmi /etc/nginx/sites-enabled/rmi

# Test nginx config
nginx -t

# Restart nginx
systemctl restart nginx

# =============================================================================
# STEP 8: SSL Certificate (Let's Encrypt)
# =============================================================================
echo "🔒 Step 8: Setting up SSL certificate..."

echo "NOTE: SSL will be configured after DNS is pointed to this server."
echo "Run: certbot --nginx -d $DOMAIN"

# =============================================================================
# STEP 9: Supervisor Configuration
# =============================================================================
echo "⚙️  Step 9: Configuring supervisor..."

# Web app service
cat > /etc/supervisor/conf.d/rmi-web.conf << EOF
[program:rmi-web]
directory=$RMI_DIR
command=$RMI_DIR/venv/bin/python main.py web
autostart=true
autorestart=true
user=root
stdout_logfile=$RMI_DIR/logs/web.log
stderr_logfile=$RMI_DIR/logs/web-error.log
environment=PYTHONPATH="$RMI_DIR"
EOF

# Telegram bot service
cat > /etc/supervisor/conf.d/rmi-telegram.conf << EOF
[program:rmi-telegram]
directory=$RMI_DIR
command=$RMI_DIR/venv/bin/python main.py telegram
autostart=false
autorestart=true
user=root
stdout_logfile=$RMI_DIR/logs/telegram.log
stderr_logfile=$RMI_DIR/logs/telegram-error.log
environment=PYTHONPATH="$RMI_DIR"
EOF

# Reload supervisor
supervisorctl reread
supervisorctl update

# =============================================================================
# STEP 10: Create Startup Script
# =============================================================================
echo "🚀 Step 10: Creating startup scripts..."

cat > $RMI_DIR/start.sh << 'EOF'
#!/bin/bash
# Start RMI Platform

cd /root/rmi-platform
source venv/bin/activate

# Load environment
export $(cat .env | xargs)

# Start web server
echo "Starting web server..."
supervisorctl start rmi-web

# Start telegram bot (optional)
# echo "Starting Telegram bot..."
# supervisorctl start rmi-telegram

echo "RMI Platform started!"
echo "Web: http://localhost:5000"
echo "Logs: tail -f /root/rmi-platform/logs/*.log"
EOF

cat > $RMI_DIR/stop.sh << 'EOF'
#!/bin/bash
# Stop RMI Platform

echo "Stopping RMI Platform..."
supervisorctl stop rmi-web
supervisorctl stop rmi-telegram

echo "RMI Platform stopped."
EOF

cat > $RMI_DIR/status.sh << 'EOF'
#!/bin/bash
# Check RMI Platform status

echo "=== RMI Platform Status ==="
echo ""
echo "Supervisor processes:"
supervisorctl status

echo ""
echo "Nginx status:"
systemctl status nginx --no-pager | head -5

echo ""
echo "Recent logs:"
tail -20 /root/rmi-platform/logs/web.log 2>/dev/null || echo "No web logs yet"
EOF

chmod +x $RMI_DIR/start.sh $RMI_DIR/stop.sh $RMI_DIR/status.sh

# =============================================================================
# STEP 11: Create README
# =============================================================================
echo "📝 Step 11: Creating README..."

cat > $RMI_DIR/README.md << 'EOF'
# RMI - RugMunch Intelligence Platform

Crypto fraud investigation platform for the CRM token case.

## Quick Start

1. **Copy environment file and add API keys:**
   ```bash
   cp .env.template .env
   nano .env  # Add your API keys
   ```

2. **Start the platform:**
   ```bash
   ./start.sh
   ```

3. **Check status:**
   ```bash
   ./status.sh
   ```

4. **View logs:**
   ```bash
   tail -f logs/web.log
   tail -f logs/telegram.log
   ```

## Services

- **Web App:** http://intel.cryptorugmunch.com
- **API:** http://intel.cryptorugmunch.com/api/
- **Telegram:** @RugMunchIntelBot

## Commands

```bash
# Start services
./start.sh

# Stop services
./stop.sh

# Check status
./status.sh

# Generate report
python main.py report

# View LLM recommendations
python main.py llm
```

## Directory Structure

```
/root/rmi-platform/
├── bots/           # RMI Bot, Investigator Bot
├── config/         # API keys, LLM config
├── core/           # LLM rotation, data processor
├── forensic/       # API arsenal, clustering, reports
├── telegram/       # Telegram bot handler
├── web/            # Flask app, visualizations
├── data/           # Wallet database, evidence
├── logs/           # Application logs
├── reports/        # Generated reports
├── static/         # Static files
├── main.py         # Entry point
├── start.sh        # Start script
├── stop.sh         # Stop script
└── status.sh       # Status script
```

## API Endpoints

- `GET /api/status` - System status
- `GET /api/investigate/<wallet>` - Investigate wallet
- `GET /api/cluster/<wallet>` - Find clusters
- `GET /api/bubble/<wallet>` - Generate bubble map
- `GET /api/methodology` - View methodology

## Security

- Firewall enabled (ufw)
- Fail2ban configured
- SSL via Let's Encrypt
- Services run under supervisor

## Support

Built with Kimi AI for the CRM token investigation.
EOF

# =============================================================================
# STEP 12: Security Hardening
# =============================================================================
echo "🔐 Step 12: Security hardening..."

# Disable root login via password (use key auth)
sed -i 's/#PermitRootLogin yes/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config

# Disable password authentication
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

# Restart SSH
systemctl restart sshd

echo "✅ SSH hardened (key auth only)"

# =============================================================================
# COMPLETION
# =============================================================================
echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                       ║"
echo "║   ✅ RMI Platform Setup Complete!                                     ║"
echo "║                                                                       ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Copy your code to: $RMI_DIR"
echo "   scp -r omega_forensic_v5/* root@$SERVER_IP:$RMI_DIR/"
echo ""
echo "2. Set up environment variables:"
echo "   cp $RMI_DIR/.env.template $RMI_DIR/.env"
echo "   nano $RMI_DIR/.env"
echo ""
echo "3. Point DNS to: $SERVER_IP"
echo ""
echo "4. Get SSL certificate:"
echo "   certbot --nginx -d $DOMAIN"
echo ""
echo "5. Start the platform:"
echo "   cd $RMI_DIR && ./start.sh"
echo ""
echo "📊 Server Info:"
echo "   IP: $SERVER_IP"
echo "   Domain: $DOMAIN"
echo "   Directory: $RMI_DIR"
echo ""
echo "🔧 Useful Commands:"
echo "   ./start.sh      - Start services"
echo "   ./stop.sh       - Stop services"
echo "   ./status.sh     - Check status"
echo "   tail -f logs/*  - View logs"
echo ""
echo "🌐 Access:"
echo "   Web: http://$DOMAIN (after DNS setup)"
echo "   API: http://$DOMAIN/api/"
echo ""
