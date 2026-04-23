"""
X Scraping Configuration
Hybrid: Firecrawl (primary) + Nitter (backup)
"""

import os

# API Keys
FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY', '')
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')

# Firecrawl settings
FIRECRAWL_BASE_URL = "https://api.firecrawl.dev/v1"
FIRECRAWL_RATE_LIMIT = 1  # requests per second (conservative)

# Nitter instances (rotating)
NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.it", 
    "https://nitter.cz",
    "https://nitter.privacydev.net",
    "https://nitter.projectsegfault.com",
    "https://nitter.nixnet.services",
    "https://nitter.datura.network",
    "https://nitter.perennialte.ch",
]

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Failover settings
FAILOVER_THRESHOLD = 2  # failures before switching to backup

# Apify (paid but you have $5 credit)
APIFY_TOKEN = os.getenv('APIFY_TOKEN', '')
APIFY_CONFIG = {
    'enabled': bool(APIFY_TOKEN),
    'credits': 5.00,  # $5 credit
    'cost_per_profile': 0.005,  # ~$0.005 per profile scrape
    'cost_per_search': 0.02,  # ~$0.02 per search
    'estimated_scrapes': 1000,  # ~1000 profiles with $5
    'priority': 0  # Highest priority - use first
}
