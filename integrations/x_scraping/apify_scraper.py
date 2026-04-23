"""
Apify X/Twitter Scraper
Uses $5 credit for professional scraping
"""

import os
import requests
import logging
from typing import Dict, Optional, List
import time

logger = logging.getLogger(__name__)

APIFY_TOKEN = os.getenv('APIFY_TOKEN', '')
APIFY_BASE_URL = "https://api.apify.com/v2"

class ApifyXScraper:
    """
    Scrape X/Twitter using Apify actors
    Uses your $5 credit for reliable scraping
    """
    
    def __init__(self, token: str = None):
        self.token = token or APIFY_TOKEN
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        if not self.token:
            logger.warning("No Apify token provided!")
    
    def _get_actor_runs(self, actor_id: str, payload: dict, timeout_secs: int = 60) -> Optional[List[Dict]]:
        """
        Run an Apify actor and get results
        
        Args:
            actor_id: The actor to run (e.g., "quacker/twitter-scraper")
            payload: Input parameters
            timeout_secs: Max time to wait
            
        Returns:
            List of scraped items
        """
        if not self.token:
            logger.error("Apify token not configured")
            return None
        
        try:
            # Start actor run
            start_url = f"{APIFY_BASE_URL}/acts/{actor_id}/runs"
            
            response = requests.post(
                start_url,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code != 201:
                logger.error(f"Apify run failed: {response.status_code} - {response.text}")
                return None
            
            run_data = response.json()
            run_id = run_data['data']['id']
            dataset_id = run_data['data']['defaultDatasetId']
            
            logger.info(f"Apify run started: {run_id}")
            
            # Wait for completion
            start_time = time.time()
            while time.time() - start_time < timeout_secs:
                status_url = f"{APIFY_BASE_URL}/acts/{actor_id}/runs/{run_id}"
                status_resp = requests.get(status_url, headers=self.headers, timeout=10)
                
                if status_resp.status_code == 200:
                    status = status_resp.json()['data']['status']
                    
                    if status == 'SUCCEEDED':
                        # Get results
                        dataset_url = f"{APIFY_BASE_URL}/datasets/{dataset_id}/items"
                        items_resp = requests.get(dataset_url, headers=self.headers, timeout=30)
                        
                        if items_resp.status_code == 200:
                            return items_resp.json()
                        
                    elif status in ['FAILED', 'ABORTED', 'TIMED-OUT']:
                        logger.error(f"Apify run {run_id} failed with status: {status}")
                        return None
                
                time.sleep(2)  # Poll every 2 seconds
            
            logger.warning(f"Apify run {run_id} timed out")
            return None
            
        except Exception as e:
            logger.error(f"Apify error: {e}")
            return None
    
    def scrape_profile(self, handle: str, max_tweets: int = 20) -> Optional[Dict]:
        """
        Scrape X profile using Apify
        
        Actor: quacker/twitter-scraper (most popular, reliable)
        Cost: ~$0.001-0.005 per profile
        """
        logger.info(f"Apify: Scraping @{handle}")
        
        # Use twitter-scraper actor
        actor_id = "quacker/twitter-scraper"
        
        payload = {
            "handles": [handle],
            "tweetsDesired": max_tweets,
            "includeReplies": False,
            "includeRetweets": False,
            "maxTweets": max_tweets,
            "proxyConfig": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"]  # Better for X
            }
        }
        
        results = self._get_actor_runs(actor_id, payload, timeout_secs=120)
        
        if results and len(results) > 0:
            # Process results
            profile_data = {
                'success': True,
                'source': 'apify',
                'handle': handle,
                'actor': actor_id,
                'tweets': []
            }
            
            for item in results:
                if 'user' in item:
                    # First item usually has user info
                    user = item['user']
                    profile_data['user_info'] = {
                        'name': user.get('name'),
                        'screen_name': user.get('screen_name'),
                        'description': user.get('description'),
                        'followers_count': user.get('followers_count'),
                        'friends_count': user.get('friends_count'),
                        'statuses_count': user.get('statuses_count'),
                        'created_at': user.get('created_at'),
                        'verified': user.get('verified'),
                        'profile_image': user.get('profile_image_url_https')
                    }
                
                # Add tweet
                if 'full_text' in item:
                    profile_data['tweets'].append({
                        'text': item.get('full_text'),
                        'created_at': item.get('created_at'),
                        'retweet_count': item.get('retweet_count'),
                        'favorite_count': item.get('favorite_count'),
                        'url': f"https://x.com/{handle}/status/{item.get('id_str')}"
                    })
            
            return profile_data
        
        return None
    
    def search_tweets(self, query: str, max_results: int = 50) -> Optional[List[Dict]]:
        """
        Search tweets using Apify
        
        Cost: ~$0.01-0.05 per search
        """
        logger.info(f"Apify: Searching tweets for '{query}'")
        
        actor_id = "quacker/twitter-scraper"
        
        payload = {
            "searchTerms": [query],
            "tweetsDesired": max_results,
            "maxTweets": max_results,
            "proxyConfig": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"]
            }
        }
        
        results = self._get_actor_runs(actor_id, payload, timeout_secs=180)
        
        if results:
            tweets = []
            for item in results:
                if 'full_text' in item:
                    tweets.append({
                        'text': item.get('full_text'),
                        'created_at': item.get('created_at'),
                        'user': item.get('user', {}).get('screen_name'),
                        'retweets': item.get('retweet_count'),
                        'likes': item.get('favorite_count'),
                        'url': f"https://x.com/i/web/status/{item.get('id_str')}"
                    })
            
            return tweets
        
        return None
    
    def get_trending(self, location: str = "United States") -> Optional[List[Dict]]:
        """
        Get trending topics
        
        Cost: ~$0.001
        """
        actor_id = "petr_cermak/twitter-trends"
        
        payload = {
            "location": location
        }
        
        results = self._get_actor_runs(actor_id, payload, timeout_secs=60)
        
        if results and len(results) > 0:
            return results[0].get('trends', [])
        
        return None
    
    def get_usage(self) -> Dict:
        """Get Apify usage and remaining credits"""
        if not self.token:
            return {'error': 'No token configured'}
        
        try:
            # Get user info
            url = f"{APIFY_BASE_URL}/users/me"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()['data']
                return {
                    'username': data.get('username'),
                    'plan': data.get('plan', {}).get('planId'),
                    'credit': data.get('plan', {}).get('creditsUSD'),
                    'usage': data.get('plan', {}).get('usageUSD'),
                    'remaining': data.get('plan', {}).get('creditsUSD', 0) - data.get('plan', {}).get('usageUSD', 0)
                }
                
        except Exception as e:
            logger.error(f"Failed to get Apify usage: {e}")
        
        return {}


# Singleton
_scraper = None

def get_apify_scraper() -> ApifyXScraper:
    """Get singleton scraper"""
    global _scraper
    if _scraper is None:
        _scraper = ApifyXScraper()
    return _scraper
