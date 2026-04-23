#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# RMI Platform - Health Check & Auto-Restart Script
# Run this via cron every minute for high availability
# ═══════════════════════════════════════════════════════════════════

LOG_FILE="/var/log/rmi/health_check.log"
mkdir -p /var/log/rmi

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> $LOG_FILE
}

# Function to check and restart service
check_and_restart() {
    local name=$1
    local url=$2
    local start_cmd=$3
    local pid_file=$4
    
    if ! curl -s "$url" > /dev/null 2>&1; then
        log "⚠ $name is DOWN - Attempting restart..."
        
        # Kill existing process if any
        if [ -n "$pid_file" ] && [ -f "$pid_file" ]; then
            kill -9 $(cat "$pid_file") 2>/dev/null || true
            rm -f "$pid_file"
        fi
        
        # Start service
        eval "$start_cmd"
        sleep 5
        
        # Verify restart
        if curl -s "$url" > /dev/null 2>&1; then
            log "✓ $name restarted successfully"
        else
            log "✗ $name failed to restart"
        fi
    fi
}

# Check Backend API
check_and_restart \
    "Backend API" \
    "http://localhost:8002/health" \
    "cd /root/rmi/backend && source venv/bin/activate && export DATABASE_URL='postgresql://rmi_user:rmi_secure_pass_2024@localhost:5432/rmi_db' && export REDIS_URL='redis://:RugMuncherd451c307f52f8e061a2cc79a@localhost:6379/0' && nohup python3 -c 'from main import app; import uvicorn; uvicorn.run(app, host=\"0.0.0.0\", port=8002)' > /var/log/rmi/backend.log 2>&1 & echo \$! > /var/run/rmi-backend.pid" \
    "/var/run/rmi-backend.pid"

# Check Frontend
check_and_restart \
    "Frontend" \
    "http://localhost:3000" \
    "cd /root/rmi/frontend/the-trenches && nohup python3 -m http.server 3000 > /var/log/rmi/frontend.log 2>&1 & echo \$! > /var/run/rmi-frontend.pid" \
    "/var/run/rmi-frontend.pid"

# Check Docker containers
for container in dragonfly n8n; do
    if ! docker ps | grep -q "$container"; then
        log "⚠ Container $container is DOWN - Starting..."
        docker start "$container" 2>/dev/null || log "✗ Failed to start $container"
    fi
done

# Check PostgreSQL
if ! systemctl is-active --quiet postgresql; then
    log "⚠ PostgreSQL is DOWN - Starting..."
    systemctl start postgresql
fi

# Log system stats every 5 minutes
if [ $(date +%M) % 5 -eq 0 ]; then
    CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    MEM=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    log "System stats - CPU: ${CPU}%, Memory: ${MEM}%"
fi
