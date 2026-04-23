#!/usr/bin/env python3
"""
MunchMaps V2 - Freemium Model
Free scans to hook users, premium features that convert
"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class FeatureTier:
    name: str
    free_limit: str
    premium_benefit: str
    conversion_hook: str  # Why users upgrade

# FREEMIUM FEATURE BREAKDOWN
FREEMIUM_FEATURES = {
    # ═══════════════════════════════════════════════════════════════════════
    # TOTALLY FREE (Bait - Gets them in the door)
    # ═══════════════════════════════════════════════════════════════════════
    'basic_wallet_lookup': {
        'category': 'Bait',
        'free': {
            'limit': '5 lookups per day',
            'includes': [
                'Wallet age estimate',
                'Transaction count',
                'ETH/SOL/BSC balance',
                'Basic risk flag (Safe/Suspicious)',
                'Single chain only'
            ]
        },
        'premium': {
            'unlock': 'Unlimited lookups',
            'includes': [
                'Multi-chain aggregation',
                'Full token holdings',
                'Historical balance graph',
                'Risk score (0-100)',
                'Similar wallet suggestions'
            ]
        },
        'conversion_hook': 'Users hit 5 lookup limit quickly when investigating'
    },
    
    'basic_network_graph': {
        'category': 'Bait',
        'free': {
            'limit': '1st degree connections only',
            'includes': [
                'Static PNG image',
                'Up to 10 nodes',
                'Basic clustering',
                'Downloadable (watermarked)'
            ]
        },
        'premium': {
            'unlock': 'Interactive visualization',
            'includes': [
                '2nd & 3rd degree connections',
                'Up to 1000 nodes',
                'Zoom, pan, filter',
                'No watermark',
                'Export video/GIF',
                'Embed in reports'
            ]
        },
        'conversion_hook': 'Static image is frustrating - users want to explore'
    },
    
    'basic_risk_score': {
        'category': 'Bait',
        'free': {
            'limit': 'Simple Safe/Caution/Danger',
            'includes': [
                '3-tier risk rating',
                '1-sentence explanation',
                'Last 30 days only'
            ]
        },
        'premium': {
            'unlock': 'Detailed 0-100 score',
            'includes': [
                'Sub-scores (5 categories)',
                'Historical trend graph',
                'Comparison to known scammers',
                'AI-written risk explanation',
                'Specific red flags list'
            ]
        },
        'conversion_hook': 'Users want to know WHY its risky'
    },
    
    # ═══════════════════════════════════════════════════════════════════════
    # PREMIUM HOOKS (What makes them pay)
    # ═══════════════════════════════════════════════════════════════════════
    'temporal_playback': {
        'category': 'Killer Feature',
        'free': {
            'limit': 'Single static screenshot',
            'includes': [
                'One moment in time',
                'No animation'
            ]
        },
        'premium': {
            'price': '$29/month',
            'unlock': 'Full timeline animation',
            'includes': [
                'Frame-by-frame evolution',
                'Play/pause/scrub',
                'Speed control',
                'Export MP4 video',
                'Custom date ranges',
                'Event markers'
            ]
        },
        'conversion_hook': 'BubbleMaps charges $200+/month for this alone'
    },
    
    'clustering_analysis': {
        'category': 'Killer Feature',
        'free': {
            'limit': 'See clusters exist',
            'includes': [
                'Cluster count only',
                'No details'
            ]
        },
        'premium': {
            'price': '$49/month',
            'unlock': 'Full clustering engine',
            'includes': [
                '33 wallet type classifications',
                'Bot farm detection',
                'CEX funding patterns',
                'Fresh wallet clusters',
                'Similar amount groupings',
                'Export cluster list'
            ]
        },
        'conversion_hook': 'Investigators need to know WHO is connected'
    },
    
    'cex_funding_tracker': {
        'category': 'Killer Feature',
        'free': {
            'limit': 'Yes/No only',
            'includes': [
                'CEX funded: Yes or No'
            ]
        },
        'premium': {
            'price': '$39/month',
            'unlock': 'Full CEX analysis',
            'includes': [
                'Which CEX (Binance, Coinbase, etc.)',
                'Funding amount & date',
                'Withdrawal patterns',
                'Linked accounts via CEX',
                'KYC status indicators',
                'Freeze opportunity alerts'
            ]
        },
        'conversion_hook': 'Users need to know WHICH exchange to contact'
    },
    
    'pig_butcherer_detector': {
        'category': 'Specialist',
        'free': {
            'limit': 'Basic flag only',
            'includes': [
                'Possible pig butcherer: Yes/No'
            ]
        },
        'premium': {
            'price': '$99 per investigation',
            'unlock': 'Specialist deep dive',
            'includes': [
                'Tron USDT flow analysis',
                'Victim network mapping',
                'Operator identity clues',
                'CEX cashout tracking',
                'Recovery plan',
                'Law enforcement package',
                'Priority analyst review'
            ]
        },
        'conversion_hook': 'Victims desperate to recover $50K+ losses will pay'
    },
    
    'threat_intelligence': {
        'category': 'Enterprise',
        'free': {
            'limit': 'None',
            'includes': []
        },
        'premium': {
            'price': '$199/month',
            'unlock': 'Full threat intel',
            'includes': [
                '33 wallet type classifications',
                'Nation-state actor screening',
                'Terrorist financing alerts',
                'Sanctions list matching',
                'Organized crime database',
                'Priority threat scoring',
                'Regulatory compliance reports'
            ]
        },
        'conversion_hook': 'Compliance officers and LE need this'
    },
    
    'real_time_alerts': {
        'category': 'Monitoring',
        'free': {
            'limit': 'None',
            'includes': []
        },
        'premium': {
            'price': '$79/month',
            'unlock': 'Continuous monitoring',
            'includes': [
                'Watch up to 100 wallets',
                'Email/telegram alerts',
                'Large transfer alerts',
                'CEX movement alerts',
                'Mixer usage alerts',
                'Weekly digest reports'
            ]
        },
        'conversion_hook': 'Set it and forget it - peace of mind'
    },
    
    'api_access': {
        'category': 'Developer',
        'free': {
            'limit': '100 calls/day',
            'includes': [
                'Basic endpoints',
                '10/minute rate limit'
            ]
        },
        'premium': {
            'price': '$149/month',
            'unlock': 'Full API access',
            'includes': [
                '10,000 calls/day',
                '600/minute rate limit',
                'All endpoints',
                'Webhook support',
                'Priority processing',
                'Custom endpoints'
            ]
        },
        'conversion_hook': 'Developers hit rate limits fast'
    }
}

# CONVERSION FUNNEL STRATEGY
CONVERSION_FUNNEL = {
    'step_1_discovery': {
        'action': 'User finds wallet address to investigate',
        'free_feature': 'Basic lookup',
        'friction': '5 lookup daily limit'
    },
    'step_2_interest': {
        'action': 'Sees basic risk is "Suspicious"',
        'free_feature': 'Basic network graph',
        'friction': 'Static image, 10 nodes max'
    },
    'step_3_desire': {
        'action': 'Wants to see full network',
        'premium_gate': 'Upgrade to see 2nd/3rd degree connections',
        'price_point': '$29/month'
    },
    'step_4_justification': {
        'action': 'User thinks "This could save me thousands"',
        'premium_gate': 'Full clustering + CEX tracking',
        'price_point': '$49/month'
    },
    'step_5_conversion': {
        'action': 'Upgrades to Professional tier',
        'value_prop': 'Everything they need for $199/month',
        'alternative': 'Or pay per-scan for occasional use'
    }
}

# PAY-PER-SCAN OPTION (For occasional users)
PAY_PER_SCAN = {
    'basic_scan': {
        'price': '$9',
        'includes': [
            '1 address, all chains',
            'Full risk report',
            'Basic clustering',
            'PDF export'
        ],
        'target': 'One-time investigators'
    },
    
    'forensic_scan': {
        'price': '$29',
        'includes': [
            'Up to 10 addresses',
            '3-hop tracing',
            'Temporal analysis',
            'Behavioral clustering',
            'Video export'
        ],
        'target': 'Crypto journalists, researchers'
    },
    
    'investigation_scan': {
        'price': '$99',
        'includes': [
            'Up to 50 addresses',
            'All 33 wallet types',
            'Threat intelligence',
            'CEX tracking',
            'Expert analyst review',
            'Court-ready report'
        ],
        'target': 'Law firms, private investigators'
    },
    
    'enterprise_scan': {
        'price': '$499',
        'includes': [
            'Up to 500 addresses',
            'Everything included',
            'Priority processing',
            'Dedicated analyst',
            'Custom requirements'
        ],
        'target': 'Enterprise compliance, big cases'
    }
}

# MONETIZATION TACTICS
MONETIZATION_TACTICS = {
    'scarcity': {
        'tactic': 'Daily limits that reset',
        'example': 'Only 5 free lookups per day',
        'psychology': 'FOMO - use them or lose them'
    },
    
    'teaser': {
        'tactic': 'Show premium features locked',
        'example': 'Show "3 more clusters hidden" with lock icon',
        'psychology': 'Curiosity gap - want to see what\'s hidden'
    },
    
    'social_proof': {
        'tactic': 'Show what others found',
        'example': '"1,247 investigators upgraded this week"',
        'psychology': 'Safety in numbers'
    },
    
    'urgency': {
        'tactic': 'Time-sensitive recovery',
        'example': 'Funds moving to CEX - act fast!',
        'psychology': 'Scarcity of time'
    },
    
    'anchoring': {
        'tactic': 'Show high value first',
        'example': 'Enterprise $999 crossed out, Professional $199 highlighted',
        'psychology': '$199 seems cheap compared to $999'
    },
    
    'loss_aversion': {
        'tactic': 'Emphasize what they lose',
        'example': 'Without upgrade: "3 victims\' funds still at risk"',
        'psychology': 'Pain of losing > pleasure of gaining'
    }
}

def get_recommended_pricing(user_type: str) -> Dict:
    """Get recommended pricing based on user type"""
    
    pricing = {
        'retail_investor': {
            'tier': 'Starter ($49/mo)',
            'pay_per_scan': '$9 basic',
            'why': 'Protecting their own investments'
        },
        'crypto_journalist': {
            'tier': 'Professional ($199/mo)',
            'pay_per_scan': '$29 forensic',
            'why': 'Needs video exports and deep analysis'
        },
        'private_investigator': {
            'tier': 'Professional ($199/mo)',
            'pay_per_scan': '$99 investigation',
            'why': 'Client work, needs court-ready reports'
        },
        'law_firm': {
            'tier': 'Enterprise ($999/mo)',
            'pay_per_scan': '$499 enterprise',
            'why': 'Multiple cases, needs white-label'
        },
        'exchange_compliance': {
            'tier': 'Enterprise ($999/mo)',
            'pay_per_scan': 'Not applicable',
            'why': 'Volume monitoring, API integration'
        },
        'law_enforcement': {
            'tier': 'FREE',
            'pay_per_scan': 'FREE',
            'why': 'Verified badge, public service'
        },
        'victim_recovery': {
            'tier': 'Pay-per-scan ($99)',
            'pay_per_scan': '$99 investigation',
            'why': 'One-time need, high motivation'
        }
    }
    
    return pricing.get(user_type, pricing['retail_investor'])


if __name__ == "__main__":
    print("MunchMaps V2 - Freemium Model")
    print("=" * 60)
    
    print("\n🎣 BAIT (Free to get them hooked):")
    for feature, details in FREEMIUM_FEATURES.items():
        if details['category'] == 'Bait':
            print(f"  • {feature}: {details['free']['limit']}")
    
    print("\n💰 PREMIUM HOOKS (Why they pay):")
    for feature, details in FREEMIUM_FEATURES.items():
        if details['category'] != 'Bait':
            price = details['premium'].get('price', 'In tier')
            print(f"  • {feature}: {price}")
    
    print("\n📊 PAY-PER-SCAN OPTIONS:")
    for scan, details in PAY_PER_SCAN.items():
        print(f"  • {scan}: ${details['price']} - {details['target']}")
    
    print("\n🎯 CONVERSION RATES ESTIMATES:")
    print("  • Free → Starter: 8-12%")
    print("  • Starter → Professional: 15-25%")
    print("  • Professional → Enterprise: 5-10%")
    print("  • Pay-per-scan conversion: 20-30%")
