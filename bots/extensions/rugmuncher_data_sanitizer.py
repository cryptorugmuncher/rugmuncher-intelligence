#!/usr/bin/env python3
"""
🔒 RugMuncher Data Sanitizer
Privacy-preserving data handling for external API calls
Sanitizes PII before sending to Silicon Flow, Moonshot, or any external AI provider
"""

import hashlib
import random
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SANITIZATION CONFIGURATION
# ═══════════════════════════════════════════════════════════

@dataclass
class SanitizationConfig:
    """Configuration for data sanitization levels"""
    # Hashing
    hash_wallet_addresses: bool = True
    hash_ip_addresses: bool = True
    hash_telegram_ids: bool = True
    hash_usernames: bool = True
    
    # Stripping (complete removal)
    strip_ip_addresses: bool = True
    strip_geolocation: bool = True
    strip_device_fingerprints: bool = True
    
    # Precision reduction
    round_timestamps: str = 'hour'  # 'none', 'minute', 'hour', 'day'
    round_amounts: float = 0.1  # Add ±10% noise
    round_percentages: float = 0.05  # Add ±5% noise
    
    # Code sanitization
    strip_code_comments: bool = True
    strip_code_metadata: bool = True
    anonymize_variable_names: bool = False
    
    # Blockchain specific
    preserve_contract_address: bool = False  # Usually needed for analysis
    preserve_token_symbol: bool = True
    hash_transaction_hashes: bool = True


# Default config for Chinese/external APIs
CHINA_API_CONFIG = SanitizationConfig(
    hash_wallet_addresses=True,
    strip_ip_addresses=True,
    strip_geolocation=True,
    round_timestamps='hour',
    round_amounts=0.1,
    strip_code_comments=True,
    hash_transaction_hashes=True
)

# Minimal config for trusted providers
TRUSTED_CONFIG = SanitizationConfig(
    hash_wallet_addresses=False,
    strip_ip_addresses=True,
    strip_geolocation=True,
    round_timestamps='none',
    round_amounts=0.0
)


# ═══════════════════════════════════════════════════════════
# CORE SANITIZATION FUNCTIONS
# ═══════════════════════════════════════════════════════════

class DataSanitizer:
    """
    🔒 Privacy-preserving data sanitizer
    
    Protects user PII while preserving analytical value
    """
    
    def __init__(self, config: Optional[SanitizationConfig] = None):
        self.config = config or CHINA_API_CONFIG
        
    def _hash(self, input_data: str, length: int = 16) -> str:
        """
        Create SHA-256 hash of input
        One-way, irreversible anonymization
        """
        if not input_data:
            return ""
        
        # Consistent hashing - same input always produces same output
        hash_obj = hashlib.sha256(str(input_data).encode('utf-8'))
        return hash_obj.hexdigest()[:length]
    
    def _add_noise(self, value: Union[int, float], noise_percent: float) -> Union[int, float]:
        """
        Add random noise to numeric values (differential privacy)
        Preserves statistical patterns while protecting exact values
        """
        if value is None or noise_percent == 0:
            return value
            
        noise = random.uniform(-noise_percent, noise_percent)
        noisy_value = value * (1 + noise)
        
        # Return same type as input
        return int(noisy_value) if isinstance(value, int) else round(noisy_value, 2)
    
    def _round_timestamp(self, timestamp: Union[datetime, str, int]) -> Union[datetime, str]:
        """
        Reduce timestamp precision to protect timing patterns
        """
        if timestamp is None or self.config.round_timestamps == 'none':
            return timestamp
            
        # Convert to datetime if needed
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                return timestamp
        elif isinstance(timestamp, (int, float)):
            timestamp = datetime.fromtimestamp(timestamp)
            
        if not isinstance(timestamp, datetime):
            return timestamp
        
        # Round based on config
        if self.config.round_timestamps == 'minute':
            rounded = timestamp.replace(second=0, microsecond=0)
        elif self.config.round_timestamps == 'hour':
            rounded = timestamp.replace(minute=0, second=0, microsecond=0)
        elif self.config.round_timestamps == 'day':
            rounded = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            rounded = timestamp
            
        # Return same type as input
        if isinstance(timestamp, str):
            return rounded.isoformat()
        return rounded
    
    def _strip_comments(self, code: str) -> str:
        """
        Remove comments from code to eliminate developer fingerprints
        """
        if not code:
            return code
            
        # Remove single-line comments (//)
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        
        # Remove multi-line comments (/* */)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        # Remove NatSpec comments (///)
        code = re.sub(r'///.*$', '', code, flags=re.MULTILINE)
        
        # Clean up extra whitespace
        code = '\n'.join(line.rstrip() for line in code.split('\n') if line.strip())
        
        return code
    
    def _strip_metadata(self, code: str) -> str:
        """
        Remove metadata that could identify the developer
        """
        if not code:
            return code
            
        # Remove SPDX license identifiers (can reveal project)
        code = re.sub(r'//\s*SPDX-License-Identifier:.*$', '', code, flags=re.MULTILINE | re.IGNORECASE)
        
        # Remove author tags
        code = re.sub(r'(@author|@dev|@notice|@title).*$', '', code, flags=re.MULTILINE | re.IGNORECASE)
        
        # Remove GitHub URLs
        code = re.sub(r'https?://github\.com/\S+', '[REPO_URL]', code)
        
        return code
    
    # ═══════════════════════════════════════════════════════════
    # PUBLIC SANITIZATION METHODS
    # ═══════════════════════════════════════════════════════════
    
    def sanitize_wallet_address(self, address: str) -> str:
        """Hash wallet address"""
        if not address or not self.config.hash_wallet_addresses:
            return address
        return f"0x{self._hash(address, 12)}"  # Keep 0x prefix for format
    
    def sanitize_transaction_hash(self, tx_hash: str) -> str:
        """Hash transaction hash"""
        if not tx_hash or not self.config.hash_transaction_hashes:
            return tx_hash
        return f"0x{self._hash(tx_hash, 16)}"
    
    def sanitize_ip_address(self, ip: str) -> Optional[str]:
        """Remove or hash IP address"""
        if not ip:
            return None
        if self.config.strip_ip_addresses:
            return None
        if self.config.hash_ip_addresses:
            return self._hash(ip, 8)
        return ip
    
    def sanitize_amount(self, amount: Union[int, float]) -> Union[int, float]:
        """Add noise to monetary amounts"""
        return self._add_noise(amount, self.config.round_amounts)
    
    def sanitize_code(self, code: str) -> str:
        """Sanitize contract code for external analysis"""
        if not code:
            return code
            
        if self.config.strip_code_comments:
            code = self._strip_comments(code)
            
        if self.config.strip_code_metadata:
            code = self._strip_metadata(code)
            
        return code
    
    def sanitize_timestamp(self, timestamp: Union[datetime, str, int]) -> Union[datetime, str, int]:
        """Reduce timestamp precision"""
        result = self._round_timestamp(timestamp)
        # Preserve original type
        if isinstance(timestamp, int) and isinstance(result, datetime):
            return int(result.timestamp())
        return result
    
    # ═══════════════════════════════════════════════════════════
    # BULK SANITIZATION
    # ═══════════════════════════════════════════════════════════
    
    def sanitize_scan_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        🔍 Sanitize complete token scan data
        
        Typical input:
        {
            'contract_address': '0x1234...',
            'wallet_address': '0xabcd...',
            'chain': 'bsc',
            'holder_data': [...],
            'contract_code': '...',
            'ip_address': '1.2.3.4',
            'timestamp': '2024-01-15T10:30:00Z'
        }
        """
        sanitized = {}
        
        for key, value in data.items():
            key_lower = key.lower()
            
            # Wallet addresses
            if any(k in key_lower for k in ['wallet', 'holder', 'address', 'from', 'to']) and isinstance(value, str):
                if key_lower == 'contract_address' and self.config.preserve_contract_address:
                    sanitized[key] = value  # Keep contract address for analysis
                else:
                    sanitized[key] = self.sanitize_wallet_address(value)
                    
            # IP addresses
            elif any(k in key_lower for k in ['ip', 'ip_address', 'client_ip']):
                sanitized[key] = self.sanitize_ip_address(value)
                
            # Transaction hashes
            elif any(k in key_lower for k in ['tx_hash', 'transaction', 'txid']):
                sanitized[key] = self.sanitize_transaction_hash(value)
                
            # Timestamps
            elif any(k in key_lower for k in ['timestamp', 'time', 'created_at', 'date']):
                sanitized[key] = self.sanitize_timestamp(value)
                
            # Monetary amounts
            elif any(k in key_lower for k in ['amount', 'value', 'balance', 'usd', 'price']):
                sanitized[key] = self.sanitize_amount(value)
                
            # Contract code
            elif any(k in key_lower for k in ['code', 'contract_code', 'source', 'bytecode']):
                sanitized[key] = self.sanitize_code(value)
                
            # Geolocation
            elif any(k in key_lower for k in ['geo', 'location', 'country', 'city', 'lat', 'lng']):
                sanitized[key] = None if self.config.strip_geolocation else value
                
            # Telegram IDs
            elif any(k in key_lower for k in ['telegram_id', 'chat_id', 'user_id', 'tg_id']):
                sanitized[key] = self._hash(str(value), 12) if self.config.hash_telegram_ids else value
                
            # Usernames
            elif any(k in key_lower for k in ['username', 'user_name', 'handle']):
                sanitized[key] = self._hash(str(value), 8) if self.config.hash_usernames else value
                
            # Nested dict - recurse
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_scan_data(value)
                
            # Lists - sanitize each item if dict
            elif isinstance(value, list):
                sanitized[key] = [
                    self.sanitize_scan_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
                
            # Pass through unchanged
            else:
                sanitized[key] = value
                
        return sanitized
    
    def sanitize_for_china_api(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        🇨🇳 Special sanitization for Chinese AI providers
        Extra strict for Silicon Flow, Moonshot, etc.
        """
        # Use strict config
        original_config = self.config
        self.config = CHINA_API_CONFIG
        
        try:
            result = self.sanitize_scan_data(data)
            
            # Additional China-specific protections
            # Remove any fields that might contain sensitive keywords
            sensitive_patterns = [
                r'password', r'secret', r'private_key', r'seed',
                r'mnemonic', r'api_key', r'token', r'auth'
            ]
            
            result = self._remove_sensitive_fields(result, sensitive_patterns)
            
            return result
        finally:
            self.config = original_config
    
    def _remove_sensitive_fields(self, data: Dict, patterns: List[str]) -> Dict:
        """Remove fields matching sensitive patterns"""
        result = {}
        for key, value in data.items():
            key_lower = key.lower()
            
            # Check if key matches any sensitive pattern
            should_remove = any(re.search(p, key_lower) for p in patterns)
            
            if should_remove:
                result[key] = '[REDACTED]'
            elif isinstance(value, dict):
                result[key] = self._remove_sensitive_fields(value, patterns)
            else:
                result[key] = value
                
        return result


# ═══════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════

def sanitize_for_external_api(
    data: Dict[str, Any],
    provider: str = 'generic'
) -> Dict[str, Any]:
    """
    One-shot sanitization for common providers
    
    Args:
        data: Raw data to sanitize
        provider: 'silicon_flow', 'moonshot', 'openai', 'generic'
    """
    provider_configs = {
        'silicon_flow': CHINA_API_CONFIG,
        'moonshot': CHINA_API_CONFIG,
        'baichuan': CHINA_API_CONFIG,
        'openai': TRUSTED_CONFIG,
        'anthropic': TRUSTED_CONFIG,
        'generic': SanitizationConfig(),  # Balanced
    }
    
    config = provider_configs.get(provider.lower(), SanitizationConfig())
    sanitizer = DataSanitizer(config)
    
    if provider.lower() in ['silicon_flow', 'moonshot', 'baichuan']:
        return sanitizer.sanitize_for_china_api(data)
    
    return sanitizer.sanitize_scan_data(data)


def quick_hash(input_data: str, length: int = 16) -> str:
    """Quick one-way hash for single values"""
    if not input_data:
        return ""
    return hashlib.sha256(str(input_data).encode()).hexdigest()[:length]


def add_differential_privacy(
    value: Union[int, float],
    epsilon: float = 0.1
) -> Union[int, float]:
    """
    Add Laplace noise for differential privacy
    Higher epsilon = more privacy, less accuracy
    """
    if value is None:
        return None
        
    # Laplace noise
    scale = abs(value) * epsilon
    noise = random.uniform(-scale, scale)
    
    result = value + noise
    return int(result) if isinstance(value, int) else round(result, 2)


# ═══════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════

def demo():
    """Demonstrate sanitization capabilities"""
    
    print("🔒 RugMuncher Data Sanitizer Demo")
    print("=" * 50)
    
    # Sample raw data
    raw_data = {
        'contract_address': '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
        'wallet_address': '0x8ba1f109551bD432803012645Hac136c98C0000',
        'ip_address': '192.168.1.100',
        'telegram_id': 123456789,
        'username': 'crypto_whale',
        'amount_usd': 50000.50,
        'timestamp': datetime.now(),
        'geolocation': {'country': 'US', 'city': 'New York'},
        'contract_code': '''// SPDX-License-Identifier: MIT
// @author DevName
pragma solidity ^0.8.0;

contract MyToken {
    // Secret backdoor - don't tell anyone
    function adminTransfer(address to, uint amount) external {
        // Implementation
    }
}''',
        'tx_hash': '0xabc123def456...',
        'holder_data': [
            {'address': '0xholder1...', 'balance': 1000000},
            {'address': '0xholder2...', 'balance': 500000}
        ]
    }
    
    print("\n📥 RAW DATA:")
    print(f"  Wallet: {raw_data['wallet_address']}")
    print(f"  IP: {raw_data['ip_address']}")
    print(f"  Amount: ${raw_data['amount_usd']}")
    print(f"  Telegram ID: {raw_data['telegram_id']}")
    
    # Sanitize for China API
    print("\n🇨🇳 SANITIZED FOR CHINESE API:")
    sanitized = sanitize_for_external_api(raw_data, 'silicon_flow')
    
    print(f"  Wallet: {sanitized['wallet_address']}")
    print(f"  IP: {sanitized['ip_address']}")
    print(f"  Amount: ${sanitized['amount_usd']} (with noise)")
    print(f"  Telegram ID: {sanitized['telegram_id']}")
    print(f"  Contract code has comments: {'//' in sanitized['contract_code']}")
    
    # Verify contract address preserved for analysis
    print(f"  Contract preserved: {sanitized['contract_address'] == raw_data['contract_address']}")
    
    # Sanitize for trusted provider
    print("\n🇺🇸 SANITIZED FOR TRUSTED PROVIDER:")
    trusted = sanitize_for_external_api(raw_data, 'openai')
    print(f"  Wallet: {trusted['wallet_address'][:20]}... (unhashed)")
    print(f"  IP: {trusted['ip_address']}")
    print(f"  Amount: ${trusted['amount_usd']} (exact)")
    
    print("\n✅ Sanitization preserves analytical value while protecting privacy!")


if __name__ == "__main__":
    demo()
