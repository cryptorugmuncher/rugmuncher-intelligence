"""
RMI Bot - RugMunch Intelligence Bot
=====================================
A polite crypto investigator for tracking down scammers.
Built for the CRM case, expandable to many others.
"""

import os
import json
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

# Bot personality configuration
RMI_PERSONALITY = """You are RMI Bot (RugMunch Intelligence), a polite and professional crypto investigator.

Your personality:
- Polite and respectful in all interactions
- Matter-of-fact and evidence-based
- Thorough but concise in explanations
- Always cite sources and evidence
- Never make accusations without proof
- Transparent about limitations and uncertainties
- Helpful and patient with users

When investigating:
1. Always verify claims with on-chain data
2. Distinguish between confirmed facts and suspicions
3. Present evidence clearly with transaction signatures
4. Acknowledge when something can't be determined
5. Guide users toward proper forensic methodology

For the CRM case specifically:
- Target: Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS
- Timeline: August 2025 - March 2026
- Focus: Evidence-based scammer identification

You are built with Kimi AI and use multiple APIs for verification.
Never claim guilt without evidence. Always presume innocence until proven.

Respond in a helpful, professional tone. Use emojis sparingly for clarity.
"""

@dataclass
class BotResponse:
    """Structured bot response."""
    text: str
    confidence: float
    evidence_refs: List[str]
    suggested_actions: List[str]
    needs_verification: bool = False

class RMIBot:
    """
    RMI Bot - RugMunch Intelligence Investigator
    """
    
    def __init__(self):
        self.name = "RMI Bot"
        self.version = "1.0.0"
        self.case_focus = "CRM Token Investigation"
        self.conversation_history = []
        
    async def investigate_wallet(self, address: str, depth: int = 2) -> BotResponse:
        """
        Investigate a wallet and return findings.
        """
        # This would call the forensic APIs
        # For now, return structured response template
        
        findings = f"""🔍 Wallet Investigation: `{address[:20]}...`

**Status**: Under Investigation
**Approach**: Evidence-based analysis

I would analyze this wallet using:
- Helius API (transaction history)
- Arkham Intelligence (entity labels)
- MistTrack (risk scoring)
- On-chain verification

*Note: This is a template. Connect APIs for live analysis.*

Would you like me to:
1. Check transaction history
2. Find connected wallets
3. Analyze token flows
4. Generate a detailed report
"""
        
        return BotResponse(
            text=findings,
            confidence=0.0,  # No confidence without API data
            evidence_refs=[],
            suggested_actions=[
                "Check transaction history",
                "Find connected wallets", 
                "Analyze token flows",
                "Generate report"
            ],
            needs_verification=True
        )
    
    async def analyze_token(self, token_address: str) -> BotResponse:
        """
        Analyze a token for suspicious patterns.
        """
        analysis = f"""📊 Token Analysis: `{token_address[:20]}...`

**Analysis Areas**:
- Holder distribution
- Liquidity patterns
- Transaction anomalies
- Bot activity detection
- Whale movements

*Connect BirdEye/LunarCrush APIs for live data.*

What specific aspect would you like me to focus on?
"""
        
        return BotResponse(
            text=analysis,
            confidence=0.0,
            evidence_refs=[],
            suggested_actions=[
                "Analyze holder distribution",
                "Check liquidity patterns",
                "Detect bot activity",
                "Track whale movements"
            ]
        )
    
    async def find_wallet_cluster(self, center_wallet: str) -> BotResponse:
        """
        Find wallet clusters around a center wallet.
        """
        cluster_info = f"""🕸️ Wallet Cluster Analysis

**Center Wallet**: `{center_wallet[:20]}...`

**Cluster Detection Methods**:
1. Transaction pattern analysis
2. Temporal proximity detection
3. Common counterparty identification
4. Fund flow tracing
5. Behavioral fingerprinting

*This requires transaction data for accurate clustering.*

I can identify clusters based on:
- Shared funding sources
- Coordinated timing
- Similar transaction patterns
- Common destinations

Would you like me to proceed with cluster detection?
"""
        
        return BotResponse(
            text=cluster_info,
            confidence=0.0,
            evidence_refs=[],
            suggested_actions=[
                "Run cluster detection",
                "Show bubble map",
                "Export cluster data",
                "Generate cluster report"
            ]
        )
    
    async def generate_bubble_map(self, wallet: str, depth: int = 2) -> BotResponse:
        """
        Generate association bubble map for visualization.
        """
        bubble_info = f"""🫧 Association Bubble Map

**Target**: `{wallet[:20]}...`
**Depth**: {depth} hops

**Bubble Map Logic**:
- Size = transaction volume
- Color = connection strength
- Lines = transaction flows
- Clusters = related wallets

**What the bubbles show**:
🟢 Green = Verified connection
🟡 Yellow = Suspicious pattern
🔴 Red = Confirmed scammer
🔵 Blue = Exchange/known entity
⚪ Gray = Unknown/unverified

*Bubble maps help visualize wallet relationships at a glance.*

I'll generate an interactive map showing all connections.
"""
        
        return BotResponse(
            text=bubble_info,
            confidence=0.0,
            evidence_refs=[],
            suggested_actions=[
                "Generate interactive map",
                "Export as PNG",
                "Export as JSON",
                "Analyze clusters"
            ]
        )
    
    async def chat(self, message: str, user_id: str = None) -> str:
        """
        General chat response with RMI personality.
        """
        # Simple pattern matching for common queries
        msg_lower = message.lower()
        
        if any(x in msg_lower for x in ["hello", "hi", "hey"]):
            return f"""👋 Hello! I'm RMI Bot, your crypto investigator.

I can help you with:
• Wallet investigations
• Token analysis
• Cluster detection
• Bubble maps
• Evidence collection

What would you like to investigate today?
"""
        
        elif any(x in msg_lower for x in ["help", "commands"]):
            return f"""📋 RMI Bot Commands

**Investigation**:
`/investigate <wallet>` - Deep wallet analysis
`/cluster <wallet>` - Find wallet clusters
`/bubble <wallet>` - Generate bubble map
`/token <address>` - Analyze token

**Reports**:
`/report` - Generate case report
`/export` - Export findings
`/status` - Check investigation status

**Analysis**:
`/connections <wallet>` - Show connections
`/timeline <wallet>` - Transaction timeline
`/risk <wallet>` - Risk assessment

Just type naturally and I'll help you investigate!
"""
        
        elif len(message) == 44 and message[0].isalnum():
            # Looks like a wallet address
            return f"""🔍 I see you've shared a wallet address: `{message[:20]}...`

I can help you investigate this wallet:

1. **Check transaction history** - See all activity
2. **Find connections** - Map relationships
3. **Analyze patterns** - Detect suspicious behavior
4. **Generate report** - Document findings

Which would you like me to do?
"""
        
        else:
            return f"""🤔 I'm not sure I understood that correctly.

I can help you investigate:
• Wallets (paste address)
• Tokens (paste contract)
• Clusters (find related wallets)
• Scams (analyze patterns)

Try asking something like:
- "Investigate wallet X"
- "Find clusters around Y"
- "Generate bubble map for Z"

Or just paste a wallet address and I'll analyze it!
"""

# Singleton instance
_rmi_bot = None

def get_rmi_bot() -> RMIBot:
    """Get RMI Bot instance."""
    global _rmi_bot
    if _rmi_bot is None:
        _rmi_bot = RMIBot()
    return _rmi_bot

if __name__ == "__main__":
    print("=" * 70)
    print("RMI BOT - RugMunch Intelligence")
    print("=" * 70)
    print("\n✅ RMI Bot initialized")
    print("✅ Polite crypto investigator ready")
    print("✅ Evidence-based methodology")
    print("\n" + "=" * 70)
