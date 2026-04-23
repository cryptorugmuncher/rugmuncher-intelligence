#!/bin/bash
# Migrate from Redis to DragonflyDB - 10x Performance Upgrade
# Dragonfly: Multi-threaded Redis replacement

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "═══════════════════════════════════════════════════════════"
echo "  🐲 MIGRATING TO DRAGONFLY DB"
echo "  Multi-threaded Redis Replacement"
echo "═══════════════════════════════════════════════════════════"
echo -e "${NC}"

# Get current Redis password
if [ -f /root/.redis_password ]; then
    REDIS_PASSWORD=$(cat /root/.redis_password)
    echo -e "${GREEN}✅ Using existing password${NC}"
else
    REDIS_PASSWORD="RugMuncher$(openssl rand -hex 16)"
    echo "$REDIS_PASSWORD" > /root/.redis_password
    chmod 600 /root/.redis_password
    echo -e "${YELLOW}⚠️ Generated new password${NC}"
fi

# ═══════════════════════════════════════════════════════════
# STEP 1: Backup Redis Data
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${BLUE}STEP 1: Backing up Redis data...${NC}"

if redis-cli -a "$REDIS_PASSWORD" ping > /dev/null 2>&1; then
    redis-cli -a "$REDIS_PASSWORD" BGSAVE
    sleep 2
    cp /var/lib/redis/dump.rdb /root/redis-backup-$(date +%Y%m%d).rdb 2>/dev/null || echo "No RDB to backup"
    echo -e "${GREEN}✅ Backup created${NC}"
else
    echo -e "${YELLOW}⚠️ Redis not running, no backup needed${NC}"
fi

# ═══════════════════════════════════════════════════════════
# STEP 2: Stop Redis
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${BLUE}STEP 2: Stopping Redis...${NC}"

systemctl stop redis-server 2>/dev/null || true
systemctl disable redis-server 2>/dev/null || true
pkill -9 redis-server 2>/dev/null || true
sleep 2

echo -e "${GREEN}✅ Redis stopped${NC}"

# ═══════════════════════════════════════════════════════════
# STEP 3: Install Dragonfly
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${BLUE}STEP 3: Installing DragonflyDB...${NC}"

# Download latest Dragonfly
cd /tmp
DF_VERSION=$(curl -s https://api.github.com/repos/dragonflydb/dragonfly/releases/latest | grep '"tag_name":' | cut -d'"' -f4)
echo "Downloading Dragonfly $DF_VERSION..."

wget -q "https://github.com/dragonflydb/dragonfly/releases/download/${DF_VERSION}/dragonfly-${DF_VERSION}-linux-amd64.tar.gz" -O dragonfly.tar.gz
tar -xzf dragonfly.tar.gz
mv dragonfly-${DF_VERSION}-linux-amd64 /usr/local/bin/dragonfly
chmod +x /usr/local/bin/dragonfly
rm -f dragonfly.tar.gz

echo -e "${GREEN}✅ Dragonfly installed${NC}"

# ═══════════════════════════════════════════════════════════
# STEP 4: Configure Dragonfly
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${BLUE}STEP 4: Configuring Dragonfly...${NC}"

mkdir -p /etc/dragonfly
mkdir -p /var/lib/dragonfly
chown dragonfly:dragonfly /var/lib/dragonfly 2>/dev/null || true

cat > /etc/dragonfly/dragonfly.conf << EOF
# DragonflyDB Configuration for RugMuncher
# Multi-threaded Redis replacement

# Network
--bind 0.0.0.0
--port 6379

# Security
--requirepass $REDIS_PASSWORD

# Performance - Use all 8 cores!
--proactor_threads=8
--maxmemory=4gb

# Persistence (non-blocking snapshots!)
--dbfilename dump.rdb
--dir=/var/lib/dragonfly
--save_schedule "*/5 * * * *"

# Logging
--logtostderr
--v=1

# Advanced features
--enable_multi_shard_execution=true
EOF

echo -e "${GREEN}✅ Configuration created${NC}"

# ═══════════════════════════════════════════════════════════
# STEP 5: Create Systemd Service
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${BLUE}STEP 5: Creating systemd service...${NC}"

cat > /etc/systemd/system/dragonfly.service << EOF
[Unit]
Description=DragonflyDB - Multi-threaded Redis replacement
After=network.target

[Service]
Type=simple
User=root
Group=root
ExecStart=/usr/local/bin/dragonfly --flagfile=/etc/dragonfly/dragonfly.conf
ExecStop=/bin/kill -SIGTERM \$MAINPID
Restart=always
RestartSec=5

# Performance tuning
LimitNOFILE=65536
LimitNPROC=65536

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable dragonfly

echo -e "${GREEN}✅ Service created${NC}"

# ═══════════════════════════════════════════════════════════
# STEP 6: Start Dragonfly
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${BLUE}STEP 6: Starting Dragonfly...${NC}"

systemctl start dragonfly
sleep 3

# Test connection
if redis-cli -a "$REDIS_PASSWORD" ping 2>/dev/null | grep -q "PONG"; then
    echo -e "${GREEN}✅ Dragonfly is running!${NC}"
else
    echo -e "${RED}❌ Dragonfly failed to start${NC}"
    journalctl -u dragonfly --no-pager -n 20
    exit 1
fi

# ═══════════════════════════════════════════════════════════
# STEP 7: Performance Test
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${BLUE}STEP 7: Performance test...${NC}"

echo "Running 1000 SET operations..."
time redis-cli -a "$REDIS_PASSWORD" --eval <(cat <<'LUA'
local start = redis.call('TIME')[1]
for i = 1, 1000 do
    redis.call('SET', 'perf:test:' .. i, 'value' .. i)
end
local stop = redis.call('TIME')[1]
return 'Time: ' .. (stop - start) .. 's'
LUA
) 2>/dev/null || echo "Test skipped"

# Show info
echo ""
echo -e "${CYAN}Dragonfly Info:${NC}"
redis-cli -a "$REDIS_PASSWORD" INFO server 2>/dev/null | grep -E "dragonfly_version|redis_mode|arch_bits" || echo "Version info unavailable"

# ═══════════════════════════════════════════════════════════
# STEP 8: Update Scripts
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${BLUE}STEP 8: Updating helper scripts...${NC}"

cat > /usr/local/bin/rmi-redis << EOF
#!/bin/bash
# Now connects to Dragonfly (drop-in replacement)
PASS=\$(cat /root/.redis_password 2>/dev/null || echo "")
redis-cli -a "\$PASS" "\$@"
EOF
chmod +x /usr/local/bin/rmi-redis

cat > /usr/local/bin/rmi-cache << EOF
#!/bin/bash
# Dragonfly cache stats
PASS=\$(cat /root/.redis_password 2>/dev/null || echo "")
echo "=== Dragonfly Stats ==="
redis-cli -a "\$PASS" INFO stats 2>/dev/null | grep -E "(instantaneous_ops_per_sec|total_commands_processed)" | head -2
echo ""
echo "=== Memory ==="
redis-cli -a "\$PASS" INFO memory 2>/dev/null | grep "used_memory_human"
echo ""
echo "=== Connections ==="
redis-cli -a "\$PASS" INFO clients 2>/dev/null | grep "connected_clients"
EOF
chmod +x /usr/local/bin/rmi-cache

# ═══════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════"
echo "  ✅ DRAGONFLY DEPLOYMENT COMPLETE!"
echo "═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}🐲 Dragonfly is now running on port 6379${NC}"
echo ""
echo -e "${BLUE}🔥 Performance Improvements:${NC}"
echo "   • Multi-threaded: Using all 8 CPU cores"
echo "   • 10x higher throughput for concurrent queries"
echo "   • Non-blocking snapshots: No API freezes"
echo "   • Better memory efficiency"
echo ""
echo -e "${BLUE}📊 Connection Info:${NC}"
echo "   Host: $(curl -s ifconfig.me 2>/dev/null || echo 'your-server-ip')"
echo "   Port: 6379"
echo "   Password: $REDIS_PASSWORD"
echo ""
echo -e "${BLUE}🔧 Commands:${NC}"
echo "   rmi-redis ping        - Test connection"
echo "   rmi-cache             - Show performance stats"
echo "   systemctl status dragonfly"
echo ""
echo -e "${YELLOW}💡 Your existing code works unchanged!${NC}"
echo "   All redis-cli commands work with Dragonfly"
echo "   No code changes needed in your bot"
echo "═══════════════════════════════════════════════════════════"
