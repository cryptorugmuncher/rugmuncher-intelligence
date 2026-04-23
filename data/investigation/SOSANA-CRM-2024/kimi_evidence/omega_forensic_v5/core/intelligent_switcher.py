"""
Omega Forensic V5 - Intelligent Bot Switcher
=============================================
Smart bot selection with cost optimization.
Routes tasks to appropriate tier based on complexity.
"""

import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IntelligentSwitcher")

# === MODEL CONFIGURATIONS ===
MODELS = {
    # DeepSeek (cheap, good reasoning)
    "deepseek-chat": {
        "provider": "deepseek",
        "endpoint": "https://api.deepseek.com/v1/chat/completions",
        "api_key_env": "DEEPSEEK_API_KEY",
        "cost_tier": "cheap",
        "strengths": ["coding", "reasoning", "long_context"],
        "max_tokens": 8000,
        "temperature": 0.3
    },
    "deepseek-reasoner": {
        "provider": "deepseek",
        "endpoint": "https://api.deepseek.com/v1/chat/completions",
        "api_key_env": "DEEPSEEK_API_KEY",
        "cost_tier": "cheap",
        "strengths": ["chain_of_thought", "complex_reasoning", "evidence_evaluation"],
        "max_tokens": 8000,
        "temperature": 0.2
    },
    # Groq (fast, cheap)
    "llama-3.3-70b-versatile": {
        "provider": "groq",
        "endpoint": "https://api.groq.com/openai/v1/chat/completions",
        "api_key_env": "GROQ_API_KEY",
        "cost_tier": "cheap",
        "strengths": ["speed", "general_purpose"],
        "max_tokens": 4000,
        "temperature": 0.4
    },
    # OpenRouter (free tier)
    "meta-llama/llama-3.3-70b-instruct": {
        "provider": "openrouter",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "api_key_env": "OPENROUTER_API_KEY",
        "cost_tier": "free",
        "strengths": ["general_purpose", "instruction_following"],
        "max_tokens": 4000,
        "temperature": 0.4
    },
}

@dataclass
class TaskConfig:
    """Configuration for a specific task type."""
    task_type: str
    complexity: str  # low, medium, high
    urgency: str     # low, normal, urgent
    preferred_model: Optional[str] = None

class IntelligentSwitcher:
    """
    Intelligent bot switcher for cost-optimized AI usage.
    Routes tasks to the best model for the job.
    """
    
    def __init__(self):
        self.usage_stats = {
            "requests": 0,
            "by_model": {},
            "by_tier": {"free": 0, "cheap": 0, "moderate": 0, "expensive": 0},
            "errors": 0
        }
        self.request_history = []
    
    def select_model(
        self,
        task_type: str = "general",
        complexity: str = "medium",
        urgency: str = "normal",
        data_size: int = 0
    ) -> str:
        """
        Select the best model for a task.
        
        Strategy:
        - High complexity + reasoning needed → DeepSeek Reasoner
        - Urgent + quick reply needed → Groq
        - General purpose + cost sensitive → OpenRouter free
        """
        # High complexity tasks need reasoning
        if complexity == "high" or task_type in ["deep_analysis", "judgment", "rico_analysis"]:
            return "deepseek-reasoner"
        
        # Code generation
        if task_type in ["code_generation", "script_writing"]:
            return "deepseek-chat"
        
        # Urgent tasks need speed
        if urgency == "urgent" or task_type in ["quick_chat", "telegram_reply"]:
            return "llama-3.3-70b-versatile"
        
        # Large data processing
        if data_size > 50000:
            return "meta-llama/llama-3.3-70b-instruct"
        
        # Default to balanced option
        return "meta-llama/llama-3.3-70b-instruct"
    
    def call_model(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        task_type: str = "general",
        complexity: str = "medium",
        urgency: str = "normal",
        max_tokens: int = None,
        temperature: float = None
    ) -> Dict[str, Any]:
        """
        Call an AI model with automatic selection if not specified.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Specific model to use (or auto-select)
            task_type: Type of task for auto-selection
            complexity: Task complexity for auto-selection
            urgency: Task urgency for auto-selection
            max_tokens: Max tokens (or use model default)
            temperature: Temperature (or use model default)
        
        Returns:
            Response dict with 'content', 'model', 'usage'
        """
        # Auto-select model if not specified
        if model is None:
            model = self.select_model(task_type, complexity, urgency)
        
        model_config = MODELS.get(model)
        if not model_config:
            raise ValueError(f"Unknown model: {model}")
        
        # Get API key
        api_key = os.getenv(model_config["api_key_env"])
        if not api_key:
            raise ValueError(f"API key not found for {model}")
        
        # Build request
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Add OpenRouter specific headers
        if model_config["provider"] == "openrouter":
            headers["HTTP-Referer"] = "https://omega-forensic.local"
            headers["X-Title"] = "Omega Forensic V5"
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens or model_config.get("max_tokens", 4000),
            "temperature": temperature or model_config.get("temperature", 0.4)
        }
        
        try:
            response = requests.post(
                model_config["endpoint"],
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Track usage
            self._track_usage(model, model_config["cost_tier"], True)
            
            # Extract content
            content = result["choices"][0]["message"]["content"]
            usage = result.get("usage", {})
            
            return {
                "content": content,
                "model": model,
                "usage": usage,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error calling {model}: {e}")
            self._track_usage(model, model_config["cost_tier"], False)
            
            return {
                "content": None,
                "model": model,
                "error": str(e),
                "success": False
            }
    
    def _track_usage(self, model: str, tier: str, success: bool):
        """Track API usage."""
        self.usage_stats["requests"] += 1
        self.usage_stats["by_tier"][tier] += 1
        
        if model not in self.usage_stats["by_model"]:
            self.usage_stats["by_model"][model] = {"requests": 0, "errors": 0}
        
        self.usage_stats["by_model"][model]["requests"] += 1
        
        if not success:
            self.usage_stats["errors"] += 1
            self.usage_stats["by_model"][model]["errors"] += 1
        
        # Add to history
        self.request_history.append({
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "tier": tier,
            "success": success
        })
    
    def get_usage_report(self) -> Dict:
        """Get usage statistics report."""
        return {
            "total_requests": self.usage_stats["requests"],
            "by_tier": self.usage_stats["by_tier"],
            "by_model": self.usage_stats["by_model"],
            "error_rate": (
                self.usage_stats["errors"] / self.usage_stats["requests"]
                if self.usage_stats["requests"] > 0 else 0
            ),
            "estimated_cost_usd": self._estimate_cost()
        }
    
    def _estimate_cost(self) -> float:
        """Estimate total cost based on usage."""
        # Rough estimates per 1K tokens
        tier_costs = {
            "free": 0.0,
            "cheap": 0.001,      # ~$0.001 per 1K tokens
            "moderate": 0.01,    # ~$0.01 per 1K tokens
            "expensive": 0.1     # ~$0.1 per 1K tokens
        }
        
        total = 0.0
        for tier, count in self.usage_stats["by_tier"].items():
            total += count * tier_costs.get(tier, 0.001) * 2  # Assume 2K tokens avg
        
        return total
    
    def self_heal(self, error_info: Dict):
        """
        Self-healing: learn from errors and adjust.
        If a model fails, try a different one next time.
        """
        failed_model = error_info.get("model")
        task_type = error_info.get("task_type")
        
        logger.info(f"🩹 Self-healing: {failed_model} failed for {task_type}")
        
        # Add to history for pattern learning
        self.request_history.append({
            "timestamp": datetime.now().isoformat(),
            "model": failed_model,
            "task_type": task_type,
            "event": "failure",
            "error": error_info.get("error")
        })

# === QUICK ACCESS FUNCTIONS ===
def quick_reply(prompt: str, context: str = None) -> str:
    """Get quick reply using cheapest/fastest model."""
    switcher = IntelligentSwitcher()
    
    messages = []
    if context:
        messages.append({"role": "system", "content": context})
    messages.append({"role": "user", "content": prompt})
    
    result = switcher.call_model(
        messages=messages,
        task_type="quick_chat",
        urgency="urgent"
    )
    
    return result.get("content", "Error: No response")

def deep_analysis(prompt: str, evidence: str = None) -> str:
    """Get deep analysis using reasoning model."""
    switcher = IntelligentSwitcher()
    
    messages = [
        {"role": "system", "content": "You are a forensic blockchain analyst. Analyze evidence carefully and provide detailed reasoning."}
    ]
    
    if evidence:
        messages.append({"role": "user", "content": f"Evidence:\n{evidence}\n\n{prompt}"})
    else:
        messages.append({"role": "user", "content": prompt})
    
    result = switcher.call_model(
        messages=messages,
        task_type="deep_analysis",
        complexity="high"
    )
    
    return result.get("content", "Error: No response")

def generate_code(prompt: str, language: str = "python") -> str:
    """Generate code using coding-optimized model."""
    switcher = IntelligentSwitcher()
    
    messages = [
        {"role": "system", "content": f"You are an expert {language} developer. Write clean, well-documented code."},
        {"role": "user", "content": prompt}
    ]
    
    result = switcher.call_model(
        messages=messages,
        task_type="code_generation",
        complexity="medium"
    )
    
    return result.get("content", "Error: No response")

if __name__ == "__main__":
    # Test the switcher
    print("=" * 70)
    print("OMEGA FORENSIC V5 - INTELLIGENT SWITCHER")
    print("=" * 70)
    
    switcher = IntelligentSwitcher()
    
    # Test model selection
    print("\n📊 Model Selection Tests:")
    test_cases = [
        ("quick_chat", "low", "urgent"),
        ("deep_analysis", "high", "normal"),
        ("code_generation", "medium", "normal"),
        ("telegram_reply", "low", "urgent"),
    ]
    
    for task, complexity, urgency in test_cases:
        model = switcher.select_model(task, complexity, urgency)
        print(f"  {task:20} ({complexity}, {urgency:7}) → {model}")
    
    # Test quick reply (if API keys available)
    if os.getenv("GROQ_API_KEY"):
        print("\n💬 Testing quick reply...")
        reply = quick_reply("What is blockchain forensics?")
        print(f"  Response: {reply[:100]}...")
    
    print("\n" + "=" * 70)
