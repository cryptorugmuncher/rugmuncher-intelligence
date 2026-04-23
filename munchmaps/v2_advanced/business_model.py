#!/usr/bin/env python3
"""
MunchMaps V2 Business Model
Subscription tiers, pricing, and service offerings
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class SubscriptionTier(Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    LAW_ENFORCEMENT = "law_enforcement"
    CUSTOM = "custom"

@dataclass
class ServiceTier:
    name: str
    monthly_price_usd: int
    annual_price_usd: int
    max_addresses_per_scan: int
    max_scans_per_month: int
    chains_supported: List[str]
    features: List[str]
    api_access: bool
    priority_support: bool
    white_label: bool
    data_retention_days: int
    report_export_formats: List[str]
    custom_integrations: bool
    dedicated_manager: bool
    
# Service Tiers Definition
SERVICE_TIERS = {
    SubscriptionTier.FREE: ServiceTier(
        name="Free",
        monthly_price_usd=0,
        annual_price_usd=0,
        max_addresses_per_scan=3,
        max_scans_per_month=10,
        chains_supported=['ethereum'],
        features=[
            'Basic wallet analysis',
            'Risk score calculation',
            'Simple clustering',
            'Community support'
        ],
        api_access=False,
        priority_support=False,
        white_label=False,
        data_retention_days=7,
        report_export_formats=['json'],
        custom_integrations=False,
        dedicated_manager=False
    ),
    
    SubscriptionTier.STARTER: ServiceTier(
        name="Starter",
        monthly_price_usd=49,
        annual_price_usd=470,  # 20% discount
        max_addresses_per_scan=25,
        max_scans_per_month=50,
        chains_supported=['ethereum', 'bsc', 'polygon'],
        features=[
            'Multi-chain analysis (3 chains)',
            'Wallet type classification',
            'CEX funding detection',
            'Fresh wallet identification',
            'Email support'
        ],
        api_access=False,
        priority_support=False,
        white_label=False,
        data_retention_days=30,
        report_export_formats=['json', 'pdf'],
        custom_integrations=False,
        dedicated_manager=False
    ),
    
    SubscriptionTier.PROFESSIONAL: ServiceTier(
        name="Professional",
        monthly_price_usd=199,
        annual_price_usd=1910,  # 20% discount
        max_addresses_per_scan=100,
        max_scans_per_month=200,
        chains_supported=['ethereum', 'solana', 'bsc', 'polygon', 'tron'],
        features=[
            'All 5 chains supported',
            'Full wallet type classification (33 types)',
            'Temporal timeline playback',
            'Multi-hop relationship tracing',
            'Statistical anomaly detection',
            'Cross-chain correlation',
            'Pig butcherer tracking',
            'API access (1000 calls/day)',
            'Priority email support',
            'Custom alert rules'
        ],
        api_access=True,
        priority_support=True,
        white_label=False,
        data_retention_days=90,
        report_export_formats=['json', 'pdf', 'csv', 'graphml'],
        custom_integrations=False,
        dedicated_manager=False
    ),
    
    SubscriptionTier.ENTERPRISE: ServiceTier(
        name="Enterprise",
        monthly_price_usd=999,
        annual_price_usd=9590,  # 20% discount
        max_addresses_per_scan=1000,
        max_scans_per_month=1000,
        chains_supported=['ethereum', 'solana', 'bsc', 'polygon', 'tron', 'bitcoin', 'avalanche', 'arbitrum', 'optimism'],
        features=[
            'All chains supported',
            'Unlimited wallet types',
            'Advanced threat intelligence',
            'Real-time monitoring',
            'Custom ML models',
            'Full API access (unlimited)',
            'White-label options',
            '24/7 priority support',
            'Dedicated account manager',
            'Custom integrations',
            'On-premise deployment option',
            'SLA guarantees'
        ],
        api_access=True,
        priority_support=True,
        white_label=True,
        data_retention_days=365,
        report_export_formats=['json', 'pdf', 'csv', 'graphml', 'xlsx', 'api'],
        custom_integrations=True,
        dedicated_manager=True
    ),
    
    SubscriptionTier.LAW_ENFORCEMENT: ServiceTier(
        name="Law Enforcement",
        monthly_price_usd=0,  # Free for verified LE
        annual_price_usd=0,
        max_addresses_per_scan=5000,
        max_scans_per_month=10000,
        chains_supported=['ethereum', 'solana', 'bsc', 'polygon', 'tron', 'bitcoin'],
        features=[
            'Full platform access',
            'Priority processing',
            'Evidence-grade reports',
            'Expert witness support',
            'Training materials',
            'Direct analyst consultation',
            'International cooperation support',
            'Sanctions screening',
            'Terrorist financing alerts',
            'Regulatory compliance reports'
        ],
        api_access=True,
        priority_support=True,
        white_label=False,
        data_retention_days=2555,  # 7 years
        report_export_formats=['json', 'pdf', 'csv', 'court-admissible'],
        custom_integrations=True,
        dedicated_manager=True
    )
}

# Deep Scan Add-ons
DEEP_SCAN_PACKAGES = {
    'forensic_analysis': {
        'name': 'Forensic Deep Dive',
        'description': 'Multi-hop tracing, temporal analysis, behavioral clustering',
        'price_per_address_usd': 5,
        'min_addresses': 10,
        'includes': [
            '3-hop relationship mapping',
            '30-day timeline playback',
            'Behavioral fingerprinting',
            'Cross-chain bridge analysis',
            'Statistical anomaly report'
        ]
    },
    
    'threat_assessment': {
        'name': 'Threat Intelligence Report',
        'description': 'Full threat actor classification and risk assessment',
        'price_per_address_usd': 10,
        'min_addresses': 5,
        'includes': [
            'All 33 wallet type classifications',
            'Nation-state actor screening',
            'Sanctions list checking',
            'Terrorist financing indicators',
            'Organized crime connections',
            'Priority threat scoring'
        ]
    },
    
    'pig_butcherer_investigation': {
        'name': 'Pig Butcherer Specialist Package',
        'description': 'Specialized analysis for romance scam/pig butcherer operations',
        'price_per_address_usd': 15,
        'min_addresses': 3,
        'includes': [
            'Tron USDT flow analysis',
            'Victim identification patterns',
            'CEX cashout tracking',
            'Operator network mapping',
            'Recovery assistance report',
            'Law enforcement referral pack'
        ]
    },
    
    'enterprise_monitoring': {
        'name': 'Continuous Monitoring',
        'description': 'Ongoing surveillance of wallet clusters',
        'price_per_month_usd': 500,
        'includes': [
            'Real-time transaction alerts',
            'New wallet detection',
            'Pattern change alerts',
            'Weekly intelligence briefings',
            'Custom dashboard'
        ]
    }
}

# Professional Services
PROFESSIONAL_SERVICES = {
    'expert_witness': {
        'name': 'Expert Witness Testimony',
        'rate_per_hour_usd': 500,
        'minimum_hours': 4,
        'description': 'Court testimony for crypto investigations'
    },
    
    'investigation_support': {
        'name': 'Investigation Support',
        'rate_per_hour_usd': 250,
        'minimum_hours': 10,
        'description': 'Analyst support for complex cases'
    },
    
    'training': {
        'name': 'Platform Training',
        'rate_per_session_usd': 2000,
        'duration': '4 hours',
        'attendees': 'Up to 20',
        'description': 'Comprehensive platform usage training'
    },
    
    'custom_development': {
        'name': 'Custom Development',
        'rate_per_hour_usd': 300,
        'minimum_hours': 40,
        'description': 'Custom features and integrations'
    }
}

# API Pricing
API_PRICING = {
    'free': {
        'calls_per_day': 100,
        'rate_limit': '10/minute',
        'price_per_month': 0
    },
    'starter': {
        'calls_per_day': 1000,
        'rate_limit': '60/minute',
        'price_per_month': 49
    },
    'professional': {
        'calls_per_day': 10000,
        'rate_limit': '600/minute',
        'price_per_month': 199
    },
    'enterprise': {
        'calls_per_day': 'Unlimited',
        'rate_limit': '6000/minute',
        'price_per_month': 999
    }
}

# Data Collection Consent Tiers
DATA_CONSENT_TIERS = {
    'public_only': {
        'name': 'Public Blockchain Only',
        'description': 'Only on-chain public data',
        'consent_required': False,
        'data_sources': ['blockchain_explorers', 'public_apis'],
        'available_in': ['free', 'starter', 'professional', 'enterprise', 'law_enforcement']
    },
    
    'community_contributed': {
        'name': 'Community-Contributed Intelligence',
        'description': 'Scam reports and victim submissions with consent',
        'consent_required': True,
        'consent_type': 'explicit_opt_in',
        'data_sources': ['user_reports', 'victim_testimonials', 'scam_database'],
        'available_in': ['starter', 'professional', 'enterprise', 'law_enforcement']
    },
    
    'enriched': {
        'name': 'Enriched Intelligence',
        'description': 'Aggregated data from multiple sources with consent',
        'consent_required': True,
        'consent_type': 'terms_of_service',
        'data_sources': [
            'exchange_data_partners',
            'defi_protocol_partners', 
            'security_researchers',
            'open_source_intelligence'
        ],
        'available_in': ['professional', 'enterprise', 'law_enforcement']
    },
    
    'classified': {
        'name': 'Classified Intelligence',
        'description': 'Law enforcement and regulatory shared data',
        'consent_required': True,
        'consent_type': 'legal_agreement',
        'data_sources': [
            'law_enforcement_feeds',
            'sanctions_lists',
            'terrorist_watchlists',
            'regulatory_databases'
        ],
        'available_in': ['law_enforcement', 'enterprise_with_clearance']
    }
}

def calculate_subscription_cost(tier: SubscriptionTier, annual: bool = False) -> Dict:
    """Calculate subscription cost with any discounts"""
    service = SERVICE_TIERS[tier]
    
    base_price = service.annual_price_usd if annual else service.monthly_price_usd
    savings = (service.monthly_price_usd * 12) - service.annual_price_usd if annual else 0
    
    return {
        'tier': tier.value,
        'billing': 'annual' if annual else 'monthly',
        'price': base_price,
        'savings': savings,
        'savings_percent': (savings / (service.monthly_price_usd * 12) * 100) if annual and service.monthly_price_usd > 0 else 0
    }

def get_tier_comparison() -> str:
    """Generate tier comparison table"""
    comparison = []
    comparison.append("MunchMaps V2 Pricing Tiers")
    comparison.append("=" * 80)
    
    for tier in [t for t in SubscriptionTier if t in SERVICE_TIERS]:
        service = SERVICE_TIERS[tier]
        comparison.append(f"\n{tier.value.upper()}")
        comparison.append(f"  Price: ${service.monthly_price_usd}/mo or ${service.annual_price_usd}/yr")
        comparison.append(f"  Addresses per scan: {service.max_addresses_per_scan}")
        comparison.append(f"  Scans per month: {service.max_scans_per_month}")
        comparison.append(f"  Chains: {', '.join(service.chains_supported)}")
        comparison.append(f"  API Access: {'Yes' if service.api_access else 'No'}")
        comparison.append(f"  Data retention: {service.data_retention_days} days")
    
    return '\n'.join(comparison)

if __name__ == "__main__":
    print(get_tier_comparison())
    
    print("\n\nDeep Scan Packages:")
    print("=" * 80)
    for key, pkg in DEEP_SCAN_PACKAGES.items():
        print(f"\n{pkg['name']}")
        print(f"  Price: ${pkg.get('price_per_address_usd', pkg.get('price_per_month_usd'))}")
        print(f"  Description: {pkg['description']}")

# Add CUSTOM tier definition
SERVICE_TIERS[SubscriptionTier.CUSTOM] = ServiceTier(
    name="Custom",
    monthly_price_usd=-1,  # Contact sales
    annual_price_usd=-1,
    max_addresses_per_scan=-1,  # Unlimited
    max_scans_per_month=-1,  # Unlimited
    chains_supported=['custom'],
    features=['Custom feature set'],
    api_access=True,
    priority_support=True,
    white_label=True,
    data_retention_days=-1,
    report_export_formats=['all'],
    custom_integrations=True,
    dedicated_manager=True
)
