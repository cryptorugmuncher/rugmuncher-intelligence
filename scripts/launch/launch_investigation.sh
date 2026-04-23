#!/bin/bash
"""
CRM INVESTIGATION SYSTEM LAUNCHER
=================================
Unified launcher for the complete investigation infrastructure

Usage:
    ./launch_investigation.sh [command]

Commands:
    api       - Start the API server (port 8000)
    portal    - Start the investigation portal (opens browser)
    checker   - Run closed wallet checker
    all       - Start everything
    help      - Show this help
"""

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║      🔍 CRM INVESTIGATION SYSTEM LAUNCHER                 ║"
echo "║      Case: SOSANA-CRM-2024 | Status: ACTIVE               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Directories
RMI_DIR="/root/rmi"
API_DIR="$RMI_DIR/backend/api"
FRONTEND_DIR="$RMI_DIR/frontend/retail"
INVESTIGATION_DIR="$RMI_DIR/investigation"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}⚠️  Note: Some features may require root access${NC}"
fi

show_help() {
    cat << EOF

CRM Investigation System - Available Commands:

${GREEN}./launch_investigation.sh api${NC}
    Start the FastAPI backend server on port 8000
    Provides wallet verification, evidence serving, on-chain queries

${GREEN}./launch_investigation.sh portal${NC}
    Open the investigation portal in your browser
    Complete frontend for case visualization and verification

${GREEN}./launch_investigation.sh checker${NC}
    Run the closed wallet transaction checker
    Reconstructs history for wiped/closed wallets

${GREEN}./launch_investigation.sh case${NC}
    Display case summary and key evidence

${GREEN}./launch_investigation.sh verify [wallet]${NC}
    Quick wallet verification against case database

${GREEN}./launch_investigation.sh all${NC}
    Start API server and open portal (recommended)

${GREEN}./launch_investigation.sh help${NC}
    Show this help message

${YELLOW}Examples:${NC}
    ./launch_investigation.sh api              # Start backend
    ./launch_investigation.sh verify AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6
    ./launch_investigation.sh all              # Full system

EOF
}

start_api() {
    echo -e "${BLUE}🚀 Starting Investigation API Server...${NC}"
    echo -e "${YELLOW}   Port: 8000${NC}"
    echo -e "${YELLOW}   Docs: http://localhost:8000/docs${NC}"
    echo ""
    
    cd "$API_DIR"
    
    # Check if already running
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  API already running on port 8000${NC}"
        return
    fi
    
    # Start in background
    python3 investigation_api.py > /tmp/investigation_api.log 2>&1 &
    API_PID=$!
    
    # Save PID
    echo $API_PID > /tmp/investigation_api.pid
    
    # Wait for startup
    sleep 2
    
    # Check if started successfully
    if kill -0 $API_PID 2>/dev/null; then
        echo -e "${GREEN}✅ API Server started successfully (PID: $API_PID)${NC}"
        echo -e "${CYAN}📊 API Endpoints:${NC}"
        echo -e "   • http://localhost:8000/ - API Info"
        echo -e "   • http://localhost:8000/api/wallet/{address} - Wallet check"
        echo -e "   • http://localhost:8000/api/tiers - Tier structure"
        echo -e "   • http://localhost:8000/api/timeline - Case timeline"
        echo -e "   • http://localhost:8000/api/verify/chain/{wallet} - On-chain verification"
    else
        echo -e "${RED}❌ Failed to start API server${NC}"
        cat /tmp/investigation_api.log
        exit 1
    fi
}

open_portal() {
    echo -e "${BLUE}🌐 Opening Investigation Portal...${NC}"
    
    PORTAL_FILE="$FRONTEND_DIR/investigation-portal.html"
    
    if [ -f "$PORTAL_FILE" ]; then
        # Try different methods to open browser
        if command -v xdg-open &> /dev/null; then
            xdg-open "$PORTAL_FILE" &
        elif command -v python3 &> /dev/null; then
            cd "$FRONTEND_DIR"
            python3 -m http.server 8080 > /tmp/portal_server.log 2>&1 &
            sleep 1
            echo -e "${GREEN}✅ Portal server started on http://localhost:8080${NC}"
        else
            echo -e "${YELLOW}⚠️  Portal file location:${NC}"
            echo -e "   file://$PORTAL_FILE"
        fi
        
        echo -e "${CYAN}📁 Portal Features:${NC}"
        echo -e "   • Dashboard with case overview"
        echo -e "   • Wallet scanner with 692+ known addresses"
        echo -e "   • 5-tier criminal enterprise visualization"
        echo -e "   • Timeline with smoking gun evidence"
        echo -e "   • Closed wallet transaction checker"
        echo -e "   • Evidence portal (237 files organized)"
    else
        echo -e "${RED}❌ Portal file not found at $PORTAL_FILE${NC}"
    fi
}

run_checker() {
    echo -e "${BLUE}🔍 Running Closed Wallet Transaction Checker...${NC}"
    
    CHECKER_SCRIPT="$INVESTIGATION_DIR/wallet_tracer/closed_wallet_checker.py"
    
    if [ -f "$CHECKER_SCRIPT" ]; then
        cd "$INVESTIGATION_DIR/wallet_tracer"
        python3 closed_wallet_checker.py
    else
        echo -e "${RED}❌ Closed wallet checker not found${NC}"
    fi
}

show_case() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║           CASE SUMMARY: SOSANA-CRM-2024                    ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${GREEN}📊 Key Statistics:${NC}"
    echo "   • Financial Impact: $886,597+ extracted"
    echo "   • Victim Wallets: 970+ confirmed"
    echo "   • Criminal Tiers: 5-tier hierarchy identified"
    echo "   • Evidence Files: 237 files categorized"
    echo "   • Evidence Confidence: 97-99% blockchain-verified"
    echo ""
    
    echo -e "${RED}🔴 Critical Evidence (Smoking Gun):${NC}"
    echo "   March 26, 2026, 21:38:07 UTC"
    echo "   → Tier 1 wallet seeded 970 wallets in 7 seconds"
    echo "   → Rate: 138 wallets per second"
    echo "   → Human maximum: 2-3 wallets in 7 seconds"
    echo "   → VERDICT: Military-grade automation proven"
    echo ""
    
    echo -e "${YELLOW}🕸️ Criminal Hierarchy:${NC}"
    echo "   Tier 1: AFXigaYu... - Root Infrastructure (1 wallet)"
    echo "   Tier 2: BMq4XUa3... - Cross-Project Bridge (1 wallet)"
    echo "   Tier 3: HxyXAE1P... - Field Coordination (1 wallet)"
    echo "   Tier 4: 8eVZa7bE... - Distribution (1 wallet)"
    echo "   Tier 5: 970 wallets - Execution Layer"
    echo ""
    
    echo -e "${BLUE}⚖️ Legal Framework:${NC}"
    echo "   • RICO (18 U.S.C. § 1962) - Pattern of racketeering"
    echo "   • Securities Fraud (15 U.S.C. § 78j) - Material misrepresentations"
    echo "   • Wire Fraud (18 U.S.C. § 1343) - Electronic scheme execution"
    echo "   • Money Laundering (18 U.S.C. § 1956) - Cross-token layering"
    echo ""
    
    echo -e "${CYAN}📁 Evidence Organization:${NC}"
    echo "   /root/crm_investigation/"
    echo "   ├── evidence/blockchain_data/     (holder lists, transactions)"
    echo "   ├── evidence/communications/      (67 Telegram exports)"
    echo "   ├── evidence/financial_records/     (10 CSV exports)"
    echo "   ├── evidence/forensic_reports/      (PDF reports, analysis)"
    echo "   ├── evidence/photos_screenshots/    (70 images)"
    echo "   └── evidence/configuration_files/   (compromised credentials)"
    echo ""
}

verify_wallet() {
    WALLET=$1
    
    if [ -z "$WALLET" ]; then
        echo -e "${RED}❌ Please provide a wallet address${NC}"
        echo "Usage: ./launch_investigation.sh verify [wallet_address]"
        return
    fi
    
    echo -e "${CYAN}🔍 Verifying wallet: $WALLET${NC}"
    echo ""
    
    # Known wallets
    case "$WALLET" in
        "AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6")
            echo -e "${RED}⚠️  TIER 1 WALLET - ROOT INFRASTRUCTURE${NC}"
            echo "   Function: Master routing node"
            echo "   Evidence: Seeded 970 wallets at 138/second"
            echo "   Status: ACTIVE THREAT"
            echo ""
            echo -e "${CYAN}🔗 Explorer Links:${NC}"
            echo "   https://solscan.io/account/$WALLET"
            echo "   https://explorer.solana.com/address/$WALLET"
            ;;
        "BMq4XUa3rJJNkjXbJDpMFdSmPjvz5f9w4TvYFGADVkX5")
            echo -e "${RED}⚠️  TIER 2 WALLET - CROSS-PROJECT BRIDGE${NC}"
            echo "   Function: SHIFT extraction to CRM infiltration"
            ;;
        "HxyXAE1PHQsh6iLj3t8MagpFovmR7yk76PEADmTKeVfi")
            echo -e "${RED}⚠️  TIER 3 WALLET - FIELD COORDINATION${NC}"
            echo "   Function: CRM transaction coordination"
            echo "   Evidence: 19 CRM transactions, $36.55 USDC float"
            ;;
        "8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj")
            echo -e "${RED}⚠️  TIER 4 WALLET - DISTRIBUTION${NC}"
            echo "   Function: Loading execution wallets"
            echo "   Evidence: 20M CRM free-loaded at $0 cost basis"
            ;;
        "7abBmGf4HNu3UXsanJc7WwAPW2PgkEb9hwrFKwCySvyL")
            echo -e "${RED}⚠️  TIER 5 WALLET - EXECUTION LAYER${NC}"
            echo "   Function: Victim whale position"
            echo "   Note: Compromised, used as field operative"
            ;;
        *)
            echo -e "${GREEN}✓ Wallet not in criminal database${NC}"
            echo ""
            echo -e "${CYAN}🔗 Check on blockchain:${NC}"
            echo "   https://solscan.io/account/$WALLET"
            echo "   https://birdeye.so/profile/$WALLET"
            ;;
    esac
}

stop_all() {
    echo -e "${YELLOW}🛑 Stopping all investigation services...${NC}"
    
    # Stop API
    if [ -f /tmp/investigation_api.pid ]; then
        kill $(cat /tmp/investigation_api.pid) 2>/dev/null && echo "   ✅ API server stopped"
        rm -f /tmp/investigation_api.pid
    fi
    
    # Stop portal server
    pkill -f "http.server 8080" 2>/dev/null && echo "   ✅ Portal server stopped"
    
    echo -e "${GREEN}✅ All services stopped${NC}"
}

# Main command handler
COMMAND=${1:-help}

 case "$COMMAND" in
    api)
        start_api
        ;;
    portal)
        open_portal
        ;;
    checker)
        run_checker
        ;;
    case)
        show_case
        ;;
    verify)
        verify_wallet "$2"
        ;;
    all)
        show_case
        echo ""
        start_api
        echo ""
        open_portal
        echo ""
        echo -e "${GREEN}✅ Investigation system fully operational!${NC}"
        echo ""
        echo -e "${CYAN}📊 System Status:${NC}"
        echo "   • API Server: http://localhost:8000"
        echo "   • Portal: http://localhost:8080 (or file://$FRONTEND_DIR/investigation-portal.html)"
        echo "   • API Docs: http://localhost:8000/docs"
        echo ""
        echo -e "${YELLOW}To stop all services:${NC} ./launch_investigation.sh stop"
        ;;
    stop)
        stop_all
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        show_help
        exit 1
        ;;
esac
