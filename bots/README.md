# 🤖 RMI Bot Ecosystem - Grouped with Tools

Complete bot ecosystem integrated with RMI tools.

## 📁 Directory Structure

```
rmi/bots/
├── README.md                   # This file
├── integration.py              # Bot-to-tools integration layer
│
├── production/                 # Core production bot
│   └── rugmuncher_bot_production.py
│
├── extensions/                 # Bot capability extensions
│   ├── rugmuncher_advanced_apis.py    # Advanced API integrations
│   ├── rugmuncher_ai_router.py        # AI model routing
│   ├── rugmuncher_alert_router.py     # Alert management
│   ├── rugmuncher_bundling.py         # Wallet bundling detection
│   ├── rugmuncher_data_cleansing.py   # Data cleaning
│   ├── rugmuncher_data_sanitizer.py  # Data sanitization
│   ├── rugmuncher_features.py         # Feature flags
│   ├── rugmuncher_holders.py         # Holder analysis
│   ├── rugmuncher_ollama_addon.py    # Ollama integration
│   ├── rugmuncher_predictor.py       # ML prediction models
│   ├── rugmuncher_protector.py       # Security protection
│   ├── rugmuncher_scoring.py         # Token scoring
│   ├── rugmuncher_security_hardening.py  # Security hardening
│   ├── rugmuncher_setup.py           # Setup utilities
│   ├── rugmuncher_subscription.py    # Subscription management
│   ├── rugmuncher_telegram_bridge.py # Telegram bridge
│   ├── rugmuncher_threat_intel.py    # Threat intelligence
│   ├── rugmuncher_tor_proxy.py      # Tor proxy
│   ├── rugmuncher_twitter.py        # Twitter integration
│   ├── rugmuncher_vampire.py        # Vampire attack detection
│   ├── rugmuncher_voiceprint.py     # Voice analysis
│   └── rugmuncher_webhook.py        # Webhook handlers
│
├── telegram/                   # Telegram-specific bot
│   ├── main.py
│   ├── chart_manager.py
│   ├── chart_service.py
│   ├── chart_visualizer.py
│   ├── wallet_analyzer.py
│   ├── demo_chart.py
│   ├── handlers/
│   ├── keyboards/
│   └── charts/
│
└── discord/                    # Discord bot (placeholder)
    └── __init__.py
```

## 🔗 Integration Layer

The `integration.py` module provides unified access to all RMI tools:

```python
from rmi.bots.integration import get_connector, get_osint, get_ai, get_blockchain

# Get connector
connector = get_connector()

# Use OSINT tools
osint = get_osint()
osint.search_username("target_user")
osint.analyze_face("/path/to/image.jpg")

# Use AI tools
ai = get_ai()
ai.kimi_query("Analyze this token contract")

# Use blockchain tools
blockchain = get_blockchain()
blockchain.detect_bundling("token_address")
blockchain.score_token("token_address")
```

## 🛠️ Available Tools by Category

### OSINT Tools
| Tool | Description | Location |
|------|-------------|----------|
| maigret | Username search across platforms | rmi/tools/maigret/ |
| munchscan | Deep scanning & facial recognition | rmi/tools/munchscan/ |
| deepface | Facial recognition | rmi/tools/deepface/ |
| social_analyzer | Social media analysis | rmi/tools/social_analyzer/ |
| osint_tools.py | RMI OSINT integration | rmi/integrations/ |

### AI Tools
| Tool | Description | Location |
|------|-------------|----------|
| kimi_cli | Kimi AI integration | rmi/integrations/ai_tools/ |
| opencode | OpenCode AI integration | rmi/integrations/ai_tools/ |

### Blockchain Tools (Bot Extensions)
| Tool | Description | Module |
|------|-------------|--------|
| bundling | Wallet bundling detection | rugmuncher_bundling |
| scoring | Token safety scoring | rugmuncher_scoring |
| predictor | ML token prediction | rugmuncher_predictor |
| threat_intel | Threat intelligence | rugmuncher_threat_intel |
| holders | Holder analysis | rugmuncher_holders |
| vampire | Vampire attack detection | rugmuncher_vampire |

## 🚀 Usage Examples

### Production Bot with Tools
```python
from rmi.bots.production.rugmuncher_bot_production import RugMuncherBot
from rmi.bots.integration import get_blockchain, get_osint

bot = RugMuncherBot()
blockchain = get_blockchain()
osint = get_osint()

# Analyze token
score = blockchain.score_token(token_address)
bot.send_alert(f"Token Score: {score}")
```

### Swarm with Tools
```python
from rmi.swarm.ai_swarm_orchestrator import SwarmOrchestrator
from rmi.bots.integration import get_connector

swarm = SwarmOrchestrator()
connector = get_connector()

# Register tools with swarm
for tool in connector.get_tools_for_bot("swarm"):
    swarm.register_tool(tool.name, tool)
```

## 📊 Bot Types & Recommended Tools

| Bot Type | Recommended Tools |
|----------|-------------------|
| production | blockchain, analysis, security |
| telegram | osint, blockchain, social |
| osint | osint, ai, security |
| swarm | ai, analysis, osint |

## 🔧 Configuration

Tools can be configured via the integration layer:

```python
from rmi.bots.integration import ToolRegistry, Tool, ToolCategory

# Register custom tool
registry = ToolRegistry()
registry.register(Tool(
    name="custom_tool",
    category=ToolCategory.ANALYSIS,
    module_path="my_module.tool",
    class_name="MyToolClass",
    config={"api_key": "xxx"}
))
```

## 📝 Summary

- **24 Bot Extensions** - Full feature set
- **6 Swarm Modules** - Distributed orchestration
- **4 OSINT Tools** - Social/deep analysis
- **2 AI Integrations** - Kimi, OpenCode
- **1 Integration Layer** - Unified interface

All bots now have direct access to the complete RMI tools stack.
