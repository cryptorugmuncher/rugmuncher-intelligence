# Rug Munch Intelligence (RMI) - Frontend Features Proposed

**Source:** Chat conversations with Gemini about building the investigation platform
**Context:** These are retail/user-facing features proposed for the RMI app

---

## Core Feature Categories

### 1. LIBRARIAN SYSTEM (Document Management)

**Auto-Categorization Engine**
- Scans document content (ignores chaotic filenames)
- Generates clean titles from content using LLM
- Creates SHA-256 fingerprints for deduplication
- Tags documents by type (chat logs, CSVs, images, PDFs)

**Smart Titles**
- Converts `chat(1).txt` → `Telegram_Log_Wallet_0xABC_Oct12`
- Auto-generates descriptive names from first 500 words

---

### 2. TELEGRAM COMMAND CENTER (Bot Interface)

**Button-Based Navigation**
- [📄 View Binance Deposit Logs]
- [🕵️ Run DeepSeek Verification]
- [🔗 Map Connections]
- [⚖️ Request Claude Cross-Exam]

**Commands**
- `/case {name}` - Load investigation case
- `/suspects` - View suspect directory
- `/evidence` - Browse categorized evidence

---

### 3. SUSPECT DIRECTORY (Entity Management)

**Human Profile Cards**
- Aliases (Telegram, Discord, Twitter)
- Known wallets + burner count
- Estimated timezone from activity
- Linguistic fingerprint (slang, typos)
- Behavioral notes
- Status tracking

---

### 4. INVESTIGATION TOOLS

#### Ghost Scanner (Closed Account Analysis)
- [👻 Scan Ghost Wallet] button
- Traces to genesis transaction
- Identifies original funding source
- Bypasses burner wallet obfuscation

#### Money Trail Tracker
- Visual flow diagrams
- CEX identification
- Mixer detection

#### Cross-Project Nexus Scanner
- Links projects via shared infrastructure
- Contract bytecode comparison
- Shared deployer detection

#### Manipulation Detector
- Wash trading detection
- Circular transaction detection
- Bot trading signatures

#### Infrastructure Harvester
- Domain/IP extraction
- WHOIS lookups
- Cross-project server sharing

---

### 5. FINANCIAL ANALYSIS

#### Fee Siphon Audit
- Detects hidden fee extraction from pools
- Scans for CollectFee instructions

#### Pre-Bonding Audit
- Finds insider allocations before launch
- Detects zero-cost receives

#### Closed Account Checker
- Drained & abandoned wallets
- Burned token accounts (Solana)
- Frozen/blacklisted accounts

---

### 6. AI VERIFICATION

**Multi-Model Hierarchy**
- Librarian (Local): Document categorization
- Verifier (DeepSeek): Evidence analysis
- Auditor (Claude): Quality control

**Claude Cross-Exam**
- Hostile defense attorney role
- Finds evidence holes
- Suggests missing queries

---

### 7. VISUALIZATION & REPORTING

#### Network Graph Generator
- Wallet cluster visualization
- Fund flow spiderweb
- Delivered as images to Telegram

#### Final Indictment Generator
- Prosecutorial narrative
- Timeline + connections
- Legal framework (RICO)

#### Legal Document Generator
- Auto-draft subpoenas
- Exchange freeze requests

---

## Database Tables Needed

```sql
-- Suspect profiles
CREATE TABLE rmi_suspects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    suspect_id TEXT UNIQUE NOT NULL,
    aliases TEXT[] DEFAULT '{}',
    estimated_timezone TEXT,
    behavioral_fingerprint JSONB,
    status TEXT DEFAULT 'UNDER_INVESTIGATION',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Investigation sessions
CREATE TABLE rmi_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL,
    case_id TEXT REFERENCES investigation_cases(case_id),
    session_data JSONB DEFAULT '{}',
    vault_data JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Analysis runs
CREATE TABLE rmi_analysis_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES rmi_sessions(id),
    analysis_type TEXT,
    target_address TEXT,
    results JSONB,
    confidence INTEGER,
    run_at TIMESTAMP DEFAULT NOW()
);

-- Syndicate wallets
CREATE TABLE rmi_syndicate_wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    syndicate_name TEXT,
    role TEXT,
    wallet_address TEXT,
    chain TEXT DEFAULT 'solana',
    linked_cases TEXT[]
);
```

---

## API Keys Required

- Helius (Solana RPC)
- Arkham (Entity labeling)
- Solscan (Contract analysis)
- MistTrack (Risk scoring)
- OpenRouter (AI models)
- Telegram Bot Token
