"""
================================================================================
SANITIZATION GATEWAY - CRITICAL SECURITY LAYER
Evidence Fortress v4.0
================================================================================
THIS IS THE ONLY MODULE ALLOWED TO:
1. Access raw wallet addresses (from address_secrets table)
2. Generate pseudonyms for external use
3. Encrypt/decrypt sensitive data

PRINCIPLE: Raw addresses NEVER touch external APIs. Ever.
================================================================================
"""

import hashlib
import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import asyncio
from contextlib import asynccontextmanager

# Cryptographic imports
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64

# Database
import asyncpg
from asyncpg import Pool


@dataclass
class SanitizedOutput:
    """Output that is safe to send to external APIs."""
    text: str
    pseudonyms_used: List[str]
    original_count: int
    risk_level: str  # 'low', 'medium', 'high'


@dataclass
class EntityRegistration:
    """Result of registering a new entity."""
    address_hash: str
    pseudonym: str
    entity_tier: Optional[str]
    is_new: bool


class SanitizationGateway:
    """
    CRITICAL SECURITY LAYER: All external API calls (Groq, OpenRouter, AWS, etc.)
    MUST pass through here. Raw addresses never leave Contabo.
    
    Flow:
    1. Raw address comes in
    2. SHA256 hash generated (lookup key)
    3. Address encrypted with AES-256-GCM
    4. Stored in address_secrets (LOCAL ONLY)
    5. Pseudonym [ENTITY_001] returned for external use
    6. Only pseudonym goes to external APIs
    """
    
    # Regex patterns for detecting sensitive data
    SOLANA_ADDRESS_PATTERN = re.compile(r'[1-9A-HJ-NP-Za-km-z]{32,44}')
    EVM_ADDRESS_PATTERN = re.compile(r'0x[a-fA-F0-9]{40}')
    TX_SIGNATURE_PATTERN = re.compile(r'[A-Za-z0-9]{87,88}')
    
    # Entity tier classification patterns
    TIER_PATTERNS = {
        'tier_0_root': ['deployer', 'creator', 'owner', 'treasury'],
        'tier_1_treasury': ['treasury', 'multisig', 'gnosis', 'safe'],
        'tier_2_botnet': ['seeder', 'distributor', 'bot', 'coordinator'],
        'tier_3_mule': ['mule', 'intermediary', 'layer'],
        'tier_4_cashout': ['cex', 'exchange', 'mixer', 'tornado'],
        'tier_5_victim': ['victim', 'retail', 'user']
    }
    
    def __init__(self, db_pool: Pool, encryption_key: bytes):
        """
        Initialize the sanitization gateway.
        
        Args:
            db_pool: AsyncPG connection pool
            encryption_key: 32-byte key for AES-256 encryption
        """
        self.db_pool = db_pool
        self.encryption_key = encryption_key
        self._pseudonym_cache: Dict[str, str] = {}  # hash -> pseudonym
        self._reverse_cache: Dict[str, str] = {}     # pseudonym -> hash
        
    async def initialize(self):
        """Load existing pseudonyms into cache."""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT address_hash, pseudonym FROM crypto_entities"
            )
            for row in rows:
                self._pseudonym_cache[row['address_hash']] = row['pseudonym']
                self._reverse_cache[row['pseudonym']] = row['address_hash']
    
    def _generate_address_hash(self, address: str) -> str:
        """Generate SHA256 hash of address for lookup."""
        return hashlib.sha256(address.encode()).hexdigest()
    
    def _encrypt_address(self, address: str, salt: bytes) -> Tuple[bytes, bytes, bytes]:
        """
        Encrypt address using AES-256-GCM.
        
        Returns:
            (ciphertext, nonce, tag)
        """
        # Derive key using PBKDF2
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(self.encryption_key)
        
        # Encrypt with AES-GCM
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, address.encode(), None)
        
        # GCM appends auth tag to ciphertext
        return ciphertext[:-16], nonce, ciphertext[-16:]
    
    def _decrypt_address(self, encrypted: bytes, nonce: bytes, 
                         tag: bytes, salt: bytes) -> str:
        """Decrypt address from storage."""
        # Derive key
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(self.encryption_key)
        
        # Decrypt
        aesgcm = AESGCM(key)
        ciphertext_with_tag = encrypted + tag
        plaintext = aesgcm.decrypt(nonce, ciphertext_with_tag, None)
        
        return plaintext.decode()
    
    async def register_address(
        self, 
        real_address: str,
        entity_type: str = 'unknown',
        entity_role: Optional[str] = None,
        cluster_id: Optional[str] = None,
        tags: List[str] = [],
        risk_score: Optional[float] = None
    ) -> EntityRegistration:
        """
        Register a new address and get pseudonym for external use.
        
        This is the ONLY way to add addresses to the system.
        
        Args:
            real_address: The actual wallet address
            entity_type: Classification hint
            entity_role: Specific role in the operation
            cluster_id: Group identifier
            tags: Additional classification tags
            risk_score: 0.0 to 1.0
            
        Returns:
            EntityRegistration with hash and pseudonym
        """
        # Generate hash for lookup
        addr_hash = self._generate_address_hash(real_address)
        
        # Check if already registered
        if addr_hash in self._pseudonym_cache:
            return EntityRegistration(
                address_hash=addr_hash,
                pseudonym=self._pseudonym_cache[addr_hash],
                entity_tier=None,
                is_new=False
            )
        
        # Determine entity tier from tags/role
        entity_tier = self._classify_tier(entity_role or '', tags)
        
        # Generate pseudonym
        pseudonym = await self._generate_pseudonym(entity_tier, cluster_id)
        
        # Encrypt address for storage
        salt = os.urandom(32)
        encrypted, nonce, tag = self._encrypt_address(real_address, salt)
        
        # Store in database
        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                # Insert entity
                await conn.execute(
                    """
                    INSERT INTO crypto_entities 
                    (address_hash, pseudonym, entity_tier, entity_role, cluster_id, risk_score)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (address_hash) DO NOTHING
                    """,
                    addr_hash, pseudonym, entity_tier, entity_role, 
                    cluster_id, risk_score
                )
                
                # Insert encrypted secret
                await conn.execute(
                    """
                    INSERT INTO address_secrets 
                    (address_hash, encrypted_address, encryption_nonce, 
                     encryption_tag, kdf_salt, kdf_iterations)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (address_hash) DO NOTHING
                    """,
                    addr_hash, encrypted, nonce, tag, salt, 100000
                )
        
        # Update cache
        self._pseudonym_cache[addr_hash] = pseudonym
        self._reverse_cache[pseudonym] = addr_hash
        
        return EntityRegistration(
            address_hash=addr_hash,
            pseudonym=pseudonym,
            entity_tier=entity_tier,
            is_new=True
        )
    
    async def register_batch(
        self,
        addresses: List[Tuple[str, Optional[str], Optional[str], Optional[str], List[str]]]
    ) -> List[EntityRegistration]:
        """
        Register multiple addresses efficiently.
        
        Args:
            addresses: List of (address, entity_role, cluster_id, notes, tags)
            
        Returns:
            List of EntityRegistration results
        """
        results = []
        for addr, role, cluster, notes, tags in addresses:
            result = await self.register_address(
                real_address=addr,
                entity_role=role,
                cluster_id=cluster,
                tags=tags
            )
            results.append(result)
        return results
    
    def _classify_tier(self, role: str, tags: List[str]) -> Optional[str]:
        """Classify entity tier based on role and tags."""
        search_text = (role + ' ' + ' '.join(tags)).lower()
        
        for tier, keywords in self.TIER_PATTERNS.items():
            if any(kw in search_text for kw in keywords):
                return tier
        return 'tier_3_mule'  # Default
    
    async def _generate_pseudonym(
        self, 
        entity_tier: Optional[str],
        cluster_id: Optional[str]
    ) -> str:
        """Generate a unique pseudonym."""
        # Get prefix based on tier
        prefix_map = {
            'tier_0_root': 'GENESIS',
            'tier_1_treasury': 'TREASURY',
            'tier_2_botnet': 'BOTNET',
            'tier_3_mule': 'MULE',
            'tier_4_cashout': 'CASHOUT',
            'tier_5_victim': 'VICTIM'
        }
        
        prefix = prefix_map.get(entity_tier, 'ENTITY')
        
        # Add cluster suffix if available
        if cluster_id:
            cluster_short = cluster_id[:8].upper()
            prefix = f"{prefix}_{cluster_short}"
        
        # Get next number
        async with self.db_pool.acquire() as conn:
            count = await conn.fetchval(
                """
                SELECT COUNT(*) FROM crypto_entities 
                WHERE pseudonym LIKE $1
                """,
                f"[{prefix}_%]"
            )
        
        return f"[{prefix}_{count + 1:03d}]"
    
    async def sanitize_for_external(
        self, 
        text: str,
        preserve_structure: bool = True
    ) -> SanitizedOutput:
        """
        Sanitize text for external API consumption.
        
        Replaces all addresses with their pseudonyms.
        
        Args:
            text: Raw text that may contain addresses
            preserve_structure: Keep transaction structure readable
            
        Returns:
            SanitizedOutput safe for external APIs
        """
        pseudonyms_used = []
        original_count = 0
        
        # Find all addresses
        sol_addresses = self.SOLANA_ADDRESS_PATTERN.findall(text)
        evm_addresses = self.EVM_ADDRESS_PATTERN.findall(text)
        all_addresses = sol_addresses + evm_addresses
        
        # Replace each with pseudonym
        sanitized = text
        for addr in all_addresses:
            addr_hash = self._generate_address_hash(addr)
            
            # Check cache first
            if addr_hash in self._pseudonym_cache:
                pseudonym = self._pseudonym_cache[addr_hash]
            else:
                # Register new entity
                reg = await self.register_address(addr)
                pseudonym = reg.pseudonym
            
            sanitized = sanitized.replace(addr, pseudonym)
            pseudonyms_used.append(pseudonym)
            original_count += 1
        
        # Determine risk level
        risk_level = self._assess_risk_level(sanitized, pseudonyms_used)
        
        return SanitizedOutput(
            text=sanitized,
            pseudonyms_used=pseudonyms_used,
            original_count=original_count,
            risk_level=risk_level
        )
    
    def _assess_risk_level(self, text: str, pseudonyms: List[str]) -> str:
        """Assess risk level of sanitized content."""
        high_risk_terms = ['treasury', 'deployer', 'botnet', 'seeder', 'genesis']
        text_lower = text.lower()
        
        if any(term in text_lower for term in high_risk_terms):
            return 'high'
        elif len(pseudonyms) > 10:
            return 'medium'
        return 'low'
    
    async def desanitize_response(
        self, 
        text: str,
        for_legal_document: bool = False
    ) -> str:
        """
        Convert pseudonyms back to real addresses (for internal use only).
        
        WARNING: Only use for final report generation. Never for external APIs.
        
        Args:
            text: Text containing pseudonyms
            for_legal_document: If True, adds annotations for legal review
            
        Returns:
            Text with real addresses (handle with care!)
        """
        # Find all pseudonyms
        pseudonym_pattern = re.compile(r'\[[A-Z_]+_\d{3}\]')
        pseudonyms = pseudonym_pattern.findall(text)
        
        desanitized = text
        for pseudo in pseudonyms:
            addr_hash = self._reverse_cache.get(pseudo)
            if not addr_hash:
                continue
            
            # Fetch and decrypt
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT encrypted_address, encryption_nonce, 
                           encryption_tag, kdf_salt
                    FROM address_secrets 
                    WHERE address_hash = $1
                    """,
                    addr_hash
                )
            
            if row:
                real_address = self._decrypt_address(
                    row['encrypted_address'],
                    row['encryption_nonce'],
                    row['encryption_tag'],
                    row['kdf_salt']
                )
                
                if for_legal_document:
                    # Add legal annotation
                    replacement = f"{real_address} [LEGAL REVIEW: {pseudo}]"
                else:
                    replacement = real_address
                
                desanitized = desanitized.replace(pseudo, replacement)
        
        return desanitized
    
    async def get_entity_info(self, pseudonym: str) -> Optional[Dict]:
        """Get entity information by pseudonym (safe, no raw address)."""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT pseudonym, entity_tier, entity_role, cluster_id,
                       risk_score, confidence_score, first_seen, last_seen,
                       transaction_count, behavior_profile
                FROM crypto_entities
                WHERE pseudonym = $1
                """,
                pseudonym
            )
        
        return dict(row) if row else None
    
    async def get_address_for_investigator(
        self, 
        pseudonym: str,
        investigator_id: str,
        reason: str
    ) -> Optional[str]:
        """
        Get real address for authorized investigator.
        
        This is AUDITED - every access is logged.
        
        Args:
            pseudonym: Entity pseudonym
            investigator_id: Authorized user ID
            reason: Business reason for access
            
        Returns:
            Real address or None if not authorized
        """
        addr_hash = self._reverse_cache.get(pseudonym)
        if not addr_hash:
            return None
        
        # Log access
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO audit_logs 
                (event_type, actor_type, actor_id, target_table, target_id,
                 change_description, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, NOW())
                """,
                'address_accessed', 'user', investigator_id,
                'address_secrets', addr_hash,
                f'Access reason: {reason}'
            )
            
            # Update access stats
            await conn.execute(
                """
                UPDATE address_secrets 
                SET last_accessed = NOW(), 
                    access_count = access_count + 1
                WHERE address_hash = $1
                """,
                addr_hash
            )
            
            # Fetch and decrypt
            row = await conn.fetchrow(
                """
                SELECT encrypted_address, encryption_nonce, 
                       encryption_tag, kdf_salt
                FROM address_secrets 
                WHERE address_hash = $1
                """,
                addr_hash
            )
        
        if row:
            return self._decrypt_address(
                row['encrypted_address'],
                row['encryption_nonce'],
                row['encryption_tag'],
                row['kdf_salt']
            )
        return None


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

import os

def generate_encryption_key() -> bytes:
    """Generate a new 32-byte encryption key."""
    return os.urandom(32)


def key_to_env_format(key: bytes) -> str:
    """Convert key to base64 for environment variable storage."""
    return base64.b64encode(key).decode()


def key_from_env_format(env_str: str) -> bytes:
    """Convert base64 env string back to key."""
    return base64.b64decode(env_str)
