"""
Omega Forensic V5 - Investigation Workflow
===========================================
Proper forensic methodology:
1. Presumption of innocence
2. Evidence-based conclusions
3. Full transparency on corrections
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

from forensic_wallet_db_v2 import (
    ForensicWalletDatabase,
    ForensicWalletRecord,
    InvestigationStatus,
    EvidenceTier,
    EvidenceItem,
    get_forensic_db
)

class InvestigationWorkflow:
    """
    Proper forensic investigation workflow.
    Every step documented. Every correction transparent.
    """
    
    def __init__(self):
        self.db = get_forensic_db()
        self.investigator_name = "Omega Forensic V5"
    
    # =========================================================================
    # STEP 1: ADD AS LEAD (NOT guilty - just a lead to investigate)
    # =========================================================================
    def add_investigation_lead(self, address: str, reason: str, 
                               lead_source: str = "intelligence") -> Dict:
        """
        Add wallet as investigation lead.
        THIS IS NOT A DETERMINATION OF GUILT.
        """
        # Create wallet record if doesn't exist
        if address not in self.db.wallets:
            wallet = ForensicWalletRecord(
                address=address,
                investigation_status=InvestigationStatus.UNEXAMINED
            )
            self.db.add_wallet(wallet)
        
        # Add as lead
        self.db.add_investigation_lead(
            address=address,
            lead_source=lead_source,
            reason=reason
        )
        
        wallet = self.db.wallets[address]
        
        return {
            "status": "lead_added",
            "address": address,
            "investigation_status": wallet.investigation_status.value,
            "note": "This wallet has been added as an INVESTIGATION LEAD only. "
                    "No determination of guilt has been made.",
            "next_step": "Run API verification to collect evidence"
        }
    
    # =========================================================================
    # STEP 2: VERIFY WITH APIs (Evidence collection)
    # =========================================================================
    def verify_with_apis(self, address: str) -> Dict:
        """
        Verify wallet using all available APIs.
        Collect evidence, don't jump to conclusions.
        """
        wallet = self.db.wallets.get(address)
        if not wallet:
            return {"error": "Wallet not in database"}
        
        # Update status
        wallet.update_status(
            InvestigationStatus.UNDER_INVESTIGATION,
            "API verification started",
            self.investigator_name
        )
        
        findings = {
            "address": address,
            "verification_started": datetime.now().isoformat(),
            "apis_checked": [],
            "evidence_collected": [],
            "findings": []
        }
        
        # This would call actual APIs
        # For now, document the process
        
        wallet.add_note(
            author=self.investigator_name,
            note_type="verification_started",
            content="API verification process initiated. Checking Helius, Arkham, MistTrack, etc."
        )
        
        return findings
    
    # =========================================================================
    # STEP 3: RECORD EVIDENCE (Document what was found)
    # =========================================================================
    def record_evidence(self, address: str, source: str, 
                       evidence_type: str, description: str,
                       raw_data: Dict, evidence_tier: str) -> Dict:
        """
        Record evidence found during investigation.
        """
        wallet = self.db.wallets.get(address)
        if not wallet:
            return {"error": "Wallet not in database"}
        
        # Create evidence item
        evidence = EvidenceItem(
            source=source,
            evidence_type=evidence_type,
            description=description,
            data=raw_data,
            timestamp=datetime.now().isoformat(),
            verified=False  # Must be verified separately
        )
        
        # Set evidence tier
        try:
            evidence.evidence_tier = EvidenceTier(evidence_tier)
        except:
            evidence.evidence_tier = EvidenceTier.UNVERIFIED
        
        # Record evidence
        wallet.add_evidence(evidence)
        self.db.record_evidence(address, evidence)
        
        return {
            "status": "evidence_recorded",
            "address": address,
            "evidence_tier": evidence_tier,
            "description": description,
            "note": "Evidence recorded but NOT YET VERIFIED. "
                    "Must be double-checked before use in conclusions."
        }
    
    # =========================================================================
    # STEP 4: VERIFY EVIDENCE (Double-check everything)
    # =========================================================================
    def verify_evidence(self, address: str, evidence_timestamp: str,
                       verifier: str, verification_notes: str) -> Dict:
        """
        Verify evidence - must be double-checked.
        """
        wallet = self.db.wallets.get(address)
        if not wallet:
            return {"error": "Wallet not in database"}
        
        # Find evidence item
        for evidence in wallet.evidence_items:
            if evidence.timestamp == evidence_timestamp:
                evidence.verified = True
                evidence.verifier = verifier
                evidence.verification_timestamp = datetime.now().isoformat()
                
                wallet.add_note(
                    author=verifier,
                    note_type="evidence_verified",
                    content=f"Evidence verified: {verification_notes}",
                    related_evidence=[evidence_timestamp]
                )
                
                return {
                    "status": "evidence_verified",
                    "address": address,
                    "verified_by": verifier,
                    "note": "Evidence has been independently verified."
                }
        
        return {"error": "Evidence not found"}
    
    # =========================================================================
    # STEP 5: REACH CONCLUSION (Based on verified evidence only)
    # =========================================================================
    def reach_conclusion(self, address: str, conclusion: str,
                        concluded_by: str) -> Dict:
        """
        Reach conclusion based on verified evidence.
        """
        wallet = self.db.wallets.get(address)
        if not wallet:
            return {"error": "Wallet not in database"}
        
        # Check for verified evidence
        verified_evidence = [e for e in wallet.evidence_items if e.verified]
        
        if not verified_evidence:
            return {
                "error": "Cannot reach conclusion without verified evidence",
                "address": address,
                "evidence_count": len(wallet.evidence_items),
                "verified_count": 0
            }
        
        # Set conclusion
        wallet.conclusion = conclusion
        wallet.conclusion_date = datetime.now().isoformat()
        wallet.concluded_by = concluded_by
        
        # Update status based on conclusion
        if "connection confirmed" in conclusion.lower():
            wallet.update_status(
                InvestigationStatus.CONFIRMED_CONNECTION,
                f"Conclusion reached: {conclusion}",
                concluded_by
            )
        elif "no evidence" in conclusion.lower():
            wallet.update_status(
                InvestigationStatus.EVIDENCE_LACKING,
                f"Conclusion reached: {conclusion}",
                concluded_by
            )
        
        wallet.add_note(
            author=concluded_by,
            note_type="conclusion_reached",
            content=f"CONCLUSION: {conclusion}",
            related_evidence=[e.timestamp for e in verified_evidence]
        )
        
        return {
            "status": "conclusion_reached",
            "address": address,
            "conclusion": conclusion,
            "based_on_verified_evidence": len(verified_evidence),
            "note": "Conclusion reached based on verified evidence. "
                    "Subject to correction if new evidence emerges."
        }
    
    # =========================================================================
    # STEP 6: CORRECTION (If we got it wrong - FULL TRANSPARENCY)
    # =========================================================================
    def correct_mistake(self, address: str, correction_reason: str,
                       corrected_by: str) -> Dict:
        """
        Correct a mistake - full transparency.
        THIS IS HOW WE HANDLE BEING WRONG.
        """
        wallet = self.db.wallets.get(address)
        if not wallet:
            return {"error": "Wallet not in database"}
        
        # Record the correction
        previous_status = wallet.investigation_status.value
        
        self.db.mark_disproven(address, correction_reason, corrected_by)
        
        # Add detailed correction note
        wallet.add_note(
            author=corrected_by,
            note_type="CORRECTION",
            content=f"CORRECTION MADE: {correction_reason}. "
                    f"Previous status was {previous_status}. "
                    f"Wallet has been cleared of suspicion."
        )
        
        return {
            "status": "CORRECTION_MADE",
            "address": address,
            "previous_status": previous_status,
            "new_status": wallet.investigation_status.value,
            "correction_reason": correction_reason,
            "corrected_by": corrected_by,
            "correction_timestamp": datetime.now().isoformat(),
            "transparency_note": "This correction has been documented in the public record. "
                                "All investigations contain errors - we correct them openly."
        }
    
    # =========================================================================
    # REPORTING
    # =========================================================================
    def generate_transparency_report(self) -> Dict:
        """
        Generate full transparency report including all corrections.
        """
        report = self.db.generate_investigation_report()
        
        # Add transparency section
        report["transparency"] = {
            "methodology": {
                "presumption": "All wallets presumed innocent until evidence proves otherwise",
                "evidence_standard": "Only verified on-chain evidence accepted",
                "correction_policy": "All mistakes documented and corrected publicly",
                "accountability": "Every decision traceable to investigator"
            },
            "corrections": self.db.corrections_log,
            "total_corrections": len(self.db.corrections_log),
            "correction_rate": len(self.db.corrections_log) / max(len(self.db.wallets), 1)
        }
        
        return report
    
    def export_transparency_report(self, filepath: str) -> None:
        """Export transparency report."""
        report = self.generate_transparency_report()
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

# === EXAMPLE WORKFLOW ===

def example_workflow():
    """Example of proper investigation workflow."""
    workflow = InvestigationWorkflow()
    
    print("=" * 70)
    print("EXAMPLE INVESTIGATION WORKFLOW")
    print("=" * 70)
    
    # Step 1: Add as lead
    print("\n1️⃣ ADD AS INVESTIGATION LEAD")
    result = workflow.add_investigation_lead(
        address="ExampleWallet1234567890123456789012345678",
        reason="Received funds from suspected scammer wallet",
        lead_source="transaction_analysis"
    )
    print(f"   Status: {result['investigation_status']}")
    print(f"   Note: {result['note']}")
    
    # Step 2: Verify with APIs
    print("\n2️⃣ VERIFY WITH APIs")
    result = workflow.verify_with_apis("ExampleWallet1234567890123456789012345678")
    print(f"   Verification started")
    
    # Step 3: Record evidence
    print("\n3️⃣ RECORD EVIDENCE")
    result = workflow.record_evidence(
        address="ExampleWallet1234567890123456789012345678",
        source="Helius",
        evidence_type="transaction",
        description="Received 1M CRM from 8eVZa7b...",
        raw_data={"tx_sig": "abc123", "amount": 1000000},
        evidence_tier="strong"
    )
    print(f"   Evidence tier: {result['evidence_tier']}")
    
    # Step 4: Verify evidence
    print("\n4️⃣ VERIFY EVIDENCE")
    wallet = workflow.db.wallets["ExampleWallet1234567890123456789012345678"]
    if wallet.evidence_items:
        result = workflow.verify_evidence(
            address="ExampleWallet1234567890123456789012345678",
            evidence_timestamp=wallet.evidence_items[0].timestamp,
            verifier="Senior_Analyst",
            verification_notes="Confirmed on Solscan - transaction verified"
        )
        print(f"   Evidence verified by: {result['verified_by']}")
    
    # Step 5: Reach conclusion
    print("\n5️⃣ REACH CONCLUSION")
    result = workflow.reach_conclusion(
        address="ExampleWallet1234567890123456789012345678",
        conclusion="Connection to scammer network confirmed via verified transaction. "
                   "Wallet received 1M CRM from known bridge wallet 8eVZa7b...",
        concluded_by="Lead_Investigator"
    )
    print(f"   Conclusion: {result['conclusion'][:50]}...")
    
    # Step 6: Correction (if needed)
    print("\n6️⃣ CORRECTION (if we got it wrong)")
    print("   (Skipping - no correction needed in this example)")
    
    print("\n" + "=" * 70)
    print("WORKFLOW COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    example_workflow()
