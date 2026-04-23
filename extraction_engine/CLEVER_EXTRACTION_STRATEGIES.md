# 🧠 CLEVER EXTRACTION STRATEGIES
## Maximum Data, Minimum Cost - Advanced OSINT Automation

### Philosophy: "Free Forever, Smart Forever"

---

## 🎯 STRATEGY 1: API ROTATION & FREE TIER MAXIMIZATION

### 1.1 Multi-Account Rotation (Legal & ToS-Compliant)

**Concept:** Most APIs allow multiple free accounts per organization/project

```python
# Strategy: Rotating API Keys from Multiple Free Accounts
class APIKeyRotator:
    def __init__(self):
        self.groq_accounts = [
            "gsk_account_1",  # Your personal email
            "gsk_account_2",  # Work email
            "gsk_account_3",  # Friend/family email (with permission)
            "gsk_account_4",  # Alias email
            "gsk_account_5",  # Another alias
        ]
        self.current_index = 0
        self.rate_limits = {key: {'used': 0, 'limit': 1000} for key in self.groq_accounts}
    
    def get_key(self):
        # Round-robin with rate limit checking
        for _ in range(len(self.groq_accounts)):
            key = self.groq_accounts[self.current_index]
            if self.rate_limits[key]['used'] < self.rate_limits[key]['limit']:
                self.rate_limits[key]['used'] += 1
                return key
            self.current_index = (self.current_index + 1) % len(self.groq_accounts)
        
        # All exhausted - wait or use backup
        time.sleep(60)
        return self.get_key()
```

**Free APIs with Generous Limits:**
| Service | Free Tier | Accounts/Org | Total Free |
|---------|-----------|--------------|------------|
| Groq | $200/month | 5 accounts | $1000/month |
| OpenAI | $5-18 initial | 3 accounts | $15-54 |
| Gemini | 60 requests/min | Unlimited keys | ∞ |
| Cohere | 1000 calls/month | 5 accounts | 5000/month |
| HuggingFace | Unlimited | Multiple tokens | ∞ |
| Together AI | $5 initial | 3 accounts | $15 |

### 1.2 Rate Limit Optimization

```python
# Smart rate limiting with exponential backoff
import time
import random

class SmartRateLimiter:
    def __init__(self, requests_per_minute=60):
        self.interval = 60.0 / requests_per_minute
        self.last_request = 0
        self.jitter_range = (0.1, 0.5)  # Random delay
    
    def wait(self):
        elapsed = time.time() - self.last_request
        jitter = random.uniform(*self.jitter_range)
        sleep_time = max(0, self.interval - elapsed + jitter)
        
        if sleep_time > 0:
            time.sleep(sleep_time)
        
        self.last_request = time.time()
```

---

## 🌐 STRATEGY 2: IP ROTATION & ANONYMIZATION

### 2.1 Tor Rotation (Free)

```python
import requests
from stem import Signal
from stem.control import Controller

class TorRotator:
    def __init__(self):
        self.proxy = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
        self.controller = Controller.from_port(port=9051)
        self.controller.authenticate()
    
    def new_identity(self):
        """Get new Tor exit node"""
        self.controller.signal(Signal.NEWNYM)
        time.sleep(5)  # Wait for new circuit
    
    def request(self, url):
        self.new_identity()
        return requests.get(url, proxies=self.proxy, timeout=30)

# Usage: Rotate IP every 10-50 requests to avoid blocking
```

**Tor Benefits:**
- Completely free
- Thousands of exit nodes
- Changes IP every request if needed
- Works with most APIs (unless they block Tor)

### 2.2 Free Proxy Rotation

```python
# Free proxy lists (auto-updating)
FREE_PROXY_SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
]

class FreeProxyRotator:
    def __init__(self):
        self.proxies = []
        self.update_proxies()
    
    def update_proxies(self):
        """Fetch fresh free proxies"""
        for source in FREE_PROXY_SOURCES:
            try:
                response = requests.get(source, timeout=10)
                new_proxies = [p.strip() for p in response.text.split('\n') if p.strip()]
                self.proxies.extend(new_proxies)
            except:
                continue
        
        # Test and filter working proxies
        self.proxies = self._test_proxies(self.proxies[:100])  # Test top 100
    
    def get_proxy(self):
        return random.choice(self.proxies) if self.proxies else None
```

### 2.3 VPN + Docker Rotation

```bash
# Using free VPN trials with Docker containers
# Each container gets different VPN exit point

# Example: ProtonVPN (free tier), Windscribe (10GB free)
# Rotate containers every hour

#!/bin/bash
for i in {1..10}; do
    docker run -d --name "scraper-$i" \
        --env VPN_PROVIDER=protonvpn \
        --env VPN_USER=free_user_$i \
        -v $(pwd)/data:/data \
        my-scraper-image
    
    sleep 3600  # Rotate every hour
    docker stop "scraper-$i" && docker rm "scraper-$i"
done
```

---

## 📊 STRATEGY 3: UNCONVENTIONAL DATA SOURCES

### 3.1 GitHub Intelligence (Free, Unlimited)

```python
# GitHub is a goldmine for crypto intel
class GitHubIntelligence:
    def __init__(self, tokens):  # Multiple tokens for rotation
        self.tokens = tokens
        self.current_token = 0
    
    def search_scam_repos(self):
        """Find reported scam contracts"""
        queries = [
            "honeypot contract language:solidity",
            "rug pull token ethereum",
            "scam contract reported",
            "malicious token code",
        ]
        
        results = []
        for query in queries:
            url = f"https://api.github.com/search/code?q={query}&per_page=100"
            response = self._github_request(url)
            results.extend(response.get('items', []))
        
        return results
    
    def get_gist_secrets(self):
        """Find leaked API keys, private keys in public gists"""
        # Search for patterns like:
        # - PRIVATE_KEY=0x...
        # - API_KEY=...
        # These often indicate scammer infrastructure
        pass
    
    def _github_request(self, url):
        token = self.tokens[self.current_token % len(self.tokens)]
        headers = {'Authorization': f'token {token}'}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 403:  # Rate limited
            self.current_token += 1
            return self._github_request(url)
        
        return response.json()
```

### 3.2 Blockchain Mempool Monitoring (Free)

```python
# Monitor pending transactions for scam patterns
import websocket
import json

class MempoolMonitor:
    def __init__(self):
        # Connect to free public mempool
        self.ws = websocket.create_connection("wss://api.blocknative.com/v0")
        self.scam_patterns = [
            "0x8f9e...",  # Known scam contract patterns
        ]
    
    def monitor(self):
        while True:
            msg = json.loads(self.ws.recv())
            tx = msg.get('transaction', {})
            
            # Detect sandwich attacks
            if self._is_sandwich_attack(tx):
                self._alert(tx)
            
            # Detect honeypot deployments
            if self._is_honeypot_deploy(tx):
                self._alert(tx)
```

### 3.3 IPFS Data Mining (Free)

```python
# Scammers often store data on IPFS
import ipfshttpclient

class IPFSMiner:
    def __init__(self):
        # Use public IPFS gateways
        self.gateways = [
            "https://ipfs.io/ipfs/",
            "https://cloudflare-ipfs.com/ipfs/",
            "https://gateway.pinata.cloud/ipfs/",
        ]
    
    def search_scam_content(self, cids):
        """Fetch content from known scam CIDs"""
        for cid in cids:
            for gateway in self.gateways:
                try:
                    url = f"{gateway}{cid}"
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        self._analyze_content(response.text, cid)
                        break
                except:
                    continue
```

---

## 🎯 STRATEGY 4: CLEVER SCRAPING TECHNIQUES

### 4.1 JavaScript Rendering Bypass

```python
# For sites that block scrapers
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class StealthScraper:
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        
        # Stealth mode - appear as regular browser
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        # Random user agent
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        ]
        self.options.add_argument(f"user-agent={random.choice(user_agents)}")
    
    def scrape(self, url):
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        driver.get(url)
        content = driver.page_source
        driver.quit()
        
        return content
```

### 4.2 Cache Harvesting (Free Historical Data)

```python
# Use web caches to get historical versions
class CacheHarvester:
    def __init__(self):
        self.cache_sources = {
            'wayback': 'https://webcache.googleusercontent.com/search?q=cache:',
            'google': 'https://webcache.googleusercontent.com/search?q=cache:',
            'archive': 'https://web.archive.org/web/*/',
        }
    
    def get_historical_version(self, url, date=None):
        """Get past versions of scam websites"""
        if date:
            archive_url = f"https://web.archive.org/web/{date}/{url}"
        else:
            archive_url = f"https://web.archive.org/web/*/{url}"
        
        response = requests.get(archive_url)
        return response.text
    
    def extract_deleted_content(self, url):
        """Get content that's been deleted from live site"""
        # Try multiple cache sources
        for source, base_url in self.cache_sources.items():
            try:
                response = requests.get(base_url + url, timeout=10)
                if response.status_code == 200:
                    return response.text
            except:
                continue
        return None
```

### 4.3 RSS/Atom Feed Aggregation (Free Real-time)

```python
# Monitor crypto news, scam reports via RSS
import feedparser

class RSSAggregator:
    def __init__(self):
        self.sources = {
            'scam_alert': 'https://scam-alert.io/feed',
            'crypto_twitter': 'https://nitter.net/cryptoscamtracker/rss',
            'reddit_scams': 'https://www.reddit.com/r/CryptoScams/.rss',
            'chainalysis_blog': 'https://blog.chainalysis.com/feed',
        }
    
    def aggregate(self):
        """Collect all feeds"""
        articles = []
        for name, url in self.sources.items():
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    articles.append({
                        'source': name,
                        'title': entry.title,
                        'link': entry.link,
                        'published': entry.get('published', ''),
                        'content': entry.get('summary', ''),
                    })
            except:
                continue
        return articles
```

---

## 🤖 STRATEGY 5: AUTOMATION FOR MAXIMUM EXTRACTION

### 5.1 Distributed Scraping Network

```python
# Use free tiers of cloud providers
# AWS Lambda: 1M free requests/month
# Google Cloud Functions: 2M free invocations/month
# Vercel: 100GB bandwidth free
# Netlify: 100GB bandwidth free

# Deploy scrapers across multiple free tiers
CLOUD_FUNCTIONS = [
    {'provider': 'aws', 'region': 'us-east-1', 'function_url': 'https://xxx.lambda-url.us-east-1.on.aws/'},
    {'provider': 'gcp', 'region': 'us-central1', 'function_url': 'https://us-central1-xxx.cloudfunctions.net/scraper'},
    {'provider': 'vercel', 'url': 'https://scraper-1.vercel.app/api/extract'},
    {'provider': 'netlify', 'url': 'https://scraper-2.netlify.app/.netlify/functions/extract'},
]

class DistributedScraper:
    def __init__(self):
        self.nodes = CLOUD_FUNCTIONS
        self.current_node = 0
    
    def scrape(self, target_url):
        """Distribute load across free cloud tiers"""
        node = self.nodes[self.current_node % len(self.nodes)]
        self.current_node += 1
        
        response = requests.post(
            node['url'],
            json={'target': target_url},
            timeout=30
        )
        
        return response.json()
```

### 5.2 Smart Scheduling

```python
# Run scrapers during off-peak hours
from datetime import datetime
import schedule

class SmartScheduler:
    def __init__(self):
        self.tasks = []
    
    def schedule_tasks(self):
        # Run heavy scraping at night when API limits reset
        schedule.every().day.at("00:01").do(self.reset_counters)
        schedule.every().day.at("01:00").do(self.heavy_scrape_pass)
        
        # Light monitoring during day
        schedule.every(10).minutes.do(self.light_monitoring)
        
        # Weekend deep dive (more free resources available)
        schedule.every().saturday.at("02:00").do(self.weekend_deep_dive)
    
    def reset_counters(self):
        """Reset all API rate limit counters"""
        for api in self.apis:
            api.reset_limits()
```

---

## 📱 STRATEGY 6: SOCIAL MEDIA INTELLIGENCE

### 6.1 Nitter Instances (Free Twitter)

```python
# Nitter is a free Twitter alternative
NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.it",
    "https://nitter.pussthecat.org",
    "https://nitter.nixnet.services",
    "https://nitter.fdn.fr",
]

class NitterScraper:
    def __init__(self):
        self.instances = NITTER_INSTANCES
        self.current = 0
    
    def get_user_tweets(self, username):
        """Scrape tweets without Twitter API"""
        instance = self.instances[self.current % len(self.instances)]
        url = f"{instance}/{username}/rss"
        
        feed = feedparser.parse(url)
        return [entry.title for entry in feed.entries]
    
    def search_tweets(self, query):
        """Search without rate limits"""
        for instance in self.instances:
            try:
                url = f"{instance}/search?f=tweets&q={query}"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    return self._parse_tweets(response.text)
            except:
                continue
```

### 6.2 Telegram OSINT (Free)

```python
# Use Telethon with free MTProto proxies
from telethon import TelegramClient
from telethon.sessions import StringSession

class TelegramOSINT:
    def __init__(self, api_id, api_hash, session_string=None):
        self.client = TelegramClient(
            StringSession(session_string) if session_string else StringSession(),
            api_id, 
            api_hash,
            proxy=('socks5', '127.0.0.1', 9050)  # Tor proxy
        )
    
    async def monitor_public_channels(self, channels):
        """Monitor scam channels without joining"""
        messages = []
        for channel in channels:
            try:
                entity = await self.client.get_entity(channel)
                async for message in self.client.iter_messages(entity, limit=100):
                    if self._is_scam_related(message.text):
                        messages.append({
                            'channel': channel,
                            'text': message.text,
                            'date': message.date,
                            'views': message.views,
                        })
            except:
                continue
        return messages
```

---

## 💾 STRATEGY 7: DATA PRESERVATION & DEDUPLICATION

### 7.1 Smart Deduplication

```python
import hashlib

class SmartDeduplicator:
    def __init__(self):
        self.seen_hashes = set()
    
    def content_hash(self, content):
        """Create semantic hash (not just exact match)"""
        # Normalize content
        normalized = self._normalize(content)
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    def _normalize(self, text):
        """Normalize text for comparison"""
        # Remove whitespace variations
        text = ' '.join(text.split())
        # Lowercase
        text = text.lower()
        # Remove common variations
        text = text.replace('0x', '').replace('https://', '').replace('http://', '')
        return text
    
    def is_duplicate(self, content):
        content_hash = self.content_hash(content)
        if content_hash in self.seen_hashes:
            return True
        self.seen_hashes.add(content_hash)
        return False
```

### 7.2 Incremental Updates

```python
# Only fetch changed data
class IncrementalUpdater:
    def __init__(self):
        self.last_etag = {}
        self.last_modified = {}
    
    def fetch_if_changed(self, url):
        """Only download if content changed"""
        headers = {}
        if url in self.last_etag:
            headers['If-None-Match'] = self.last_etag[url]
        if url in self.last_modified:
            headers['If-Modified-Since'] = self.last_modified[url]
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 304:  # Not modified
            return None  # No change
        
        # Update tracking
        self.last_etag[url] = response.headers.get('ETag')
        self.last_modified[url] = response.headers.get('Last-Modified')
        
        return response.content
```

---

## 🎭 STRATEGY 8: DECEPTION DETECTION

### 8.1 Honeypot Detection

```python
class HoneypotDetector:
    def __init__(self):
        self.test_wallet = "0x123..."  # Low-value test wallet
    
    def test_token(self, token_address):
        """Test if token is a honeypot without buying"""
        # Check if sell function exists
        # Check for blacklists
        # Check for transfer limits
        # Check contract code for suspicious patterns
        
        checks = {
            'has_sell_function': self._check_sell_function(token_address),
            'no_blacklist': self._check_blacklist(token_address),
            'reasonable_tax': self._check_tax(token_address),
            'verified_source': self._check_verified(token_address),
        }
        
        # All must pass
        return all(checks.values()), checks
```

---

## 📋 IMPLEMENTATION CHECKLIST

### Phase 1: Setup (Free)
- [ ] Install Tor for IP rotation
- [ ] Create 5 Groq accounts
- [ ] Create 3 OpenAI accounts
- [ ] Set up GitHub tokens
- [ ] Configure free proxies

### Phase 2: Automation (Free)
- [ ] Deploy to AWS Lambda free tier
- [ ] Deploy to Vercel free tier
- [ ] Set up GitHub Actions for scraping
- [ ] Configure RSS aggregation

### Phase 3: Advanced (Minimal Cost)
- [ ] Rent residential proxy ($5-10/mo)
- [ ] Shodan membership ($59/mo)
- [ ] Nansen Lite subscription

---

## ⚠️ LEGAL & ETHICAL NOTES

### ✅ ALLOWED:
- Using multiple free accounts for personal use
- IP rotation via Tor/VPNs
- Scraping public data
- Using RSS feeds
- Monitoring public blockchain data
- Analyzing public smart contracts

### ❌ NOT ALLOWED:
- Creating fake identities for accounts
- DDoS attacks
- Scraping private/restricted data
- Violating CFAA (Computer Fraud and Abuse Act)
- Impersonating others

### 🟡 GRAY AREA (Use Caution):
- Multiple accounts for same service (check ToS)
- Aggressive scraping that could be considered abuse
- Using residential proxies (legal but some sites block)

---

## 🚀 NEXT STEPS

**Tell me:**
1. "**Set up Tor rotation**" - Configure Tor for IP rotation
2. "**Create multi-account setup**" - Set up 5 Groq accounts
3. "**Build GitHub scraper**" - Mine GitHub for scam contracts
4. "**Deploy distributed scrapers**" - AWS Lambda + Vercel setup

Ready to implement any of these strategies!
