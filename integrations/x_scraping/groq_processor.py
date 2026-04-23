"""
Groq Processor for X Data
Extract structured insights from scraped content
"""

import os
import json
import logging
from typing import Dict, Optional
import requests

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

class XDataProcessor:
    """Process scraped X data using Groq LLMs"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or GROQ_API_KEY
        self.model = "llama-3.1-70b-versatile"  # Fast, cheap, good quality
        
        if not self.api_key:
            logger.warning("No Groq API key provided!")
    
    def _call_groq(self, prompt: str, max_tokens: int = 2000) -> Optional[str]:
        """Call Groq API"""
        if not self.api_key:
            return None
        
        url = f"{GROQ_BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You extract structured data from social media profiles. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.1,  # Low for consistent extraction
            "response_format": {"type": "json_object"}
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            else:
                logger.error(f"Groq error {response.status_code}: {response.text}")
                
        except Exception as e:
            logger.error(f"Groq request failed: {e}")
        
        return None
    
    async def extract_profile_data(self, scraped_data: Dict) -> Dict:
        """
        Extract structured profile data from scraped content
        
        Args:
            scraped_data: Raw scraped data from Firecrawl or Nitter
            
        Returns:
            Structured profile dict
        """
        content = scraped_data.get('content', '') or scraped_data.get('raw_html', '')
        handle = scraped_data.get('handle', '')
        
        prompt = f"""
        Extract structured information from this X/Twitter profile content.
        
        Handle: @{handle}
        
        Content:
        {content[:4000]}  # Truncate to fit context
        
        Extract and return JSON:
        {{
            "display_name": "User's display name",
            "bio": "Profile bio/description",
            "location": "Location if mentioned",
            "website": "Website URL if present",
            "followers_count": "Number of followers (parse from text)",
            "following_count": "Number following",
            "tweets_count": "Total tweets",
            "account_created": "Join date if present",
            "is_verified": true/false,
            "recent_tweets": [
                {{
                    "text": "Tweet content",
                    "date": "Date posted",
                    "likes": "Like count if available",
                    "retweets": "RT count if available"
                }}
            ],
            "crypto_mentions": ["List any crypto tokens mentioned"],
            "sentiment_indicators": ["Bullish/bearish/neutral keywords"],
            "red_flags": ["Any suspicious patterns"],
            "influence_score": 1-100 (based on followers/engagement)
        }}
        
        Return valid JSON only. If data not present, use null or empty array.
        """
        
        result = self._call_groq(prompt)
        
        if result:
            try:
                parsed = json.loads(result)
                parsed['source'] = scraped_data.get('source', 'unknown')
                parsed['handle'] = handle
                parsed['scraped_at'] = scraped_data.get('scraped_at')
                return parsed
            except json.JSONDecodeError:
                logger.error("Groq returned invalid JSON")
        
        # Return raw if processing fails
        return scraped_data
    
    async def analyze_sentiment(self, tweets: list) -> Dict:
        """
        Analyze sentiment of tweets
        
        Args:
            tweets: List of tweet dicts with 'text' key
            
        Returns:
            Sentiment analysis
        """
        tweets_text = "\n".join([f"- {t.get('text', '')}" for t in tweets[:10]])
        
        prompt = f"""
        Analyze the sentiment of these tweets. Return JSON:
        
        Tweets:
        {tweets_text}
        
        Return:
        {{
            "overall_sentiment": "bullish/bearish/neutral",
            "confidence": 0-100,
            "key_topics": ["main topics discussed"],
            "mentioned_tokens": ["crypto tokens mentioned"],
            "risk_indicators": ["any red flags or concerns"],
            "engagement_quality": "high/medium/low based on call-to-actions"
        }}
        """
        
        result = self._call_groq(prompt, max_tokens=1000)
        
        if result:
            try:
                return json.loads(result)
            except:
                pass
        
        return {"error": "Sentiment analysis failed"}
    
    async def detect_scam_signals(self, profile_data: Dict) -> Dict:
        """
        Detect potential scam indicators
        
        Args:
            profile_data: Structured profile data
            
        Returns:
            Scam analysis
        """
        prompt = f"""
        Analyze this X profile for scam indicators. Return JSON:
        
        Profile: @{profile_data.get('handle', '')}
        Bio: {profile_data.get('bio', '')}
        Recent tweets: {json.dumps(profile_data.get('recent_tweets', []))}
        
        Check for:
        - Unrealistic promises ("guaranteed 100x")
        - Urgency tactics ("limited time", "act now")
        - Anonymous teams with no history
        - Copy-paste shilling
        - Fake engagement
        - Suspicious link patterns
        
        Return:
        {{
            "scam_likelihood": "low/medium/high",
            "confidence": 0-100,
            "red_flags": ["specific concerns"],
            "recommendation": "safe/caution/avoid",
            "reasoning": "brief explanation"
        }}
        """
        
        result = self._call_groq(prompt, max_tokens=1500)
        
        if result:
            try:
                return json.loads(result)
            except:
                pass
        
        return {"error": "Scam detection failed"}


# Singleton
_processor = None

def get_processor() -> XDataProcessor:
    """Get singleton processor"""
    global _processor
    if _processor is None:
        _processor = XDataProcessor()
    return _processor
