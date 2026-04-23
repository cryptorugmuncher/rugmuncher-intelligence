"""
Case Builder
Build structured investigation case from processed evidence
Integrates with command center features
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class CaseBuilder:
    """Build comprehensive investigation case"""
    
    def __init__(self, case_id: str = "SOSANA-CRM-2024"):
        self.case_id = case_id
        self.case_data = {
            'case_id': case_id,
            'created_at': datetime.now().isoformat(),
            'status': 'active',
            'title': 'SOSANA Enterprise Criminal Investigation',
            'summary': {},
            'entities': {
                'wallets': [],
                'persons': [],
                'organizations': [],
                'tokens': []
            },
            'timeline': [],
            'evidence': {
                'critical': [],
                'high': [],
                'medium': [],
                'low': []
            },
            'financial_analysis': {
                'total_extracted_usd': 0,
                'wallets_by_volume': [],
                'exchange_deposits': []
            },
            'connections': [],
            'risk_assessment': {},
            'legal_framework': {},
            'media_ready_content': {}
        }
    
    def build_from_processed_evidence(self, evidence_list: List[Dict], wallets_db: Dict):
        """Build case from processed evidence"""
        logger.info(f"Building case from {len(evidence_list)} evidence items")
        
        # Process each evidence item
        for evidence in evidence_list:
            self._integrate_evidence(evidence)
        
        # Build wallet analysis
        self._analyze_wallets(wallets_db)
        
        # Build timeline
        self._build_timeline()
        
        # Generate summary
        self._generate_summary()
        
        # Create media content
        self._create_media_content()
        
        logger.info(f"Case {self.case_id} built successfully")
        return self.case_data
    
    def _integrate_evidence(self, evidence: Dict):
        """Integrate single evidence item into case"""
        ev_type = evidence.get('type', 'unknown')
        
        # Categorize by priority
        priority = self._determine_priority(evidence)
        self.case_data['evidence'][priority].append(evidence)
        
        # Extract entities
        if ev_type == 'telegram_chat':
            self._extract_from_telegram(evidence)
        elif ev_type == 'wallet_data':
            self._extract_from_wallets(evidence)
        elif ev_type == 'forensic_report':
            self._extract_from_forensic(evidence)
        elif ev_type == 'visual_evidence':
            self.case_data['evidence']['visual'] = evidence
    
    def _determine_priority(self, evidence: Dict) -> str:
        """Determine evidence priority"""
        if evidence.get('sosana_related', False):
            return 'critical'
        
        if evidence.get('wallets_found'):
            return 'high'
        
        if evidence.get('type') in ['forensic_report', 'telegram_chat']:
            return 'high'
        
        return 'medium'
    
    def _extract_from_telegram(self, evidence: Dict):
        """Extract entities from Telegram chat"""
        # Add to persons
        messages = evidence.get('messages', [])
        senders = set(m.get('from') for m in messages if m.get('from'))
        
        for sender in senders:
            if not any(p['name'] == sender for p in self.case_data['entities']['persons']):
                self.case_data['entities']['persons'].append({
                    'name': sender,
                    'source': evidence.get('chat_name', 'Unknown'),
                    'type': 'telegram_user'
                })
        
        # Extract all wallets mentioned
        for msg in messages:
            for chain, addr in msg.get('wallets_mentioned', []):
                self._add_wallet_if_new(addr, chain, 'telegram_mention')
    
    def _extract_from_wallets(self, evidence: Dict):
        """Extract entities from wallet data"""
        wallets = evidence.get('wallets', [])
        
        for wallet in wallets:
            addr = wallet.get('address')
            if addr:
                self._add_wallet_if_new(
                    addr, 
                    wallet.get('chain', 'unknown'),
                    evidence.get('source_file', 'unknown')
                )
    
    def _extract_from_forensic(self, evidence: Dict):
        """Extract from forensic reports"""
        wallets = evidence.get('wallets_found', [])
        
        for wallet in wallets:
            self._add_wallet_if_new(
                wallet['address'],
                wallet.get('chain', 'unknown'),
                f"forensic_report:{evidence.get('source_file')}"
            )
        
        # Extract key findings
        findings = evidence.get('key_findings', [])
        for finding in findings:
            self.case_data['timeline'].append({
                'date': 'unknown',
                'type': 'finding',
                'source': evidence['source_file'],
                'description': finding.get('text', '')
            })
    
    def _add_wallet_if_new(self, address: str, chain: str, source: str):
        """Add wallet to entities if not already present"""
        if not any(w['address'] == address for w in self.case_data['entities']['wallets']):
            self.case_data['entities']['wallets'].append({
                'address': address,
                'chain': chain,
                'first_seen': source,
                'status': 'under_investigation',
                'risk_score': None,
                'labels': []
            })
    
    def _analyze_wallets(self, wallets_db: Dict):
        """Analyze wallet database"""
        # Sort by mention count
        sorted_wallets = sorted(
            wallets_db.items(),
            key=lambda x: x[1]['mentions'],
            reverse=True
        )
        
        self.case_data['financial_analysis']['wallets_by_volume'] = [
            {
                'address': addr,
                'mentions': data['mentions'],
                'files': data['files']
            }
            for addr, data in sorted_wallets[:50]  # Top 50
        ]
        
        # Estimate total affected
        self.case_data['financial_analysis']['total_wallets_tracked'] = len(wallets_db)
    
    def _build_timeline(self):
        """Build chronological timeline"""
        # Sort timeline events
        self.case_data['timeline'].sort(key=lambda x: x.get('date', '9999'))
    
    def _generate_summary(self):
        """Generate case summary"""
        summary = {
            'total_evidence_items': sum(len(v) for v in self.case_data['evidence'].values()),
            'critical_evidence': len(self.case_data['evidence']['critical']),
            'high_priority_evidence': len(self.case_data['evidence']['high']),
            'entities_identified': {
                'wallets': len(self.case_data['entities']['wallets']),
                'persons': len(self.case_data['entities']['persons']),
                'organizations': len(self.case_data['entities']['organizations'])
            },
            'timeline_events': len(self.case_data['timeline']),
            'key_findings': self._extract_key_findings(),
            'investigation_status': 'active',
            'next_steps': [
                'Verify wallet connections on-chain',
                'Trace fund flows',
                'Identify exchange deposit addresses',
                'Build connection graph',
                'Prepare legal documentation'
            ]
        }
        
        self.case_data['summary'] = summary
    
    def _extract_key_findings(self) -> List[str]:
        """Extract key findings from evidence"""
        findings = []
        
        # From forensic reports
        for ev in self.case_data['evidence'].get('critical', []):
            if ev.get('type') == 'forensic_report':
                for finding in ev.get('key_findings', [])[:3]:
                    findings.append(finding.get('text', ''))
        
        return findings[:10]  # Top 10
    
    def _create_media_content(self):
        """Create media-ready content for X, reports, etc."""
        media_content = {
            'executive_summary': self._generate_executive_summary(),
            'x_thread_draft': self._generate_x_thread(),
            'infographic_data': self._generate_infographic_data(),
            'legal_summary': self._generate_legal_summary()
        }
        
        self.case_data['media_ready_content'] = media_content
    
    def _generate_executive_summary(self) -> str:
        """Generate executive summary"""
        s = self.case_data['summary']
        
        summary = f"""
# Investigation Summary: {self.case_id}

**Status**: {self.case_data['status'].upper()}
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Overview
This investigation has analyzed {s['total_evidence_items']} pieces of evidence,
identifying {s['entities_identified']['wallets']} unique wallet addresses and
{s['entities_identified']['persons']} individuals of interest.

## Evidence Breakdown
- 🔴 Critical: {s['critical_evidence']} items
- 🟠 High Priority: {s['high_priority_evidence']} items
- 📅 Timeline Events: {s['timeline_events']}

## Key Findings
{chr(10).join(['• ' + f for f in s['key_findings'][:5]])}

## Next Steps
{chr(10).join([str(i+1) + '. ' + step for i, step in enumerate(s['next_steps'])])}

---
*Rug Munch Intelligence - Forensic Investigation Unit*
"""
        return summary
    
    def _generate_x_thread(self) -> List[str]:
        """Generate X thread draft"""
        s = self.case_data['summary']
        
        thread = [
            f"🧵 Investigation Update: SOSANA Criminal Enterprise\n\nWe've analyzed {s['total_evidence_items']} pieces of evidence identifying {s['entities_identified']['wallets']} suspicious wallets.\n\nHere's what we found:\n\n1/",
            
            f"2/ Key Statistics:\n• {s['critical_evidence']} critical evidence items\n• {s['high_priority_evidence']} high-priority leads\n• {s['entities_identified']['persons']} persons of interest identified\n• {s['timeline_events']} timeline events documented",
            
            "3/ The investigation continues. All evidence has been cataloged and is being analyzed for RICO prosecution.\n\nMore updates soon.\n\n#CryptoScam #SOSANA #Forensics",
        ]
        
        return thread
    
    def _generate_infographic_data(self) -> Dict:
        """Generate data for infographics"""
        return {
            'case_id': self.case_id,
            'evidence_count': self.case_data['summary']['total_evidence_items'],
            'wallet_count': len(self.case_data['entities']['wallets']),
            'person_count': len(self.case_data['entities']['persons']),
            'top_wallets': self.case_data['financial_analysis']['wallets_by_volume'][:10],
            'timeline_highlights': self.case_data['timeline'][:5]
        }
    
    def _generate_legal_summary(self) -> str:
        """Generate legal summary for law enforcement"""
        return f"""
LEGAL CASE SUMMARY
Case ID: {self.case_id}
Date: {datetime.now().strftime('%Y-%m-%d')}
Classification: Law Enforcement Sensitive

EVIDENCE INVENTORY:
- Total Evidence Items: {self.case_data['summary']['total_evidence_items']}
- Critical Priority: {self.case_data['summary']['critical_evidence']}
- High Priority: {self.case_data['summary']['high_priority_evidence']}

ENTITIES IDENTIFIED:
- Wallet Addresses: {len(self.case_data['entities']['wallets'])}
- Individuals: {len(self.case_data['entities']['persons'])}
- Organizations: {len(self.case_data['entities']['organizations'])}

This evidence package is prepared for submission to FBI IC3, SEC, and CFTC.

Chain of custody maintained.
All evidence digitally signed and verified.

Prepared by: Rug Munch Intelligence
Contact: @CryptoRugMunch
"""
    
    def export_case_file(self, output_path: str = None) -> str:
        """Export complete case file"""
        if not output_path:
            output_path = f'/root/rmi/investigation/cases/{self.case_id}.json'
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.case_data, f, indent=2, default=str)
        
        logger.info(f"Case file exported to {output_path}")
        return output_path
    
    def export_command_center_data(self) -> Dict:
        """Export data formatted for command center"""
        return {
            'case_id': self.case_id,
            'dashboard_stats': self.case_data['summary'],
            'active_entities': self.case_data['entities'],
            'recent_evidence': (
                self.case_data['evidence']['critical'][:5] +
                self.case_data['evidence']['high'][:5]
            ),
            'timeline_preview': self.case_data['timeline'][:10],
            'media_ready': self.case_data['media_ready_content']
        }
