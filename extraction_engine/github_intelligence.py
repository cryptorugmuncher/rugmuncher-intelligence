#!/usr/bin/env python3
"""
GitHub Intelligence Miner
Extract crypto scam intel from GitHub (free, unlimited with tokens)
"""
import requests
import base64
import re
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubIntelligence:
    """
    Mine GitHub for crypto scam intelligence
    Free tier: 5000 requests/hour per token
    """
    
    # Patterns for scam detection
    SCAM_PATTERNS = [
        r'honeypot',
        r'rug.?pull',
        r'scam.?contract',
        r'malicious.?token',
        r'fake.?token',
        r'pump.?and.?dump',
        r'drainer',
        r'wallet.?drain',
    ]
    
    SUSPICIOUS_KEYWORDS = [
        'private_key',
        'api_key',
        'secret_key',
        'mnemonic',
        'wallet_seed',
    ]
    
    def __init__(self, tokens: List[str]):
        self.tokens = tokens
        self.current_token = 0
        self.base_url = "https://api.github.com"
    
    def _get_headers(self) -> Dict:
        """Get headers with rotating token"""
        token = self.tokens[self.current_token % len(self.tokens)]
        return {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def _handle_rate_limit(self, response):
        """Handle rate limiting by switching tokens"""
        if response.status_code == 403:
            reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
            remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
            
            if remaining == 0:
                logger.warning(f"Token {self.current_token} rate limited")
                self.current_token += 1
                
                if self.current_token >= len(self.tokens):
                    # All tokens exhausted, wait
                    wait_time = max(reset_time - int(datetime.now().timestamp()), 60)
                    logger.info(f"All tokens exhausted, waiting {wait_time}s...")
                    import time
                    time.sleep(wait_time)
                    self.current_token = 0
    
    def search_scam_contracts(self, language: str = "solidity", per_page: int = 100) -> List[Dict]:
        """
        Search GitHub for reported scam contracts
        """
        results = []
        
        queries = [
            f"honeypot language:{language}",
            f"rug pull contract language:{language}",
            f"malicious token ethereum",
            f"scam contract reported",
            f"fake token solidity",
            f"wallet drainer",
        ]
        
        for query in queries:
            url = f"{self.base_url}/search/code"
            params = {
                'q': query,
                'per_page': per_page,
                'sort': 'updated',
                'order': 'desc'
            }
            
            try:
                response = requests.get(url, headers=self._get_headers(), params=params)
                
                if response.status_code == 403:
                    self._handle_rate_limit(response)
                    continue
                
                data = response.json()
                items = data.get('items', [])
                
                for item in items:
                    result = {
                        'repository': item['repository']['full_name'],
                        'file_path': item['path'],
                        'html_url': item['html_url'],
                        'score': item['score'],
                        'query': query,
                    }
                    results.append(result)
                
                logger.info(f"Found {len(items)} results for query: {query}")
                
            except Exception as e:
                logger.error(f"Error searching GitHub: {e}")
        
        return results
    
    def search_leaked_keys(self) -> List[Dict]:
        """
        Search for potentially leaked API keys and private keys
        (For security research purposes)
        """
        results = []
        
        # Search patterns that might indicate leaked keys
        patterns = [
            'ETH_PRIVATE_KEY=',
            'SOLANA_PRIVATE_KEY=',
            'ALCHEMY_API_KEY=',
            'INFURA_API_KEY=',
            'extension:env PRIVATE_KEY',
            'extension:json "mnemonic"',
        ]
        
        for pattern in patterns:
            url = f"{self.base_url}/search/code"
            params = {'q': pattern, 'per_page': 30}
            
            try:
                response = requests.get(url, headers=self._get_headers(), params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('items', []):
                        # Don't actually fetch the content to avoid exposing keys
                        results.append({
                            'repository': item['repository']['full_name'],
                            'warning': f'Potential leaked keys in {item["path"]}',
                            'url': item['html_url']
                        })
                        
            except Exception as e:
                logger.error(f"Error searching for keys: {e}")
        
        return results
    
    def get_repository_info(self, repo: str) -> Optional[Dict]:
        """Get metadata about a repository"""
        url = f"{self.base_url}/repos/{repo}"
        
        try:
            response = requests.get(url, headers=self._get_headers())
            if response.status_code == 200:
                data = response.json()
                return {
                    'name': data['name'],
                    'owner': data['owner']['login'],
                    'created_at': data['created_at'],
                    'updated_at': data['updated_at'],
                    'stars': data['stargazers_count'],
                    'forks': data['forks_count'],
                    'language': data['language'],
                    'topics': data.get('topics', []),
                    'description': data['description'],
                }
        except Exception as e:
            logger.error(f"Error getting repo info: {e}")
        
        return None
    
    def get_user_activity(self, username: str) -> Optional[Dict]:
        """Get recent activity for a user"""
        url = f"{self.base_url}/users/{username}/events"
        
        try:
            response = requests.get(url, headers=self._get_headers())
            if response.status_code == 200:
                events = response.json()
                return {
                    'username': username,
                    'recent_events': len(events),
                    'event_types': list(set(e['type'] for e in events)),
                    'repositories': list(set(
                        e['repo']['name'] for e in events if 'repo' in e
                    ))
                }
        except Exception as e:
            logger.error(f"Error getting user activity: {e}")
        
        return None
    
    def analyze_contract_similarity(self, contract_code: str) -> List[Dict]:
        """
        Search for similar contracts (potential copy-paste scams)
        """
        # Extract function signatures
        functions = re.findall(r'function\s+(\w+)', contract_code)
        
        similar = []
        for func in functions[:5]:  # Check top 5 functions
            query = f"function {func} solidity"
            url = f"{self.base_url}/search/code"
            
            try:
                response = requests.get(
                    url, 
                    headers=self._get_headers(), 
                    params={'q': query, 'per_page': 10}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('items', [])[:3]:
                        similar.append({
                            'function': func,
                            'repository': item['repository']['full_name'],
                            'similarity_score': item['score'],
                            'url': item['html_url']
                        })
                        
            except Exception as e:
                logger.error(f"Error analyzing similarity: {e}")
        
        return similar
    
    def find_scam_report_issues(self) -> List[Dict]:
        """
        Search for issues/PRs reporting scams
        """
        results = []
        queries = [
            'scam report in:title',
            'honeypot in:title',
            'rug pull in:title',
            'malicious contract in:title',
        ]
        
        for query in queries:
            url = f"{self.base_url}/search/issues"
            params = {'q': query, 'sort': 'updated', 'order': 'desc'}
            
            try:
                response = requests.get(url, headers=self._get_headers(), params=params)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('items', []):
                        results.append({
                            'title': item['title'],
                            'url': item['html_url'],
                            'state': item['state'],
                            'created_at': item['created_at'],
                            'body_preview': item['body'][:200] if item['body'] else '',
                        })
            except Exception as e:
                logger.error(f"Error searching issues: {e}")
        
        return results


if __name__ == "__main__":
    # Example usage
    print("GitHub Intelligence Miner")
    print("=" * 50)
    
    # Initialize with your GitHub tokens
    # Get tokens: https://github.com/settings/tokens
    tokens = []  # Add your tokens: ['ghp_xxx', 'ghp_yyy', ...]
    
    if not tokens:
        print("⚠️  Add GitHub tokens to use this miner")
        print("Get tokens at: https://github.com/settings/tokens")
    else:
        miner = GitHubIntelligence(tokens)
        
        print("\nSearching for scam contracts...")
        scams = miner.search_scam_contracts()
        print(f"Found {len(scams)} potential scam contracts")
        
        for scam in scams[:5]:
            print(f"  - {scam['repository']}: {scam['file_path']}")
