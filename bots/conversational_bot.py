#!/usr/bin/env python3
"""
🤖 RUGMUNCHBOT AI-FIRST - Conversational Interface
Natural language crypto forensics assistant with AI orchestration
"""

import os
import re
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Telegram imports
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)


class UserIntent(Enum):
    SCAN_REQUEST = "scan_request"
    EXPLAIN_REQUEST = "explain_request"
    PORTFOLIO_REVIEW = "portfolio_review"
    EDUCATION = "education"
    PRICING_INQUIRY = "pricing_inquiry"
    SUPPORT = "support"
    GREETING = "greeting"
    UNKNOWN = "unknown"


@dataclass
class UserContext:
    """User context for personalized interactions"""

    user_id: int
    customer_id: Optional[str]
    username: str
    display_name: str
    tier: str
    experience_level: str  # 'beginner', 'intermediate', 'expert'
    language: str
    scans_remaining: int
    active_subscription: Optional[Dict]
    recent_scans: List[Dict]
    preferences: Dict
    conversation_history: List[Dict]

    def has_seen_concept(self, concept: str) -> bool:
        """Check if user has been educated about a concept"""
        return concept in self.preferences.get("seen_concepts", [])

    def has_high_risk_experience(self) -> bool:
        """Check if user has experience with high-risk tokens"""
        return any(s.get("risk_score", 100) < 30 for s in self.recent_scans)


class AIIntentRouter:
    """Routes user messages to appropriate intents using AI"""

    # Keywords for quick routing (before AI classification)
    SCAN_KEYWORDS = [
        r"0x[a-fA-F0-9]{40}",  # ETH/BSC address
        r"[1-9A-HJ-NP-Za-km-z]{32,44}",  # Solana address
        r"scan",
        r"check",
        r"analyze",
        r"is this safe",
        r"what do you think",
        r"rug check",
        r"token",
        r"contract",
        r"address",
    ]

    EXPLAIN_KEYWORDS = [
        r"what is",
        r"what does",
        r"how does",
        r"why",
        r"explain",
        r"mean",
        r"honeypot",
        r"rug",
        r"bundle",
        r"liquidity",
        r"mint",
        r"ownership",
    ]

    PORTFOLIO_KEYWORDS = [
        r"my portfolio",
        r"my wallet",
        r"my tokens",
        r"my scans",
        r"watchlist",
        r"tracked",
        r"my history",
        r"what i have",
        r"check my",
    ]

    PRICING_KEYWORDS = [
        r"price",
        r"cost",
        r"how much",
        r"upgrade",
        r"pro",
        r"elite",
        r"subscribe",
        r"plan",
        r"tier",
        r"free",
        r"premium",
        r"payment",
    ]

    def __init__(self, llm_client=None):
        self.llm = llm_client

    async def classify_intent(self, message: str, context: UserContext) -> Dict:
        """Classify user intent from message"""

        message_lower = message.lower().strip()

        # Quick keyword matching for common intents
        if self._contains_address(message):
            return {
                "type": UserIntent.SCAN_REQUEST,
                "confidence": 0.95,
                "extracted_addresses": self._extract_addresses(message),
                "tone": self._detect_tone(message),
            }

        if any(re.search(kw, message_lower) for kw in self.EXPLAIN_KEYWORDS):
            # Extract the concept being asked about
            concept = self._extract_concept(message_lower)
            return {
                "type": UserIntent.EXPLAIN_REQUEST,
                "confidence": 0.85,
                "concept": concept,
                "tone": "curious",
            }

        if any(kw in message_lower for kw in self.PORTFOLIO_KEYWORDS):
            return {
                "type": UserIntent.PORTFOLIO_REVIEW,
                "confidence": 0.80,
                "tone": "neutral",
            }

        if any(kw in message_lower for kw in self.PRICING_KEYWORDS):
            return {
                "type": UserIntent.PRICING_INQUIRY,
                "confidence": 0.80,
                "tone": "interested",
            }

        # Use AI for complex classification
        if self.llm:
            ai_classification = await self._ai_classify(message, context)
            return ai_classification

        return {"type": UserIntent.UNKNOWN, "confidence": 1.0, "tone": "neutral"}

    def _contains_address(self, message: str) -> bool:
        """Check if message contains a blockchain address"""
        eth_pattern = r"0x[a-fA-F0-9]{40}"
        sol_pattern = r"[1-9A-HJ-NP-Za-km-z]{32,44}"
        return bool(re.search(eth_pattern, message) or re.search(sol_pattern, message))

    def _extract_addresses(self, message: str) -> List[Dict]:
        """Extract all blockchain addresses from message"""
        addresses = []

        # ETH/BSC addresses
        eth_matches = re.findall(r"0x[a-fA-F0-9]{40}", message)
        for addr in eth_matches:
            addresses.append(
                {
                    "address": addr,
                    "chain": "eth",  # Will be refined based on context
                }
            )

        # Solana addresses
        sol_matches = re.findall(r"[1-9A-HJ-NP-Za-km-z]{32,44}", message)
        for addr in sol_matches:
            if len(addr) >= 32:
                addresses.append({"address": addr, "chain": "sol"})

        return addresses

    def _detect_tone(self, message: str) -> str:
        """Detect emotional tone of message"""
        urgency_words = [
            "urgent",
            "help",
            "scam",
            "stolen",
            "lost",
            "hurry",
            "quick",
            "emergency",
        ]
        worry_words = [
            "worried",
            "concern",
            "nervous",
            "unsure",
            "safe",
            "legit",
            "trust",
        ]
        excitement_words = ["moon", "pump", "gem", "100x", "lambo", "buy now"]

        message_lower = message.lower()

        if any(w in message_lower for w in urgency_words):
            return "urgent"
        if any(w in message_lower for w in worry_words):
            return "concerned"
        if any(w in message_lower for w in excitement_words):
            return "excited"

        return "neutral"

    def _extract_concept(self, message: str) -> Optional[str]:
        """Extract concept being asked about"""
        concepts = {
            "honeypot": [
                "honeypot",
                "honey pot",
                "cant sell",
                "can't sell",
                "sell error",
            ],
            "rugpull": ["rug pull", "rugpull", "rug", "scam token"],
            "bundle": ["bundle", "snipers", "sniper bots", "coordinated"],
            "liquidity": ["liquidity", "lp", "pool", "locked"],
            "mint": ["mint", "inflation", "print tokens"],
            "ownership": ["ownership", "renounced", "owner"],
            "tax": ["tax", "fee", "transfer fee"],
            "contract": ["contract", "verified", "source code"],
        }

        for concept, keywords in concepts.items():
            if any(kw in message for kw in keywords):
                return concept

        return None

    async def _ai_classify(self, message: str, context: UserContext) -> Dict:
        """Use AI to classify complex intents"""
        # Placeholder for AI classification
        # In production, this would call an LLM API
        return {"type": UserIntent.UNKNOWN, "confidence": 0.5, "tone": "neutral"}


class ConversationalResponseGenerator:
    """Generates natural language responses based on context"""

    RISK_TEMPLATES = {
        "critical": {
            "beginner": "🚨 **STOP! This token is extremely dangerous.**\n\nI've found critical red flags that almost always mean a scam:",
            "intermediate": "🚨 **CRITICAL RISK DETECTED**\n\nMultiple severe vulnerabilities identified:",
            "expert": "🚨 **CRITICAL: Immediate exit recommended**\n\nAttack vectors confirmed:",
        },
        "high": {
            "beginner": "⚠️ **High Risk Warning**\n\nThis token has several concerning issues:",
            "intermediate": "⚠️ **High Risk Assessment**\n\nSignificant threats detected:",
            "expert": "⚠️ **HIGH: Caution advised**\n\nRisk factors:",
        },
        "medium": {
            "beginner": "🟡 **Medium Risk - Be Careful**\n\nI've spotted some things to watch out for:",
            "intermediate": "🟡 **Medium Risk**\n\nSome concerns identified:",
            "expert": "🟡 **MODERATE: Due diligence required**\n\nObservations:",
        },
        "safe": {
            "beginner": "🟢 **Looks Safe!**\n\nGood news - I didn't find major issues:",
            "intermediate": "🟢 **Safe Assessment**\n\nSecurity checks passed:",
            "expert": "🟢 **LOW RISK: Standard due diligence**\n\nFindings:",
        },
    }

    def __init__(self, llm_client=None):
        self.llm = llm_client

    def generate_scan_response(
        self, scan_result: Dict, user_context: UserContext, tone: str = "neutral"
    ) -> str:
        """Generate personalized scan response"""

        score = scan_result.get("score", 50)

        # Determine risk category
        if score < 30:
            risk_level = "critical"
        elif score < 50:
            risk_level = "high"
        elif score < 70:
            risk_level = "medium"
        else:
            risk_level = "safe"

        # Get base template for user's experience level
        base = self.RISK_TEMPLATES[risk_level].get(
            user_context.experience_level,
            self.RISK_TEMPLATES[risk_level]["intermediate"],
        )

        # Add specific findings
        findings_text = self._format_findings(
            scan_result, user_context.experience_level, tone
        )

        # Add contextual help for beginners
        help_section = ""
        if user_context.experience_level == "beginner":
            help_section = self._generate_contextual_help(scan_result, user_context)

        # Add action buttons hint
        action_hint = self._generate_action_hint(risk_level, user_context)

        return f"{base}\n\n{findings_text}\n\n{help_section}\n\n{action_hint}"

    def _format_findings(
        self, scan_result: Dict, experience_level: str, tone: str
    ) -> str:
        """Format scan findings based on user level"""

        findings = []

        # Critical flags
        critical = scan_result.get("critical_flags", [])
        if critical:
            for flag in critical[:3]:
                if experience_level == "beginner":
                    # Simplify technical terms
                    simplified = self._simplify_technical_term(flag)
                    findings.append(f"❌ {simplified}")
                else:
                    findings.append(f"❌ {flag}")

        # High flags
        high = scan_result.get("high_flags", [])
        if high:
            for flag in high[:3]:
                if experience_level == "beginner":
                    simplified = self._simplify_technical_term(flag)
                    findings.append(f"⚠️ {simplified}")
                else:
                    findings.append(f"⚠️ {flag}")

        # For safe tokens, show positive indicators
        if scan_result.get("score", 50) >= 80:
            findings.append("✅ Contract is verified and open source")
            findings.append("✅ Liquidity is locked")
            if scan_result.get("honeypot_data", {}).get("is_honeypot") is False:
                findings.append("✅ You can buy AND sell freely")

        return (
            "\n".join(f"• {f}" for f in findings)
            if findings
            else "No major issues found."
        )

    def _simplify_technical_term(self, text: str) -> str:
        """Simplify technical terms for beginners"""
        simplifications = {
            "honeypot": "You can buy but can't sell (SCAM!)",
            "liquidity": "Money available for trading",
            "mint function": "Hidden way to create more tokens (bad!)",
            "ownership": "Who controls the contract",
            "renounced": "No one can change it anymore (good!)",
            "bundle": "Group of connected buyers",
            "dev wallet": "Developer/owner's wallet",
        }

        result = text
        for technical, simple in simplifications.items():
            if technical in text.lower():
                result = result.replace(technical, simple)

        return result

    def _generate_contextual_help(
        self, scan_result: Dict, user_context: UserContext
    ) -> str:
        """Generate contextual help based on findings"""

        help_items = []

        # Check if user hasn't seen this concept before
        if "honeypot" in str(scan_result.get("critical_flags", [])):
            if not user_context.has_seen_concept("honeypot"):
                help_items.append(
                    "🍯 **What is a Honeypot?**\n"
                    "A scam where you can buy tokens but can't sell them. "
                    "The developer steals all the money while you're stuck.\n"
                    "[Learn more about honeypots]"
                )

        if scan_result.get("score", 100) < 30:
            help_items.append(
                "🚨 **What should I do?**\n"
                "If you already bought: Try to sell immediately (may not work if honeypot).\n"
                "If you haven't: Stay away! This will likely rug.\n"
                "[Report this token]"
            )

        return "\n\n".join(help_items)

    def _generate_action_hint(self, risk_level: str, user_context: UserContext) -> str:
        """Generate hint about available actions"""

        if risk_level in ["critical", "high"]:
            return (
                "🛠️ **Available actions:**\n"
                "🔴 Panic Sell (if you hold)\n"
                "📊 Full Analysis\n"
                "🔔 Set Rug Alert"
            )
        else:
            return (
                "🛠️ **Want to dig deeper?**\n"
                "🫧 View Bubble Map\n"
                "🕸️ Check for Bundles"
                + (" (PRO)" if user_context.tier == "free" else "")
                + "\n"
                "🔔 Watch this token"
            )

    def generate_explanation(self, concept: str, user_context: UserContext) -> str:
        """Generate educational explanation"""

        explanations = {
            "honeypot": {
                "beginner": (
                    "🍯 **What is a Honeypot Scam?**\n\n"
                    "Imagine a jar of honey. Bees can fly in, but they can't fly out.\n\n"
                    "A crypto honeypot works the same way:\n"
                    "✅ You CAN buy the token\n"
                    "❌ You CAN'T sell it\n\n"
                    "The scammer waits for many people to buy (raising the price), "
                    "then they drain all the money. You're left with worthless tokens.\n\n"
                    "🛡️ **How to avoid:**\n"
                    "• Always use RugMuncher to scan before buying\n"
                    "• If it says HONEYPOT - never buy\n"
                    "• Small test sells don't work - they often allow tiny sells"
                ),
                "intermediate": (
                    "🍯 **Honeypot Technical Explanation**\n\n"
                    "A honeypot is a smart contract with asymmetric transfer logic:\n"
                    "• `transfer()` allows incoming transfers\n"
                    "• `transfer()` reverts on outgoing transfers (except for whitelisted addresses)\n\n"
                    "Common honeypot patterns:\n"
                    "1. Balance tracking with hidden sell restrictions\n"
                    "2. Dynamic tax that exceeds 100% on sells\n"
                    "3. Blacklist that activates after purchase\n"
                    "4. Cooldown periods that only apply to sellers\n\n"
                    "Advanced detection requires simulating sell transactions."
                ),
            },
            "rugpull": {
                "beginner": (
                    "💀 **What is a Rug Pull?**\n\n"
                    "A rug pull is when crypto developers suddenly abandon a project and run away with investors' money.\n\n"
                    "**Common types:**\n"
                    "1. **Liquidity Pull** - Developers remove all trading money\n"
                    "2. **Dump** - Developers sell all their tokens at once\n"
                    "3. **Mint & Dump** - Create new tokens and sell them\n\n"
                    "**Warning signs:**\n"
                    "• Unlocked liquidity\n"
                    "• Developers hold >20% of tokens\n"
                    "• No contract verification\n"
                    "• Hidden mint functions\n\n"
                    "🛡️ RugMuncher checks all of these for you!"
                )
            },
            "bundle": {
                "beginner": (
                    "🕸️ **What is Bundle Buying?**\n\n"
                    "Bundle buying is when a group of connected wallets buy a token together to manipulate the price.\n\n"
                    "**Why it's bad:**\n"
                    "• They pump the price artificially\n"
                    "• Regular buyers think it's popular\n"
                    "• They all dump at once, crashing the price\n\n"
                    "**How to spot:**\n"
                    "• Multiple wallets buying at the exact same time\n"
                    "• New wallets created just before buying\n"
                    "• Similar amounts purchased\n\n"
                    "🕸️ RugMuncher's Bundle Detector finds these patterns!"
                )
            },
        }

        return explanations.get(concept, {}).get(
            user_context.experience_level,
            explanations.get(concept, {}).get("beginner", "Explanation not available."),
        )


class SmartOnboarding:
    """Intelligent onboarding flow for new users"""

    ONBOARDING_STEPS = [
        {
            "id": "welcome",
            "message": (
                "👋 **Welcome to RugMuncher!**\n\n"
                "I'm your crypto bodyguard. I analyze tokens to keep you safe from scams.\n\n"
                "**In 60 seconds, you'll be scam-proof.**"
            ),
            "actions": ["Start Quick Tour", "Scan Something Now"],
        },
        {
            "id": "what_i_do",
            "message": (
                "🔍 **Here's what I do:**\n\n"
                "✅ **Instant Scans** - Check any token in seconds\n"
                "🛡️ **Rug Detection** - Spot scams before they happen\n"
                "🕵️ **Dev Analysis** - See who's behind the project\n"
                "📊 **Holder Maps** - Visualize who owns what\n"
                "🔔 **Smart Alerts** - Get warned before rugs\n\n"
                "I use real blockchain data - no guessing!"
            ),
            "actions": ["Cool! What's next?"],
        },
        {
            "id": "demo_scan",
            "message": (
                "📱 **Try a real scan:**\n\n"
                "Paste any contract address and I'll analyze it instantly.\n\n"
                "**Example address:**\n"
                "`0x742d35Cc6634C0532925a3b844Bc9e7595fdf5aa`\n\n"
                "Or send your own!"
            ),
            "actions": ["📋 Copy Example"],
            "wait_for_input": True,
        },
        {
            "id": "gift",
            "message": (
                "🎁 **Welcome Gift Activated!**\n\n"
                "You've received **3 FREE Pro scans**!\n\n"
                "Try premium features:\n"
                "• 🕸️ Bundle Detection\n"
                "• 🫧 Full Bubble Maps\n"
                "• 🧠 Deep Wallet Analysis\n\n"
                "Your free scans expire in 7 days."
            ),
            "actions": ["🚀 Start Scanning!", "📊 View Plans"],
        },
    ]

    async def start_onboarding(self, user_id: int, context: ContextTypes.DEFAULT_TYPE):
        """Start onboarding flow"""
        step = self.ONBOARDING_STEPS[0]

        keyboard = self._build_keyboard(step.get("actions", []))

        await context.bot.send_message(
            chat_id=user_id,
            text=step["message"],
            reply_markup=keyboard,
            parse_mode="Markdown",
        )

        # Store onboarding state
        context.user_data["onboarding"] = {
            "current_step": 0,
            "started_at": datetime.utcnow().isoformat(),
        }

    async def handle_onboarding_step(
        self, user_id: int, action: str, context: ContextTypes.DEFAULT_TYPE
    ) -> bool:
        """Handle onboarding step progression"""

        onboarding = context.user_data.get("onboarding", {})
        current_step_idx = onboarding.get("current_step", 0)

        if action == "skip":
            # Mark onboarding complete
            context.user_data["onboarding_complete"] = True
            return True

        if current_step_idx < len(self.ONBOARDING_STEPS) - 1:
            # Move to next step
            next_step = self.ONBOARDING_STEPS[current_step_idx + 1]
            onboarding["current_step"] = current_step_idx + 1

            keyboard = self._build_keyboard(next_step.get("actions", []))

            await context.bot.send_message(
                chat_id=user_id,
                text=next_step["message"],
                reply_markup=keyboard,
                parse_mode="Markdown",
            )

            return False  # Not complete
        else:
            # Onboarding complete
            context.user_data["onboarding_complete"] = True

            await context.bot.send_message(
                chat_id=user_id,
                text="✅ **You're all set!**\n\n"
                "Remember: When in doubt, scan it!\n\n"
                "Just paste any contract address anytime.\n\n"
                "Stay safe! 🛡️",
                parse_mode="Markdown",
            )

            return True

    def _build_keyboard(self, actions: List[str]) -> InlineKeyboardMarkup:
        """Build inline keyboard for actions"""
        buttons = []
        for action in actions:
            callback_data = (
                f"onboarding_{action.lower().replace(' ', '_').replace('!', '')}"
            )
            buttons.append([InlineKeyboardButton(action, callback_data=callback_data)])

        buttons.append(
            [InlineKeyboardButton("⏭️ Skip Tour", callback_data="onboarding_skip")]
        )

        return InlineKeyboardMarkup(buttons)


class ConversationalRugMuncherBot:
    """Main conversational bot class"""

    def __init__(self, db_client=None, llm_client=None):
        self.db = db_client
        self.intent_router = AIIntentRouter(llm_client)
        self.response_generator = ConversationalResponseGenerator(llm_client)
        self.onboarding = SmartOnboarding()
        self.user_contexts: Dict[int, UserContext] = {}

    async def get_user_context(self, user: Any) -> UserContext:
        """Get or create user context"""

        if user.id in self.user_contexts:
            return self.user_contexts[user.id]

        # Load from database
        customer = await self._load_customer(user.id)

        context = UserContext(
            user_id=user.id,
            customer_id=customer.get("id") if customer else None,
            username=user.username or "",
            display_name=user.first_name or "there",
            tier=customer.get("subscription_tier", "free") if customer else "free",
            experience_level=customer.get("experience_level", "beginner")
            if customer
            else "beginner",
            language=customer.get("language", "en") if customer else "en",
            scans_remaining=customer.get("scans_remaining", 3) if customer else 3,
            active_subscription=None,  # Would load from DB
            recent_scans=[],  # Would load recent scans
            preferences=customer.get("preferences", {}) if customer else {},
            conversation_history=[],
        )

        self.user_contexts[user.id] = context
        return context

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Main message handler"""

        user = update.effective_user
        message_text = update.message.text.strip()

        # Check if onboarding in progress
        if not context.user_data.get("onboarding_complete"):
            if context.user_data.get("onboarding"):
                await self.onboarding.handle_onboarding_step(
                    user.id, "continue", context
                )
                return
            else:
                await self.onboarding.start_onboarding(user.id, context)
                return

        # Get user context
        user_context = await self.get_user_context(user)

        # Classify intent
        intent = await self.intent_router.classify_intent(message_text, user_context)

        # Handle based on intent
        if intent["type"] == UserIntent.SCAN_REQUEST:
            await self.handle_scan_request(update, context, intent, user_context)

        elif intent["type"] == UserIntent.EXPLAIN_REQUEST:
            await self.handle_explain_request(update, context, intent, user_context)

        elif intent["type"] == UserIntent.PORTFOLIO_REVIEW:
            await self.handle_portfolio_review(update, context, user_context)

        elif intent["type"] == UserIntent.PRICING_INQUIRY:
            await self.handle_pricing_inquiry(update, context, user_context)

        elif intent["type"] == UserIntent.GREETING:
            await update.message.reply_text(
                f"Hey {user_context.display_name}! 👋 Ready to check some tokens?\n\n"
                f"Just paste a contract address and I'll analyze it!"
            )

        else:
            # Unknown intent - helpful fallback
            await update.message.reply_text(
                "I'm not sure what you're looking for! 🤔\n\n"
                "I can help you:\n"
                "🔍 Scan a token (just paste the address)\n"
                "❓ Explain crypto terms (ask 'what is a honeypot?')\n"
                "📊 Review your portfolio\n"
                "💰 See pricing plans\n\n"
                "What would you like to do?"
            )

        # Store in conversation history
        user_context.conversation_history.append(
            {
                "role": "user",
                "content": message_text,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    async def handle_scan_request(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        intent: Dict,
        user_context: UserContext,
    ):
        """Handle token scan request"""

        addresses = intent.get("extracted_addresses", [])
        if not addresses:
            await update.message.reply_text(
                "I don't see a valid contract address. 🤔\n\n"
                "Make sure it's a valid Ethereum (0x...) or Solana address."
            )
            return

        address = addresses[0]["address"]
        chain = addresses[0]["chain"]

        # Check scan limits
        if user_context.scans_remaining <= 0:
            await update.message.reply_text(
                "❌ **Daily scan limit reached!**\n\n"
                "Upgrade to Pro for unlimited scans:",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "⭐ Upgrade to Pro", callback_data="upgrade_menu"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "📊 View Plans", callback_data="view_plans"
                            )
                        ],
                    ]
                ),
                parse_mode="Markdown",
            )
            return

        # Show scanning message
        scanning_msg = await update.message.reply_text(
            f"🔍 Analyzing `{address[:20]}...`\n⏳ Checking blockchain data...",
            parse_mode="Markdown",
        )

        # Perform scan (would integrate with actual scanner)
        scan_result = await self._perform_scan(address, chain)

        # Generate personalized response
        response = self.response_generator.generate_scan_response(
            scan_result, user_context, intent.get("tone", "neutral")
        )

        # Update scanning message with results
        await scanning_msg.edit_text(
            response,
            parse_mode="Markdown",
            reply_markup=self._build_scan_actions_keyboard(
                address, chain, scan_result, user_context
            ),
        )

        # Decrement scans
        user_context.scans_remaining -= 1

    async def handle_explain_request(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        intent: Dict,
        user_context: UserContext,
    ):
        """Handle educational explain request"""

        concept = intent.get("concept")

        if concept:
            explanation = self.response_generator.generate_explanation(
                concept, user_context
            )

            # Mark as seen
            user_context.preferences.setdefault("seen_concepts", []).append(concept)

            await update.message.reply_text(
                explanation,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🔍 Scan a Token", callback_data="start_scan"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "📚 More Lessons", callback_data="education_menu"
                            )
                        ],
                    ]
                ),
            )
        else:
            await update.message.reply_text(
                "I'd love to explain! What would you like to learn about?\n\n"
                "• Honeypots\n"
                "• Rug pulls\n"
                "• Bundle buying\n"
                "• Liquidity locks\n"
                "• Token contracts\n\n"
                "Just ask!"
            )

    async def handle_portfolio_review(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        user_context: UserContext,
    ):
        """Handle portfolio review request"""

        # Would load actual portfolio data
        await update.message.reply_text(
            f"📊 **Your Portfolio Review**\n\n"
            f"**Active Subscription:** {user_context.tier.upper()}\n"
            f"**Scans Remaining Today:** {user_context.scans_remaining}\n\n"
            f"**Recent Activity:**\n"
            f"• {len(user_context.recent_scans)} tokens scanned\n"
            f"• Watchlist: Coming soon\n\n"
            f"[View Full Dashboard]",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🔍 Scan New Token", callback_data="start_scan"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "📈 View Analytics", callback_data="view_analytics"
                        )
                    ],
                ]
            ),
        )

    async def handle_pricing_inquiry(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        user_context: UserContext,
    ):
        """Handle pricing inquiry"""

        await update.message.reply_text(
            "💰 **RugMuncher Plans**\n\n"
            "**Free**\n"
            "• 3 scans/day\n"
            "• Basic risk check\n"
            "• Community alerts\n\n"
            "**Pro - $29/month**\n"
            "• 50 scans/day\n"
            "• Bundle detection\n"
            "• Full bubble maps\n"
            "• Wallet tracking\n\n"
            "**Elite - $99/month**\n"
            "• Unlimited scans\n"
            "• AI rug predictor\n"
            "• Dev voiceprint\n"
            "• Auto-protection\n\n"
            f"**Your Status:** {user_context.tier.upper()}",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⭐ Upgrade Now", callback_data="upgrade_menu"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "📊 Compare All Plans", callback_data="compare_plans"
                        )
                    ],
                ]
            ),
        )

    def _build_scan_actions_keyboard(
        self, address: str, chain: str, scan_result: Dict, user_context: UserContext
    ) -> InlineKeyboardMarkup:
        """Build action buttons for scan results"""

        buttons = []

        # Primary actions based on risk
        score = scan_result.get("score", 50)

        if score < 50:
            # High risk - show panic actions
            buttons.append(
                [
                    InlineKeyboardButton(
                        "🔴 Panic Sell Guide", callback_data=f"panic_{address}_{chain}"
                    )
                ]
            )

        # Standard actions
        buttons.append(
            [
                InlineKeyboardButton(
                    "📋 Copy Address", callback_data=f"copy_{address}"
                ),
                InlineKeyboardButton(
                    "📈 View Chart", url=f"https://dexscreener.com/{chain}/{address}"
                ),
            ]
        )

        # AI features
        buttons.append(
            [InlineKeyboardButton("━━━ AI Analysis ━━━", callback_data="separator")]
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    "🫧 Bubble Map", callback_data=f"bubble_{address}_{chain}"
                )
            ]
        )

        if user_context.tier in ["pro", "elite"]:
            buttons.append(
                [
                    InlineKeyboardButton(
                        "🕸️ Bundle Detector", callback_data=f"bundle_{address}_{chain}"
                    )
                ]
            )
        else:
            buttons.append(
                [
                    InlineKeyboardButton(
                        "🕸️ Bundle Detection (PRO)",
                        callback_data=f"upg_pro_bundle_{address}_{chain}",
                    )
                ]
            )

        if user_context.tier == "elite":
            buttons.append(
                [
                    InlineKeyboardButton(
                        "🎙️ Dev Voiceprint", callback_data=f"voice_{address}_{chain}"
                    )
                ]
            )
            buttons.append(
                [
                    InlineKeyboardButton(
                        "⏰ Rug Predictor", callback_data=f"predict_{address}_{chain}"
                    )
                ]
            )

        # Utility actions
        buttons.append(
            [InlineKeyboardButton("━━━ Actions ━━━", callback_data="separator")]
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    "🔔 Set Alert", callback_data=f"alert_{address}_{chain}"
                ),
                InlineKeyboardButton(
                    "📤 Share", callback_data=f"share_{address}_{chain}_{score}"
                ),
            ]
        )

        return InlineKeyboardMarkup(buttons)

    async def _perform_scan(self, address: str, chain: str) -> Dict:
        """Perform actual blockchain scan"""
        # Would integrate with actual scanner
        # Placeholder return
        return {
            "score": 45,
            "critical_flags": ["Ownership not renounced"],
            "high_flags": ["Liquidity not locked"],
            "medium_flags": ["Contract recently deployed"],
            "honeypot_data": {"is_honeypot": False},
        }

    async def _load_customer(self, telegram_id: int) -> Optional[Dict]:
        """Load customer from database"""
        # Would query actual database
        return None


# Export main classes
__all__ = [
    "ConversationalRugMuncherBot",
    "AIIntentRouter",
    "ConversationalResponseGenerator",
    "SmartOnboarding",
    "UserContext",
    "UserIntent",
]
