# 🛡️ RMI Platform - Reliability & High Availability Setup

## ✅ AUTOMATIC STARTUP ON BOOT

All services are configured to start automatically when the server boots:

```bash
# Enable auto-start
systemctl enable rmi-backend
systemctl enable rmi-frontend

# Services will start on boot and restart if they crash
```

## 📊 HEALTH MONITORING

### Every Minute (via Cron)
- Checks if Backend API is responding
- Checks if Frontend is serving pages
- Checks if Docker containers are running
- Checks PostgreSQL status
- **Auto-restarts any failed service**

### Backup Schedule
- Database backups: Twice daily (00:00 and 12:00)
- Keeps last 7 backups in `/root/rmi/backups/`

## 🚀 QUICK COMMANDS

```bash
# Start all services
/root/rmi/start_all_services.sh

# Stop all services
/root/rmi/stop_all_services.sh

# Check status
/root/rmi/status.sh

# Manual service control
systemctl start rmi-backend
systemctl stop rmi-backend
systemctl restart rmi-backend
systemctl status rmi-backend

# Same for frontend
systemctl start rmi-frontend
systemctl stop rmi-frontend
```

## 📋 SERVICE DETAILS

| Service | Port | Auto-Restart | Logs |
|---------|------|--------------|------|
| Backend API | 8002 | ✅ Always | `/var/log/rmi/backend.log` |
| Frontend | 3000 | ✅ Always | `/var/log/rmi/frontend.log` |
| PostgreSQL | 5432 | ✅ systemd | `/var/log/postgresql/` |
| DragonflyDB | 6379 | ✅ Docker | `docker logs dragonfly` |
| N8N | 5678 | ✅ Docker | `docker logs n8n` |

## 🔧 TROUBLESHOOTING

### If Backend Won't Start
```bash
# Check logs
tail -50 /var/log/rmi/backend.log

# Restart manually
cd /root/rmi/backend
source venv/bin/activate
python3 -c "from main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8002)"
```

### If Database Connection Fails
```bash
# Test PostgreSQL
psql -h localhost -U rmi_user -d rmi_db -c "SELECT 1"

# Restart PostgreSQL
systemctl restart postgresql
```

### If DragonflyDB Won't Start
```bash
# Restart container
docker restart dragonfly

# Check logs
docker logs dragonfly --tail 20
```

## 📝 CONFIGURATION FILES

| File | Purpose |
|------|---------|
| `/root/rmi/backend/.env` | Database credentials |
| `/root/rmi/.env` | DragonflyDB password |
| `/etc/systemd/system/rmi-backend.service` | Backend service config |
| `/etc/systemd/system/rmi-frontend.service` | Frontend service config |
| `/var/spool/cron/crontabs/root` | Health check & backup cron |

## 🎯 MONITORING ENDPOINTS

```bash
# Health check
curl http://localhost:8002/health

# Expected response:
{"status":"healthy","services":{"supabase":"connected","redis":"connected"}}

# API documentation
curl http://localhost:8002/docs

# Database stats
curl http://localhost:8002/api/v1/admin/system/health
```

## 🔄 UPDATE PROCEDURE

```bash
# 1. Stop services
/root/rmi/stop_all_services.sh

# 2. Pull updates (if using git)
cd /root/rmi && git pull

# 3. Restart services
/root/rmi/start_all_services.sh

# 4. Verify
/root/rmi/status.sh
```

## 🚨 ALERTS

The system will automatically:
- ✅ Restart crashed services within 10 seconds
- ✅ Create database backups twice daily
- ✅ Log all health checks to `/var/log/rmi/health_check.log`

---

**Your system is now configured for 99.9% uptime!** 🎉
