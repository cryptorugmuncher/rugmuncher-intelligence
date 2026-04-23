"""
RMI Bot Tools Integration Layer
=================================

This module provides the integration layer between the Rug Muncher Bot ecosystem
and the RMI OSINT/Tools stack.

Architecture:
    Bot Layer (Production/Extensions) → Integration Layer → Tools Layer (OSINT/AI/Blockchain)
    
Components:
    - ToolRegistry: Registry for all available tools
    - BotToolConnector: Connects bots to tools
    - OSINTIntegration: OSINT tools integration
    - AIIntegration: AI tool integrations (Kimi, OpenCode)
    - BlockchainIntegration: Blockchain analysis tools
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add paths for RMI tools
RMI_BASE = Path(__file__).parent.parent
sys.path.insert(0, str(RMI_BASE / "tools"))
sys.path.insert(0, str(RMI_BASE / "integrations" / "ai_tools"))
sys.path.insert(0, str(RMI_BASE / "integrations" / "blockchain"))


class ToolCategory(Enum):
    """Tool categories for organization"""
    OSINT = "osint"
    AI = "ai"
    BLOCKCHAIN = "blockchain"
    SECURITY = "security"
    ANALYSIS = "analysis"
    SOCIAL = "social"


@dataclass
class Tool:
    """Tool definition"""
    name: str
    category: ToolCategory
    module_path: str
    class_name: Optional[str] = None
    function_name: Optional[str] = None
    description: str = ""
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)


class ToolRegistry:
    """
    Central registry for all RMI tools.
    
    Manages tool discovery, configuration, and access.
    """
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._instances: Dict[str, Any] = {}
        self._discover_tools()
    
    def _discover_tools(self):
        """Auto-discover available tools"""
        
        # OSINT Tools
        self.register(Tool(
            name="maigret",
            category=ToolCategory.OSINT,
            module_path="rmi.tools.maigret",
            description="Social media account discovery via username"
        ))
        
        self.register(Tool(
            name="munchscan",
            category=ToolCategory.OSINT,
            module_path="rmi.tools.munchscan",
            description="Deep scanning and facial recognition"
        ))
        
        self.register(Tool(
            name="social_analyzer",
            category=ToolCategory.OSINT,
            module_path="rmi.tools.social_analyzer",
            description="Social media analysis"
        ))
        
        self.register(Tool(
            name="deepface",
            category=ToolCategory.OSINT,
            module_path="rmi.tools.deepface",
            description="Facial recognition and analysis"
        ))
        
        self.register(Tool(
            name="osint_tools",
            category=ToolCategory.OSINT,
            module_path="rmi.integrations.osint_tools",
            description="RMI OSINT integration tools"
        ))
        
        # AI Tools
        self.register(Tool(
            name="kimi_cli",
            category=ToolCategory.AI,
            module_path="rmi.integrations.ai_tools.kimi_launcher",
            class_name="KimiLauncher",
            description="Kimi CLI integration"
        ))
        
        self.register(Tool(
            name="opencode",
            category=ToolCategory.AI,
            module_path="rmi.integrations.ai_tools.opencode_launcher",
            class_name="OpenCodeLauncher",
            description="OpenCode AI integration"
        ))
        
        # Security/Analysis Tools from bot extensions
        self.register(Tool(
            name="bundling",
            category=ToolCategory.BLOCKCHAIN,
            module_path="rmi.bots.extensions.rugmuncher_bundling",
            description="Wallet bundling detection"
        ))
        
        self.register(Tool(
            name="threat_intel",
            category=ToolCategory.SECURITY,
            module_path="rmi.bots.extensions.rugmuncher_threat_intel",
            description="Threat intelligence analysis"
        ))
        
        self.register(Tool(
            name="predictor",
            category=ToolCategory.ANALYSIS,
            module_path="rmi.bots.extensions.rugmuncher_predictor",
            description="Token prediction models"
        ))
        
        self.register(Tool(
            name="voiceprint",
            category=ToolCategory.SECURITY,
            module_path="rmi.bots.extensions.rugmuncher_voiceprint",
            description="Voice analysis"
        ))
        
        self.register(Tool(
            name="scoring",
            category=ToolCategory.ANALYSIS,
            module_path="rmi.bots.extensions.rugmuncher_scoring",
            description="Token scoring system"
        ))
    
    def register(self, tool: Tool):
        """Register a tool"""
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name} ({tool.category.value})")
    
    def get(self, name: str) -> Optional[Tool]:
        """Get tool by name"""
        return self._tools.get(name)
    
    def list_by_category(self, category: ToolCategory) -> List[Tool]:
        """List tools by category"""
        return [t for t in self._tools.values() if t.category == category]
    
    def list_all(self) -> List[Tool]:
        """List all tools"""
        return list(self._tools.values())
    
    def get_instance(self, name: str) -> Any:
        """Get or create tool instance"""
        if name not in self._instances:
            tool = self.get(name)
            if not tool:
                raise ValueError(f"Tool not found: {name}")
            
            try:
                module = __import__(tool.module_path, fromlist=[tool.class_name or "main"])
                
                if tool.class_name:
                    cls = getattr(module, tool.class_name)
                    self._instances[name] = cls(**tool.config)
                elif tool.function_name:
                    self._instances[name] = getattr(module, tool.function_name)
                else:
                    self._instances[name] = module
                    
            except Exception as e:
                logger.error(f"Failed to load tool {name}: {e}")
                return None
        
        return self._instances.get(name)


class BotToolConnector:
    """
    Connects bots to the RMI tool registry.
    
    Provides unified interface for bots to access tools.
    """
    
    def __init__(self):
        self.registry = ToolRegistry()
        self._hooks: Dict[str, List[Callable]] = {}
    
    def call_tool(self, tool_name: str, method: str = None, **kwargs) -> Any:
        """
        Call a tool method
        
        Args:
            tool_name: Name of the tool
            method: Method to call (if class-based)
            **kwargs: Arguments to pass
        """
        instance = self.registry.get_instance(tool_name)
        
        if instance is None:
            raise RuntimeError(f"Tool {tool_name} not available")
        
        if method:
            if not hasattr(instance, method):
                raise AttributeError(f"Tool {tool_name} has no method {method}")
            return getattr(instance, method)(**kwargs)
        
        # If it's callable, call it directly
        if callable(instance):
            return instance(**kwargs)
        
        return instance
    
    def register_hook(self, event: str, callback: Callable):
        """Register event hook"""
        if event not in self._hooks:
            self._hooks[event] = []
        self._hooks[event].append(callback)
    
    def trigger_hook(self, event: str, **kwargs):
        """Trigger event hooks"""
        for hook in self._hooks.get(event, []):
            try:
                hook(**kwargs)
            except Exception as e:
                logger.error(f"Hook error for {event}: {e}")
    
    def get_tools_for_bot(self, bot_type: str) -> List[Tool]:
        """
        Get recommended tools for a specific bot type
        
        Args:
            bot_type: Type of bot (production, telegram, osint, etc.)
        """
        tool_map = {
            "production": [
                ToolCategory.BLOCKCHAIN,
                ToolCategory.ANALYSIS,
                ToolCategory.SECURITY
            ],
            "telegram": [
                ToolCategory.OSINT,
                ToolCategory.BLOCKCHAIN,
                ToolCategory.SOCIAL
            ],
            "osint": [
                ToolCategory.OSINT,
                ToolCategory.AI,
                ToolCategory.SECURITY
            ],
            "swarm": [
                ToolCategory.AI,
                ToolCategory.ANALYSIS,
                ToolCategory.OSINT
            ]
        }
        
        categories = tool_map.get(bot_type, [])
        tools = []
        for cat in categories:
            tools.extend(self.registry.list_by_category(cat))
        return tools


class OSINTIntegration:
    """
    Specialized integration for OSINT tools
    """
    
    def __init__(self, connector: BotToolConnector):
        self.connector = connector
    
    def search_username(self, username: str) -> Dict:
        """Search username across platforms"""
        return self.connector.call_tool("maigret", "search", username=username)
    
    def analyze_face(self, image_path: str) -> Dict:
        """Analyze face in image"""
        return self.connector.call_tool("deepface", "analyze", img_path=image_path)
    
    def run_munchscan(self, target: str, scan_type: str = "full") -> Dict:
        """Run munchscan on target"""
        return self.connector.call_tool("munchscan", "scan", target=target, type=scan_type)


class AIIntegration:
    """
    Specialized integration for AI tools
    """
    
    def __init__(self, connector: BotToolConnector):
        self.connector = connector
    
    def kimi_query(self, prompt: str, context: str = None) -> str:
        """Query Kimi AI"""
        return self.connector.call_tool("kimi_cli", "query", prompt=prompt, context=context)
    
    def opencode_query(self, prompt: str) -> str:
        """Query OpenCode AI"""
        return self.connector.call_tool("opencode", "query", prompt=prompt)


class BlockchainIntegration:
    """
    Specialized integration for blockchain tools
    """
    
    def __init__(self, connector: BotToolConnector):
        self.connector = connector
    
    def detect_bundling(self, token_address: str) -> Dict:
        """Detect wallet bundling"""
        return self.connector.call_tool("bundling", "detect", token_address=token_address)
    
    def get_threat_intel(self, address: str) -> Dict:
        """Get threat intelligence"""
        return self.connector.call_tool("threat_intel", "analyze", address=address)
    
    def predict_token(self, token_data: Dict) -> Dict:
        """Run token prediction"""
        return self.connector.call_tool("predictor", "predict", data=token_data)
    
    def score_token(self, token_address: str) -> Dict:
        """Score token safety"""
        return self.connector.call_tool("scoring", "score", address=token_address)


# Global connector instance
_connector: Optional[BotToolConnector] = None


def get_connector() -> BotToolConnector:
    """Get global connector instance"""
    global _connector
    if _connector is None:
        _connector = BotToolConnector()
    return _connector


# Convenience functions
def call_tool(tool_name: str, method: str = None, **kwargs) -> Any:
    """Call a tool via global connector"""
    return get_connector().call_tool(tool_name, method, **kwargs)


def get_osint() -> OSINTIntegration:
    """Get OSINT integration"""
    return OSINTIntegration(get_connector())


def get_ai() -> AIIntegration:
    """Get AI integration"""
    return AIIntegration(get_connector())


def get_blockchain() -> BlockchainIntegration:
    """Get blockchain integration"""
    return BlockchainIntegration(get_connector())


if __name__ == "__main__":
    # Demo usage
    connector = get_connector()
    
    print("=" * 60)
    print("RMI Bot Tools Integration")
    print("=" * 60)
    
    print("\n[All Registered Tools]")
    for tool in connector.registry.list_all():
        status = "✓" if tool.enabled else "✗"
        print(f"  {status} {tool.name:<20} ({tool.category.value})")
    
    print("\n[Tools by Category]")
    for cat in ToolCategory:
        tools = connector.registry.list_by_category(cat)
        print(f"\n  {cat.value.upper()}:")
        for tool in tools:
            print(f"    - {tool.name}")
    
    print("\n[Tools for Production Bot]")
    for tool in connector.get_tools_for_bot("production"):
        print(f"  - {tool.name}")
    
    print("\n" + "=" * 60)
