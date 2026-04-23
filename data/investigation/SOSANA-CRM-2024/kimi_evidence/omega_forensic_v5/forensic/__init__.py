"""
Omega Forensic V5 - Forensic Module
====================================
Complete forensic investigation toolkit.

Divisions:
- Division 1: Identity & AML (Arkham, MistTrack, ChainAbuse)
- Division 2: On-Chain Autopsy (Helius, QuickNode, Solscan)
- Division 3: Token Mechanics (BirdEye, LunarCrush)
- Division 4: Real World OSINT (Serper)

Modules:
- api_arsenal: Complete API integration
- wallet_database: 200+ wallet database
- deep_scanner: Multi-layer wallet analysis
- cross_token_tracker: Cross-project affiliation tracking
- prebond_mapper: Pre-bonding money flow mapping
- closed_account_tracker: Deleted account tracing
- report_generator: Federal RICO report generation
"""

from .api_arsenal import ForensicAPIArsenal, APIResponse, sync_full_wallet_profile, sync_kyc_vector_hunt
from .wallet_database import (
    WalletDatabase, 
    WalletRecord, 
    WalletCategory, 
    EvidenceTier,
    get_wallet_database
)
from .deep_scanner import (
    DeepWalletScanner, 
    WalletAnalysis, 
    ConnectionPath,
    deep_scan,
    batch_scan
)
from .cross_token_tracker import (
    CrossTokenAffiliationTracker,
    TokenAffiliation,
    CrossProjectConnection,
    track_wallet,
    find_cross_project_wallets
)
from .prebond_mapper import (
    PrebondingMoneyFlowMapper,
    MoneyFlow,
    PrebondActivity,
    map_prebond_flows,
    batch_map_prebond
)
from .closed_account_tracker import (
    ClosedAccountTracker,
    ClosedAccountRecord,
    investigate_closed,
    batch_investigate_closed
)
from .report_generator import (
    FinalReportGenerator,
    RICOCharge,
    SuspectDossier,
    generate_final_report
)

__all__ = [
    # API Arsenal
    "ForensicAPIArsenal",
    "APIResponse",
    "sync_full_wallet_profile",
    "sync_kyc_vector_hunt",
    
    # Wallet Database
    "WalletDatabase",
    "WalletRecord",
    "WalletCategory",
    "EvidenceTier",
    "get_wallet_database",
    
    # Deep Scanner
    "DeepWalletScanner",
    "WalletAnalysis",
    "ConnectionPath",
    "deep_scan",
    "batch_scan",
    
    # Cross Token Tracker
    "CrossTokenAffiliationTracker",
    "TokenAffiliation",
    "CrossProjectConnection",
    "track_wallet",
    "find_cross_project_wallets",
    
    # Prebond Mapper
    "PrebondingMoneyFlowMapper",
    "MoneyFlow",
    "PrebondActivity",
    "map_prebond_flows",
    "batch_map_prebond",
    
    # Closed Account Tracker
    "ClosedAccountTracker",
    "ClosedAccountRecord",
    "investigate_closed",
    "batch_investigate_closed",
    
    # Report Generator
    "FinalReportGenerator",
    "RICOCharge",
    "SuspectDossier",
    "generate_final_report",
]

__version__ = "5.0.0"
