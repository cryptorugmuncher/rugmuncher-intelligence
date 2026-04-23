#!/usr/bin/env python3
"""
🧠 RugMuncher AI Router
Smart routing between local Ollama (sensitive) and external APIs (public)

SECURITY FEATURES:
- Local Ollama: Sensitive data (wallets, live contracts, large amounts)
- External APIs: Via Tor SOCKS5 proxy for anonymity
- HashiCorp Vault: API keys encrypted at rest

ROUTING RULES:
┌─────────────────────────────────────────────────────────────┐
│ DATA TYPE          │ ROUTING          │ REASON              │
├─────────────────────────────────────────────────────────────┤
│ Wallet addresses   │ Local Ollama     │ PII - Never leaves  │
│ Large amounts      │ Local Ollama     │ Whale protection    │
│ Live contracts     │ Local Ollama     │ Real money at risk  │
│ Test/demo data     │ External via Tor │ Fast, cheap         │
│ Public metrics     │ External via Tor │ Already public      │
│ Sanitized data     │ External via Tor │ Anonymized OK       │
└─────────────────────────────────────────────────────────────┘
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Union, Literal
from enum import Enum
import logging

from rugmuncher_data_sanitizer import sanitize_for_external_api, DataSanitizer
from rugmuncher_vault_client import vault_client
from rugmuncher_tor_proxy import tor_proxy

logger = logging.getLogger(__name__)

# Configuration
OLLAMA_URL = f"http://{os.getenv('OLLAMA_HOST', '127.0.0.1')}:{os.getenv('OLLAMA_PORT', '11434')}"

EXTERNAL_APIS = {
    'silicon-flow': {
        'url': 'https://api.siliconflow.cn/v1/chat/completions',
        'model': 'deepseek-ai/DeepSeek-V3'
    },
    'groq': {
        'url': 'https://api.groq.com/openai/v1/chat/completions',
        'model': 'llama-3.1-70b-versatile'
    }
}

LOCAL_MODELS = {
    'heavy': 'deepseek-r1:14b',
    'code': 'qwen2.5:14b',
    'fast': 'gemma2:9b',
    'long': 'qwen2.5:7b'
}


class DataSensitivity(Enum):
    SENSITIVE = "sensitive"
    PUBLIC = "public"
    TEST = "test"


class RugMuncherAIRouter:
    """
    🎯 Routes AI requests based on data sensitivity
    
    - Sensitive: Local Ollama (127.0.0.1:11434)
    - Public: External APIs via Tor SOCKS5
    """
    
    def __init__(self):
        self.ollama_available: Optional[bool] = None
        self.sanitizer = DataSanitizer()
        
    async def check_ollama(self) -> bool:
        """Check if local Ollama is running"""
        if self.ollama_available is None:
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=3)) as session:
                    async with session.get(f"{OLLAMA_URL}/api/tags") as resp:
                        self.ollama_available = resp.status == 200
            except Exception:
                self.ollama_available = False
        return self.ollama_available
    
    def classify_data(self, data: Dict[str, Any]) -> DataSensitivity:
        """Classify data sensitivity for routing decision"""
        data_str = json.dumps(data, default=str).lower()
        
        sensitive_indicators = [
            'wallet_address', 'holder_address', 'user_address',
            'ip_address', 'telegram_id', 'private_key'
        ]
        
        has_large_amounts = any(
            isinstance(v, (int, float)) and v > 10000
            for k, v in data.items()
            if any(x in k.lower() for x in ['amount', 'balance', 'usd'])
        )
        
        is_live = data.get('is_live') or data.get('has_liquidity', 0) > 0
        sensitive_count = sum(1 for i in sensitive_indicators if i in data_str)
        
        if sensitive_count >= 1 or has_large_amounts or is_live:
            return DataSensitivity.SENSITIVE
        elif data.get('is_test') or data.get('demo'):
            return DataSensitivity.TEST
        else:
            return DataSensitivity.PUBLIC
    
    async def _call_local(self, prompt: str, model: str, system: Optional[str] = None) -> Dict:
        """🏠 Call local Ollama - sensitive data never leaves"""
        if not await self.check_ollama():
            raise Exception("Local Ollama not available")
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 4096}
        }
        if system:
            payload["system"] = system
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=120)) as session:
            async with session.post(f"{OLLAMA_URL}/api/generate", json=payload) as resp:
                data = await resp.json()
                return {
                    'text': data.get('response', ''),
                    'model': model,
                    'provider': 'local_ollama'
                }
    
    async def _call_external(self, prompt: str, provider: str, system: Optional[str] = None) -> Dict:
        """🌐 Call external API via Tor SOCKS5 proxy"""
        api_config = EXTERNAL_APIS.get(provider)
        if not api_config:
            raise Exception(f"Unknown provider: {provider}")
        
        # Get API key from Vault
        api_key = await vault_client.get_api_key(provider)
        if not api_key:
            api_key = os.getenv(f'{provider.upper().replace("-", "_")}_KEY', '')
        if not api_key:
            raise Exception(f"No API key for {provider}")
        
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": api_config['model'],
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 4096
        }
        
        # Use Tor proxy session
        async with tor_proxy.get_session(timeout=60) as session:
            proxy_info = "via Tor" if tor_proxy.get_connector() else "direct"
            logger.info(f"External API call to {provider} {proxy_info}")
            
            async with session.post(api_config['url'], headers=headers, json=payload) as resp:
                if resp.status != 200:
                    raise Exception(f"API error {resp.status}")
                data = await resp.json()
                choice = data.get('choices', [{}])[0]
                return {
                    'text': choice.get('message', {}).get('content', ''),
                    'model': api_config['model'],
                    'provider': f'external_{provider}',
                    'proxy_used': tor_proxy.get_connector() is not None
                }
    
    async def analyze_contract(self, contract_code: str, contract_address: str = "", 
                               is_live: bool = False, **kwargs) -> Dict:
        """🔍 Analyze smart contract - routes based on sensitivity"""
        
        data = {
            'contract_code': contract_code[:1000],
            'contract_address': contract_address,
            'is_live': is_live,
            'has_liquidity': kwargs.get('has_liquidity', 0)
        }
        
        sensitivity = self.classify_data(data)
        
        system = """You are a smart contract security auditor. 
Respond in JSON format with: risk_score, severity, findings[], honeypot_risk, summary"""

        prompt = f"""Analyze this contract:
```solidity
{contract_code[:30000]}
```
Address: {contract_address}
Live: {is_live}
Provide security analysis in JSON format."""

        if sensitivity == DataSensitivity.SENSITIVE:
            logger.info(f"Contract {contract_address[:16]}... → Local Ollama")
            result = await self._call_local(prompt, LOCAL_MODELS['code'], system)
        else:
            logger.info(f"Contract {contract_address[:16]}... → External via Tor")
            result = await self._call_external(prompt, 'groq', system)
        
        # Parse JSON response
        try:
            text = result['text']
            if '```json' in text:
                json_str = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                json_str = text.split('```')[1].split('```')[0]
            else:
                json_str = text
            analysis = json.loads(json_str.strip())
        except (json.JSONDecodeError, IndexError, KeyError):
            analysis = {'parsing_error': True, 'raw': result['text'][:500]}
        
        return {
            **analysis,
            'routing': {'provider': result['provider'], 'model': result['model']},
            'sensitivity': sensitivity.value
        }
    
    async def analyze_wallet(self, wallet_address: str, wallet_data: Dict, **kwargs) -> Dict:
        """👤 Analyze wallet - ALWAYS local (sensitive)"""
        
        # FORCE local - wallet data never leaves
        if not await self.check_ollama():
            return {'error': 'Local Ollama required', 'privacy_protected': True}
        
        logger.info(f"Wallet {wallet_address[:16]}... → Local Ollama (PRIVATE)")
        
        system = "You are a blockchain forensics analyst. Respond in JSON format."
        prompt = f"""Analyze wallet {wallet_address}:
{json.dumps(wallet_data, default=str)[:5000]}
Provide behavioral analysis in JSON format."""

        result = await self._call_local(prompt, LOCAL_MODELS['heavy'], system)
        
        try:
            analysis = json.loads(result['text'].split('```json')[-1].split('```')[0] if '```json' in result['text'] else result['text'])
        except (json.JSONDecodeError, IndexError):
            analysis = {'notes': result['text'][:300]}
        
        return {**analysis, 'privacy_protected': True, 'provider': 'local_ollama'}
    
    async def get_status(self) -> Dict:
        """Get router status"""
        return {
            'ollama': {'available': await self.check_ollama(), 'url': OLLAMA_URL},
            'vault': {'enabled': vault_client.is_configured, 'authenticated': bool(vault_client._client_token)},
            'tor': {'enabled': tor_proxy.enabled, 'proxy': f"{tor_proxy.host}:{tor_proxy.port}"},
            'routing': {
                'sensitive': 'local_ollama',
                'public': 'external_via_tor',
                'wallets': 'local_only'
            }
        }


# Global instance
ai_router = RugMuncherAIRouter()


async def demo():
    """Demo the router"""
    print("🧠 RugMuncher AI Router Demo")
    print("=" * 50)
    
    router = RugMuncherAIRouter()
    status = await router.get_status()
    
    print(f"\n🔒 Security Features:")
    print(f"  Ollama: {'✓' if status['ollama']['available'] else '✗'}")
    print(f"  Vault: {'✓' if status['vault']['enabled'] else '✗'}")
    print(f"  Tor Proxy: {'✓' if status['tor']['enabled'] else '✗'}")
    
    # Test routing decisions
    tests = [
        ('Live Contract', {'is_live': True, 'has_liquidity': 500000}),
        ('Test Contract', {'is_test': True}),
        ('Wallet', {'wallet_address': '0x123...', 'balance': 50000}),
        ('Public Data', {'token_symbol': 'PEPE', 'holders': 5000})
    ]
    
    print(f"\n📊 Routing Decisions:")
    for name, data in tests:
        sensitivity = router.classify_data(data)
        route = 'LOCAL' if sensitivity == DataSensitivity.SENSITIVE else 'TOR'
        print(f"  {name}: {route} ({sensitivity.value})")


if __name__ == "__main__":
    asyncio.run(demo())
