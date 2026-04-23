"""
Example: How to use X scraping in RMI
"""

import asyncio
from x_scraping import get_hybrid_scraper, get_processor

async def main():
    # Get scraper
    scraper = get_hybrid_scraper()
    processor = get_processor()
    
    # Scrape a profile
    handle = "CryptoRugMunch"
    
    print(f"🔍 Scraping @{handle}...")
    
    # Method 1: Raw scrape (auto-failover)
    raw_data = await scraper.scrape_profile(handle)
    
    if raw_data:
        print(f"✅ Scraped via {raw_data.get('source', 'unknown')}")
        print(f"Content preview: {raw_data.get('content', '')[:200]}...")
    else:
        print("❌ Failed to scrape")
        return
    
    # Method 2: Scrape + process with Groq
    print("\n🤖 Processing with Groq...")
    processed = await scraper.scrape_with_processor(
        handle, 
        groq_processor=processor.extract_profile_data
    )
    
    if processed:
        print(f"✅ Processed profile:")
        print(f"  Name: {processed.get('display_name')}")
        print(f"  Bio: {processed.get('bio', '')[:100]}...")
        print(f"  Followers: {processed.get('followers_count')}")
        print(f"  Crypto mentions: {processed.get('crypto_mentions', [])}")
        
        # Analyze for scams
        scam_check = await processor.detect_scam_signals(processed)
        print(f"\n🚨 Scam check: {scam_check.get('scam_likelihood', 'unknown')}")
    
    # Check health
    print("\n📊 Scraper health:")
    health = scraper.get_health_status()
    print(f"  Firecrawl: {health['firecrawl']['status']}")
    print(f"  Nitter instances: {health['nitter']['instances_available']}/{health['nitter']['instances_total']}")

if __name__ == "__main__":
    asyncio.run(main())
