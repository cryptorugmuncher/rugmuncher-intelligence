#!/usr/bin/env python3
"""
🦙 RugMuncher Ollama Addon
Plug-in module for local LLM inference
Add this to your bot for zero-cost AI analysis!
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'localhost')
OLLAMA_PORT = int(os.getenv('OLLAMA_PORT', '11434'))
OLLAMA_ENABLED = os.getenv('OLLAMA_ENABLED', 'true').lower() == 'true'

# Model routing priorities
MODEL_ROUTING = {
    'contract_analysis': 'qwen2.5:7b',      # Long context for contracts
    'threat_detection': 'deepseek-r1:14b',   # Reasoning for threats
    'quick_summary': 'gemma2:9b',            # Fast responses
    'wallet_analysis': 'deepseek-r1:14b',    # Pattern recognition
    'code_review': 'qwen2.5:7b',             # Technical analysis
}


@dataclass
class OllamaResponse:
    """Structured response from Ollama"""
    text: str
    model: str
    duration_ms: int
    prompt_tokens: int = 0
    completion_tokens: int = 0


class OllamaAIProvider:
    """
    🦙 Local AI Provider using Ollama
    Drop-in replacement for cloud AI APIs
    """
    
    def __init__(self, host: str = None, port: int = None):
        self.host = host or OLLAMA_HOST
        self.port = port or OLLAMA_PORT
        self.base_url = f"http://{self.host}:{self.port}"
        self._available_models: List[str] = []
        self._model_loaded: Dict[str, bool] = {}
        
    @property
    def is_available(self) -> bool:
        """Check if Ollama is running and has models"""
        if not OLLAMA_ENABLED:
            return False
        try:
            # Quick health check
            import urllib.request
            urllib.request.urlopen(f"{self.base_url}/api/tags", timeout=2)
            return True
        except Exception:
            return False
    
    async def list_models(self) -> List[str]:
        """Get list of downloaded models"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(f"{self.base_url}/api/tags") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self._available_models = [m['name'] for m in data.get('models', [])]
                        return self._available_models
        except Exception as e:
            logger.warning(f"Failed to list Ollama models: {e}")
        return []
    
    def get_model_for_task(self, task: str) -> str:
        """Select best model for the task"""
        preferred = MODEL_ROUTING.get(task, 'gemma2:9b')
        
        # Check if preferred is available
        if self._available_models and preferred in self._available_models:
            return preferred
        
        # Fallback chain
        fallbacks = ['gemma2:9b', 'qwen2.5:7b', 'deepseek-r1:14b', 'llama3.2:3b']
        for model in fallbacks:
            if not self._available_models or model in self._available_models:
                return model
        
        return preferred  # Default even if not confirmed
    
    async def generate(
        self,
        prompt: str,
        task: str = 'general',
        system: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        json_mode: bool = False
    ) -> OllamaResponse:
        """Generate completion using Ollama"""
        
        model = self.get_model_for_task(task)
        
        # Add JSON instruction if needed
        if json_mode and 'json' not in prompt.lower():
            system = (system or "") + "\nRespond in valid JSON format only."
        
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "num_predict": max_tokens,
            "stream": False
        }
        
        if system:
            payload["system"] = system.strip()
        
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=120)
            ) as session:
                start_time = asyncio.get_event_loop().time()
                
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                ) as resp:
                    if resp.status != 200:
                        error = await resp.text()
                        raise Exception(f"Ollama error {resp.status}: {error}")
                    
                    data = await resp.json()
                    duration = int((asyncio.get_event_loop().time() - start_time) * 1000)
                    
                    return OllamaResponse(
                        text=data.get('response', ''),
                        model=model,
                        duration_ms=duration,
                        prompt_tokens=data.get('prompt_eval_count', 0),
                        completion_tokens=data.get('eval_count', 0)
                    )
                    
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        task: str = 'general',
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> OllamaResponse:
        """Chat completion with message history"""
        
        model = self.get_model_for_task(task)
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "num_predict": max_tokens,
            "stream": False
        }
        
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=120)
            ) as session:
                start_time = asyncio.get_event_loop().time()
                
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                ) as resp:
                    if resp.status != 200:
                        error = await resp.text()
                        raise Exception(f"Ollama chat error {resp.status}: {error}")
                    
                    data = await resp.json()
                    duration = int((asyncio.get_event_loop().time() - start_time) * 1000)
                    
                    return OllamaResponse(
                        text=data.get('message', {}).get('content', ''),
                        model=model,
                        duration_ms=duration
                    )
                    
        except Exception as e:
            logger.error(f"Ollama chat failed: {e}")
            raise

    # ═══════════════════════════════════════════════════════════
    # CRYPTO FORENSICS METHODS
    # ═══════════════════════════════════════════════════════════
    
    async def analyze_smart_contract(
        self,
        contract_code: str,
        contract_address: str = ""
    ) -> Dict[str, Any]:
        """
        🔍 AI-powered smart contract analysis
        """
        system = """You are an expert smart contract security auditor. Analyze code for vulnerabilities.
Respond in valid JSON format only."""

        # Truncate very large contracts
        code_sample = contract_code[:30000] if len(contract_code) > 30000 else contract_code
        
        prompt = f"""Analyze this smart contract for security vulnerabilities:

Contract Address: {contract_address}

```solidity
{code_sample}
```

Provide analysis in this exact JSON format:
{{
  "risk_score": <0-100>,
  "severity": "<safe/low/medium/high/critical>",
  "findings": [
    {{
      "severity": "<critical/high/medium/low/info>",
      "category": "<vulnerability_type>",
      "description": "<explanation>",
      "line": <line_number_or_null>
    }}
  ],
  "honeypot_risk": <true/false>,
  "rugpull_risk": <true/false>,
  "summary": "<brief risk assessment>"
}}"""

        response = await self.generate(
            prompt=prompt,
            task='contract_analysis',
            system=system,
            temperature=0.3,
            json_mode=True
        )
        
        # Parse JSON response
        try:
            # Extract JSON from markdown if present
            text = response.text
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
            
            result = json.loads(text.strip())
            result['model_used'] = response.model
            result['analysis_time_ms'] = response.duration_ms
            return result
            
        except json.JSONDecodeError:
            # Return structured error with raw response
            return {
                "risk_score": 50,
                "severity": "unknown",
                "findings": [],
                "honeypot_risk": None,
                "rugpull_risk": None,
                "summary": "Analysis parsing failed",
                "raw_response": response.text[:500],
                "model_used": response.model,
                "parsing_error": True
            }
    
    async def detect_threats(
        self,
        token_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        🚨 Detect scam indicators and threats
        """
        system = """You are a crypto threat detection specialist. Identify scams and malicious patterns.
Respond in valid JSON format only."""

        prompt = f"""Analyze this token for threats and scam indicators:

Token Data:
{json.dumps(token_data, indent=2, default=str)[:5000]}

Identify threats in JSON format:
{{
  "threat_level": "<none/low/medium/high/critical>",
  "confidence": <0-100>,
  "indicators": [
    {{
      "type": "<honeypot/rugpull/mint_risk/ownership/tax_manipulation/etc>",
      "severity": "<low/medium/high/critical>",
      "description": "<explanation>"
    }}
  ],
  "red_flags": ["<flag1>", "<flag2>"],
  "recommendation": "<buy/hold/avoid/urgent_sell>"
}}"""

        response = await self.generate(
            prompt=prompt,
            task='threat_detection',
            system=system,
            temperature=0.4,
            json_mode=True
        )
        
        try:
            text = response.text
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
            
            result = json.loads(text.strip())
            result['model_used'] = response.model
            return result
            
        except json.JSONDecodeError:
            return {
                "threat_level": "unknown",
                "confidence": 0,
                "indicators": [],
                "red_flags": [],
                "recommendation": "unknown",
                "raw_response": response.text[:500],
                "parsing_error": True
            }
    
    async def generate_risk_summary(
        self,
        token_name: str,
        token_symbol: str,
        risk_score: int,
        findings: List[Dict]
    ) -> str:
        """
        📝 Generate human-readable risk summary
        """
        prompt = f"""Generate a concise, punchy risk summary for this token:

Token: {token_name} (${token_symbol})
Risk Score: {risk_score}/100
Key Findings: {json.dumps(findings[:5])}

Write 2-3 sentences maximum. Use emoji.
Tone: Urgent if high risk, reassuring if safe.
Be direct and actionable."""

        response = await self.generate(
            prompt=prompt,
            task='quick_summary',
            temperature=0.6,
            max_tokens=200
        )
        
        return response.text.strip()
    
    async def analyze_wallet_patterns(
        self,
        wallet_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        👤 Analyze wallet for suspicious behavior
        """
        system = """You are a blockchain forensics analyst. Examine wallet patterns for suspicious activity."""

        prompt = f"""Analyze this wallet for suspicious patterns:

{json.dumps(wallet_data, indent=2, default=str)[:4000]}

Provide analysis in JSON format:
{{
  "risk_level": "<low/medium/high/critical>",
  "behavior_type": "<normal/trader/bot/whale/scammer/insider>",
  "suspicious_patterns": ["<pattern1>", "<pattern2>"],
  "connected_wallets": ["<address1>", "<address2>"],
  "notes": "<brief analysis summary>"
}}"""

        response = await self.generate(
            prompt=prompt,
            task='wallet_analysis',
            system=system,
            temperature=0.4,
            json_mode=True
        )
        
        try:
            text = response.text
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
            
            return json.loads(text.strip())
        except (json.JSONDecodeError, IndexError, AttributeError):
            return {
                "risk_level": "unknown",
                "behavior_type": "unknown",
                "suspicious_patterns": [],
                "notes": response.text[:300]
            }


# ═══════════════════════════════════════════════════════════
# INTEGRATION HELPER
# ═══════════════════════════════════════════════════════════

class AIProviderRouter:
    """
    🎯 Routes AI requests between Ollama (local) and cloud APIs
    Uses Ollama when available, falls back to cloud
    """
    
    def __init__(self):
        self.ollama = OllamaAIProvider()
        self._ollama_available: Optional[bool] = None
        
    async def check_ollama(self) -> bool:
        """Check if Ollama is available"""
        if self._ollama_available is None:
            self._ollama_available = self.ollama.is_available
            if self._ollama_available:
                models = await self.ollama.list_models()
                logger.info(f"Ollama available with models: {models}")
        return self._ollama_available
    
    async def analyze_contract(
        self,
        contract_code: str,
        contract_address: str = "",
        use_local: bool = True
    ) -> Dict[str, Any]:
        """Analyze contract with auto-routing"""
        
        if use_local and await self.check_ollama():
            try:
                result = await self.ollama.analyze_smart_contract(
                    contract_code, contract_address
                )
                result['source'] = 'ollama_local'
                return result
            except Exception as e:
                logger.warning(f"Ollama failed, would fall back to cloud: {e}")
                # Fall through to cloud
        
        # TODO: Implement cloud fallback
        return {
            "error": "No AI provider available",
            "source": "none"
        }
    
    async def detect_threats(self, token_data: Dict) -> Dict[str, Any]:
        """Detect threats with auto-routing"""
        
        if await self.check_ollama():
            try:
                result = await self.ollama.detect_threats(token_data)
                result['source'] = 'ollama_local'
                return result
            except Exception as e:
                logger.warning(f"Ollama threat detection failed: {e}")
        
        return {"error": "No AI provider available", "source": "none"}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get AI provider status"""
        ollama_ready = await self.check_ollama()
        models = await self.ollama.list_models() if ollama_ready else []
        
        return {
            "ollama_available": ollama_ready,
            "local_models": models,
            "primary_provider": "ollama_local" if ollama_ready else "cloud_fallback",
            "routing_active": True
        }


# ═══════════════════════════════════════════════════════════
# FAST SETUP
# ═══════════════════════════════════════════════════════════

# Global router instance
ai_router = AIProviderRouter()

async def quick_test():
    """Quick test of Ollama integration"""
    print("🦙 Testing RugMuncher Ollama Integration")
    print("=" * 50)
    
    status = await ai_router.get_status()
    print(f"\n📊 Status: {status}")
    
    if status['ollama_available']:
        print("\n✅ Ollama is ready!")
        
        # Test basic generation
        print("\n🧪 Testing basic generation...")
        response = await ai_router.ollama.generate(
            "What are 3 common crypto scam patterns?",
            task='quick_summary'
        )
        print(f"Response ({response.model}): {response.text[:200]}...")
        
        # Test contract analysis
        print("\n🔍 Testing contract analysis...")
        sample_contract = """
        contract TestToken {
            mapping(address => uint) public balances;
            address public owner;
            
            constructor() {
                owner = msg.sender;
            }
            
            function transfer(address to, uint amount) public {
                balances[msg.sender] -= amount;
                balances[to] += amount;
            }
        }
        """
        
        result = await ai_router.analyze_contract(sample_contract, "0x1234...")
        print(f"Risk Score: {result.get('risk_score', 'N/A')}")
        print(f"Severity: {result.get('severity', 'N/A')}")
        print(f"Findings: {len(result.get('findings', []))}")
        print(f"Source: {result.get('source', 'unknown')}")
    else:
        print("\n❌ Ollama not available. Is it running?")
        print(f"   Check: http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/tags")


if __name__ == "__main__":
    asyncio.run(quick_test())
