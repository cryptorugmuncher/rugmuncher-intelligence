"""
Omega Forensic V5 - Optimal Bot Configuration
==============================================
Best-in-class AI bot assignments for each forensic task.
Two-tier architecture: Premium models for analysis, cheap models for output.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum

class TaskType(Enum):
    """Classification of forensic tasks."""
    QUICK_CHAT = "quick_chat"           # Fast Telegram replies
    DEEP_ANALYSIS = "deep_analysis"     # Complex reasoning
    CODE_GENERATION = "code_generation" # Python/scripts
    RESEARCH = "research"               # Deep investigation
    SUMMARIZATION = "summarization"     # Report generation
    JUDGMENT = "judgment"               # Evidence assessment
    DATA_PROCESSING = "data_processing" # Large data analysis

@dataclass
class BotConfig:
    """Configuration for a specific AI bot."""
    name: str
    model_id: str
    provider: str
    cost_tier: str  # free, cheap, moderate, expensive
    strengths: List[str]
    context_window: int
    speed: str  # fast, medium, slow
    best_for: List[TaskType]
    api_key_env: str
    
    def __repr__(self):
        return f"{self.name} ({self.provider}) - {self.cost_tier}"

# === BOT ARSENAL ===
class BotArsenal:
    """Complete bot configuration for Omega Forensic V5."""
    
    # === TIER 1: FREE/PREMIUM MODELS (Analysis) ===
    DEEPSEEK_CHAT = BotConfig(
        name="DeepSeek-V3",
        model_id="deepseek-chat",
        provider="deepseek",
        cost_tier="cheap",
        strengths=["coding", "reasoning", "mathematics", "long context"],
        context_window=64000,
        speed="medium",
        best_for=[TaskType.DEEP_ANALYSIS, TaskType.CODE_GENERATION, TaskType.RESEARCH],
        api_key_env="DEEPSEEK_API_KEY"
    )
    
    DEEPSEEK_REASONER = BotConfig(
        name="DeepSeek-R1",
        model_id="deepseek-reasoner",
        provider="deepseek",
        cost_tier="cheap",
        strengths=["chain-of-thought", "complex reasoning", "evidence evaluation"],
        context_window=64000,
        speed="slow",
        best_for=[TaskType.DEEP_ANALYSIS, TaskType.JUDGMENT, TaskType.RESEARCH],
        api_key_env="DEEPSEEK_API_KEY"
    )
    
    OPENROUTER_LLAMA = BotConfig(
        name="Llama-3.3-70B",
        model_id="meta-llama/llama-3.3-70b-instruct",
        provider="openrouter",
        cost_tier="free",
        strengths=["general purpose", "instruction following", "balanced"],
        context_window=128000,
        speed="fast",
        best_for=[TaskType.QUICK_CHAT, TaskType.SUMMARIZATION, TaskType.DATA_PROCESSING],
        api_key_env="OPENROUTER_API_KEY"
    )
    
    OPENROUTER_DEEPSEEK = BotConfig(
        name="DeepSeek-V3-OR",
        model_id="deepseek/deepseek-chat",
        provider="openrouter",
        cost_tier="free",
        strengths=["coding", "analysis", "cost-effective"],
        context_window=64000,
        speed="medium",
        best_for=[TaskType.CODE_GENERATION, TaskType.DEEP_ANALYSIS],
        api_key_env="OPENROUTER_API_KEY"
    )
    
    # === TIER 2: CHEAP MODELS (Output) ===
    GROQ_LLAMA = BotConfig(
        name="Llama-3.3-70B-Groq",
        model_id="llama-3.3-70b-versatile",
        provider="groq",
        cost_tier="cheap",
        strengths=["speed", "cost-effective", "good quality"],
        context_window=128000,
        speed="fast",
        best_for=[TaskType.QUICK_CHAT, TaskType.SUMMARIZATION],
        api_key_env="GROQ_API_KEY"
    )
    
    GROQ_MIXTRAL = BotConfig(
        name="Mixtral-8x7B",
        model_id="mixtral-8x7b-32768",
        provider="groq",
        cost_tier="cheap",
        strengths=["fast", "multilingual", "efficient"],
        context_window=32768,
        speed="fast",
        best_for=[TaskType.QUICK_CHAT, TaskType.SUMMARIZATION],
        api_key_env="GROQ_API_KEY"
    )
    
    # === SPECIALIZED BOTS ===
    INVESTIGATOR_BOT = BotConfig(
        name="The Investigator",
        model_id="deepseek-reasoner",
        provider="deepseek",
        cost_tier="cheap",
        strengths=[
            "matter-of-fact personality",
            "online investigator mindset",
            "digs multiple wallet layers deep",
            "always finds answers",
            "polite but persistent",
            "reasoning skills",
            "self-healing",
            "self-learning"
        ],
        context_window=64000,
        speed="medium",
        best_for=[TaskType.RESEARCH, TaskType.DEEP_ANALYSIS, TaskType.JUDGMENT],
        api_key_env="DEEPSEEK_API_KEY"
    )
    
    # === ASSIGNMENTS BY TASK ===
    @classmethod
    def get_bot_for_task(cls, task: TaskType, prefer_speed: bool = False) -> BotConfig:
        """Get optimal bot for a specific task."""
        assignments = {
            TaskType.QUICK_CHAT: cls.GROQ_LLAMA if prefer_speed else cls.OPENROUTER_LLAMA,
            TaskType.DEEP_ANALYSIS: cls.DEEPSEEK_REASONER,
            TaskType.CODE_GENERATION: cls.DEEPSEEK_CHAT,
            TaskType.RESEARCH: cls.INVESTIGATOR_BOT,
            TaskType.SUMMARIZATION: cls.GROQ_LLAMA,
            TaskType.JUDGMENT: cls.DEEPSEEK_REASONER,
            TaskType.DATA_PROCESSING: cls.OPENROUTER_LLAMA,
        }
        return assignments.get(task, cls.DEEPSEEK_CHAT)
    
    @classmethod
    def get_all_bots(cls) -> List[BotConfig]:
        """Return all available bot configurations."""
        return [
            cls.DEEPSEEK_CHAT,
            cls.DEEPSEEK_REASONER,
            cls.OPENROUTER_LLAMA,
            cls.OPENROUTER_DEEPSEEK,
            cls.GROQ_LLAMA,
            cls.GROQ_MIXTRAL,
            cls.INVESTIGATOR_BOT,
        ]
    
    @classmethod
    def get_bot_by_name(cls, name: str) -> Optional[BotConfig]:
        """Get bot configuration by name."""
        for bot in cls.get_all_bots():
            if bot.name.lower() == name.lower():
                return bot
        return None

# === INTELLIGENT SWITCHER ===
class IntelligentSwitcher:
    """
    Smart bot selection with cost optimization.
    Routes tasks to appropriate tier based on complexity.
    """
    
    def __init__(self):
        self.request_count = 0
        self.cost_tracker = {"free": 0, "cheap": 0, "moderate": 0, "expensive": 0}
    
    def select_bot(
        self,
        task: TaskType,
        complexity: str = "medium",  # low, medium, high
        urgency: str = "normal",     # low, normal, urgent
        data_size: int = 0
    ) -> BotConfig:
        """
        Intelligently select the best bot for the job.
        
        Strategy:
        - High complexity + large data → Premium (DeepSeek)
        - Quick replies needed → Groq (cheap, fast)
        - Balanced → OpenRouter free tier
        """
        # High complexity tasks need reasoning models
        if complexity == "high" or task in [TaskType.DEEP_ANALYSIS, TaskType.JUDGMENT]:
            return BotArsenal.DEEPSEEK_REASONER
        
        # Urgent tasks need speed
        if urgency == "urgent" or task == TaskType.QUICK_CHAT:
            return BotArsenal.GROQ_LLAMA
        
        # Large data processing
        if data_size > 50000:  # 50KB+
            return BotArsenal.OPENROUTER_LLAMA
        
        # Code generation
        if task == TaskType.CODE_GENERATION:
            return BotArsenal.DEEPSEEK_CHAT
        
        # Default to balanced option
        return BotArsenal.OPENROUTER_LLAMA
    
    def track_usage(self, bot: BotConfig):
        """Track API usage for cost monitoring."""
        self.request_count += 1
        self.cost_tracker[bot.cost_tier] += 1
    
    def get_usage_report(self) -> Dict:
        """Get usage statistics."""
        return {
            "total_requests": self.request_count,
            "by_tier": self.cost_tracker,
            "estimated_cost_usd": (
                self.cost_tracker["cheap"] * 0.001 +
                self.cost_tracker["moderate"] * 0.01 +
                self.cost_tracker["expensive"] * 0.1
            )
        }

# === BOT PERSONALITIES ===
BOT_PERSONALITIES = {
    "investigator": {
        "name": "The Investigator",
        "description": "Matter-of-fact online investigator personality",
        "traits": [
            "Direct and to-the-point communication",
            "Always looking for more evidence",
            "Can dialogue naturally without button pressing",
            "Offers solutions proactively",
            "Asks questions politely but persistently",
            "Digs deeper on every lead",
            "Uses reasoning skills to find solutions",
            "Digs multiple layers of wallets deep",
            "Always finds a way to get the answer",
            "Self-healing and self-learning",
            "Daily reset for security (no dangerous persistence)"
        ],
        "system_prompt": """You are The Investigator, a forensic blockchain analyst with a matter-of-fact personality.

Your traits:
- Direct and to-the-point - no fluff
- Always looking for more evidence, never satisfied with surface-level
- Can dialogue naturally, ask follow-up questions without being prompted
- Offer solutions proactively, don't wait to be asked
- Ask questions politely but dig persistently
- Use reasoning skills to connect dots others miss
- Dig multiple layers deep into wallet connections
- Always find a way to get the answer if it exists
- Self-healing: if you make a mistake, acknowledge and correct immediately
- Self-learning: improve from each interaction
- Security-first: no dangerous persistence, daily reset

When analyzing:
1. Always write full wallet addresses
2. Distinguish between verified and suspected connections
3. Cite evidence for every claim
4. Flag anything that needs verification
5. Look for KYC vectors and real-world identities
6. Map money flows precisely
7. Identify patterns of manipulation

You are investigating the CRM token scam (Aug 2025 - Mar 2026).
Target CA: Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS
Key suspect wallets are in your database.

Respond like a professional investigator: factual, thorough, relentless."""
    }
}

# === EXPORT FUNCTIONS ===
def get_investigator_config() -> Dict:
    """Get complete Investigator bot configuration."""
    return {
        "bot": BotArsenal.INVESTIGATOR_BOT,
        "personality": BOT_PERSONALITIES["investigator"],
        "model_config": {
            "temperature": 0.3,  # Low for factual analysis
            "max_tokens": 8000,
            "top_p": 0.9,
        }
    }

def get_quick_reply_config() -> Dict:
    """Get configuration for quick Telegram replies."""
    return {
        "bot": BotArsenal.GROQ_LLAMA,
        "model_config": {
            "temperature": 0.5,
            "max_tokens": 1000,
        }
    }

if __name__ == "__main__":
    # Print bot arsenal overview
    print("=" * 70)
    print("OMEGA FORENSIC V5 - BOT ARSENAL")
    print("=" * 70)
    
    print("\n📋 AVAILABLE BOTS:")
    print("-" * 70)
    for bot in BotArsenal.get_all_bots():
        print(f"\n🔹 {bot.name}")
        print(f"   Provider: {bot.provider}")
        print(f"   Cost Tier: {bot.cost_tier}")
        print(f"   Context: {bot.context_window:,} tokens")
        print(f"   Speed: {bot.speed}")
        print(f"   Best For: {', '.join(t.value for t in bot.best_for)}")
    
    print("\n" + "=" * 70)
    print("TASK ASSIGNMENTS:")
    print("=" * 70)
    for task in TaskType:
        bot = BotArsenal.get_bot_for_task(task)
        print(f"  {task.value:20} → {bot.name}")
    
    print("\n" + "=" * 70)
