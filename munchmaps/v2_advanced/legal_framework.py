#!/usr/bin/env python3
"""
Legal Framework for MunchMaps V2
Data collection, privacy, and compliance
"""

from typing import Dict, List
from dataclasses import dataclass

@dataclass
class LegalDocument:
    name: str
    version: str
    last_updated: str
    purpose: str
    key_points: List[str]
    jurisdictions: List[str]
    compliance_frameworks: List[str]

# Legal Documentation
LEGAL_DOCUMENTS = {
    'terms_of_service': LegalDocument(
        name="Terms of Service",
        version="2.0",
        last_updated="2024-04-09",
        purpose="Define user rights and platform obligations",
        key_points=[
            "Platform provides blockchain analysis services only",
            "No financial advice provided",
            "Users responsible for their own investigations",
            "Data accuracy not guaranteed - always verify independently",
            "Prohibited uses: harassment, stalking, doxxing without cause",
            "Service availability not guaranteed",
            "API usage subject to rate limits"
        ],
        jurisdictions=["Global", "USA", "EU", "UK"],
        compliance_frameworks=["GDPR", "CCPA", "ePrivacy"]
    ),
    
    'privacy_policy': LegalDocument(
        name="Privacy Policy",
        version="2.0",
        last_updated="2024-04-09",
        purpose="Explain data collection and usage practices",
        key_points=[
            "We collect only blockchain data (already public)",
            "User-submitted scam reports require explicit consent",
            "No PII collected without explicit consent",
            "Data shared with law enforcement only under legal obligation",
            "Users can request data deletion",
            "Analytics cookies used for platform improvement",
            "Third-party service providers under DPAs"
        ],
        jurisdictions=["Global", "USA", "EU", "UK"],
        compliance_frameworks=["GDPR", "CCPA", "PIPEDA"]
    ),
    
    'data_collection_consent': LegalDocument(
        name="Data Collection Consent Agreement",
        version="2.0",
        last_updated="2024-04-09",
        purpose="Obtain informed consent for data collection",
        key_points=[
            "We analyze public blockchain data only",
            "Wallet addresses are public information",
            "Transaction history is immutable and public",
            "No private keys or sensitive data accessed",
            "Aggregated patterns may be shared with community",
            "Individual wallet data kept confidential",
            "Consent can be withdrawn at any time"
        ],
        jurisdictions=["Global"],
        compliance_frameworks=["GDPR Article 6", "GDPR Article 9"]
    ),
    
    'law_enforcement_policy': LegalDocument(
        name="Law Enforcement Cooperation Policy",
        version="1.0",
        last_updated="2024-04-09",
        purpose="Define cooperation with legal authorities",
        key_points=[
            "Free access for verified law enforcement agencies",
            "Court orders required for user data disclosure",
            "Emergency disclosure for imminent harm",
            "Transparency reports published annually",
            "User notification when legally permitted",
            "No voluntary surveillance programs",
            "Due process respected in all jurisdictions"
        ],
        jurisdictions=["USA", "EU", "UK", "APAC"],
        compliance_frameworks=["MLA", "EU-US Data Privacy Framework"]
    ),
    
    'open_source_disclaimer': LegalDocument(
        name="Open Source Software Disclaimer",
        version="1.0",
        last_updated="2024-04-09",
        purpose="Licensing and liability for open source components",
        key_points=[
            "Core algorithms open source under MIT License",
            "No warranty provided - use at own risk",
            "Attribution required for derivative works",
            "Proprietary data sources remain closed",
            "Community contributions welcome",
            "Security audits by third parties",
            "Bug bounty program available"
        ],
        jurisdictions=["Global"],
        compliance_frameworks=["OSI", "FSF"]
    )
}

# Data Collection Consent Framework
CONSENT_FRAMEWORK = {
    'public_blockchain_data': {
        'category': 'Public Data',
        'consent_required': False,
        'legal_basis': 'Legitimate Interest / Public Information',
        'description': 'Data already publicly available on blockchains',
        'data_types': [
            'Wallet addresses',
            'Transaction hashes',
            'Transaction amounts',
            'Timestamps',
            'Smart contract interactions'
        ],
        'usage': [
            'Pattern analysis',
            'Risk scoring',
            'Clustering algorithms',
            'Visualization'
        ],
        'retention': 'Indefinite (blockchain is immutable)',
        'sharing': 'Aggregated insights only',
        'withdrawal': 'Not applicable - public data'
    },
    
    'user_submitted_reports': {
        'category': 'User Generated Content',
        'consent_required': True,
        'consent_type': 'Explicit Opt-In',
        'legal_basis': 'Consent (GDPR Art. 6(1)(a))',
        'description': 'Scam reports and suspicious activity tips',
        'data_types': [
            'Reporter contact information',
            'Scam details and evidence',
            'Victim statements',
            'Suspected wallet addresses',
            'Screenshots and documents'
        ],
        'usage': [
            'Investigation support',
            'Pattern recognition',
            'Database enrichment',
            'Alert generation'
        ],
        'retention': '7 years or until consent withdrawn',
        'sharing': 'Anonymized for research, identifiable for LE',
        'withdrawal': 'Full deletion within 30 days of request'
    },
    
    'enrichment_data': {
        'category': 'Third-Party Enrichment',
        'consent_required': True,
        'consent_type': 'Terms of Service Agreement',
        'legal_basis': 'Contractual Necessity (GDPR Art. 6(1)(b))',
        'description': 'Data from partners and public sources',
        'data_types': [
            'Exchange labels',
            'Protocol tags',
            'Risk scores from partners',
            'Sanctions list data',
            'OSINT aggregations'
        ],
        'sources': [
            'Cryptocurrency exchanges (with data agreements)',
            'DeFi protocols',
            'Security researchers',
            'Public databases',
            'Chainalysis/Elliptic (enterprise only)'
        ],
        'usage': [
            'Enhanced labeling',
            'Risk assessment',
            'Attribution assistance'
        ],
        'retention': 'As per source agreement',
        'sharing': 'No onward sharing without consent',
        'withdrawal': 'Depends on source terms'
    },
    
    'usage_analytics': {
        'category': 'Platform Analytics',
        'consent_required': True,
        'consent_type': 'Cookie Consent',
        'legal_basis': 'Consent (GDPR Art. 6(1)(a)) / Legitimate Interest',
        'description': 'Platform usage and performance data',
        'data_types': [
            'IP addresses (anonymized)',
            'Browser type',
            'Feature usage',
            'Search queries',
            'Error logs'
        ],
        'usage': [
            'Platform improvement',
            'Performance optimization',
            'Feature prioritization',
            'Security monitoring'
        ],
        'retention': '26 months',
        'sharing': 'Aggregated statistics only',
        'withdrawal': 'Immediate upon opt-out'
    }
}

# Compliance Checklist
COMPLIANCE_CHECKLIST = {
    'gdpr': {
        'name': 'General Data Protection Regulation (EU)',
        'requirements': [
            'Lawful basis for processing identified',
            'Data minimization practiced',
            'Purpose limitation enforced',
            'Accuracy maintained',
            'Storage limitation applied',
            'Integrity and confidentiality ensured',
            'Accountability demonstrated'
        ],
        'user_rights': [
            'Right to access',
            'Right to rectification',
            'Right to erasure',
            'Right to restrict processing',
            'Right to data portability',
            'Right to object',
            'Rights related to automated decision-making'
        ],
        'status': 'Compliant'
    },
    
    'ccpa': {
        'name': 'California Consumer Privacy Act',
        'requirements': [
            'Privacy notice provided',
            'Opt-out mechanism available',
            'Non-discrimination for opt-outs',
            'Data sale disclosure'
        ],
        'user_rights': [
            'Right to know',
            'Right to delete',
            'Right to opt-out',
            'Right to non-discrimination'
        ],
        'status': 'Compliant'
    },
    
    'aml_cft': {
        'name': 'Anti-Money Laundering / Counter-Terrorist Financing',
        'requirements': [
            'Sanctions screening implemented',
            'Suspicious activity monitoring',
            'Law enforcement cooperation',
            'Record retention (5-7 years)',
            'Risk-based approach'
        ],
        'obligations': [
            'Report suspicious transactions',
            'Maintain audit trails',
            'Customer due diligence',
            'Ongoing monitoring'
        ],
        'status': 'Compliant - Services exempt as software-only'
    },
    
    'bSA': {
        'name': 'Bank Secrecy Act (USA)',
        'requirements': [
            'MSB registration if applicable',
            'AML program',
            'Suspicious Activity Reports',
            'Currency Transaction Reports'
        ],
        'note': 'Software-only analytics not classified as MSB',
        'status': 'Exempt - Software-only service'
    }
}

# Jurisdiction-Specific Requirements
JURISDICTION_REQUIREMENTS = {
    'usa': {
        'regulators': ['FinCEN', 'OFAC', 'SEC', 'CFTC'],
        'key_laws': ['BSA', 'USA PATRIOT Act', 'OFAC Sanctions'],
        'data_localization': False,
        'special_notes': 'Free speech protections for public data analysis'
    },
    
    'eu': {
        'regulators': ['EDPB', 'National DPAs', 'Europol'],
        'key_laws': ['GDPR', 'ePrivacy Directive', 'AMLD5', 'AMLD6'],
        'data_localization': True,
        'special_notes': 'Right to be forgotten applies to personal data'
    },
    
    'uk': {
        'regulators': ['ICO', 'FCA', 'NCA'],
        'key_laws': ['UK GDPR', 'MLRs 2017', 'Sanctions Act'],
        'data_localization': False,
        'special_notes': 'Post-Brexit alignment with EU standards'
    },
    
    'singapore': {
        'regulators': ['MAS', 'PDPC'],
        'key_laws': ['PSA', 'PDPA'],
        'data_localization': False,
        'special_notes': 'Pro-crypto regulatory environment'
    },
    
    'uae': {
        'regulators': ['VARA', 'FSRA'],
        'key_laws': ['Dubai VA Regulations'],
        'data_localization': False,
        'special_notes': 'Growing crypto hub with clear regulations'
    }
}

# Open Source Licensing
OPEN_SOURCE_LICENSE = """
MIT License - MunchMaps Core

Copyright (c) 2024 Rug Munch Media LLC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

DATA DISCLAIMER: This software analyzes public blockchain data only. No
private information is accessed. Users are responsible for ensuring their
use complies with applicable laws.

ATTRIBUTION: Use of this software must include attribution to MunchMaps.

DERIVATIVE WORKS: Modifications and derivative works must be shared under
the same license.
"""

def generate_consent_form(tier: str) -> str:
    """Generate consent form for specific tier"""
    form = []
    form.append("MUNCHMAPS DATA COLLECTION CONSENT")
    form.append("=" * 60)
    form.append("\nBy using MunchMaps services, you consent to:")
    
    for category, details in CONSENT_FRAMEWORK.items():
        form.append(f"\n{details['category']}")
        form.append(f"  Legal Basis: {details['legal_basis']}")
        form.append(f"  Consent Required: {'Yes' if details['consent_required'] else 'No'}")
        form.append(f"  Data Types: {', '.join(details.get('data_types', []))}")
        form.append(f"  Usage: {', '.join(details.get('usage', [])[:2])}...")
    
    form.append("\n\nYou have the right to:")
    form.append("  - Withdraw consent at any time")
    form.append("  - Request data deletion")
    form.append("  - Access your data")
    form.append("  - Object to processing")
    form.append("  - Lodge a complaint with supervisory authority")
    
    return '\n'.join(form)

if __name__ == "__main__":
    print(generate_consent_form("professional"))
    
    print("\n\nCompliance Status:")
    print("=" * 60)
    for framework, details in COMPLIANCE_CHECKLIST.items():
        print(f"{framework.upper()}: {details['status']}")
