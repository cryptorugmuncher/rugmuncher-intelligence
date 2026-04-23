#!/usr/bin/env python3
"""
RMI Evidence Integration Module

This module integrates the CRM forensic evidence vault into the RMI platform,
providing:
- Database import tools for the 40+ wallet addresses
- Interactive 5-tier hierarchy visualizations
- Real-time wallet monitoring and alerting
- KYC subpoena tracking and management
- Investigation workspace dashboard

Usage:
    from evidence_integration import EvidenceIntegration
    
    integration = EvidenceIntegration(supabase_url, supabase_key)
    await integration.initialize()
    await integration.start_monitoring()
"""

from .crm_evidence_importer import CRMEvidenceVault, EvidenceImporter
from .tier_hierarchy_visualization import TierHierarchyVisualizer
from .wallet_monitoring_system import WalletMonitoringSystem, WebhookServer
from .kyc_subpoena_dashboard import SubpoenaManager, SubpoenaDashboard
from .investigation_workspace import InvestigationWorkspace, EvidencePackageGenerator
from .sosana_syndicate_evidence import SOSANASyndicateEvidence
from .crm_sosana_connection_map import CRMSOSANAConnectionMap
from .bot_autonomous_infrastructure import (
    BotCollaborationNetwork,
    AutonomousBotSwarm,
    HeliusProvisioner,
    QuickNodeProvisioner,
    CodeInterpreter,
    BOT_TEMPLATES
)

__version__ = "1.1.0"
__all__ = [
    "CRMEvidenceVault",
    "EvidenceImporter", 
    "TierHierarchyVisualizer",
    "WalletMonitoringSystem",
    "WebhookServer",
    "SubpoenaManager",
    "SubpoenaDashboard",
    "InvestigationWorkspace",
    "EvidencePackageGenerator",
    "SOSANASyndicateEvidence",
    "CRMSOSANAConnectionMap",
    "BotCollaborationNetwork",
    "AutonomousBotSwarm",
    "HeliusProvisioner",
    "QuickNodeProvisioner",
    "CodeInterpreter",
    "BOT_TEMPLATES",
    "EvidenceIntegration"
]


class EvidenceIntegration:
    """
    Master integration class that coordinates all evidence tools
    """
    
    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        helius_api_key: str = None,
        telegram_bot_token: str = None,
        telegram_chat_id: str = None
    ):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.helius_api_key = helius_api_key
        
        # Initialize components
        self.vault = CRMEvidenceVault()
        self.importer = EvidenceImporter(supabase_url, supabase_key)
        self.visualizer = TierHierarchyVisualizer()
        self.subpoena_manager = SubpoenaManager(supabase_url, supabase_key)
        self.workspace = InvestigationWorkspace()
        
        # Monitoring (optional - requires Helius API)
        self.monitoring = None
        if helius_api_key:
            self.monitoring = WalletMonitoringSystem(
                helius_api_key=helius_api_key,
                supabase_url=supabase_url,
                supabase_key=supabase_key,
                telegram_bot_token=telegram_bot_token,
                telegram_chat_id=telegram_chat_id
            )
    
    async def initialize(self):
        """Initialize all evidence systems"""
        print("[EvidenceIntegration] Initializing...")
        
        # Import evidence to Supabase
        print("[EvidenceIntegration] Importing evidence vault...")
        result = await self.importer.import_to_supabase()
        print(f"[EvidenceIntegration] Import complete: {len(result['success'])} tables updated")
        
        # Load wallets into monitoring if available
        if self.monitoring:
            print("[EvidenceIntegration] Loading wallets into monitoring...")
            wallets = self.monitoring.load_wallets_from_supabase()
            print(f"[EvidenceIntegration] {len(wallets)} wallets loaded for monitoring")
        
        print("[EvidenceIntegration] Initialization complete")
    
    async def start_monitoring(self):
        """Start real-time wallet monitoring"""
        if not self.monitoring:
            raise ValueError("Monitoring not configured - Helius API key required")
        
        print("[EvidenceIntegration] Starting wallet monitoring...")
        await self.monitoring.start_monitoring()
    
    def generate_visualizations(self, output_dir: str = "./visualizations") -> dict:
        """Generate all visualization files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        files = {}
        
        # Tier hierarchy
        viz_files = self.visualizer.export_files(output_dir)
        files.update(viz_files)
        
        # KYC dashboard
        dashboard = SubpoenaDashboard(self.subpoena_manager)
        kyc_path = os.path.join(output_dir, "kyc_dashboard.html")
        dashboard.export_dashboard(kyc_path)
        files["kyc_dashboard"] = kyc_path
        
        # Investigation workspace
        workspace_path = os.path.join(output_dir, "investigation_workspace.html")
        self.workspace.export_dashboard(workspace_path)
        files["investigation_workspace"] = workspace_path
        
        return files
    
    def generate_evidence_package(self, output_dir: str = "./evidence_package") -> dict:
        """Generate complete evidence package for legal proceedings"""
        generator = EvidencePackageGenerator()
        return generator.generate_evidence_package(output_dir)
    
    def get_statistics(self) -> dict:
        """Get comprehensive statistics"""
        return {
            "evidence_vault": self.vault.get_statistics(),
            "subpoenas": self.subpoena_manager.get_statistics() if hasattr(self.subpoena_manager, 'subpoenas') else {},
            "monitoring": self.monitoring.get_alert_statistics() if self.monitoring else {}
        }
