"""
🔌 Extension Plugin Loader
===========================
Dynamically loads the 22 bot extensions from bots/extensions/ as plugins.
Each extension is wrapped in a unified interface for the orchestrator.
"""

import os
import sys
import importlib.util
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger("orchestrator.plugins")

# Add bots path for extension imports
sys.path.insert(0, str(Path(__file__).parent.parent / "bots"))
sys.path.insert(0, str(Path(__file__).parent.parent / "bots" / "extensions"))


@dataclass
class PluginCapability:
    name: str
    description: str
    handler: Callable
    category: str
    bot_roles: List[str]  # which bot roles can use this
    async_handler: bool = True


class ExtensionPluginManager:
    """
    Loads and manages bot extensions as unified plugins.
    """

    EXTENSION_DIR = Path(__file__).parent.parent / "bots" / "extensions"

    # Map of extension filenames to their exposed capabilities
    EXTENSION_REGISTRY = {
        "rugmuncher_scoring": {
            "capabilities": ["token_score", "risk_assess"],
            "roles": ["sentry", "oracle", "auditor"],
            "description": "Token safety scoring engine",
        },
        "rugmuncher_bundling": {
            "capabilities": ["detect_bundling", "wallet_cluster"],
            "roles": ["warden", "investigator"],
            "description": "Wallet bundling detection",
        },
        "rugmuncher_predictor": {
            "capabilities": ["predict_rug", "price_forecast"],
            "roles": ["oracle"],
            "description": "ML-based rug pull prediction",
        },
        "rugmuncher_threat_intel": {
            "capabilities": ["threat_lookup", "ioc_check", "attack_pattern"],
            "roles": ["warden", "sentry"],
            "description": "Threat intelligence database",
        },
        "rugmuncher_protector": {
            "capabilities": ["shield_token", "blocklist_check"],
            "roles": ["sentry", "warden", "auditor"],
            "description": "Security protection layer",
        },
        "rugmuncher_vampire": {
            "capabilities": ["detect_vampire", "liquidity_drain"],
            "roles": ["warden"],
            "description": "Vampire attack detection",
        },
        "rugmuncher_alert_router": {
            "capabilities": ["route_alert", "severity_classify"],
            "roles": ["herald", "sentry"],
            "description": "Alert distribution router",
        },
        "rugmuncher_telegram_bridge": {
            "capabilities": ["tg_broadcast", "tg_format"],
            "roles": ["herald"],
            "description": "Telegram channel bridge",
        },
        "rugmuncher_twitter": {
            "capabilities": ["twitter_scan", "sentiment_gauge", "shill_detect"],
            "roles": ["vanguard", "herald"],
            "description": "Twitter/X intelligence",
        },
        "rugmuncher_webhook": {
            "capabilities": ["webhook_send", "webhook_format"],
            "roles": ["herald"],
            "description": "Webhook dispatcher",
        },
        "rugmuncher_holders": {
            "capabilities": ["holder_analyze", "whale_track", "concentration_check"],
            "roles": ["oracle", "vanguard", "investigator"],
            "description": "Holder analysis and whale tracking",
        },
        "rugmuncher_ai_router": {
            "capabilities": ["model_route", "fallback_switch"],
            "roles": ["all"],
            "description": "AI model routing and fallback",
        },
        "rugmuncher_advanced_apis": {
            "capabilities": ["api_enrich", "multi_source_fetch"],
            "roles": ["investigator", "auditor", "oracle"],
            "description": "Advanced API integrations",
        },
        "rugmuncher_data_cleansing": {
            "capabilities": ["clean_data", "dedupe", "normalize"],
            "roles": ["archivist"],
            "description": "Data cleansing pipeline",
        },
        "rugmuncher_data_sanitizer": {
            "capabilities": ["sanitize_input", "validate_schema"],
            "roles": ["archivist", "sentry"],
            "description": "Data sanitization",
        },
        "rugmuncher_features": {
            "capabilities": ["feature_flag", "capability_check"],
            "roles": ["all"],
            "description": "Feature flag management",
        },
        "rugmuncher_security_hardening": {
            "capabilities": ["harden_config", "security_audit"],
            "roles": ["warden", "auditor", "sentry"],
            "description": "Security hardening checks",
        },
        "rugmuncher_subscription": {
            "capabilities": ["sub_check", "tier_verify"],
            "roles": ["all"],
            "description": "Subscription management",
        },
        "rugmuncher_setup": {
            "capabilities": ["bot_setup", "config_validate"],
            "roles": ["all"],
            "description": "Setup utilities",
        },
        "rugmuncher_ollama_addon": {
            "capabilities": ["local_llm", "offline_analyze"],
            "roles": ["all"],
            "description": "Ollama local LLM integration",
        },
        "rugmuncher_tor_proxy": {
            "capabilities": ["tor_route", "anonymize_request"],
            "roles": ["investigator", "warden"],
            "description": "Tor proxy routing",
        },
        "rugmuncher_voiceprint": {
            "capabilities": ["voice_analyze", "biometric_check"],
            "roles": ["vanguard"],
            "description": "Voice biometrics",
        },
    }

    def __init__(self):
        self.plugins: Dict[str, Any] = {}
        self.capabilities: Dict[str, PluginCapability] = {}
        self._load_extensions()

    def _load_extensions(self):
        """Attempt to load each extension module."""
        for ext_name, meta in self.EXTENSION_REGISTRY.items():
            filepath = self.EXTENSION_DIR / f"{ext_name}.py"
            if not filepath.exists():
                logger.warning(f"Extension file not found: {filepath}")
                continue

            try:
                spec = importlib.util.spec_from_file_location(ext_name, filepath)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.plugins[ext_name] = module
                logger.info(f"✅ Loaded extension: {ext_name}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load {ext_name}: {e}")
                # Still register capabilities with a fallback handler
                self.plugins[ext_name] = None

    def get_capabilities_for_role(self, role: str) -> List[str]:
        """Get capability names available to a bot role."""
        caps = []
        for ext_name, meta in self.EXTENSION_REGISTRY.items():
            if role in meta["roles"] or "all" in meta["roles"]:
                caps.extend(meta["capabilities"])
        return caps

    def get_extension_meta(self, ext_name: str) -> Optional[Dict]:
        return self.EXTENSION_REGISTRY.get(ext_name)

    def list_all_capabilities(self) -> Dict[str, List[str]]:
        """Return all capabilities grouped by extension."""
        result = {}
        for ext_name, meta in self.EXTENSION_REGISTRY.items():
            result[ext_name] = meta["capabilities"]
        return result

    def is_loaded(self, ext_name: str) -> bool:
        return self.plugins.get(ext_name) is not None

    def get_load_status(self) -> Dict[str, bool]:
        """Return load status for all extensions."""
        return {name: self.is_loaded(name) for name in self.EXTENSION_REGISTRY}
