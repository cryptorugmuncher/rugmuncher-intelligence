"""
Hybrid X Scraper
Firecrawl (primary) → Nitter (backup)
With Groq processing
"""

import logging
from typing import Dict, Optional
from firecrawl_scraper import FirecrawlXScraper, get_scraper as get_firecrawl
from nitter_scraper import NitterXScraper, get_scraper as get_nitter

logger = logging.getLogger(__name__)

class HybridXScraper:
    """
    Intelligent X scraper with failover
    Primary: Firecrawl (reliable, structured)
    Backup: Nitter (free, unlimited)
    """
    
    def __init__(self):
        self.firecrawl = get_firecrawl()
        self.nitter = get_nitter()
        self.primary_failures = 0
        self.FAILOVER_THRESHOLD = 2
    
    async def scrape_profile(self, handle: str, use_backup: bool = False) -> Optional[Dict]:
        """
        Scrape profile with automatic failover
        
        Args:
            handle: X handle
            use_backup: Force use backup method
            
        Returns:
            Profile data dict
        """
        # Try primary first (unless forced backup)
        if not use_backup and self.primary_failures < self.FAILOVER_THRESHOLD:
            logger.info(f"Trying Firecrawl for @{handle}")
            result = self.firecrawl.scrape_profile(handle)
            
            if result and result.get('success'):
                self.primary_failures = 0  # Reset on success
                logger.info(f"Firecrawl success for @{handle}")
                return result
            else:
                self.primary_failures += 1
                logger.warning(f"Firecrawl failed ({self.primary_failures}/{self.FAILOVER_THRESHOLD})")
        
        # Failover to Nitter
        logger.info(f"Failing over to Nitter for @{handle}")
        result = self.nitter.scrape_profile(handle)
        
        if result and result.get('success'):
            logger.info(f"Nitter success for @{handle}")
            return result
        
        logger.error(f"Both scrapers failed for @{handle}")
        return None
    
    async def scrape_with_processor(self, handle: str, groq_processor=None) -> Optional[Dict]:
        """
        Scrape and process with Groq
        
        Args:
            handle: X handle
            groq_processor: Optional Groq processing function
            
        Returns:
            Processed profile data
        """
        # Scrape
        raw_data = await self.scrape_profile(handle)
        
        if not raw_data:
            return None
        
        # Process with Groq if available
        if groq_processor:
            try:
                processed = await groq_processor(raw_data)
                return processed
            except Exception as e:
                logger.error(f"Groq processing failed: {e}")
                # Return raw if processing fails
                return raw_data
        
        return raw_data
    
    def get_health_status(self) -> Dict:
        """Get health of both scrapers"""
        return {
            'firecrawl': {
                'configured': bool(self.firecrawl.api_key),
                'recent_failures': self.primary_failures,
                'status': 'healthy' if self.primary_failures < self.FAILOVER_THRESHOLD else 'degraded'
            },
            'nitter': {
                'instances_total': len(self.nitter.instances),
                'instances_failed': len(self.nitter.failed_instances),
                'instances_available': len(self.nitter.instances) - len(self.nitter.failed_instances),
                'health': self.nitter.get_instance_health()
            }
        }


# Singleton
_scraper = None

def get_hybrid_scraper() -> HybridXScraper:
    """Get singleton hybrid scraper"""
    global _scraper
    if _scraper is None:
        _scraper = HybridXScraper()
    return _scraper
