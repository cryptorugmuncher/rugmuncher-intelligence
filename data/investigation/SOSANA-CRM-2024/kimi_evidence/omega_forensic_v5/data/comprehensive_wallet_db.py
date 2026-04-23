"""
Omega Forensic V5 - Comprehensive Wallet Database
==================================================
Complete snapshot database with scammer connection mapping.
Every wallet tracked with relationship analysis.
"""

import json
import csv
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Set
from datetime import datetime
from enum import Enum

class WalletStatus(Enum):
    """Status of wallet in investigation."""
    CONFIRMED_SCAMMER = "confirmed_scammer"      # Directly identified
    SUSPECTED_SCAMMER = "suspected_scammer"      # Strong connections
    CONNECTED = "connected"                       # Linked to scammers
    ASSOCIATED = "associated"                     # Secondary connection
    CLEAN = "clean"                               # No connections found
    UNKNOWN = "unknown"                           # Not yet analyzed
    VICTIM = "victim"                             # Confirmed victim

class ConnectionType(Enum):
    """Types of connections between wallets."""
    DIRECT_TRANSACTION = "direct_transaction"     # Direct tx between wallets
    FUNDING = "funding"                           # Funded by scammer
    RECEIVED_FROM = "received_from"              # Received from scammer
    SENT_TO = "sent_to"                          # Sent to scammer
    COMMON_COUNTERPARTY = "common_counterparty"  # Shared connections
    SAME_CLUSTER = "same_cluster"                # Part of same operation
    BOTNET_LINK = "botnet_link"                  # Same botnet deployment
    TEMPORAL_PROXIMITY = "temporal_proximity"    # Similar timing patterns

@dataclass
class WalletConnection:
    """Connection between two wallets."""
    target_address: str
    connection_type: ConnectionType
    strength: float  # 0.0 to 1.0
    evidence: List[str] = field(default_factory=list)
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    transaction_count: int = 0
    total_value_transferred: float = 0.0

@dataclass
class ComprehensiveWalletRecord:
    """Complete wallet record with connection mapping."""
    # Identity
    address: str
    status: WalletStatus
    
    # Balances (at snapshot time)
    balance_sol: float = 0.0
    balance_crm: float = 0.0
    balance_usdc: float = 0.0
    balance_usdt: float = 0.0
    other_tokens: Dict[str, float] = field(default_factory=dict)
    
    # Classification
    tier: Optional[int] = None  # 0-6 for known scammers
    labels: List[str] = field(default_factory=list)
    
    # Timeline
    created_at: Optional[str] = None
    first_transaction: Optional[str] = None
    last_transaction: Optional[str] = None
    
    # Connections to scammers
    scammer_connections: List[WalletConnection] = field(default_factory=list)
    connection_score: float = 0.0  # 0.0 to 1.0
    
    # Network analysis
    total_transactions: int = 0
    unique_counterparties: int = 0
    scammer_counterparties: int = 0
    
    # Evidence
    evidence_refs: List[str] = field(default_factory=list)
    notes: str = ""
    
    # Risk assessment
    risk_level: str = "unknown"  # critical, high, medium, low, none
    flags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    def get_connection_summary(self) -> str:
        """Get summary of scammer connections."""
        if not self.scammer_connections:
            return "No scammer connections found"
        
        conn_types = {}
        for conn in self.scammer_connections:
            ct = conn.connection_type.value
            conn_types[ct] = conn_types.get(ct, 0) + 1
        
        return ", ".join(f"{k}: {v}" for k, v in conn_types.items())

class ComprehensiveWalletDatabase:
    """
    Complete wallet database with scammer connection mapping.
    """
    
    # Known scammer wallets (from our investigation)
    KNOWN_SCAMMERS = {
        # Tier 0: Root
        "CNSob1LwXvDRmjioxyjm78tDb2S7nzFK6K8t3VmuhKpn": 0,
        "EQ2E92SS64j4uh3UxfG6bFHwq2cbj6YMn8kw9Pm3T4ew": 0,
        
        # Tier 1: Treasuries
        "A77HErqtfN1hLLpvZ9pCtu66FEtM8BveoaKbbMoZ4RiR": 1,
        "ASTyfSima4LLAdDgoFGkgqoKowG1LZFDr9fAQrg7iaJZ": 1,
        "H8sMJSCQxfKiFTCfDR3DUMLPwcRbM61LGFJ8N4dK3WjS": 1,
        "F7p3dFrjRTbtRp8FRF6qHLomXbKRBzpvBLjtQcfcgmNe": 1,
        
        # Tier 2: Routers
        "AHXDVNdFAaMrBMnSiBLQT6MGsvPS4aSne5FV7DSP4BWt": 2,
        "DojAziGhpLddzSPTCsCvp577wkP9N6AtVc87HJqihcZd": 2,
        
        # Tier 3: Bridges
        "8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj": 3,
        "DLHnb1yt6DMx2PCEuTniiTPfoM4EuTfuTqT8jRfdw9P8": 3,
        "F4HGHWyaCvDkUF88svvCHhSMpR9YzHCYSNmojaKQtRSB": 3,
        
        # Tier 4: Coordinators
        "JATcFT2j762i7CAayBhQCGuKVstxgL3gWwQXKWtSPbj4": 4,
        "CCyYKtnsnkkktZw9KuUrdRWZ4qv9rn3pcNB3LouFMY5Q": 4,
        "8HvfGdKrgy5iiG9MjR7cQQmfjPNUT2iE7kqH83bJgaPm": 4,
        "HxyXAE1PHQsh6iLj3t8MagpFovmR7yk76PEADmTKeVfi": 4,
        
        # Tier 5: Field Operatives
        "7abBmGf4HNu3UXsanJc7WwAPW2PgkEb9hwrFKwCySvyL": 5,
        "D9ZGRMhmdMdf5dRdEiLSJLrSETsFuofSPDZHjx5tuULT": 5,
        "HPVUJGJwJnpGBDCzoAPKPjHe8QfXLgRjbktXCRyMNi5w": 5,
        "J3V68JvjXFArRBb86NAX8mCoYgFce7MmZjs9ziz74RzT": 5,
        "hHxyZi7ZxbYqQmBhTRtdwpjwpfhmWVypRfMVmn2HzPt": 5,
        "CyhJT3o8xrW5vvenMkrJDdpYcdboGGg6SQvSoeVtcA35": 5,
        "89dWxECkCYVd7hBrUC1i4gLSjhmcb3aMa5eU1Yw8QFCM": 5,
        
        # Tier 6: Dump
        "HLnpSz9h2S4hiLQ4uN3vGYAHJqDmbFCwkx9prSXkdPMc": 6,
        "GVC9Zvh3mxfUHfMRi9zGzjRdQtfoQ2WkFXHSfy3ySwoT": 6,
        
        # Botnet Commander
        "AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6": 4,
    }
    
    def __init__(self):
        self.wallets: Dict[str, ComprehensiveWalletRecord] = {}
        self.scammer_addresses: Set[str] = set(self.KNOWN_SCAMMERS.keys())
        self.connection_graph: Dict[str, List[str]] = {}
    
    def add_wallet(self, record: ComprehensiveWalletRecord) -> None:
        """Add a wallet to the database."""
        # Auto-classify if known scammer
        if record.address in self.KNOWN_SCAMMERS:
            record.status = WalletStatus.CONFIRMED_SCAMMER
            record.tier = self.KNOWN_SCAMMERS[record.address]
            record.risk_level = "critical"
            record.labels.append(f"TIER_{record.tier}_SCAMMER")
        
        self.wallets[record.address] = record
    
    def analyze_connections(self, address: str) -> List[WalletConnection]:
        """
        Analyze a wallet's connections to known scammers.
        Returns list of connections found.
        """
        wallet = self.wallets.get(address)
        if not wallet:
            return []
        
        connections = []
        
        # Check if directly connected to any scammer
        for scammer_addr in self.scammer_addresses:
            scammer = self.wallets.get(scammer_addr)
            if not scammer:
                continue
            
            # Check for direct transaction evidence
            # (This would be populated from actual transaction data)
            
        return connections
    
    def calculate_connection_score(self, address: str) -> float:
        """
        Calculate a wallet's connection score to scammers.
        0.0 = no connection, 1.0 = direct scammer
        """
        wallet = self.wallets.get(address)
        if not wallet:
            return 0.0
        
        # Known scammer = 1.0
        if wallet.status == WalletStatus.CONFIRMED_SCAMMER:
            return 1.0
        
        # Calculate based on connections
        score = 0.0
        for conn in wallet.scammer_connections:
            score += conn.strength * 0.3  # Each connection adds up to 0.3
        
        # Cap at 0.95 for non-scammers
        return min(score, 0.95)
    
    def find_connected_wallets(self, min_score: float = 0.1) -> List[ComprehensiveWalletRecord]:
        """Find all wallets connected to scammers above threshold."""
        connected = []
        for wallet in self.wallets.values():
            score = self.calculate_connection_score(wallet.address)
            if score >= min_score:
                wallet.connection_score = score
                connected.append(wallet)
        
        # Sort by connection score
        connected.sort(key=lambda w: w.connection_score, reverse=True)
        return connected
    
    def get_wallets_by_status(self, status: WalletStatus) -> List[ComprehensiveWalletRecord]:
        """Get all wallets with a specific status."""
        return [w for w in self.wallets.values() if w.status == status]
    
    def get_wallets_by_tier(self, tier: int) -> List[ComprehensiveWalletRecord]:
        """Get all wallets in a specific tier."""
        return [w for w in self.wallets.values() if w.tier == tier]
    
    def export_to_json(self, filepath: str) -> None:
        """Export database to JSON."""
        data = {
            "exported_at": datetime.now().isoformat(),
            "total_wallets": len(self.wallets),
            "scammer_wallets": len(self.scammer_addresses),
            "wallets": [w.to_dict() for w in self.wallets.values()]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def export_to_csv(self, filepath: str) -> None:
        """Export database to CSV."""
        if not self.wallets:
            return
        
        # Flatten data for CSV
        rows = []
        for wallet in self.wallets.values():
            row = {
                "address": wallet.address,
                "status": wallet.status.value,
                "tier": wallet.tier,
                "risk_level": wallet.risk_level,
                "connection_score": wallet.connection_score,
                "balance_sol": wallet.balance_sol,
                "balance_crm": wallet.balance_crm,
                "scammer_connections": len(wallet.scammer_connections),
                "labels": "|".join(wallet.labels),
                "notes": wallet.notes[:200] if wallet.notes else ""
            }
            rows.append(row)
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
    
    def generate_connection_report(self) -> Dict:
        """Generate report on wallet connections."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_wallets": len(self.wallets),
                "confirmed_scammers": len(self.get_wallets_by_status(WalletStatus.CONFIRMED_SCAMMER)),
                "suspected_scammers": len(self.get_wallets_by_status(WalletStatus.SUSPECTED_SCAMMER)),
                "connected_wallets": len(self.get_wallets_by_status(WalletStatus.CONNECTED)),
                "clean_wallets": len(self.get_wallets_by_status(WalletStatus.CLEAN)),
                "unknown_wallets": len(self.get_wallets_by_status(WalletStatus.UNKNOWN)),
            },
            "by_tier": {},
            "high_risk_wallets": [],
            "recommendations": []
        }
        
        # Count by tier
        for tier in range(7):
            wallets = self.get_wallets_by_tier(tier)
            if wallets:
                report["by_tier"][f"tier_{tier}"] = len(wallets)
        
        # Find high-risk wallets (not confirmed scammers but high connection score)
        for wallet in self.wallets.values():
            if wallet.status != WalletStatus.CONFIRMED_SCAMMER:
                score = self.calculate_connection_score(wallet.address)
                if score > 0.5:
                    report["high_risk_wallets"].append({
                        "address": wallet.address,
                        "connection_score": score,
                        "status": wallet.status.value
                    })
        
        # Sort by score
        report["high_risk_wallets"].sort(key=lambda x: x["connection_score"], reverse=True)
        
        return report

# === UTILITY FUNCTIONS ===

def create_wallet_from_snapshot(
    address: str,
    balance_sol: float = 0.0,
    balance_crm: float = 0.0,
    created_at: str = None,
    **kwargs
) -> ComprehensiveWalletRecord:
    """Create a wallet record from snapshot data."""
    return ComprehensiveWalletRecord(
        address=address,
        status=WalletStatus.UNKNOWN,
        balance_sol=balance_sol,
        balance_crm=balance_crm,
        created_at=created_at,
        **kwargs
    )

def add_connection(
    wallet: ComprehensiveWalletRecord,
    target_address: str,
    connection_type: ConnectionType,
    strength: float = 0.5,
    evidence: List[str] = None
) -> None:
    """Add a connection to a wallet."""
    conn = WalletConnection(
        target_address=target_address,
        connection_type=connection_type,
        strength=strength,
        evidence=evidence or []
    )
    wallet.scammer_connections.append(conn)

# === GLOBAL INSTANCE ===
_db = None

def get_comprehensive_db() -> ComprehensiveWalletDatabase:
    """Get singleton database instance."""
    global _db
    if _db is None:
        _db = ComprehensiveWalletDatabase()
    return _db

if __name__ == "__main__":
    # Test the database
    db = get_comprehensive_db()
    
    print("=" * 70)
    print("COMPREHENSIVE WALLET DATABASE")
    print("=" * 70)
    
    print(f"\n📊 Known Scammer Wallets: {len(db.KNOWN_SCAMMERS)}")
    print(f"📊 By Tier:")
    for tier in range(7):
        count = sum(1 for t in db.KNOWN_SCAMMERS.values() if t == tier)
        if count > 0:
            print(f"  Tier {tier}: {count} wallets")
    
    print("\n" + "=" * 70)
