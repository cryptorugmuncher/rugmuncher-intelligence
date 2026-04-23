"""
UPDATED Hybrid X Scraper
Priority: Apify ($5 credit) → Firecrawl (500/mo free) → Nitter (free)
"""

import logging
from typing import Dict, Optional
from apify_scraper import ApifyXScraper, get_apify_scraper
from firecrawl_scraper import FirecrawlXScraper, get_scraper as get_firecrawl
from nitter_scraper import NitterXScraper, get_scraper as get_nitter
from config import APIFY_CONFIG

logger = logging.getLogger(__name__)

class UltimateXScraper:
    """
    Ultimate X scraper with 4-tier system:
    1. Apify ($5 credit) - Most reliable, paid
    2. Firecrawl (500/mo free) - Structured, reliable
    3. Nitter (free) - Backup, unlimited
    4. Search APIs (free) - Last resort
    """
    
    def __init__(self):
        self.apify = get_apify_scraper()
        self.firecrawl = get_firecrawl()
        self.nitter = get_nitter()
        self.apify_used_credits = 0.0
        
        logger.info("Ultimate X Scraper initialized")
        logger.info(f"Apify available: {APIFY_CONFIG['enabled']} (${APIFY_CONFIG['credits']} credit)")
    
    async def scrape_profile(self, handle: str, prefer_reliability: bool = True) -> Optional[Dict]:
        """
        Scrape profile with intelligent 4-tier system
        
        Args:
            handle: X handle (without @)
            prefer_reliability: Use paid options first if available
            
        Returns:
            Profile data dict
        """
        # Tier 1: Apify (if credits available and prefer reliability)
        if prefer_reliability and APIFY_CONFIG['enabled']:
            if self.apify_used_credits < APIFY_CONFIG['credits']:
                logger.info(f"Trying Apify for @{handle}")
                result = self.apify.scrape_profile(handle)
                
                if result and result.get('success'):
                    self.apify_used_credits += APIFY_CONFIG['cost_per_profile']
                    logger.info(f"Apify success! Remaining credit: ${APIFY_CONFIG['credits'] - self.apify_used_credits:.2f}")
                    return result
                
                logger.warning("Apify failed, trying next tier")
            else:
                logger.info("Apify credits exhausted, using free tiers")
        
        # Tier 2: Firecrawl (free, structured)
        logger.info(f"Trying Firecrawl for @{handle}")
        result = self.firecrawl.scrape_profile(handle)
        
        if result and result.get('success'):
            logger.info(f"Firecrawl success for @{handle}")
            return result
        
        logger.warning("Firecrawl failed, trying Nitter")
        
        # Tier 3: Nitter (free, backup)
        logger.info(f"Trying Nitter for @{handle}")
        result = self.nitter.scrape_profile(handle)
        
        if result and result.get('success'):
            logger.info(f"Nitter success for @{handle}")
            return result
        
        logger.error(f"All scrapers failed for @{handle}")
        return None
    
    async def smart_scrape(self, handle: str, importance: str = 'medium') -> Optional[Dict]:
        """
        Smart scraping based on importance
        
        importance:
        - 'critical': Always use Apify if available
        - 'high': Prefer Apify
        - 'medium': Try Apify, fallback to free
        - 'low': Use free tiers only
        """
        if importance == 'critical':
            # Always use best available
            return await self.scrape_profile(handle, prefer_reliability=True)
        
        elif importance == 'low':
            # Skip Apify to save credits
            return await self.scrape_profile(handle, prefer_reliability=False)
        
        else:  # high, medium
            # Normal flow
            return await self.scrape_profile(handle, prefer_reliability=True)
    
    def get_credits_remaining(self) -> float:
        """Get remaining Apify credits"""
        if not APIFY_CONFIG['enabled']:
            return 0.0
        return APIFY_CONFIG['credits'] - self.apify_used_credits
    
    def get_status(self) -> Dict:
        """Get full scraper status"""
        return {
            'apify': {
                'available': APIFY_CONFIG['enabled'],
                'credits_total': APIFY_CONFIG['credits'],
                'credits_used': self.apify_used_credits,
                'credits_remaining': self.get_credits_remaining(),
                'estimated_remaining_scrapes': int(self.get_credits_remaining() / APIFY_CONFIG['cost_per_profile'])
            },
            'firecrawl': {
                'configured': bool(self.firecrawl.api_key),
                'free_tier': '500/month'
            },
            'nitter': {
                'instances': len(self.nitter.instances),
                'available': len(self.nitter.instances) - len(self.nitter.failed_instances)
            }
        }


# Update singleton
def get_ultimate_scraper() -> UltimateXScraper:
    """Get ultimate scraper"""
    global _ultimate_scraper
    if '_ultimate_scraper' not in globals():
        _ultimate_scraper = UltimateXScraper()
    return _ultimate_scraper

# For backwards compatibility
HybridXScraper = UltimateXScraper
get_hybrid_scraper = get_ultimate_scraper
