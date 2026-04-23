"""
LLM Rotation System - Free Tier API Manager
===========================================
Rotates through free API tiers to minimize costs while maximizing capability.
Groq, Amazon Bedrock, Google AI, Claude free tiers
"""

import os
import json
import asyncio
import random
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import aiohttp


class LLMProvider(Enum):
    """Available LLM providers with free tiers."""
    GROQ = "groq"
    AMAZON_BEDROCK = "amazon"
    GOOGLE_AI = "google"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"
    DEEPSEEK = "deepseek"
    LOCAL = "local"


@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    name: str
    provider: LLMProvider
    max_tokens: int
    context_window: int
    rpm_limit: int  # Requests per minute
    daily_limit: int  # Daily request limit (for free tiers)
    cost_per_1k_input: float
    cost_per_1k_output: float
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)


# Free tier model configurations
FREE_MODELS = {
    # Groq - $200 credit, very fast
    "llama-3.3-70b-versatile": ModelConfig(
        name="llama-3.3-70b-versatile",
        provider=LLMProvider.GROQ,
        max_tokens=32768,
        context_window=128000,
        rpm_limit=30,
        daily_limit=1440,  # 30 * 48 (assuming we spread across day)
        cost_per_1k_input=0.0,  # Free with credit
        cost_per_1k_output=0.0,
        strengths=["fast", "coding", "reasoning", "cheap"],
        weaknesses=["context_limit"]
    ),
    "llama-3.1-8b-instant": ModelConfig(
        name="llama-3.1-8b-instant",
        provider=LLMProvider.GROQ,
        max_tokens=8192,
        context_window=128000,
        rpm_limit=60,
        daily_limit=2880,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        strengths=["very_fast", "simple_tasks", "cheap"],
        weaknesses=["complex_reasoning"]
    ),
    "mixtral-8x7b-32768": ModelConfig(
        name="mixtral-8x7b-32768",
        provider=LLMProvider.GROQ,
        max_tokens=32768,
        context_window=32768,
        rpm_limit=30,
        daily_limit=1440,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        strengths=["long_context", "analysis"],
        weaknesses=["coding"]
    ),
    
    # Amazon Bedrock - $200 credit
    "amazon.nova-pro-v1:0": ModelConfig(
        name="amazon.nova-pro-v1:0",
        provider=LLMProvider.AMAZON_BEDROCK,
        max_tokens=4096,
        context_window=128000,
        rpm_limit=20,
        daily_limit=1000,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        strengths=["reliable", "balanced", "good_output"],
        weaknesses=["speed"]
    ),
    "amazon.nova-lite-v1:0": ModelConfig(
        name="amazon.nova-lite-v1:0",
        provider=LLMProvider.AMAZON_BEDROCK,
        max_tokens=4096,
        context_window=128000,
        rpm_limit=40,
        daily_limit=2000,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        strengths=["fast", "cheap", "good_for_simple"],
        weaknesses=["complex_tasks"]
    ),
    
    # Google AI - Free tier
    "gemini-2.0-flash": ModelConfig(
        name="gemini-2.0-flash",
        provider=LLMProvider.GOOGLE_AI,
        max_tokens=8192,
        context_window=1000000,
        rpm_limit=15,
        daily_limit=1500,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        strengths=["huge_context", "fast", "multimodal"],
        weaknesses=["inconsistent"]
    ),
    "gemini-2.0-flash-lite": ModelConfig(
        name="gemini-2.0-flash-lite",
        provider=LLMProvider.GOOGLE_AI,
        max_tokens=8192,
        context_window=1000000,
        rpm_limit=30,
        daily_limit=3000,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        strengths=["very_fast", "cheap", "huge_context"],
        weaknesses=["quality"]
    ),
    
    # Anthropic Claude - Limited free tier
    "claude-3-haiku-20240307": ModelConfig(
        name="claude-3-haiku-20240307",
        provider=LLMProvider.ANTHROPIC,
        max_tokens=4096,
        context_window=200000,
        rpm_limit=10,
        daily_limit=500,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        strengths=["excellent_reasoning", "careful", "accurate"],
        weaknesses=["slow", "limited_free"]
    ),
    
    # OpenRouter - Free tier access to many models
    "meta-llama/llama-3.3-70b-instruct:free": ModelConfig(
        name="meta-llama/llama-3.3-70b-instruct:free",
        provider=LLMProvider.OPENROUTER,
        max_tokens=32768,
        context_window=128000,
        rpm_limit=20,
        daily_limit=1000,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        strengths=["free_access", "good_quality", "reliable"],
        weaknesses=["rate_limits"]
    ),
    "google/gemini-2.0-flash-exp:free": ModelConfig(
        name="google/gemini-2.0-flash-exp:free",
        provider=LLMProvider.OPENROUTER,
        max_tokens=8192,
        context_window=1000000,
        rpm_limit=20,
        daily_limit=1000,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        strengths=["huge_context", "free", "fast"],
        weaknesses=["experimental"]
    ),
    
    # DeepSeek - Very cheap, good reasoning
    "deepseek-chat": ModelConfig(
        name="deepseek-chat",
        provider=LLMProvider.DEEPSEEK,
        max_tokens=8192,
        context_window=64000,
        rpm_limit=20,
        daily_limit=1000,
        cost_per_1k_input=0.00027,  # Very cheap even if not free
        cost_per_1k_output=0.0011,
        strengths=["excellent_coding", "cheap", "good_reasoning"],
        weaknesses=["availability"]
    ),
    "deepseek-reasoner": ModelConfig(
        name="deepseek-reasoner",
        provider=LLMProvider.DEEPSEEK,
        max_tokens=8192,
        context_window=64000,
        rpm_limit=10,
        daily_limit=500,
        cost_per_1k_input=0.00055,
        cost_per_1k_output=0.00219,
        strengths=["excellent_reasoning", "chain_of_thought", "complex_analysis"],
        weaknesses=["slow", "expensive"]
    ),
}


@dataclass
class UsageStats:
    """Track usage for a model."""
    model_name: str
    requests_today: int = 0
    tokens_input_today: int = 0
    tokens_output_today: int = 0
    last_request_time: Optional[datetime] = None
    errors_today: int = 0
    
    def can_make_request(self, config: ModelConfig) -> bool:
        """Check if we can make another request."""
        if self.requests_today >= config.daily_limit:
            return False
        if self.last_request_time:
            time_since = datetime.now() - self.last_request_time
            min_interval = timedelta(seconds=60 / config.rpm_limit)
            if time_since < min_interval:
                return False
        return True


class LLMRotator:
    """
    Intelligent LLM rotation system for free tier optimization.
    Selects best model for task while respecting rate limits.
    """
    
    def __init__(self):
        self.usage_stats: Dict[str, UsageStats] = {}
        self.api_keys = self._load_api_keys()
        self.request_history: List[Dict] = []
        self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0)
        
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from environment."""
        return {
            "groq": os.getenv("GROQ_API_KEY", ""),
            "amazon_access": os.getenv("AWS_ACCESS_KEY_ID", ""),
            "amazon_secret": os.getenv("AWS_SECRET_ACCESS_KEY", ""),
            "google": os.getenv("GOOGLE_API_KEY", ""),
            "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
            "openrouter": os.getenv("OPENROUTER_API_KEY", ""),
            "deepseek": os.getenv("DEEPSEEK_API_KEY", ""),
        }
    
    def _get_or_create_stats(self, model_name: str) -> UsageStats:
        """Get or create usage stats for a model."""
        if model_name not in self.usage_stats:
            self.usage_stats[model_name] = UsageStats(model_name=model_name)
        return self.usage_stats[model_name]
    
    def _reset_daily_stats(self):
        """Reset daily stats at midnight."""
        now = datetime.now()
        if now.date() > self.daily_reset_time.date():
            for stats in self.usage_stats.values():
                stats.requests_today = 0
                stats.tokens_input_today = 0
                stats.tokens_output_today = 0
                stats.errors_today = 0
            self.daily_reset_time = now.replace(hour=0, minute=0, second=0)
    
    def select_model(
        self,
        task_type: str = "general",
        required_context: int = 0,
        prefer_speed: bool = False,
        prefer_quality: bool = False,
        exclude_providers: List[LLMProvider] = None
    ) -> Optional[str]:
        """
        Select best available model for the task.
        
        Args:
            task_type: Type of task (coding, analysis, quick_reply, reasoning)
            required_context: Required context window size
            prefer_speed: Prioritize fast models
            prefer_quality: Prioritize high quality models
            exclude_providers: Providers to exclude
        """
        self._reset_daily_stats()
        exclude_providers = exclude_providers or []
        
        # Task type to model strengths mapping
        task_strengths = {
            "coding": ["coding", "excellent_coding", "reasoning"],
            "analysis": ["analysis", "excellent_reasoning", "careful"],
            "quick_reply": ["very_fast", "fast", "simple_tasks"],
            "reasoning": ["excellent_reasoning", "chain_of_thought", "reasoning"],
            "general": ["fast", "balanced", "reliable"],
        }
        
        candidates = []
        for name, config in FREE_MODELS.items():
            # Skip excluded providers
            if config.provider in exclude_providers:
                continue
            
            # Skip if no API key
            if not self._has_api_key(config.provider):
                continue
            
            # Check context window
            if required_context > config.context_window:
                continue
            
            # Check rate limits
            stats = self._get_or_create_stats(name)
            if not stats.can_make_request(config):
                continue
            
            # Calculate score
            score = 100
            
            # Boost for task-appropriate strengths
            desired_strengths = task_strengths.get(task_type, ["balanced"])
            for strength in desired_strengths:
                if strength in config.strengths:
                    score += 20
            
            # Speed preference
            if prefer_speed:
                if "very_fast" in config.strengths:
                    score += 30
                elif "fast" in config.strengths:
                    score += 15
            
            # Quality preference
            if prefer_quality:
                if "excellent_reasoning" in config.strengths:
                    score += 30
                elif "careful" in config.strengths:
                    score += 15
            
            # Penalty for high error rate
            if stats.errors_today > 5:
                score -= 50
            
            # Penalty for approaching daily limit
            usage_ratio = stats.requests_today / config.daily_limit
            if usage_ratio > 0.8:
                score -= 40
            elif usage_ratio > 0.5:
                score -= 20
            
            candidates.append((name, config, score))
        
        if not candidates:
            return None
        
        # Sort by score descending
        candidates.sort(key=lambda x: x[2], reverse=True)
        
        # Return top candidate
        return candidates[0][0]
    
    def _has_api_key(self, provider: LLMProvider) -> bool:
        """Check if we have API key for provider."""
        key_map = {
            LLMProvider.GROQ: "groq",
            LLMProvider.AMAZON_BEDROCK: "amazon_access",
            LLMProvider.GOOGLE_AI: "google",
            LLMProvider.ANTHROPIC: "anthropic",
            LLMProvider.OPENROUTER: "openrouter",
            LLMProvider.DEEPSEEK: "deepseek",
        }
        key_name = key_map.get(provider)
        if not key_name:
            return False
        return bool(self.api_keys.get(key_name))
    
    async def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        task_type: str = "general",
        temperature: float = 0.7,
        max_tokens: int = None,
        **kwargs
    ) -> Dict:
        """
        Generate text using the best available model.
        
        Returns:
            Dict with text, model_used, tokens_used, cost, success
        """
        # Select model
        required_context = len(prompt) + len(system_prompt or "")
        model_name = self.select_model(
            task_type=task_type,
            required_context=required_context,
            prefer_speed=kwargs.get("prefer_speed", False),
            prefer_quality=kwargs.get("prefer_quality", False)
        )
        
        if not model_name:
            return {
                "success": False,
                "error": "No available models within rate limits",
                "text": None,
                "model_used": None,
                "tokens_used": 0,
                "cost": 0
            }
        
        config = FREE_MODELS[model_name]
        stats = self._get_or_create_stats(model_name)
        
        try:
            # Route to appropriate provider
            if config.provider == LLMProvider.GROQ:
                result = await self._call_groq(prompt, system_prompt, model_name, temperature, max_tokens)
            elif config.provider == LLMProvider.AMAZON_BEDROCK:
                result = await self._call_bedrock(prompt, system_prompt, model_name, temperature, max_tokens)
            elif config.provider == LLMProvider.GOOGLE_AI:
                result = await self._call_google(prompt, system_prompt, model_name, temperature, max_tokens)
            elif config.provider == LLMProvider.ANTHROPIC:
                result = await self._call_anthropic(prompt, system_prompt, model_name, temperature, max_tokens)
            elif config.provider == LLMProvider.OPENROUTER:
                result = await self._call_openrouter(prompt, system_prompt, model_name, temperature, max_tokens)
            elif config.provider == LLMProvider.DEEPSEEK:
                result = await self._call_deepseek(prompt, system_prompt, model_name, temperature, max_tokens)
            else:
                raise ValueError(f"Unknown provider: {config.provider}")
            
            # Update stats
            stats.requests_today += 1
            stats.tokens_input_today += result.get("input_tokens", 0)
            stats.tokens_output_today += result.get("output_tokens", 0)
            stats.last_request_time = datetime.now()
            
            # Log request
            self.request_history.append({
                "timestamp": datetime.now().isoformat(),
                "model": model_name,
                "provider": config.provider.value,
                "task_type": task_type,
                "success": True,
                "tokens": result.get("total_tokens", 0)
            })
            
            return {
                "success": True,
                "text": result["text"],
                "model_used": model_name,
                "provider": config.provider.value,
                "tokens_input": result.get("input_tokens", 0),
                "tokens_output": result.get("output_tokens", 0),
                "total_tokens": result.get("total_tokens", 0),
                "cost": self._calculate_cost(config, result)
            }
            
        except Exception as e:
            stats.errors_today += 1
            return {
                "success": False,
                "error": str(e),
                "text": None,
                "model_used": model_name,
                "tokens_used": 0,
                "cost": 0
            }
    
    async def _call_groq(self, prompt, system, model, temperature, max_tokens):
        """Call Groq API."""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_keys['groq']}",
            "Content-Type": "application/json"
        }
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 4096
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as resp:
                result = await resp.json()
                return {
                    "text": result["choices"][0]["message"]["content"],
                    "input_tokens": result["usage"]["prompt_tokens"],
                    "output_tokens": result["usage"]["completion_tokens"],
                    "total_tokens": result["usage"]["total_tokens"]
                }
    
    async def _call_bedrock(self, prompt, system, model, temperature, max_tokens):
        """Call Amazon Bedrock API."""
        import boto3
        
        client = boto3.client(
            'bedrock-runtime',
            region_name='us-east-1',
            aws_access_key_id=self.api_keys["amazon_access"],
            aws_secret_access_key=self.api_keys["amazon_secret"]
        )
        
        body = {
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
            "inferenceConfig": {
                "temperature": temperature,
                "maxTokens": max_tokens or 4096
            }
        }
        
        response = client.converse(
            modelId=model,
            **body
        )
        
        return {
            "text": response["output"]["message"]["content"][0]["text"],
            "input_tokens": response["usage"]["inputTokens"],
            "output_tokens": response["usage"]["outputTokens"],
            "total_tokens": response["usage"]["totalTokens"]
        }
    
    async def _call_google(self, prompt, system, model, temperature, max_tokens):
        """Call Google AI API."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        params = {"key": self.api_keys["google"]}
        
        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        if system:
            contents.insert(0, {"role": "model", "parts": [{"text": system}]})
        
        data = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens or 8192
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params, json=data) as resp:
                result = await resp.json()
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                # Google doesn't always return token counts in free tier
                return {
                    "text": text,
                    "input_tokens": len(prompt) // 4,  # Estimate
                    "output_tokens": len(text) // 4,
                    "total_tokens": (len(prompt) + len(text)) // 4
                }
    
    async def _call_anthropic(self, prompt, system, model, temperature, max_tokens):
        """Call Anthropic API."""
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_keys["anthropic"],
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": model,
            "max_tokens": max_tokens or 4096,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }
        if system:
            data["system"] = system
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as resp:
                result = await resp.json()
                return {
                    "text": result["content"][0]["text"],
                    "input_tokens": result["usage"]["input_tokens"],
                    "output_tokens": result["usage"]["output_tokens"],
                    "total_tokens": result["usage"]["input_tokens"] + result["usage"]["output_tokens"]
                }
    
    async def _call_openrouter(self, prompt, system, model, temperature, max_tokens):
        """Call OpenRouter API."""
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_keys['openrouter']}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 4096
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as resp:
                result = await resp.json()
                return {
                    "text": result["choices"][0]["message"]["content"],
                    "input_tokens": result["usage"]["prompt_tokens"],
                    "output_tokens": result["usage"]["completion_tokens"],
                    "total_tokens": result["usage"]["total_tokens"]
                }
    
    async def _call_deepseek(self, prompt, system, model, temperature, max_tokens):
        """Call DeepSeek API."""
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_keys['deepseek']}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 4096
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as resp:
                result = await resp.json()
                return {
                    "text": result["choices"][0]["message"]["content"],
                    "input_tokens": result["usage"]["prompt_tokens"],
                    "output_tokens": result["usage"]["completion_tokens"],
                    "total_tokens": result["usage"]["total_tokens"]
                }
    
    def _calculate_cost(self, config: ModelConfig, result: Dict) -> float:
        """Calculate cost for the request."""
        input_cost = (result.get("input_tokens", 0) / 1000) * config.cost_per_1k_input
        output_cost = (result.get("output_tokens", 0) / 1000) * config.cost_per_1k_output
        return input_cost + output_cost
    
    def get_usage_report(self) -> Dict:
        """Get comprehensive usage report."""
        total_requests = sum(s.requests_today for s in self.usage_stats.values())
        total_tokens = sum(s.tokens_input_today + s.tokens_output_today for s in self.usage_stats.values())
        total_errors = sum(s.errors_today for s in self.usage_stats.values())
        
        model_breakdown = {}
        for name, stats in self.usage_stats.items():
            config = FREE_MODELS.get(name)
            if config:
                model_breakdown[name] = {
                    "requests": stats.requests_today,
                    "requests_limit": config.daily_limit,
                    "usage_percent": (stats.requests_today / config.daily_limit * 100) if config.daily_limit > 0 else 0,
                    "tokens": stats.tokens_input_today + stats.tokens_output_today,
                    "errors": stats.errors_today
                }
        
        return {
            "total_requests_today": total_requests,
            "total_tokens_today": total_tokens,
            "total_errors_today": total_errors,
            "models": model_breakdown,
            "request_history_last_10": self.request_history[-10:]
        }


# Global rotator instance
_rotator = None

def get_llm_rotator() -> LLMRotator:
    """Get global LLM rotator instance."""
    global _rotator
    if _rotator is None:
        _rotator = LLMRotator()
    return _rotator


async def quick_generate(prompt: str, task_type: str = "quick_reply", **kwargs) -> str:
    """Quick generation with automatic model selection."""
    rotator = get_llm_rotator()
    result = await rotator.generate(prompt, task_type=task_type, **kwargs)
    if result["success"]:
        return result["text"]
    return f"Error: {result.get('error', 'Unknown error')}"


async def deep_analyze(prompt: str, system_prompt: str = None, **kwargs) -> Dict:
    """Deep analysis with quality model."""
    rotator = get_llm_rotator()
    return await rotator.generate(
        prompt=prompt,
        system_prompt=system_prompt,
        task_type="reasoning",
        prefer_quality=True,
        **kwargs
    )


if __name__ == "__main__":
    print("=" * 70)
    print("LLM ROTATION SYSTEM - Free Tier Optimizer")
    print("=" * 70)
    
    rotator = get_llm_rotator()
    
    print("\n📊 Available Models:")
    for name, config in FREE_MODELS.items():
        has_key = rotator._has_api_key(config.provider)
        status = "✅" if has_key else "❌ (no API key)"
        print(f"  {status} {name}")
        print(f"      Provider: {config.provider.value}")
        print(f"      RPM: {config.rpm_limit} | Daily: {config.daily_limit}")
        print(f"      Strengths: {', '.join(config.strengths[:3])}")
    
    print("\n🎯 Model Selection Examples:")
    for task in ["quick_reply", "coding", "analysis", "reasoning"]:
        model = rotator.select_model(task_type=task)
        print(f"  {task}: {model or 'No model available'}")
    
    print("\n" + "=" * 70)
