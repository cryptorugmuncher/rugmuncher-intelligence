#!/usr/bin/env python3
"""
RMI Local AI Chat — Lightweight Instant Assistant
═══════════════════════════════════════════════════

Fast responses using Groq Llama 3.1 8B (30 req/min free tier).
Crypto security expert personality. Cached responses for speed.
"""

import os
import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger("rmi-chat")

GROQ_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# System prompt — crypto security expert personality
SYSTEM_PROMPT = """You are RMI-Alpha, a crypto intelligence assistant built by Rug Munch Intelligence.
You specialize in Solana token security, on-chain analysis, and threat detection.

Rules:
- Keep answers SHORT (1-3 sentences max)
- Be direct and actionable
- Use crypto terminology naturally
- Never give financial advice — only security analysis
- Reference your tools: Birdeye, GMGN, Helius, Solscan, SolanaFM, DexScreener, Moralis

Available commands you can suggest:
/security <token> — Full security scan
/whales <token> — Whale concentration analysis
/gmgnscan <token> — Deep token research
/trendingv2 — Trending tokens with safety scores
/smartmoney — Live smart money dashboard
/syndicate — CRM V1 syndicate tracker

Current mission: Protect traders from rug pulls and scams through forensic-grade analysis."""

# Response cache for common questions
_response_cache: Dict[str, Any] = {}
_cache_hits = 0
_cache_misses = 0


class RMIChatService:
    """Lightweight chat service with caching and rate limiting."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self._conversation_history: Dict[str, list] = {}  # Per-user context
        self._request_count = 0
        self._last_reset = datetime.utcnow()
        self._max_requests_per_min = 30  # Groq free tier
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=15),
                headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
            )
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within Groq rate limits."""
        now = datetime.utcnow()
        if (now - self._last_reset).total_seconds() > 60:
            self._request_count = 0
            self._last_reset = now
        return self._request_count < self._max_requests_per_min
    
    async def ask(self, message: str, user_id: str = "default") -> Dict[str, Any]:
        """Process a chat message and return a response."""
        global _cache_hits, _cache_misses
        
        if not GROQ_KEY:
            return self._fallback_response(message)
        
        # Check cache for exact match
        cache_key = message.lower().strip()
        if cache_key in _response_cache:
            _cache_hits += 1
            cached = _response_cache[cache_key]
            cached["cached"] = True
            return cached
        
        _cache_misses += 1
        
        # Rate limit check
        if not self._check_rate_limit():
            return {
                "response": "⏳ Rate limit reached. Try again in a moment.",
                "status": "rate_limited",
                "timestamp": datetime.utcnow().isoformat(),
            }
        
        try:
            # Get or create conversation history
            history = self._conversation_history.get(user_id, [])
            
            # Build messages
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            messages.extend(history[-6:])  # Last 3 exchanges for context
            messages.append({"role": "user", "content": message})
            
            # Call Groq
            s = await self._get_session()
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": messages,
                "max_tokens": 200,
                "temperature": 0.7,
            }
            
            async with s.post(GROQ_URL, json=payload) as resp:
                self._request_count += 1
                
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.warning(f"Groq error: {resp.status} - {error_text[:100]}")
                    return self._fallback_response(message)
                
                data = await resp.json()
                reply = data["choices"][0]["message"]["content"]
                
                # Update history
                history.append({"role": "user", "content": message})
                history.append({"role": "assistant", "content": reply})
                self._conversation_history[user_id] = history[-20:]  # Keep last 10 exchanges
                
                result = {
                    "response": reply,
                    "status": "ok",
                    "model": "llama-3.1-8b-instant",
                    "cached": False,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                
                # Cache simple responses
                if len(message) < 100 and len(reply) < 300:
                    _response_cache[cache_key] = result.copy()
                
                return result
                
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return self._fallback_response(message)
    
    def _fallback_response(self, message: str) -> Dict[str, Any]:
        """Fallback when AI is unavailable."""
        msg_lower = message.lower()
        
        # Keyword-based responses
        if any(w in msg_lower for w in ["security", "scan", "safe", "rug"]):
            return {"response": "Use /security <token_address> for a full security scan. I check honeypot, taxes, mint authority, and holder concentration.", "status": "fallback"}
        elif any(w in msg_lower for w in ["whale", "holder", "concentration"]):
            return {"response": "Use /whales <token_address> to see whale concentration. Top 10 holders over 50% = high risk.", "status": "fallback"}
        elif any(w in msg_lower for w in ["trending", "hot", "pump"]):
            return {"response": "Use /trendingv2 to see trending tokens with safety scores. /trenches shows new launches.", "status": "fallback"}
        elif any(w in msg_lower for w in ["smart money", "kol", "degen"]):
            return {"response": "Use /smartmoney to see what smart degens and KOLs are buying right now.", "status": "fallback"}
        elif any(w in msg_lower for w in ["crm", "syndicate", "sosana"]):
            return {"response": "Use /syndicate to track the CRM V1 syndicate. 93% supply under criminal control.", "status": "fallback"}
        else:
            return {"response": "I'm RMI-Alpha, your crypto security assistant. Ask me about token security, whale analysis, or type /help for commands.", "status": "fallback"}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get chat service statistics."""
        return {
            "cache_hits": _cache_hits,
            "cache_misses": _cache_misses,
            "cache_size": len(_response_cache),
            "conversations": len(self._conversation_history),
            "requests_this_minute": self._request_count,
            "groq_key_set": bool(GROQ_KEY),
        }


# ─── Singleton ───────────────────────────────────────────────────────────

_service: Optional[RMIChatService] = None

def get_chat_service() -> RMIChatService:
    global _service
    if _service is None:
        _service = RMIChatService()
    return _service
