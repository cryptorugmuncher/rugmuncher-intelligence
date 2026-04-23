"""
Groq AI Launcher - Self-contained within RMI
==============================================

High-speed LLM inference using Groq API.
$200 credit available via API key.

Models Available:
- llama-3.1-70b-versatile (fast, cheap, good)
- llama-3.1-405b-reasoning (powerful reasoning)
- mixtral-8x7b-32768 (large context)
- gemma2-9b-it (lightweight)

Usage:
    from rmi.integrations.ai_tools.groq_launcher import GroqLauncher, get_groq
    
    groq = get_groq()
    response = groq.query("Analyze this token contract for red flags")
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Generator
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Groq Configuration
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# Model pricing (per 1M tokens) - very cheap on Groq
MODELS = {
    "llama-3.1-70b-versatile": {
        "input": 0.59,
        "output": 0.79,
        "context": 131072,
        "description": "Best balance of speed, quality, cost"
    },
    "llama-3.1-8b-instant": {
        "input": 0.05,
        "output": 0.08,
        "context": 131072,
        "description": "Fastest, cheapest"
    },
    "llama-3.3-70b-specdec": {
        "input": 0.59,
        "output": 0.99,
        "context": 8192,
        "description": "Speculative decoding for speed"
    },
    "mixtral-8x7b-32768": {
        "input": 0.24,
        "output": 0.24,
        "context": 32768,
        "description": "Large context window"
    },
    "gemma2-9b-it": {
        "input": 0.20,
        "output": 0.20,
        "context": 8192,
        "description": "Lightweight, efficient"
    },
    "deepseek-r1-distill-llama-70b": {
        "input": 0.75,
        "output": 2.99,
        "context": 131072,
        "description": "Reasoning model (DeepSeek R1)"
    }
}


class GroqLauncher:
    """
    Groq AI Launcher for RMI integration
    
    Provides high-speed inference for:
    - Token analysis
    - Smart contract review
    - OSINT data processing
    - Threat intelligence
    - Code auditing
    """
    
    def __init__(self, api_key: Optional[str] = None, default_model: str = None):
        """
        Initialize Groq launcher
        
        Args:
            api_key: Groq API key (or from GROQ_API_KEY env)
            default_model: Default model to use
        """
        self.api_key = api_key or GROQ_API_KEY
        self.default_model = default_model or "llama-3.1-70b-versatile"
        self.base_url = GROQ_BASE_URL
        self.session = requests.Session()
        
        # Usage tracking
        self.usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "requests": 0,
            "estimated_cost": 0.0
        }
        
        if not self.api_key:
            logger.warning("No Groq API key provided! Set GROQ_API_KEY env var.")
        else:
            # Validate key format (don't log full key)
            masked = self.api_key[:8] + "..." + self.api_key[-4:] if len(self.api_key) > 12 else "invalid"
            logger.info(f"Groq initialized with key: {masked}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API headers"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _update_usage(self, response_data: Dict):
        """Track token usage and cost"""
        usage = response_data.get('usage', {})
        prompt_tokens = usage.get('prompt_tokens', 0)
        completion_tokens = usage.get('completion_tokens', 0)
        total_tokens = usage.get('total_tokens', 0)
        model = response_data.get('model', self.default_model)
        
        self.usage["prompt_tokens"] += prompt_tokens
        self.usage["completion_tokens"] += completion_tokens
        self.usage["total_tokens"] += total_tokens
        self.usage["requests"] += 1
        
        # Calculate cost
        model_info = MODELS.get(model, MODELS[self.default_model])
        cost = (prompt_tokens / 1_000_000 * model_info["input"] + 
                completion_tokens / 1_000_000 * model_info["output"])
        self.usage["estimated_cost"] += cost
    
    def query(self, 
              prompt: str, 
              system: str = None,
              model: str = None,
              max_tokens: int = 2000,
              temperature: float = 0.1,
              json_mode: bool = False) -> Dict[str, Any]:
        """
        Send query to Groq
        
        Args:
            prompt: User prompt
            system: System message
            model: Model to use (default: llama-3.1-70b-versatile)
            max_tokens: Max response tokens
            temperature: Randomness (0.0-1.0)
            json_mode: Return structured JSON
            
        Returns:
            Dict with text, usage, timing info
        """
        if not self.api_key:
            return {"error": "No API key configured", "text": None}
        
        model = model or self.default_model
        messages = []
        
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        
        try:
            import time
            start = time.time()
            
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=self._get_headers(),
                timeout=60
            )
            
            elapsed = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                self._update_usage(data)
                
                text = data['choices'][0]['message']['content']
                
                # Parse JSON if requested
                if json_mode:
                    try:
                        text = json.loads(text)
                    except json.JSONDecodeError:
                        logger.warning("JSON parse failed, returning raw text")
                
                return {
                    "text": text,
                    "model": data.get('model', model),
                    "tokens": data.get('usage', {}),
                    "time_seconds": elapsed,
                    "success": True
                }
            else:
                error_msg = f"Groq error {response.status_code}: {response.text}"
                logger.error(error_msg)
                return {"error": error_msg, "text": None, "success": False}
                
        except Exception as e:
            logger.error(f"Groq request failed: {e}")
            return {"error": str(e), "text": None, "success": False}
    
    def stream(self,
               prompt: str,
               system: str = None,
               model: str = None,
               max_tokens: int = 2000) -> Generator[str, None, None]:
        """
        Stream response from Groq
        
        Args:
            prompt: User prompt
            system: System message
            model: Model to use
            max_tokens: Max tokens
            
        Yields:
            Text chunks as they arrive
        """
        if not self.api_key:
            yield "Error: No API key configured"
            return
        
        model = model or self.default_model
        messages = []
        
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.1,
            "stream": True
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=self._get_headers(),
                timeout=60,
                stream=True
            )
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            delta = chunk['choices'][0]['delta'].get('content', '')
                            if delta:
                                yield delta
                        except:
                            pass
                            
        except Exception as e:
            logger.error(f"Groq stream failed: {e}")
            yield f"Error: {e}"
    
    def analyze_token(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Specialized token analysis using Groq
        
        Args:
            token_data: Token contract info, holder data, etc.
            
        Returns:
            Risk assessment and analysis
        """
        system = """You are a crypto token risk analyzer. Analyze the provided token data and return a JSON response with:
        - risk_score (0-100)
        - risk_level (low/medium/high/critical)
        - red_flags (list of concerns)
        - positive_signals (list of good signs)
        - recommendation (buy/hold/avoid/unknown)
        - reasoning (brief explanation)"""
        
        prompt = f"Analyze this token:\n\n{json.dumps(token_data, indent=2)}"
        
        return self.query(
            prompt=prompt,
            system=system,
            json_mode=True,
            model="llama-3.1-70b-versatile",
            temperature=0.1
        )
    
    def analyze_contract(self, contract_code: str, language: str = "solidity") -> Dict[str, Any]:
        """
        Analyze smart contract code
        
        Args:
            contract_code: Source code
            language: Programming language
            
        Returns:
            Security analysis
        """
        system = """You are a smart contract security auditor. Analyze the provided code and return JSON with:
        - severity_score (0-100, higher = more risky)
        - vulnerabilities (list of issues found)
        - warnings (potential concerns)
        - good_practices (positive findings)
        - overall_assessment (safe/suspicious/dangerous)"""
        
        prompt = f"Analyze this {language} contract:\n\n```{language}\n{contract_code}\n```"
        
        return self.query(
            prompt=prompt,
            system=system,
            json_mode=True,
            model="llama-3.1-70b-versatile"
        )
    
    def process_osint_data(self, raw_data: Dict[str, Any], data_type: str = "profile") -> Dict[str, Any]:
        """
        Process OSINT data into structured format
        
        Args:
            raw_data: Scraped/raw OSINT data
            data_type: Type of data (profile, post, network)
            
        Returns:
            Structured extracted data
        """
        templates = {
            "profile": "Extract profile info: name, bio, location, interests, links, activity level, credibility indicators",
            "post": "Extract post content: sentiment, topics, mentions, engagement metrics, credibility",
            "network": "Extract network relationships: connections, interactions, influence patterns"
        }
        
        system = f"You are an OSINT data processor. {templates.get(data_type, templates['profile'])}. Return structured JSON."
        prompt = f"Process this {data_type} data:\n\n{json.dumps(raw_data, indent=2)}"
        
        return self.query(prompt, system=system, json_mode=True)
    
    def get_usage_report(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            **self.usage,
            "models_available": list(MODELS.keys()),
            "default_model": self.default_model
        }
    
    def list_models(self) -> Dict[str, Dict]:
        """List available models with pricing"""
        return MODELS


# Global instance
_groq_instance: Optional[GroqLauncher] = None


def get_groq(api_key: str = None) -> GroqLauncher:
    """Get global Groq instance"""
    global _groq_instance
    if _groq_instance is None or api_key:
        _groq_instance = GroqLauncher(api_key=api_key)
    return _groq_instance


if __name__ == "__main__":
    # Test/demo
    groq = get_groq()
    
    print("=" * 60)
    print("Groq AI Launcher - RMI Integration")
    print("=" * 60)
    
    # Show available models
    print("\n[Available Models]")
    for name, info in groq.list_models().items():
        print(f"  {name}")
        print(f"    Input: ${info['input']}/1M, Output: ${info['output']}/1M")
        print(f"    Context: {info['context']:,} tokens")
        print(f"    Desc: {info['description']}")
    
    # Test query if key is set
    if groq.api_key:
        print("\n[Test Query]")
        result = groq.query(
            "What is the capital of France?",
            max_tokens=100
        )
        
        if result.get('success'):
            print(f"  Response: {result['text']}")
            print(f"  Time: {result['time_seconds']:.2f}s")
            print(f"  Tokens: {result['tokens']}")
        else:
            print(f"  Error: {result.get('error')}")
        
        print("\n[Usage Report]")
        report = groq.get_usage_report()
        print(f"  Requests: {report['requests']}")
        print(f"  Total tokens: {report['total_tokens']:,}")
        print(f"  Est. cost: ${report['estimated_cost']:.4f}")
    else:
        print("\n[!] No API key set. Skipping test query.")
    
    print("\n" + "=" * 60)
