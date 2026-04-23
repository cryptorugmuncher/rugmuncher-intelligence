# Evidence Fortress v4.0
## Privacy-First Forensic Evidence Processing System

**For: SOSANA/CRM RICO Investigation**

---

## Quick Answers to Your Questions

### Q1: Can I encrypt data going out to use free OpenRouter models?

**Short answer: No. Encryption doesn't solve the core problem.**

Here's why:

| Approach | Safe? | Why |
|----------|-------|-----|
| Encrypt addresses, send to API | ❌ **NO** | Provider logs encrypted ciphertext + your decryption key = compromised |
| Hash addresses, send hash | ❌ **NO** | Rainbow tables can reverse common addresses |
| **Pseudonymization** (our approach) | ✅ **YES** | Replace `AFXigaYu...` with `[BOTNET_SEEDER_001]` before API call |

**The OpenRouter Free Tier Problem:**

OpenRouter's free models (Gemma 4, Qwen 3.6, etc.) log prompts for:
- Training data collection
- Quality assurance
- Abuse detection
- Model improvement

Even if you encrypt the data:
1. They log the encrypted payload
2. They log your API requests (patterns, timing)
3. If your key is ever compromised, all historical logs become readable

**The Only Safe Approach:**

```python
# ❌ WRONG: Sending encrypted data
encrypted = encrypt("AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6")
send_to_openrouter(encrypted)  # Still logged!

# ✅ CORRECT: Pseudonymization
pseudonym = get_pseudonym("AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6")
# Returns: [BOTNET_SEEDER_001]
send_to_openrouter(pseudonym)  # Safe to log!
```

**Our SanitizationGateway does this automatically.**

---

### Q2: How do I build database ingestion from text files/JSON?

**Short answer: Use `scripts/seed_from_files.py`**

```bash
# Ingest all files in a directory
python scripts/seed_from_files.py --input /mnt/okcomputer/upload/ --case SOSANA_RICO_2026

# Ingest single file
python scripts/seed_from_files.py --input /path/to/transfers.csv
```

**What it does:**

1. **Hashes** every wallet address (SHA256) → lookup key
2. **Encrypts** real addresses (AES-256-GCM) → stored locally only
3. **Generates** pseudonyms → `[ENTITY_001]`, `[BOTNET_SEEDER_001]`
4. **Stores** raw evidence encrypted in `evidence_vault`
5. **Creates** sanitized transaction graph using pseudonyms only

**Supported formats:**
- Solscan transfer exports (`export_transfer_*.csv`)
- Solscan balance changes (`export_balance_change_*.csv`)
- Token holder exports (`export_token_holders_*.csv`)
- Chat logs (`*.txt`)
- JSON exports

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EVIDENCE FORTRESS v4.0                              │
│                    4-Tier Privacy-First Architecture                        │
└─────────────────────────────────────────────────────────────────────────────┘

TIER 1: INGESTION (Raw Evidence)
├── CSV exports from Solscan/Helius
├── Chat logs (Telegram, Discord)
├── JSON exports
└── Chain of custody logging

TIER 2: LOCAL PROCESSING (Contabo Server - NEVER leaves)
├── Address → SHA256 hash (lookup key)
├── Address → AES-256-GCM encryption (storage)
├── Pseudonym generation [ENTITY_001]
└── LUKS encrypted volume

TIER 3: SANITIZATION GATEWAY (Security Layer)
├── All external API calls MUST pass through
├── Raw addresses → Pseudonyms before external APIs
├── Groq ($200 credit) - FAST, doesn't log training data
├── AWS Bedrock ($200 credit) - Enterprise
└── OpenRouter FREE - ONLY with pre-sanitized data

TIER 4: EXTERNAL ANALYSIS
├── LLM pattern detection
├── Graph analysis
├── Timeline reconstruction
└── Report generation
```

---

## Database Schema

### Core Tables

| Table | Purpose | Contains Raw Addresses? |
|-------|---------|------------------------|
| `evidence_vault` | Immutable evidence storage | ✅ Encrypted (AES-256) |
| `crypto_entities` | Pseudonym registry | ❌ NO - only hashes & pseudonyms |
| `address_secrets` | Local-only encrypted addresses | ✅ Encrypted, local only |
| `transaction_graph` | Sanitized relationships | ❌ NO - pseudonyms only |
| `human_operators` | Off-chain intelligence | ❌ NO - aliases only |
| `analysis_jobs` | Cost tracking | ❌ NO - metadata only |
| `audit_logs` | Legal chain of custody | ❌ NO - actions only |

---

## Evidence Analysis Results

### Files Processed

| File | Type | Records | Key Findings |
|------|------|---------|--------------|
| `export_transfer_AFXigaYu*.csv` | Botnet seeder | 1,000 transfers | **71.4 tx/sec** - Rapid-fire seeding |
| `export_balance_change_8eVZa7b*.csv` | CRM distributor | 384 changes | Net +50K CRM tokens |
| `export_token_holders_Eme5T2s*.csv` | Token holders | 1,000 holders | Top 10 control 29.3% |
| `Marcus Aurelius(1).txt` | Chat log | 8848 addresses | Bot capabilities documented |

### Key Entities Identified

```
[BOTNET_SEEDER_001] → AFXigaYu...
  Tier: tier_2_botnet
  Role: wallet_seeder
  Evidence: 1,000 transfers in 14 seconds (71.4/sec)
  Risk Score: 0.98

[DISTRIBUTOR_009] → 8eVZa7b...
  Tier: tier_2_botnet
  Role: crm_distributor
  Evidence: 384 balance changes, 1.97% of SOSANA supply
  Risk Score: 0.92

[TREASURY_SOSANA] → Eme5T2s2HB7...
  Tier: tier_1_treasury
  Role: token_treasury
  Evidence: Token mint authority
  Risk Score: 0.95
```

---

## LLM Cost Optimization

### Routing Priority

1. **Ollama (Local)** - FREE, PRIVATE, preferred for 80% of tasks
2. **Groq** - $200 credit, fast, no training logging
3. **AWS Bedrock** - $200 credit, enterprise features
4. **OpenRouter Free** - LAST RESORT, requires pre-sanitization

### Cost Tracking

Every API call is tracked to the microdollar:

```sql
SELECT 
    llm_provider,
    SUM(actual_cost_microdollars) / 1000000.0 as total_cost
FROM analysis_jobs
GROUP BY llm_provider;
```

---

## Setup Instructions

### 1. Install Dependencies

```bash
cd /mnt/okcomputer/output/evidence_fortress
pip install -r requirements.txt
```

### 2. Setup Database

```bash
# Create PostgreSQL database
python scripts/setup_database.py
```

### 3. Configure Environment

```bash
export DB_HOST=localhost
export DB_NAME=evidence_fortress
export DB_USER=evidence_user
export DB_PASSWORD=your_password

export GROQ_API_KEY=your_groq_key
export OPENROUTER_API_KEY=your_openrouter_key  # Optional

# Generate encryption key
python -c "from backend.security.sanitization_gateway import generate_encryption_key, key_to_env_format; print(key_to_env_format(generate_encryption_key()))"
export ENCRYPTION_KEY_B64=your_generated_key
```

### 4. Ingest Evidence

```bash
python scripts/seed_from_files.py \
    --input /path/to/evidence/files \
    --case SOSANA_RICO_2026
```

---

## Security Checklist

- [x] Raw addresses never touch external APIs
- [x] All evidence encrypted at rest (AES-256-GCM)
- [x] Chain of custody logging
- [x] Audit trail for all address access
- [x] Pseudonymization before any external call
- [x] LUKS encryption for evidence volume
- [x] Cost tracking to microdollar
- [x] Local LLM preference (Ollama)

---

## File Structure

```
evidence_fortress/
├── backend/
│   ├── database/
│   │   └── schema.sql          # PostgreSQL schema
│   ├── security/
│   │   └── sanitization_gateway.py  # CRITICAL security layer
│   └── services/
│       └── llm_cost_optimizer.py    # Smart LLM routing
├── scripts/
│   ├── setup_database.py       # DB initialization
│   └── seed_from_files.py      # Evidence ingestion
├── config/
│   └── settings.py             # Configuration
├── evidence/
│   ├── raw/                    # Original files (encrypted)
│   ├── processed/              # Parsed data
│   └── vault/                  # LUKS encrypted storage
├── requirements.txt
└── README.md                   # This file
```

---

## Legal Compliance

- **Chain of Custody**: Every action logged with timestamp
- **Tamper Detection**: SHA256 hashes for all evidence
- **Access Control**: Role-based address access
- **Retention**: 7-year audit log retention
- **Export**: Legal-grade report generation

---

## Next Steps

1. ✅ Review this README
2. ✅ Set up PostgreSQL database
3. ✅ Run `setup_database.py`
4. ✅ Configure environment variables
5. ✅ Ingest your evidence files
6. ✅ Start analysis with local Ollama
7. ✅ Escalate to Groq for complex tasks

---

**Built for the SOSANA/CRM RICO Investigation**
**Privacy First. Legal Grade. Cost Optimized.**
