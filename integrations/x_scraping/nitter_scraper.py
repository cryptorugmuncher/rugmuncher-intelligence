"""
Nitter X Scraper
Backup method - rotates through instances
"""

import requests
import time
import logging
import random
from typing import Dict, Optional, List
from bs4 import BeautifulSoup
from config import NITTER_INSTANCES, MAX_RETRIES, RETRY_DELAY

logger = logging.getLogger(__name__)

class NitterXScraper:
    """Scrape X/Twitter via Nitter instances"""
    
    def __init__(self):
        self.instances = NITTER_INSTANCES.copy()
        self.current_instance_idx = 0
        self.failed_instances = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _get_instance(self) -> str:
        """Get next working instance"""
        available = [i for i in self.instances if i not in self.failed_instances]
        
        if not available:
            # Reset failed instances after some time
            logger.warning("All Nitter instances failed, resetting...")
            self.failed_instances.clear()
            available = self.instances
        
        # Round-robin selection
        instance = available[self.current_instance_idx % len(available)]
        self.current_instance_idx += 1
        return instance
    
    def _mark_failed(self, instance: str):
        """Mark instance as failed"""
        self.failed_instances.add(instance)
        logger.warning(f"Nitter instance failed: {instance}")
    
    def scrape_profile(self, handle: str) -> Optional[Dict]:
        """
        Scrape X profile via Nitter
        
        Args:
            handle: X handle (without @)
            
        Returns:
            Dict with profile data or None
        """
        for attempt in range(MAX_RETRIES):
            instance = self._get_instance()
            url = f"{instance}/{handle}"
            
            try:
                logger.info(f"Trying Nitter instance: {instance}")
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract data
                    profile_data = self._parse_profile(soup, handle)
                    
                    if profile_data:
                        profile_data['source'] = 'nitter'
                        profile_data['instance'] = instance
                        return profile_data
                    
                elif response.status_code in [403, 429]:
                    self._mark_failed(instance)
                    
            except requests.Timeout:
                logger.warning(f"Timeout on {instance}")
                self._mark_failed(instance)
            except Exception as e:
                logger.error(f"Nitter error on {instance}: {e}")
                self._mark_failed(instance)
            
            time.sleep(RETRY_DELAY)
        
        logger.error(f"All Nitter instances failed for @{handle}")
        return None
    
    def _parse_profile(self, soup: BeautifulSoup, handle: str) -> Optional[Dict]:
        """Parse profile HTML"""
        try:
            # Profile name
            name_elem = soup.find('a', class_='profile-card-fullname')
            name = name_elem.text.strip() if name_elem else handle
            
            # Bio
            bio_elem = soup.find('div', class_='profile-bio')
            bio = bio_elem.text.strip() if bio_elem else ''
            
            # Stats
            stats = {}
            stat_items = soup.find_all('div', class_='profile-stat-num')
            if len(stat_items) >= 3:
                stats['tweets'] = stat_items[0].text.strip()
                stats['following'] = stat_items[1].text.strip()
                stats['followers'] = stat_items[2].text.strip()
            
            # Tweets (last 5)
            tweets = []
            tweet_divs = soup.find_all('div', class_='timeline-item')[:5]
            for tweet in tweet_divs:
                text_elem = tweet.find('div', class_='tweet-content')
                date_elem = tweet.find('span', class_='tweet-date')
                
                if text_elem:
                    tweets.append({
                        'text': text_elem.get_text(strip=True),
                        'date': date_elem.text.strip() if date_elem else ''
                    })
            
            return {
                'success': True,
                'handle': handle,
                'name': name,
                'bio': bio,
                'stats': stats,
                'tweets': tweets,
                'raw_html': str(soup)[:10000]  # First 10KB
            }
            
        except Exception as e:
            logger.error(f"Failed to parse profile: {e}")
            return None
    
    def search_tweets(self, query: str, max_results: int = 20) -> List[Dict]:
        """Search tweets via Nitter"""
        results = []
        
        for attempt in range(MAX_RETRIES):
            instance = self._get_instance()
            # Nitter search URL format
            url = f"{instance}/search?f=tweets&q={query}"
            
            try:
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    tweets = soup.find_all('div', class_='timeline-item')[:max_results]
                    
                    for tweet in tweets:
                        parsed = self._parse_tweet(tweet)
                        if parsed:
                            results.append(parsed)
                    
                    if results:
                        return results
                        
            except Exception as e:
                logger.error(f"Search error on {instance}: {e}")
                self._mark_failed(instance)
            
            time.sleep(RETRY_DELAY)
        
        return results
    
    def _parse_tweet(self, tweet_elem) -> Optional[Dict]:
        """Parse individual tweet"""
        try:
            text_elem = tweet_elem.find('div', class_='tweet-content')
            date_elem = tweet_elem.find('span', class_='tweet-date')
            author_elem = tweet_elem.find('a', class_='username')
            
            return {
                'text': text_elem.get_text(strip=True) if text_elem else '',
                'date': date_elem.text.strip() if date_elem else '',
                'author': author_elem.text.strip() if author_elem else '',
            }
        except:
            return None
    
    def get_instance_health(self) -> Dict:
        """Check health of all instances"""
        health = {}
        
        for instance in self.instances:
            try:
                start = time.time()
                response = self.session.get(instance, timeout=10)
                latency = time.time() - start
                
                health[instance] = {
                    'status': 'up' if response.status_code == 200 else 'down',
                    'latency': round(latency, 2),
                    'failed': instance in self.failed_instances
                }
            except:
                health[instance] = {
                    'status': 'down',
                    'latency': None,
                    'failed': True
                }
        
        return health


# Singleton
_scraper = None

def get_scraper() -> NitterXScraper:
    """Get singleton scraper instance"""
    global _scraper
    if _scraper is None:
        _scraper = NitterXScraper()
    return _scraper
