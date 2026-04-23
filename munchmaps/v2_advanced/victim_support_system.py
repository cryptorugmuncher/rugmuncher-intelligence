#!/usr/bin/env python3
"""
Victim Support System
Helps scam victims track stolen funds and support recovery efforts
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
import json

@dataclass
class VictimCase:
    case_id: str
    victim_id: str  # Anonymous identifier
    scam_type: str
    date_reported: str
    status: str  # 'active', 'investigating', 'recovered', 'closed'
    
    # Financial details
    total_lost_usd: float
    cryptocurrency_type: str
    stolen_amount_crypto: float
    
    # Wallet addresses
    victim_wallet_address: str
    scammer_addresses: List[str] = field(default_factory=list)
    intermediate_addresses: List[str] = field(default_factory=list)
    
    # Evidence
    transaction_hashes: List[str] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)
    communications: List[Dict] = field(default_factory=list)
    
    # Recovery tracking
    recovery_attempts: List[Dict] = field(default_factory=list)
    amount_recovered_usd: float = 0.0
    recovery_percentage: float = 0.0
    
    # Support assigned
    assigned_analyst: Optional[str] = None
    law_enforcement_case: Optional[str] = None
    priority: str = 'medium'  # 'low', 'medium', 'high', 'critical'


class VictimSupportSystem:
    """
    Comprehensive victim support for crypto scam recovery
    """
    
    def __init__(self):
        self.cases: Dict[str, VictimCase] = {}
        self.scammer_database: Dict[str, Dict] = {}
        self.recovery_partners = []
        
    def create_case(self, victim_data: Dict) -> VictimCase:
        """Create new victim case"""
        case_id = f"VS-{datetime.now().strftime('%Y%m%d')}-{len(self.cases)+1:04d}"
        
        case = VictimCase(
            case_id=case_id,
            victim_id=victim_data.get('anonymous_id', 'anonymous'),
            scam_type=victim_data.get('scam_type', 'unknown'),
            date_reported=datetime.now().isoformat(),
            status='active',
            total_lost_usd=victim_data.get('amount_lost_usd', 0),
            cryptocurrency_type=victim_data.get('crypto_type', 'unknown'),
            stolen_amount_crypto=victim_data.get('amount_crypto', 0),
            victim_wallet_address=victim_data.get('victim_address', ''),
            scammer_addresses=victim_data.get('scammer_addresses', []),
            priority=self._assess_priority(victim_data)
        )
        
        self.cases[case_id] = case
        
        # Update scammer database
        for addr in case.scammer_addresses:
            if addr not in self.scammer_database:
                self.scammer_database[addr] = {
                    'first_reported': datetime.now().isoformat(),
                    'victim_count': 0,
                    'total_stolen_usd': 0,
                    'cases': []
                }
            
            self.scammer_database[addr]['victim_count'] += 1
            self.scammer_database[addr]['total_stolen_usd'] += case.total_lost_usd
            self.scammer_database[addr]['cases'].append(case_id)
        
        return case
    
    def _assess_priority(self, victim_data: Dict) -> str:
        """Assess case priority based on severity"""
        amount = victim_data.get('amount_lost_usd', 0)
        
        if amount >= 100000:
            return 'critical'
        elif amount >= 50000:
            return 'high'
        elif amount >= 10000:
            return 'medium'
        return 'low'
    
    def track_funds(self, case_id: str, chain_analyzer) -> Dict:
        """Track stolen funds across chains"""
        case = self.cases.get(case_id)
        if not case:
            return {'error': 'Case not found'}
        
        tracking_results = {
            'case_id': case_id,
            'tracking_date': datetime.now().isoformat(),
            'scammer_addresses_tracked': {},
            'fund_movement': [],
            'cex_cashouts': [],
            'frozen_funds': [],
            'recovery_opportunities': []
        }
        
        for scammer_addr in case.scammer_addresses:
            # Analyze each scammer address
            result = chain_analyzer.analyze_address(scammer_addr)
            tracking_results['scammer_addresses_tracked'][scammer_addr] = result
            
            # Look for CEX cashouts
            if result.get('cex_interactions'):
                tracking_results['cex_cashouts'].append({
                    'address': scammer_addr,
                    'cex': result['cex_interactions']
                })
                
                # Opportunity: CEX can freeze if notified
                tracking_results['recovery_opportunities'].append({
                    'type': 'cex_freeze',
                    'address': scammer_addr,
                    'action': 'Contact exchange with court order'
                })
        
        return tracking_results
    
    def generate_recovery_plan(self, case_id: str) -> Dict:
        """Generate recovery action plan"""
        case = self.cases.get(case_id)
        if not case:
            return {'error': 'Case not found'}
        
        plan = {
            'case_id': case_id,
            'generated_at': datetime.now().isoformat(),
            'immediate_actions': [],
            'short_term_actions': [],
            'long_term_actions': [],
            'estimated_recovery_chance': 0.0,
            'estimated_recovery_amount': 0.0
        }
        
        # Immediate actions (first 24 hours)
        plan['immediate_actions'] = [
            {
                'action': 'Report to local law enforcement',
                'priority': 'CRITICAL',
                'timeframe': 'Within 24 hours',
                'resources': ['Police report', 'Transaction evidence']
            },
            {
                'action': 'Contact exchanges where funds moved',
                'priority': 'CRITICAL',
                'timeframe': 'Within 24 hours',
                'resources': ['Exchange support tickets', 'Tx hashes']
            },
            {
                'action': 'Preserve all evidence',
                'priority': 'HIGH',
                'timeframe': 'Immediately',
                'resources': ['Screenshots', 'Chat logs', 'Wallet addresses']
            }
        ]
        
        # Calculate recovery estimate
        if case.total_lost_usd > 0:
            # Based on scam type and timing
            if case.scam_type == 'pig_butcherer':
                plan['estimated_recovery_chance'] = 0.15  # 15% for pig butcherer
                plan['estimated_recovery_amount'] = case.total_lost_usd * 0.15
            elif case.scam_type == 'phishing':
                plan['estimated_recovery_chance'] = 0.05  # 5% for phishing
                plan['estimated_recovery_amount'] = case.total_lost_usd * 0.05
            elif case.scam_type == 'rug_pull':
                plan['estimated_recovery_chance'] = 0.02  # 2% for rug pull
                plan['estimated_recovery_amount'] = case.total_lost_usd * 0.02
        
        return plan
    
    def get_support_resources(self, victim_location: str = 'USA') -> List[Dict]:
        """Get support resources for victim"""
        resources = {
            'USA': [
                {
                    'name': 'FBI IC3',
                    'url': 'https://ic3.gov',
                    'phone': '1-800-CALL-FBI',
                    'type': 'law_enforcement'
                },
                {
                    'name': 'FTC Fraud Report',
                    'url': 'https://reportfraud.ftc.gov',
                    'type': 'regulatory'
                },
                {
                    'name': 'CFTC Tips',
                    'url': 'https://www.cftc.gov/tipline',
                    'type': 'regulatory'
                }
            ],
            'UK': [
                {
                    'name': 'Action Fraud',
                    'url': 'https://www.actionfraud.police.uk',
                    'phone': '0300 123 2040',
                    'type': 'law_enforcement'
                },
                {
                    'name': 'FCA Scam Reporting',
                    'url': 'https://www.fca.org.uk/consumers/report-scam',
                    'type': 'regulatory'
                }
            ],
            'EU': [
                {
                    'name': 'Europol EC3',
                    'url': 'https://www.europol.europa.eu/report-a-crime',
                    'type': 'law_enforcement'
                }
            ],
            'Global': [
                {
                    'name': 'Interpol',
                    'url': 'https://www.interpol.int/How-we-work/Notices/View-Red-Notices',
                    'type': 'international'
                },
                {
                    'name': 'Chainabuse',
                    'url': 'https://www.chainabuse.com',
                    'type': 'community'
                }
            ]
        }
        
        # Combine location-specific with global
        result = resources.get(victim_location, [])
        result.extend(resources['Global'])
        return result
    
    def generate_victim_report(self, case_id: str) -> Dict:
        """Generate comprehensive victim report for law enforcement"""
        case = self.cases.get(case_id)
        if not case:
            return {'error': 'Case not found'}
        
        report = {
            'report_type': 'VICTIM_STATEMENT',
            'case_id': case_id,
            'generated_at': datetime.now().isoformat(),
            'for_law_enforcement': True,
            
            'incident_summary': {
                'scam_type': case.scam_type,
                'date_occurred': case.date_reported,
                'total_loss_usd': case.total_lost_usd,
                'cryptocurrency': case.cryptocurrency_type,
                'amount_crypto': case.stolen_amount_crypto
            },
            
            'financial_details': {
                'victim_wallet': case.victim_wallet_address,
                'scammer_wallets': case.scammer_addresses,
                'transaction_hashes': case.transaction_hashes,
                'fiat_onramp': 'To be determined',
                'fiat_offramp_suspected': 'To be investigated'
            },
            
            'evidence_package': {
                'screenshots_count': len(case.screenshots),
                'communications_count': len(case.communications),
                'transaction_evidence': len(case.transaction_hashes),
                'digital_footprint': 'Available upon request'
            },
            
            'recommended_actions': [
                'Issue subpoena to exchanges where funds moved',
                'Request blockchain analysis from MunchMaps',
                'Cross-reference with known scammer databases',
                'Contact international partners if cross-border'
            ],
            
            'munchmaps_analysis': {
                'platform': 'MunchMaps V2 Master',
                'analyst_notes': 'Professional blockchain investigation',
                'confidence_level': 'High',
                'evidence_grade': 'Court-admissible'
            }
        }
        
        return report
    
    def get_statistics(self) -> Dict:
        """Get victim support statistics"""
        total_cases = len(self.cases)
        total_lost = sum(c.total_lost_usd for c in self.cases.values())
        total_recovered = sum(c.amount_recovered_usd for c in self.cases.values())
        
        by_scam_type = {}
        for case in self.cases.values():
            st = case.scam_type
            if st not in by_scam_type:
                by_scam_type[st] = {'count': 0, 'total_lost': 0}
            by_scam_type[st]['count'] += 1
            by_scam_type[st]['total_lost'] += case.total_lost_usd
        
        return {
            'total_cases_reported': total_cases,
            'total_amount_lost_usd': total_lost,
            'total_recovered_usd': total_recovered,
            'recovery_rate': (total_recovered / total_lost * 100) if total_lost > 0 else 0,
            'by_scam_type': by_scam_type,
            'known_scammers': len(self.scammer_database),
            'total_victims_helped': sum(s['victim_count'] for s in self.scammer_database.values())
        }


class RecoveryTracker:
    """
    Track recovery efforts and success rates
    """
    
    def __init__(self):
        self.recovery_attempts = []
        self.successful_recoveries = []
        
    def log_recovery_attempt(self, attempt: Dict):
        """Log a recovery attempt"""
        attempt['timestamp'] = datetime.now().isoformat()
        attempt['status'] = 'pending'
        self.recovery_attempts.append(attempt)
        return attempt
    
    def update_recovery_status(self, attempt_id: str, status: str, amount_recovered: float = 0):
        """Update status of recovery attempt"""
        for attempt in self.recovery_attempts:
            if attempt.get('id') == attempt_id:
                attempt['status'] = status
                attempt['amount_recovered'] = amount_recovered
                attempt['updated_at'] = datetime.now().isoformat()
                
                if status == 'successful' and amount_recovered > 0:
                    self.successful_recoveries.append(attempt)
                
                return attempt
        return None
    
    def get_recovery_statistics(self) -> Dict:
        """Get recovery success statistics"""
        total = len(self.recovery_attempts)
        successful = len(self.successful_recoveries)
        total_recovered = sum(r.get('amount_recovered', 0) for r in self.successful_recoveries)
        
        by_method = {}
        for attempt in self.recovery_attempts:
            method = attempt.get('method', 'unknown')
            if method not in by_method:
                by_method[method] = {'attempted': 0, 'successful': 0, 'amount': 0}
            
            by_method[method]['attempted'] += 1
            if attempt.get('status') == 'successful':
                by_method[method]['successful'] += 1
                by_method[method]['amount'] += attempt.get('amount_recovered', 0)
        
        return {
            'total_attempts': total,
            'successful_recoveries': successful,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'total_amount_recovered_usd': total_recovered,
            'by_recovery_method': by_method
        }


if __name__ == "__main__":
    print("Victim Support System initialized")
    print("Helping scam victims recover stolen cryptocurrency")
    
    # Demo
    support = VictimSupportSystem()
    
    # Create a case
    case = support.create_case({
        'scam_type': 'pig_butcherer',
        'amount_lost_usd': 150000,
        'crypto_type': 'USDT',
        'amount_crypto': 150000,
        'victim_address': '0x123...',
        'scammer_addresses': ['TABC...', '0xDEF...']
    })
    
    print(f"\nCreated case: {case.case_id}")
    print(f"Priority: {case.priority}")
    print(f"Status: {case.status}")
    
    # Get stats
    stats = support.get_statistics()
    print(f"\nTotal cases: {stats['total_cases_reported']}")
    print(f"Total lost: ${stats['total_amount_lost_usd']:,.2f}")
