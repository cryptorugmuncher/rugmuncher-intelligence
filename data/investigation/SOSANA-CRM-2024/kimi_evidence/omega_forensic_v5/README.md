# RMI - RugMunch Intelligence Platform

A comprehensive crypto fraud investigation platform built for the CRM token case, expandable to any scam investigation.

## 🎯 Mission

**Bust scammers with evidence-based investigations.**

- Evidence-based only - all claims verified on-chain
- Presumption of innocence until proven
- Transparent methodology and corrections
- Full disclosure of APIs, models, and methods used

## 🌐 Access

- **Web App:** https://intel.cryptorugmunch.com
- **Telegram Bot:** @RugMunchIntelBot
- **API:** https://intel.cryptorugmunch.com/api/

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repo>
cd omega_forensic_v5

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.template .env
# Edit .env with your API keys

# Start services
python main.py web      # Web server
python main.py telegram # Telegram bot
python main.py both     # Both services

# Generate report
python main.py report
```

## 📁 Project Structure

```
omega_forensic_v5/
├── bots/                   # Bot implementations
│   ├── rmi_bot.py         # RMI Bot - Polite crypto investigator
│   └── investigator_bot.py # Deep investigation bot
│
├── config/                 # Configuration
│   ├── api_keys.py        # API key management
│   ├── optimal_bots.py    # Bot configurations
│   └── local_llm_config.py # Local LLM recommendations
│
├── core/                   # Core systems
│   ├── llm_rotation.py    # Free tier LLM rotation
│   ├── intelligent_switcher.py # Model selection
│   └── data_processor.py  # Data processing pipeline
│
├── forensic/              # Forensic tools
│   ├── api_arsenal.py     # 11 API integrations
│   ├── wallet_clustering.py # Wallet cluster detection
│   ├── wallet_database.py # 200+ wallet database
│   ├── bubble_map_visualizer.py # Interactive visualizations
│   ├── cross_token_tracker.py # Cross-project tracking
│   ├── prebond_mapper.py  # Pre-bonding analysis
│   ├── closed_account_tracker.py # Closed account analysis
│   └── final_report_generator.py # Legal-ready reports
│
├── telegram/              # Telegram integration
│   └── bot_handler.py     # Telegram bot handler
│
├── web/                   # Web application
│   ├── app.py            # Flask backend
│   └── static/           # Static assets
│
├── data/                  # Data storage
│   └── wallet_intelligence/ # Wallet evidence
│
├── deploy/                # Deployment
│   └── setup_server.sh   # Server setup script
│
└── main.py               # Entry point
```

## 🤖 RMI Bot

Your polite crypto investigator for Telegram and web.

### Personality
- Polite and respectful in all interactions
- Matter-of-fact and evidence-based
- Thorough but concise
- Always cites sources
- Never makes accusations without proof

### Commands
```
/investigate <wallet>  - Deep wallet analysis
/cluster <wallet>      - Find wallet clusters
/bubble <wallet>       - Generate bubble map
/token <address>       - Analyze token
/report                - Generate case report
/status                - Check system status
/methodology           - View our methodology
/help                  - Show all commands
```

## 🕸️ Wallet Clustering

Advanced cluster detection using multiple forensic signals:

1. **Temporal Proximity** - Transactions within 5-minute windows
2. **Common Counterparties** - Shared senders/recipients
3. **Behavioral Patterns** - Similar transaction patterns
4. **Common Funding** - Same funding sources

## 🫧 Bubble Maps

Interactive visualization of wallet relationships:
- Size = Transaction volume
- Color = Wallet type (center/scammer/exchange/unknown)
- Line thickness = Connection strength
- Click to investigate
- Export as PNG/SVG

## 🔄 LLM Rotation

Intelligent free tier optimization across:
- **Groq** - $200 credit (Llama 3.3, Mixtral)
- **Amazon Bedrock** - $200 credit (Nova Pro/Lite)
- **Google AI** - Free tier (Gemini 2.0 Flash)
- **Anthropic** - Limited free (Claude 3 Haiku)
- **OpenRouter** - Free tier access
- **DeepSeek** - Very cheap

Automatically selects best model for task while respecting rate limits.

## 💻 Local LLMs (Optional)

Recommended CPU-friendly models for Contabo VPS:

| Model | Size | RAM | Best For |
|-------|------|-----|----------|
| **Phi-4** | 2.8GB | 6GB | Primary reasoning |
| **Qwen2.5-7B** | 4.5GB | 8GB | Long context |
| **Llama-3.2-3B** | 1.9GB | 4GB | Quick replies |

```bash
# Generate setup script
python main.py llm

# Run setup
chmod +x setup_local_llms.sh
./setup_local_llms.sh
```

## 📊 Evidence Tiers

| Tier | Name | Description |
|------|------|-------------|
| 🟢 | **Direct** | Confirmed on-chain evidence |
| 🟡 | **Strong Correlation** | Multiple sources agree |
| 🟠 | **Suspicious Pattern** | Worth investigating |
| 🔴 | **Indirect** | Circumstantial connection |
| ⚪ | **Unverified** | Needs confirmation |

## 🔌 APIs Used

### Blockchain
- **Helius** - Solana data, transactions, token accounts
- **QuickNode** - RPC access

### Intelligence
- **Arkham** - Entity labeling, wallet attribution
- **MistTrack** - Risk scoring, AML analysis
- **ChainAbuse** - Scam database

### Token Analytics
- **BirdEye** - Token prices, holder data
- **LunarCrush** - Social metrics, sentiment

### AI/LLM
- **Groq** - Fast inference (Llama, Mixtral)
- **DeepSeek** - Reasoning models
- **OpenRouter** - Model aggregation
- **Anthropic** - Claude models
- **Google** - Gemini models

## 📄 Final Reports

Generate comprehensive forensic reports with:
- Named wallets and entities
- KYC vectors
- Evidence tiers for all findings
- Transaction signatures
- Transparent methodology
- Legal disclaimers
- Corrections log

```bash
python main.py report
```

## 🔒 Security

- Firewall (ufw) configured
- Fail2ban for brute force protection
- SSL via Let's Encrypt
- Services under supervisor
- SSH key authentication only

## 🛠️ Server Setup

```bash
# On your Contabo VPS (167.86.116.51)
chmod +x deploy/setup_server.sh
./deploy/setup_server.sh

# Copy code
scp -r omega_forensic_v5/* root@167.86.116.51:/root/rmi-platform/

# Configure environment
ssh root@167.86.116.51
cd /root/rmi-platform
cp .env.template .env
nano .env  # Add API keys

# Start
./start.sh
```

## 📝 Methodology

### Principles
1. **Evidence-Based Only** - All claims verified with on-chain data
2. **Presumption of Innocence** - Never assume guilt without proof
3. **Transparent Corrections** - Document when investigations are wrong
4. **Verifiable Claims** - Provide transaction signatures

### Process
1. Collect on-chain data via APIs
2. Cross-reference multiple sources
3. Apply evidence tier classification
4. Generate findings with confidence scores
5. Document methodology and limitations
6. Log corrections transparently

## 🐛 Corrections

When we're wrong, we document it:

```
2024-01-15: Original claim that Wallet X was the deployer was incorrect.
Correction: Wallet X is a holder, not the deployer.
Reason: Misread transaction logs - deployer is Wallet Y.
```

## 📈 Status

```bash
python main.py status
```

Shows:
- API key status
- Component health
- Service status
- Recent activity

## 🤝 Built With

- **Kimi AI** - Primary development
- **Flask** - Web framework
- **python-telegram-bot** - Telegram integration
- **D3.js** - Visualizations
- **llama.cpp** - Local LLM inference

## 📜 License

MIT License - For educational and investigative purposes only.

## ⚠️ Disclaimer

This platform is for **informational and educational purposes only**.

- All parties are presumed innocent until proven guilty
- Evidence tiers indicate confidence, not legal conclusions
- Independent verification recommended
- Not legal advice

## 📞 Contact

- **Web:** https://intel.cryptorugmunch.com
- **Telegram:** @RugMunchIntelBot
- **Case:** CRM Token Investigation (Aug 2025 - Mar 2026)

---

*Built with ❤️ to bust scammers and protect the crypto community.*
