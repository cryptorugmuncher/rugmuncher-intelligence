#!/usr/bin/env python3
"""
🔍 CROSS-PROJECT NETWORK EXPANSION ANALYZER
===========================================
Analyzes CRM network counterparties to find other scam connections.

Since primary wallets are wiped/dormant, this tool:
1. Reads existing CRM transaction exports
2. Identifies counterparties (victims, exchanges, intermediaries)
3. Analyzes counterparty holdings across other tokens
4. Maps "friend-of-friend" network expansion

Author: Marcus Aurelius
Date: April 13, 2026
Case: CRM-SCAM-2025-001 (RICO-eligible)
"""

import asyncio
import aiohttp
import json
import os
import csv
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict

# API Keys
SOLSCAN_KEY = os.getenv('SOLSCAN_KEY', open('/root/.secrets/solscan_api_key').read().strip())
HELIUS_KEY = os.getenv('HELIUS_API_KEY', open('/root/.secrets/helius_api_key').read().strip())

# Target wallets to find counterparties for
TARGET_WALLETS = [
    "F4HGHWyaMAkQH7Q2YJfAyGmPoo5aRs6R6VuSPia3JM3U",  # Treasury
    "AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6",  # Automation
    "8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj",  # Feeder
    "HLnpSz9h2S4hiLQ43rnSD9XkcUThA7B8hQMKmDaiTLcC",  # Just analyzed
]

# Known suspicious token patterns (partial matching)
SUSPICIOUS_TOKEN_PATTERNS = [
    "BONK", "WIF", "POPCAT", "WEN", "SLERF", "BOME", "PONKE",
    "pump", "launch", "fair", "moon", "safe", "elon", "pepe",
    "doge", "shib", "floki", "akita", "kishu"
]

# Known scam/rug pull indicators in token metadata
RUG_INDICATORS = [
    "mint_authority_enabled",
    "freeze_authority_enabled", 
    "single_holder_50plus",
    "created_and_dumped_same_day",
    "liquidity_removed",
    "contract_renounced_after_launch"
]


@dataclass
class CounterpartyAnalysis:
    """Analysis of a counterparty wallet"""
    address: str
    crm_interaction_type: str  # "sent_to", "received_from", "intermediary"
    crm_transaction_count: int
    other_tokens_held: List[Dict]
    suspicious_activities: List[str]
    risk_score: float
    network_tier: str  # "victim", "exchange", "intermediary", "suspicious"


@dataclass
class CrossProjectFinding:
    """Cross-project connection finding"""
    source_wallet: str
    counterparty: str
    token_address: str
    token_name: str
    finding_type: str
    confidence: float
    evidence: List[str]
    pattern_signature: str


class CounterpartyNetworkAnalyzer:
    """
    Analyzes counterparty networks to find cross-project scam connections
    """
    
    def __init__(self):
        self.solscan_base = "https://pro-api.solscan.io/v1.0"
        self.session: Optional[aiohttp.ClientSession] = None
        self.counterparties: Dict[str, CounterpartyAnalysis] = {}
        self.findings: List[CrossProjectFinding] = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
    
    async def solscan_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make Solscan Pro API request"""
        url = f"{self.solscan_base}/{endpoint}"
        headers = {'token': SOLSCAN_KEY, 'Accept': 'application/json'}
        
        try:
            async with self.session.get(url, params=params, headers=headers, timeout=30) as resp:
                if resp.status == 200:
                    return await resp.json()
                elif resp.status == 429:
                    await asyncio.sleep(2)
                    return await self.solscan_request(endpoint, params)
                return None
        except Exception as e:
            return None
    
    def load_crm_transactions_from_exports(self) -> Dict[str, List[Dict]]:
        """
        Load existing CRM transaction exports
        Returns: Dict[wallet_address, List[transactions]]
        """
        transactions_by_wallet = defaultdict(list)
        
        # Look for transaction export files
        export_dirs = [
            "/root/crm_investigation/evidence",
            "/root/crm_investigation/evidence/blockchain_data",
            "/root/dumps/investigation-20260409/mixed"
        ]
        
        for export_dir in export_dirs:
            if os.path.exists(export_dir):
                for file in os.listdir(export_dir):
                    if file.endswith('.csv') or file.endswith('.csv.json'):
                        file_path = os.path.join(export_dir, file)
                        try:
                            # Try to extract wallet from filename
                            for wallet in TARGET_WALLETS:
                                if wallet[:8] in file or wallet[:20] in file:
                                    # Parse CSV/JSON
                                    if file.endswith('.csv'):
                                        with open(file_path, 'r') as f:
                                            reader = csv.DictReader(f)
                                            for row in reader:
                                                row['source_file'] = file
                                                transactions_by_wallet[wallet].append(row)
                                    elif file.endswith('.csv.json'):
                                        with open(file_path, 'r') as f:
                                            data = json.load(f)
                                            if isinstance(data, list):
                                                for row in data:
                                                    row['source_file'] = file
                                                transactions_by_wallet[wallet].extend(data)
                        except Exception as e:
                            print(f"⚠️  Error loading {file}: {e}")
        
        return dict(transactions_by_wallet)
    
    def extract_counterparties(self, transactions: List[Dict]) -> Dict[str, Dict]:
        """
        Extract unique counterparties from transaction list
        Returns: Dict[counterparty_address, metadata]
        """
        counterparties = defaultdict(lambda: {
            'interaction_count': 0,
            'total_crm_volume': 0,
            'first_interaction': None,
            'last_interaction': None,
            'interaction_types': set()
        })
        
        for tx in transactions:
            # Determine counterparty (sender or receiver)
            sender = tx.get('sender', tx.get('from', tx.get('source', '')))
            receiver = tx.get('receiver', tx.get('to', tx.get('destination', '')))
            amount = float(tx.get('amount', tx.get('value', 0)))
            timestamp = tx.get('timestamp', tx.get('time', tx.get('blockTime', '')))
            
            # Add both sides as counterparties (excluding our target wallets)
            for counterparty in [sender, receiver]:
                if counterparty and counterparty not in TARGET_WALLETS:
                    counterparties[counterparty]['interaction_count'] += 1
                    counterparties[counterparty]['total_crm_volume'] += amount
                    
                    if timestamp:
                        if not counterparties[counterparty]['first_interaction']:
                            counterparties[counterparty]['first_interaction'] = timestamp
                        counterparties[counterparty]['last_interaction'] = timestamp
                    
                    # Determine interaction type
                    if sender in TARGET_WALLETS:
                        counterparties[counterparty]['interaction_types'].add('received_from_network')
                    if receiver in TARGET_WALLETS:
                        counterparties[counterparty]['interaction_types'].add('sent_to_network')
        
        return dict(counterparties)
    
    async def analyze_counterparty_tokens(self, address: str) -> List[Dict]:
        """
        Analyze what other tokens a counterparty holds
        """
        print(f"🔍 Analyzing counterparty: {address[:20]}...")
        
        tokens = []
        
        # Get token accounts
        data = await self.solscan_request("account/tokenaccounts", {
            "address": address,
            "type": "token",
            "page": 1,
            "pageSize": 100
        })
        
        if data and 'data' in data:
            for token_account in data['data']:
                token_address = token_account.get('tokenAddress', 'Unknown')
                token_name = token_account.get('tokenName', 'Unknown')
                amount = float(token_account.get('amount', 0))
                
                # Check if token name matches suspicious patterns
                is_suspicious = any(
                    pattern.lower() in token_name.lower() 
                    for pattern in SUSPICIOUS_TOKEN_PATTERNS
                )
                
                if amount > 0:
                    tokens.append({
                        'address': token_address,
                        'name': token_name,
                        'amount': amount,
                        'suspicious_name': is_suspicious,
                        'risk_flag': 'potential_rug_token' if is_suspicious else 'unknown'
                    })
        
        return tokens
    
    async def analyze_single_counterparty(self, address: str, metadata: Dict) -> CounterpartyAnalysis:
        """
        Comprehensive analysis of a single counterparty
        """
        # Get token holdings
        other_tokens = await self.analyze_counterparty_tokens(address)
        
        # Analyze for suspicious patterns
        suspicious_activities = []
        
        # Check for meme token concentration
        meme_tokens = [t for t in other_tokens if t.get('suspicious_name')]
        if len(meme_tokens) >= 3:
            suspicious_activities.append(f"Holds {len(meme_tokens)} meme/suspicious tokens")
        
        # Check for high CRM volume
        if metadata['total_crm_volume'] > 1000000:  # 1M+ CRM
            suspicious_activities.append(f"High CRM volume: {metadata['total_crm_volume']:,.0f}")
        
        # Determine network tier
        if metadata['interaction_count'] >= 50:
            network_tier = "heavy_intermediary"
        elif metadata['interaction_count'] >= 10:
            network_tier = "active_counterparty"
        elif any('received_from_network' in t for t in metadata['interaction_types']):
            network_tier = "victim"
        else:
            network_tier = "exchange_or_bridge"
        
        # Calculate risk score
        risk_score = 0.0
        risk_score += min(0.3, len(meme_tokens) * 0.1)  # Up to 0.3 for meme tokens
        risk_score += min(0.3, metadata['interaction_count'] * 0.01)  # Up to 0.3 for activity
        risk_score += 0.2 if len(suspicious_activities) > 0 else 0  # 0.2 for any suspicious activity
        
        return CounterpartyAnalysis(
            address=address,
            crm_interaction_type=list(metadata['interaction_types'])[0] if metadata['interaction_types'] else 'unknown',
            crm_transaction_count=metadata['interaction_count'],
            other_tokens_held=other_tokens,
            suspicious_activities=suspicious_activities,
            risk_score=risk_score,
            network_tier=network_tier
        )
    
    async def find_cross_project_connections(self, analysis: CounterpartyAnalysis) -> List[CrossProjectFinding]:
        """
        Find cross-project connections based on counterparty analysis
        """
        findings = []
        
        # Check each token held
        for token in analysis.other_tokens_held:
            # Skip CRM itself
            if 'CRM' in token.get('name', '').upper() or token.get('address') == 'Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS':
                continue
            
            # If it's a suspicious meme token, flag it
            if token.get('suspicious_name'):
                finding = CrossProjectFinding(
                    source_wallet=analysis.address,
                    counterparty=analysis.address,
                    token_address=token.get('address', 'Unknown'),
                    token_name=token.get('name', 'Unknown'),
                    finding_type="suspicious_meme_token_holder",
                    confidence=0.70,
                    evidence=[
                        f"Counterparty of CRM network holds {token.get('amount', 0):,.0f} {token.get('name')}",
                        f"CRM interactions: {analysis.crm_transaction_count} transactions"
                    ],
                    pattern_signature="meme_token_network_connection"
                )
                findings.append(finding)
        
        # If high-risk counterparty, flag for deeper investigation
        if analysis.risk_score >= 0.5:
            finding = CrossProjectFinding(
                source_wallet=analysis.address,
                counterparty=analysis.address,
                token_address="MULTI_TOKEN",
                token_name="High-Risk Network Node",
                finding_type="high_risk_counterparty",
                confidence=analysis.risk_score,
                evidence=[
                    f"Risk Score: {analysis.risk_score:.2f}",
                    f"Suspicious activities: {', '.join(analysis.suspicious_activities)}"
                ],
                pattern_signature="high_risk_network_connection"
            )
            findings.append(finding)
        
        return findings
    
    async def run_analysis(self) -> Dict:
        """
        Run complete counterparty network analysis
        """
        print("\n" + "="*70)
        print("🔍 COUNTERPARTY NETWORK EXPANSION ANALYZER")
        print("="*70)
        print(f"Analysis Date: {datetime.now().isoformat()}")
        print("Strategy: Analyzing counterparties of wiped CRM network wallets")
        print("="*70 + "\n")
        
        # Step 1: Load existing transaction exports
        print("📂 Loading CRM transaction exports...")
        transactions_by_wallet = self.load_crm_transactions_from_exports()
        
        total_transactions = sum(len(txs) for txs in transactions_by_wallet.values())
        print(f"   Loaded {total_transactions} transactions across {len(transactions_by_wallet)} wallets\n")
        
        # Step 2: Extract all counterparties
        print("🔗 Extracting counterparties from transactions...")
        all_counterparties = {}
        
        for wallet, transactions in transactions_by_wallet.items():
            wallet_counterparties = self.extract_counterparties(transactions)
            print(f"   {wallet[:20]}...: {len(wallet_counterparties)} counterparties")
            
            # Merge into global counterparty list
            for address, metadata in wallet_counterparties.items():
                if address in all_counterparties:
                    # Merge metadata
                    all_counterparties[address]['interaction_count'] += metadata['interaction_count']
                    all_counterparties[address]['total_crm_volume'] += metadata['total_crm_volume']
                    all_counterparties[address]['interaction_types'].update(metadata['interaction_types'])
                else:
                    all_counterparties[address] = metadata
        
        print(f"\n   Total unique counterparties identified: {len(all_counterparties)}\n")
        
        # Step 3: Analyze top counterparties (limit to avoid rate limiting)
        print("🔍 Analyzing top counterparties for cross-project connections...")
        sorted_counterparties = sorted(
            all_counterparties.items(),
            key=lambda x: x[1]['interaction_count'],
            reverse=True
        )[:50]  # Top 50 by activity
        
        all_findings = []
        analyzed_counterparties = []
        
        for address, metadata in sorted_counterparties:
            try:
                analysis = await self.analyze_single_counterparty(address, metadata)
                analyzed_counterparties.append(analysis)
                
                # Find cross-project connections
                findings = await self.find_cross_project_connections(analysis)
                all_findings.extend(findings)
                
                if findings:
                    print(f"   ⚠️  {address[:20]}... - {len(findings)} findings")
                    for f in findings:
                        print(f"      └─ {f.token_name}: {f.finding_type}")
                
                # Rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"   ❌ Error analyzing {address[:20]}: {e}")
        
        # Step 4: Compile report
        print("\n" + "="*70)
        print("📊 COMPILING CROSS-PROJECT INTELLIGENCE REPORT")
        print("="*70 + "\n")
        
        # Group findings by token
        findings_by_token = defaultdict(list)
        for finding in all_findings:
            findings_by_token[finding.token_name].append(finding)
        
        # Identify most connected projects
        project_connections = sorted(
            [(token, len(findings)) for token, findings in findings_by_token.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        report = {
            "investigation_id": "COUNTERPARTY-CROSS-PROJECT-001",
            "timestamp": datetime.now().isoformat(),
            "total_counterparties_analyzed": len(analyzed_counterparties),
            "total_findings": len(all_findings),
            "high_risk_counterparties": len([c for c in analyzed_counterparties if c.risk_score >= 0.5]),
            
            "cross_project_connections": {
                token: {
                    "connection_count": len(findings),
                    "wallet_addresses": list(set([f.counterparty for f in findings])),
                    "avg_confidence": sum(f.confidence for f in findings) / len(findings) if findings else 0
                }
                for token, findings in findings_by_token.items()
            },
            
            "top_connected_projects": [
                {
                    "token": token,
                    "network_connections": count,
                    "suspicion_level": "HIGH" if count >= 5 else "MEDIUM" if count >= 2 else "LOW"
                }
                for token, count in project_connections[:10]
            ],
            
            "high_risk_nodes": [
                {
                    "address": c.address,
                    "risk_score": c.risk_score,
                    "crm_transactions": c.crm_transaction_count,
                    "suspicious_activities": c.suspicious_activities,
                    "tokens_held": len(c.other_tokens_held)
                }
                for c in sorted(analyzed_counterparties, key=lambda x: x.risk_score, reverse=True)
                if c.risk_score >= 0.5
            ][:20],
            
            "all_counterparty_analyses": [asdict(c) for c in analyzed_counterparties],
            "all_findings": [asdict(f) for f in all_findings],
            
            "recommended_actions": [
                "Export full transaction histories for top-connected projects",
                "Analyze timing correlation between CRM and other token dumps",
                "Map shared counterparties across all suspicious tokens",
                "Create master network graph showing all connections",
                "Check if high-risk nodes appear in other known scam investigations"
            ]
        }
        
        return report


async def main():
    """Main execution"""
    async with CounterpartyNetworkAnalyzer() as analyzer:
        report = await analyzer.run_analysis()
        
        # Save report
        output_path = "/root/crm_investigation/case_files/cross_token/counterparty_cross_project_analysis.json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*70)
        print("📊 CROSS-PROJECT ANALYSIS COMPLETE")
        print("="*70)
        print(f"Counterparties Analyzed: {report['total_counterparties_analyzed']}")
        print(f"Total Cross-Project Findings: {report['total_findings']}")
        print(f"High-Risk Network Nodes: {report['high_risk_counterparties']}")
        print(f"\nTop Connected Projects:")
        for proj in report['top_connected_projects'][:5]:
            print(f"   • {proj['token']}: {proj['network_connections']} connections ({proj['suspicion_level']})")
        print(f"\nReport saved: {output_path}")
        print("="*70 + "\n")
        
        return report


if __name__ == "__main__":
    asyncio.run(main())
