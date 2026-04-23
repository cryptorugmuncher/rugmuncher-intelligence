#!/usr/bin/env python3
"""
API Key Rotator - Maximize Free Tiers
"""
import time
import random
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIAccount:
    name: str
    key: str
    daily_limit: int
    used_today: int = 0
    last_used: float = 0
    is_active: bool = True

class APIKeyRotator:
    """
    Rotates through multiple API keys to maximize free tier usage
    """
    
    def __init__(self, provider: str):
        self.provider = provider
        self.accounts: List[APIAccount] = []
        self.current_index = 0
        self.daily_reset_time = None
        
    def add_account(self, name: str, key: str, daily_limit: int):
        """Add an API account to rotation"""
        self.accounts.append(APIAccount(
            name=name,
            key=key,
            daily_limit=daily_limit
        ))
        logger.info(f"Added {self.provider} account: {name}")
    
    def get_key(self) -> Optional[str]:
        """Get next available API key"""
        self._reset_daily_counts_if_needed()
        
        # Try to find an account with remaining quota
        attempts = 0
        while attempts < len(self.accounts):
            account = self.accounts[self.current_index]
            
            if account.is_active and account.used_today < account.daily_limit:
                # Add small delay to avoid hitting rate limits
                time.sleep(random.uniform(0.1, 0.5))
                
                account.used_today += 1
                account.last_used = time.time()
                self.current_index = (self.current_index + 1) % len(self.accounts)
                
                logger.debug(f"Using {account.name} ({account.used_today}/{account.daily_limit})")
                return account.key
            
            self.current_index = (self.current_index + 1) % len(self.accounts)
            attempts += 1
        
        # All accounts exhausted
        logger.warning(f"All {self.provider} accounts exhausted. Waiting...")
        time.sleep(60)  # Wait a minute and retry
        return self.get_key()
    
    def _reset_daily_counts_if_needed(self):
        """Reset daily usage counts at midnight"""
        import datetime
        now = datetime.datetime.now()
        
        if self.daily_reset_time is None or now.date() != self.daily_reset_time.date():
            for account in self.accounts:
                account.used_today = 0
            self.daily_reset_time = now
            logger.info(f"Reset daily limits for {self.provider}")
    
    def get_stats(self) -> Dict:
        """Get usage statistics"""
        return {
            'provider': self.provider,
            'total_accounts': len(self.accounts),
            'total_daily_limit': sum(a.daily_limit for a in self.accounts),
            'total_used_today': sum(a.used_today for a in self.accounts),
            'accounts': [
                {
                    'name': a.name,
                    'used': a.used_today,
                    'limit': a.daily_limit,
                    'remaining': a.daily_limit - a.used_today
                }
                for a in self.accounts
            ]
        }


class MultiProviderRotator:
    """
    Manages rotators for multiple API providers
    """
    
    def __init__(self):
        self.rotators: Dict[str, APIKeyRotator] = {}
    
    def add_provider(self, provider: str) -> APIKeyRotator:
        """Add a new provider rotator"""
        self.rotators[provider] = APIKeyRotator(provider)
        return self.rotators[provider]
    
    def get_key(self, provider: str) -> Optional[str]:
        """Get key for specific provider"""
        if provider not in self.rotators:
            raise ValueError(f"Provider {provider} not configured")
        return self.rotators[provider].get_key()
    
    def get_all_stats(self) -> Dict:
        """Get stats for all providers"""
        return {
            provider: rotator.get_stats()
            for provider, rotator in self.rotators.items()
        }


# Pre-configured setups for common APIs

def create_groq_rotator() -> APIKeyRotator:
    """
    Create Groq rotator with 5 accounts
    Total: 5 x $200 = $1000/month free credits
    """
    rotator = APIKeyRotator("groq")
    # Add your accounts here
    # rotator.add_account("personal", "gsk_xxx1", 10000)
    # rotator.add_account("work", "gsk_xxx2", 10000)
    # rotator.add_account("alt1", "gsk_xxx3", 10000)
    # rotator.add_account("alt2", "gsk_xxx4", 10000)
    # rotator.add_account("alt3", "gsk_xxx5", 10000)
    return rotator

def create_openai_rotator() -> APIKeyRotator:
    """
    Create OpenAI rotator with 3 accounts
    Total: 3 x $18 = $54 free credits
    """
    rotator = APIKeyRotator("openai")
    # rotator.add_account("personal", "sk-xxx1", 5000)
    # rotator.add_account("work", "sk-xxx2", 5000)
    # rotator.add_account("alt", "sk-xxx3", 5000)
    return rotator

def create_github_rotator() -> APIKeyRotator:
    """
    Create GitHub rotator with multiple tokens
    Total: 5000 requests/hour per token
    """
    rotator = APIKeyRotator("github")
    # GitHub has 5000 requests/hour per token
    # rotator.add_account("token1", "ghp_xxx1", 5000)
    # rotator.add_account("token2", "ghp_xxx2", 5000)
    # rotator.add_account("token3", "ghp_xxx3", 5000)
    return rotator


if __name__ == "__main__":
    # Example usage
    multi = MultiProviderRotator()
    
    # Setup providers (add your actual keys)
    groq = multi.add_provider("groq")
    # groq.add_account("account1", "gsk_your_key_here", 10000)
    
    # Get stats
    print("API Rotation Stats:")
    print(multi.get_all_stats())
