"""
RMI - RugMunch Intelligence Platform
=====================================
Main entry point for the crypto fraud investigation platform.

Usage:
    python main.py web          # Start web server
    python main.py telegram     # Start Telegram bot
    python main.py both         # Start both
    python main.py report       # Generate CRM report
    python main.py setup        # Show setup instructions
"""

import sys
import os

# Add to path
sys.path.insert(0, '/mnt/okcomputer/output/omega_forensic_v5')

from forensic.final_report_generator import get_final_report_generator, WalletEvidence, EvidenceTier
from forensic.wallet_clustering import get_clustering_engine
from config.local_llm_config import print_recommendations, generate_setup_script


def print_banner():
    """Print the RMI banner."""
    print("""
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                                                                       ║
    ║   ██████╗ ███╗   ███╗██╗    ██████╗ ██╗   ██╗ ██████╗ ██████╗        ║
    ║   ██╔══██╗████╗ ████║██║    ██╔══██╗██║   ██║██╔════╝██╔════╝        ║
    ║   ██████╔╝██╔████╔██║██║    ██████╔╝██║   ██║██║     ██║  ███╗       ║
    ║   ██╔══██╗██║╚██╔╝██║██║    ██╔══██╗██║   ██║██║     ██║   ██║       ║
    ║   ██║  ██║██║ ╚═╝ ██║██║    ██║  ██║╚██████╔╝╚██████╗╚██████╔╝       ║
    ║   ╚═╝  ╚═╝╚═╝     ╚═╝╚═╝    ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═════╝        ║
    ║                                                                       ║
    ║        RugMunch Intelligence - Crypto Fraud Investigation             ║
    ║                                                                       ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    """)


def start_web_server():
    """Start the web server."""
    print("\n🌐 Starting Web Server...")
    from web.app import run_server
    run_server(host='0.0.0.0', port=5000, debug=False)


def start_telegram_bot():
    """Start the Telegram bot."""
    print("\n🤖 Starting Telegram Bot...")
    from telegram.bot_handler import run_bot_sync
    run_bot_sync()


def generate_report():
    """Generate the CRM investigation report."""
    print("\n📄 Generating CRM Investigation Report...")
    
    generator = get_final_report_generator()
    
    # Create sample evidence for CRM case
    sample_wallets = [
        WalletEvidence(
            address="Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS",
            entity_name="CRM Token Deployer",
            evidence_tier=EvidenceTier.DIRECT,
            findings=[
                "Token contract deployer",
                "Controls 20.4% of total supply (204M CRM)",
                "Pre-bonding manipulation detected",
                "Botnet commander wallet identified"
            ],
            transaction_signatures=[
                "SampleSignature1...",
                "SampleSignature2..."
            ],
            connected_wallets=[
                "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
                "5xot9PVkphiX2adznhKBAD7BqCjT5pRSfh5s4nBw7Z8V"
            ],
            risk_score=0.95,
            total_volume=5000000.0,
            transaction_count=1500
        ),
        WalletEvidence(
            address="AFXigaYu...",
            entity_name="Botnet Commander",
            evidence_tier=EvidenceTier.STRONG_CORRELATION,
            findings=[
                "Controls 970-wallet botnet",
                "Coordinated buy/sell signals",
                "Pre-bonding manipulation"
            ],
            risk_score=0.98,
            total_volume=2500000.0,
            transaction_count=3000
        )
    ]
    
    report = generator.create_crm_report(wallet_evidence=sample_wallets)
    
    # Export
    md_path = generator.export_report(report.report_id, "markdown")
    json_path = generator.export_report(report.report_id, "json")
    
    print(f"\n✅ Report Generated!")
    print(f"   Report ID: {report.report_id}")
    print(f"   Markdown: {md_path}")
    print(f"   JSON: {json_path}")
    
    # Print summary
    summary = generator.get_report_summary(report.report_id)
    print(f"\n📊 Report Summary:")
    for key, value in summary.items():
        print(f"   {key}: {value}")


def show_setup():
    """Show setup instructions."""
    print("\n" + "=" * 70)
    print("RMI SETUP INSTRUCTIONS")
    print("=" * 70)
    
    print("""
## 1. Environment Setup

Create a .env file with your API keys:

```bash
# Blockchain APIs
HELIUS_API_KEY=your_key
QUICKNODE_URL=your_url
ARKHAM_API_KEY=your_key

# Risk/OSINT APIs
MISTTRACK_API_KEY=your_key
CHAINABUSE_API_KEY=your_key

# Token APIs
BIRDEYE_API_KEY=your_key
LUNARCRUSH_API_KEY=your_key

# AI APIs
GROQ_API_KEY=your_key
DEEPSEEK_API_KEY=your_key
OPENROUTER_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
GOOGLE_API_KEY=your_key

# AWS (for Bedrock)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# Telegram
TELEGRAM_BOT_TOKEN=your_token

# Server
DOMAIN=intel.cryptorugmunch.com
```

## 2. Install Dependencies

```bash
pip install flask flask-cors python-telegram-bot aiohttp
```

## 3. Local LLM Setup (Optional)

For CPU-friendly local models:
""")
    
    print_recommendations()
    
    print("""
## 4. Start Services

```bash
# Web server only
python main.py web

# Telegram bot only
python main.py telegram

# Both
python main.py both

# Generate report
python main.py report
```

## 5. Access

- Web App: http://your-server:5000
- API: http://your-server:5000/api/
- Telegram: @RugMunchIntelBot

## 6. Directory Structure

```
omega_forensic_v5/
├── bots/           # RMI Bot, Investigator Bot
├── config/         # API keys, LLM config
├── core/           # LLM rotation, data processor
├── forensic/       # API arsenal, clustering, reports
├── telegram/       # Telegram bot handler
├── web/            # Flask app, visualizations
├── data/           # Wallet database, evidence
└── main.py         # Entry point
```
""")


def show_status():
    """Show system status."""
    print("\n📊 RMI System Status")
    print("=" * 50)
    
    # Check API keys
    apis = {
        "HELIUS_API_KEY": "Helius (Solana)",
        "GROQ_API_KEY": "Groq (AI)",
        "DEEPSEEK_API_KEY": "DeepSeek (AI)",
        "TELEGRAM_BOT_TOKEN": "Telegram Bot",
        "ARKHAM_API_KEY": "Arkham Intelligence"
    }
    
    print("\n🔑 API Keys:")
    for env_var, name in apis.items():
        status = "✅" if os.getenv(env_var) else "❌"
        print(f"   {status} {name}")
    
    print("\n🤖 Components:")
    print("   ✅ RMI Bot - Polite crypto investigator")
    print("   ✅ Wallet Clustering - Multi-signal detection")
    print("   ✅ Bubble Maps - Interactive visualization")
    print("   ✅ LLM Rotation - Free tier optimization")
    print("   ✅ Report Generator - Legal-ready reports")
    
    print("\n📡 Services:")
    print("   🟡 Web Server - Ready to start")
    print("   🟡 Telegram Bot - Ready to start")
    
    print("\n" + "=" * 50)


def main():
    """Main entry point."""
    print_banner()
    
    if len(sys.argv) < 2:
        print("""
Usage: python main.py <command>

Commands:
    web         Start web server
    telegram    Start Telegram bot
    both        Start both services
    report      Generate CRM report
    setup       Show setup instructions
    status      Show system status
    llm         Show LLM recommendations

Examples:
    python main.py web
    python main.py telegram
    python main.py report
""")
        return
    
    command = sys.argv[1].lower()
    
    if command == "web":
        start_web_server()
    elif command == "telegram":
        start_telegram_bot()
    elif command == "both":
        import threading
        
        # Start web server in thread
        web_thread = threading.Thread(target=start_web_server)
        web_thread.daemon = True
        web_thread.start()
        
        # Start Telegram bot in main thread
        start_telegram_bot()
    elif command == "report":
        generate_report()
    elif command == "setup":
        show_setup()
    elif command == "status":
        show_status()
    elif command == "llm":
        print_recommendations()
        
        # Generate setup script
        script = generate_setup_script(ram_gb=8, cpu_cores=4)
        script_path = "/mnt/okcomputer/output/omega_forensic_v5/setup_local_llms.sh"
        with open(script_path, 'w') as f:
            f.write(script)
        print(f"\n📝 Setup script saved to: {script_path}")
    else:
        print(f"Unknown command: {command}")
        print("Run 'python main.py' for usage information.")


if __name__ == "__main__":
    main()
