"""
Evidence Processor
Process categorized files into structured investigation data
"""

import os
import re
import json
import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from bs4 import BeautifulSoup
import csv
import io

logger = logging.getLogger(__name__)

class EvidenceProcessor:
    """Process raw evidence files into structured data"""
    
    def __init__(self):
        self.processed_evidence = []
        self.wallets_database = {}
        self.timeline_events = []
        self.connections_graph = {}
    
    def process_file(self, file_info: Dict) -> Optional[Dict]:
        """Process a single file based on its category"""
        category = file_info.get('category', 'uncategorized')
        file_path = file_info.get('path')
        
        processor_map = {
            'telegram_chats': self._process_telegram_html,
            'wallet_data': self._process_wallet_data,
            'visual_evidence': self._process_visual,
            'forensic_reports': self._process_forensic_report,
            'architecture_docs': self._process_architecture_doc,
            'compressed_archives': self._process_archive
        }
        
        processor = processor_map.get(category)
        if processor:
            try:
                return processor(file_path, file_info)
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
        
        return None
    
    def _process_telegram_html(self, file_path: str, file_info: Dict) -> Dict:
        """Process Telegram HTML exports"""
        logger.info(f"Processing Telegram chat: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Extract chat name
        chat_name = "Unknown"
        header = soup.find('div', class_='page_header')
        if header:
            chat_name = header.get_text(strip=True)
        
        # Extract messages
        messages = []
        for msg_div in soup.find_all('div', class_='message'):
            try:
                # Get message text
                text_div = msg_div.find('div', class_='text')
                text = text_div.get_text(strip=True) if text_div else ''
                
                # Get sender
                from_name = msg_div.get('data-from', 'Unknown')
                
                # Get date
                date_elem = msg_div.find('div', class_='date')
                date = date_elem.get('title', '') if date_elem else ''
                
                # Extract wallets from message
                wallets = self._extract_wallets_from_text(text)
                
                msg_data = {
                    'from': from_name,
                    'text': text[:500],  # Truncate long messages
                    'date': date,
                    'wallets_mentioned': wallets,
                    'has_crypto_terms': any(term in text.lower() for term in 
                                          ['token', 'scam', 'wallet', 'sol', 'eth'])
                }
                
                messages.append(msg_data)
                
                # Add to timeline if date available
                if date:
                    self.timeline_events.append({
                        'date': date,
                        'type': 'telegram_message',
                        'source': chat_name,
                        'content': text[:200],
                        'wallets': wallets
                    })
                
            except Exception as e:
                logger.warning(f"Failed to parse message: {e}")
        
        evidence = {
            'type': 'telegram_chat',
            'source_file': file_info['filename'],
            'chat_name': chat_name,
            'message_count': len(messages),
            'messages': messages[:100],  # Store first 100
            'wallets_found': list(set(w for m in messages for w in m['wallets_mentioned'])),
            'key_topics': self._extract_topics(messages),
            'processed_at': datetime.now().isoformat()
        }
        
        self.processed_evidence.append(evidence)
        return evidence
    
    def _process_wallet_data(self, file_path: str, file_info: Dict) -> Dict:
        """Process wallet/transaction CSV or text files"""
        logger.info(f"Processing wallet data: {file_path}")
        
        wallets = []
        transactions = []
        
        # Try CSV parsing first
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check if it's CSV-like
            if ',' in content[:1000]:
                reader = csv.DictReader(io.StringIO(content))
                for row in reader:
                    # Look for wallet addresses in any column
                    for key, value in row.items():
                        if value and len(value) >= 32:
                            wallet = self._clean_wallet_address(value)
                            if wallet:
                                wallets.append({
                                    'address': wallet,
                                    'source_file': file_info['filename'],
                                    'metadata': row
                                })
            else:
                # Treat as text file with one address per line
                for line in content.split('\n'):
                    wallet = self._clean_wallet_address(line.strip())
                    if wallet:
                        wallets.append({
                            'address': wallet,
                            'source_file': file_info['filename']
                        })
        
        except Exception as e:
            logger.error(f"Failed to parse wallet file: {e}")
        
        # Add to wallets database
        for w in wallets:
            addr = w['address']
            if addr not in self.wallets_database:
                self.wallets_database[addr] = {
                    'first_seen': file_info['filename'],
                    'mentions': 1,
                    'files': [file_info['filename']]
                }
            else:
                self.wallets_database[addr]['mentions'] += 1
                if file_info['filename'] not in self.wallets_database[addr]['files']:
                    self.wallets_database[addr]['files'].append(file_info['filename'])
        
        evidence = {
            'type': 'wallet_data',
            'source_file': file_info['filename'],
            'wallets_count': len(wallets),
            'wallets': wallets[:50],  # Store first 50
            'tags': file_info.get('tags', []),
            'processed_at': datetime.now().isoformat()
        }
        
        self.processed_evidence.append(evidence)
        return evidence
    
    def _process_visual(self, file_path: str, file_info: Dict) -> Dict:
        """Process images (screenshots)"""
        logger.info(f"Processing visual evidence: {file_path}")
        
        # For now, just catalog the image
        # OCR would be added here with pytesseract
        
        evidence = {
            'type': 'visual_evidence',
            'source_file': file_info['filename'],
            'size_bytes': file_info.get('size', 0),
            'is_screenshot': 'screenshot' in file_info['filename'].lower(),
            'potential_date': self._extract_date_from_filename(file_info['filename']),
            'tags': file_info.get('tags', []),
            'notes': 'OCR processing pending',
            'processed_at': datetime.now().isoformat()
        }
        
        self.processed_evidence.append(evidence)
        return evidence
    
    def _process_forensic_report(self, file_path: str, file_info: Dict) -> Dict:
        """Process forensic report text files"""
        logger.info(f"Processing forensic report: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Extract all wallets
        wallets = self._extract_all_wallets(content)
        
        # Extract key findings
        findings = []
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if any(marker in line.lower() for marker in ['finding:', 'key:', 'alert:', 'warning:']):
                findings.append({
                    'line': i,
                    'text': line.strip()[:200]
                })
        
        evidence = {
            'type': 'forensic_report',
            'source_file': file_info['filename'],
            'content_hash': hashlib.md5(content.encode()).hexdigest()[:16],
            'wallets_found': wallets,
            'key_findings': findings[:20],
            'sosana_related': file_info.get('sosana_related', False),
            'size_chars': len(content),
            'processed_at': datetime.now().isoformat()
        }
        
        self.processed_evidence.append(evidence)
        return evidence
    
    def _process_architecture_doc(self, file_path: str, file_info: Dict) -> Dict:
        """Process architecture/design documents"""
        logger.info(f"Processing architecture doc: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(50000)  # First 50KB
        except:
            content = ''
        
        # Extract features mentioned
        features = []
        feature_keywords = [
            'bot', 'scanner', 'risk', 'wallet', 'chart', 'telegram',
            'api', 'database', 'scrape', 'alert', 'monitor'
        ]
        
        for keyword in feature_keywords:
            if keyword in content.lower():
                features.append(keyword)
        
        evidence = {
            'type': 'architecture_doc',
            'source_file': file_info['filename'],
            'features_mentioned': features,
            'has_code_snippets': '```' in content or 'def ' in content,
            'is_nvidia_plan': 'nvidia' in file_info['filename'].lower(),
            'processed_at': datetime.now().isoformat()
        }
        
        self.processed_evidence.append(evidence)
        return evidence
    
    def _process_archive(self, file_path: str, file_info: Dict) -> Dict:
        """Process ZIP archives"""
        logger.info(f"Archive found (extract separately): {file_path}")
        
        evidence = {
            'type': 'compressed_archive',
            'source_file': file_info['filename'],
            'size_mb': file_info.get('size', 0) / (1024 * 1024),
            'status': 'needs_extraction',
            'processed_at': datetime.now().isoformat()
        }
        
        self.processed_evidence.append(evidence)
        return evidence
    
    # ═══════════════════════════════════════════════════════════
    # HELPER METHODS
    # ═══════════════════════════════════════════════════════════
    
    def _extract_wallets_from_text(self, text: str) -> List[str]:
        """Extract wallet addresses from text"""
        wallets = []
        
        # Solana pattern
        sol_pattern = r'[A-HJ-NP-Za-km-z1-9]{32,44}'
        for match in re.findall(sol_pattern, text):
            if len(match) >= 32:  # Valid Solana length
                wallets.append(('solana', match))
        
        # Ethereum pattern
        eth_pattern = r'0x[a-fA-F0-9]{40}'
        for match in re.findall(eth_pattern, text):
            wallets.append(('ethereum', match))
        
        return wallets
    
    def _extract_all_wallets(self, text: str) -> List[Dict]:
        """Extract all wallet addresses with context"""
        wallets = []
        seen = set()
        
        patterns = [
            (r'[A-HJ-NP-Za-km-z1-9]{32,44}', 'solana'),
            (r'0x[a-fA-F0-9]{40}', 'ethereum'),
        ]
        
        for pattern, chain in patterns:
            for match in re.findall(pattern, text):
                if match not in seen and len(match) >= 32:
                    seen.add(match)
                    
                    # Find context (text around wallet)
                    idx = text.find(match)
                    context = text[max(0, idx-50):min(len(text), idx+50)]
                    
                    wallets.append({
                        'address': match,
                        'chain': chain,
                        'context': context.replace('\n', ' ')
                    })
        
        return wallets
    
    def _clean_wallet_address(self, text: str) -> Optional[str]:
        """Clean and validate wallet address"""
        if not text:
            return None
        
        # Remove common prefixes/suffixes
        text = text.strip().replace('`', '').replace("'", '').replace('"', '')
        
        # Check if it's a wallet
        if len(text) >= 32 and len(text) <= 50:
            # Basic validation - should be alphanumeric
            if text.isalnum() or (text.startswith('0x') and len(text) == 42):
                return text
        
        return None
    
    def _extract_topics(self, messages: List[Dict]) -> List[str]:
        """Extract key topics from messages"""
        topics = []
        
        all_text = ' '.join([m.get('text', '').lower() for m in messages])
        
        topic_keywords = {
            'wallets': ['wallet', 'address'],
            'trading': ['buy', 'sell', 'trade', 'pump', 'dump'],
            'scam': ['scam', 'rug', 'honeypot'],
            'sosana': ['sosana', 'sosanna'],
            'crm': ['crm token', '$crm'],
            'investigation': ['investigate', 'forensic', 'track']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(kw in all_text for kw in keywords):
                topics.append(topic)
        
        return topics
    
    def _extract_date_from_filename(self, filename: str) -> Optional[str]:
        """Try to extract date from screenshot filename"""
        # Pattern: Screenshot_2026-03-30_020116
        match = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
        if match:
            return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
        return None
    
    # ═══════════════════════════════════════════════════════════
    # EXPORT METHODS
    # ═══════════════════════════════════════════════════════════
    
    def export_to_supabase(self, supabase_client):
        """Export processed evidence to Supabase"""
        try:
            # Export wallets
            if self.wallets_database:
                wallet_records = []
                for addr, data in self.wallets_database.items():
                    wallet_records.append({
                        'address': addr,
                        'first_seen_file': data['first_seen'],
                        'mention_count': data['mentions'],
                        'source_files': data['files'],
                        'investigation_id': 'sosana-2024'
                    })
                
                supabase_client.table('investigation_wallets').insert(wallet_records).execute()
                logger.info(f"Exported {len(wallet_records)} wallets to Supabase")
            
            # Export timeline
            if self.timeline_events:
                supabase_client.table('investigation_timeline').insert(
                    self.timeline_events
                ).execute()
                logger.info(f"Exported {len(self.timeline_events)} timeline events")
            
            # Export evidence summary
            if self.processed_evidence:
                supabase_client.table('processed_evidence').insert(
                    self.processed_evidence
                ).execute()
                logger.info(f"Exported {len(self.processed_evidence)} evidence items")
        
        except Exception as e:
            logger.error(f"Failed to export to Supabase: {e}")
    
    def save_report(self, output_path: str = '/root/rmi/investigation/evidence_report.json'):
        """Save full evidence report"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_evidence_items': len(self.processed_evidence),
            'unique_wallets': len(self.wallets_database),
            'timeline_events': len(self.timeline_events),
            'wallets_database': self.wallets_database,
            'timeline': sorted(self.timeline_events, key=lambda x: x.get('date', '')),
            'evidence_summary': self.processed_evidence
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Evidence report saved to {output_path}")
        return report


# Singleton
_processor = None

def get_processor() -> EvidenceProcessor:
    """Get singleton processor"""
    global _processor
    if _processor is None:
        _processor = EvidenceProcessor()
    return _processor
