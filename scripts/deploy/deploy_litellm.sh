#!/bin/bash
# Deploy LiteLLM Proxy - Unified interface for 100+ LLM providers
# Replaces complex AI routing with single endpoint

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "═══════════════════════════════════════════════════════════"
echo "  🧠 DEPLOYING LITELLM PROXY"
echo "  Unified LLM API for 100+ Providers"
echo "═══════════════════════════════════════════════════════════"
echo -e "${NC}"

# ═══════════════════════════════════════════════════════════
# STEP 1: Install LiteLLM Python SDK
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${BLUE}STEP 1: Installing LiteLLM...${NC}"

pip install -q litellm litellm[proxy] 2>/dev/null || pip3 install -q litellm litellm[proxy] 2>/dev/null || echo "Installing..."

# Verify installation
if python3 -c "import litellm" 2>/dev/null; then
    echo -e "${GREEN}✅ LiteLLM installed${NC}"
else
    echo -e "${YELLOW}⚠️ Installing with pip...${NC}"
    pip install litellm litellm[proxy] --quiet
fi

# ═══════════════════════════════════════════════════════════
# STEP 2: Create LiteLLM Configuration
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${BLUE}STEP 2: Creating configuration...${NC}"

mkdir -p /root/rmi/litellm

cat > /root/rmi/litellm/config.yaml << 'EOF'
# LiteLLM Configuration for RugMuncher
# Manages 23+ AI providers with unified interface

model_list:
  # ═══════════════════════════════════════════════════════
  # TIER 1: Premium Models (Highest Quality)
  # ═══════════════════════════════════════════════════════
  
  - model_name: gpt-4-turbo
    litellm_params:
      model: openai/gpt-4-turbo-preview
      api_key: os.environ/OPENAI_API_KEY
      rpm: 100
      tpm: 10000
    model_info:
      mode: chat
      base_model: azure/gpt-4
      cost_per_token: 0.00001
      quality: premium
      use_case: critical_analysis

  - model_name: claude-3-opus
    litellm_params:
      model: anthropic/claude-3-opus-20240229
      api_key: os.environ/ANTHROPIC_API_KEY
      rpm: 50
      tpm: 5000
    model_info:
      mode: chat
      cost_per_token: 0.000015
      quality: premium
      use_case: deep_investigation

  - model_name: gemini-pro
    litellm_params:
      model: gemini/gemini-pro
      api_key: os.environ/GEMINI_API_KEY
      rpm: 60
    model_info:
      mode: chat
      cost_per_token: 0.0000005
      quality: high
      use_case: general_analysis

  # ═══════════════════════════════════════════════════════
  # TIER 2: Fast Models (High Throughput)
  # ═══════════════════════════════════════════════════════
  
  - model_name: gpt-3.5-turbo
    litellm_params:
      model: openai/gpt-3.5-turbo
      api_key: os.environ/OPENAI_API_KEY
      rpm: 200
      tpm: 40000
    model_info:
      mode: chat
      cost_per_token: 0.0000005
      quality: good
      use_case: quick_scans

  - model_name: claude-3-sonnet
    litellm_params:
      model: anthropic/claude-3-sonnet-20240229
      api_key: os.environ/ANTHROPIC_API_KEY
      rpm: 100
      tpm: 20000
    model_info:
      mode: chat
      cost_per_token: 0.000003
      quality: high
      use_case: detailed_analysis

  - model_name: command-r
    litellm_params:
      model: cohere/command-r
      api_key: os.environ/COHERE_API_KEY
      rpm: 100
    model_info:
      mode: chat
      cost_per_token: 0.0000005
      quality: good
      use_case: summarization

  # ═══════════════════════════════════════════════════════
  # TIER 3: Budget Models (Cost Effective)
  # ═══════════════════════════════════════════════════════
  
  - model_name: gpt-3.5-turbo-budget
    litellm_params:
      model: openai/gpt-3.5-turbo-0125
      api_key: os.environ/OPENAI_API_KEY
      rpm: 300
      tpm: 60000
    model_info:
      mode: chat
      cost_per_token: 0.00000025
      quality: acceptable
      use_case: batch_processing

  - model_name: llama3-8b
    litellm_params:
      model: ollama/llama3:8b
      api_base: os.environ/OLLAMA_API_BASE
    model_info:
      mode: chat
      cost_per_token: 0
      quality: acceptable
      use_case: local_processing

  # ═══════════════════════════════════════════════════════
  # FALLBACK MODELS
  # ═══════════════════════════════════════════════════════
  
  - model_name: fallback-fast
    litellm_params:
      model: openrouter/openai/gpt-3.5-turbo
      api_key: os.environ/OPENROUTER_API_KEY
    model_info:
      mode: chat
      fallback: true
      cost_per_token: 0.0000005

  - model_name: fallback-premium
    litellm_params:
      model: openrouter/anthropic/claude-3-opus
      api_key: os.environ/OPENROUTER_API_KEY
    model_info:
      mode: chat
      fallback: true
      cost_per_token: 0.000015

# ═══════════════════════════════════════════════════════════
# ROUTER SETTINGS
# ═══════════════════════════════════════════════════════════

router_settings:
  # Routing strategy
  routing_strategy: simple-shuffle
  
  # Retry settings
  num_retries: 3
  timeout: 30
  
  # Cooldown for failed models
  cooldown_time: 300
  
  # Fallback logic
  fallbacks: 
    - gpt-4-turbo: ["claude-3-opus", "fallback-premium"]
    - gpt-3.5-turbo: ["claude-3-sonnet", "command-r", "fallback-fast"]

# ═══════════════════════════════════════════════════════════
# GENERAL SETTINGS
# ═══════════════════════════════════════════════════════════

general_settings:
  # Telemetry
  log_level: info
  
  # Database for logging
  database_url: os.environ/DATABASE_URL
  
  # Proxy settings
  master_key: os.environ/LITELLM_MASTER_KEY
  
  # Alerting
  alerting: ["slack", "webhook"]
  
  # Cache
  cache: true
  cache_type: redis
  cache_host: os.environ/REDIS_HOST
  cache_port: os.environ/REDIS_PORT
  cache_password: os.environ/REDIS_PASSWORD

# ═══════════════════════════════════════════════════════════
# LITELLM SETTINGS
# ═══════════════════════════════════════════════════════════

litellm_settings:
  # Enable caching
  cache: true
  
  # Cache settings
  cache_params:
    type: redis
    host: localhost
    port: 6379
    password: os.environ/REDIS_PASSWORD
  
  # Success/failure callbacks
  success_callback: ["langfuse"]
  failure_callback: ["sentry"]
  
  # Rate limiting
  rate_limit: true
EOF

echo -e "${GREEN}✅ Configuration created${NC}"

# ═══════════════════════════════════════════════════════════
# STEP 3: Create Environment Template
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${BLUE}STEP 3: Creating environment template...${NC}"

cat > /root/rmi/litellm/.env.example << 'EOF'
# LiteLLM Configuration
# Copy to .env and fill in your API keys

# Master key for LiteLLM proxy
LITELLM_MASTER_KEY=sk-rugmuncher-$(openssl rand -hex 16)

# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Google Gemini
GEMINI_API_KEY=...

# Cohere
COHERE_API_KEY=...

# OpenRouter (fallback provider)
OPENROUTER_API_KEY=sk-or-...

# Ollama (local models)
OLLAMA_API_BASE=http://localhost:11434

# Redis (for caching)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# Database (for logging)
DATABASE_URL=postgresql://user:pass@localhost/litellm

# Langfuse (observability)
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
EOF

echo -e "${GREEN}✅ Environment template created${NC}"

# ═══════════════════════════════════════════════════════════
# STEP 4: Create Python Integration
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${BLUE}STEP 4: Creating Python integration...${NC}"

cat > /root/rmi/backend/litellm_router.py << 'PYEOF'
"""
🧠 LiteLLM Router for RugMuncher
Unified interface for 100+ LLM providers
"""

import os
import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

# LiteLLM imports
try:
    import litellm
    from litellm import Router, completion, acompletion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    print("⚠️ LiteLLM not installed. Run: pip install litellm")


class ModelTier(Enum):
    """Model quality tiers"""
    PREMIUM = "premium"      # GPT-4, Claude Opus
    HIGH = "high"            # Claude Sonnet, Gemini Pro
    STANDARD = "standard"    # GPT-3.5, Command-R
    BUDGET = "budget"        # GPT-3.5-turbo-0125
    LOCAL = "local"          # Ollama models


@dataclass
class LLMResponse:
    """Standardized LLM response"""
    content: str
    model: str
    tokens_used: int
    cost: float
    latency_ms: float
    success: bool
    error: Optional[str] = None


class LiteLLMRouter:
    """
    Unified LLM router for RugMuncher
    
    Usage:
        router = LiteLLMRouter()
        response = await router.analyze_wallet(wallet_address, tier=ModelTier.HIGH)
    """
    
    def __init__(self, config_path: Optional[str] = None):
        if not LITELLM_AVAILABLE:
            raise ImportError("LiteLLM not installed")
        
        self.config_path = config_path or "/root/rmi/litellm/config.yaml"
        self.router = None
        self._setup()
    
    def _setup(self):
        """Initialize LiteLLM"""
        # Enable caching (uses Redis if configured)
        litellm.cache = litellm.Cache(
            type="redis",
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD")
        )
        
        # Set callbacks for observability
        litellm.success_callback = [self._log_success]
        litellm.failure_callback = [self._log_failure]
        
        # Initialize router with config
        try:
            self.router = Router(
                model_list=self._load_model_list(),
                routing_strategy="simple-shuffle",
                num_retries=3,
                timeout=30
            )
            print("✅ LiteLLM router initialized")
        except Exception as e:
            print(f"⚠️ Router init warning: {e}")
            self.router = None
    
    def _load_model_list(self) -> List[Dict]:
        """Load model configurations"""
        return [
            # Premium models
            {
                "model_name": "gpt-4-turbo",
                "litellm_params": {
                    "model": "openai/gpt-4-turbo-preview",
                    "api_key": os.getenv("OPENAI_API_KEY"),
                    "rpm": 100,
                    "tpm": 10000
                }
            },
            {
                "model_name": "claude-3-opus",
                "litellm_params": {
                    "model": "anthropic/claude-3-opus-20240229",
                    "api_key": os.getenv("ANTHROPIC_API_KEY"),
                    "rpm": 50
                }
            },
            # High quality models
            {
                "model_name": "claude-3-sonnet",
                "litellm_params": {
                    "model": "anthropic/claude-3-sonnet-20240229",
                    "api_key": os.getenv("ANTHROPIC_API_KEY"),
                    "rpm": 100
                }
            },
            {
                "model_name": "gemini-pro",
                "litellm_params": {
                    "model": "gemini/gemini-pro",
                    "api_key": os.getenv("GEMINI_API_KEY"),
                    "rpm": 60
                }
            },
            # Fast models
            {
                "model_name": "gpt-3.5-turbo",
                "litellm_params": {
                    "model": "openai/gpt-3.5-turbo",
                    "api_key": os.getenv("OPENAI_API_KEY"),
                    "rpm": 200
                }
            },
            {
                "model_name": "command-r",
                "litellm_params": {
                    "model": "cohere/command-r",
                    "api_key": os.getenv("COHERE_API_KEY"),
                    "rpm": 100
                }
            },
            # Fallback
            {
                "model_name": "openrouter-gpt4",
                "litellm_params": {
                    "model": "openrouter/openai/gpt-4-turbo",
                    "api_key": os.getenv("OPENROUTER_API_KEY")
                }
            }
        ]
    
    def _log_success(self, kwargs, response, start_time, end_time):
        """Log successful request"""
        latency = (end_time - start_time).total_seconds() * 1000
        print(f"✅ LLM Success: {kwargs.get('model')} | {latency:.0f}ms | ${kwargs.get('response_cost', 0):.6f}")
    
    def _log_failure(self, kwargs, error, start_time, end_time):
        """Log failed request"""
        print(f"❌ LLM Failed: {kwargs.get('model')} | Error: {error}")
    
    def _get_model_for_tier(self, tier: ModelTier) -> str:
        """Get appropriate model for quality tier"""
        tier_models = {
            ModelTier.PREMIUM: ["gpt-4-turbo", "claude-3-opus"],
            ModelTier.HIGH: ["claude-3-sonnet", "gemini-pro"],
            ModelTier.STANDARD: ["gpt-3.5-turbo", "command-r"],
            ModelTier.BUDGET: ["gpt-3.5-turbo"],
            ModelTier.LOCAL: ["ollama/llama3:8b"]
        }
        models = tier_models.get(tier, tier_models[ModelTier.STANDARD])
        return models[0]  # Return first available
    
    async def complete(self, 
                      messages: List[Dict[str, str]], 
                      model: Optional[str] = None,
                      tier: ModelTier = ModelTier.STANDARD,
                      temperature: float = 0.7,
                      max_tokens: Optional[int] = None,
                      **kwargs) -> LLMResponse:
        """
        Get completion from LLM
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Specific model name (optional)
            tier: Quality tier to use
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            
        Returns:
            LLMResponse with standardized format
        """
        import time
        start_time = time.time()
        
        try:
            # Select model
            selected_model = model or self._get_model_for_tier(tier)
            
            # Make request
            if self.router:
                response = await self.router.acompletion(
                    model=selected_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
            else:
                response = await acompletion(
                    model=selected_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
            
            # Extract response data
            latency = (time.time() - start_time) * 1000
            content = response.choices[0].message.content
            usage = response.usage
            cost = litellm.completion_cost(response)
            
            return LLMResponse(
                content=content,
                model=selected_model,
                tokens_used=usage.total_tokens,
                cost=cost,
                latency_ms=latency,
                success=True
            )
            
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            return LLMResponse(
                content="",
                model=model or str(tier),
                tokens_used=0,
                cost=0,
                latency_ms=latency,
                success=False,
                error=str(e)
            )
    
    async def analyze_wallet(self, 
                            wallet_address: str, 
                            chain: str = "ethereum",
                            tier: ModelTier = ModelTier.HIGH) -> LLMResponse:
        """
        Analyze a wallet address using LLM
        
        Args:
            wallet_address: The wallet to analyze
            chain: Blockchain (ethereum, solana, etc.)
            tier: Quality tier for analysis
        """
        system_prompt = """You are an expert crypto forensics analyst. 
Analyze the provided wallet and identify risk factors.
Return your analysis in JSON format with:
- risk_score (0-100)
- risk_factors (list of strings)
- summary (brief description)
- confidence (0-1)"""
        
        user_prompt = f"Analyze wallet {wallet_address} on {chain}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return await self.complete(messages, tier=tier, temperature=0.3)
    
    async def detect_scam(self, 
                         contract_address: str,
                         token_data: Dict[str, Any],
                         tier: ModelTier = ModelTier.PREMIUM) -> LLMResponse:
        """
        Analyze a token contract for scam indicators
        """
        system_prompt = """You are a crypto scam detection expert.
Analyze the token contract data and identify scam indicators.
Return JSON with:
- is_scam (boolean)
- scam_probability (0-1)
- indicators (list of red flags)
- recommendation (buy/avoid/investigate)"""
        
        user_prompt = f"""Analyze this token contract:
Address: {contract_address}
Data: {token_data}
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return await self.complete(messages, tier=tier, temperature=0.2, max_tokens=1000)
    
    async def generate_report(self,
                             investigation_data: Dict[str, Any],
                             tier: ModelTier = ModelTier.HIGH) -> LLMResponse:
        """
        Generate an investigation report
        """
        system_prompt = """You are a professional crypto investigator.
Generate a detailed investigation report based on the provided data.
Include:
- Executive summary
- Key findings
- Risk assessment
- Recommendations"""
        
        user_prompt = f"Generate report for investigation:\n{investigation_data}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return await self.complete(messages, tier=tier, temperature=0.5, max_tokens=2000)


class LiteLLMProxy:
    """
    LiteLLM Proxy Server wrapper
    Run this to have a unified API endpoint
    """
    
    @staticmethod
    def start_proxy(config_path: str = "/root/rmi/litellm/config.yaml", 
                   port: int = 8000):
        """
        Start the LiteLLM proxy server
        
        Usage:
            LiteLLMProxy.start_proxy()
            
        Then access at: http://localhost:8000
        """
        import subprocess
        
        cmd = [
            "litellm",
            "--config", config_path,
            "--port", str(port),
            "--num_workers", "4"
        ]
        
        print(f"🚀 Starting LiteLLM proxy on port {port}")
        subprocess.Popen(cmd)
        print(f"✅ Proxy started at http://localhost:{port}")


# Simple usage example
async def main():
    """Example usage"""
    router = LiteLLMRouter()
    
    # Analyze a wallet
    response = await router.analyze_wallet(
        wallet_address="0x1234567890abcdef",
        chain="ethereum",
        tier=ModelTier.HIGH
    )
    
    print(f"Response: {response}")


if __name__ == "__main__":
    asyncio.run(main())
PYEOF

echo -e "${GREEN}✅ Python integration created${NC}"

# ═══════════════════════════════════════════════════════════
# STEP 5: Create Docker Compose for Proxy
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${BLUE}STEP 5: Creating Docker setup...${NC}"

cat > /root/rmi/litellm/docker-compose.yml << 'EOF'
version: '3.8'

services:
  litellm-proxy:
    image: ghcr.io/berriai/litellm:main-latest
    container_name: litellm-proxy
    ports:
      - "8000:8000"
    volumes:
      - ./config.yaml:/app/config.yaml
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - COHERE_API_KEY=${COHERE_API_KEY}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - REDIS_HOST=${REDIS_HOST:-dragonfly}
      - REDIS_PORT=${REDIS_PORT:-6379}
      - REDIS_PASSWORD=${REDIS_PASSWORD}
      - LITELLM_MASTER_KEY=${LITELLM_MASTER_KEY}
    command: >
      --config /app/config.yaml
      --port 8000
      --num_workers 4
    restart: unless-stopped
    networks:
      - rmi_network

networks:
  rmi_network:
    external: true
EOF

echo -e "${GREEN}✅ Docker Compose created${NC}"

# ═══════════════════════════════════════════════════════════
# STEP 6: Create Helper Scripts
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${BLUE}STEP 6: Creating helper scripts...${NC}"

cat > /usr/local/bin/rmi-litellm << 'EOF'
#!/bin/bash
# LiteLLM helper

case "$1" in
  start)
    echo "🚀 Starting LiteLLM proxy..."
    cd /root/rmi/litellm
    docker-compose up -d
    echo "✅ Proxy started at http://localhost:8000"
    ;;
  stop)
    echo "🛑 Stopping LiteLLM proxy..."
    cd /root/rmi/litellm
    docker-compose down
    ;;
  status)
    docker ps | grep litellm-proxy || echo "LiteLLM proxy not running"
    ;;
  logs)
    docker logs litellm-proxy --tail 50
    ;;
  test)
    echo "Testing LiteLLM proxy..."
    curl -X POST http://localhost:8000/v1/chat/completions \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
      -d '{
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hello"}]
      }' 2>/dev/null | head -20 || echo "Proxy not responding"
    ;;
  *)
    echo "Usage: rmi-litellm [start|stop|status|logs|test]"
    ;;
esac
EOF
chmod +x /usr/local/bin/rmi-litellm

# ═══════════════════════════════════════════════════════════
# STEP 7: Update Main Bot Integration
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${BLUE}STEP 7: Updating bot integration...${NC}"

cat > /root/rmi/backend/ai_router_litellm.py << 'PYEOF'
"""
🧠 AI Router using LiteLLM
Replaces complex multi-provider routing with unified interface
"""

import os
from typing import Optional, Dict, Any
from litellm_router import LiteLLMRouter, ModelTier, LLMResponse

class AIRouter:
    """
    Unified AI Router for RugMuncher
    Uses LiteLLM for 100+ provider support
    """
    
    def __init__(self):
        self.router = LiteLLMRouter()
        self.cache_enabled = True
    
    async def analyze_wallet(self, 
                            wallet_address: str, 
                            chain: str = "ethereum",
                            analysis_depth: str = "standard") -> Dict[str, Any]:
        """
        Analyze wallet using LLM
        
        Args:
            wallet_address: Wallet to analyze
            chain: Blockchain type
            analysis_depth: 'quick', 'standard', or 'deep'
        """
        # Map depth to quality tier
        tier_map = {
            'quick': ModelTier.BUDGET,
            'standard': ModelTier.HIGH,
            'deep': ModelTier.PREMIUM
        }
        tier = tier_map.get(analysis_depth, ModelTier.STANDARD)
        
        # Get analysis from LLM
        response = await self.router.analyze_wallet(
            wallet_address=wallet_address,
            chain=chain,
            tier=tier
        )
        
        if not response.success:
            return {
                'success': False,
                'error': response.error,
                'wallet': wallet_address
            }
        
        # Parse JSON response
        try:
            import json
            analysis = json.loads(response.content)
            analysis['success'] = True
            analysis['model_used'] = response.model
            analysis['cost'] = response.cost
            analysis['latency_ms'] = response.latency_ms
            return analysis
        except json.JSONDecodeError:
            return {
                'success': True,
                'raw_response': response.content,
                'model_used': response.model,
                'cost': response.cost
            }
    
    async def detect_scam(self,
                         contract_address: str,
                         token_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect if token is a scam"""
        response = await self.router.detect_scam(
            contract_address=contract_address,
            token_data=token_data,
            tier=ModelTier.PREMIUM
        )
        
        if not response.success:
            return {'success': False, 'error': response.error}
        
        try:
            import json
            result = json.loads(response.content)
            result['success'] = True
            return result
        except:
            return {
                'success': True,
                'raw_response': response.content,
                'is_scam': 'scam' in response.content.lower()
            }
    
    async def generate_investigation_report(self,
                                           investigation_data: Dict[str, Any]) -> str:
        """Generate detailed report"""
        response = await self.router.generate_report(
            investigation_data=investigation_data,
            tier=ModelTier.HIGH
        )
        
        if response.success:
            return response.content
        return f"Error generating report: {response.error}"


# Singleton instance
_ai_router = None

def get_ai_router() -> AIRouter:
    """Get or create AI router singleton"""
    global _ai_router
    if _ai_router is None:
        _ai_router = AIRouter()
    return _ai_router
PYEOF

echo -e "${GREEN}✅ Bot integration updated${NC}"

# ═══════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════"
echo "  ✅ LITELLM DEPLOYMENT COMPLETE!"
echo "═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}🧠 LiteLLM is installed and ready${NC}"
echo ""
echo -e "${BLUE}📁 Files Created:${NC}"
echo "   /root/rmi/litellm/config.yaml              - Provider config"
echo "   /root/rmi/litellm/.env.example             - Environment template"
echo "   /root/rmi/litellm/docker-compose.yml       - Docker setup"
echo "   /root/rmi/backend/litellm_router.py        - Python SDK"
echo "   /root/rmi/backend/ai_router_litellm.py     - Bot integration"
echo ""
echo -e "${BLUE}🔧 Commands:${NC}"
echo "   rmi-litellm start    - Start proxy server"
echo "   rmi-litellm stop     - Stop proxy server"
echo "   rmi-litellm test     - Test connection"
echo ""
echo -e "${BLUE}🚀 To Start:${NC}"
echo "   1. Copy and edit environment:"
echo "      cp /root/rmi/litellm/.env.example /root/rmi/litellm/.env"
echo "      nano /root/rmi/litellm/.env"
echo ""
echo "   2. Start proxy:"
echo "      rmi-litellm start"
echo ""
echo "   3. Use in bot:"
echo "      from ai_router_litellm import get_ai_router"
echo "      router = get_ai_router()"
echo "      result = await router.analyze_wallet('0x123...')"
echo ""
echo -e "${YELLOW}💡 Key Features:${NC}"
echo "   ✓ Unified API for 100+ LLM providers"
echo "   ✓ Automatic failover between providers"
echo "   ✓ Redis caching integration"
echo "   ✓ Cost tracking and optimization"
echo "   ✓ Rate limiting per provider"
echo "   ✓ Load balancing across models"
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
