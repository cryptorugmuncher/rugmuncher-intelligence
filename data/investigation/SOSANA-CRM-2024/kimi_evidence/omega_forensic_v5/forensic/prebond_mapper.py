"""
Omega Forensic V5 - Pre-Bonding Money Flow Mapper
==================================================
Maps money flows during pre-bonding manipulation period.
Proves zero-cost token acquisition before public launch.
Timeline: August 2025 - March 2026
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

from .api_arsenal import ForensicAPIArsenal, APIResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PrebondMapper")

# === TIMELINE CONSTANTS ===
PREBOND_START = 1755120000  # August 2025
BONDING_DATE = 1757808000   # September 2025 (estimated)
INVESTIGATION_END = 1743465600  # March 2026

# === TARGET CONTRACT ===
CRM_TOKEN = "Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS"

@dataclass
class MoneyFlow:
    """Represents a money flow between wallets."""
    from_address: str
    to_address: str
    amount: float
    token: str
    timestamp: datetime
    transaction_signature: str
    flow_type: str  # inflow, outflow, internal

@dataclass
class PrebondActivity:
    """Pre-bonding activity for a wallet."""
    wallet: str
    crm_acquired: float = 0.0
    sol_spent: float = 0.0
    acquisition_price: float = 0.0  # estimated price per token
    first_purchase: Optional[datetime] = None
    last_purchase: Optional[datetime] = None
    funding_sources: List[str] = field(default_factory=list)
    destinations: List[str] = field(default_factory=list)
    suspicious_patterns: List[str] = field(default_factory=list)

class PrebondingMoneyFlowMapper:
    """
    Maps money flows during pre-bonding manipulation.
    Proves insiders acquired tokens at near-zero cost.
    """
    
    def __init__(self):
        self.money_flows: List[MoneyFlow] = []
        self.prebond_activities: Dict[str, PrebondActivity] = {}
        self.suspicious_wallets: List[str] = []
    
    async def map_wallet_flows(
        self,
        wallet: str,
        arsenal: Optional[ForensicAPIArsenal] = None
    ) -> PrebondActivity:
        """
        Map all money flows for a wallet during pre-bonding period.
        
        Args:
            wallet: Wallet address to analyze
            arsenal: Optional API arsenal instance
        
        Returns:
            Pre-bonding activity summary
        """
        logger.info(f"💰 Mapping pre-bonding flows for {wallet}")
        
        activity = PrebondActivity(wallet=wallet)
        
        async with ForensicAPIArsenal() as api:
            # Get all transactions during pre-bonding period
            tx_result = await api.helius_get_transactions(wallet, limit=500)
            
            if not tx_result.success or not tx_result.data:
                logger.warning(f"  No transaction data for {wallet}")
                return activity
            
            transactions = tx_result.data
            
            for tx in transactions:
                timestamp = tx.get("timestamp")
                if not timestamp:
                    continue
                
                # Check if within pre-bonding period
                if not (PREBOND_START <= timestamp <= BONDING_DATE):
                    continue
                
                tx_time = datetime.fromtimestamp(timestamp)
                sig = tx.get("signature", "")
                
                # Analyze token transfers
                token_transfers = tx.get("tokenTransfers", [])
                
                for transfer in token_transfers:
                    mint = transfer.get("mint")
                    
                    if mint == CRM_TOKEN:
                        amount = transfer.get("tokenAmount", 0)
                        from_addr = transfer.get("fromUserAccount")
                        to_addr = transfer.get("toUserAccount")
                        
                        if to_addr == wallet:
                            # CRM inflow
                            activity.crm_acquired += amount
                            
                            if activity.first_purchase is None:
                                activity.first_purchase = tx_time
                            activity.last_purchase = tx_time
                            
                            if from_addr and from_addr not in activity.funding_sources:
                                activity.funding_sources.append(from_addr)
                            
                            # Record money flow
                            flow = MoneyFlow(
                                from_address=from_addr or "unknown",
                                to_address=wallet,
                                amount=amount,
                                token="CRM",
                                timestamp=tx_time,
                                transaction_signature=sig,
                                flow_type="inflow"
                            )
                            self.money_flows.append(flow)
                        
                        elif from_addr == wallet:
                            # CRM outflow
                            if to_addr and to_addr not in activity.destinations:
                                activity.destinations.append(to_addr)
                            
                            flow = MoneyFlow(
                                from_address=wallet,
                                to_address=to_addr or "unknown",
                                amount=amount,
                                token="CRM",
                                timestamp=tx_time,
                                transaction_signature=sig,
                                flow_type="outflow"
                            )
                            self.money_flows.append(flow)
                
                # Analyze SOL transfers (to estimate cost)
                native_transfers = tx.get("nativeTransfers", [])
                
                for transfer in native_transfers:
                    from_addr = transfer.get("fromUserAccount")
                    to_addr = transfer.get("toUserAccount")
                    amount = transfer.get("amount", 0) / 1e9  # Convert lamports to SOL
                    
                    # If wallet is spending SOL during pre-bonding, track it
                    if from_addr == wallet:
                        activity.sol_spent += amount
            
            # Calculate acquisition price
            if activity.crm_acquired > 0 and activity.sol_spent > 0:
                activity.acquisition_price = activity.sol_spent / activity.crm_acquired
            
            # Detect suspicious patterns
            self._detect_suspicious_patterns(activity)
        
        self.prebond_activities[wallet] = activity
        
        logger.info(f"  ✓ Mapped: {activity.crm_acquired:,.0f} CRM acquired, {activity.sol_spent:.4f} SOL spent")
        
        return activity
    
    def _detect_suspicious_patterns(self, activity: PrebondActivity):
        """Detect suspicious pre-bonding patterns."""
        patterns = []
        
        # Pattern 1: Zero or near-zero cost acquisition
        if activity.acquisition_price < 0.000001:  # Less than 0.000001 SOL per token
            patterns.append("ZERO_COST_ACQUISITION")
        
        # Pattern 2: Very early acquisition (first week)
        if activity.first_purchase:
            days_from_start = (activity.first_purchase - datetime.fromtimestamp(PREBOND_START)).days
            if days_from_start <= 7:
                patterns.append("FIRST_WEEK_ACQUISITION")
        
        # Pattern 3: Large accumulation
        if activity.crm_acquired > 1000000:  # > 1M tokens
            patterns.append("LARGE_ACCUMULATION")
        
        # Pattern 4: Multiple funding sources
        if len(activity.funding_sources) > 3:
            patterns.append("MULTI_SOURCE_FUNDING")
        
        # Pattern 5: No SOL spent (completely free)
        if activity.sol_spent == 0 and activity.crm_acquired > 0:
            patterns.append("COMPLETELY_FREE_ACQUISITION")
        
        activity.suspicious_patterns = patterns
        
        if patterns:
            self.suspicious_wallets.append(activity.wallet)
    
    async def map_multiple_wallets(
        self,
        wallets: List[str]
    ) -> Dict[str, PrebondActivity]:
        """Map pre-bonding flows for multiple wallets."""
        logger.info(f"💰 Mapping {len(wallets)} wallets for pre-bonding activity")
        
        tasks = [self.map_wallet_flows(wallet) for wallet in wallets]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        activities = {}
        for wallet, result in zip(wallets, results):
            if isinstance(result, Exception):
                logger.error(f"  ✗ Error mapping {wallet}: {result}")
            else:
                activities[wallet] = result
        
        logger.info(f"  ✓ Mapped {len(activities)} wallets")
        return activities
    
    def trace_fund_origins(
        self,
        wallet: str,
        depth: int = 3
    ) -> List[Dict]:
        """
        Trace the origin of funds for a wallet.
        Follows the money backwards to find KYC vectors.
        """
        logger.info(f"🔍 Tracing fund origins for {wallet} (depth={depth})")
        
        origins = []
        activity = self.prebond_activities.get(wallet)
        
        if not activity:
            return origins
        
        for source in activity.funding_sources:
            origins.append({
                "wallet": source,
                "relationship": "funding_source",
                "amount_crm": activity.crm_acquired,
                "depth": 1
            })
        
        return origins
    
    def generate_prebond_report(self) -> Dict:
        """Generate comprehensive pre-bonding manipulation report."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "period": {
                "start": datetime.fromtimestamp(PREBOND_START).isoformat(),
                "bonding_date": datetime.fromtimestamp(BONDING_DATE).isoformat(),
                "end": datetime.fromtimestamp(INVESTIGATION_END).isoformat()
            },
            "summary": {
                "wallets_analyzed": len(self.prebond_activities),
                "suspicious_wallets": len(self.suspicious_wallets),
                "total_crm_acquired": sum(
                    a.crm_acquired for a in self.prebond_activities.values()
                ),
                "total_sol_spent": sum(
                    a.sol_spent for a in self.prebond_activities.values()
                ),
                "avg_acquisition_price": 0.0
            },
            "suspicious_activity": [],
            "money_flows": []
        }
        
        # Calculate average acquisition price
        total_crm = report["summary"]["total_crm_acquired"]
        total_sol = report["summary"]["total_sol_spent"]
        if total_crm > 0:
            report["summary"]["avg_acquisition_price"] = total_sol / total_crm
        
        # Compile suspicious activity
        for wallet, activity in self.prebond_activities.items():
            if activity.suspicious_patterns:
                report["suspicious_activity"].append({
                    "wallet": wallet,
                    "crm_acquired": activity.crm_acquired,
                    "sol_spent": activity.sol_spent,
                    "acquisition_price": activity.acquisition_price,
                    "patterns": activity.suspicious_patterns,
                    "funding_sources": activity.funding_sources
                })
        
        # Compile money flows
        for flow in self.money_flows:
            report["money_flows"].append({
                "from": flow.from_address,
                "to": flow.to_address,
                "amount": flow.amount,
                "token": flow.token,
                "timestamp": flow.timestamp.isoformat(),
                "signature": flow.transaction_signature
            })
        
        return report
    
    def get_zero_cost_acquirers(self) -> List[str]:
        """Get wallets that acquired CRM at zero/near-zero cost."""
        return [
            wallet for wallet, activity in self.prebond_activities.items()
            if "ZERO_COST_ACQUISITION" in activity.suspicious_patterns
            or "COMPLETELY_FREE_ACQUISITION" in activity.suspicious_patterns
        ]
    
    def get_early_insiders(self) -> List[str]:
        """Get wallets that acquired CRM in first week (insider indicator)."""
        return [
            wallet for wallet, activity in self.prebond_activities.items()
            if "FIRST_WEEK_ACQUISITION" in activity.suspicious_patterns
        ]

# === SYNC WRAPPERS ===
def map_prebond_flows(wallet: str) -> PrebondActivity:
    """Synchronous wrapper for mapping pre-bonding flows."""
    mapper = PrebondingMoneyFlowMapper()
    return asyncio.run(mapper.map_wallet_flows(wallet))

def batch_map_prebond(wallets: List[str]) -> Dict[str, PrebondActivity]:
    """Synchronous wrapper for batch pre-bonding mapping."""
    mapper = PrebondingMoneyFlowMapper()
    return asyncio.run(mapper.map_multiple_wallets(wallets))

if __name__ == "__main__":
    # Test the mapper
    import asyncio
    
    async def test():
        print("=" * 70)
        print("OMEGA FORENSIC V5 - PRE-BONDING MONEY FLOW MAPPER")
        print("=" * 70)
        
        mapper = PrebondingMoneyFlowMapper()
        
        # Test critical wallets
        test_wallets = [
            "AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6",
            "7XCU8zT6K8G7z9Lm3PqRsTuVwXyZAbCdEfGhIjKlMnOp",
        ]
        
        for wallet in test_wallets:
            print(f"\n💰 Mapping: {wallet}")
            print("-" * 70)
            
            activity = await mapper.map_wallet_flows(wallet)
            
            print(f"  CRM Acquired: {activity.crm_acquired:,.0f}")
            print(f"  SOL Spent: {activity.sol_spent:.4f}")
            print(f"  Acquisition Price: {activity.acquisition_price:.10f} SOL/CRM")
            print(f"  First Purchase: {activity.first_purchase}")
            print(f"  Funding Sources: {len(activity.funding_sources)}")
            print(f"  Suspicious Patterns: {', '.join(activity.suspicious_patterns) or 'None'}")
        
        # Generate report
        print("\n" + "=" * 70)
        print("PRE-BONDING REPORT SUMMARY:")
        print("=" * 70)
        
        report = mapper.generate_prebond_report()
        
        print(f"  Wallets Analyzed: {report['summary']['wallets_analyzed']}")
        print(f"  Suspicious Wallets: {report['summary']['suspicious_wallets']}")
        print(f"  Total CRM Acquired: {report['summary']['total_crm_acquired']:,.0f}")
        print(f"  Total SOL Spent: {report['summary']['total_sol_spent']:.4f}")
        print(f"  Avg Acquisition Price: {report['summary']['avg_acquisition_price']:.10f}")
        
        print("\n" + "=" * 70)
    
    asyncio.run(test())
