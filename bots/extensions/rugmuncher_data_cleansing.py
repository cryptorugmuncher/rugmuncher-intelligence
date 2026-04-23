#!/usr/bin/env python3
"""
🧼 RugMuncher Data Cleansing Pipeline
Sanitize data on the way IN and OUT

Principles:
- IN: Validate, normalize, remove injection attempts
- OUT: Remove PII, minimize data exposure, respect privacy
- Always log what was cleansed for audit
- Different rules for different contexts (internal vs external)
"""

import re
import json
import hashlib
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from html import escape

# Optional bleach import (for HTML sanitization)
try:
    import bleach
    HAS_BLEACH = True
except ImportError:
    HAS_BLEACH = False
    bleach = None

logger = logging.getLogger(__name__)


class DataDirection(Enum):
    """Direction of data flow"""
    INCOMING = "incoming"    # From external sources (APIs, users)
    OUTGOING = "outgoing"    # To external services, public channels


class DataSensitivity(Enum):
    """Classification for cleansing rules"""
    PUBLIC = "public"          # Safe to share
    INTERNAL = "internal"      # Internal use only
    SENSITIVE = "sensitive"    # PII - needs protection
    CRITICAL = "critical"      # Keys, passwords - never expose


@dataclass
class CleansingRule:
    """A data cleansing rule"""
    name: str
    pattern: str  # Regex pattern
    replacement: Union[str, Callable]
    description: str
    applies_to: List[DataDirection]
    sensitivity: DataSensitivity
    
    def apply(self, value: str) -> str:
        """Apply this rule to a value"""
        if callable(self.replacement):
            return re.sub(self.pattern, self.replacement, value)
        return re.sub(self.pattern, self.replacement, value)


@dataclass
class CleansingReport:
    """Report of what was cleansed"""
    timestamp: str
    direction: DataDirection
    fields_cleansed: List[str] = field(default_factory=list)
    rules_applied: List[str] = field(default_factory=list)
    items_removed: int = 0
    items_masked: int = 0
    items_hashed: int = 0
    original_size: int = 0
    cleansed_size: int = 0
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp,
            'direction': self.direction.value,
            'fields_cleansed': self.fields_cleansed,
            'rules_applied': self.rules_applied,
            'items_removed': self.items_removed,
            'items_masked': self.items_masked,
            'items_hashed': self.items_hashed,
            'size_reduction': f"{self.original_size - self.cleansed_size} bytes"
        }


class DataCleansingPipeline:
    """
    🧼 Main data cleansing pipeline
    
    Handles both INCOMING (validation) and OUTGOING (sanitization) cleansing
    """
    
    def __init__(self):
        self.incoming_rules: List[CleansingRule] = []
        self.outgoing_rules: List[CleansingRule] = []
        self._init_default_rules()
        
    def _init_default_rules(self):
        """Initialize default cleansing rules"""
        
        # ═══════════════════════════════════════════════════════════
        # INCOMING RULES (Validation & Normalization)
        # ═══════════════════════════════════════════════════════════
        
        self.incoming_rules = [
            # Remove HTML/JS injection attempts
            CleansingRule(
                name="strip_html",
                pattern=r'<[^>]+>',
                replacement='',
                description="Remove HTML tags to prevent XSS",
                applies_to=[DataDirection.INCOMING],
                sensitivity=DataSensitivity.CRITICAL
            ),
            
            # Remove SQL injection patterns
            CleansingRule(
                name="block_sql_injection",
                pattern=r'(DROP TABLE|DELETE FROM|INSERT INTO|UNION SELECT|--|;--)',
                replacement='[BLOCKED]',
                description="Block common SQL injection patterns",
                applies_to=[DataDirection.INCOMING],
                sensitivity=DataSensitivity.CRITICAL
            ),
            
            # Normalize wallet addresses (lowercase)
            CleansingRule(
                name="normalize_wallet",
                pattern=r'^(0x[a-fA-F0-9]{40})$',
                replacement=lambda m: m.group(1).lower(),
                description="Normalize Ethereum addresses to lowercase",
                applies_to=[DataDirection.INCOMING],
                sensitivity=DataSensitivity.PUBLIC
            ),
            
            # Remove control characters
            CleansingRule(
                name="strip_control_chars",
                pattern=r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]',
                replacement='',
                description="Remove non-printable control characters",
                applies_to=[DataDirection.INCOMING],
                sensitivity=DataSensitivity.PUBLIC
            ),
            
            # Trim excessive whitespace
            CleansingRule(
                name="normalize_whitespace",
                pattern=r'\s+',
                replacement=' ',
                description="Normalize whitespace to single spaces",
                applies_to=[DataDirection.INCOMING],
                sensitivity=DataSensitivity.PUBLIC
            ),
            
            # Validate email format (basic)
            CleansingRule(
                name="validate_email",
                pattern=r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                replacement=lambda m: m.group(0).lower(),
                description="Normalize email addresses",
                applies_to=[DataDirection.INCOMING],
                sensitivity=DataSensitivity.SENSITIVE
            ),
        ]
        
        # ═══════════════════════════════════════════════════════════
        # OUTGOING RULES (Sanitization & PII Removal)
        # ═══════════════════════════════════════════════════════════
        
        self.outgoing_rules = [
            # Truncate wallet addresses (6...4 format)
            CleansingRule(
                name="truncate_wallet",
                pattern=r'(0x[a-fA-F0-9]{40})',
                replacement=lambda m: f"{m.group(1)[:6]}...{m.group(1)[-4:]}",
                description="Truncate wallet addresses for public display",
                applies_to=[DataDirection.OUTGOING],
                sensitivity=DataSensitivity.SENSITIVE
            ),
            
            # Remove IP addresses entirely
            CleansingRule(
                name="remove_ip_addresses",
                pattern=r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
                replacement='[IP_REDACTED]',
                description="Remove IP addresses",
                applies_to=[DataDirection.OUTGOING],
                sensitivity=DataSensitivity.SENSITIVE
            ),
            
            # Remove email addresses
            CleansingRule(
                name="remove_emails",
                pattern=r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                replacement='[EMAIL_REDACTED]',
                description="Remove email addresses",
                applies_to=[DataDirection.OUTGOING],
                sensitivity=DataSensitivity.SENSITIVE
            ),
            
            # Remove phone numbers
            CleansingRule(
                name="remove_phones",
                pattern=r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
                replacement='[PHONE_REDACTED]',
                description="Remove phone numbers",
                applies_to=[DataDirection.OUTGOING],
                sensitivity=DataSensitivity.SENSITIVE
            ),
            
            # Remove Telegram IDs/Chat IDs
            CleansingRule(
                name="remove_telegram_ids",
                pattern=r'\b[0-9]{9,10}\b',
                replacement='[ID_REDACTED]',
                description="Remove Telegram user/chat IDs",
                applies_to=[DataDirection.OUTGOING],
                sensitivity=DataSensitivity.SENSITIVE
            ),
            
            # Round large amounts (privacy through granularity)
            CleansingRule(
                name="round_amounts",
                pattern=r'(\$?[0-9,]+(?:\.[0-9]{2})?)',
                replacement=self._round_amount_replacement,
                description="Round monetary amounts to protect privacy",
                applies_to=[DataDirection.OUTGOING],
                sensitivity=DataSensitivity.SENSITIVE
            ),
            
            # Remove API keys (various formats) - MUST come before amount rounding
            CleansingRule(
                name="remove_api_keys",
                pattern=r'\b(sk-[a-zA-Z0-9_-]{8,}|gsk_[a-zA-Z0-9_-]{8,}|Bearer\s+[a-zA-Z0-9\-_]{8,})\b',
                replacement='[API_KEY_REDACTED]',
                description="Remove API keys and tokens",
                applies_to=[DataDirection.OUTGOING],
                sensitivity=DataSensitivity.CRITICAL
            ),
            
            # Remove private keys / seed phrases
            CleansingRule(
                name="remove_private_keys",
                pattern=r'(0x[a-fA-F0-9]{64}|\b[a-z]+\s+[a-z]+\s+[a-z]+(?:\s+[a-z]+){9,23}\b)',
                replacement='[PRIVATE_KEY_REDACTED]',
                description="Remove private keys and seed phrases",
                applies_to=[DataDirection.OUTGOING],
                sensitivity=DataSensitivity.CRITICAL
            ),
            
            # Remove geolocation data
            CleansingRule(
                name="remove_geolocation",
                pattern=r'(latitude|longitude|lat|lng|gps|coordinates?)[:\s]*[0-9.\-]+',
                replacement='[GEO_REDACTED]',
                description="Remove GPS coordinates",
                applies_to=[DataDirection.OUTGOING],
                sensitivity=DataSensitivity.SENSITIVE
            ),
            
            # Remove device fingerprints
            CleansingRule(
                name="remove_device_fp",
                pattern=r'(user[_-]?agent|fingerprint|device[_-]?id|browser[_-]?fp)[:\s]*[^\s,]+',
                replacement='[DEVICE_FP_REDACTED]',
                description="Remove device fingerprinting data",
                applies_to=[DataDirection.OUTGOING],
                sensitivity=DataSensitivity.SENSITIVE
            ),
        ]
    
    def _round_amount_replacement(self, match) -> str:
        """Round amounts for privacy"""
        try:
            amount_str = match.group(1).replace('$', '').replace(',', '')
            amount = float(amount_str)
            
            if amount > 1000000:
                return f"~${amount/1000000:.1f}M"
            elif amount > 1000:
                return f"~${amount/1000:.0f}K"
            else:
                return f"~${amount:.0f}"
        except:
            return '[AMOUNT_REDACTED]'
    
    # ═══════════════════════════════════════════════════════════
    # MAIN CLEANSING METHODS
    # ═══════════════════════════════════════════════════════════
    
    def cleanse_string(self, value: str, direction: DataDirection, 
                      context: str = "default") -> tuple[str, List[str]]:
        """
        Cleanse a single string value
        
        Returns:
            (cleansed_value, list_of_rules_applied)
        """
        if not isinstance(value, str):
            return value, []
        
        rules = self.incoming_rules if direction == DataDirection.INCOMING else self.outgoing_rules
        applied_rules = []
        original = value
        
        for rule in rules:
            if direction in rule.applies_to:
                new_value = rule.apply(value)
                if new_value != value:
                    value = new_value
                    applied_rules.append(rule.name)
                    logger.debug(f"Applied rule '{rule.name}' in context '{context}'")
        
        return value, applied_rules
    
    def cleanse_dict(self, data: Dict[str, Any], direction: DataDirection,
                    context: str = "default") -> tuple[Dict, CleansingReport]:
        """
        Recursively cleanse a dictionary
        """
        report = CleansingReport(
            timestamp=datetime.now().isoformat(),
            direction=direction
        )
        
        original_json = json.dumps(data, default=str)
        report.original_size = len(original_json)
        
        cleansed = self._cleanse_recursive(data, direction, context, report)
        
        cleansed_json = json.dumps(cleansed, default=str)
        report.cleansed_size = len(cleansed_json)
        
        return cleansed, report
    
    def _cleanse_recursive(self, obj: Any, direction: DataDirection, 
                          context: str, report: CleansingReport) -> Any:
        """Recursively cleanse data structures"""
        
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                # Determine sensitivity based on key name
                sensitivity = self._classify_field(key)
                
                # Cleanse the key (for outgoing)
                cleansed_key = key
                if direction == DataDirection.OUTGOING:
                    cleansed_key, _ = self.cleanse_string(key, direction, context)
                
                # Recursively cleanse value
                cleansed_value = self._cleanse_recursive(value, direction, context, report)
                
                # Track what was cleansed
                if value != cleansed_value:
                    report.fields_cleansed.append(key)
                    if sensitivity == DataSensitivity.CRITICAL:
                        report.items_removed += 1
                    elif sensitivity == DataSensitivity.SENSITIVE:
                        report.items_masked += 1
                
                result[cleansed_key] = cleansed_value
            return result
            
        elif isinstance(obj, list):
            return [self._cleanse_recursive(item, direction, context, report) for item in obj]
            
        elif isinstance(obj, str):
            cleansed, rules = self.cleanse_string(obj, direction, context)
            report.rules_applied.extend(rules)
            return cleansed
            
        else:
            return obj
    
    def _classify_field(self, field_name: str) -> DataSensitivity:
        """Classify field sensitivity based on name"""
        field_lower = field_name.lower()
        
        critical_patterns = ['password', 'secret', 'key', 'private', 'seed', 'mnemonic', 'token']
        sensitive_patterns = ['wallet', 'address', 'email', 'phone', 'ip', 'telegram', 'user_id']
        
        if any(p in field_lower for p in critical_patterns):
            return DataSensitivity.CRITICAL
        elif any(p in field_lower for p in sensitive_patterns):
            return DataSensitivity.SENSITIVE
        else:
            return DataSensitivity.PUBLIC
    
    # ═══════════════════════════════════════════════════════════
    # CONTEXT-SPECIFIC CLEANSING
    # ═══════════════════════════════════════════════════════════
    
    def cleanse_incoming_api_request(self, data: Dict) -> tuple[Dict, CleansingReport]:
        """Cleanse incoming data from external API/webhook"""
        return self.cleanse_dict(data, DataDirection.INCOMING, "incoming_api")
    
    def cleanse_outgoing_to_external_ai(self, data: Dict) -> tuple[Dict, CleansingReport]:
        """Cleanse data before sending to external AI (Silicon Flow, Groq)"""
        return self.cleanse_dict(data, DataDirection.OUTGOING, "external_ai")
    
    def cleanse_for_public_channel(self, data: Dict) -> tuple[Dict, CleansingReport]:
        """Cleanse data for public Telegram/social media"""
        return self.cleanse_dict(data, DataDirection.OUTGOING, "public_channel")
    
    def cleanse_for_logging(self, data: Dict) -> tuple[Dict, CleansingReport]:
        """Cleanse data before logging (remove sensitive fields)"""
        return self.cleanse_dict(data, DataDirection.OUTGOING, "logging")
    
    def cleanse_contract_data(self, data: Dict, direction: DataDirection) -> tuple[Dict, CleansingReport]:
        """Cleanse smart contract related data"""
        return self.cleanse_dict(data, direction, "contract_data")


# ═══════════════════════════════════════════════════════════
# SPECIALIZED CLEANSERS
# ═══════════════════════════════════════════════════════════

class ContractDataCleanser:
    """Specialized cleanser for smart contract data"""
    
    @staticmethod
    def remove_code_comments(code: str) -> str:
        """Remove comments from Solidity code (removes dev fingerprints)"""
        # Remove single-line comments
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        # Remove multi-line comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        # Remove NatSpec
        code = re.sub(r'///.*$', '', code, flags=re.MULTILINE)
        return code.strip()
    
    @staticmethod
    def remove_metadata(code: str) -> str:
        """Remove metadata that could identify dev"""
        # SPDX license
        code = re.sub(r'//\s*SPDX-License-Identifier:.*$', '', code, flags=re.MULTILINE)
        # Author tags
        code = re.sub(r'(@author|@dev|@notice|@title).*$', '', code, flags=re.MULTILINE)
        # GitHub URLs
        code = re.sub(r'https?://github\.com/[^\s]+', '[REPO_URL]', code)
        return code.strip()
    
    @staticmethod
    def normalize_bytecode(bytecode: str) -> str:
        """Normalize bytecode (remove timestamps, metadata hash)"""
        # Remove Swarm hash (last 43 bytes of deployed bytecode)
        if len(bytecode) > 86:
            bytecode = bytecode[:-86]
        return bytecode


class BlockchainDataCleanser:
    """Specialized cleanser for blockchain data"""
    
    @staticmethod
    def sanitize_transaction(tx: Dict) -> Dict:
        """Sanitize transaction data for external sharing"""
        return {
            'hash': tx.get('hash', '')[:10] + '...' if tx.get('hash') else '',
            'from': tx.get('from', '')[:6] + '...' + tx.get('from', '')[-4:] if tx.get('from') else '',
            'to': tx.get('to', '')[:6] + '...' + tx.get('to', '')[-4:] if tx.get('to') else '',
            'value': f"~{float(tx.get('value', 0)) / 1e18:.2f} ETH" if tx.get('value') else '0',
            'timestamp': tx.get('timestamp'),  # Keep timestamp
            # Remove: input data, gas price, nonce
        }
    
    @staticmethod
    def sanitize_holder(holder: Dict) -> Dict:
        """Sanitize holder data"""
        return {
            'address': holder.get('address', '')[:6] + '...' + holder.get('address', '')[-4:],
            'percentage': holder.get('percentage'),
            'rank': holder.get('rank'),
            # Remove: exact balance, transaction count
        }


# ═══════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════

_pipeline = DataCleansingPipeline()

def cleanse_incoming(data: Dict) -> tuple[Dict, CleansingReport]:
    """Quick cleanse for incoming data"""
    return _pipeline.cleanse_incoming_api_request(data)

def cleanse_outgoing(data: Dict, context: str = "default") -> tuple[Dict, CleansingReport]:
    """Quick cleanse for outgoing data"""
    return _pipeline.cleanse_dict(data, DataDirection.OUTGOING, context)

def cleanse_for_ai(data: Dict) -> tuple[Dict, CleansingReport]:
    """Cleanse before sending to external AI"""
    return _pipeline.cleanse_outgoing_to_external_ai(data)

def cleanse_for_public(data: Dict) -> tuple[Dict, CleansingReport]:
    """Cleanse for public channels"""
    return _pipeline.cleanse_for_public_channel(data)


# ═══════════════════════════════════════════════════════════
# DEMONSTRATION
# ═══════════════════════════════════════════════════════════

def demo():
    """Demonstrate data cleansing"""
    print("🧼 RugMuncher Data Cleansing Pipeline Demo")
    print("=" * 70)
    
    pipeline = DataCleansingPipeline()
    
    # Sample incoming data (from API/webhook)
    incoming_data = {
        'contract_address': '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
        'wallet_address': '0x8ba1f109551bD432803012645Hac136c98C0000',
        'email': 'admin@scamtoken.com',
        'ip_address': '192.168.1.100',
        'telegram_id': '123456789',
        'amount_usd': 50000.50,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'timestamp': '2024-01-15T10:30:00Z',
        'xss_attempt': '<script>alert("xss")</script>',
        'sql_attempt': "'; DROP TABLE users; --",
        'contract_code': '''// SPDX-License-Identifier: MIT
// @author ScamDev
pragma solidity ^0.8.0;
// Malicious contract'''
    }
    
    print("\n📥 INCOMING DATA CLEANSING:")
    print("-" * 70)
    print("Original:")
    for k, v in incoming_data.items():
        print(f"  {k}: {str(v)[:60]}{'...' if len(str(v)) > 60 else ''}")
    
    cleansed_in, report_in = pipeline.cleanse_incoming_api_request(incoming_data)
    
    print("\nCleansed:")
    for k, v in cleansed_in.items():
        print(f"  {k}: {str(v)[:60]}{'...' if len(str(v)) > 60 else ''}")
    
    print(f"\nRules applied: {report_in.rules_applied}")
    print(f"Fields cleansed: {report_in.fields_cleansed}")
    
    # Sample outgoing data (to external AI)
    print("\n" + "=" * 70)
    print("\n📤 OUTGOING DATA CLEANSING (for External AI):")
    print("-" * 70)
    
    outgoing_data = {
        'token_name': 'Scam Token',
        'contract_address': '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
        'deployer_wallet': '0x8ba1f109551bD432803012645Hac136c98C0000',
        'liquidity_usd': 150000,
        'holder_data': [
            {'address': '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb', 'balance': 500000},
            {'address': '0x1111111111111111111111111111111111111111', 'balance': 100000}
        ],
        'ip_address': '10.0.0.1',
        'email': 'victim@email.com',
        'api_key': 'sk-abc123def456',
        'analysis_notes': 'High risk detected'
    }
    
    print("Original:")
    print(json.dumps(outgoing_data, indent=2)[:500])
    
    cleansed_out, report_out = pipeline.cleanse_outgoing_to_external_ai(outgoing_data)
    
    print("\nCleansed for External AI:")
    print(json.dumps(cleansed_out, indent=2))
    
    print(f"\n📊 Cleansing Report:")
    print(f"  Direction: {report_out.direction.value}")
    print(f"  Fields cleansed: {report_out.fields_cleansed}")
    print(f"  Items removed: {report_out.items_removed}")
    print(f"  Items masked: {report_out.items_masked}")
    print(f"  Size reduction: {report_out.original_size - report_out.cleansed_size} bytes")
    print(f"  Rules applied: {set(report_out.rules_applied)}")
    
    # Contract code cleansing
    print("\n" + "=" * 70)
    print("\n📝 SOLIDITY CODE CLEANSING:")
    print("-" * 70)
    
    contract_code = '''// SPDX-License-Identifier: MIT
// @author DevName
// GitHub: https://github.com/scammer/malicious-repo
pragma solidity ^0.8.0;

contract ScamToken {
    // Steal all the money
    function steal() external {
        // Implementation here
    }
}'''
    
    print("Original code:")
    print(contract_code)
    
    cc = ContractDataCleanser()
    no_comments = cc.remove_code_comments(contract_code)
    no_metadata = cc.remove_metadata(no_comments)
    
    print("\nAfter cleansing:")
    print(no_metadata)


if __name__ == "__main__":
    demo()
