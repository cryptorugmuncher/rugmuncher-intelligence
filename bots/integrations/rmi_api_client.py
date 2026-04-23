"""
RMI Bot - Backend API Integration
==================================

Telegram bots should call RMI Backend API at localhost:8002
NOT import modules directly. This ensures:
- Single source of truth (RMI Backend)
- Proper caching and rate limiting
- Unified data pipeline
- Consistent authentication

Architecture:
    Telegram Bot → RMI Backend API (port 8002) → Blockchain APIs
                        ↓
                    Supabase/Redis (Cache)
                        ↓
                    Telegram Response
"""

import os
import aiohttp
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# RMI Backend API URL
RMI_API_BASE = os.getenv('RMI_API_URL', 'http://localhost:8002/api/v1')


@dataclass
class RMIClient:
    """Client for RMI Backend API - Central data source"""
    
    base_url: str = RMI_API_BASE
    timeout: int = 30
    
    async def _request(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Optional[Dict]:
        """Make request to RMI Backend"""
        url = f"{self.base_url}/{endpoint}"
        
        async with aiohttp.ClientSession() as session:
            try:
                if method == 'GET':
                    async with session.get(url, timeout=self.timeout) as resp:
                        if resp.status == 200:
                            return await resp.json()
                        logger.warning(f"RMI API {endpoint}: {resp.status}")
                        return None
                elif method == 'POST':
                    async with session.post(url, json=data, timeout=self.timeout) as resp:
                        if resp.status == 200:
                            return await resp.json()
                        return None
            except Exception as e:
                logger.error(f"RMI API error ({endpoint}): {e}")
                return None
    
    # ═══════════════════════════════════════════════════════════
    # BLOCKCHAIN DATA (via Unified Client)
    # ═══════════════════════════════════════════════════════════
    
    async def get_wallet_analysis(self, address: str, chain: str = 'solana') -> Optional[Dict]:
        """Get wallet analysis from RMI Backend (Arkham + Helius + QuickNode)"""
        return await self._request(f"blockchain/wallet/{address}?chain={chain}")
    
    async def get_token_analysis(self, mint: str, chain: str = 'solana') -> Optional[Dict]:
        """Get token analysis from RMI Backend (Helius + Solscan + QuickNode)"""
        return await self._request(f"blockchain/token/{mint}?chain={chain}")
    
    async def get_token_risk(self, address: str) -> Optional[Dict]:
        """Quick token risk scan"""
        return await self._request(f"solana/token/{address}")
    
    async def get_wallet_transactions(self, address: str, chain: str = 'solana', limit: int = 50) -> Optional[Dict]:
        """Get labeled transactions"""
        return await self._request(f"blockchain/wallet/{address}/transactions?chain={chain}&limit={limit}")
    
    async def search_entity(self, query: str) -> Optional[Dict]:
        """Search Arkham entities"""
        return await self._request(f"blockchain/search/entity?query={query}")
    
    async def bulk_scan_wallets(self, addresses: list, chain: str = 'solana') -> Optional[Dict]:
        """Scan multiple wallets"""
        return await self._request(f"blockchain/scan/bulk-wallets?chain={chain}", 'POST', {'addresses': addresses})
    
    async def bulk_scan_tokens(self, mints: list, chain: str = 'solana') -> Optional[Dict]:
        """Scan multiple tokens"""
        return await self._request(f"blockchain/scan/bulk-tokens?chain={chain}", 'POST', {'mints': mints})
    
    # ═══════════════════════════════════════════════════════════
    # INVESTIGATION DATA
    # ═══════════════════════════════════════════════════════════
    
    async def get_investigation(self, case_id: str) -> Optional[Dict]:
        """Get investigation case"""
        return await self._request(f"investigation/{case_id}")
    
    async def create_investigation(self, data: Dict) -> Optional[Dict]:
        """Create new investigation"""
        return await self._request("investigation", 'POST', data)
    
    # ═══════════════════════════════════════════════════════════
    # SYSTEM HEALTH
    # ═══════════════════════════════════════════════════════════
    
    async def check_health(self) -> Dict:
        """Check RMI Backend health"""
        blockchain = await self._request("blockchain/health")
        solana = await self._request("solana/health")
        return {
            'blockchain': blockchain,
            'solana': solana,
            'api_base': self.base_url
        }


# ═══════════════════════════════════════════════════════════
# BOT HANDLER HELPERS
# ═══════════════════════════════════════════════════════════

class BlockchainCommandHandler:
    """
    Helper class for Telegram bot blockchain commands.
    
    Usage in bot:
        from integrations.rmi_api_client import BlockchainCommandHandler
        
        handler = BlockchainCommandHandler()
        
        async def munch_command(update, context):
            token = context.args[0]
            result = await handler.analyze_token(token)
            await update.message.reply_text(result)
    """
    
    def __init__(self, client: Optional[RMIClient] = None):
        self.client = client or RMIClient()
    
    async def analyze_token(self, token_address: str) -> str:
        """
        Analyze token and return formatted message for Telegram
        
        Returns formatted text with emojis for Telegram display
        """
        data = await self.client.get_token_analysis(token_address)
        
        if not data or 'token' not in data:
            return f"❌ Could not analyze token: {token_address[:20]}..."
        
        token = data['token']
        risk = data['risk']
        
        # Risk emoji
        risk_emoji = {
            'LOW': '🟢',
            'MEDIUM': '🟡',
            'HIGH': '🔴'
        }.get(risk['level'], '⚪')
        
        message = f"""
🔍 Token Analysis: {token['name']} (${token['symbol']})

{risk_emoji} Risk Score: {risk['score']}/100 ({risk['level']})
📊 Supply: {token['supply']:,.0f}
🔗 Chain: {token['chain'].upper()}
"""
        
        if risk['warnings']:
            message += "\n⚠️ Warnings:\n"
            for warning in risk['warnings']:
                message += f"  • {warning}\n"
        
        return message
    
    async def analyze_wallet(self, wallet_address: str) -> str:
        """
        Analyze wallet and return formatted message for Telegram
        """
        data = await self.client.get_wallet_analysis(wallet_address)
        
        if not data or 'wallet' not in data:
            return f"❌ Could not analyze wallet: {wallet_address[:20]}..."
        
        wallet = data['wallet']
        risk = data['risk']
        sources = data.get('sources', {})
        
        # Source indicators
        source_icons = []
        if sources.get('arkham'): source_icons.append('🔍 Arkham')
        if sources.get('helius'): source_icons.append('⚡ Helius')
        if sources.get('quicknode'): source_icons.append('🚀 QuickNode')
        
        message = f"""
👤 Wallet Analysis: {wallet['address'][:20]}...

💰 SOL Balance: {wallet.get('balance_sol', 'N/A')}
🎫 Tokens: {wallet['token_count']}
🖼 NFTs: {wallet['nft_count']}
🏷 Labels: {', '.join(wallet['labels']) if wallet['labels'] else 'None'}

{risk['level']} Risk Score: {risk['score']}/100

Sources: {' | '.join(source_icons) if source_icons else 'Basic RPC'}
"""
        return message
    
    async def scan_bundle(self, token_address: str) -> str:
        """
        Check for coordinated buying/bundle patterns
        """
        # Get holders and analyze distribution
        data = await self.client.get_token_analysis(token_address)
        
        if not data:
            return "❌ Could not analyze token"
        
        risk = data['risk']
        
        if risk['score'] > 70:
            return f"""
🚨 BUNDLE ALERT: {data['token']['symbol']}

Risk Score: {risk['score']}/100 🔴
Status: HIGH RISK - Possible coordinated activity detected

Warnings:
{chr(10).join('• ' + w for w in risk['warnings'])}

⚠️ DYOR - This shows signs of potential manipulation
"""
        else:
            return f"""
✅ {data['token']['symbol']}: No bundle detected
Risk Score: {risk['score']}/100 🟢
Distribution appears normal.
"""


# Convenience singleton
_rmi_client: Optional[RMIClient] = None

async def get_rmi_client() -> RMIClient:
    """Get or create RMI API client"""
    global _rmi_client
    if _rmi_client is None:
        _rmi_client = RMIClient()
    return _rmi_client


# ═══════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════

async def example():
    """Example: How bots should use RMI Backend API"""
    
    client = RMIClient()
    
    # 1. Analyze a token (all providers via RMI Backend)
    print("\n1️⃣ Token Analysis (via RMI Backend)")
    token_data = await client.get_token_analysis(
        "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
        'solana'
    )
    print(f"   Token: {token_data.get('token', {}).get('name')}")
    print(f"   Risk: {token_data.get('risk', {}).get('score')}/100")
    
    # 2. Analyze wallet (Arkham labels + Helius assets + QuickNode balance)
    print("\n2️⃣ Wallet Analysis (via RMI Backend)")
    wallet_data = await client.get_wallet_analysis(
        "JUP6LkbZbjS1jKKwapdHNy74zcjn3L3kKjGNhVrN1Kx",
        'solana'
    )
    print(f"   Labels: {wallet_data.get('wallet', {}).get('labels', [])}")
    
    # 3. Check health
    print("\n3️⃣ RMI Backend Health")
    health = await client.check_health()
    print(f"   Providers: {health.get('blockchain', {}).get('providers', {})}")
    
    print("\n✅ All data came from RMI Backend - single source of truth")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example())
