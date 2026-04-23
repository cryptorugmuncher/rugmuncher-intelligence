#!/usr/bin/env python3
"""
External Intelligence Feeds Integration
Connect to third-party data sources for enhanced analysis
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

class IntelligenceFeedManager:
    """
    Manage external intelligence feeds
    """
    
    def __init__(self):
        self.feeds: Dict[str, Dict] = {}
        self.cache = {}
        self.enabled_feeds = []
    
    def register_feed(self, feed_id: str, config: Dict):
        """Register an external intelligence feed"""
        self.feeds[feed_id] = {
            'id': feed_id,
            'name': config['name'],
            'provider': config['provider'],
            'endpoint': config['endpoint'],
            'api_key': config.get('api_key'),
            'rate_limit': config.get('rate_limit', 100),
            'cost_per_call': config.get('cost_per_call', 0),
            'data_types': config.get('data_types', []),
            'reliability_score': config.get('reliability', 0.8),
            'last_update': None,
            'status': 'inactive'
        }
    
    def enable_feed(self, feed_id: str):
        """Enable a feed"""
        if feed_id in self.feeds:
            self.feeds[feed_id]['status'] = 'active'
            self.enabled_feeds.append(feed_id)
    
    async def query_feed(self, feed_id: str, query: Dict) -> Dict:
        """Query a specific feed"""
        if feed_id not in self.feeds:
            return {'error': 'Feed not found'}
        
        feed = self.feeds[feed_id]
        
        if feed['status'] != 'active':
            return {'error': 'Feed not active'}
        
        # This would make actual API calls
        # Placeholder implementation
        
        return {
            'feed_id': feed_id,
            'query': query,
            'results': [],
            'timestamp': datetime.now().isoformat(),
            'source_reliability': feed['reliability_score']
        }
    
    async def query_all_feeds(self, query: Dict) -> Dict:
        """Query all enabled feeds"""
        results = {}
        
        tasks = []
        for feed_id in self.enabled_feeds:
            task = self.query_feed(feed_id, query)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for feed_id, response in zip(self.enabled_feeds, responses):
            if isinstance(response, Exception):
                results[feed_id] = {'error': str(response)}
            else:
                results[feed_id] = response
        
        return {
            'query': query,
            'feed_results': results,
            'aggregated_at': datetime.now().isoformat(),
            'feeds_queried': len(self.enabled_feeds)
        }


# Pre-configured feeds
AVAILABLE_FEEDS = {
    'chainalysis': {
        'name': 'Chainalysis KYT',
        'provider': 'Chainalysis',
        'data_types': ['risk_score', 'category', 'clustering'],
        'description': 'Industry-standard risk scoring and clustering'
    },
    'elliptic': {
        'name': 'Elliptic Lens',
        'provider': 'Elliptic',
        'data_types': ['risk_score', 'entity', 'licensing'],
        'description': 'Cryptocurrency risk intelligence'
    },
    'tether': {
        'name': 'Tether Blacklist',
        'provider': 'Tether',
        'data_types': ['blocked_addresses'],
        'description': 'USDT blacklisted addresses'
    },
    'ofac': {
        'name': 'OFAC SDN List',
        'provider': 'US Treasury',
        'data_types': ['sanctions', 'sdn_entries'],
        'description': 'Specially Designated Nationals',
        'free': True
    },
    'un_sanctions': {
        'name': 'UN Consolidated List',
        'provider': 'United Nations',
        'data_types': ['sanctions', 'individuals', 'entities'],
        'description': 'UN Security Council sanctions',
        'free': True
    },
    'europol': {
        'name': 'Europol Focal Point',
        'provider': 'Europol',
        'data_types': ['crime_reports', 'intelligence'],
        'description': 'Law enforcement intelligence (LE only)',
        'restricted': True
    },
    'bitcoinabuse': {
        'name': 'Bitcoin Abuse Database',
        'provider': 'Community',
        'data_types': ['reported_addresses', 'abuse_types'],
        'description': 'Community-reported scam addresses',
        'free': True
    },
    'chainabuse': {
        'name': 'Chainabuse',
        'provider': 'Chainabuse',
        'data_types': ['reports', 'wallet_labels', 'scam_types'],
        'description': 'Multi-chain scam reporting platform',
        'free': True
    },
    'scamalert': {
        'name': 'Scam Alert Database',
        'provider': 'Various',
        'data_types': ['scam_urls', 'wallet_addresses'],
        'description': 'Aggregated scam reports',
        'free': True
    },
    'slowmist': {
        'name': 'SlowMist Hacked',
        'provider': 'SlowMist',
        'data_types': ['hack_incidents', 'stolen_funds', 'tracking'],
        'description': 'Blockchain security incidents',
        'free': True
    },
    'forta': {
        'name': 'Forta Network',
        'provider': 'Forta',
        'data_types': ['threat_intelligence', 'bot_alerts'],
        'description': 'Real-time threat detection network',
        'blockchain_native': True
    },
    'trmlabs': {
        'name': 'TRM Labs',
        'provider': 'TRM',
        'data_types': ['risk_score', 'entity', 'investigation'],
        'description': 'Blockchain intelligence platform'
    },
    'ciphertrace': {
        'name': 'CipherTrace',
        'provider': 'Mastercard',
        'data_types': ['risk_score', 'attribution', 'compliance'],
        'description': 'Cryptocurrency intelligence'
    },
    'merkle_science': {
        'name': 'Merkle Science',
        'provider': 'Merkle Science',
        'data_types': ['risk_score', 'transaction_monitoring'],
        'description': 'Blockchain risk monitoring'
    },
    'solidus_labs': {
        'name': 'Solidus Labs',
        'provider': 'Solidus',
        'data_types': ['market_abuse', 'manipulation'],
        'description': 'Crypto-native market surveillance'
    }
}


class FeedIntegrations:
    """
    Specific integrations for common feeds
    """
    
    @staticmethod
    def get_ofac_sanctions() -> List[Dict]:
        """Fetch OFAC sanctions list"""
        # In production, this would fetch from:
        # https://www.treasury.gov/ofac/downloads/sdnlist.txt
        # or use the OFAC API
        
        return {
            'source': 'OFAC SDN List',
            'last_updated': datetime.now().isoformat(),
            'total_entries': 0,  # Would be actual count
            'crypto_addresses': [],  # Would be extracted addresses
            'note': 'Fetch from https://www.treasury.gov/ofac/downloads/'
        }
    
    @staticmethod
    def get_un_sanctions() -> List[Dict]:
        """Fetch UN sanctions list"""
        # https://www.un.org/securitycouncil/content/un-sc-consolidated-list
        return {
            'source': 'UN Consolidated List',
            'last_updated': datetime.now().isoformat(),
            'note': 'Fetch from https://www.un.org/securitycouncil/content/un-sc-consolidated-list'
        }
    
    @staticmethod
    def get_bitcoin_abuse_reports(address: str) -> Dict:
        """Query Bitcoin Abuse database"""
        # https://www.bitcoinabuse.com/api-docs
        return {
            'source': 'Bitcoin Abuse',
            'address': address,
            'abuse_reports': 0,
            'abuse_types': [],
            'note': 'Use API: https://www.bitcoinabuse.com/api/reports/check'
        }
    
    @staticmethod
    def get_chainabuse_data(address: str) -> Dict:
        """Query Chainabuse database"""
        return {
            'source': 'Chainabuse',
            'address': address,
            'reports': [],
            'note': 'Use Chainabuse API or web interface'
        }


# Open Source Intelligence (OSINT) Sources
OSINT_SOURCES = {
    'blockchain_explorers': {
        'etherscan': 'https://etherscan.io',
        'solscan': 'https://solscan.io',
        'tronscan': 'https://tronscan.org',
        'bscscan': 'https://bscscan.com',
        'polygonscan': 'https://polygonscan.com'
    },
    
    'social_media': {
        'twitter_x': 'Crypto scam reports',
        'reddit': 'r/CryptoScams, r/Scams',
        'telegram': 'Scam alert channels',
        'discord': 'Community warnings'
    },
    
    'forums': {
        'bitcointalk': 'Scam accusations',
        'reddit_crypto': 'Various subreddits',
        '4chan_biz': 'Unverified claims'
    },
    
    'news_sources': {
        'cointelegraph': 'Security news',
        'coindesk': 'Investigation reports',
        'the_block': 'Research reports',
        'decrypt': 'Scam alerts'
    },
    
    'government_sources': {
        'fbi_ic3': 'https://ic3.gov',
        'ftc': 'https://reportfraud.ftc.gov',
        'cftc': 'https://www.cftc.gov/tipline',
        'sec': 'https://www.sec.gov/tcr'
    },
    
    'academic_research': {
        'arxiv': 'Blockchain security papers',
        'ieee': 'Transaction analysis research',
        'springer': 'Cryptocurrency crime studies'
    }
}


class OSINTAggregator:
    """
    Aggregate open source intelligence
    """
    
    def __init__(self):
        self.sources = OSINT_SOURCES
        self.collected_data = {}
    
    def search_address(self, address: str) -> Dict:
        """Search for address across OSINT sources"""
        results = {
            'address': address,
            'search_time': datetime.now().isoformat(),
            'sources_checked': [],
            'mentions': [],
            'risk_indicators': []
        }
        
        # In production, this would:
        # 1. Check blockchain explorers
        # 2. Search social media APIs
        # 3. Query forums
        # 4. Check news sources
        # 5. Review government databases
        
        return results
    
    def monitor_mentions(self, keywords: List[str]) -> List[Dict]:
        """Monitor for mentions of keywords"""
        mentions = []
        
        # In production, this would use:
        # - Twitter/X API
        # - Reddit API
        # - Telegram bot API
        # - RSS feeds for news
        
        return mentions


if __name__ == "__main__":
    print("External Intelligence Feeds Manager")
    print("=" * 50)
    print(f"\nAvailable feeds: {len(AVAILABLE_FEEDS)}")
    
    print("\nFree feeds:")
    for feed_id, feed in AVAILABLE_FEEDS.items():
        if feed.get('free'):
            print(f"  ✓ {feed['name']}")
    
    print("\nOSINT Sources:")
    for category, sources in OSINT_SOURCES.items():
        print(f"  {category}: {len(sources)} sources")
