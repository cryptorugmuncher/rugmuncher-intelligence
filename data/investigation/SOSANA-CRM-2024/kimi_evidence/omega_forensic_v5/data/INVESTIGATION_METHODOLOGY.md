# Omega Forensic V5 - Investigation Methodology

## Core Principles

### 1. Presumption of Innocence
**Every wallet is presumed innocent until evidence proves otherwise.**

- Wallets added to the database are **INVESTIGATION LEADS**, not guilty parties
- No wallet is flagged as "scammer" without verified on-chain evidence
- Labels like "suspected" indicate investigative status, not legal conclusion

### 2. Evidence-Based Conclusions
**All determinations must be based on verified on-chain evidence.**

| Evidence Tier | Description | Use in Conclusions |
|---------------|-------------|-------------------|
| UNVERIFIED | Raw lead, no verification | Cannot use |
| CIRCUMSTANTIAL | Indirect indicators | Supporting only |
| SUPPORTING | Supports but doesn't prove | Part of pattern |
| STRONG | Compelling but needs confirmation | With verification |
| CONCLUSIVE | On-chain proof verified | Primary basis |

### 3. Full Transparency on Corrections
**When we make mistakes, we document and correct them openly.**

- All corrections are logged with:
  - What was wrong
  - Why it was wrong
  - Who made the correction
  - When it was corrected
- Correction reports are public
- No shame in being wrong - only in hiding it

---

## Investigation Workflow

### Step 1: Add as Investigation Lead
```python
workflow.add_investigation_lead(
    address="WalletAddress...",
    reason="Received funds from wallet flagged in intelligence",
    lead_source="intelligence_report"
)
```
**Status**: `UNEXAMINED` → `LEAD`  
**Note**: This is NOT a determination of guilt. Just a lead to investigate.

### Step 2: Verify with APIs
```python
workflow.verify_with_apis("WalletAddress...")
```
**APIs Used**:
- Helius (transaction history)
- Arkham (entity intelligence)
- MistTrack (risk scoring)
- ChainAbuse (scam reports)
- Solscan (account data)

**Status**: `LEAD` → `UNDER_INVESTIGATION`

### Step 3: Record Evidence
```python
workflow.record_evidence(
    address="WalletAddress...",
    source="Helius",
    evidence_type="transaction",
    description="Received 1M CRM from 8eVZa7b...",
    raw_data={"tx_sig": "abc123", "amount": 1000000},
    evidence_tier="strong"
)
```
**Status**: Evidence recorded but NOT YET VERIFIED

### Step 4: Verify Evidence
```python
workflow.verify_evidence(
    address="WalletAddress...",
    evidence_timestamp="2026-03-28T09:19:00Z",
    verifier="Senior_Analyst",
    verification_notes="Confirmed on Solscan - transaction verified"
)
```
**Requirement**: All evidence must be independently verified before use in conclusions.

### Step 5: Reach Conclusion
```python
workflow.reach_conclusion(
    address="WalletAddress...",
    conclusion="Connection to scammer network confirmed via verified transaction.",
    concluded_by="Lead_Investigator"
)
```
**Status**: Based on verified evidence only  
**Note**: Subject to correction if new evidence emerges

### Step 6: Correction (If Wrong)
```python
workflow.correct_mistake(
    address="WalletAddress...",
    correction_reason="Further analysis shows wallet is exchange hot wallet, not scammer",
    corrected_by="Lead_Investigator"
)
```
**Transparency**: Full documentation of what was wrong and why

---

## Investigation Status Definitions

| Status | Meaning | Can Accuse? |
|--------|---------|-------------|
| UNEXAMINED | Not yet analyzed | ❌ NO |
| LEAD | Potential connection identified | ❌ NO |
| UNDER_INVESTIGATION | Active API analysis | ❌ NO |
| EVIDENCE_FOUND | Evidence documented | ❌ NO (needs verification) |
| EVIDENCE_LACKING | No proof found | ❌ NO |
| DISPROVEN | Evidence contradicts suspicion | ❌ NO (cleared) |
| CONFIRMED_CONNECTION | Verified link (not guilt) | ⚠️ Report only |
| VICTIM | Confirmed victim | ❌ NO |

**Important**: Even `CONFIRMED_CONNECTION` does not mean "guilty." It means "verified connection to known scammer wallet." Legal guilt requires court determination.

---

## Correction Policy

### When to Correct
- New evidence contradicts previous finding
- Original evidence found to be incorrect
- Wallet identified as legitimate (exchange, known entity)
- Any doubt about accuracy

### How to Correct
1. Document what was wrong
2. Explain why it was wrong
3. State the correct finding
4. Log who made correction and when
5. Update all reports

### Correction Log Format
```json
{
  "timestamp": "2026-03-28T10:00:00Z",
  "address": "WalletAddress...",
  "correction_type": "disproven",
  "previous_status": "CONFIRMED_CONNECTION",
  "new_status": "DISPROVEN",
  "reason": "Further analysis shows wallet is MEXC exchange hot wallet",
  "corrected_by": "Lead_Investigator",
  "transparency_note": "This correction has been publicly documented"
}
```

---

## API Verification Requirements

### Minimum Evidence for Each Claim

| Claim Type | Required Evidence |
|------------|-------------------|
| "Received from scammer" | Transaction signature + verification |
| "Sent to scammer" | Transaction signature + verification |
| "Same cluster" | Multiple shared counterparties + timing analysis |
| "Botnet link" | Deployment pattern + timing correlation |
| "Exchange connection" | Entity label from Arkham or exchange confirmation |

### Verification Process
1. Collect evidence from primary API
2. Cross-reference with secondary API
3. Verify transaction on blockchain explorer
4. Document verification in evidence item
5. Only use verified evidence in conclusions

---

## Reporting Standards

### What to Include
- All evidence used (with sources)
- All evidence NOT used (and why)
- All corrections made
- Confidence levels for each claim
- Clear distinction between fact and inference

### What NOT to Include
- Unverified claims
- Hearsay or rumors
- Assumptions without evidence
- Legal conclusions ("guilty", "criminal")

### Sample Report Language

✅ **Correct**:
> "Wallet 8eVZa7b... received 1M CRM from wallet HLnpSz9h... on March 28, 2026 at 09:19 UTC (Transaction: RXEMcfj...). This transaction was verified on Solscan and Helius. The sending wallet HLnpSz9h... has been confirmed through verified transactions to be part of the scammer network."

❌ **Incorrect**:
> "Wallet 8eVZa7b... is a scammer wallet that stole 1M CRM."

---

## Accountability

### Every Decision is Traceable
- Who made the decision
- When it was made
- What evidence was used
- Why that conclusion was reached

### Every Mistake is Documented
- What was wrong
- Why it was wrong
- How it was corrected
- Who made the correction

### No Anonymous Accusations
- All investigators identified
- All evidence attributed
- All corrections signed

---

## Summary

1. **Presume innocence** - Wallets are leads, not guilty parties
2. **Require evidence** - Only verified on-chain evidence counts
3. **Verify everything** - Double-check all evidence
4. **Correct openly** - Document all mistakes
5. **Report carefully** - Distinguish fact from inference
6. **Be accountable** - Every decision traceable

**The goal is truth, not convictions.**
