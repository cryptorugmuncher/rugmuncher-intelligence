# Evidence Fortress v4.0 - Build Summary

## What Was Built

A complete privacy-first forensic evidence processing system for the SOSANA/CRM RICO investigation.

---

## Your Questions Answered

### Q1: Can I encrypt data to use free OpenRouter models?

**Answer: No - encryption doesn't solve the problem.**

OpenRouter's free tiers log prompts for training. Even encrypted data is logged, and if your key is ever compromised, all historical logs become readable.

**The Solution (Implemented):**
- **Pseudonymization**: Replace `AFXigaYu...` with `[BOTNET_SEEDER_001]` BEFORE any API call
- **SanitizationGateway**: All external APIs must pass through this security layer
- **Local LLM Priority**: Ollama (free, private) for 80% of tasks
- **Groq Escalation**: $200 credit, fast, doesn't log training data

See `backend/security/sanitization_gateway.py` for implementation.

---

### Q2: How do I build database ingestion from text files/JSON?

**Answer: Use the provided ingestion pipeline.**

```bash
# Ingest all evidence files
python scripts/seed_from_files.py --input ./evidence/raw --case SOSANA_RICO_2026
```

**What it does:**
1. Reads CSV/TXT/JSON files
2. SHA256 hashes all addresses (lookup key)
3. AES-256-GCM encrypts real addresses (local storage only)
4. Generates pseudonyms `[ENTITY_001]`, `[BOTNET_SEEDER_001]`
5. Stores encrypted evidence in `evidence_vault`
6. Creates sanitized transaction graph

See `scripts/seed_from_files.py` for implementation.

---

## Files Created

### Core System (11 files)

```
evidence_fortress/
├── README.md                          # Main documentation
├── ANALYSIS_REPORT.md                 # Evidence analysis results
├── BUILD_SUMMARY.md                   # This file
├── requirements.txt                   # Python dependencies
├── quickstart.sh                      # One-command setup
│
├── backend/
│   ├── database/
│   │   └── schema.sql                 # PostgreSQL schema (7 tables)
│   ├── security/
│   │   └── sanitization_gateway.py    # CRITICAL security layer
│   └── services/
│       ├── llm_cost_optimizer.py      # Smart LLM routing
│       └── analysis.py                # Pattern detection
│
├── config/
│   └── settings.py                    # Configuration management
│
└── scripts/
    ├── setup_database.py              # DB initialization
    └── seed_from_files.py             # Evidence ingestion
```

### Evidence Files (9 files analyzed)

```
evidence/raw/
├── export_transfer_AFXigaYu*.csv      # Botnet seeder (1,000 transfers)
├── export_balance_change_8eVZa7b*.csv # CRM distributor (384 changes)
├── export_token_holders_Eme5T2s*.csv  # SOSANA holders (1,000)
├── export_transfer_Cx5qTE*.csv        # Intermediary wallet
└── Marcus Aurelius(1).txt             # Chat log (bot capabilities)
```

---

## Key Findings from Evidence Analysis

### 1. Botnet Seeder Identified

**Entity:** `[BOTNET_SEEDER_001]` (AFXigaYu...)

```
1,000 transfers in 14 seconds = 71.4 transfers/second
677 unique recipient wallets
Amount: 1 SOL per transfer (~$0.0017)
```

**Assessment:** Automated botnet funding operation

---

### 2. CRM Distributor Mapped

**Entity:** `[DISTRIBUTOR_009]` (8eVZa7b...)

```
384 balance changes over 4.5 months
Net: +50,001.89 CRM tokens
SOSANA holdings: 19.7M (1.97% of supply, rank #10)
```

**Assessment:** Key distribution node in network

---

### 3. Token Concentration Risk

```
Top 10 holders: 29.3% of supply
Top 50 holders: 69.8% of supply
```

**Assessment:** Highly concentrated, manipulation risk

---

### 4. Bot Operation Documented

**Source:** Marcus Aurelius chat log

**Capabilities:**
- Auto-scan trending tokens
- Wallet tracking
- Bundle/sniper detection
- Pattern recognition
- Social sentiment monitoring
- LP movement alerts
- Rug autopsy

**Assessment:** Sophisticated market manipulation toolkit

---

## Database Schema

### 7 Core Tables

| Table | Purpose | Raw Addresses? |
|-------|---------|----------------|
| `evidence_vault` | Immutable evidence | ✅ Encrypted |
| `crypto_entities` | Pseudonym registry | ❌ Hashes only |
| `address_secrets` | Local-only storage | ✅ Encrypted |
| `transaction_graph` | Sanitized graph | ❌ Pseudonyms |
| `human_operators` | Off-chain intel | ❌ Aliases only |
| `analysis_jobs` | Cost tracking | ❌ Metadata |
| `audit_logs` | Chain of custody | ❌ Actions only |

---

## LLM Cost Optimization

### Routing Priority

1. **Ollama (Local)** - FREE, PRIVATE, preferred
2. **Groq** - $200 credit, fast, no training logs
3. **AWS Bedrock** - $200 credit, enterprise
4. **OpenRouter Free** - LAST RESORT, requires pre-sanitization

### Cost Tracking

Every API call tracked to the microdollar:

```sql
SELECT 
    llm_provider,
    SUM(actual_cost_microdollars) / 1000000.0 as total_cost
FROM analysis_jobs
GROUP BY llm_provider;
```

---

## Quick Start

### 1. Setup (One Command)

```bash
cd /mnt/okcomputer/output/evidence_fortress
./quickstart.sh
```

### 2. Configure

```bash
# Edit .env with your API keys
nano .env

source .env
```

### 3. Ingest Evidence

```bash
python scripts/seed_from_files.py --input ./evidence/raw
```

### 4. Run Analysis

```bash
# Analyze specific entity
python -m backend.services.analysis --entity [BOTNET_SEEDER_001]

# Analyze all high-risk entities
python -m backend.services.analysis --all
```

---

## Security Checklist

- [x] Raw addresses never touch external APIs
- [x] AES-256-GCM encryption at rest
- [x] SHA-256 hashing for lookups
- [x] Pseudonymization before external calls
- [x] Chain of custody logging
- [x] Audit trail for address access
- [x] Cost tracking to microdollar
- [x] Local LLM preference

---

## Next Steps

1. ✅ Review this summary
2. ✅ Read `README.md` for detailed documentation
3. ✅ Review `ANALYSIS_REPORT.md` for evidence findings
4. ⏳ Set up PostgreSQL database
5. ⏳ Run `quickstart.sh`
6. ⏳ Add your API keys to `.env`
7. ⏳ Ingest evidence files
8. ⏳ Start pattern analysis

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     EVIDENCE FORTRESS v4.0                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  TIER 1: INGESTION                                              │
│  ├── CSV/TXT/JSON files                                         │
│  └── Chain of custody logging                                   │
│                              ↓                                  │
│  TIER 2: LOCAL PROCESSING (Contabo Server)                      │
│  ├── Address → SHA256 hash (lookup key)                         │
│  ├── Address → AES-256 encryption (local storage)               │
│  └── Pseudonym generation [ENTITY_001]                          │
│                              ↓                                  │
│  TIER 3: SANITIZATION GATEWAY                                   │
│  ├── All external APIs MUST pass through                        │
│  ├── Groq ($200 credit) - FAST, private                        │
│  ├── AWS Bedrock ($200 credit) - enterprise                    │
│  └── OpenRouter FREE - ONLY with pre-sanitized data            │
│                              ↓                                  │
│  TIER 4: EXTERNAL ANALYSIS                                      │
│  ├── Pattern detection                                          │
│  ├── Graph analysis                                             │
│  └── Report generation                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Support

For questions or issues:
1. Check `README.md` for detailed documentation
2. Review `ANALYSIS_REPORT.md` for evidence findings
3. Examine source code comments for implementation details

---

**Built for:** SOSANA/CRM RICO Investigation  
**Version:** 4.0  
**Date:** 2026-04-06
