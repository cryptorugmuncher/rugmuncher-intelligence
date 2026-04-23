"""
File Categorizer for Investigation Evidence
Automatically categorize dumped files into investigation types
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from config import EVIDENCE_CATEGORIES, SOSANA_KEYWORDS, WALLET_PATTERNS

logger = logging.getLogger(__name__)

class FileCategorizer:
    """Automatically categorize investigation files"""
    
    def __init__(self, dumps_path: str = '/root/dumps/investigation-20260409/mixed'):
        self.dumps_path = dumps_path
        self.categorized = {cat: [] for cat in EVIDENCE_CATEGORIES.keys()}
        self.categorized['uncategorized'] = []
        self.wallet_addresses = set()
        self.sosana_mentions = 0
    
    def scan_all_files(self) -> Dict:
        """Scan dumps folder and categorize all files"""
        logger.info(f"Scanning {self.dumps_path}...")
        
        files = Path(self.dumps_path).glob('*')
        files = [f for f in files if f.is_file() and not f.name.endswith('.json')]
        
        total = len(files)
        logger.info(f"Found {total} files to categorize")
        
        for file_path in files:
            category = self._categorize_file(file_path)
            
            file_info = {
                'filename': file_path.name,
                'path': str(file_path),
                'size': file_path.stat().st_size,
                'extension': file_path.suffix.lower(),
                'category': category,
                'tags': self._extract_tags(file_path),
                'sosana_related': self._check_sosana_related(file_path),
                'wallets_found': self._extract_wallets_preview(file_path)
            }
            
            self.categorized[category].append(file_info)
            
            if file_info['sosana_related']:
                self.sosana_mentions += 1
        
        return self._generate_report()
    
    def _categorize_file(self, file_path: Path) -> str:
        """Determine category of a single file"""
        filename_lower = file_path.name.lower()
        extension = file_path.suffix.lower()
        
        for category, rules in EVIDENCE_CATEGORIES.items():
            # Check extension
            if extension in rules['extensions']:
                # Check patterns in filename
                if any(pattern in filename_lower for pattern in rules['patterns']):
                    return category
                
                # For some categories, extension is enough
                if category in ['visual_evidence', 'compressed_archives']:
                    return category
        
        # Special checks for forensic reports
        if extension == '.txt' and self._is_forensic_report(file_path):
            return 'forensic_reports'
        
        # Default
        return 'uncategorized'
    
    def _is_forensic_report(self, file_path: Path) -> bool:
        """Check if file contains forensic content"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(5000).lower()  # Read first 5KB
                
                forensic_terms = ['wallet', 'forensic', 'scam', 'investigation', 
                                 'on-chain', 'transaction', 'sosana', 'crm']
                return sum(1 for term in forensic_terms if term in content) >= 3
        except:
            return False
    
    def _extract_tags(self, file_path: Path) -> List[str]:
        """Extract relevant tags from filename"""
        filename_lower = file_path.name.lower()
        tags = []
        
        # SOSANA-related
        if 'sosana' in filename_lower or 'sosanna' in filename_lower:
            tags.append('sosana')
        
        # CRM-related
        if 'crm' in filename_lower:
            tags.append('crm')
        
        # Wallet-related
        if any(x in filename_lower for x in ['wallet', 'holder', 'transfer']):
            tags.append('wallets')
        
        # Export data
        if 'export' in filename_lower:
            tags.append('export_data')
        
        # Screenshots
        if 'screenshot' in filename_lower or 'photo' in filename_lower:
            tags.append('screenshot')
            
            # Try to extract date from screenshot filename
            date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', file_path.name)
            if date_match:
                tags.append(f"date_{date_match.group(0)}")
        
        return tags
    
    def _check_sosana_related(self, file_path: Path) -> bool:
        """Check if file is SOSANA-related"""
        filename_lower = file_path.name.lower()
        
        # Check filename
        if any(kw in filename_lower for kw in SOSANA_KEYWORDS):
            return True
        
        # Check content for text files
        if file_path.suffix.lower() in ['.txt', '.html', '.md', '.csv']:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(10000).lower()
                    if sum(1 for kw in SOSANA_KEYWORDS if kw in content) >= 2:
                        return True
            except:
                pass
        
        return False
    
    def _extract_wallets_preview(self, file_path: Path) -> List[str]:
        """Extract first few wallet addresses from file"""
        wallets = []
        
        if file_path.suffix.lower() not in ['.txt', '.csv', '.html']:
            return wallets
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(50000)  # First 50KB
                
                for chain, pattern in WALLET_PATTERNS.items():
                    matches = re.findall(pattern, content)
                    wallets.extend(matches[:5])  # First 5 of each type
                    self.wallet_addresses.update(matches)
        except:
            pass
        
        return wallets[:10]  # Max 10 per file
    
    def _generate_report(self) -> Dict:
        """Generate categorization report"""
        total_files = sum(len(files) for files in self.categorized.values())
        
        report = {
            'total_files': total_files,
            'categorized_at': datetime.now().isoformat(),
            'categories': {},
            'summary': {
                'sosana_related_files': self.sosana_mentions,
                'unique_wallets_found': len(self.wallet_addresses),
                'critical_evidence': 0,
                'high_priority': 0,
                'medium_priority': 0
            }
        }
        
        for category, files in self.categorized.items():
            if not files:
                continue
            
            priority = EVIDENCE_CATEGORIES.get(category, {}).get('priority', 'low')
            
            report['categories'][category] = {
                'count': len(files),
                'priority': priority,
                'total_size_mb': sum(f['size'] for f in files) / (1024 * 1024),
                'sosana_related': sum(1 for f in files if f['sosana_related']),
                'files': files[:10] if len(files) > 10 else files  # First 10 details
            }
            
            # Update priority counts
            if priority == 'critical':
                report['summary']['critical_evidence'] += len(files)
            elif priority == 'high':
                report['summary']['high_priority'] += len(files)
            elif priority == 'medium':
                report['summary']['medium_priority'] += len(files)
        
        # Add top wallets
        report['unique_wallets'] = list(self.wallet_addresses)[:50]  # Top 50
        
        return report
    
    def export_report(self, output_path: str = '/root/rmi/investigation/categorization_report.json'):
        """Export categorization report to JSON"""
        report = self.scan_all_files()
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Report exported to {output_path}")
        return report


# Singleton
_categorizer = None

def get_categorizer() -> FileCategorizer:
    """Get singleton categorizer"""
    global _categorizer
    if _categorizer is None:
        _categorizer = FileCategorizer()
    return _categorizer
