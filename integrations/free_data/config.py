"""
Configuration for free data APIs
"""

import os

# API Keys (all free tiers)
BRAVE_API_KEY = os.getenv('BRAVE_API_KEY', '')
BING_API_KEY = os.getenv('BING_API_KEY', '')
SERPER_API_KEY = os.getenv('SERPER_API_KEY', '')
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY', '')
EXA_API_KEY = os.getenv('EXA_API_KEY', '')
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY', '')

# Free API Configuration
FREE_APIS = {
    'brave': {
        'enabled': bool(BRAVE_API_KEY),
        'monthly_limit': 2000,
        'priority': 1,
        'type': 'search'
    },
    'bing': {
        'enabled': bool(BING_API_KEY),
        'monthly_limit': 1000,
        'priority': 2,
        'type': 'search'
    },
    'serper': {
        'enabled': bool(SERPER_API_KEY),
        'monthly_limit': 2500,
        'priority': 3,
        'type': 'search'
    },
    'tavily': {
        'enabled': bool(TAVILY_API_KEY),
        'monthly_limit': 1000,
        'priority': 4,
        'type': 'search'
    },
    'exa': {
        'enabled': bool(EXA_API_KEY),
        'monthly_limit': 1000,
        'priority': 5,
        'type': 'search'
    },
    'duckduckgo': {
        'enabled': True,  # No API key needed
        'monthly_limit': float('inf'),
        'priority': 10,  # Fallback
        'type': 'search'
    },
    'searx': {
        'enabled': True,  # Public instances
        'monthly_limit': float('inf'),
        'priority': 11,
        'type': 'search'
    }
}

# Searx instances (public, free)
SEARX_INSTANCES = [
    "https://searx.be",
    "https://search.sapti.me",
    "https://searx.fmac.xyz",
    "https://search.bus-hit.me",
    "https://searx.tiekoetter.com"
]
