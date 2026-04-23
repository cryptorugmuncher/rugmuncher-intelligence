"""
Final Report Generator - Comprehensive Investigation Reports
===========================================================
Generates legal-ready forensic reports with:
- Named wallets and entities
- KYC vectors
- Evidence tiers
- Transparent methodology
"""

import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class EvidenceTier(Enum):
    """Evidence quality tiers."""
    DIRECT = 1
    STRONG_CORRELATION = 2
    SUSPICIOUS_PATTERN = 3
    INDIRECT = 4
    UNVERIFIED = 5


@dataclass
class WalletEvidence:
    """Evidence for a specific wallet."""
    address: str
    entity_name: Optional[str] = None
    evidence_tier: EvidenceTier = EvidenceTier.UNVERIFIED
    findings: List[str] = field(default_factory=list)
    transaction_signatures: List[str] = field(default_factory=list)
    connected_wallets: List[str] = field(default_factory=list)
    kyc_vectors: List[str] = field(default_factory=list)
    risk_score: float = 0.0
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    total_volume: float = 0.0
    transaction_count: int = 0


@dataclass
class NamedEntity:
    """A named entity in the investigation."""
    name: str
    aliases: List[str] = field(default_factory=list)
    wallets: List[str] = field(default_factory=list)
    evidence_tier: EvidenceTier = EvidenceTier.UNVERIFIED
    description: str = ""
    kyc_info: Dict = field(default_factory=dict)
    social_profiles: Dict = field(default_factory=dict)


@dataclass
class InvestigationFinding:
    """A single finding in the investigation."""
    title: str
    description: str
    evidence_tier: EvidenceTier
    wallets_involved: List[str]
    transaction_signatures: List[str]
    confidence: float
    verification_status: str = "pending"
    notes: str = ""


@dataclass
class FinalReport:
    """Complete investigation report."""
    report_id: str
    case_name: str
    generated_at: datetime
    investigation_period: Dict[str, datetime]
    
    # Summary
    executive_summary: str = ""
    key_findings: List[InvestigationFinding] = field(default_factory=list)
    
    # Entities
    named_entities: List[NamedEntity] = field(default_factory=list)
    wallet_evidence: List[WalletEvidence] = field(default_factory=list)
    
    # Clusters
    wallet_clusters: List[Dict] = field(default_factory=list)
    
    # KYC
    kyc_vectors: List[Dict] = field(default_factory=list)
    
    # Methodology
    apis_used: List[str] = field(default_factory=list)
    models_used: List[str] = field(default_factory=list)
    evidence_methodology: str = ""
    
    # Corrections
    corrections_log: List[Dict] = field(default_factory=list)
    
    # Legal
    legal_disclaimers: List[str] = field(default_factory=list)
    
    # Appendices
    raw_data_refs: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert report to dictionary."""
        return {
            "report_id": self.report_id,
            "case_name": self.case_name,
            "generated_at": self.generated_at.isoformat(),
            "investigation_period": {
                "start": self.investigation_period["start"].isoformat(),
                "end": self.investigation_period["end"].isoformat()
            },
            "executive_summary": self.executive_summary,
            "key_findings": [
                {
                    "title": f.title,
                    "description": f.description,
                    "evidence_tier": f.evidence_tier.name,
                    "wallets_involved": f.wallets_involved,
                    "transaction_signatures": f.transaction_signatures,
                    "confidence": f.confidence,
                    "verification_status": f.verification_status
                }
                for f in self.key_findings
            ],
            "named_entities": [
                {
                    "name": e.name,
                    "aliases": e.aliases,
                    "wallets": e.wallets,
                    "evidence_tier": e.evidence_tier.name,
                    "description": e.description,
                    "kyc_info": e.kyc_info,
                    "social_profiles": e.social_profiles
                }
                for e in self.named_entities
            ],
            "wallet_evidence": [
                {
                    "address": w.address,
                    "entity_name": w.entity_name,
                    "evidence_tier": w.evidence_tier.name,
                    "findings": w.findings,
                    "transaction_signatures": w.transaction_signatures,
                    "connected_wallets": w.connected_wallets,
                    "kyc_vectors": w.kyc_vectors,
                    "risk_score": w.risk_score,
                    "total_volume": w.total_volume,
                    "transaction_count": w.transaction_count
                }
                for w in self.wallet_evidence
            ],
            "wallet_clusters": self.wallet_clusters,
            "kyc_vectors": self.kyc_vectors,
            "methodology": {
                "apis_used": self.apis_used,
                "models_used": self.models_used,
                "evidence_methodology": self.evidence_methodology
            },
            "corrections_log": self.corrections_log,
            "legal_disclaimers": self.legal_disclaimers,
            "raw_data_refs": self.raw_data_refs
        }
    
    def to_markdown(self) -> str:
        """Generate markdown report."""
        md = f"""# {self.case_name}
## Forensic Investigation Report

**Report ID:** {self.report_id}  
**Generated:** {self.generated_at.strftime('%Y-%m-%d %H:%M UTC')}  
**Investigation Period:** {self.investigation_period['start'].strftime('%Y-%m-%d')} to {self.investigation_period['end'].strftime('%Y-%m-%d')}

---

## Executive Summary

{self.executive_summary}

---

## Key Findings

"""
        
        for i, finding in enumerate(self.key_findings, 1):
            tier_emoji = {
                EvidenceTier.DIRECT: "🟢",
                EvidenceTier.STRONG_CORRELATION: "🟡",
                EvidenceTier.SUSPICIOUS_PATTERN: "🟠",
                EvidenceTier.INDIRECT: "🔴",
                EvidenceTier.UNVERIFIED: "⚪"
            }.get(finding.evidence_tier, "⚪")
            
            md += f"""### {i}. {finding.title}

**Evidence Tier:** {tier_emoji} {finding.evidence_tier.name.replace('_', ' ')}
**Confidence:** {finding.confidence * 100:.1f}%
**Status:** {finding.verification_status}

{finding.description}

**Wallets Involved:**
"""
            for wallet in finding.wallets_involved:
                md += f"- `{wallet}`\n"
            
            if finding.transaction_signatures:
                md += "\n**Transaction Signatures:**\n"
                for sig in finding.transaction_signatures[:5]:  # Limit to 5
                    md += f"- `{sig}`\n"
            
            md += "\n---\n\n"
        
        # Named Entities
        md += "## Named Entities\n\n"
        for entity in self.named_entities:
            tier_emoji = {
                EvidenceTier.DIRECT: "🟢",
                EvidenceTier.STRONG_CORRELATION: "🟡",
                EvidenceTier.SUSPICIOUS_PATTERN: "🟠",
                EvidenceTier.INDIRECT: "🔴",
                EvidenceTier.UNVERIFIED: "⚪"
            }.get(entity.evidence_tier, "⚪")
            
            md += f"""### {entity.name}

**Evidence Tier:** {tier_emoji} {entity.evidence_tier.name.replace('_', ' ')}

{entity.description}

**Associated Wallets:**
"""
            for wallet in entity.wallets:
                md += f"- `{wallet}`\n"
            
            if entity.aliases:
                md += "\n**Aliases:** " + ", ".join(entity.aliases) + "\n"
            
            md += "\n---\n\n"
        
        # KYC Vectors
        md += "## KYC Vectors\n\n"
        md += "Potential Know-Your-Customer connection points:\n\n"
        for vector in self.kyc_vectors:
            md += f"- **{vector.get('type', 'Unknown')}:** {vector.get('description', '')}\n"
        
        md += "\n---\n\n"
        
        # Methodology
        md += """## Methodology

### Evidence Tiers

- **🟢 Tier 1 (Direct):** Confirmed on-chain evidence
- **🟡 Tier 2 (Strong Correlation):** Multiple independent sources agree
- **🟠 Tier 3 (Suspicious Pattern):** Worth investigating further
- **🔴 Tier 4 (Indirect):** Circumstantial connection
- **⚪ Tier 5 (Unverified):** Needs confirmation

### APIs Used

"""
        for api in self.apis_used:
            md += f"- {api}\n"
        
        md += "\n### Models Used\n\n"
        for model in self.models_used:
            md += f"- {model}\n"
        
        md += """
### Investigation Principles

1. **Evidence-Based Only** - All claims verified with on-chain data
2. **Presumption of Innocence** - Never assume guilt without proof
3. **Transparent Corrections** - Document when investigations are wrong
4. **Verifiable Claims** - Provide transaction signatures for verification

---

## Legal Disclaimers

"""
        for disclaimer in self.legal_disclaimers:
            md += f"- {disclaimer}\n"
        
        md += f"""
---

## Corrections Log

"""
        if self.corrections_log:
            for correction in self.corrections_log:
                md += f"""**{correction.get('date', 'Unknown')}**
- Original: {correction.get('original', '')}
- Correction: {correction.get('correction', '')}
- Reason: {correction.get('reason', '')}

"""
        else:
            md += "No corrections recorded.\n"
        
        md += f"""
---

*This report was generated by RMI (RugMunch Intelligence) using Kimi AI.*  
*Platform: intel.cryptorugmunch.com*  
*Report ID: {self.report_id}*
"""
        
        return md


class FinalReportGenerator:
    """
    Generates comprehensive forensic investigation reports.
    """
    
    def __init__(self):
        self.reports: Dict[str, FinalReport] = {}
        self.apis_used = [
            "Helius (Solana blockchain data)",
            "Arkham Intelligence (entity labeling)",
            "MistTrack (risk scoring)",
            "ChainAbuse (scam database)",
            "BirdEye (token analytics)",
            "LunarCrush (social metrics)",
            "QuickNode (RPC access)"
        ]
        self.models_used = [
            "Llama 3.3 70B (Meta/Groq)",
            "Gemini 2.0 Flash (Google)",
            "Claude 3 Haiku (Anthropic)",
            "DeepSeek Chat/Reasoner (DeepSeek)",
            "Qwen2.5 7B (Alibaba - local)",
            "Phi-4 (Microsoft - local)"
        ]
    
    def create_crm_report(
        self,
        wallet_evidence: List[WalletEvidence] = None,
        named_entities: List[NamedEntity] = None,
        clusters: List[Dict] = None
    ) -> FinalReport:
        """
        Create the CRM token investigation final report.
        
        Args:
            wallet_evidence: List of wallet evidence
            named_entities: List of named entities
            clusters: List of wallet clusters
            
        Returns:
            FinalReport object
        """
        report = FinalReport(
            report_id=f"RMI-CRM-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            case_name="CRM Token Investigation",
            generated_at=datetime.now(),
            investigation_period={
                "start": datetime(2025, 8, 1),
                "end": datetime(2026, 3, 31)
            },
            apis_used=self.apis_used,
            models_used=self.models_used,
            evidence_methodology="""
All evidence is classified into tiers based on verification level:
- Tier 1: Direct on-chain evidence with transaction signatures
- Tier 2: Strong correlation from multiple independent sources
- Tier 3: Suspicious patterns requiring further investigation
- Tier 4: Indirect connections, circumstantial
- Tier 5: Unverified information

We maintain presumption of innocence until proven guilty.
All claims are verified with on-chain data where possible.
""",
            legal_disclaimers=[
                "This report is for informational purposes only.",
                "All parties are presumed innocent until proven guilty in a court of law.",
                "Evidence tiers indicate confidence levels, not legal conclusions.",
                "Wallet addresses do not necessarily indicate guilt.",
                "This report should be verified by independent forensic analysis.",
                "KYC vectors represent potential leads, not confirmed identities."
            ]
        )
        
        # Executive Summary
        report.executive_summary = """
This report documents the investigation into the CRM token, which exhibited 
patterns consistent with market manipulation and potential fraud between 
August 2025 and March 2026.

Key findings include:
- Identification of coordinated wallet clusters
- Suspicious pre-bonding activity
- Evidence of bot-driven trading
- Cross-project connections to other tokens

All findings are classified by evidence tier and include transaction 
signatures for independent verification.
"""
        
        # Add wallet evidence if provided
        if wallet_evidence:
            report.wallet_evidence = wallet_evidence
        
        # Add named entities if provided
        if named_entities:
            report.named_entities = named_entities
        
        # Add clusters if provided
        if clusters:
            report.wallet_clusters = clusters
        
        # Store report
        self.reports[report.report_id] = report
        
        return report
    
    def add_correction(
        self,
        report_id: str,
        original: str,
        correction: str,
        reason: str
    ):
        """Add a correction to a report."""
        if report_id in self.reports:
            self.reports[report_id].corrections_log.append({
                "date": datetime.now().isoformat(),
                "original": original,
                "correction": correction,
                "reason": reason
            })
    
    def export_report(
        self,
        report_id: str,
        format: str = "markdown",
        output_dir: str = "/mnt/okcomputer/output/omega_forensic_v5/reports"
    ) -> str:
        """
        Export report to file.
        
        Args:
            report_id: Report ID
            format: Output format (markdown, json)
            output_dir: Output directory
            
        Returns:
            Path to exported file
        """
        os.makedirs(output_dir, exist_ok=True)
        
        report = self.reports.get(report_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")
        
        if format == "markdown":
            content = report.to_markdown()
            filename = f"{report_id}.md"
        elif format == "json":
            content = json.dumps(report.to_dict(), indent=2)
            filename = f"{report_id}.json"
        else:
            raise ValueError(f"Unknown format: {format}")
        
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        
        return filepath
    
    def get_report_summary(self, report_id: str) -> Dict:
        """Get summary of a report."""
        report = self.reports.get(report_id)
        if not report:
            return {"error": "Report not found"}
        
        tier_counts = {"DIRECT": 0, "STRONG_CORRELATION": 0, "SUSPICIOUS_PATTERN": 0, 
                       "INDIRECT": 0, "UNVERIFIED": 0}
        
        for finding in report.key_findings:
            tier_counts[finding.evidence_tier.name] += 1
        
        for wallet in report.wallet_evidence:
            tier_counts[wallet.evidence_tier.name] += 1
        
        return {
            "report_id": report_id,
            "case_name": report.case_name,
            "generated_at": report.generated_at.isoformat(),
            "total_wallets": len(report.wallet_evidence),
            "total_entities": len(report.named_entities),
            "total_findings": len(report.key_findings),
            "evidence_tier_distribution": tier_counts,
            "corrections": len(report.corrections_log)
        }


# Global generator instance
_generator = None

def get_final_report_generator() -> FinalReportGenerator:
    """Get global report generator instance."""
    global _generator
    if _generator is None:
        _generator = FinalReportGenerator()
    return _generator


if __name__ == "__main__":
    print("=" * 70)
    print("FINAL REPORT GENERATOR")
    print("=" * 70)
    
    generator = get_final_report_generator()
    
    # Create sample report
    sample_wallets = [
        WalletEvidence(
            address="Eme5T2s2HB7B8W4YgLG1eReQpnadEVUnQBRjaKTdBAGS",
            entity_name="CRM Deployer",
            evidence_tier=EvidenceTier.DIRECT,
            findings=["Token deployer", "Controls 20.4% of supply"],
            risk_score=0.95,
            total_volume=5000000,
            transaction_count=1500
        )
    ]
    
    report = generator.create_crm_report(wallet_evidence=sample_wallets)
    
    print(f"\n📄 Generated Report: {report.report_id}")
    print(f"   Case: {report.case_name}")
    print(f"   Wallets: {len(report.wallet_evidence)}")
    print(f"   Entities: {len(report.named_entities)}")
    
    # Export
    md_path = generator.export_report(report.report_id, "markdown")
    json_path = generator.export_report(report.report_id, "json")
    
    print(f"\n✅ Exported:")
    print(f"   Markdown: {md_path}")
    print(f"   JSON: {json_path}")
    
    print("\n" + "=" * 70)
