#!/usr/bin/env python3
"""
Bot Autonomous Infrastructure - Usage Examples
Self-provisioning webhooks and bot-to-bot code sharing
"""

import asyncio
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot_autonomous_infrastructure import (
    BotCollaborationNetwork,
    AutonomousBotSwarm,
    HeliusProvisioner,
    CodeInterpreter,
    BOT_TEMPLATES,
    CodeArtifact
)
from datetime import datetime
import hashlib

async def example_1_spawn_monitoring_bot():
    """Example: Spawn a monitoring bot that provisions its own Helius webhook"""
    
    print("="*70)
    print("EXAMPLE 1: Spawn Autonomous Monitoring Bot")
    print("="*70)
    
    swarm = AutonomousBotSwarm()
    
    # Wallets to monitor (CRM case wallets)
    wallets = [
        "AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6",  # Tier 1 root
        "8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj",  # Tier 4 distribution
        "7abBmGf4HNu3UXsanJc7WwAPW2PgkEb9hwrFKwCySvyL",  # Victim whale
    ]
    
    # Credentials (from environment in production)
    credentials = {
        "api_key": "your-helius-api-key-here",
        "webhook_url": "https://your-server.com/webhooks/crm-monitor"
    }
    
    # Spawn bot - it provisions its own infrastructure
    bot_id = await swarm.spawn_monitoring_bot(
        name="CRM Case Monitor",
        wallets=wallets,
        credentials=credentials
    )
    
    print(f"\nBot spawned: {bot_id}")
    print("Bot self-provisioned:")
    print("  - Helius webhook for account/transaction monitoring")
    print("  - Wallet monitoring code (auto-shared)")
    print("  - Alert threshold configuration")
    
    return bot_id


async def example_2_bot_code_sharing():
    """Example: Bot shares code with another bot"""
    
    print("\n" + "="*70)
    print("EXAMPLE 2: Bot-to-Bot Code Sharing")
    print("="*70)
    
    network = BotCollaborationNetwork()
    
    # Register bots
    analysis_bot = network.register_bot(
        bot_id="analysis_bot_001",
        name="Transaction Analyzer",
        capabilities=["transaction_analysis", "pattern_detection"],
        trusted_bots=["monitor_bot_001", "alert_bot_001"]
    )
    
    monitor_bot = network.register_bot(
        bot_id="monitor_bot_001",
        name="Wallet Monitor",
        capabilities=["wallet_monitor", "alert"],
        trusted_bots=["analysis_bot_001"]
    )
    
    # Analysis bot creates and shares code
    analysis_code = '''
import json

def detect_wash_trading(transactions):
    """Detect wash trading patterns"""
    suspicious = []
    for tx in transactions:
        if tx.get("from") == tx.get("to"):
            suspicious.append({
                "type": "self_trade",
                "tx": tx["hash"],
                "amount": tx["amount"]
            })
    return suspicious

# Run analysis
result = detect_wash_trading(__CONTEXT__.get("transactions", []))
print(json.dumps(result))
'''
    
    # Share code from analysis_bot to monitor_bot
    artifact = await network.share_code(
        source_bot="analysis_bot_001",
        code=analysis_code,
        description="Wash trading detection algorithm",
        target_bot="monitor_bot_001",
        dependencies=["json"]
    )
    
    print(f"\nCode shared: {artifact.id}")
    print(f"Language detected: {artifact.language.value}")
    print(f"Hash: {artifact.hash[:16]}...")
    
    # Monitor bot executes the shared code
    test_transactions = [
        {"hash": "tx1", "from": "A", "to": "B", "amount": 1000},
        {"hash": "tx2", "from": "C", "to": "C", "amount": 5000},  # Self-trade
    ]
    
    result = await network.execute_shared_code(
        bot_id="monitor_bot_001",
        artifact_id=artifact.id,
        context={"transactions": test_transactions}
    )
    
    print(f"\nExecution result:")
    print(f"  Success: {result['success']}")
    print(f"  Output: {result.get('output', 'N/A')}")
    
    return artifact


async def example_3_auto_language_detection():
    """Example: Auto-detect code language and execute"""
    
    print("\n" + "="*70)
    print("EXAMPLE 3: Auto Language Detection")
    print("="*70)
    
    interpreter = CodeInterpreter()
    
    # Various code samples
    code_samples = [
        ("python", '''
def calculate_risk(wallet_data):
    risk_score = 0
    if wallet_data.get("tx_count", 0) > 1000:
        risk_score += 50
    return risk_score

print(calculate_risk({"tx_count": 1500}))
'''),
        ("javascript", '''
const analyzeVolume = (txs) => {
    return txs.reduce((sum, tx) => sum + tx.amount, 0);
};
console.log(analyzeVolume([{amount: 100}, {amount: 200}]));
'''),
        ("typescript", '''
interface Wallet {
    address: string;
    balance: number;
}
const getBalance = (w: Wallet): number => w.balance;
console.log(getBalance({address: "abc", balance: 1000}));
''')
    ]
    
    for expected_lang, code in code_samples:
        detected = interpreter.detect_language(code)
        status = "✅" if detected.value == expected_lang else "❌"
        print(f"{status} Expected: {expected_lang}, Detected: {detected.value}")


async def example_4_self_provisioned_webhook():
    """Example: Bot provisions its own webhook infrastructure"""
    
    print("\n" + "="*70)
    print("EXAMPLE 4: Self-Provisioned Webhook")
    print("="*70)
    
    network = BotCollaborationNetwork()
    
    # Register a bot
    bot = network.register_bot(
        bot_id="forensic_bot_001",
        name="Forensic Analysis Bot",
        capabilities=["blockchain_analysis", "pattern_detection", "webhook_management"],
        trusted_bots=["master_bot"]
    )
    
    # Bot provisions its own Helius webhook
    # (In production, this uses real Helius API)
    print("\nBot requesting webhook provisioning...")
    print("  Provider: Helius")
    print("  Event types: account, transaction, program")
    print("  Accounts: 42 CRM case wallets")
    
    # Simulated result (would be actual API call)
    print("\n✅ Webhook provisioned successfully!")
    print("  Webhook ID: helius_wh_12345")
    print("  Endpoint: https://rmi-platform.com/webhooks/forensic_bot_001")
    print("  Status: Active")
    print("  Bot can now receive real-time blockchain events")


async def example_5_prebuilt_templates():
    """Example: Use pre-built bot code templates"""
    
    print("\n" + "="*70)
    print("EXAMPLE 5: Pre-Built Bot Templates")
    print("="*70)
    
    interpreter = CodeInterpreter()
    
    print("\nAvailable templates:")
    for name, code in BOT_TEMPLATES.items():
        lines = code.strip().split('\n')
        print(f"  - {name}: {len(lines)} lines")
    
    # Execute wallet_monitor template
    print("\nExecuting 'wallet_monitor' template...")
    
    code = BOT_TEMPLATES["wallet_monitor"]
    
    artifact = CodeArtifact(
        id=f"template_test_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        source_bot="template_library",
        target_bot=None,
        language=interpreter.detect_language(code),
        code=code,
        description="Wallet monitoring template",
        dependencies=["asyncio", "json"],
        hash=hashlib.sha256(code.encode()).hexdigest(),
        created_at=datetime.now(),
        executed_count=0,
        execution_results=[]
    )
    
    result = await interpreter.execute_code(
        artifact,
        context={"wallets": ["wallet1", "wallet2"], "threshold": 1000}
    )
    
    print(f"\nTemplate execution:")
    print(f"  Success: {result['success']}")
    if result['success']:
        print(f"  Output: {result['output'][:200]}...")


async def main():
    """Run all examples"""
    
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║     RMI BOT AUTONOMOUS INFRASTRUCTURE - USAGE EXAMPLES               ║
║                                                                      ║
║  Self-provisioning webhooks • Bot-to-bot code sharing               ║
║  Auto language detection • Pre-built templates                       ║
╚══════════════════════════════════════════════════════════════════════╝
""")
    
    # Run examples (some are simulated without real API keys)
    await example_3_auto_language_detection()
    await example_2_bot_code_sharing()
    await example_4_self_provisioned_webhook()
    await example_5_prebuilt_templates()
    
    print("\n" + "="*70)
    print("EXAMPLES COMPLETE")
    print("="*70)
    print("""
To use in production:

1. Set environment variables:
   export HELIUS_API_KEY="your-key"
   export SUPABASE_URL="your-url"
   export SUPABASE_KEY="your-key"

2. Spawn autonomous bots:
   python -m evidence_integration.bot_autonomous_infrastructure \\
       --spawn-bot "CRM Monitor" \\
       --wallets "addr1,addr2,addr3" \\
       --helius-key "$HELIUS_API_KEY"

3. Bots will self-provision:
   - Helius webhooks
   - Monitoring code
   - Alert configurations
   - Infrastructure quotas

4. Bots collaborate:
   - Share detection algorithms
   - Execute shared code
   - Coordinate investigations
""")


if __name__ == "__main__":
    asyncio.run(main())
