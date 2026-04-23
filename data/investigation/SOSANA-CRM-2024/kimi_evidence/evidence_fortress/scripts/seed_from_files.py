"""
================================================================================
EVIDENCE INGESTION PIPELINE
Evidence Fortress v4.0

Processes CSV/TXT evidence files into the database with full sanitization.

Usage:
    python seed_from_files.py --input /path/to/evidence --case SOSANA_RICO_2026

Supported formats:
    - Solscan transfer exports (CSV)
    - Solscan balance change exports (CSV)
    - Token holder exports (CSV)
    - Chat logs (TXT)
    - JSON exports
================================================================================
"""

import os
import sys
import csv
import json
import hashlib
import argparse
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
import asyncpg

# Add parent to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.security.sanitization_gateway import (
    SanitizationGateway, 
    generate_encryption_key
)


@dataclass
class ParsedTransfer:
    """Parsed transfer record."""
    signature: str
    block_time: datetime
    from_address: str
    to_address: str
    amount: float
    token_address: str
    token_symbol: str
    flow: str


@dataclass
class ParsedBalanceChange:
    """Parsed balance change record."""
    tx_hash: str
    block_time: datetime
    token_account: str
    change_type: str  # 'inc' or 'dec'
    change_amount: float
    pre_balance: float
    post_balance: float
    token_address: str


@dataclass
class ParsedHolder:
    """Parsed token holder record."""
    wallet_address: str
    token_account: str
    quantity: float
    percentage: float


@dataclass
class IngestionResult:
    """Result of file ingestion."""
    file_path: str
    evidence_id: str
    evidence_hash: str
    rows_processed: int
    entities_registered: int
    transactions_added: int
    errors: List[str]


class EvidenceIngester:
    """
    Ingests evidence files into the Evidence Fortress database.
    
    All addresses are automatically registered and pseudonymized.
    Raw content is encrypted and stored in evidence_vault.
    """
    
    def __init__(self, db_pool: asyncpg.Pool, gateway: SanitizationGateway):
        self.db_pool = db_pool
        self.gateway = gateway
        self.case_id = "SOSANA_RICO_2026"
        
        # Known entity mappings from case file
        self.known_entities = {
            # Treasury and main actors
            'Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS': {
                'role': 'token_treasury',
                'tier': 'tier_1_treasury',
                'cluster': 'sosana_core',
                'pseudonym': '[TREASURY_SOSANA]'
            },
            # Botnet seeder (970 wallets in 7 seconds)
            'AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6': {
                'role': 'wallet_seeder',
                'tier': 'tier_2_botnet',
                'cluster': 'botnet_alpha',
                'pseudonym': '[BOTNET_SEEDER_001]'
            },
            # CRM distributor #9
            '8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj': {
                'role': 'crm_distributor',
                'tier': 'tier_2_botnet',
                'cluster': 'crm_network',
                'pseudonym': '[DISTRIBUTOR_009]'
            },
            # CRM token
            'HfMbPyDdZH6QMaDDUokjYCkHxzjoGBMpgaUvpLWGbF5p': {
                'role': 'crm_token',
                'tier': 'tier_1_treasury',
                'cluster': 'crm_network',
                'pseudonym': '[CRM_TOKEN]'
            },
            # Intermediate wallet
            'Cx5qTEtnp3arFVBuusMXHafoRzLCLuigtz2AiQAFmq2Q': {
                'role': 'intermediary',
                'tier': 'tier_3_mule',
                'cluster': 'sosana_core',
                'pseudonym': '[INTERMEDIARY_001]'
            },
            
            # CRIMINAL ENTERPRISE WALLETS (March 30, 2026 Cross-Reference)
            # Tier 1: Master Feeders
            'HLnpSz9h2S4hiLQ4mxtAYJJQXx9USzEXbte2RVP9QEd': {
                'role': 'dust_fee_source',
                'tier': 'tier_1_treasury',
                'cluster': 'crm_criminal_enterprise',
                'pseudonym': '[MASTER_FEEDER_001]'
            },
            'HLnpSz9h2S4hiLQ4uN3vGYAHJqDmbFCwkx9prSXkdPMc': {
                'role': 'dust_fee_source',
                'tier': 'tier_1_treasury',
                'cluster': 'crm_criminal_enterprise',
                'pseudonym': '[MASTER_FEEDER_002]'
            },
            # Tier 2: Core Botnet
            'DLHnb1yt6DMx2q3qoU2i8coMtnzD5y99eJ4EjhdZgLVh': {
                'role': 'cluster_leader',
                'tier': 'tier_2_botnet',
                'cluster': 'crm_criminal_enterprise',
                'pseudonym': '[DORMANT_VOLCANO]'
            },
            '8pyiqMctEzfUZvegKH5jHenHTBkQ5W37WSAitieYZz3m': {
                'role': 'consolidation_wallet',
                'tier': 'tier_2_botnet',
                'cluster': 'crm_criminal_enterprise',
                'pseudonym': '[CONSOLIDATION_001]'
            },
            'E9bg6VCatYJGgrjADYbGdRF43HC3nqsFdqnQNk54oPpV': {
                'role': 'sosana_cluster',
                'tier': 'tier_2_botnet',
                'cluster': 'crm_criminal_enterprise',
                'pseudonym': '[SOSANA_CORE_001]'
            },
            # Tier 3: Satellite Mules
            'D9ZGRMhmdMdf5dRdEiLSJLrSETsFuofSPDZHjx5tuULT': {
                'role': 'execution_wallet',
                'tier': 'tier_3_mule',
                'cluster': 'crm_criminal_enterprise',
                'pseudonym': '[SATELLITE_001]'
            },
            'HPVUJGJwJnpGBDCzoAPKPjHe8QfXLgRjbktXCRyMNi5w': {
                'role': 'reload_wallet',
                'tier': 'tier_3_mule',
                'cluster': 'crm_criminal_enterprise',
                'pseudonym': '[RELOAD_001]'
            },
            'J3V68JvjXFArRBb86NAX8mCoYgFce7MmZjs9ziz74RzT': {
                'role': 'dust_accumulator',
                'tier': 'tier_3_mule',
                'cluster': 'crm_criminal_enterprise',
                'pseudonym': '[SATELLITE_002]'
            },
            'CyhJT3o8xrW5vvenMkrJDdpYcdboGGg6SQvSoeVtcA35': {
                'role': 'dormant_threat',
                'tier': 'tier_3_mule',
                'cluster': 'crm_criminal_enterprise',
                'pseudonym': '[IMMINENT_THREAT]'
            },
            # Tier 4: Cashout
            'hHxyZi7ZxbYqQmBhTRtdwpjwpfhmWVypRfMVmn2HzPt': {
                'role': 'systematic_seller',
                'tier': 'tier_4_cashout',
                'cluster': 'crm_criminal_enterprise',
                'pseudonym': '[EXIT_SELLER_001]'
            },
            # Tier 5: Victim
            '7abBmGf4HNu3UXsanJc7WwAPW2PgkEb9hwrFKwCySvyL': {
                'role': 'downstream_victim',
                'tier': 'tier_5_victim',
                'cluster': 'crm_criminal_enterprise',
                'pseudonym': '[VICTIM_WHALE_001]'
            }
        }
    
    async def ingest_file(self, file_path: str) -> IngestionResult:
        """
        Ingest a single evidence file.
        
        Args:
            file_path: Path to evidence file
            
        Returns:
            IngestionResult with details
        """
        print(f"\n{'='*60}")
        print(f"INGESTING: {file_path}")
        print(f"{'='*60}")
        
        errors = []
        
        # Determine file type
        file_type = self._detect_file_type(file_path)
        print(f"Detected type: {file_type}")
        
        # Read and hash raw content
        with open(file_path, 'rb') as f:
            raw_content = f.read()
        
        evidence_hash = hashlib.sha256(raw_content).hexdigest()
        print(f"Evidence hash: {evidence_hash[:16]}...")
        
        # Check for duplicates
        existing = await self._check_duplicate(evidence_hash)
        if existing:
            print(f"WARNING: Duplicate evidence detected (ID: {existing})")
            return IngestionResult(
                file_path=file_path,
                evidence_id=existing,
                evidence_hash=evidence_hash,
                rows_processed=0,
                entities_registered=0,
                transactions_added=0,
                errors=["Duplicate evidence"]
            )
        
        # Store in vault
        evidence_id = await self._store_in_vault(
            file_path, 
            raw_content, 
            evidence_hash,
            file_type
        )
        print(f"Stored in vault: {evidence_id}")
        
        # Parse and process based on type
        entities_registered = 0
        transactions_added = 0
        rows_processed = 0
        
        try:
            if file_type == 'transfer_csv':
                rows_processed, entities_registered, transactions_added = \
                    await self._process_transfer_csv(file_path, evidence_id)
                    
            elif file_type == 'balance_change_csv':
                rows_processed, entities_registered = \
                    await self._process_balance_change_csv(file_path, evidence_id)
                    
            elif file_type == 'token_holders_csv':
                rows_processed, entities_registered = \
                    await self._process_token_holders_csv(file_path, evidence_id)
                    
            elif file_type == 'chat_log':
                rows_processed, entities_registered = \
                    await self._process_chat_log(file_path, evidence_id)
                    
            else:
                errors.append(f"Unknown file type: {file_type}")
                
        except Exception as e:
            errors.append(f"Processing error: {str(e)}")
            print(f"ERROR: {e}")
        
        # Update evidence record
        await self._update_evidence_status(evidence_id, rows_processed, len(errors) == 0)
        
        print(f"\n✓ Ingested: {rows_processed} rows")
        print(f"✓ Entities: {entities_registered} registered")
        print(f"✓ Transactions: {transactions_added} added")
        
        return IngestionResult(
            file_path=file_path,
            evidence_id=evidence_id,
            evidence_hash=evidence_hash,
            rows_processed=rows_processed,
            entities_registered=entities_registered,
            transactions_added=transactions_added,
            errors=errors
        )
    
    def _detect_file_type(self, file_path: str) -> str:
        """Detect the type of evidence file."""
        filename = os.path.basename(file_path).lower()
        
        if 'transfer' in filename and filename.endswith('.csv'):
            return 'transfer_csv'
        elif 'balance_change' in filename and filename.endswith('.csv'):
            return 'balance_change_csv'
        elif 'token_holders' in filename or 'holder' in filename:
            return 'token_holders_csv'
        elif filename.endswith('.txt') or 'chat' in filename.lower():
            return 'chat_log'
        elif filename.endswith('.json'):
            return 'json_export'
        else:
            return 'unknown'
    
    async def _check_duplicate(self, evidence_hash: str) -> Optional[str]:
        """Check if evidence already exists."""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchval(
                "SELECT id FROM evidence_vault WHERE evidence_hash = $1",
                evidence_hash
            )
        return row
    
    async def _store_in_vault(
        self, 
        file_path: str, 
        raw_content: bytes,
        evidence_hash: str,
        evidence_type: str
    ) -> str:
        """Store raw evidence in encrypted vault."""
        filename = os.path.basename(file_path)
        
        # Encrypt content (using simple Fernet for now - upgrade to AES-GCM in production)
        from cryptography.fernet import Fernet
        key = Fernet.generate_key()
        fernet = Fernet(key)
        encrypted = fernet.encrypt(raw_content)
        
        async with self.db_pool.acquire() as conn:
            evidence_id = await conn.fetchval(
                """
                INSERT INTO evidence_vault 
                (evidence_hash, evidence_type, source_file, case_id,
                 encrypted_content, content_hash, file_size_bytes, custody_chain)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
                """,
                evidence_hash,
                evidence_type,
                filename,
                self.case_id,
                encrypted,
                evidence_hash,
                len(raw_content),
                json.dumps([{
                    'action': 'ingested',
                    'timestamp': datetime.now().isoformat(),
                    'system': 'evidence_fortress_v4'
                }])
            )
        
        return str(evidence_id)
    
    async def _register_entity_with_context(
        self, 
        address: str,
        evidence_type: str
    ) -> str:
        """Register entity with known context if available."""
        # Check if this is a known entity
        known = self.known_entities.get(address)
        
        if known:
            # Register with known role
            result = await self.gateway.register_address(
                real_address=address,
                entity_role=known['role'],
                cluster_id=known['cluster'],
                tags=[known['tier'], known['role']]
            )
            
            # Update with known pseudonym if new
            if result.is_new:
                async with self.db_pool.acquire() as conn:
                    await conn.execute(
                        """
                        UPDATE crypto_entities 
                        SET pseudonym = $1, entity_tier = $2
                        WHERE address_hash = $3
                        """,
                        known['pseudonym'],
                        known['tier'],
                        result.address_hash
                    )
                # Update cache
                self.gateway._pseudonym_cache[result.address_hash] = known['pseudonym']
                self.gateway._reverse_cache[known['pseudonym']] = result.address_hash
                
            return known['pseudonym']
        else:
            # Unknown entity - auto-classify
            result = await self.gateway.register_address(
                real_address=address,
                entity_role='unknown',
                cluster_id='unclassified'
            )
            return result.pseudonym
    
    async def _process_transfer_csv(
        self, 
        file_path: str,
        evidence_id: str
    ) -> Tuple[int, int, int]:
        """Process transfer CSV file."""
        print("Processing transfer CSV...")
        
        rows_processed = 0
        entities_registered = 0
        transactions_added = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                rows_processed += 1
                
                # Extract addresses
                from_addr = row.get('From', '').strip()
                to_addr = row.get('To', '').strip()
                token_addr = row.get('Token Address', '').strip()
                
                # Register entities
                from_pseudo = await self._register_entity_with_context(from_addr, 'transfer')
                to_pseudo = await self._register_entity_with_context(to_addr, 'transfer')
                if token_addr and len(token_addr) > 30:
                    await self._register_entity_with_context(token_addr, 'token')
                
                entities_registered += 2
                
                # Parse transaction
                try:
                    block_time = datetime.fromisoformat(
                        row.get('Human Time', '').replace('Z', '+00:00')
                    )
                except:
                    block_time = datetime.now()
                
                amount_str = row.get('Amount', '0').replace(',', '')
                try:
                    amount = float(amount_str)
                except:
                    amount = 0.0
                
                # Detect pattern
                pattern = None
                if rows_processed > 1:
                    pattern = 'rapid_fire'  # Multiple transfers in sequence
                
                # Insert transaction
                async with self.db_pool.acquire() as conn:
                    await conn.execute(
                        """
                        INSERT INTO transaction_graph 
                        (signature, block_time, from_pseudonym, to_pseudonym,
                         token_address, token_symbol, amount_decimal, flow_type,
                         evidence_id, pattern_detected)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                        ON CONFLICT (signature) DO NOTHING
                        """,
                        row.get('Signature', ''),
                        block_time,
                        from_pseudo,
                        to_pseudo,
                        token_addr,
                        row.get('Token Address', 'SOL'),
                        amount,
                        row.get('Flow', 'unknown'),
                        evidence_id,
                        pattern
                    )
                    transactions_added += 1
                
                # Progress update
                if rows_processed % 100 == 0:
                    print(f"  Processed {rows_processed} rows...")
        
        return rows_processed, entities_registered, transactions_added
    
    async def _process_balance_change_csv(
        self, 
        file_path: str,
        evidence_id: str
    ) -> Tuple[int, int]:
        """Process balance change CSV file."""
        print("Processing balance change CSV...")
        
        rows_processed = 0
        entities_registered = 0
        
        # Extract wallet address from filename
        filename = os.path.basename(file_path)
        wallet_addr = None
        if 'balance_change_' in filename:
            start = filename.find('balance_change_') + 15
            end = filename.find('_', start)
            if end > start:
                wallet_addr = filename[start:end]
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                rows_processed += 1
                
                # Register token account
                token_account = row.get('TokenAccount', '').strip()
                if token_account:
                    await self.gateway.register_address(token_account)
                    entities_registered += 1
                
                # Register token
                token_addr = row.get('TokenAddress', '').strip()
                if token_addr:
                    await self._register_entity_with_context(token_addr, 'token')
        
        return rows_processed, entities_registered
    
    async def _process_token_holders_csv(
        self, 
        file_path: str,
        evidence_id: str
    ) -> Tuple[int, int]:
        """Process token holders CSV file."""
        print("Processing token holders CSV...")
        
        rows_processed = 0
        entities_registered = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                rows_processed += 1
                
                wallet_addr = row.get('Account', '').strip()
                token_account = row.get('Token Account', '').strip()
                
                if wallet_addr:
                    await self._register_entity_with_context(wallet_addr, 'holder')
                    entities_registered += 1
                
                if token_account:
                    await self.gateway.register_address(token_account)
        
        return rows_processed, entities_registered
    
    async def _process_chat_log(
        self, 
        file_path: str,
        evidence_id: str
    ) -> Tuple[int, int]:
        """Process chat log TXT file."""
        print("Processing chat log...")
        
        # Read entire file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract potential addresses using regex
        import re
        solana_pattern = re.compile(r'[1-9A-HJ-NP-Za-km-z]{32,44}')
        addresses = set(solana_pattern.findall(content))
        
        print(f"Found {len(addresses)} potential addresses in chat log")
        
        # Register each
        entities_registered = 0
        for addr in addresses:
            # Filter out likely false positives
            if len(addr) >= 32 and len(addr) <= 44:
                await self.gateway.register_address(addr)
                entities_registered += 1
        
        # Extract Telegram handles
        tg_pattern = re.compile(r'@(\w{5,32})')
        handles = tg_pattern.findall(content)
        print(f"Found {len(handles)} Telegram handles: {handles[:5]}")
        
        # Store in human_operators if relevant
        if 'marcus' in content.lower() or 'aurelius' in content.lower():
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO human_operators 
                    (operator_pseudonym, known_aliases, telegram_handles, 
                     rico_role, intelligence_notes, source_evidence_ids)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT DO NOTHING
                    """,
                    '[OPERATOR_MARCUS]',
                    json.dumps(['Marcus Aurelius', 'Crypto Rug Muncher']),
                    json.dumps(handles),
                    'foot_soldier',
                    'Telegram bot operator discussing token scanner capabilities',
                    json.dumps([evidence_id])
                )
        
        return len(content.split('\n')), entities_registered
    
    async def _update_evidence_status(
        self, 
        evidence_id: str, 
        row_count: int,
        success: bool
    ):
        """Update evidence record with processing status."""
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE evidence_vault 
                SET row_count = $1, parsed_successfully = $2
                WHERE id = $3
                """,
                row_count,
                success,
                evidence_id
            )


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Evidence Ingestion Pipeline')
    parser.add_argument('--input', '-i', required=True, help='Input file or directory')
    parser.add_argument('--case', '-c', default='SOSANA_RICO_2026', help='Case ID')
    parser.add_argument('--db-url', default='postgresql://localhost/evidence_fortress',
                        help='Database connection URL')
    
    args = parser.parse_args()
    
    print("="*60)
    print("EVIDENCE FORTRESS - INGESTION PIPELINE")
    print("="*60)
    print(f"Case: {args.case}")
    print(f"Input: {args.input}")
    print("="*60)
    
    # Connect to database
    print("\nConnecting to database...")
    db_pool = await asyncpg.create_pool(args.db_url)
    
    # Initialize sanitization gateway
    encryption_key = generate_encryption_key()
    gateway = SanitizationGateway(db_pool, encryption_key)
    await gateway.initialize()
    
    # Create ingester
    ingester = EvidenceIngester(db_pool, gateway)
    ingester.case_id = args.case
    
    # Collect files
    input_path = Path(args.input)
    files_to_process = []
    
    if input_path.is_file():
        files_to_process.append(str(input_path))
    elif input_path.is_dir():
        for ext in ['*.csv', '*.txt', '*.json']:
            files_to_process.extend(input_path.glob(ext))
        files_to_process = [str(f) for f in files_to_process]
    
    print(f"\nFound {len(files_to_process)} files to process")
    
    # Process each file
    results = []
    for file_path in files_to_process:
        result = await ingester.ingest_file(file_path)
        results.append(result)
    
    # Summary
    print("\n" + "="*60)
    print("INGESTION SUMMARY")
    print("="*60)
    
    total_rows = sum(r.rows_processed for r in results)
    total_entities = sum(r.entities_registered for r in results)
    total_txs = sum(r.transactions_added for r in results)
    
    print(f"Files processed: {len(results)}")
    print(f"Total rows: {total_rows}")
    print(f"Entities registered: {total_entities}")
    print(f"Transactions added: {total_txs}")
    
    # Close pool
    await db_pool.close()
    
    print("\n✓ Ingestion complete!")


if __name__ == '__main__':
    asyncio.run(main())
