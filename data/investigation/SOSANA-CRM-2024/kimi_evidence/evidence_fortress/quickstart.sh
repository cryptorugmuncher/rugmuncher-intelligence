#!/bin/bash
# Evidence Fortress Quick Start Script
# Usage: ./quickstart.sh

set -e

echo "======================================================================"
echo "EVIDENCE FORTRESS v4.0 - Quick Start"
echo "======================================================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "Step 1: Checking Python..."
python3 --version || { echo "${RED}Python 3 not found!${NC}"; exit 1; }

echo ""
echo "Step 2: Installing dependencies..."
pip install -q -r requirements.txt
echo "${GREEN}✓ Dependencies installed${NC}"

echo ""
echo "Step 3: Checking PostgreSQL..."
if command -v psql &> /dev/null; then
    echo "${GREEN}✓ PostgreSQL found${NC}"
else
    echo "${YELLOW}⚠ PostgreSQL not found. Install with:${NC}"
    echo "  Ubuntu/Debian: sudo apt install postgresql postgresql-contrib"
    echo "  CentOS/RHEL:   sudo yum install postgresql-server"
    exit 1
fi

echo ""
echo "Step 4: Setting up database..."
read -p "PostgreSQL password for 'postgres' user: " -s DB_PASS
echo ""

export PGPASSWORD=$DB_PASS

# Create database and user
psql -U postgres -c "DROP DATABASE IF EXISTS evidence_fortress;" 2>/dev/null || true
psql -U postgres -c "DROP USER IF EXISTS evidence_user;" 2>/dev/null || true
psql -U postgres -c "CREATE DATABASE evidence_fortress;"
psql -U postgres -c "CREATE USER evidence_user WITH PASSWORD 'evidence_pass_2026';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE evidence_fortress TO evidence_user;"

echo "${GREEN}✓ Database created${NC}"

echo ""
echo "Step 5: Creating schema..."
psql -U postgres -d evidence_fortress -f backend/database/schema.sql
echo "${GREEN}✓ Schema created${NC}"

echo ""
echo "Step 6: Generating encryption key..."
ENCRYPTION_KEY=$(python3 -c "
import base64
import os
key = os.urandom(32)
print(base64.b64encode(key).decode())
")
echo "${GREEN}✓ Encryption key generated${NC}"

echo ""
echo "Step 7: Creating .env file..."
cat > .env << EOF
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=evidence_fortress
DB_USER=evidence_user
DB_PASSWORD=evidence_pass_2026

# Encryption (KEEP SECRET!)
ENCRYPTION_KEY_B64=$ENCRYPTION_KEY

# LLM APIs (optional - add your keys)
GROQ_API_KEY=your_groq_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
AWS_ACCESS_KEY=your_aws_key_here
AWS_SECRET_KEY=your_aws_secret_here

# Case
CASE_ID=SOSANA_RICO_2026
CASE_NAME=SOSANA/CRM RICO Investigation
EOF

echo "${GREEN}✓ .env file created${NC}"

echo ""
echo "Step 8: Checking Ollama..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "${GREEN}✓ Ollama is running${NC}"
    curl -s http://localhost:11434/api/tags | python3 -c "import sys,json; d=json.load(sys.stdin); print('  Models:', [m['name'] for m in d.get('models', [])])"
else
    echo "${YELLOW}⚠ Ollama not detected${NC}"
    echo "  Install from: https://ollama.com/download"
    echo "  Then run: ollama pull llama3.1:8b"
fi

echo ""
echo "======================================================================"
echo "SETUP COMPLETE!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env and add your API keys:"
echo "   - GROQ_API_KEY (get from groq.com)"
echo "   - OPENROUTER_API_KEY (optional, from openrouter.ai)"
echo ""
echo "2. Load environment:"
echo "   source .env"
echo ""
echo "3. Ingest evidence:"
echo "   python scripts/seed_from_files.py --input /path/to/evidence"
echo ""
echo "4. Start analysis:"
echo "   python -m backend.services.analysis"
echo ""
echo "======================================================================"
