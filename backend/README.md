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
```

---

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
