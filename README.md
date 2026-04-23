<<<<<<< HEAD
# RugMuncher Intelligence Backend

> **⚠️ PROPRIETARY SOFTWARE — ALL RIGHTS RESERVED**
>
> This codebase is the confidential and proprietary intellectual property of CryptoRugMuncher. Unauthorized access, distribution, or use is strictly prohibited.

---

## What This Is

The RugMuncher Intelligence Backend is the proprietary detection engine, data pipeline, and API infrastructure that powers the RugMuncher ecosystem. It is **not open-source** and is maintained exclusively by the core development team.

This repository contains:
- Real-time rug-pull detection algorithms
- On-chain behavioral analysis engines
- Historical scam pattern databases
- Model training and inference pipelines
- Institutional-grade REST/gRPC API
- User authentication, billing, and entitlement systems

---

## Architecture at a Glance

```
┌─────────────────────────────────────────────┐
│         RugMuncher Frontend (Open)          │
│        github.com/cryptorugmuncher/         │
│           rugmuncher-intelligence           │
└──────────────────┬──────────────────────────┘
                   │ API Calls
                   ▼
┌─────────────────────────────────────────────┐
│    RugMuncher Backend (Proprietary)         │
│  ┌─────────────┐  ┌─────────────────────┐  │
│  │  API Layer  │  │  Detection Engine   │  │
│  │  FastAPI    │  │  ML/Heuristic Stack │  │
│  └──────┬──────┘  └─────────────────────┘  │
│         │                                    │
│  ┌──────┴──────┐  ┌─────────────────────┐  │
│  │  Data Layer │  │  Training Pipeline  │  │
│  │  Supabase   │  │  Feature Engineering│  │
│  │  Redis      │  │  Model Retraining   │  │
│  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────┘
=======
# 🔍 RMI System Tools

## Overview

Three production-ready system tools for the Rug Munch Intelligence (RMI) investigation platform.

## 📦 Tools Included

### 1. Evidence Processor (`tools/evidence_processor.py`)

**Purpose:** Automated extraction and processing of investigation evidence

**Features:**
- ZIP archive extraction with automatic categorization
- OCR processing for screenshots/images (78 images supported)
- Wallet address extraction from all file types
- Parallel processing for performance
- JSON export of extraction manifest

**Usage:**
```bash
# Run full pipeline
python3 /root/rmi/tools/evidence_processor.py --full

# Extract archives only
python3 /root/rmi/tools/evidence_processor.py --extract

# Process images with OCR
python3 /root/rmi/tools/evidence_processor.py --ocr

# Export wallet list for tracing
python3 /root/rmi/tools/evidence_processor.py --wallets
```

**Output:**
- `/root/rmi/tools/extracted/extraction_manifest.json` - All extracted files
- `/root/rmi/tools/extracted/pipeline_results.json` - Processing summary
- `/root/rmi/tools/extracted/wallets_for_tracing.json` - Wallet list for analysis

---

### 2. Wallet Tracer (`tools/wallet_tracer.py`)

**Purpose:** On-chain analysis and wallet forensics

**Features:**
- Multi-chain support (Solana, Ethereum, BSC, Base, Bitcoin)
- Balance and transaction queries via Helius API
- Exchange deposit detection
- Entity identification via Arkham Intelligence
- Fund flow tracing (multi-hop)
- Risk scoring algorithm
- Batch processing

**APIs Used:**
- **Helius** (Solana) - Free tier: 100k requests/month
- **Arkham** (Entity intel) - Free tier available
- **Birdeye** (Token prices) - Free tier available

**Usage:**
```bash
# Analyze single wallet
python3 /root/rmi/tools/wallet_tracer.py <wallet_address> --export

# Batch analyze from evidence results
python3 /root/rmi/tools/wallet_tracer.py --top 100 --export

# Batch analyze from file
python3 /root/rmi/tools/wallet_tracer.py --batch /path/to/wallets.json --export

# With fund flow tracing
python3 /root/rmi/tools/wallet_tracer.py <address> --trace-flows
```

**Output:**
- `/root/rmi/tools/tracing_results/wallet_analysis_YYYYMMDD_HHMMSS.json`

---

### 3. Investigation API Server (`api/investigation_server.py`)

**Purpose:** RESTful API backend with Supabase and n8n integration

**Features:**
- Investigation status endpoint
- Wallet listing with pagination
- Evidence catalog
- Search across all data
- Admin endpoints for processing triggers
- Webhook endpoints for n8n workflows
- File upload handling

**Public Endpoints:**
```
GET  /api/health                    - Health check
GET  /api/investigation/status      - Processing status
GET  /api/investigation/wallets     - List wallets (paginated)
GET  /api/investigation/wallet/:addr - Wallet details
GET  /api/investigation/evidence    - List evidence
POST /api/investigation/search      - Search evidence
```

**Admin Endpoints:**
```
POST /api/admin/investigation/process        - Trigger processing
POST /api/admin/investigation/analyze-wallets - Trigger wallet analysis
POST /api/admin/upload                       - Upload evidence
GET  /api/admin/stats                        - Detailed stats
```

**Webhook Endpoints:**
```
POST /webhook/evidence-ready   - External evidence notification
POST /webhook/n8n-callback     - n8n workflow callbacks
```

**Usage:**
```bash
# Start server
python3 /root/rmi/api/investigation_server.py

# With custom port
FLASK_PORT=8080 python3 /root/rmi/api/investigation_server.py

# Health check
curl http://localhost:5000/api/health

# Get wallets
curl http://localhost:5000/api/investigation/wallets?page=1&limit=10

# Admin trigger (requires API key)
curl -X POST http://localhost:5000/api/admin/investigation/process \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"target": "all"}'
>>>>>>> main
```

---

<<<<<<< HEAD
## For Institutional Investors & API Customers

### Full API Access — Available by License

The public frontend uses a **subset** of our detection capabilities. Institutional clients receive access to the complete intelligence stack.

#### Premium Capabilities

| Capability | Community | Developer | Institutional |
|------------|-----------|-----------|---------------|
| Basic scan results | Yes | Yes | Yes |
| Standard REST API | — | Yes | Yes |
| Raw confidence signals | — | — | Yes |
| Bulk historical data | — | — | Yes |
| Custom model training | — | — | Yes |
| Real-time threat websocket | — | — | Yes |
| SLA / dedicated support | — | — | Yes |
| White-label embedding | — | — | Yes |

#### Data Products

- **Historical Scam Dataset**: Fully labeled rug-pull events with on-chain feature extractions
- **Wallet Risk Scores**: Proprietary reputation scoring for EOAs and contract deployers
- **Sybil Cluster Feeds**: Real-time identification of coordinated attack wallets
- **Chain-Specific Models**: Fine-tuned detection for Solana, Ethereum, BSC, Base, and others

### Licensing Inquiries

To discuss enterprise licensing, data partnerships, or custom deployments:

- **Email**: biz@rugmunch.io
- **Subject**: `Institutional API — [Your Organization]`
- **Expected Response**: Within 48 business hours

Please include:
- Estimated API call volume
- Chains of interest
- Use case (exchange integration, VC due diligence, custody risk management, etc.)

---

## Security & Responsible Disclosure

If you discover a vulnerability in our backend infrastructure:

1. **Do not** open a public issue
2. Email **security@cryptorugmunch.com** with detailed reproduction steps
3. Allow 90 days for remediation before public disclosure
4. Bounty eligibility determined on a case-by-case basis

---

## For Core Developers

### Local Development Setup

```bash
cd /root/rmi/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Environment configuration lives in `app/core/config.py` and `.env` files.

### Deployment

The backend is deployed as containerized services orchestrated via Docker Compose. See `/root/rmi/docker-compose.yml` for service topology.

---

*© CryptoRugMuncher — All Rights Reserved*
=======
## 🔧 Environment Variables

Create a `.env` file in `/root`:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# n8n
N8N_WEBHOOK_URL=https://your-n8n.com/webhook/xxx

# Security
ADMIN_API_KEY=secure-random-key-here

# APIs (optional, defaults work without keys)
HELIUS_API_KEY=your-helius-key
ARKHAM_API_KEY=your-arkham-key
BIRDEYE_API_KEY=your-birdeye-key

# Server
FLASK_PORT=5000
FLASK_DEBUG=false
ALLOWED_ORIGINS=http://localhost,http://127.0.0.1
```

---

## 📁 Directory Structure

```
/root/rmi/
├── tools/
│   ├── evidence_processor.py      # Tool 1
│   ├── wallet_tracer.py           # Tool 2
│   ├── extracted/                 # Output from evidence processor
│   │   ├── extraction_manifest.json
│   │   ├── pipeline_results.json
│   │   ├── wallets_for_tracing.json
│   │   └── [categorized files]
│   └── tracing_results/           # Output from wallet tracer
│       └── wallet_analysis_*.json
├── api/
│   └── investigation_server.py    # Tool 3
├── config/                        # (future)
└── integrations/                  # (future)
```

---

## 🚀 Quick Start

### Step 1: Set up environment
```bash
# Add to your .env file
echo "ADMIN_API_KEY=dev-key-123" >> /root/.env
```

### Step 2: Run evidence processing
```bash
python3 /root/rmi/tools/evidence_processor.py --full
```

### Step 3: Analyze top wallets
```bash
python3 /root/rmi/tools/wallet_tracer.py --top 50 --export
```

### Step 4: Start API server
```bash
python3 /root/rmi/api/investigation_server.py &

# Test
curl http://localhost:5000/api/health
curl http://localhost:5000/api/investigation/status
```

---

## 📊 Integration Workflow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Evidence      │────▶│  Evidence        │────▶│  Wallet         │
│   Dumps         │     │  Processor       │     │  Tracer         │
│   (ZIP/images)  │     │  (extract/OCR)   │     │  (on-chain)     │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   n8n           │◀────│  Investigation   │◀────│  Supabase       │
│   Workflows     │     │  API Server      │     │  Database       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

---

## 🔌 API Integration Notes

### Supabase Integration
The API server uses the Supabase REST API directly:
- Tables auto-created on first use
- RLS policies should be configured
- Service key used for admin operations

### n8n Integration
Webhooks trigger n8n workflows:
- `evidence_uploaded` - New evidence received
- `evidence_processed` - Processing complete
- `wallets_analyzed` - Analysis complete

Configure your n8n workflow to listen to the webhook URL.

---

## 🛡️ Security Notes

1. **Never commit `.env` files**
2. **Rotate ADMIN_API_KEY regularly**
3. **Use HTTPS in production**
4. **Configure CORS origins properly**
5. **Enable Supabase RLS policies**
6. **Store actual passwords OFF-SERVER** (hashes only locally)

---

## 📝 Next Steps

To fully operationalize:

1. **Install Tesseract OCR** (for image processing):
   ```bash
   apt-get install tesseract-ocr
   pip install pytesseract pillow
   ```

2. **Set up Supabase tables** using schema in `/root/data/database_schema.sql`

3. **Configure n8n** workflows to process webhook events

4. **Add real API keys** for Helius/Arkham (optional, works with defaults)

5. **Set up systemd service** for API server:
   ```bash
   # See /root/config/systemd/ for example service files
   ```

---

## 🎯 Features Implemented

- ✅ ZIP extraction with categorization
- ✅ OCR with Tesseract (when installed)
- ✅ Wallet extraction from text and images
- ✅ Multi-chain wallet analysis
- ✅ Exchange detection
- ✅ Risk scoring
- ✅ RESTful API
- ✅ Supabase integration (async)
- ✅ n8n webhook triggers
- ✅ Admin authentication
- ✅ File upload endpoints

---

**Built for RMI Investigation System** 🔍
>>>>>>> main
