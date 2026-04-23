"""
X Scraping Integration
4-Tier: Apify (paid) → Firecrawl (free) → Nitter (free) + Groq (AI)
"""

from .ultimate_hybrid import UltimateXScraper, get_ultimate_scraper
from .apify_scraper import ApifyXScraper, get_apify_scraper
from .groq_processor import XDataProcessor, get_processor
from .firecrawl_scraper import FirecrawlXScraper
from .nitter_scraper import NitterXScraper

# Backwards compatibility
HybridXScraper = UltimateXScraper
get_hybrid_scraper = get_ultimate_scraper

__all__ = [
    'UltimateXScraper',
    'get_ultimate_scraper',
    'ApifyXScraper',
    'get_apify_scraper',
    'XDataProcessor',
    'get_processor',
    'FirecrawlXScraper',
    'NitterXScraper',
    # Backwards compatibility
    'HybridXScraper',
    'get_hybrid_scraper'
]
