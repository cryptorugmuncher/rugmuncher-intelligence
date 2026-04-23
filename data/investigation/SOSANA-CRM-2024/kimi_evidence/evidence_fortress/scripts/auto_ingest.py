"""
================================================================================
AUTO-INGEST: Drop Evidence, Auto-Classify & Store
Evidence Fortress v4.0

Usage:
    python scripts/auto_ingest.py --watch ./evidence/inbox
    
Or process existing files:
    python scripts/auto_ingest.py --input ./evidence/raw
================================================================================
"""

import os
import sys
import json
import csv
import hashlib
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
import asyncpg

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@dataclass
class EvidenceClassification:
    """Classification result for an evidence file."""
    file_path: str
    file_type: str
    evidence_category: str
    priority: str  # 'critical', 'high', 'medium', 'low'
    entities_found: List[str]
    summary: str
    related_case: str
    tags: List[str]


class EvidenceClassifier:
    """Auto-classify evidence files by type and content."""
    
    # File type patterns
    FILE_PATTERNS = {
        'solscan_transfer': ['export_transfer', '.csv'],
        'solscan_balance': ['export_balance_change', '.csv'],
        'solscan_holders': ['export_token_holders', '.csv'],
        'helius_transactions': ['transactions', '.json'],
        'pump_deployers': ['deployers', 'pump', '.csv'],
        'telegram_export': ['messages', '.html'],
        'chat_log': ['.txt'],
        'litepaper': ['litepaper', '.pdf'],
        'json_export': ['.json'],
    }
    
    # Entity patterns for auto-detection
    ENTITY_PATTERNS = {
        'sosana_treasury': ['Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS'],
        'botnet_seeder': ['AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6'],
        'crm_distributor': ['8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj'],
        'crm_token': ['HfMbPyDdZH6QMaDDUokjYCkHxzjoGBMpgaUvpLWGbF5p'],
        'intermediary': ['Cx5qTEtnp3arFVBuusMXHafoRzLCLuigtz2AiQAFmq2Q'],
        'sosana_token': ['49jdQxUkKtuvorvnwWqDzUoYKEjfgroTzHkQqXG9YFMj'],
    }
    
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
    
    async def classify_file(self, file_path: str) -> EvidenceClassification:
        """Auto-classify an evidence file."""
        filename = os.path.basename(file_path).lower()
        
        # Detect file type
        file_type = self._detect_file_type(filename)
        
        # Extract entities based on file type
        entities, summary = await self._extract_content(file_path, file_type)
        
        # Determine category and priority
        category, priority, tags = self._categorize(file_type, entities, filename)
        
        # Determine related case
        related_case = self._determine_case(filename, entities)
        
        return EvidenceClassification(
            file_path=file_path,
            file_type=file_type,
            evidence_category=category,
            priority=priority,
            entities_found=entities,
            summary=summary,
            related_case=related_case,
            tags=tags
        )
    
    def _detect_file_type(self, filename: str) -> str:
        """Detect the type of evidence file."""
        for file_type, patterns in self.FILE_PATTERNS.items():
            if all(p.lower() in filename for p in patterns):
                return file_type
        
        # Fallback detection
        if filename.endswith('.json'):
            return 'json_export'
        elif filename.endswith('.csv'):
            return 'csv_export'
        elif filename.endswith('.txt'):
            return 'text_log'
        elif filename.endswith('.pdf'):
            return 'document'
        
        return 'unknown'
    
    async def _extract_content(self, file_path: str, file_type: str) -> Tuple[List[str], str]:
        """Extract entities and summary from file."""
        entities = []
        summary = ""
        
        try:
            if file_type == 'helius_transactions':
                entities, summary = self._parse_helius_json(file_path)
            elif file_type == 'solscan_transfer':
                entities, summary = self._parse_solscan_csv(file_path, 'transfer')
            elif file_type == 'solscan_balance':
                entities, summary = self._parse_solscan_csv(file_path, 'balance')
            elif file_type == 'solscan_holders':
                entities, summary = self._parse_solscan_csv(file_path, 'holders')
            elif file_type == 'pump_deployers':
                entities, summary = self._parse_pump_deployers(file_path)
            elif file_type == 'telegram_export':
                entities, summary = self._parse_telegram_html(file_path)
            elif file_type == 'chat_log':
                entities, summary = self._parse_chat_log(file_path)
            elif file_type == 'litepaper':
                entities, summary = self._parse_litepaper(file_path)
            else:
                summary = f"File type {file_type} - manual review needed"
        except Exception as e:
            summary = f"Parse error: {str(e)}"
        
        return entities, summary
    
    def _parse_helius_json(self, file_path: str) -> Tuple[List[str], str]:
        """Parse Helius transaction export."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            data = [data]
        
        addresses = set()
        tx_count = len(data)
        
        for tx in data:
            # Extract fee payer
            if 'feePayer' in tx:
                addresses.add(tx['feePayer'])
            
            # Extract from native transfers
            for transfer in tx.get('nativeTransfers', []):
                addresses.add(transfer.get('fromUserAccount', ''))
                addresses.add(transfer.get('toUserAccount', ''))
            
            # Extract from token transfers
            for transfer in tx.get('tokenTransfers', []):
                addresses.add(transfer.get('fromUserAccount', ''))
                addresses.add(transfer.get('toUserAccount', ''))
                addresses.add(transfer.get('mint', ''))
        
        addresses.discard('')
        addresses.discard('11111111111111111111111111111111')
        
        summary = f"Helius export: {tx_count} transactions, {len(addresses)} unique addresses"
        return list(addresses), summary
    
    def _parse_solscan_csv(self, file_path: str, subtype: str) -> Tuple[List[str], str]:
        """Parse Solscan CSV export."""
        addresses = set()
        row_count = 0
        
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_count += 1
                
                if subtype == 'transfer':
                    addresses.add(row.get('From', ''))
                    addresses.add(row.get('To', ''))
                    addresses.add(row.get('Token Address', ''))
                elif subtype == 'balance':
                    addresses.add(row.get('TokenAccount', ''))
                    addresses.add(row.get('TokenAddress', ''))
                elif subtype == 'holders':
                    addresses.add(row.get('Account', ''))
                    addresses.add(row.get('Token Account', ''))
        
        addresses.discard('')
        summary = f"Solscan {subtype}: {row_count} rows, {len(addresses)} unique addresses"
        return list(addresses), summary
    
    def _parse_pump_deployers(self, file_path: str) -> Tuple[List[str], str]:
        """Parse Pump.fun deployers CSV."""
        addresses = []
        total_tokens = 0
        total_pnl = 0.0
        
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                addresses.append(row.get('address', ''))
                try:
                    total_tokens += int(row.get('token_deployed', 0))
                    total_pnl += float(row.get('total_pnl_usd', 0))
                except:
                    pass
        
        summary = f"Pump.fun deployers: {len(addresses)} addresses, {total_tokens} total tokens, ${total_pnl:,.2f} total PnL"
        return addresses, summary
    
    def _parse_telegram_html(self, file_path: str) -> Tuple[List[str], str]:
        """Parse Telegram Desktop HTML export."""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            return [], "BeautifulSoup not installed"
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Get chat title
        chat_title = ""
        title_elem = soup.find('div', class_='text bold')
        if title_elem:
            chat_title = title_elem.get_text(strip=True)
        
        # Extract messages
        messages = []
        message_divs = soup.find_all('div', class_=lambda x: x and 'message' in x and 'default' in x)
        
        current_sender = "Unknown"
        for msg_div in message_divs:
            if 'joined' not in msg_div.get('class', []):
                from_name_elem = msg_div.find('div', class_='from_name')
                if from_name_elem:
                    current_sender = from_name_elem.get_text(strip=True)
            
            text_elem = msg_div.find('div', class_='text')
            text = text_elem.get_text(strip=True) if text_elem else ""
            
            if text:
                messages.append({'sender': current_sender, 'text': text})
        
        # Extract addresses from all messages
        import re
        sol_pattern = re.compile(r'[1-9A-HJ-NP-Za-km-z]{32,44}')
        all_addresses = set()
        for msg in messages:
            addrs = sol_pattern.findall(msg['text'])
            all_addresses.update(a for a in addrs if len(a) >= 32)
        
        # Extract Telegram handles
        tg_pattern = re.compile(r'@(\w{3,32})')
        all_handles = set()
        for msg in messages:
            handles = tg_pattern.findall(msg['text'])
            all_handles.update(handles)
        
        participants = list(set(m['sender'] for m in messages))
        
        summary = f"Telegram '{chat_title}': {len(messages)} messages, {len(all_addresses)} addresses, {len(all_handles)} handles, participants: {', '.join(participants)}"
        return list(all_addresses), summary

    def _parse_chat_log(self, file_path: str) -> Tuple[List[str], str]:
        """Parse chat log for addresses and handles."""
        import re
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Find Solana addresses
        sol_pattern = re.compile(r'[1-9A-HJ-NP-Za-km-z]{32,44}')
        addresses = list(set(sol_pattern.findall(content)))
        
        # Find Telegram handles
        tg_pattern = re.compile(r'@(\w{5,32})')
        handles = list(set(tg_pattern.findall(content)))
        
        summary = f"Chat log: {len(addresses)} addresses, {len(handles)} Telegram handles"
        return addresses, summary
    
    def _parse_litepaper(self, file_path: str) -> Tuple[List[str], str]:
        """Parse litepaper for token addresses."""
        import re
        
        # For PDF, we'd need PyPDF2 - for now just extract from filename
        # In production, use: PyPDF2, pdfplumber, or pymupdf
        
        addresses = []
        
        # Try to read as text (some PDFs are text-extractable)
        try:
            with open(file_path, 'rb') as f:
                content = f.read().decode('utf-8', errors='ignore')
            
            sol_pattern = re.compile(r'[1-9A-HJ-NP-Za-km-z]{32,44}')
            addresses = list(set(sol_pattern.findall(content)))
        except:
            pass
        
        summary = f"Litepaper: {len(addresses)} addresses found"
        return addresses, summary
    
    def _categorize(self, file_type: str, entities: List[str], filename: str) -> Tuple[str, str, List[str]]:
        """Determine evidence category and priority."""
        
        # Check for known entities
        has_known_entity = any(
            any(pattern in addr for pattern in sum(self.ENTITY_PATTERNS.values(), []))
            for addr in entities
        )
        
        # Category mapping
        category_map = {
            'helius_transactions': ('transaction_data', 'high'),
            'solscan_transfer': ('transaction_data', 'high'),
            'solscan_balance': ('financial_record', 'medium'),
            'solscan_holders': ('ownership_record', 'medium'),
            'pump_deployers': ('threat_intelligence', 'critical'),
            'telegram_export': ('communication_record', 'critical'),
            'chat_log': ('communication_record', 'high'),
            'litepaper': ('project_documentation', 'medium'),
        }
        
        category, base_priority = category_map.get(file_type, ('uncategorized', 'low'))
        
        # Boost priority for known entities
        if has_known_entity:
            priority = 'critical' if base_priority == 'high' else 'high'
            tags = ['known_entity', 'sosana_related']
        else:
            priority = base_priority
            tags = []
        
        # Add file-specific tags
        if file_type == 'pump_deployers':
            tags.extend(['pump_fun', 'deployer_analysis', 'serial_rugger_risk'])
        elif file_type == 'telegram_export':
            tags.extend(['telegram', 'operational_intel', 'chat_evidence', 'crm_network'])
        elif file_type == 'chat_log':
            tags.extend(['telegram', 'operational_intel'])
        elif file_type == 'helius_transactions':
            tags.extend(['helius', 'on_chain'])
        
        return category, priority, tags
    
    def _determine_case(self, filename: str, entities: List[str]) -> str:
        """Determine which case this evidence relates to."""
        filename_lower = filename.lower()
        
        # Check filename indicators
        if 'sosana' in filename_lower:
            return 'SOSANA_RICO_2026'
        elif 'crm' in filename_lower:
            return 'CRM_INVESTIGATION_2026'
        elif 'pump' in filename_lower:
            return 'PUMP_FUN_ANALYSIS_2026'
        
        # Check entity indicators
        sosana_entities = self.ENTITY_PATTERNS.get('sosana_treasury', []) + \
                         self.ENTITY_PATTERNS.get('crm_distributor', [])
        
        if any(e in sosana_entities for e in entities):
            return 'SOSANA_RICO_2026'
        
        return 'GENERAL_CRYPTO_INVESTIGATION'


class AutoIngester:
    """Auto-ingest and classify evidence files."""
    
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
        self.classifier = EvidenceClassifier(db_pool)
    
    async def ingest_file(self, file_path: str) -> Dict:
        """Ingest a single file with auto-classification."""
        print(f"\n{'='*60}")
        print(f"Processing: {os.path.basename(file_path)}")
        print(f"{'='*60}")
        
        # Classify
        classification = await self.classifier.classify_file(file_path)
        
        print(f"Type: {classification.file_type}")
        print(f"Category: {classification.evidence_category}")
        print(f"Priority: {classification.priority.upper()}")
        print(f"Case: {classification.related_case}")
        print(f"Summary: {classification.summary}")
        print(f"Entities: {len(classification.entities_found)}")
        print(f"Tags: {', '.join(classification.tags)}")
        
        # Store in database
        evidence_id = await self._store_classification(classification)
        
        print(f"✓ Stored with ID: {evidence_id}")
        
        return {
            'evidence_id': evidence_id,
            'classification': asdict(classification)
        }
    
    async def _store_classification(self, classification: EvidenceClassification) -> str:
        """Store classification in database."""
        # Read and hash file
        with open(classification.file_path, 'rb') as f:
            content = f.read()
        
        evidence_hash = hashlib.sha256(content).hexdigest()
        
        # Check for duplicates
        async with self.db_pool.acquire() as conn:
            existing = await conn.fetchval(
                "SELECT id FROM evidence_vault WHERE evidence_hash = $1",
                evidence_hash
            )
            
            if existing:
                print(f"⚠ Duplicate detected: {existing}")
                return str(existing)
            
            # Insert new evidence
            from cryptography.fernet import Fernet
            key = Fernet.generate_key()
            fernet = Fernet(key)
            encrypted = fernet.encrypt(content)
            
            evidence_id = await conn.fetchval(
                """
                INSERT INTO evidence_vault 
                (evidence_hash, evidence_type, source_file, case_id,
                 encrypted_content, content_hash, file_size_bytes,
                 parsed_successfully, custody_chain)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING id
                """,
                evidence_hash,
                classification.file_type,
                os.path.basename(classification.file_path),
                classification.related_case,
                encrypted,
                evidence_hash,
                len(content),
                True,
                json.dumps([{
                    'action': 'auto_classified',
                    'timestamp': datetime.now().isoformat(),
                    'category': classification.evidence_category,
                    'priority': classification.priority,
                    'tags': classification.tags
                }])
            )
        
        return str(evidence_id)
    
    async def process_directory(self, directory: str) -> List[Dict]:
        """Process all files in a directory."""
        results = []
        
        path = Path(directory)
        files = []
        
        for ext in ['*.csv', '*.json', '*.txt', '*.pdf']:
            files.extend(path.glob(ext))
        
        print(f"Found {len(files)} files to process")
        
        for file_path in files:
            try:
                result = await self.ingest_file(str(file_path))
                results.append(result)
            except Exception as e:
                print(f"✗ Error processing {file_path}: {e}")
        
        return results


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Auto-Ingest Evidence')
    parser.add_argument('--input', '-i', help='Input file or directory')
    parser.add_argument('--db-url', default='postgresql://localhost/evidence_fortress')
    
    args = parser.parse_args()
    
    print("="*60)
    print("EVIDENCE FORTRESS - AUTO-INGEST")
    print("="*60)
    
    # Connect to database
    db_pool = await asyncpg.create_pool(args.db_url)
    
    # Create ingester
    ingester = AutoIngester(db_pool)
    
    if args.input:
        path = Path(args.input)
        
        if path.is_file():
            await ingester.ingest_file(str(path))
        elif path.is_dir():
            results = await ingester.process_directory(str(path))
            
            print("\n" + "="*60)
            print("SUMMARY")
            print("="*60)
            print(f"Files processed: {len(results)}")
    else:
        print("Usage:")
        print("  python scripts/auto_ingest.py --input ./evidence/raw")
    
    await db_pool.close()


if __name__ == '__main__':
    asyncio.run(main())
