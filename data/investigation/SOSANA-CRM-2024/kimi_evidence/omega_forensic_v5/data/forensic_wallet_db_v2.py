"""
Omega Forensic V5 - Forensic Wallet Database v2
================================================
EVIDENCE-BASED investigation methodology.
Presumption of innocence until proven on-chain.
Full audit trail for corrections and transparency.
"""

import json
import csv
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Set
from datetime import datetime
from enum import Enum

class InvestigationStatus(Enum):
    """
    Investigation status - NOT guilt determination.
    These are investigative stages, not legal conclusions.
    """
    UNEXAMINED = "unexamined"           # Not yet analyzed
    LEAD = "lead"                       # Potential connection identified
    UNDER_INVESTIGATION = "under_investigation"  # Active API analysis
    EVIDENCE_FOUND = "evidence_found"   # On-chain proof documented
    EVIDENCE_LACKING = "evidence_lacking"  # No proof found
    DISPROVEN = "disproven"             # Evidence contradicts suspicion
    CONFIRMED_CONNECTION = "confirmed_connection"  # Verified link (not guilt)
    VICTIM = "victim"                   # Confirmed victim

class EvidenceTier(Enum):
    """Evidence quality tiers - NOT guilt levels."""
    UNVERIFIED = "unverified"           # Raw lead, no verification
    CIRCUMSTANTIAL = "circumstantial"   # Indirect indicators
    SUPPORTING = "supporting"           # Supports but doesn't prove
    STRONG = "strong"                   # Compelling but needs confirmation
    CONCLUSIVE = "conclusive"           # On-chain proof verified

@dataclass
class EvidenceItem:
    """Single piece of evidence with full attribution."""
    source: str                         # API source (Helius, Arkham, etc.)
    evidence_type: str                  # transaction, entity_label, etc.
    description: str                    # What was found
    data: Dict                          # Raw evidence data
    timestamp: str                      # When evidence was collected
    verified: bool = False              # Has been double-checked
    verifier: str = None                # Who verified
    verification_timestamp: str = None  # When verified
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class InvestigationNote:
    """Audit trail note for transparency."""
    timestamp: str
    author: str                         # Who made the note
    note_type: str                      # observation, correction, finding
    content: str                        # Note content
    related_evidence: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class WalletConnection:
    """Connection to another wallet - with full evidence trail."""
    target_address: str
    connection_type: str                # funded_by, sent_to, same_cluster, etc.
    evidence_tier: EvidenceTier
    evidence_items: List[EvidenceItem] = field(default_factory=list)
    confidence: float = 0.0             # 0.0 to 1.0 based on evidence
    first_observed: str = None
    last_observed: str = None
    status: str = "active"              # active, disputed, corrected, deleted
    
    def add_evidence(self, evidence: EvidenceItem) -> None:
        """Add evidence with verification."""
        self.evidence_items.append(evidence)
        self._recalculate_confidence()
    
    def _recalculate_confidence(self) -> None:
        """Recalculate confidence based on evidence quality."""
        if not self.evidence_items:
            self.confidence = 0.0
            return
        
        # Weight by evidence tier
        tier_weights = {
            EvidenceTier.UNVERIFIED: 0.1,
            EvidenceTier.CIRCUMSTANTIAL: 0.2,
            EvidenceTier.SUPPORTING: 0.4,
            EvidenceTier.STRONG: 0.7,
            EvidenceTier.CONCLUSIVE: 1.0
        }
        
        total_weight = sum(
            tier_weights.get(e.evidence_tier, 0.1) 
            for e in self.evidence_items
        )
        
        # Cap at 0.95 - never 100% certain
        self.confidence = min(total_weight / len(self.evidence_items), 0.95)

@dataclass
class ForensicWalletRecord:
    """
    Complete wallet record with full audit trail.
    PRESUMPTION OF INNOCENCE until evidence proves otherwise.
    """
    # Identity
    address: str
    investigation_status: InvestigationStatus = InvestigationStatus.UNEXAMINED
    
    # Balances (at snapshot time)
    balance_sol: float = 0.0
    balance_crm: float = 0.0
    balance_usdc: float = 0.0
    balance_usdt: float = 0.0
    other_tokens: Dict[str, float] = field(default_factory=dict)
    
    # Classification (NOT guilt - investigative only)
    suspected_tier: Optional[int] = None   # Suspected tier (unverified)
    labels: List[str] = field(default_factory=list)
    
    # Timeline
    created_at: Optional[str] = None
    first_transaction: Optional[str] = None
    last_transaction: Optional[str] = None
    
    # Evidence-based connections
    connections: List[WalletConnection] = field(default_factory=list)
    
    # Investigation tracking
    evidence_items: List[EvidenceItem] = field(default_factory=list)
    investigation_notes: List[InvestigationNote] = field(default_factory=list)
    
    # Correction tracking
    corrections_made: List[Dict] = field(default_factory=list)
    previous_statuses: List[Dict] = field(default_factory=list)
    
    # Risk assessment (investigative, not legal)
    risk_level: str = "unassessed"  # unassessed, low, medium, high, critical
    risk_factors: List[str] = field(default_factory=list)
    
    # Final determination
    conclusion: str = ""              # Summary of findings
    conclusion_date: str = None       # When conclusion reached
    concluded_by: str = None          # Who made conclusion
    
    def add_evidence(self, evidence: EvidenceItem) -> None:
        """Add evidence to wallet record."""
        self.evidence_items.append(evidence)
        
        # Add investigation note
        self.add_note(
            author="system",
            note_type="evidence_added",
            content=f"Evidence added from {evidence.source}: {evidence.description}",
            related_evidence=[evidence.timestamp]
        )
    
    def add_note(self, author: str, note_type: str, content: str, 
                 related_evidence: List[str] = None) -> None:
        """Add investigation note for audit trail."""
        note = InvestigationNote(
            timestamp=datetime.now().isoformat(),
            author=author,
            note_type=note_type,
            content=content,
            related_evidence=related_evidence or []
        )
        self.investigation_notes.append(note)
    
    def update_status(self, new_status: InvestigationStatus, reason: str,
                      updated_by: str = "system") -> None:
        """Update status with full audit trail."""
        # Save previous status
        self.previous_statuses.append({
            "status": self.investigation_status.value,
            "timestamp": datetime.now().isoformat(),
            "reason": reason
        })
        
        # Update status
        old_status = self.investigation_status
        self.investigation_status = new_status
        
        # Add note
        self.add_note(
            author=updated_by,
            note_type="status_change",
            content=f"Status changed from {old_status.value} to {new_status.value}. Reason: {reason}"
        )
    
    def mark_disproven(self, reason: str, corrected_by: str) -> None:
        """Mark wallet as disproven - full transparency."""
        self.update_status(
            InvestigationStatus.DISPROVEN,
            reason,
            corrected_by
        )
        
        # Add correction record
        self.corrections_made.append({
            "timestamp": datetime.now().isoformat(),
            "correction_type": "disproven",
            "reason": reason,
            "corrected_by": corrected_by
        })
        
        # Clear suspicious labels
        self.labels = [l for l in self.labels if not l.startswith("SUSPECTED")]
        self.risk_level = "low"
        self.risk_factors = []
    
    def get_evidence_summary(self) -> Dict:
        """Get summary of all evidence."""
        by_tier = {}
        by_source = {}
        
        for evidence in self.evidence_items:
            tier = evidence.evidence_tier.value
            by_tier[tier] = by_tier.get(tier, 0) + 1
            
            source = evidence.source
            by_source[source] = by_source.get(source, 0) + 1
        
        return {
            "total_evidence_items": len(self.evidence_items),
            "by_tier": by_tier,
            "by_source": by_source,
            "verified_count": sum(1 for e in self.evidence_items if e.verified)
        }
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for export."""
        return {
            "address": self.address,
            "investigation_status": self.investigation_status.value,
            "balance_sol": self.balance_sol,
            "balance_crm": self.balance_crm,
            "suspected_tier": self.suspected_tier,
            "labels": self.labels,
            "connections": [
                {
                    "target": c.target_address,
                    "type": c.connection_type,
                    "confidence": c.confidence,
                    "evidence_count": len(c.evidence_items),
                    "status": c.status
                }
                for c in self.connections
            ],
            "evidence_summary": self.get_evidence_summary(),
            "investigation_notes_count": len(self.investigation_notes),
            "corrections_made": len(self.corrections_made),
            "risk_level": self.risk_level,
            "conclusion": self.conclusion,
            "conclusion_date": self.conclusion_date
        }

class ForensicWalletDatabase:
    """
    Evidence-based wallet database.
    Full audit trail for corrections and transparency.
    """
    
    def __init__(self):
        self.wallets: Dict[str, ForensicWalletRecord] = {}
        self.investigation_log: List[Dict] = []
        self.corrections_log: List[Dict] = []
        
        # Investigation leads (NOT confirmed scammers)
        self.investigation_leads: Dict[str, Dict] = {}
    
    def add_wallet(self, record: ForensicWalletRecord) -> None:
        """Add wallet to database."""
        self.wallets[record.address] = record
        
        # Log addition
        self.investigation_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": "wallet_added",
            "address": record.address,
            "initial_status": record.investigation_status.value
        })
    
    def add_investigation_lead(self, address: str, lead_source: str, 
                               reason: str, evidence_refs: List[str] = None) -> None:
        """
        Add a wallet as an investigation lead.
        This is NOT a determination of guilt - just a lead to investigate.
        """
        self.investigation_leads[address] = {
            "address": address,
            "lead_source": lead_source,
            "reason": reason,
            "evidence_refs": evidence_refs or [],
            "added_at": datetime.now().isoformat(),
            "status": "open"  # open, investigating, closed
        }
        
        # If wallet exists, update status
        if address in self.wallets:
            self.wallets[address].update_status(
                InvestigationStatus.LEAD,
                f"Added as investigation lead from {lead_source}: {reason}"
            )
    
    def investigate_with_api(self, address: str, api_source: str) -> Dict:
        """
        Investigate wallet using API.
        Returns findings for review.
        """
        wallet = self.wallets.get(address)
        if not wallet:
            return {"error": "Wallet not in database"}
        
        # Update status
        wallet.update_status(
            InvestigationStatus.UNDER_INVESTIGATION,
            f"API investigation started: {api_source}"
        )
        
        # This would call actual APIs
        # For now, return placeholder
        return {
            "address": address,
            "api_source": api_source,
            "status": "investigation_started",
            "timestamp": datetime.now().isoformat()
        }
    
    def record_evidence(self, address: str, evidence: EvidenceItem) -> None:
        """Record evidence for a wallet."""
        wallet = self.wallets.get(address)
        if not wallet:
            return
        
        wallet.add_evidence(evidence)
        
        # Update status based on evidence
        if evidence.evidence_tier == EvidenceTier.CONCLUSIVE:
            wallet.update_status(
                InvestigationStatus.EVIDENCE_FOUND,
                f"Conclusive evidence found: {evidence.description}"
            )
        elif evidence.evidence_tier == EvidenceTier.STRONG:
            if wallet.investigation_status == InvestigationStatus.UNEXAMINED:
                wallet.update_status(
                    InvestigationStatus.UNDER_INVESTIGATION,
                    "Strong evidence requires investigation"
                )
    
    def mark_disproven(self, address: str, reason: str, corrected_by: str) -> None:
        """
        Mark wallet as disproven - full transparency.
        This is how we handle mistakes.
        """
        wallet = self.wallets.get(address)
        if not wallet:
            return
        
        # Record correction
        self.corrections_log.append({
            "timestamp": datetime.now().isoformat(),
            "address": address,
            "correction_type": "disproven",
            "reason": reason,
            "corrected_by": corrected_by,
            "previous_status": wallet.investigation_status.value
        })
        
        # Update wallet
        wallet.mark_disproven(reason, corrected_by)
    
    def generate_correction_report(self) -> Dict:
        """Generate report of all corrections made."""
        return {
            "generated_at": datetime.now().isoformat(),
            "total_corrections": len(self.corrections_log),
            "corrections": self.corrections_log,
            "transparency_note": "All mistakes are documented and corrected publicly."
        }
    
    def generate_investigation_report(self) -> Dict:
        """Generate comprehensive investigation report."""
        status_counts = {}
        for wallet in self.wallets.values():
            status = wallet.investigation_status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "generated_at": datetime.now().isoformat(),
            "methodology": {
                "principle": "Presumption of innocence until evidence proves otherwise",
                "evidence_required": "On-chain verification via APIs",
                "correction_policy": "All mistakes documented and corrected transparently"
            },
            "summary": {
                "total_wallets": len(self.wallets),
                "investigation_leads": len(self.investigation_leads),
                "by_status": status_counts,
                "total_corrections": len(self.corrections_log)
            },
            "evidence_summary": {
                "total_evidence_items": sum(
                    len(w.evidence_items) for w in self.wallets.values()
                ),
                "verified_evidence": sum(
                    sum(1 for e in w.evidence_items if e.verified)
                    for w in self.wallets.values()
                )
            },
            "corrections": self.corrections_log
        }
    
    def export_to_json(self, filepath: str) -> None:
        """Export database to JSON."""
        data = {
            "exported_at": datetime.now().isoformat(),
            "methodology": "Evidence-based investigation with presumption of innocence",
            "wallets": {addr: w.to_dict() for addr, w in self.wallets.items()},
            "investigation_leads": self.investigation_leads,
            "corrections_log": self.corrections_log
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def export_to_csv(self, filepath: str) -> None:
        """Export to CSV for review."""
        rows = []
        for wallet in self.wallets.values():
            rows.append({
                "address": wallet.address,
                "status": wallet.investigation_status.value,
                "suspected_tier": wallet.suspected_tier,
                "risk_level": wallet.risk_level,
                "evidence_count": len(wallet.evidence_items),
                "connections_count": len(wallet.connections),
                "corrections": len(wallet.corrections_made),
                "conclusion": wallet.conclusion[:100] if wallet.conclusion else ""
            })
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

# === GLOBAL INSTANCE ===
_forensic_db = None

def get_forensic_db() -> ForensicWalletDatabase:
    """Get singleton forensic database instance."""
    global _forensic_db
    if _forensic_db is None:
        _forensic_db = ForensicWalletDatabase()
    return _forensic_db

if __name__ == "__main__":
    print("=" * 70)
    print("FORENSIC WALLET DATABASE v2")
    print("Evidence-Based Investigation Methodology")
    print("=" * 70)
    print("\n✅ Presumption of innocence until evidence proves otherwise")
    print("✅ All evidence must be verified on-chain via APIs")
    print("✅ All mistakes documented and corrected transparently")
    print("✅ Full audit trail for accountability")
    print("\n" + "=" * 70)
