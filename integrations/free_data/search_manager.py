"""
Free Search API Manager
Intelligently rotates through free search APIs
Maximizes zero-cost data access
"""

import requests
import random
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from duckduckgo_search import DDGS
from config import (
    BRAVE_API_KEY, BING_API_KEY, SERPER_API_KEY,
    TAVILY_API_KEY, EXA_API_KEY, NEWS_API_KEY,
    SEARX_INSTANCES, FREE_APIS
)

logger = logging.getLogger(__name__)

class FreeSearchManager:
    """
    Manages free search APIs with intelligent rotation
    Maximizes usage without hitting limits
    """
    
    def __init__(self):
        self.usage = {name: 0 for name in FREE_APIS}
        self.last_reset = datetime.now()
        self.ddgs = DDGS()
        
    def _check_reset(self):
        """Reset counters monthly"""
        if datetime.now() - self.last_reset > timedelta(days=30):
            self.usage = {name: 0 for name in FREE_APIS}
            self.last_reset = datetime.now()
            logger.info("Monthly usage counters reset")
    
    def _can_use(self, api_name: str) -> bool:
        """Check if API is available and under limit"""
        self._check_reset()
        
        config = FREE_APIS.get(api_name)
        if not config or not config['enabled']:
            return False
        
        current_usage = self.usage.get(api_name, 0)
        limit = config['monthly_limit']
        
        return current_usage < limit
    
    def _track_usage(self, api_name: str):
        """Track API usage"""
        self.usage[api_name] = self.usage.get(api_name, 0) + 1
    
    def _get_priority_apis(self) -> List[str]:
        """Get APIs sorted by priority (best first)"""
        available = [
            (name, config) 
            for name, config in FREE_APIS.items() 
            if self._can_use(name)
        ]
        
        # Sort by priority
        available.sort(key=lambda x: x[1]['priority'])
        return [name for name, _ in available]
    
    # ═══════════════════════════════════════════════════════════
    # SEARCH METHODS
    # ═══════════════════════════════════════════════════════════
    
    def search_brave(self, query: str, count: int = 10) -> Optional[List[Dict]]:
        """Brave Search API"""
        if not BRAVE_API_KEY:
            return None
        
        try:
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                "X-Subscription-Token": BRAVE_API_KEY,
                "Accept": "application/json"
            }
            params = {"q": query, "count": count}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                for item in data.get('web', {}).get('results', []):
                    results.append({
                        'title': item.get('title'),
                        'url': item.get('url'),
                        'description': item.get('description'),
                        'source': 'brave'
                    })
                
                self._track_usage('brave')
                return results
                
        except Exception as e:
            logger.error(f"Brave search error: {e}")
        
        return None
    
    def search_tavily(self, query: str, count: int = 10) -> Optional[List[Dict]]:
        """Tavily AI Search"""
        if not TAVILY_API_KEY:
            return None
        
        try:
            from tavily import TavilyClient
            tavily = TavilyClient(api_key=TAVILY_API_KEY)
            
            result = tavily.search(
                query=query,
                search_depth="basic",
                max_results=count,
                include_answer=False
            )
            
            results = []
            for item in result.get('results', []):
                results.append({
                    'title': item.get('title'),
                    'url': item.get('url'),
                    'description': item.get('content', '')[:200],
                    'source': 'tavily'
                })
            
            self._track_usage('tavily')
            return results
            
        except Exception as e:
            logger.error(f"Tavily search error: {e}")
        
        return None
    
    def search_exa(self, query: str, count: int = 10) -> Optional[List[Dict]]:
        """Exa Neural Search"""
        if not EXA_API_KEY:
            return None
        
        try:
            from exa_py import Exa
            exa = Exa(EXA_API_KEY)
            
            result = exa.search(query, num_results=count, use_autoprompt=True)
            
            results = []
            for item in result.results:
                results.append({
                    'title': item.title or '',
                    'url': item.url,
                    'description': item.text[:200] if hasattr(item, 'text') else '',
                    'source': 'exa'
                })
            
            self._track_usage('exa')
            return results
            
        except Exception as e:
            logger.error(f"Exa search error: {e}")
        
        return None
    
    def search_duckduckgo(self, query: str, count: int = 10) -> List[Dict]:
        """DuckDuckGo Search (unlimited, no API key)"""
        try:
            results = []
            ddg_results = self.ddgs.text(query, max_results=count)
            
            for item in ddg_results:
                results.append({
                    'title': item.get('title'),
                    'url': item.get('href'),
                    'description': item.get('body'),
                    'source': 'duckduckgo'
                })
            
            self._track_usage('duckduckgo')
            return results
            
        except Exception as e:
            logger.error(f"DDG search error: {e}")
        
        return []
    
    def search_searx(self, query: str, count: int = 10) -> List[Dict]:
        """Searx Search (public instances)"""
        instance = random.choice(SEARX_INSTANCES)
        
        try:
            url = f"{instance}/search"
            params = {"q": query, "format": "json", "pageno": 1}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get('results', [])[:count]:
                    results.append({
                        'title': item.get('title'),
                        'url': item.get('url'),
                        'description': item.get('content', ''),
                        'source': 'searx'
                    })
                
                self._track_usage('searx')
                return results
                
        except Exception as e:
            logger.error(f"Searx search error: {e}")
        
        return []
    
    # ═══════════════════════════════════════════════════════════
    # UNIFIED SEARCH (Intelligent Rotation)
    # ═══════════════════════════════════════════════════════════
    
    def search(self, query: str, count: int = 10, force_source: str = None) -> Dict:
        """
        Search with intelligent API rotation
        
        Tries premium APIs first, falls back to unlimited free sources
        """
        if force_source:
            # Use specific source
            method = getattr(self, f'search_{force_source}', None)
            if method:
                results = method(query, count)
                return {
                    'query': query,
                    'source': force_source,
                    'results': results or [],
                    'count': len(results or [])
                }
            return {'error': f'Source {force_source} not available'}
        
        # Intelligent rotation
        apis_to_try = self._get_priority_apis()
        
        for api_name in apis_to_try:
            method = getattr(self, f'search_{api_name}', None)
            if not method:
                continue
            
            try:
                logger.info(f"Trying {api_name} for: {query[:50]}...")
                results = method(query, count)
                
                if results and len(results) > 0:
                    return {
                        'query': query,
                        'source': api_name,
                        'results': results,
                        'count': len(results),
                        'usage': self.usage.copy()
                    }
                    
            except Exception as e:
                logger.warning(f"{api_name} failed: {e}")
                continue
        
        # All failed
        return {
            'query': query,
            'source': 'none',
            'results': [],
            'count': 0,
            'error': 'All search APIs exhausted'
        }
    
    def search_all(self, query: str, count: int = 5) -> Dict:
        """
        Search across ALL available APIs and aggregate
        Best for comprehensive research
        """
        all_results = []
        sources_used = []
        
        for api_name in FREE_APIS:
            if not self._can_use(api_name):
                continue
            
            method = getattr(self, f'search_{api_name}', None)
            if not method:
                continue
            
            try:
                results = method(query, count)
                if results:
                    all_results.extend(results)
                    sources_used.append(api_name)
            except:
                continue
        
        # Deduplicate by URL
        seen_urls = set()
        unique_results = []
        for r in all_results:
            url = r.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(r)
        
        return {
            'query': query,
            'sources': sources_used,
            'results': unique_results,
            'count': len(unique_results),
            'usage': self.usage.copy()
        }
    
    # ═══════════════════════════════════════════════════════════
    # NEWS SEARCH
    # ═══════════════════════════════════════════════════════════
    
    def search_news(self, query: str, count: int = 10) -> List[Dict]:
        """Search news articles"""
        results = []
        
        # Try NewsAPI
        if NEWS_API_KEY and self._can_use('newsapi'):
            try:
                url = "https://newsapi.org/v2/everything"
                params = {
                    "q": query,
                    "apiKey": NEWS_API_KEY,
                    "sortBy": "publishedAt",
                    "pageSize": count
                }
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('articles', []):
                        results.append({
                            'title': item.get('title'),
                            'url': item.get('url'),
                            'description': item.get('description'),
                            'published': item.get('publishedAt'),
                            'source': f"newsapi:{item.get('source', {}).get('name')}"
                        })
                    
                    self._track_usage('newsapi')
            except:
                pass
        
        # Fallback to DDG news
        if not results:
            try:
                ddg_news = self.ddgs.news(query, max_results=count)
                for item in ddg_news:
                    results.append({
                        'title': item.get('title'),
                        'url': item.get('url'),
                        'description': item.get('body'),
                        'published': item.get('date'),
                        'source': 'duckduckgo:news'
                    })
            except:
                pass
        
        return results
    
    # ═══════════════════════════════════════════════════════════
    # STATS & MONITORING
    # ═══════════════════════════════════════════════════════════
    
    def get_usage_stats(self) -> Dict:
        """Get current usage statistics"""
        stats = {}
        
        for api_name, config in FREE_APIS.items():
            used = self.usage.get(api_name, 0)
            limit = config['monthly_limit']
            
            if limit == float('inf'):
                remaining = 'unlimited'
                percent = 0
            else:
                remaining = limit - used
                percent = (used / limit) * 100
            
            stats[api_name] = {
                'used': used,
                'limit': limit if limit != float('inf') else 'unlimited',
                'remaining': remaining,
                'percent_used': round(percent, 1),
                'enabled': config['enabled']
            }
        
        return stats
    
    def get_capacity(self) -> Dict:
        """Get total remaining capacity this month"""
        stats = self.get_usage_stats()
        
        limited_total = 0
        limited_used = 0
        
        for api_name, data in stats.items():
            if data['limit'] != 'unlimited':
                limited_total += data['limit']
                limited_used += data['used']
        
        return {
            'limited_apis': {
                'total_quota': limited_total,
                'used': limited_used,
                'remaining': limited_total - limited_used,
                'percent_used': round((limited_used / limited_total) * 100, 1)
            },
            'unlimited_apis': ['duckduckgo', 'searx'],
            'total_capacity': f"{limited_total - limited_used}+ searches this month"
        }


# Singleton
_manager = None

def get_search_manager() -> FreeSearchManager:
    """Get singleton search manager"""
    global _manager
    if _manager is None:
        _manager = FreeSearchManager()
    return _manager
