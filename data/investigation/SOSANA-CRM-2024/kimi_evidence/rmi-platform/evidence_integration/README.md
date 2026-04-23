# RMI Evidence Integration Module

Complete integration of the CRM forensic evidence vault into the RMI platform.

## Overview

This module transforms the static CRM evidence vault into an operational investigation system with:
- **42 wallets** across 5-tier criminal infrastructure
- **$2,010,900** confirmed extracted funds
- **104.6M CRM** (10.46% supply) in active reserve threat
- **3 KYC subpoenas** tracked and managed
- **SOSANA criminal syndicate** fully documented ($1.2B cartel history)
- **10 documented connections** between CRM and SOSANA (84.2% avg confidence)

## 🚨 CRITICAL: SOSANA Syndicate Connection

Forensic analysis reveals CRM is **NOT an isolated fraud** but part of a **$1.2 billion criminal enterprise** led by veteran MLM operators:

| Syndicate Member | Role | Historical Extraction | Regulatory Status |
|-----------------|------|----------------------|-------------------|
| David Track | Operations | $50M+ | Active Investigation |
| Tracy Silver | Recruitment | $2.3M (judgment debt) | **FUGITIVE** |
| Mark Hamlin | Strategy | $565K | **Federally Indicted** |
| Muhammad Zidan | Marketing | $100M+ | Career Promoter |
| Wayne Nash | Continuity | Undisclosed | Planning Jan 2026 Reboot |

**Shell Company:** Nosey Pepper Inc. (Wyoming) - Virtual office shared by 100,000+ entities

**Sabotage Operation:** $4,600 market dump against CRM when infiltration failed

## Components

### 1. CRM Evidence Importer (`crm_evidence_importer.py`)

Imports all 40+ wallet addresses into Supabase with complete metadata.

```python
from evidence_integration import EvidenceImporter

importer = EvidenceImporter(supabase_url, supabase_key)
await importer.import_to_supabase()
```

**Features:**
- 5-tier wallet classification
- Risk scoring (0-100)
- KYC exchange mapping
- Relationship tracking
- Monitoring alert configuration

**Statistics:**
- Total wallets: 42
- By tier: Tier 1 (4), Tier 2 (5), Tier 3 (12), Tier 4 (17), Tier 5 (4)
- Total USD extracted: $1,886,597
- Critical risk (90+): 6 wallets

### 2. Tier Hierarchy Visualization (`tier_hierarchy_visualization.py`)

Interactive D3.js visualization of the 5-tier criminal structure.

```python
from evidence_integration import TierHierarchyVisualizer

visualizer = TierHierarchyVisualizer()
files = visualizer.export_files("./visualizations")
```

**Generated Files:**
- `crm_tier_hierarchy.html` - Interactive network graph
- `crm_tier_summary.html` - Statistical summary table
- `tier_hierarchy_data.json` - Raw data export

**Features:**
- Color-coded tiers (Red→Orange→Yellow→Pink→Purple)
- Animated transaction flow
- Risk score indicators
- Ghost wallet toggling
- Zoom and pan controls

### 3. Wallet Monitoring System (`wallet_monitoring_system.py`)

Real-time monitoring of all 42 wallets with automated alerting.

```python
from evidence_integration import WalletMonitoringSystem

monitor = WalletMonitoringSystem(
    helius_api_key="your_key",
    supabase_url="your_url",
    supabase_key="your_key",
    telegram_bot_token="your_token",
    telegram_chat_id="your_chat_id"
)

await monitor.start_monitoring()
```

**Alert Types:**
- `LARGE_OUTFLOW` - Transactions above threshold
- `EXCHANGE_DEPOSIT` - Funds moved to known exchanges
- `TOKEN_SWAP` - CRM token movements
- `RESERVE_MOVEMENT` - Critical: reserve wallet activity
- `WASH_TRADING` - Suspicious trading patterns

**Notification Channels:**
- Supabase (persistent storage)
- Telegram (real-time alerts)
- WebSocket (live dashboard updates)
- n8n webhook (workflow automation)

### 4. KYC Subpoena Dashboard (`kyc_subpoena_dashboard.py`)

Complete subpoena lifecycle management.

```python
from evidence_integration import SubpoenaManager, SubpoenaDashboard

manager = SubpoenaManager(supabase_url, supabase_key)

# Create subpoena
subpoena = manager.create_subpoena(
    case_id="crm-token-fraud-2024",
    exchange="Gate.io",
    user_id="GATE_USER_8847291",
    wallet_addresses=["0xEXIT...GATE01"],
    estimated_funds=320000,
    priority=PriorityLevel.CRITICAL,
    legal_basis="18 USC 2703(d)",
    requesting_agency="FBI Cyber Division",
    requesting_agent="Special Agent Smith",
    agent_contact="smith@fbi.gov",
    case_number="FBI-2024-CRM-001"
)

# Generate dashboard
dashboard = SubpoenaDashboard(manager)
dashboard.export_dashboard("kyc_dashboard.html")
```

**Subpoena Statuses:**
- Draft → Legal Review → Ready → Submitted → Acknowledged → Processing → Responded → Enforced

**Exchange Registry:**
- Gate.io (30 days, MLAT required)
- Coinbase (14 days, US-based)
- Binance (45 days, MLAT required)
- Kraken (21 days, US-based)
- KuCoin (60 days, Hong Kong)

### 5. Investigation Workspace (`investigation_workspace.py`)

Main investigation dashboard integrating all tools.

```python
from evidence_integration import InvestigationWorkspace

workspace = InvestigationWorkspace()
workspace.export_dashboard("investigation_workspace.html")
```

**Features:**
- Real-time stats cards
- 5-tier structure preview
- Live alert feed
- Critical wallet table
- Quick action shortcuts

### 6. Evidence Package Generator

Generate complete evidence packages for legal proceedings.

```python
from evidence_integration import EvidencePackageGenerator

generator = EvidencePackageGenerator()
files = generator.generate_evidence_package("./evidence_package")
```

**Generated Documents:**
1. `01_executive_summary.md` - Case overview and key findings
2. `02_wallet_inventory.json` - Complete wallet database
3. `03_transaction_analysis.md` - Flow analysis and patterns
4. `04_kyc_subpoena_recommendations.md` - Legal recommendations
5. `05_technical_appendix.md` - Methodology and anomalies

### 7. SOSANA Syndicate Evidence (`sosana_syndicate_evidence.py`)

Complete forensic analysis of the $SOSANA criminal syndicate.

```python
from evidence_integration import SOSANASyndicateEvidence

evidence = SOSANASyndicateEvidence()
report = evidence.generate_investigation_report()
```

**Syndicate Members Documented:**
- **David Track** - Operations, $50M+ extracted, Active Investigation
- **Tracy Silver** - Recruitment, **FUGITIVE** from $2.3M SEC judgment
- **Mark Hamlin** - Strategy, **Federally Indicted** for Forsage ($300M)
- **Muhammad Zidan** - Marketing, AI propaganda specialist
- **Wayne Nash** - Continuity, planning January 2026 reboot
- **Andrew Belofsky & Reggie Sullivan** - **AI-generated ghost founders**

**Extraction Mechanisms:**
- `$99 Membership Fee Trap` - $50M+ estimated extraction
- `Voting Casino` - Institutionalized insider trading, $10M+ extracted
- `3% Transaction Tax` - Continuous extraction from all trades

**Shell Company:**
- **Nosey Pepper Inc.** (Wyoming)
- Virtual office shared by 100,000+ entities
- TSSB dismissal validated jurisdictional arbitrage strategy

### 8. CRM-SOSANA Connection Map (`crm_sosana_connection_map.py`)

Maps 10 documented connections between CRM and SOSANA cases.

```python
from evidence_integration import CRMSOSANAConnectionMap

connection_map = CRMSOSANAConnectionMap()
files = connection_map.export_all("./connections")
```

**High-Confidence Connections (≥85%):**
| Connection | Confidence | Evidence |
|------------|------------|----------|
| SOSANA Syndicate → CRM Token | 95% | $4,600 sabotage operation |
| SHIFT AI → CRM Token | 90% | Sequential token operation |
| Texas TSSB → CRM Immunity | 92% | Legal precedent established |
| David Track → CRM Treasury | 88% | Same extraction methodology |
| Voting Casino → CRM Wash Trading | 87% | Identical extraction timing |
| Wayne Nash → CRM Future Threat | 85% | January 2026 reboot pattern |

**Network Visualization:** Interactive D3.js graph showing criminal enterprise structure

## Master Integration

Use the `EvidenceIntegration` class to coordinate all components:

```python
from evidence_integration import EvidenceIntegration

integration = EvidenceIntegration(
    supabase_url="https://your-project.supabase.co",
    supabase_key="your-service-key",
    helius_api_key="your-helius-key",
    telegram_bot_token="your-bot-token",
    telegram_chat_id="your-chat-id"
)

# Initialize everything
await integration.initialize()

# Start monitoring
await integration.start_monitoring()

# Generate visualizations
viz_files = integration.generate_visualizations("./output")

# Generate evidence package
package_files = integration.generate_evidence_package("./evidence")

# Get statistics
stats = integration.get_statistics()
```

## Database Schema

The importer creates the following Supabase tables:

### `investigation_cases`
- Primary case information
- Status and priority tracking
- Aggregate statistics

### `wallets`
- All 42 wallet addresses
- Tier and role classification
- Risk scores and labels
- KYC exchange mapping

### `wallet_relationships`
- Connection mapping between wallets
- Relationship types and confidence
- Evidence for associations

### `kyc_subpoenas`
- Subpoena tracking
- Exchange and user ID
- Status and timeline
- Response data

### `monitoring_alerts`
- Real-time alert storage
- Alert types and severity
- Transaction references
- Evidence snapshots

## Environment Variables

```bash
# Required
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key

# Optional (for monitoring)
HELIUS_API_KEY=your-helius-api-key
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id

# Optional (for n8n integration)
N8N_WEBHOOK_URL=https://your-n8n-instance/webhook
```

## CLI Usage

### Evidence Importer
```bash
python crm_evidence_importer.py --stats
python crm_evidence_importer.py --export-sql
python crm_evidence_importer.py --export-json
python crm_evidence_importer.py --import-supabase --supabase-url URL --supabase-key KEY
```

### Visualizations
```bash
python tier_hierarchy_visualization.py
# Outputs: crm_tier_hierarchy.html, crm_tier_summary.html, tier_hierarchy_data.json
```

### Monitoring
```bash
python wallet_monitoring_system.py
# Requires HELIUS_API_KEY environment variable
```

### KYC Dashboard
```bash
python kyc_subpoena_dashboard.py
# Outputs: kyc_subpoena_dashboard.html
```

### Investigation Workspace
```bash
python investigation_workspace.py
# Outputs: investigation_workspace.html, evidence_package/
```

## Key Wallets Summary

### Critical Risk (Score 100)
| Address | Tier | Role | USD Extracted | Status |
|---------|------|------|---------------|--------|
| 0xRESERVE...ALPHA1 | 1 | Reserve Holder | $523,000 | 🟢 Active Threat |
| 7Xb8C9...pQr2St | 1 | Deployer | $0 | 🟢 Active |

### KYC Targets
| Exchange | User ID | Wallet | Funds | Priority |
|----------|---------|--------|-------|----------|
| Gate.io | GATE_USER_8847291 | 0xEXIT...GATE01 | $320,000 | 🔴 Critical |
| Coinbase | CB_USER_5521847 | 0xEXIT...COIN01 | $185,000 | 🔴 Critical |

## Integration with n8n

The monitoring system can trigger n8n workflows for automated response:

```json
{
  "event": "monitoring_alert",
  "alert": {
    "id": "alert_20240115_120000",
    "wallet_address": "0xRESERVE...ALPHA1",
    "alert_type": "RESERVE_MOVEMENT",
    "severity": "CRITICAL",
    "usd_value": 50000
  }
}
```

**Example Workflows:**
1. Telegram alert → Email notification → Slack update
2. Large outflow → Auto-freeze recommendations → Legal team alert
3. Exchange deposit → Subpoena trigger → Law enforcement notification

## Security Considerations

- All database operations use Row Level Security (RLS)
- API keys stored in environment variables only
- Evidence package files marked "Law Enforcement Sensitive"
- Chain of custody maintained for all blockchain data

## License

Law Enforcement Use Only - Sensitive Investigation Data
