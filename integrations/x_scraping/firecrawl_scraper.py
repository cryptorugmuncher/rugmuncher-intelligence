"""
Firecrawl X Scraper
Primary method - 500 free scrapes/month
"""

import requests
import time
import logging
from typing import Dict, Optional, List
from config import FIRECRAWL_API_KEY, FIRECRAWL_BASE_URL, FIRECRAWL_RATE_LIMIT

logger = logging.getLogger(__name__)

class FirecrawlXScraper:
    """Scrape X/Twitter using Firecrawl API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or FIRECRAWL_API_KEY
        self.base_url = FIRECRAWL_BASE_URL
        self.last_request_time = 0
        
        if not self.api_key:
            logger.warning("No Firecrawl API key provided!")
    
    def _rate_limit(self):
        """Respect rate limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < 1.0 / FIRECRAWL_RATE_LIMIT:
            time.sleep(1.0 / FIRECRAWL_RATE_LIMIT - elapsed)
        self.last_request_time = time.time()
    
    def scrape_profile(self, handle: str) -> Optional[Dict]:
        """
        Scrape X profile
        
        Args:
            handle: X handle (without @)
            
        Returns:
            Dict with profile data or None
        """
        if not self.api_key:
            logger.error("Firecrawl API key not configured")
            return None
        
        self._rate_limit()
        
        url = f"{self.base_url}/scrape"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "url": f"https://x.com/{handle}",
            "formats": ["markdown", "html"],
            "onlyMainContent": True,
            "waitFor": 3000  # Wait 3s for JS to load
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return {
                        'success': True,
                        'handle': handle,
                        'content': data['data']['markdown'],
                        'html': data['data']['html'],
                        'source': 'firecrawl'
                    }
            else:
                logger.error(f"Firecrawl error {response.status_code}: {response.text}")
                
        except Exception as e:
            logger.error(f"Firecrawl request failed: {e}")
        
        return None
    
    def scrape_tweet(self, tweet_id: str) -> Optional[Dict]:
        """Scrape specific tweet"""
        if not self.api_key:
            return None
        
        self._rate_limit()
        
        url = f"{self.base_url}/scrape"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "url": f"https://x.com/i/web/status/{tweet_id}",
            "formats": ["markdown"]
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return {
                        'success': True,
                        'tweet_id': tweet_id,
                        'content': data['data']['markdown'],
                        'source': 'firecrawl'
                    }
                    
        except Exception as e:
            logger.error(f"Firecrawl tweet scrape failed: {e}")
        
        return None
    
    def search_x(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search X using Firecrawl crawl
        Note: This crawls search results page
        """
        if not self.api_key:
            return []
        
        self._rate_limit()
        
        # X search URL
        search_url = f"https://x.com/search?q={query}&f=live"
        
        url = f"{self.base_url}/crawl"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "url": search_url,
            "limit": max_results,
            "formats": ["markdown"]
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data['data']
                    
        except Exception as e:
            logger.error(f"Firecrawl search failed: {e}")
        
        return []
    
    def get_usage(self) -> Dict:
        """Get API usage stats"""
        if not self.api_key:
            return {'error': 'No API key'}
        
        url = f"{self.base_url}/team/credits"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get usage: {e}")
        
        return {}


# Singleton instance
_scraper = None

def get_scraper() -> FirecrawlXScraper:
    """Get singleton scraper instance"""
    global _scraper
    if _scraper is None:
        _scraper = FirecrawlXScraper()
    return _scraper
