"""
Omega Forensic V5 - UPDATED Wallet Intelligence
================================================
New wallet data integrated from forensic analysis.
Updated with latest on-chain balances and connections.
"""

from forensic.wallet_database import WalletRecord, WalletCategory, EvidenceTier
from typing import List, Dict

# === UPDATED WALLET INTELLIGENCE (March 2026) ===

# TIER 0: ROOT FUNDING
TIER_0_WALLETS = [
    WalletRecord(
        address="CNSob1LwXvDRmjioxyjm78tDb2S7nzFK6K8t3VmuhKpn",
        category=WalletCategory.ROOT_FUNDER,
        evidence_tier=EvidenceTier.TIER_1_DIRECT,
        labels=["ROOT_FUNDER", "MOONPAY_KYC", "CLEAN_ON_RAMP", "TIER_0"],
        balance_crm=0,
        balance_sol=0.5,  # Self-funded via DEXs
        first_seen="2025-08-10",
        last_seen="2025-12-31",
        connected_wallets=["EQ2E92SS64j4uh3UxfG6bFHwq2cbj6YMn8kw9Pm3T4ew"],
        cross_project_affiliations=["SOSANA", "CRM"],
        kyc_vectors=[{"type": "moonpay", "confidence": "high", "entity": "MoonPay"}],
        evidence_refs=["MOONPAY_RECEIPT_001", "SOLSCAN_TX_001"],
        notes="Root funder via MoonPay. Clean retail on-ramp. Skeleton wallet after initial distribution. KYC vector exists."
    ),
    WalletRecord(
        address="EQ2E92SS64j4uh3UxfG6bFHwq2cbj6YMn8kw9Pm3T4ew",
        category=WalletCategory.BRIDGE_NODE,
        evidence_tier=EvidenceTier.TIER_2_STRONG,
        labels=["RELAY_NODE", "TIER_0_LINK", "ENTRY_COORDINATOR"],
        balance_crm=0,
        balance_sol=2.0,
        first_seen="2025-08-15",
        last_seen="2026-03-01",
        connected_wallets=["CNSob1LwXvDRmjioxyjm78tDb2S7nzFK6K8t3VmuhKpn", "HxyXAE1PHQsh6iLj3t8MagpFovmR7yk76PEADmTKeVfi"],
        cross_project_affiliations=["SOSANA"],
        evidence_refs=["HELIUS_RELAY_ANALYSIS"],
        notes="Relay node linking root entry to coordinator. Bridges Tier 0 to operational tiers."
    ),
]

# TIER 1: SENIOR COMMAND TREASURIES
TIER_1_WALLETS = [
    WalletRecord(
        address="ASTyfSima4LLAdDgoFGkgqoKowG1LZFDr9fAQrg7iaJZ",
        category=WalletCategory.TREASURY_COMMAND,
        evidence_tier=EvidenceTier.TIER_1_DIRECT,
        labels=["NUCLEAR_TREASURY", "PAYMASTER", "PBTC_CONTROLLER", "TIER_1", "$5.8M"],
        balance_crm=0,
        balance_sol=34445.0,  # 34,445 SOL
        first_seen="2025-09-10",
        last_seen="2026-03-28",
        connected_wallets=["8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj", "DojAziGhpLddzSPTCsCvp577wkP9N6AtVc87HJqihcZd"],
        cross_project_affiliations=["SHIFT_AI", "CRM", "SOSANA"],
        kyc_vectors=[{"type": "cex_connection", "confidence": "medium", "notes": "MEXC linked"}],
        evidence_refs=["ASTYFIMA_TREASURY_001", "PBTC_DISTRIBUTION_LOG"],
        notes="Nuclear treasury with 34,445 SOL (~$5.8M). Paymaster for both SHIFT AI and CRM operations. Controls 42,997 PBTC. Senior command."
    ),
    WalletRecord(
        address="H8sMJSCQxfKiFTCfDR3DUMLPwcRbM61LGFJ8N4dK3WjS",
        category=WalletCategory.TREASURY_COMMAND,
        evidence_tier=EvidenceTier.TIER_1_DIRECT,
        labels=["PARALLEL_TREASURY", "ACTIVE_BURST", "TIER_1", "$6.7M"],
        balance_crm=0,
        balance_sol=39828.0,  # 39,828 SOL
        first_seen="2025-09-15",
        last_seen="2026-03-28",
        connected_wallets=["8VTFvhQ5C8aGvQbXoRzKpLcM3dWnJ7sYtE2iU9oP4hA1", "CCyYKtnsnkkktZw9KuUrdRWZ4qv9rn3pcNB3LouFMY5Q"],
        cross_project_affiliations=["CRM", "SOSANA"],
        evidence_refs=["H8S_BURST_ANALYSIS_001"],
        notes="Parallel treasury with 39,828 SOL (~$6.7M). Active burst pattern: 20 txs in 4 minutes on March 28. Live coordination."
    ),
    WalletRecord(
        address="F7p3dFrjRTbtRp8FRF6qHLomXbKRBzpvBLjtQcfcgmNe",
        category=WalletCategory.TREASURY_COMMAND,
        evidence_tier=EvidenceTier.TIER_2_STRONG,
        labels=["SECONDARY_TREASURY", "TIER_1", "$620K"],
        balance_crm=0,
        balance_sol=5140.0,  # 5,140 SOL
        first_seen="2025-10-01",
        last_seen="2026-03-25",
        connected_wallets=["AHXDVNdFAaMrBMnSiBLQT6MGsvPS4aSne5FV7DSP4BWt"],
        cross_project_affiliations=["CRM"],
        evidence_refs=["F7P3D_TREASURY_001"],
        notes="Secondary treasury with 5,140 SOL (~$620K). Funds router operations."
    ),
    WalletRecord(
        address="A77HErqtfN1hLLpvZ9pCtu66FEtM8BveoaKbbMoZ4RiR",
        category=WalletCategory.TREASURY_COMMAND,
        evidence_tier=EvidenceTier.TIER_1_DIRECT,
        labels=["MASTER_CONTROLLER", "TIER_0_ROOT", "$18M", "URGENT"],
        balance_crm=0,
        balance_sol=100000.0,  # Estimated ~100K SOL equivalent
        first_seen="2025-08-01",
        last_seen="2026-03-28",
        connected_wallets=["ASTyfSima4LLAdDgoFGkgqoKowG1LZFDr9fAQrg7iaJZ", "H8sMJSCQxfKiFTCfDR3DUMLPwcRbM61LGFJ8N4dK3WjS"],
        cross_project_affiliations=["SOSANA", "CRM", "SHIFT_AI"],
        evidence_refs=["A77H_MASTER_TREASURY"],
        notes="MASTER CONTROLLER. $18M+ in SOL/USDT/USDC + 794 pump tokens. Assets moving NOW. Root of entire operation."
    ),
]

# TIER 2: SECONDARY ROUTERS
TIER_2_WALLETS = [
    WalletRecord(
        address="AHXDVNdFAaMrBMnSiBLQT6MGsvPS4aSne5FV7DSP4BWt",
        category=WalletCategory.BRIDGE_NODE,
        evidence_tier=EvidenceTier.TIER_2_STRONG,
        labels=["PROCEEDS_COLLECTOR", "TIER_2", "212_SOL"],
        balance_crm=0,
        balance_sol=212.0,
        first_seen="2025-11-01",
        last_seen="2026-03-28",
        connected_wallets=["F7p3dFrjRTbtRp8FRF6qHLomXbKRBzpvBLjtQcfcgmNe", "8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj"],
        cross_project_affiliations=["CRM"],
        evidence_refs=["AHXD_ROUTER_001"],
        notes="Proceeds collector. 212 SOL + 44 tokens. Variable balance based on extraction timing."
    ),
    WalletRecord(
        address="DojAziGhpLddzSPTCsCvp577wkP9N6AtVc87HJqihcZd",
        category=WalletCategory.PAYROLL_DISTRIBUTOR,
        evidence_tier=EvidenceTier.TIER_1_DIRECT,
        labels=["PAYMENT_PROCESSOR", "PBTC_DISTRIBUTOR", "91%_PBTC_SUPPLY", "TIER_2"],
        balance_crm=0,
        balance_sol=500.0,
        first_seen="2025-06-01",
        last_seen="2026-03-01",
        connected_wallets=["ASTyfSima4LLAdDgoFGkgqoKowG1LZFDr9fAQrg7iaJZ", "8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj"],
        cross_project_affiliations=["SOSANA", "PBTC"],
        evidence_refs=["DOJAZI_PBTC_DIST_001", "JUNE_2025_DISTRIBUTION"],
        notes="Payment processor. Distributed 51,285 PBTC in June 2025. Controls 91% of PBTC supply. Internal compensation/laundering."
    ),
]

# TIER 3: BRIDGE WALLETS (CRITICAL LINKAGE)
TIER_3_WALLETS = [
    WalletRecord(
        address="8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj",
        category=WalletCategory.BRIDGE_NODE,
        evidence_tier=EvidenceTier.TIER_1_DIRECT,
        labels=["PRIMARY_BRIDGE", "SMOKING_GUN", "CRM_PBTC_NEXUS", "TIER_3", "19.7M_CRM", "73K_PBTC"],
        balance_crm=19700000.0,  # 19.7M CRM
        balance_sol=45.0,
        first_seen="2025-08-25",
        last_seen="2026-03-28",
        connected_wallets=[
            "HLnpSz9h2S4hiLQ4uN3vGYAHJqDmbFCwkx9prSXkdPMc",
            "F4HGHWyaCvDkUF88svvCHhSMpR9YzHCYSNmojaKQtRSB",
            "ASTyfSima4LLAdDgoFGkgqoKowG1LZFDr9fAQrg7iaJZ",
            "DojAziGhpLddzSPTCsCvp577wkP9N6AtVc87HJqihcZd",
            "7abBmGf4HNu3UXsanJc7WwAPW2PgkEb9hwrFKwCySvyL"
        ],
        cross_project_affiliations=["CRM", "PBTC", "SOSANA", "SHIFT_AI"],
        evidence_refs=[
            "8EVZA_BRIDGE_001",
            "RXEMcfjDJ7Y6BM4oorDr6BC2TC38Tnf1DnYATBZQ4CipcQJupwxLM3AHkqbCkpm2H7wLr8QHEKvRyLMeooby8VR"
        ],
        notes="SMOKING GUN: Primary bridge between SOSANA (PBTC) and CRM operations. 19.7M CRM + 73,574 PBTC. Sent 1M CRM to 7abBmGf4H (Signature verified). Multi-token hub."
    ),
    WalletRecord(
        address="DLHnb1yt6DMx2PCEuTniiTPfoM4EuTfuTqT8jRfdw9P8",
        category=WalletCategory.HOSTAGE_BAG,
        evidence_tier=EvidenceTier.TIER_2_STRONG,
        labels=["DORMANT_VOLCANO", "CORE_CLUSTER_LEADER", "TIER_3", "104.6M_CRM", "237M_GAS"],
        balance_crm=104600000.0,  # 104.6M CRM
        balance_sol=50.0,
        first_seen="2025-09-01",
        last_seen="2026-03-28",
        connected_wallets=["8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj"],
        cross_project_affiliations=["CRM", "GAS"],
        evidence_refs=["DLHNB_DORMANT_VOLCANO"],
        notes="DORMANT VOLCANO: Core cluster leader. 104.6M CRM + 237M GAS. Largest single CRM concentration. Routing hub for CRM/GAS."
    ),
    WalletRecord(
        address="F4HGHWyaCvDkUF88svvCHhSMpR9YzHCYSNmojaKQtRSB",
        category=WalletCategory.TREASURY_COMMAND,
        evidence_tier=EvidenceTier.TIER_2_STRONG,
        labels=["SOSANA_TREASURY", "SOSANA_V2", "ROOT_CONTROLLER", "TIER_3"],
        balance_crm=5000000.0,  # 5M CRM
        balance_sol=150.0,
        first_seen="2025-09-01",
        last_seen="2026-03-05",
        connected_wallets=["8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj"],
        cross_project_affiliations=["SOSANA", "CRM"],
        evidence_refs=["SOSANA_LITE_PAPER", "SOSANA_V2_TREASURY"],
        notes="SOSANA v2 Treasury. Root controller for SOSANA ecosystem. 5M CRM cross-holdings. Strong project connection."
    ),
]

# TIER 4: COORDINATORS
TIER_4_WALLETS = [
    WalletRecord(
        address="JATcFT2j762i7CAayBhQCGuKVstxgL3gWwQXKWtSPbj4",
        category=WalletCategory.BOTNET_SEEDER,
        evidence_tier=EvidenceTier.TIER_1_DIRECT,
        labels=["WAVE_2_ORCHESTRATOR", "COORDINATOR", "100_TXS_7_MIN", "TIER_4"],
        balance_crm=0,
        balance_sol=10.0,
        first_seen="2026-03-26",
        last_seen="2026-03-28",
        connected_wallets=["AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6"],
        cross_project_affiliations=["CRM"],
        evidence_refs=["JATC_WAVE2_ORCHESTRATOR", "2RAWXuFqKvk5U17qBECkqcCtgvUD5ENwwAdLeDQrZ1AXYzAXT7DYmyqSd1qGwcMYgtqMcN13VfKPzGdwujQ6rNQA"],
        notes="Wave 2 orchestrator. 100 transactions in 7 minutes. Botnet coordination. Active deployment."
    ),
    WalletRecord(
        address="CCyYKtnsnkkktZw9KuUrdRWZ4qv9rn3pcNB3LouFMY5Q",
        category=WalletCategory.BOTNET_SEEDER,
        evidence_tier=EvidenceTier.TIER_1_DIRECT,
        labels=["TERTIARY_COORDINATOR", "MOST_ACTIVE", "54_WALLETS", "TIER_4"],
        balance_crm=0,
        balance_sol=5.0,
        first_seen="2026-01-01",
        last_seen="2026-03-28",
        connected_wallets=["H8sMJSCQxfKiFTCfDR3DUMLPwcRbM61LGFJ8N4dK3WjS"],
        cross_project_affiliations=["CRM"],
        evidence_refs=[["CCYYK_MOST_ACTIVE"]],
        notes="Tertiary coordinator. Most active in network. Controls 54+ wallets. Live coordination."
    ),
    WalletRecord(
        address="8HvfGdKrgy5iiG9MjR7cQQmfjPNUT2iE7kqH83bJgaPm",
        category=WalletCategory.BOTNET_SEEDER,
        evidence_tier=EvidenceTier.TIER_2_STRONG,
        labels=["SECONDARY_COORDINATOR", "TIER_4"],
        balance_crm=0,
        balance_sol=3.0,
        first_seen="2025-12-01",
        last_seen="2026-03-27",
        connected_wallets=["AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6"],
        cross_project_affiliations=["CRM"],
        evidence_refs=["8HVF_SECONDARY_COORD"],
        notes="Secondary coordinator. Supports primary botnet operations."
    ),
    WalletRecord(
        address="HxyXAE1PHQsh6iLj3t8MagpFovmR7yk76PEADmTKeVfi",
        category=WalletCategory.BRIDGE_NODE,
        evidence_tier=EvidenceTier.TIER_2_STRONG,
        labels=["CLUSTER_COORDINATOR", "TIER_4", "CONNECTS_AFXI_BMQ4"],
        balance_crm=2000000.0,  # 2M CRM
        balance_sol=8.0,
        first_seen="2025-10-15",
        last_seen="2026-02-10",
        connected_wallets=["EQ2E92SS64j4uh3UxfG6bFHwq2cbj6YMn8kw9Pm3T4ew", "AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6", "BMq4XUa3z9vDov6rwuhRBy1hVFD7VYXfSpJKPDVCyequ"],
        cross_project_affiliations=["CRM", "SOSANA"],
        evidence_refs=["HXYX_CLUSTER_COORD"],
        notes="Cluster coordinator. Connects AFXigaYu (botnet) to BMq4XUa3 (cross-project router). Received 2M CRM from 7abBmGf4H."
    ),
]

# TIER 5: FIELD OPERATIVES
TIER_5_WALLETS = [
    WalletRecord(
        address="7abBmGf4HNu3UXsanJc7WwAPW2PgkEb9hwrFKwCySvyL",
        category=WalletCategory.DUMPER_NODE,
        evidence_tier=EvidenceTier.TIER_1_DIRECT,
        labels=["COMPROMISED_WHALE", "FIELD_OPERATIVE", "30M_CRM", "TIER_5", "VICTIM_INTIMIDATION"],
        balance_crm=30000000.0,  # 30M CRM (started with 1M, grew to 30M)
        balance_sol=25.0,
        first_seen="2025-12-31",
        last_seen="2026-02-10",
        connected_wallets=["8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj", "HxyXAE1PHQsh6iLj3t8MagpFovmR7yk76PEADmTKeVfi"],
        cross_project_affiliations=["CRM"],
        evidence_refs=["7ABBM_COMPROMISED_WHALE", "RXEMcfjDJ7Y6BM4oorDr6BC2TC38Tnf1DnYATBZQ4CipcQJupwxLM3AHkqbCkpm2H7wLr8QHEKvRyLMeooby8VR"],
        notes="COMPROMISED WHALE: Received 1M CRM directly from 8eVZa7b (Dec 31, 2025). Grew to 30M CRM. Sent 2M to HxyXAE1. Field operative. NOT affiliated with victim Marcus Aurelius."
    ),
    WalletRecord(
        address="D9ZGRMhmdMdf5dRdEiLSJLrSETsFuofSPDZHjx5tuULT",
        category=WalletCategory.DUMPER_NODE,
        evidence_tier=EvidenceTier.TIER_2_STRONG,
        labels=["FIELD_OPERATIVE", "DORMANT", "32M_CRM", "TIER_5", "CRITICAL_THREAT"],
        balance_crm=31971154.0,  # 31.97M CRM
        balance_sol=5.0,
        first_seen="2025-11-01",
        last_seen="2026-02-01",
        connected_wallets=["HLnpSz9h2S4hiLQ4uN3vGYAHJqDmbFCwkx9prSXkdPMc"],
        cross_project_affiliations=["CRM"],
        evidence_refs=["D9ZG_FIELD_OP_001"],
        notes="Field operative. 31.97M CRM. DORMANT status - armed and waiting. Critical threat for coordinated dump."
    ),
    WalletRecord(
        address="HPVUJGJwJnpGBDCzoAPKPjHe8QfXLgRjbktXCRyMNi5w",
        category=WalletCategory.DUMPER_NODE,
        evidence_tier=EvidenceTier.TIER_2_STRONG,
        labels=["FIELD_OPERATIVE", "DORMANT", "22M_CRM", "TIER_5", "CRITICAL_THREAT"],
        balance_crm=22015172.0,  # 22.02M CRM
        balance_sol=3.0,
        first_seen="2025-11-15",
        last_seen="2026-02-01",
        connected_wallets=["HLnpSz9h2S4hiLQ4uN3vGYAHJqDmbFCwkx9prSXkdPMc"],
        cross_project_affiliations=["CRM"],
        evidence_refs=["HPVU_FIELD_OP_001"],
        notes="Field operative. 22.02M CRM. DORMANT status - armed and waiting."
    ),
    WalletRecord(
        address="J3V68JvjXFArRBb86NAX8mCoYgFce7MmZjs9ziz74RzT",
        category=WalletCategory.DUMPER_NODE,
        evidence_tier=EvidenceTier.TIER_2_STRONG,
        labels=["FIELD_OPERATIVE", "DORMANT", "22M_CRM", "TIER_5", "CRITICAL_THREAT"],
        balance_crm=22000000.0,  # 22M CRM
        balance_sol=3.0,
        first_seen="2025-12-01",
        last_seen="2026-02-01",
        connected_wallets=["HLnpSz9h2S4hiLQ4uN3vGYAHJqDmbFCwkx9prSXkdPMc"],
        cross_project_affiliations=["CRM"],
        evidence_refs=["J3V68_FIELD_OP_001"],
        notes="Field operative. 22M CRM. DORMANT status - armed and waiting."
    ),
    WalletRecord(
        address="hHxyZi7ZxbYqQmBhTRtdwpjwpfhmWVypRfMVmn2HzPt",
        category=WalletCategory.DUMPER_NODE,
        evidence_tier=EvidenceTier.TIER_2_STRONG,
        labels=["FIELD_OPERATIVE", "RELOADING", "19.3M_CRM", "TIER_5", "IMMINENT_THREAT"],
        balance_crm=19298335.0,  # 19.3M CRM
        balance_sol=4.0,
        first_seen="2025-12-15",
        last_seen="2026-03-28",
        connected_wallets=["3TyLzagkCqQ9RUsXyTj8Wk8U2h8oX7vQb5iJ3mN9pL2s", "9Xx7usVBtYpQmBhTRtdwpjwpfhmWVypRfMVmn2HzPtK"],
        cross_project_affiliations=["CRM"],
        evidence_refs=["HHXY_RELOADING_001"],
        notes="Field operative. 19.3M CRM. RELOADING status - recently funded. Imminent threat."
    ),
    WalletRecord(
        address="CyhJT3o8xrW5vvenMkrJDdpYcdboGGg6SQvSoeVtcA35",
        category=WalletCategory.DUMPER_NODE,
        evidence_tier=EvidenceTier.TIER_2_STRONG,
        labels=["FIELD_OPERATIVE", "ARMED", "12.1M_CRM", "TIER_5", "IMMINENT_THREAT"],
        balance_crm=12107745.0,  # 12.1M CRM
        balance_sol=2.0,
        first_seen="2026-01-01",
        last_seen="2026-03-28",
        connected_wallets=["HLnpSz9h2S4hiLQ4uN3vGYAHJqDmbFCwkx9prSXkdPMc"],
        cross_project_affiliations=["CRM"],
        evidence_refs=["CYHJ_ARMED_001"],
        notes="Field operative. 12.1M CRM. ARMED status - ready to dump."
    ),
    WalletRecord(
        address="89dWxECkCYVd7hBrUC1i4gLSjhmcb3aMa5eU1Yw8QFCM",
        category=WalletCategory.DUMPER_NODE,
        evidence_tier=EvidenceTier.TIER_2_STRONG,
        labels=["FIELD_OPERATIVE", "ACTIVE", "6.4M_CRM", "TIER_5", "ACTIVE_DUMP"],
        balance_crm=6402469.0,  # 6.4M CRM
        balance_sol=1.0,
        first_seen="2025-12-01",
        last_seen="2026-03-28",
        connected_wallets=["HLnpSz9h2S4hiLQ4uN3vGYAHJqDmbFCwkx9prSXkdPMc"],
        cross_project_affiliations=["CRM"],
        evidence_refs=["89DW_ACTIVE_001"],
        notes="Field operative. 6.4M CRM. ACTIVE status - currently dumping."
    ),
]

# TIER 6: ACTIVE DUMP MECHANISM
TIER_6_WALLETS = [
    WalletRecord(
        address="HLnpSz9h2S4hiLQ4uN3vGYAHJqDmbFCwkx9prSXkdPMc",
        category=WalletCategory.DUMPER_NODE,
        evidence_tier=EvidenceTier.TIER_1_DIRECT,
        labels=["ACTIVE_DUMP_WALLET", "WAVE_2", "79.7M_CRM", "DELETED", "TIER_6", "URGENT"],
        balance_crm=79700000.0,  # 79.7M CRM (was 81M, actively dumping)
        balance_sol=0.0,
        first_seen="2025-08-20",
        last_seen="2026-03-28",
        connected_wallets=[
            "8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj",
            "GVC9Zvh3mxfUHfMRi9zGzjRdQtfoQ2WkFXHSfy3ySwoT",
            "D9ZGRMhmdMdf5dRdEiLSJLrSETsFuofSPDZHjx5tuULT",
            "HPVUJGJwJnpGBDCzoAPKPjHe8QfXLgRjbktXCRyMNi5w",
            "J3V68JvjXFArRBb86NAX8mCoYgFce7MmZjs9ziz74RzT"
        ],
        cross_project_affiliations=["CRM"],
        evidence_refs=["HLNP_DUMP_WALLET", "MARCH_26_DELETION", "WAVE_2_ACTIVE"],
        notes="ACTIVE DUMP WALLET: 79.7M CRM (7.97% of supply). Selling in 105K-428K batches via GVC9Zvh3. Wallet DELETED March 26, 2026 after dumping 140K CRM. Wave 2 extraction ongoing."
    ),
    WalletRecord(
        address="GVC9Zvh3mxfUHfMRi9zGzjRdQtfoQ2WkFXHSfy3ySwoT",
        category=WalletCategory.PAYROLL_DISTRIBUTOR,
        evidence_tier=EvidenceTier.TIER_1_DIRECT,
        labels=["FEE_COLLECTOR", "SOL_COLLECTOR", "223_SOL", "TIER_6", "LIVE"],
        balance_crm=0,
        balance_sol=223.88,
        first_seen="2026-03-26",
        last_seen="2026-03-28",
        connected_wallets=["HLnpSz9h2S4hiLQ4uN3vGYAHJqDmbFCwkx9prSXkdPMc"],
        cross_project_affiliations=["CRM"],
        evidence_refs=["GVC9Z_FEE_COLLECTOR"],
        notes="CRM-for-SOL swap fee collector. 223.88 SOL collected (~$26,800 and growing). LIVE - active extraction ongoing."
    ),
]

# VICTIM WALLETS (Marcus Aurelius)
VICTIM_WALLETS = [
    WalletRecord(
        address="HFTwoBvjLcjo5CTpM42jKKVyETnHGWDUM4CpB4fZVBSc",
        category=WalletCategory.VERIFIED_VICTIM,
        evidence_tier=EvidenceTier.TIER_1_DIRECT,
        labels=["VICTIM_WALLET", "MARCUS_AURELIUS", "DUSTED", "WITNESS_INTIMIDATION"],
        balance_crm=0,
        balance_sol=0.001,
        first_seen="2025-01-01",
        last_seen="2026-03-28",
        connected_wallets=[],
        cross_project_affiliations=[],
        evidence_refs=["VICTIM_WALLET_001", "DUSTING_SIGNATURE_2h9GeUwZPjPprwDDPESij2PR5zeCwUkPfUPQXb9Zrz2yhupVEbjQDw1QQkAmMr2CDiSgHPjUHrsdonFB4d6QjSkn"],
        notes="Victim wallet - Marcus Aurelius (CRM token developer). Dusted with 1-lamport transactions. Witness intimidation under 18 U.S.C. § 1512. NO connection to criminal enterprise.",
        kyc_vectors=[{"type": "victim_identity", "name": "Marcus Aurelius", "role": "CRM Developer"}]
    ),
    WalletRecord(
        address="8d6f2pSMDsvnrhVz34uQ7EVNYoe7SUL4eWN8avNsjicd",
        category=WalletCategory.VERIFIED_VICTIM,
        evidence_tier=EvidenceTier.TIER_1_DIRECT,
        labels=["VICTIM_WALLET", "MARCUS_AURELIUS", "DUSTED", "WITNESS_INTIMIDATION"],
        balance_crm=0,
        balance_sol=0.001,
        first_seen="2025-01-01",
        last_seen="2026-03-28",
        connected_wallets=[],
        cross_project_affiliations=[],
        evidence_refs=["VICTIM_WALLET_002", "DUSTING_SIGNATURE_3eHMA6RLnqFcDxati3hFh3Wa5QLVLPH9txYvgedpqJpQcNztk9gtj1inCvNTpNiaznVkj7peAdAayaK1JrnAz4QN"],
        notes="Victim wallet - Marcus Aurelius. Dusted with 1-lamport transactions. Retaliation for investigation. NO connection to criminal enterprise.",
        kyc_vectors=[{"type": "victim_identity", "name": "Marcus Aurelius", "role": "CRM Developer"}]
    ),
]

# HUMAN SUSPECTS (Named Individuals)
HUMAN_SUSPECTS = [
    WalletRecord(
        address="Suspect_Mark_Ross_001",
        category=WalletCategory.SUSPECTED,
        evidence_tier=EvidenceTier.TIER_3_CIRCUMSTANTIAL,
        labels=["MARK_ROSS", "PROJECT_CREATOR", "SOSANA_LINKED", "HUMAN_SUSPECT"],
        balance_crm=0,
        balance_sol=0,
        first_seen="2025-06-01",
        last_seen="2026-03-28",
        connected_wallets=["ASTyfSima4LLAdDgoFGkgqoKowG1LZFDr9fAQrg7iaJZ", "F4HGHWyaCvDkUF88svvCHhSMpR9YzHCYSNmojaKQtRSB"],
        cross_project_affiliations=["CRM", "SOSANA"],
        kyc_vectors=[{"type": "suspected_identity", "name": "Mark Ross", "aliases": ["@markross", "MarkR"], "confidence": "medium", "role": "Suspected Project Creator"}],
        evidence_refs=["HUMAN_INTEL_001", "SOSANA_LITE_PAPER"],
        notes="Suspected project creator. Cross-project involvement with SOSANA. Linked to treasury wallets."
    ),
    WalletRecord(
        address="Suspect_Brian_Lyles_002",
        category=WalletCategory.SUSPECTED,
        evidence_tier=EvidenceTier.TIER_3_CIRCUMSTANTIAL,
        labels=["BRIAN_LYLES", "DEVELOPER", "HUMAN_SUSPECT"],
        balance_crm=0,
        balance_sol=0,
        first_seen="2025-08-01",
        last_seen="2026-03-01",
        connected_wallets=["AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6"],
        cross_project_affiliations=["CRM"],
        kyc_vectors=[{"type": "suspected_identity", "name": "Brian Lyles", "aliases": ["@brianlyles", "BrianL"], "confidence": "medium", "role": "Suspected Developer"}],
        evidence_refs=["HUMAN_INTEL_002"],
        notes="Suspected developer. Technical implementation of botnet and automation."
    ),
    WalletRecord(
        address="Suspect_Tracy_Silver_003",
        category=WalletCategory.SUSPECTED,
        evidence_tier=EvidenceTier.TIER_4_SUSPICIOUS,
        labels=["TRACY_SILVER", "MARKETING", "HUMAN_SUSPECT"],
        balance_crm=0,
        balance_sol=0,
        first_seen="2025-09-01",
        last_seen="2026-02-01",
        connected_wallets=[],
        cross_project_affiliations=["CRM"],
        kyc_vectors=[{"type": "suspected_identity", "name": "Tracy Silver", "aliases": ["@tracysilver", "TracyS"], "confidence": "low", "role": "Suspected Marketing Operator"}],
        evidence_refs=["HUMAN_INTEL_003"],
        notes="Suspected marketing operator. Promotional activities for CRM token."
    ),
    WalletRecord(
        address="Suspect_David_Track_004",
        category=WalletCategory.SUSPECTED,
        evidence_tier=EvidenceTier.TIER_4_SUSPICIOUS,
        labels=["DAVID_TRACK", "LIQUIDITY", "HUMAN_SUSPECT"],
        balance_crm=0,
        balance_sol=0,
        first_seen="2025-10-01",
        last_seen="2026-03-01",
        connected_wallets=["8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj"],
        cross_project_affiliations=["CRM"],
        kyc_vectors=[{"type": "suspected_identity", "name": "David Track", "aliases": ["@davidtrack", "DavidT"], "confidence": "low", "role": "Suspected Liquidity Operator"}],
        evidence_refs=["HUMAN_INTEL_004"],
        notes="Suspected liquidity operator. Pool manipulation and DEX coordination."
    ),
]

# === COMBINE ALL WALLETS ===
ALL_UPDATED_WALLETS = (
    TIER_0_WALLETS +
    TIER_1_WALLETS +
    TIER_2_WALLETS +
    TIER_3_WALLETS +
    TIER_4_WALLETS +
    TIER_5_WALLETS +
    TIER_6_WALLETS +
    VICTIM_WALLETS +
    HUMAN_SUSPECTS
)

# === STATISTICS ===
def get_updated_statistics():
    """Get statistics for updated wallet intelligence."""
    total_crm = sum(w.balance_crm for w in ALL_UPDATED_WALLETS)
    total_sol = sum(w.balance_sol for w in ALL_UPDATED_WALLETS)
    
    by_tier = {
        "Tier_0_Root": len(TIER_0_WALLETS),
        "Tier_1_Treasuries": len(TIER_1_WALLETS),
        "Tier_2_Routers": len(TIER_2_WALLETS),
        "Tier_3_Bridges": len(TIER_3_WALLETS),
        "Tier_4_Coordinators": len(TIER_4_WALLETS),
        "Tier_5_Field_Ops": len(TIER_5_WALLETS),
        "Tier_6_Dump": len(TIER_6_WALLETS),
        "Victims": len(VICTIM_WALLETS),
        "Human_Suspects": len(HUMAN_SUSPECTS),
    }
    
    return {
        "total_wallets": len(ALL_UPDATED_WALLETS),
        "total_crm_controlled": total_crm,
        "total_sol_controlled": total_sol,
        "by_tier": by_tier,
        "field_operative_crm": sum(w.balance_crm for w in TIER_5_WALLETS),
        "treasury_value_usd_estimate": total_sol * 170,  # ~$170/SOL
    }

if __name__ == "__main__":
    import json
    
    print("=" * 70)
    print("OMEGA FORENSIC V5 - UPDATED WALLET INTELLIGENCE")
    print("=" * 70)
    
    stats = get_updated_statistics()
    
    print(f"\n📊 UPDATED STATISTICS:")
    print(f"  Total Wallets: {stats['total_wallets']}")
    print(f"  Total CRM Controlled: {stats['total_crm_controlled']:,.0f}")
    print(f"  Total SOL Controlled: {stats['total_sol_controlled']:,.2f}")
    print(f"  Field Operative CRM: {stats['field_operative_crm']:,.0f}")
    print(f"  Treasury Value (est): ${stats['treasury_value_usd_estimate']:,.0f}")
    
    print(f"\n📁 BY TIER:")
    for tier, count in stats['by_tier'].items():
        print(f"  {tier}: {count}")
    
    print("\n" + "=" * 70)
