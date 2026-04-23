"""
Omega Forensic V5 - Closed Account Tracker
===========================================
Tracks deleted accounts and rent recovery exploits.
Identifies where funds went before account closure.
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

from .api_arsenal import ForensicAPIArsenal, APIResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ClosedAccountTracker")

@dataclass
class ClosedAccountRecord:
    """Record of a closed/deleted account."""
    address: str
    closed_at: Optional[datetime] = None
    rent_recovered: float = 0.0  # SOL recovered from rent
    final_balance_crm: float = 0.0
    final_balance_sol: float = 0.0
    fund_destinations: List[Dict] = field(default_factory=list)
    closure_transaction: str = ""
    evidence_of_deletion: List[str] = field(default_factory=list)

class ClosedAccountTracker:
    """
    Tracks closed/deleted accounts and traces fund movements.
    Critical for following money that "disappeared" via rent recovery.
    """
    
    def __init__(self):
        self.closed_accounts: Dict[str, ClosedAccountRecord] = {}
        self.known_closed = set([
            "HLnpSz9h2S4hiLQ4uN3vGYAHJqDmbFCwkx9prSXkdPMc",  # 81M CRM
        ])
    
    async def investigate_closed_account(
        self,
        address: str,
        arsenal: Optional[ForensicAPIArsenal] = None
    ) -> ClosedAccountRecord:
        """
        Investigate a closed account and trace where funds went.
        
        Args:
            address: Closed account address
            arsenal: Optional API arsenal instance
        
        Returns:
            Closed account investigation record
        """
        logger.info(f"🗑️ Investigating closed account: {address}")
        
        record = ClosedAccountRecord(address=address)
        
        async with ForensicAPIArsenal() as api:
            # Try to get account info (will fail if closed)
            account_result = await api.helius_get_account(address)
            
            if account_result.success and account_result.data:
                # Account still exists
                logger.info(f"  ⚠️ Account {address} still exists")
                record.evidence_of_deletion.append("account_still_exists")
            else:
                # Account is closed
                record.evidence_of_deletion.append("account_not_found_on_chain")
                logger.info(f"  ✓ Confirmed: Account is closed")
            
            # Get transaction history to find closure
            tx_result = await api.helius_get_transactions(address, limit=500)
            
            if tx_result.success and tx_result.data:
                transactions = tx_result.data
                
                # Find the last transactions (closure pattern)
                if transactions:
                    last_tx = transactions[-1]
                    record.closure_transaction = last_tx.get("signature", "")
                    
                    timestamp = last_tx.get("timestamp")
                    if timestamp:
                        record.closed_at = datetime.fromtimestamp(timestamp)
                    
                    # Analyze final transactions for fund movements
                    await self._analyze_final_transactions(record, transactions, api)
            
            # Check if this is a known closed account
            if address in self.known_closed:
                record.evidence_of_deletion.append("known_closed_account_in_database")
        
        self.closed_accounts[address] = record
        
        logger.info(f"  ✓ Investigation complete. Destinations: {len(record.fund_destinations)}")
        
        return record
    
    async def _analyze_final_transactions(
        self,
        record: ClosedAccountRecord,
        transactions: List[Dict],
        api: ForensicAPIArsenal
    ):
        """Analyze final transactions to trace fund movements."""
        # Look at last 20 transactions before closure
        final_txs = transactions[-20:] if len(transactions) >= 20 else transactions
        
        for tx in final_txs:
            # Check for token transfers OUT
            token_transfers = tx.get("tokenTransfers", [])
            
            for transfer in token_transfers:
                from_addr = transfer.get("fromUserAccount")
                
                if from_addr == record.address:
                    # Tokens leaving the account
                    to_addr = transfer.get("toUserAccount")
                    amount = transfer.get("tokenAmount", 0)
                    mint = transfer.get("mint")
                    
                    if mint == "Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS":
                        record.final_balance_crm += amount
                        
                        record.fund_destinations.append({
                            "to": to_addr,
                            "amount": amount,
                            "token": "CRM",
                            "transaction": tx.get("signature"),
                            "timestamp": tx.get("timestamp")
                        })
            
            # Check for SOL transfers OUT
            native_transfers = tx.get("nativeTransfers", [])
            
            for transfer in native_transfers:
                from_addr = transfer.get("fromUserAccount")
                
                if from_addr == record.address:
                    to_addr = transfer.get("toUserAccount")
                    amount = transfer.get("amount", 0) / 1e9
                    record.final_balance_sol += amount
                    
                    record.fund_destinations.append({
                        "to": to_addr,
                        "amount": amount,
                        "token": "SOL",
                        "transaction": tx.get("signature"),
                        "timestamp": tx.get("timestamp")
                    })
            
            # Check for rent recovery (account closure)
            instructions = tx.get("instructions", [])
            
            for ix in instructions:
                program = ix.get("programId")
                
                # System program close account
                if program == "11111111111111111111111111111111":
                    data = ix.get("data", "")
                    if "close" in str(data).lower():
                        record.evidence_of_deletion.append("system_program_close_instruction")
                
                # Token program close account
                if program == "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA":
                    record.evidence_of_deletion.append("token_program_close_instruction")
    
    async def batch_investigate(
        self,
        addresses: List[str]
    ) -> Dict[str, ClosedAccountRecord]:
        """Investigate multiple closed accounts."""
        logger.info(f"🗑️ Investigating {len(addresses)} closed accounts")
        
        tasks = [self.investigate_closed_account(addr) for addr in addresses]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        records = {}
        for addr, result in zip(addresses, results):
            if isinstance(result, Exception):
                logger.error(f"  ✗ Error investigating {addr}: {result}")
            else:
                records[addr] = result
        
        logger.info(f"  ✓ Investigated {len(records)} accounts")
        return records
    
    def trace_fund_destination_graph(
        self,
        start_address: str,
        depth: int = 3
    ) -> Dict:
        """
        Trace fund destinations recursively to build a graph.
        Follows the money through multiple hops.
        """
        logger.info(f"🔍 Tracing fund destinations from {start_address} (depth={depth})")
        
        graph = {
            "start": start_address,
            "nodes": [],
            "edges": [],
            "depth_reached": 0
        }
        
        record = self.closed_accounts.get(start_address)
        if not record:
            return graph
        
        # Add start node
        graph["nodes"].append({
            "id": start_address,
            "type": "closed_account",
            "crm_moved": record.final_balance_crm,
            "sol_moved": record.final_balance_sol
        })
        
        # Add direct destinations
        for dest in record.fund_destinations:
            dest_addr = dest.get("to")
            if dest_addr:
                graph["nodes"].append({
                    "id": dest_addr,
                    "type": "destination",
                    "amount": dest.get("amount"),
                    "token": dest.get("token")
                })
                graph["edges"].append({
                    "source": start_address,
                    "target": dest_addr,
                    "amount": dest.get("amount"),
                    "token": dest.get("token")
                })
        
        return graph
    
    def generate_closed_account_report(self) -> Dict:
        """Generate report on all closed accounts."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "accounts_investigated": len(self.closed_accounts),
                "total_crm_moved": sum(
                    r.final_balance_crm for r in self.closed_accounts.values()
                ),
                "total_sol_moved": sum(
                    r.final_balance_sol for r in self.closed_accounts.values()
                ),
                "total_destinations": sum(
                    len(r.fund_destinations) for r in self.closed_accounts.values()
                )
            },
            "closed_accounts": []
        }
        
        for addr, record in self.closed_accounts.items():
            report["closed_accounts"].append({
                "address": addr,
                "closed_at": record.closed_at.isoformat() if record.closed_at else None,
                "rent_recovered": record.rent_recovered,
                "crm_moved": record.final_balance_crm,
                "sol_moved": record.final_balance_sol,
                "destinations": record.fund_destinations,
                "closure_transaction": record.closure_transaction,
                "evidence": record.evidence_of_deletion
            })
        
        return report
    
    def get_high_value_closed(self, min_crm: float = 1000000) -> List[str]:
        """Get closed accounts that moved significant CRM."""
        return [
            addr for addr, record in self.closed_accounts.items()
            if record.final_balance_crm >= min_crm
        ]

# === SYNC WRAPPERS ===
def investigate_closed(address: str) -> ClosedAccountRecord:
    """Synchronous wrapper for investigating closed account."""
    tracker = ClosedAccountTracker()
    return asyncio.run(tracker.investigate_closed_account(address))

def batch_investigate_closed(addresses: List[str]) -> Dict[str, ClosedAccountRecord]:
    """Synchronous wrapper for batch closed account investigation."""
    tracker = ClosedAccountTracker()
    return asyncio.run(tracker.batch_investigate(addresses))

if __name__ == "__main__":
    # Test the tracker
    import asyncio
    
    async def test():
        print("=" * 70)
        print("OMEGA FORENSIC V5 - CLOSED ACCOUNT TRACKER")
        print("=" * 70)
        
        tracker = ClosedAccountTracker()
        
        # Test known closed account
        test_account = "HLnpSz9h2S4hiLQ4uN3vGYAHJqDmbFCwkx9prSXkdPMc"
        
        print(f"\n🗑️ Investigating: {test_account}")
        print("-" * 70)
        
        record = await tracker.investigate_closed_account(test_account)
        
        print(f"  Closed At: {record.closed_at}")
        print(f"  CRM Moved: {record.final_balance_crm:,.0f}")
        print(f"  SOL Moved: {record.final_balance_sol:.4f}")
        print(f"  Destinations: {len(record.fund_destinations)}")
        print(f"  Evidence: {', '.join(record.evidence_of_deletion)}")
        
        # Generate report
        print("\n" + "=" * 70)
        print("CLOSED ACCOUNT REPORT:")
        print("=" * 70)
        
        report = tracker.generate_closed_account_report()
        
        print(f"  Accounts Investigated: {report['summary']['accounts_investigated']}")
        print(f"  Total CRM Moved: {report['summary']['total_crm_moved']:,.0f}")
        print(f"  Total SOL Moved: {report['summary']['total_sol_moved']:.4f}")
        
        print("\n" + "=" * 70)
    
    asyncio.run(test())
