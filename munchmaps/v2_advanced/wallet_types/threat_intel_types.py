#!/usr/bin/env python3
"""
Advanced Threat Intelligence Wallet Types
Comprehensive classification of malicious actors in the crypto ecosystem
"""

from typing import Dict, List

# Expanded wallet types covering the full threat landscape
ADVANCED_THREAT_TYPES = {
    # ═══════════════════════════════════════════════════════════════════════
    # CRITICAL THREATS - Nation States, Organized Crime, Terror
    # ═══════════════════════════════════════════════════════════════════════
    
    'STATE_ACTOR_APT': {
        'tier': 'CRITICAL',
        'category': 'Nation State',
        'description': 'Advanced Persistent Threat group backed by nation state',
        'geopolitical_context': ['Lazarus Group (DPRK)', 'APT38', 'Cozy Bear', 'Fancy Bear'],
        'indicators': [
            'Sophisticated multi-chain operations',
            'Use of zero-day exploits',
            'Mixer and privacy coin preference',
            'Long-term holding patterns',
            'Cross-border coordination',
            'Exchange exploitation',
            'DeFi protocol manipulation'
        ],
        'typical_behavior': [
            'Bridge exploits',
            'Exchange hacks',
            'Ransomware payment collection',
            'Sanctions evasion',
            'Funding of state programs'
        ],
        'detection_confidence': 'MEDIUM',
        'reporting_authorities': ['FBI', 'OFAC', 'Interpol', 'UN'],
        'priority': 'P0'
    },
    
    'TERRORIST_FINANCIER': {
        'tier': 'CRITICAL',
        'category': 'Terrorism',
        'description': 'Wallet associated with terrorist financing',
        'groups': ['ISIS', 'Al-Qaeda', 'Hamas', 'Hezbollah', 'Al-Shabaab'],
        'indicators': [
            'Donation collection patterns',
            'Small frequent deposits (crowdfunding)',
            'Rapid conversion to privacy coins',
            'Geographic concentration',
            'Social media linked addresses',
            'Charity front operations'
        ],
        'typical_behavior': [
            'Crowdfunding campaigns',
            'Remittances to conflict zones',
            'Weapon procurement funding',
            'Propaganda funding'
        ],
        'detection_confidence': 'HIGH',
        'reporting_authorities': ['FinCEN', 'FATF', 'OFAC', 'Local CT units'],
        'priority': 'P0'
    },
    
    'ORGANIZED_CRIME_SYNDICATE': {
        'tier': 'CRITICAL',
        'category': 'Organized Crime',
        'description': 'Transnational criminal organization wallet',
        'groups': ['Mafia', 'Triads', 'Cartels', 'Yakuza', 'Cybercrime Gangs'],
        'indicators': [
            'Multi-generational wallet clusters',
            'Hierarchical funding structures',
            'Mix of legitimate and illicit flows',
            'Real estate purchase patterns',
            'Casino/gambling connections',
            'Shell company interactions'
        ],
        'typical_behavior': [
            'Drug trafficking proceeds',
            'Human trafficking payments',
            'Money laundering operations',
            'Racketeering proceeds',
            'Cybercrime revenue'
        ],
        'detection_confidence': 'MEDIUM',
        'reporting_authorities': ['FBI', 'Europol', 'NCA', 'Interpol'],
        'priority': 'P0'
    },
    
    # ═══════════════════════════════════════════════════════════════════════
    # SERIAL OPERATORS - Professional Scammers
    # ═══════════════════════════════════════════════════════════════════════
    
    'SERIAL_RUG_PULL_DEPLOYER': {
        'tier': 'CRITICAL',
        'category': 'Serial Scammer',
        'description': 'Repeatedly deploys tokens, pumps, then drains liquidity',
        'indicators': [
            'Multiple token contracts deployed',
            'Pattern: Deploy → Shill → Dump',
            'Reused code across contracts',
            'Same funding source for deployments',
            'Coordinated social media campaigns',
            'Paid influencer connections',
            'Bot-driven volume manipulation'
        ],
        'typical_behavior': [
            'Token deployment on multiple chains',
            'Fake partnership announcements',
            'Celebrity endorsement scams',
            'Honeypot contracts',
            'Liquidity removal timing'
        ],
        'victim_estimate': '1000+ per deployment',
        'detection_confidence': 'HIGH',
        'priority': 'P0'
    },
    
    'SERIAL_PONZI_OPERATOR': {
        'tier': 'CRITICAL',
        'category': 'Serial Scammer',
        'description': 'Runs multiple Ponzi schemes sequentially',
        'indicators': [
            'Yield farming promises (guaranteed returns)',
            'Pyramid structure (referral systems)',
            'Early investor payouts from new deposits',
            'Complex withdrawal mechanisms',
            'Fake audit claims',
            'Anonymous team',
            'Unrealistic APYs (100%+ annual)'
        ],
        'typical_behavior': [
            'Staking contracts with lock periods',
            'Multi-level marketing structures',
            'Compounding reward schemes',
            'Exit scams after liquidity peaks'
        ],
        'detection_confidence': 'HIGH',
        'priority': 'P0'
    },
    
    'SERIAL_PHISHING_OPERATOR': {
        'tier': 'HIGH',
        'category': 'Serial Scammer',
        'description': 'Operates persistent phishing infrastructure',
        'indicators': [
            'Wallet drain contract interactions',
            ' victims with infinite approvals',
            'Clone website deployments',
            'Social media impersonation',
            'Discord/Telegram bot deployment',
            'Airdrop scam patterns',
            'Fake support accounts'
        ],
        'typical_behavior': [
            'Fake exchange login pages',
            'Impersonation of popular projects',
            'Urgency-based social engineering',
            'Seed phrase collection',
            'Private key extraction'
        ],
        'victim_estimate': '100+ per campaign',
        'detection_confidence': 'HIGH',
        'priority': 'P1'
    },
    
    'SERIAL_NFT_SCAMMER': {
        'tier': 'HIGH',
        'category': 'Serial Scammer',
        'description': 'Repeatedly launches fraudulent NFT projects',
        'indicators': [
            'Multiple NFT contract deployments',
            'Copycat collections (fake BAYC, etc.)',
            'Mint funds immediately moved',
            'Fake roadmap promises',
            'Paid celebrity endorsements',
            'Rug pull after mint',
            'Honeypot trading contracts'
        ],
        'typical_behavior': [
            'Generative art with stolen assets',
            'Fake utility promises',
            'Community building then abandonment',
            'Secondary market manipulation'
        ],
        'detection_confidence': 'HIGH',
        'priority': 'P1'
    },
    
    # ═══════════════════════════════════════════════════════════════════════
    # TECHNICAL OPERATORS - Code-based Attacks
    # ═══════════════════════════════════════════════════════════════════════
    
    'CONTRACT_DRAINER': {
        'tier': 'CRITICAL',
        'category': 'Technical Attacker',
        'description': 'Deploys malicious contracts to drain user wallets',
        'indicators': [
            'Unverified contract bytecode',
            'Hidden mint functions',
            'Owner-only withdrawal functions',
            'Approval exploitation patterns',
            'Permit2 signature abuse',
            'Gasless approval scams',
            'Flash loan attack preparation'
        ],
        'typical_behavior': [
            'Fake token airdrops requiring approval',
            'Malicious dApp interfaces',
            'Wallet connection scams',
            'Transaction simulation bypasses',
            'Multi-call exploitation'
        ],
        'technical_sophistication': 'EXPERT',
        'detection_confidence': 'HIGH',
        'priority': 'P0'
    },
    
    'FLASH_LOAN_ATTACKER': {
        'tier': 'CRITICAL',
        'category': 'Technical Attacker',
        'description': 'Exploits DeFi protocols using flash loans',
        'indicators': [
            'Large flash loan borrowings',
            'Price oracle manipulation',
            'Liquidity pool draining',
            'Governance token accumulation',
            'Proposal manipulation',
            'Complex multi-step transactions',
            'MEV extraction patterns'
        ],
        'typical_behavior': [
            'Price manipulation attacks',
            'Oracle manipulation',
            'Governance attacks',
            'Liquidation cascades',
            'Sandwich attacks'
        ],
        'technical_sophistication': 'EXPERT',
        'detection_confidence': 'HIGH',
        'priority': 'P0'
    },
    
    'FRONTRUNNING_BOT': {
        'tier': 'MEDIUM',
        'category': 'Technical Operator',
        'description': 'MEV extraction through transaction ordering',
        'indicators': [
            'High gas price competition',
            'Transaction replacement (speed-up)',
            'Same block inclusion as victims',
            'Arbitrage patterns',
            'Sandwich attack structures',
            'Validator relationships'
        ],
        'typical_behavior': [
            'DEX arbitrage',
            'Liquidation hunting',
            'NFT sniping',
            'IDO participation',
            'Priority gas auctions'
        ],
        'technical_sophistication': 'ADVANCED',
        'detection_confidence': 'MEDIUM',
        'priority': 'P2'
    },
    
    # ═══════════════════════════════════════════════════════════════════════
    # MARKET MANIPULATORS - Trading Scams
    # ═══════════════════════════════════════════════════════════════════════
    
    'COPY_TRADING_SCAMMER': {
        'tier': 'HIGH',
        'category': 'Trading Scam',
        'description': 'Fakes trading success to sell signals/subscriptions',
        'indicators': [
            'Simulated winning trades (wash trading)',
            'Multiple accounts coordinating',
            'Fake P&L screenshots',
            'Subscription fee collection',
            'Signal group operations',
            'Pump coordination',
            'Victim fund management (exit scams)'
        ],
        'typical_behavior': [
            'Social media "alpha" sharing',
            'Paid signal groups',
            'Copy trading platform scams',
            'Managed fund schemes',
            'Educational course scams'
        ],
        'detection_confidence': 'MEDIUM',
        'priority': 'P1'
    },
    
    'FAKE_MARKET_MAKER': {
        'tier': 'HIGH',
        'category': 'Market Manipulation',
        'description': 'Creates artificial volume and liquidity to deceive traders',
        'indicators': [
            'Wash trading (buy/sell to self)',
            'Spoofing (fake orders)',
            'Layering (multiple fake levels)',
            'Quote stuffing',
            'Volume spikes without price movement',
            'Cross-exchange arbitrage manipulation',
            'Liquidity mirage (fake depth)'
        ],
        'typical_behavior': [
            'Artificial volume generation',
            'Price manipulation',
            'Liquidity spoofing',
            'Order book manipulation',
            'Slippage exploitation'
        ],
        'detection_confidence': 'HIGH',
        'priority': 'P1'
    },
    
    'PUMP_AND_DUMP_COORDINATOR': {
        'tier': 'HIGH',
        'category': 'Market Manipulation',
        'description': 'Coordinates groups to artificially inflate then crash prices',
        'indicators': [
            'Coordinated buying signals',
            'Social media campaign timing',
            'Group chat coordination',
            'Pre-pump accumulation',
            'Staged selling (tiers)',
            'Victim buy-in tracking',
            'Multi-platform promotion'
        ],
        'typical_behavior': [
            'Telegram/Discord pump groups',
            'Twitter/X coordinated posts',
            'YouTube influencer campaigns',
            'TikTok viral campaigns',
            'Celebrity endorsement scams'
        ],
        'detection_confidence': 'HIGH',
        'priority': 'P1'
    },
    
    # ═══════════════════════════════════════════════════════════════════════
    # SOLO OPERATORS - Individual Scammers
    # ═══════════════════════════════════════════════════════════════════════
    
    'SOLO_ROMANCE_SCAMMER': {
        'tier': 'HIGH',
        'category': 'Social Engineering',
        'description': 'Individual operating romance/pig butcherer scams',
        'indicators': [
            'One-on-one victim grooming',
            'Gradual trust building',
            'Investment opportunity introduction',
            'Emotional manipulation',
            'Urgency creation',
            'Multiple victim wallets',
            'Regular cashout patterns'
        ],
        'typical_behavior': [
            'Dating app initial contact',
            'WhatsApp/Telegram migration',
            'Fake investment platform',
            'Cryptocurrency "assistance"',
            'Emergency fund requests'
        ],
        'avg_victim_loss': '$50,000 - $500,000',
        'detection_confidence': 'MEDIUM',
        'priority': 'P1'
    },
    
    'SOLO_IMPERSONATOR': {
        'tier': 'MEDIUM',
        'category': 'Social Engineering',
        'description': 'Impersonates celebrities, support staff, or known individuals',
        'indicators': [
            'Handle typosquatting (ElonMvsK)',
            'Verified badge mimicry',
            'Urgent request patterns',
            'Giveaway scam promises',
            'Private message initiation',
            'Social graph analysis'
        ],
        'typical_behavior': [
            'Celebrity giveaway scams',
            'Support staff impersonation',
            'CEO/CFO email compromise',
            'Influencer partnership scams',
            'Double-your-money schemes'
        ],
        'detection_confidence': 'HIGH',
        'priority': 'P2'
    },
    
    'SOLO_AIRDROP_HUNTER': {
        'tier': 'LOW',
        'category': 'Airdrop Farming',
        'description': 'Creates multiple wallets to farm airdrops (not illegal, but notable)',
        'indicators': [
            'Sybil cluster patterns',
            'Minimal value transfers',
            'Protocol interaction farming',
            'Bridge usage for multi-chain',
            'Dusting transactions',
            'Governance participation farming'
        ],
        'typical_behavior': [
            'LayerZero farming',
            'ZkSync farming',
            'StarkNet farming',
            'DeFi protocol farming',
            'NFT marketplace farming'
        ],
        'detection_confidence': 'HIGH',
        'priority': 'P3'
    },
    
    # ═══════════════════════════════════════════════════════════════════════
    # INFRASTRUCTURE - Supporting Criminal Operations
    # ═══════════════════════════════════════════════════════════════════════
    
    'MIXER_SERVICE_OPERATOR': {
        'tier': 'CRITICAL',
        'category': 'Infrastructure',
        'description': 'Operates cryptocurrency mixing/tumbling service',
        'indicators': [
            'Multiple pool contracts',
            'Anonymity set management',
            'Fee collection patterns',
            'Relay network operation',
            'Compliance evasion',
            'Multi-chain expansion'
        ],
        'services': ['Tornado Cash', 'Samourai', 'Wasabi', 'CashFusion'],
        'typical_behavior': [
            'Obfuscation of fund sources',
            'Sanctions evasion assistance',
            'Criminal proceeds laundering',
            'Privacy preservation (legitimate and illicit)'
        ],
        'legal_status': 'Varying by jurisdiction',
        'detection_confidence': 'HIGH',
        'priority': 'P0'
    },
    
    'EXCHANGE_MULE': {
        'tier': 'HIGH',
        'category': 'Money Laundering',
        'description': 'Uses exchange accounts to launder funds for criminals',
        'indicators': [
            'Rapid buy/sell cycles',
            'Multiple exchange accounts',
            'Geographic IP hopping',
            'Structuring (amounts under thresholds)',
            'KYC document sharing',
            'Commission-based operation',
            'OTC desk connections'
        ],
        'typical_behavior': [
            'Fiat off-ramping for criminals',
            'Cross-exchange arbitrage laundering',
            'P2P trading laundering',
            'Gift card monetization'
        ],
        'detection_confidence': 'MEDIUM',
        'priority': 'P1'
    },
    
    'SHELL_COMPANY_OPERATOR': {
        'tier': 'HIGH',
        'category': 'Money Laundering',
        'description': 'Uses corporate structures to legitimize crypto proceeds',
        'indicators': [
            'Corporate wallet structures',
            'Invoice generation patterns',
            'Fake service provision',
            'Cross-border corporate flows',
            'Nominee director patterns',
            'Banking relationship exploitation'
        ],
        'typical_behavior': [
            'Fake consulting services',
            'Shell company invoicing',
            'Real estate acquisition',
            'Luxury goods purchases',
            'Offshore company formation'
        ],
        'detection_confidence': 'LOW',
        'priority': 'P1'
    },
    
    # ═══════════════════════════════════════════════════════════════════════
    # EMERGING THREATS
    # ═══════════════════════════════════════════════════════════════════════
    
    'AI_DEEPFAKE_SCAMMER': {
        'tier': 'HIGH',
        'category': 'Emerging Threat',
        'description': 'Uses AI-generated content for sophisticated scams',
        'indicators': [
            'Deepfake video endorsements',
            'AI voice cloning',
            'Real-time face substitution',
            'Synthetic social media profiles',
            'AI-generated project websites',
            'Automated social engineering'
        ],
        'typical_behavior': [
            'Celebrity deepfake endorsements',
            'Live video call scams',
            'Family member impersonation',
            'CEO voice cloning',
            'AI-generated whitepapers'
        ],
        'detection_confidence': 'MEDIUM',
        'priority': 'P1',
        'emerging': True
    },
    
    'QUANTUM_ATTACK_PREP': {
        'tier': 'MEDIUM',
        'category': 'Future Threat',
        'description': 'Harvesting encrypted data for future quantum decryption',
        'indicators': [
            'Large encrypted data collection',
            'High-value target focus',
            'Long-term data storage',
            'Communication interception',
            'Public key harvesting'
        ],
        'typical_behavior': [
            'Store now, decrypt later',
            'High-value wallet targeting',
            'Institutional data collection'
        ],
        'detection_confidence': 'LOW',
        'priority': 'P3',
        'speculative': True
    }
}

# Group wallet types by category for easier analysis
THREAT_CATEGORIES = {
    'Nation State & Terror': [
        'STATE_ACTOR_APT',
        'TERRORIST_FINANCIER',
        'ORGANIZED_CRIME_SYNDICATE'
    ],
    'Serial Scammers': [
        'SERIAL_RUG_PULL_DEPLOYER',
        'SERIAL_PONZI_OPERATOR',
        'SERIAL_PHISHING_OPERATOR',
        'SERIAL_NFT_SCAMMER'
    ],
    'Technical Attackers': [
        'CONTRACT_DRAINER',
        'FLASH_LOAN_ATTACKER',
        'FRONTRUNNING_BOT'
    ],
    'Market Manipulators': [
        'COPY_TRADING_SCAMMER',
        'FAKE_MARKET_MAKER',
        'PUMP_AND_DUMP_COORDINATOR'
    ],
    'Solo Operators': [
        'SOLO_ROMANCE_SCAMMER',
        'SOLO_IMPERSONATOR',
        'SOLO_AIRDROP_HUNTER'
    ],
    'Infrastructure': [
        'MIXER_SERVICE_OPERATOR',
        'EXCHANGE_MULE',
        'SHELL_COMPANY_OPERATOR'
    ],
    'Emerging': [
        'AI_DEEPFAKE_SCAMMER',
        'QUANTUM_ATTACK_PREP'
    ]
}

# Risk scoring weights
RISK_WEIGHTS = {
    'CRITICAL': 100,
    'HIGH': 50,
    'MEDIUM': 20,
    'LOW': 5
}

def get_threat_statistics() -> Dict:
    """Get statistics about threat types"""
    stats = {
        'total_types': len(ADVANCED_THREAT_TYPES),
        'by_tier': {},
        'by_category': {},
        'by_priority': {}
    }
    
    for wt, info in ADVANCED_THREAT_TYPES.items():
        tier = info['tier']
        category = info['category']
        priority = info.get('priority', 'P3')
        
        stats['by_tier'][tier] = stats['by_tier'].get(tier, 0) + 1
        stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
        stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
    
    return stats


if __name__ == "__main__":
    stats = get_threat_statistics()
    print("Advanced Threat Intelligence Types")
    print("=" * 50)
    print(f"Total wallet types: {stats['total_types']}")
    print(f"\nBy Risk Tier:")
    for tier, count in stats['by_tier'].items():
        print(f"  {tier}: {count} types")
    print(f"\nBy Category:")
    for cat, count in stats['by_category'].items():
        print(f"  {cat}: {count} types")
