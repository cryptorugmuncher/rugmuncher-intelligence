"""
================================================================================
LLM COST OPTIMIZER - Smart Routing for Free vs Paid Models
Evidence Fortress v4.0
================================================================================
Routes tasks to the cheapest appropriate LLM while maintaining quality.

Priority Order:
1. Local Ollama (FREE, always preferred for simple tasks)
2. Groq ($200 credit, fast, good for complex reasoning)
3. AWS Bedrock ($200 credit, enterprise features)
4. OpenRouter (free tiers with STRICT sanitization)

CRITICAL: OpenRouter free tiers log prompts for training.
Only send ALREADY-SANITIZED data to OpenRouter.
================================================================================
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import aiohttp
import asyncpg


class LLMProvider(Enum):
    """Supported LLM providers."""
    OLLAMA = "ollama"           # Local, FREE
    GROQ = "groq"               # $200 credit, fast
    AWS_BEDROCK = "aws"         # $200 credit, enterprise
    OPENROUTER = "openrouter"   # Free tiers available (LOGGED!)


class TaskComplexity(Enum):
    """Task complexity levels for routing decisions."""
    SIMPLE = 1      # Pattern matching, regex, simple extraction
    MODERATE = 2    # Basic reasoning, summarization
    COMPLEX = 3     # Multi-step reasoning, analysis
    EXPERT = 4      # Deep forensic analysis, legal reasoning


@dataclass
class ModelConfig:
    """Configuration for an LLM model."""
    provider: LLMProvider
    model_name: str
    cost_per_1k_input: float,   # In dollars
    cost_per_1k_output: float,  # In dollars
    max_tokens: int
    supports_json: bool
    speed_rating: int,          # 1-10 (10 = fastest)
    quality_rating: int,        # 1-10 (10 = best)
    is_free: bool = False
    logs_prompts: bool = True   # CRITICAL: Does provider log for training?


@dataclass
class RoutingDecision:
    """Result of routing decision."""
    provider: LLMProvider
    model: str
    estimated_cost_microdollars: int
    reason: str
    is_free: bool
    requires_sanitization: bool


# ==============================================================================
# MODEL CONFIGURATION
# ==============================================================================

# Local Ollama models (FREE, PRIVATE)
OLLAMA_MODELS = {
    "llama3.1:8b": ModelConfig(
        provider=LLMProvider.OLLAMA,
        model_name="llama3.1:8b",
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        max_tokens=8192,
        supports_json=True,
        speed_rating=7,
        quality_rating=6,
        is_free=True,
        logs_prompts=False  # Local = private
    ),
    "llama3.1:70b": ModelConfig(
        provider=LLMProvider.OLLAMA,
        model_name="llama3.1:70b",
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        max_tokens=8192,
        supports_json=True,
        speed_rating=5,
        quality_rating=8,
        is_free=True,
        logs_prompts=False
    ),
    "phi4:14b": ModelConfig(
        provider=LLMProvider.OLLAMA,
        model_name="phi4:14b",
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        max_tokens=16384,
        supports_json=True,
        speed_rating=8,
        quality_rating=7,
        is_free=True,
        logs_prompts=False
    ),
    "qwen2.5:32b": ModelConfig(
        provider=LLMProvider.OLLAMA,
        model_name="qwen2.5:32b",
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        max_tokens=32768,
        supports_json=True,
        speed_rating=6,
        quality_rating=7,
        is_free=True,
        logs_prompts=False
    ),
    "deepseek-coder:33b": ModelConfig(
        provider=LLMProvider.OLLAMA,
        model_name="deepseek-coder:33b",
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        max_tokens=16384,
        supports_json=True,
        speed_rating=5,
        quality_rating=8,
        is_free=True,
        logs_prompts=False
    ),
}

# Groq models ($200 credit)
GROQ_MODELS = {
    "llama-3.1-70b-versatile": ModelConfig(
        provider=LLMProvider.GROQ,
        model_name="llama-3.1-70b-versatile",
        cost_per_1k_input=0.00059,
        cost_per_1k_output=0.00079,
        max_tokens=32768,
        supports_json=True,
        speed_rating=10,
        quality_rating=8,
        is_free=False,
        logs_prompts=False  # Enterprise, no training logging
    ),
    "mixtral-8x7b-32768": ModelConfig(
        provider=LLMProvider.GROQ,
        model_name="mixtral-8x7b-32768",
        cost_per_1k_input=0.00024,
        cost_per_1k_output=0.00024,
        max_tokens=32768,
        supports_json=True,
        speed_rating=10,
        quality_rating=7,
        is_free=False,
        logs_prompts=False
    ),
    "gemma2-9b-it": ModelConfig(
        provider=LLMProvider.GROQ,
        model_name="gemma2-9b-it",
        cost_per_1k_input=0.00020,
        cost_per_1k_output=0.00020,
        max_tokens=8192,
        supports_json=True,
        speed_rating=10,
        quality_rating=6,
        is_free=False,
        logs_prompts=False
    ),
}

# OpenRouter FREE models (WARNING: LOGS PROMPTS!)
# Only use with ALREADY-SANITIZED data
OPENROUTER_FREE_MODELS = {
    "google/gemma-3-27b-it:free": ModelConfig(
        provider=LLMProvider.OPENROUTER,
        model_name="google/gemma-3-27b-it:free",
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        max_tokens=8192,
        supports_json=True,
        speed_rating=6,
        quality_rating=6,
        is_free=True,
        logs_prompts=True  # FREE = LOGGED FOR TRAINING!
    ),
    "qwen/qwen-2.5-72b-instruct:free": ModelConfig(
        provider=LLMProvider.OPENROUTER,
        model_name="qwen/qwen-2.5-72b-instruct:free",
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        max_tokens=32768,
        supports_json=True,
        speed_rating=5,
        quality_rating=7,
        is_free=True,
        logs_prompts=True
    ),
    "meta-llama/llama-3.3-70b-instruct:free": ModelConfig(
        provider=LLMProvider.OPENROUTER,
        model_name="meta-llama/llama-3.3-70b-instruct:free",
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        max_tokens=32768,
        supports_json=True,
        speed_rating=6,
        quality_rating=7,
        is_free=True,
        logs_prompts=True
    ),
}


class LLMCostOptimizer:
    """
    Smart router for LLM requests.
    
    Prioritizes free/local models but escalates to paid when needed.
    Tracks costs to the microdollar.
    """
    
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
        self.balances = {
            'groq': 200.0,      # $200 credit
            'aws': 200.0,       # $200 credit
        }
        self.ollama_available = True  # Will be checked at runtime
        
    async def check_ollama_health(self) -> bool:
        """Check if Ollama is running locally."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "http://localhost:11434/api/tags",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        available_models = [m['name'] for m in data.get('models', [])]
                        print(f"Ollama available with models: {available_models}")
                        return True
        except Exception as e:
            print(f"Ollama not available: {e}")
        return False
    
    async def route_request(
        self,
        task_description: str,
        estimated_input_tokens: int,
        estimated_output_tokens: int,
        requires_json: bool = False,
        data_is_pre_sanitized: bool = False,
        urgency: str = "normal"  # 'low', 'normal', 'high'
    ) -> RoutingDecision:
        """
        Determine the best LLM for a task.
        
        Args:
            task_description: What needs to be done
            estimated_input_tokens: Expected input size
            estimated_output_tokens: Expected output size
            requires_json: Does output need to be valid JSON?
            data_is_pre_sanitized: Has data passed through SanitizationGateway?
            urgency: How fast does this need to be?
            
        Returns:
            RoutingDecision with provider and cost estimate
        """
        # Check Ollama first (FREE, PRIVATE)
        if await self.check_ollama_health():
            model = self._select_ollama_model(
                estimated_input_tokens, 
                requires_json, 
                urgency
            )
            if model:
                return RoutingDecision(
                    provider=LLMProvider.OLLAMA,
                    model=model,
                    estimated_cost_microdollars=0,
                    reason="Local Ollama - FREE and PRIVATE",
                    is_free=True,
                    requires_sanitization=False
                )
        
        # Determine task complexity
        complexity = self._assess_complexity(task_description)
        
        # For simple tasks, try OpenRouter free (ONLY if pre-sanitized!)
        if complexity in [TaskComplexity.SIMPLE, TaskComplexity.MODERATE]:
            if data_is_pre_sanitized:
                model = self._select_openrouter_model(complexity, requires_json)
                if model:
                    return RoutingDecision(
                        provider=LLMProvider.OPENROUTER,
                        model=model,
                        estimated_cost_microdollars=0,
                        reason="OpenRouter FREE tier (pre-sanitized data only)",
                        is_free=True,
                        requires_sanitization=True  # Must be sanitized!
                    )
            else:
                print("WARNING: Data not sanitized, skipping OpenRouter free tier")
        
        # Use Groq (paid but fast)
        if self.balances['groq'] > 0:
            model = self._select_groq_model(complexity, requires_json, urgency)
            cost = self._estimate_cost(
                model, 
                estimated_input_tokens, 
                estimated_output_tokens
            )
            return RoutingDecision(
                provider=LLMProvider.GROQ,
                model=model,
                estimated_cost_microdollars=cost,
                reason=f"Groq - fast, reliable (${cost/1000000:.4f})",
                is_free=False,
                requires_sanitization=False  # Groq doesn't log for training
            )
        
        # Fallback to AWS Bedrock
        if self.balances['aws'] > 0:
            return RoutingDecision(
                provider=LLMProvider.AWS_BEDROCK,
                model="anthropic.claude-3-sonnet",
                estimated_cost_microdollars=3000,  # $0.003 per 1K
                reason="AWS Bedrock - enterprise fallback",
                is_free=False,
                requires_sanitization=False
            )
        
        # Last resort: OpenRouter free (MUST sanitize!)
        if data_is_pre_sanitized:
            model = self._select_openrouter_model(complexity, requires_json)
            return RoutingDecision(
                provider=LLMProvider.OPENROUTER,
                model=model or "meta-llama/llama-3.3-70b-instruct:free",
                estimated_cost_microdollars=0,
                reason="OpenRouter FREE - LAST RESORT",
                is_free=True,
                requires_sanitization=True
            )
        
        raise RuntimeError(
            "No suitable LLM available. Add credits or sanitize data for OpenRouter."
        )
    
    def _select_ollama_model(
        self, 
        tokens: int, 
        requires_json: bool, 
        urgency: str
    ) -> Optional[str]:
        """Select best Ollama model for the task."""
        if urgency == 'high':
            return "phi4:14b"  # Fast
        elif tokens > 16000:
            return "qwen2.5:32b"  # Large context
        elif requires_json:
            return "llama3.1:8b"  # Reliable JSON
        else:
            return "llama3.1:8b"  # Default
    
    def _select_groq_model(
        self, 
        complexity: TaskComplexity, 
        requires_json: bool,
        urgency: str
    ) -> str:
        """Select best Groq model."""
        if urgency == 'high':
            return "gemma2-9b-it"  # Fastest
        elif complexity == TaskComplexity.EXPERT:
            return "llama-3.1-70b-versatile"
        elif requires_json:
            return "mixtral-8x7b-32768"
        else:
            return "llama-3.1-70b-versatile"
    
    def _select_openrouter_model(
        self, 
        complexity: TaskComplexity,
        requires_json: bool
    ) -> Optional[str]:
        """Select best OpenRouter free model."""
        if complexity == TaskComplexity.EXPERT:
            return "qwen/qwen-2.5-72b-instruct:free"
        elif requires_json:
            return "meta-llama/llama-3.3-70b-instruct:free"
        else:
            return "google/gemma-3-27b-it:free"
    
    def _assess_complexity(self, task_description: str) -> TaskComplexity:
        """Assess task complexity from description."""
        task_lower = task_description.lower()
        
        expert_indicators = [
            'legal', 'rico', 'prosecution', 'court', 'evidence', 'chain of custody',
            'forensic', 'expert witness', 'pattern analysis', 'network graph'
        ]
        
        complex_indicators = [
            'multi-step', 'reasoning', 'analysis', 'correlation', 'timeline',
            'relationship', 'hierarchy', 'clustering'
        ]
        
        simple_indicators = [
            'extract', 'parse', 'count', 'list', 'format', 'convert'
        ]
        
        if any(ind in task_lower for ind in expert_indicators):
            return TaskComplexity.EXPERT
        elif any(ind in task_lower for ind in complex_indicators):
            return TaskComplexity.COMPLEX
        elif any(ind in task_lower for ind in simple_indicators):
            return TaskComplexity.SIMPLE
        else:
            return TaskComplexity.MODERATE
    
    def _estimate_cost(
        self, 
        model_name: str, 
        input_tokens: int, 
        output_tokens: int
    ) -> int:
        """Estimate cost in microdollars."""
        # Find model config
        all_models = {**OLLAMA_MODELS, **GROQ_MODELS, **OPENROUTER_FREE_MODELS}
        config = all_models.get(model_name)
        
        if not config or config.is_free:
            return 0
        
        input_cost = (input_tokens / 1000) * config.cost_per_1k_input
        output_cost = (output_tokens / 1000) * config.cost_per_1k_output
        total_cost = input_cost + output_cost
        
        # Convert to microdollars
        return int(total_cost * 1000000)
    
    async def record_job_start(
        self,
        job_id: str,
        routing: RoutingDecision,
        input_text: str
    ):
        """Record job start in database."""
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO analysis_jobs 
                (id, job_type, llm_provider, llm_model, 
                 estimated_cost_microdollars, status, started_at)
                VALUES ($1, $2, $3, $4, $5, $6, NOW())
                """,
                job_id,
                'llm_analysis',
                routing.provider.value,
                routing.model,
                routing.estimated_cost_microdollars,
                'running'
            )
    
    async def record_job_complete(
        self,
        job_id: str,
        actual_cost_microdollars: int,
        tokens_input: int,
        tokens_output: int,
        result_summary: Dict
    ):
        """Record job completion and update balances."""
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE analysis_jobs 
                SET status = 'complete',
                    actual_cost_microdollars = $1,
                    tokens_input = $2,
                    tokens_output = $3,
                    result_summary = $4,
                    completed_at = NOW()
                WHERE id = $5
                """,
                actual_cost_microdollars,
                tokens_input,
                tokens_output,
                json.dumps(result_summary),
                job_id
            )
        
        # Update balance tracking
        job = await self._get_job(job_id)
        if job and job['llm_provider'] == 'groq':
            self.balances['groq'] -= actual_cost_microdollars / 1000000
    
    async def _get_job(self, job_id: str) -> Optional[Dict]:
        """Get job details."""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM analysis_jobs WHERE id = $1",
                job_id
            )
        return dict(row) if row else None
    
    async def get_cost_report(self) -> Dict:
        """Generate cost analysis report."""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT 
                    llm_provider,
                    COUNT(*) as job_count,
                    SUM(actual_cost_microdollars) as total_cost_micro,
                    SUM(tokens_input) as total_input,
                    SUM(tokens_output) as total_output
                FROM analysis_jobs
                WHERE status = 'complete'
                GROUP BY llm_provider
                """
            )
        
        report = {
            'by_provider': {},
            'remaining_balances': self.balances,
            'total_spent': 0.0
        }
        
        for row in rows:
            provider = row['llm_provider']
            cost_dollars = row['total_cost_micro'] / 1000000
            report['by_provider'][provider] = {
                'jobs': row['job_count'],
                'cost_dollars': cost_dollars,
                'tokens_input': row['total_input'],
                'tokens_output': row['total_output']
            }
            report['total_spent'] += cost_dollars
        
        return report


# ==============================================================================
# OPENROUTER CLIENT (FREE TIER - USE WITH CAUTION!)
# ==============================================================================

class OpenRouterClient:
    """
    Client for OpenRouter free tier.
    
    ⚠️  WARNING: OpenRouter free tiers log prompts for training!
    ⚠️  ONLY use with data that has passed through SanitizationGateway!
    ⚠️  Never send raw addresses to OpenRouter!
    """
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Send chat completion request to OpenRouter.
        
        Args:
            model: Model identifier (e.g., "google/gemma-3-27b-it:free")
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            response_format: Optional JSON schema
            
        Returns:
            API response dict
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://evidence-fortress.local",
            "X-Title": "Evidence Fortress"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if response_format:
            payload["response_format"] = response_format
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise RuntimeError(f"OpenRouter error: {error_text}")
                
                return await resp.json()


# ==============================================================================
# GROQ CLIENT
# ==============================================================================

class GroqClient:
    """Client for Groq API (fast, doesn't log for training)."""
    
    BASE_URL = "https://api.groq.com/openai/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Send chat completion request to Groq."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if response_format:
            payload["response_format"] = response_format
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise RuntimeError(f"Groq error: {error_text}")
                
                return await resp.json()
    
    def extract_usage(self, response: Dict) -> Tuple[int, int]:
        """Extract token usage from response."""
        usage = response.get('usage', {})
        return usage.get('prompt_tokens', 0), usage.get('completion_tokens', 0)


# ==============================================================================
# OLLAMA CLIENT
# ==============================================================================

class OllamaClient:
    """Client for local Ollama instance."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
    
    async def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        format: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send chat completion request to Ollama."""
        
        # Convert OpenAI format to Ollama format
        ollama_messages = []
        for msg in messages:
            ollama_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        payload = {
            "model": model,
            "messages": ollama_messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        if format == "json":
            payload["format"] = "json"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=300)
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise RuntimeError(f"Ollama error: {error_text}")
                
                result = await resp.json()
                
                # Convert to OpenAI-like format
                return {
                    "choices": [{
                        "message": {
                            "content": result.get("message", {}).get("content", "")
                        }
                    }],
                    "usage": {
                        "prompt_tokens": result.get("prompt_eval_count", 0),
                        "completion_tokens": result.get("eval_count", 0)
                    }
                }
