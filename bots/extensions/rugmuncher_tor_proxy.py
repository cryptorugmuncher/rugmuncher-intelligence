#!/usr/bin/env python3
"""
🧅 RugMuncher Tor Proxy Handler
Routes external API calls through Tor SOCKS5 for anonymity

Usage:
    External APIs (Silicon Flow, etc.) → Tor SOCKS5 → Internet
    Local Ollama → Direct (no proxy)
"""

import os
import aiohttp
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Tor SOCKS5 configuration
TOR_PROXY_HOST = os.getenv('TOR_PROXY_HOST', '127.0.0.1')
TOR_PROXY_PORT = int(os.getenv('TOR_PROXY_PORT', '9050'))
TOR_ENABLED = os.getenv('TOR_ENABLED', 'true').lower() == 'true'


class TorProxyManager:
    """
    🧅 Manages Tor SOCKS5 proxy connections
    
    For external API calls only:
    - Silicon Flow (Chinese provider)
    - Groq
    - Other cloud APIs
    
    Not used for:
    - Local Ollama (127.0.0.1:11434)
    - HashiCorp Vault (local)
    """
    
    def __init__(self):
        self.host = TOR_PROXY_HOST
        self.port = TOR_PROXY_PORT
        self.enabled = TOR_ENABLED
        self._connector = None
        
    def get_connector(self) -> Optional[aiohttp.BaseConnector]:
        """Get SOCKS5 connector for Tor"""
        if not self.enabled:
            return None
            
        try:
            import aiohttp_socks
            proxy_url = f"socks5://{self.host}:{self.port}"
            connector = aiohttp_socks.ProxyConnector.from_url(proxy_url)
            logger.debug(f"Tor proxy configured: {proxy_url}")
            return connector
        except ImportError:
            logger.warning("aiohttp-socks not installed, Tor proxy disabled")
            return None
        except Exception as e:
            logger.error(f"Tor proxy setup failed: {e}")
            return None
    
    async def test_connection(self) -> bool:
        """Test if Tor is working by checking external IP"""
        if not self.enabled:
            return False
            
        connector = self.get_connector()
        if not connector:
            return False
            
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                # Check IP through Tor
                async with session.get(
                    'https://check.torproject.org/api/ip',
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        is_tor = data.get('IsTor', False)
                        ip = data.get('IP', 'unknown')
                        logger.info(f"Tor connection test: IP={ip}, IsTor={is_tor}")
                        return is_tor
        except Exception as e:
            logger.error(f"Tor connection test failed: {e}")
        return False
    
    def get_session(self, timeout: int = 60) -> aiohttp.ClientSession:
        """
        Get aiohttp session with Tor proxy if enabled
        
        Args:
            timeout: Request timeout (longer for Tor - default 60s)
        """
        connector = self.get_connector()
        
        # Tor is slower, use longer timeout
        actual_timeout = timeout if not connector else timeout + 30
        
        return aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=actual_timeout)
        )


# Global instance
tor_proxy = TorProxyManager()


async def test_tor():
    """Test Tor connection"""
    print("🧅 Testing Tor Proxy Connection")
    print(f"  Host: {TOR_PROXY_HOST}:{TOR_PROXY_PORT}")
    print(f"  Enabled: {TOR_ENABLED}")
    
    result = await tor_proxy.test_connection()
    
    if result:
        print("  ✅ Tor is working! Traffic routed through Tor network.")
    else:
        print("  ⚠️ Tor connection failed. Check if Tor service is running:")
        print("     sudo systemctl status tor")
        print("     or install: sudo apt install tor")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_tor())
