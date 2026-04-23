"""
Omega Forensic V5 - The Investigator Bot
=========================================
Self-healing, self-learning forensic investigator bot.
Matter-of-fact personality, digs multiple layers deep.
"""

import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging

# Add parent to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.intelligent_switcher import IntelligentSwitcher, deep_analysis
from forensic.wallet_database import get_wallet_database, WalletCategory, EvidenceTier
from forensic.api_arsenal import ForensicAPIArsenal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("InvestigatorBot")

# === THE INVESTIGATOR SYSTEM PROMPT ===
INVESTIGATOR_PERSONALITY = """You are The Investigator, a forensic blockchain analyst with a matter-of-fact personality.

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
1. ALWAYS write full wallet addresses (44 characters)
2. Distinguish between verified and suspected connections
3. Cite evidence for every claim
4. Flag anything that needs verification
5. Look for KYC vectors and real-world identities
6. Map money flows precisely
7. Identify patterns of manipulation

You are investigating the CRM token scam (Aug 2025 - Mar 2026).
Target CA: Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS

Critical wallets in your database:
- AFXigaYuRKYmvd9HZQCobtZ98FNAwnwpsnjvJRztUGb6 (Botnet Commander, 970 wallets)
- CNSob1LwXvDRmjioxyjm78tDb2S7nzFK6K8t3VmuhKpn (Root Funder, MoonPay KYC)
- HLnpSz9h2S4hiLQ4uN3vGYAHJqDmbFCwkx9prSXkdPMc (Master Feeder, 81M CRM, DELETED)
- 8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj (CRM/PBTC Nexus, SMOKING GUN)
- F4HGHWyaCvDkUF88svvCHhSMpR9YzHCYSNmojaKQtRSB (SOSANA Treasury)
- ASTyfSima4LLAdDgoFGkgqoKowG1LZFDr9fAQrg7iaJZ (Nuclear Treasury, 33K SOL)

Human suspects:
- Mark Ross: Suspected project creator
- Brian Lyles: Suspected developer
- Tracy Silver: Suspected marketing operator
- David Track: Suspected liquidity operator

Respond like a professional investigator: factual, thorough, relentless.
"""

@dataclass
class InvestigationSession:
    """Session state for an investigation."""
    session_id: str
    started_at: datetime
    queries: List[Dict] = field(default_factory=list)
    findings: List[Dict] = field(default_factory=list)
    wallets_examined: List[str] = field(default_factory=list)
    last_reset: datetime = None
    
    def __post_init__(self):
        if self.last_reset is None:
            self.last_reset = datetime.now()

class InvestigatorBot:
    """
    The Investigator - Self-healing, self-learning forensic bot.
    
    Capabilities:
    - Deep wallet analysis (multiple layers)
    - Cross-project connection tracking
    - KYC vector hunting
    - Evidence evaluation
    - Natural dialogue
    - Proactive solution offering
    """
    
    def __init__(self):
        self.switcher = IntelligentSwitcher()
        self.wallet_db = get_wallet_database()
        self.sessions: Dict[str, InvestigationSession] = {}
        self.learned_patterns: List[Dict] = []
        self.error_history: List[Dict] = []
        self.daily_reset_time = datetime.now()
        
        logger.info("🕵️ The Investigator initialized")
    
    def reset_daily(self):
        """Perform daily reset for security."""
        now = datetime.now()
        if (now - self.daily_reset_time).days >= 1:
            logger.info("🔄 Performing daily security reset...")
            
            # Clear non-essential data
            self.sessions = {}
            self.error_history = []
            
            # Keep learned patterns (they're valuable)
            
            self.daily_reset_time = now
            logger.info("  ✓ Daily reset complete")
    
    def investigate_wallet(
        self,
        wallet_address: str,
        depth: int = 3,
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        Investigate a wallet deeply.
        
        Args:
            wallet_address: Wallet to investigate
            depth: How many connection layers deep
            session_id: Optional session tracking
        
        Returns:
            Investigation results
        """
        self.reset_daily()
        
        logger.info(f"🔍 Investigating wallet: {wallet_address}")
        
        # Get wallet from database
        db_wallet = self.wallet_db.get_wallet(wallet_address)
        
        # Build investigation prompt
        prompt = f"""Investigate wallet: {wallet_address}

Search depth: {depth} layers

Please provide:
1. Wallet classification and role
2. Connected wallets and relationships
3. Cross-project affiliations
4. Suspicious patterns or red flags
5. KYC vectors if any
6. Evidence quality assessment
7. Recommended next steps

Be thorough. Dig deep. Cite evidence."""
        
        # Call AI for analysis
        response = deep_analysis(prompt)
        
        # Track in session
        if session_id:
            if session_id not in self.sessions:
                self.sessions[session_id] = InvestigationSession(
                    session_id=session_id,
                    started_at=datetime.now()
                )
            
            self.sessions[session_id].queries.append({
                "type": "wallet_investigation",
                "target": wallet_address,
                "timestamp": datetime.now().isoformat()
            })
            self.sessions[session_id].wallets_examined.append(wallet_address)
        
        result = {
            "wallet": wallet_address,
            "analysis": response,
            "database_info": db_wallet.to_dict() if db_wallet else None,
            "timestamp": datetime.now().isoformat()
        }
        
        # Self-learning: store pattern
        self.learned_patterns.append({
            "type": "wallet_investigation",
            "wallet": wallet_address,
            "timestamp": datetime.now().isoformat(),
            "has_db_record": db_wallet is not None
        })
        
        return result
    
    def investigate_connection(
        self,
        wallet1: str,
        wallet2: str,
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        Investigate the connection between two wallets.
        
        Args:
            wallet1: First wallet
            wallet2: Second wallet
            session_id: Optional session tracking
        
        Returns:
            Connection analysis
        """
        self.reset_daily()
        
        logger.info(f"🔗 Investigating connection: {wallet1} ↔ {wallet2}")
        
        prompt = f"""Analyze the connection between these two wallets:

Wallet A: {wallet1}
Wallet B: {wallet2}

Determine:
1. Direct transaction history between them
2. Common connections (shared wallets)
3. Temporal patterns (coordinated activity)
4. Financial flows (who funded whom)
5. Evidence strength of connection
6. Strategic importance of this link

Provide specific transaction signatures if available."""
        
        response = deep_analysis(prompt)
        
        return {
            "wallet_a": wallet1,
            "wallet_b": wallet2,
            "connection_analysis": response,
            "timestamp": datetime.now().isoformat()
        }
    
    def hunt_kyc_vectors(
        self,
        wallet_address: str,
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        Hunt for KYC vectors on a wallet.
        
        Args:
            wallet_address: Wallet to investigate
            session_id: Optional session tracking
        
        Returns:
            KYC vector analysis
        """
        self.reset_daily()
        
        logger.info(f"🎯 Hunting KYC vectors for: {wallet_address}")
        
        # Check database first
        db_wallet = self.wallet_db.get_wallet(wallet_address)
        known_vectors = db_wallet.kyc_vectors if db_wallet else []
        
        prompt = f"""Hunt for KYC vectors for wallet: {wallet_address}

Known vectors from database:
{json.dumps(known_vectors, indent=2) if known_vectors else "None recorded"}

Search strategies:
1. Exchange connections (MoonPay, etc.)
2. Entity labels from Arkham
3. Online mentions (Twitter, forums)
4. Linked projects with known teams
5. Funding patterns suggesting KYC
6. Social media connections

For each vector found, specify:
- Type (exchange, entity, social, etc.)
- Confidence level (high/medium/low)
- Subpoena potential
- Specific entity name if known

Be aggressive in finding connections."""
        
        response = deep_analysis(prompt)
        
        return {
            "wallet": wallet_address,
            "kyc_analysis": response,
            "known_vectors": known_vectors,
            "timestamp": datetime.now().isoformat()
        }
    
    def analyze_cross_project(
        self,
        project1: str = "CRM",
        project2: str = "SOSANA",
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        Analyze cross-project connections.
        
        Args:
            project1: First project
            project2: Second project
            session_id: Optional session tracking
        
        Returns:
            Cross-project analysis
        """
        self.reset_daily()
        
        logger.info(f"🌐 Analyzing {project1} ↔ {project2} connections")
        
        # Get wallets affiliated with both projects
        p1_wallets = self.wallet_db.get_cross_project_wallets(project1)
        p2_wallets = self.wallet_db.get_cross_project_wallets(project2)
        
        # Find overlap
        p1_addrs = {w.address for w in p1_wallets}
        p2_addrs = {w.address for w in p2_wallets}
        overlap = p1_addrs.intersection(p2_addrs)
        
        prompt = f"""Analyze cross-project connections between {project1} and {project2}.

Wallets affiliated with {project1}: {len(p1_wallets)}
Wallets affiliated with {project2}: {len(p2_wallets)}
Wallets connected to BOTH: {len(overlap)}

Overlapping wallets:
{list(overlap)[:10] if overlap else "None directly overlapping"}

Provide:
1. Strength of project connection
2. Key bridging wallets
3. Money flow patterns between projects
4. Evidence this is coordinated activity
5. RICO implications of cross-project coordination

This is critical for proving enterprise scope."""
        
        response = deep_analysis(prompt)
        
        return {
            "project_a": project1,
            "project_b": project2,
            "analysis": response,
            "overlapping_wallets": list(overlap),
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_leads(self, session_id: str = None) -> Dict[str, Any]:
        """
        Generate new investigation leads.
        
        Args:
            session_id: Optional session tracking
        
        Returns:
            Generated leads
        """
        self.reset_daily()
        
        logger.info("💡 Generating investigation leads...")
        
        # Get statistics
        stats = self.wallet_db.get_statistics()
        
        # Get unexamined wallets
        all_wallets = set(self.wallet_db.wallets.keys())
        
        if session_id and session_id in self.sessions:
            examined = set(self.sessions[session_id].wallets_examined)
            unexamined = all_wallets - examined
        else:
            unexamined = all_wallets
        
        prompt = f"""Generate investigation leads based on current database.

Database Statistics:
- Total wallets: {stats['total_wallets']}
- CRM controlled: {stats['total_crm_controlled']:,.0f}
- KYC vectors: {stats['kyc_vectors_found']}
- Cross-project connections: {stats['cross_project_connections']}

Unexamined wallets: {len(unexamined)}

Generate 5 high-priority investigation leads:
1. Wallets that need deeper analysis
2. Connection paths to explore
3. KYC vectors to pursue
4. Cross-project links to verify
5. Patterns that suggest coordination

For each lead, specify:
- Priority (critical/high/medium)
- Specific wallets or connections
- Expected evidence value
- Recommended investigation method"""
        
        response = deep_analysis(prompt)
        
        return {
            "leads": response,
            "unexamined_count": len(unexamined),
            "timestamp": datetime.now().isoformat()
        }
    
    def self_heal(self, error_info: Dict):
        """
        Self-healing: learn from errors.
        
        Args:
            error_info: Information about the error
        """
        logger.info(f"🩹 Self-healing from error: {error_info.get('type', 'unknown')}")
        
        self.error_history.append({
            "timestamp": datetime.now().isoformat(),
            **error_info
        })
        
        # Store learned pattern
        self.learned_patterns.append({
            "type": "error_recovery",
            "error": error_info,
            "timestamp": datetime.now().isoformat()
        })
        
        # Limit history size
        if len(self.error_history) > 100:
            self.error_history = self.error_history[-50:]
    
    def get_status(self) -> Dict[str, Any]:
        """Get bot status and statistics."""
        return {
            "status": "operational",
            "daily_reset": self.daily_reset_time.isoformat(),
            "active_sessions": len(self.sessions),
            "learned_patterns": len(self.learned_patterns),
            "error_count": len(self.error_history),
            "wallet_database_size": len(self.wallet_db.wallets),
            "capabilities": [
                "wallet_investigation",
                "connection_analysis",
                "kyc_vector_hunting",
                "cross_project_analysis",
                "lead_generation"
            ]
        }
    
    def chat(self, message: str, session_id: str = None) -> str:
        """
        Natural dialogue with the investigator.
        
        Args:
            message: User message
            session_id: Optional session tracking
        
        Returns:
            Investigator response
        """
        self.reset_daily()
        
        # Build conversation context
        messages = [
            {"role": "system", "content": INVESTIGATOR_PERSONALITY},
            {"role": "user", "content": message}
        ]
        
        # Use quick reply for chat
        result = self.switcher.call_model(
            messages=messages,
            task_type="quick_chat",
            urgency="normal"
        )
        
        response = result.get("content", "I'm investigating... please provide more details.")
        
        # Track in session
        if session_id:
            if session_id not in self.sessions:
                self.sessions[session_id] = InvestigationSession(
                    session_id=session_id,
                    started_at=datetime.now()
                )
            
            self.sessions[session_id].queries.append({
                "type": "chat",
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
        
        return response

# === SINGLETON INSTANCE ===
_investigator = None

def get_investigator() -> InvestigatorBot:
    """Get singleton investigator instance."""
    global _investigator
    if _investigator is None:
        _investigator = InvestigatorBot()
    return _investigator

# === QUICK ACCESS FUNCTIONS ===
def investigate(wallet: str, depth: int = 3) -> Dict:
    """Quick function to investigate a wallet."""
    bot = get_investigator()
    return bot.investigate_wallet(wallet, depth)

def find_kyc(wallet: str) -> Dict:
    """Quick function to hunt KYC vectors."""
    bot = get_investigator()
    return bot.hunt_kyc_vectors(wallet)

def ask_investigator(message: str) -> str:
    """Quick chat with the investigator."""
    bot = get_investigator()
    return bot.chat(message)

if __name__ == "__main__":
    # Test the investigator
    print("=" * 70)
    print("OMEGA FORENSIC V5 - THE INVESTIGATOR BOT")
    print("=" * 70)
    
    bot = get_investigator()
    
    # Print status
    status = bot.get_status()
    print(f"\n📊 Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Test chat
    print("\n💬 Test Chat:")
    response = bot.chat("What is the CRM token investigation about?")
    print(f"  Q: What is the CRM token investigation about?")
    print(f"  A: {response[:200]}...")
    
    print("\n" + "=" * 70)
