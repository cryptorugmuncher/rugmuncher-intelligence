#!/bin/bash
#
# 🔍 RMI Tools Launcher
# Quick launcher for RMI investigation tools
#

set -e

RMI_DIR="/root/rmi"
TOOLS_DIR="$RMI_DIR/tools"
API_DIR="$RMI_DIR/api"

colors() {
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
}

check_env() {
    if [ -f "/root/.env" ]; then
        echo -e "${GREEN}✓${NC} Environment file found"
        export $(grep -v '^#' /root/.env | xargs) 2>/dev/null || true
    else
        echo -e "${YELLOW}⚠${NC} No .env file found at /root/.env"
    fi
}

show_help() {
    echo -e "${BLUE}🔍 RMI Tools Launcher${NC}"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  process         Run evidence processing pipeline"
    echo "  wallets [n]     Analyze top N wallets (default: 50)"
    echo "  server          Start API server"
    echo "  server-bg       Start API server in background"
    echo "  status          Show investigation status"
    echo "  test            Run API tests"
    echo "  help            Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 process           # Process all evidence"
    echo "  $0 wallets 100       # Analyze top 100 wallets"
    echo "  $0 server-bg         # Start server in background"
}

run_processor() {
    echo -e "${BLUE}🔍 Running Evidence Processor...${NC}"
    cd "$TOOLS_DIR"
    python3 evidence_processor.py --full
    echo ""
    echo -e "${GREEN}✓${NC} Evidence processing complete"
    echo "  Output: $TOOLS_DIR/extracted/"
}

run_wallet_tracer() {
    local limit=${1:-50}
    echo -e "${BLUE}💼 Analyzing top $limit wallets...${NC}"
    cd "$TOOLS_DIR"
    python3 wallet_tracer.py --top "$limit" --export
    echo ""
    echo -e "${GREEN}✓${NC} Wallet analysis complete"
    echo "  Output: $TOOLS_DIR/tracing_results/"
}

start_server() {
    local bg=${1:-false}
    echo -e "${BLUE}🚀 Starting Investigation API Server...${NC}"
    
    # Check if already running
    if pgrep -f "investigation_server.py" > /dev/null; then
        echo -e "${YELLOW}⚠${NC} Server already running"
        echo "  PID: $(pgrep -f "investigation_server.py")"
        echo "  Test: curl http://localhost:5000/api/health"
        return
    fi
    
    cd "$API_DIR"
    
    if [ "$bg" = true ]; then
        python3 investigation_server.py > /tmp/rmi_server.log 2>&1 &
        echo $! > /tmp/rmi_server.pid
        sleep 2
        echo -e "${GREEN}✓${NC} Server started in background"
        echo "  PID: $(cat /tmp/rmi_server.pid)"
        echo "  Log: /tmp/rmi_server.log"
        echo "  Test: curl http://localhost:5000/api/health"
    else
        echo "Press Ctrl+C to stop"
        echo ""
        python3 investigation_server.py
    fi
}

show_status() {
    echo -e "${BLUE}📊 RMI Investigation Status${NC}"
    echo ""
    
    # Check server
    if pgrep -f "investigation_server.py" > /dev/null; then
        echo -e "${GREEN}✓${NC} API Server: Running"
        echo "  PID: $(pgrep -f "investigation_server.py")"
    else
        echo -e "${RED}✗${NC} API Server: Not running"
    fi
    
    echo ""
    
    # Evidence stats
    if [ -f "$TOOLS_DIR/extracted/pipeline_results.json" ]; then
        echo -e "${GREEN}✓${NC} Evidence processing: Complete"
        cat "$TOOLS_DIR/extracted/pipeline_results.json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"  Wallets found: {data.get('all_wallets', 0)}\")
print(f\"  Started: {data.get('pipeline_start', 'N/A')[:19]}\")
" 2>/dev/null || true
    else
        echo -e "${YELLOW}⚠${NC} Evidence processing: Not run yet"
    fi
    
    echo ""
    
    # Wallet analysis stats
    if [ -d "$TOOLS_DIR/tracing_results" ]; then
        local count=$(ls -1 "$TOOLS_DIR/tracing_results"/wallet_analysis_*.json 2>/dev/null | wc -l)
        if [ "$count" -gt 0 ]; then
            echo -e "${GREEN}✓${NC} Wallet analysis: $count result files"
            ls -la "$TOOLS_DIR/tracing_results"/wallet_analysis_*.json | tail -3
        else
            echo -e "${YELLOW}⚠${NC} Wallet analysis: No results yet"
        fi
    else
        echo -e "${YELLOW}⚠${NC} Wallet analysis: Not run yet"
    fi
    
    echo ""
    
    # Quick API test
    echo -e "${BLUE}Testing API...${NC}"
    curl -s http://localhost:5000/api/health | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f\"  Health: {data.get('status', 'unknown')}\")
    print(f\"  Supabase: {'connected' if data.get('supabase_connected') else 'disconnected'}\")
    print(f\"  n8n: {'configured' if data.get('n8n_configured') else 'not configured'}\")
except:
    print('  API not responding')
" 2>/dev/null || echo "  API not responding"
}

run_tests() {
    echo -e "${BLUE}🧪 Testing RMI API...${NC}"
    echo ""
    
    local base="http://localhost:5000"
    
    echo "Testing endpoints:"
    
    # Health
    echo -n "  /api/health ... "
    if curl -s "$base/api/health" > /dev/null; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${RED}FAIL${NC}"
    fi
    
    # Status
    echo -n "  /api/investigation/status ... "
    if curl -s "$base/api/investigation/status" > /dev/null; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${RED}FAIL${NC}"
    fi
    
    # Wallets
    echo -n "  /api/investigation/wallets ... "
    if curl -s "$base/api/investigation/wallets?limit=5" > /dev/null; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${RED}FAIL${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}✓${NC} Tests complete"
}

stop_server() {
    if [ -f /tmp/rmi_server.pid ]; then
        echo "Stopping server..."
        kill $(cat /tmp/rmi_server.pid) 2>/dev/null || true
        rm /tmp/rmi_server.pid
        echo -e "${GREEN}✓${NC} Server stopped"
    else
        echo "No PID file found, trying to find process..."
        pkill -f "investigation_server.py" 2>/dev/null || true
        echo -e "${GREEN}✓${NC} Server stopped"
    fi
}

# Main
colors
check_env

case "${1:-help}" in
    process)
        run_processor
        ;;
    wallets)
        run_wallet_tracer "${2:-50}"
        ;;
    server)
        start_server false
        ;;
    server-bg)
        start_server true
        ;;
    status)
        show_status
        ;;
    test)
        run_tests
        ;;
    stop)
        stop_server
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
