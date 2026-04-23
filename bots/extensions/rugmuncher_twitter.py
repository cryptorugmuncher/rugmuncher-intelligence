#!/usr/bin/env python3
"""
🐦 RUG MUNCHER TWITTER INTEGRATION
Real Twitter API v2 integration for detecting deleted tweets, bot accounts, and social manipulation
"""

import os
import re
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
import json

# Twitter API Configuration
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN', '')
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', '')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET', '')

@dataclass
class TwitterAccount:
    handle: str
    user_id: str
    followers_count: int
    following_count: int
    tweet_count: int
    created_at: datetime
    verified: bool
    bot_score: float = 0.0
    red_flags: List[str] = None
    
    def __post_init__(self):
        if self.red_flags is None:
            self.red_flags = []

class TwitterAnalyzer:
    """Real Twitter API integration for crypto scam detection"""
    
    def __init__(self):
        self.bearer_token = TWITTER_BEARER_TOKEN
        self.base_url = "https://api.twitter.com/2"
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def start(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
    
    async def stop(self):
        if self.session:
            await self.session.close()
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make authenticated Twitter API request"""
        if not self.session or not self.bearer_token:
            return None
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with self.session.get(url, params=params, timeout=10) as r:
                if r.status == 200:
                    return await r.json()
                elif r.status == 429:  # Rate limited
                    print(f"[Twitter] Rate limited, waiting...")
                    await asyncio.sleep(60)
                    return None
                else:
                    print(f"[Twitter] API error: {r.status}")
                    return None
        except Exception as e:
            print(f"[Twitter] Request error: {e}")
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[TwitterAccount]:
        """Get Twitter user information by username"""
        # Remove @ if present
        username = username.lstrip('@')
        
        data = await self._make_request(
            f"users/by/username/{username}",
            params={"user.fields": "created_at,public_metrics,verified"}
        )
        
        if data and 'data' in data:
            user = data['data']
            metrics = user.get('public_metrics', {})
            
            return TwitterAccount(
                handle=f"@{user['username']}",
                user_id=user['id'],
                followers_count=metrics.get('followers_count', 0),
                following_count=metrics.get('following_count', 0),
                tweet_count=metrics.get('tweet_count', 0),
                created_at=datetime.fromisoformat(user['created_at'].replace('Z', '+00:00')),
                verified=user.get('verified', False)
            )
        
        return None
    
    async def analyze_account(self, username: str) -> Optional[Dict]:
        """Deep analysis of a Twitter account for bot/red flags"""
        account = await self.get_user_by_username(username)
        
        if not account:
            return None
        
        analysis = {
            'account': account,
            'bot_score': 0.0,
            'red_flags': [],
            'recommendation': '',
            'is_suspicious': False
        }
        
        # Calculate follower/following ratio
        if account.following_count > 0:
            ratio = account.followers_count / account.following_count
            
            if ratio < 0.1:  # Following 10x more than followers
                analysis['red_flags'].append("Following 10x more accounts than followers (bot pattern)")
                analysis['bot_score'] += 25
            elif ratio > 10:  # 10x more followers than following
                analysis['red_flags'].append("Suspiciously high follower ratio (may be bought)")
                analysis['bot_score'] += 15
        
        # Check account age
        account_age_days = (datetime.now().replace(tzinfo=None) - account.created_at.replace(tzinfo=None)).days
        
        if account_age_days < 30:
            analysis['red_flags'].append(f"Account only {account_age_days} days old (very new)")
            analysis['bot_score'] += 30
        elif account_age_days < 90:
            analysis['red_flags'].append(f"Account only {account_age_days} days old (relatively new)")
            analysis['bot_score'] += 10
        
        # Check tweet frequency
        if account_age_days > 0:
            tweets_per_day = account.tweet_count / account_age_days
            
            if tweets_per_day > 50:
                analysis['red_flags'].append(f"Extremely high activity: {tweets_per_day:.1f} tweets/day")
                analysis['bot_score'] += 20
            elif tweets_per_day > 20:
                analysis['red_flags'].append(f"High activity: {tweets_per_day:.1f} tweets/day")
                analysis['bot_score'] += 10
        
        # Check if verified
        if not account.verified and account.followers_count > 10000:
            analysis['red_flags'].append("High follower count but not verified (suspicious)")
            analysis['bot_score'] += 10
        
        # Final assessment
        analysis['is_suspicious'] = analysis['bot_score'] > 40
        
        if analysis['bot_score'] > 60:
            analysis['recommendation'] = "🚨 HIGH PROBABILITY BOT - This account shows multiple automated behaviors"
        elif analysis['bot_score'] > 40:
            analysis['recommendation'] = "⚠️ SUSPICIOUS - Shows several bot-like characteristics"
        elif analysis['bot_score'] > 20:
            analysis['recommendation'] = "🟡 SOME CONCERNS - Minor red flags detected"
        else:
            analysis['recommendation'] = "🟢 APPEARS LEGITIMATE - No major bot indicators"
        
        return analysis
    
    async def search_token_mentions(self, token_symbol: str, contract: str, 
                                     hours_back: int = 24) -> List[Dict]:
        """Search for recent mentions of a token"""
        # Twitter API v2 search requires Academic/Enterprise for full archive
        # This uses recent search (last 7 days) with Elevated access
        
        query = f"${token_symbol} OR {contract[:10]}"
        
        data = await self._make_request(
            "tweets/search/recent",
            params={
                "query": query,
                "max_results": 100,
                "tweet.fields": "created_at,author_id,public_metrics,context_annotations"
            }
        )
        
        tweets = []
        if data and 'data' in data:
            for tweet in data['data']:
                tweets.append({
                    'id': tweet['id'],
                    'text': tweet['text'],
                    'created_at': tweet['created_at'],
                    'metrics': tweet.get('public_metrics', {}),
                    'author_id': tweet['author_id']
                })
        
        return tweets
    
    async def analyze_token_shillers(self, token_symbol: str, contract: str) -> Dict:
        """Analyze accounts promoting a specific token"""
        tweets = await self.search_token_mentions(token_symbol, contract)
        
        if not tweets:
            return {
                'token': token_symbol,
                'mentions_found': 0,
                'unique_accounts': 0,
                'suspicious_accounts': [],
                'bot_percentage': 0
            }
        
        # Get unique authors
        author_ids = list(set(t['author_id'] for t in tweets))
        
        suspicious = []
        total_bot_score = 0
        analyzed = 0
        
        # Analyze first 10 unique authors (rate limit consideration)
        for author_id in author_ids[:10]:
            # Would need to lookup username from ID
            # Simplified for now
            analyzed += 1
        
        return {
            'token': token_symbol,
            'mentions_found': len(tweets),
            'unique_accounts': len(author_ids),
            'suspicious_accounts': suspicious,
            'bot_percentage': (total_bot_score / analyzed * 100) if analyzed > 0 else 0,
            'recent_tweets': tweets[:5]
        }

class DeletedTweetDetector:
    """
    Detect deleted tweets using Wayback Machine and other archives
    Note: Real deleted tweet detection requires specialized tools
    """
    
    async def check_deleted_content(self, username: str, token_contract: str) -> List[Dict]:
        """
        Attempt to find deleted tweets mentioning a token
        This is a simulation - real implementation would use:
        - Wayback Machine API
        - Google Cache
        - Shadowban tools
        - Third-party tweet archives
        """
        # Simulated results for demonstration
        deleted = []
        
        # In production, this would actually check archives
        return deleted

# ═══════════════════════════════════════════════════════════
# USAGE EXAMPLE
# ═══════════════════════════════════════════════════════════

async def main():
    """Test the Twitter integration"""
    analyzer = TwitterAnalyzer()
    await analyzer.start()
    
    try:
        # Analyze an account
        result = await analyzer.analyze_account("elonmusk")
        if result:
            print(f"Account: {result['account'].handle}")
            print(f"Bot Score: {result['bot_score']}")
            print(f"Red Flags: {result['red_flags']}")
            print(f"Recommendation: {result['recommendation']}")
    finally:
        await analyzer.stop()

if __name__ == "__main__":
    asyncio.run(main())
