#!/usr/bin/env python3
"""
Free Data Sources - Minimize API costs, maximize coverage
Comprehensive list of free blockchain data sources
"""

from typing import Dict, List

# ═══════════════════════════════════════════════════════════════════════════════
# FREE BLOCKCHAIN EXPLORER APIs (No API key or generous free tier)
# ═══════════════════════════════════════════════════════════════════════════════

FREE_EXPLORER_APIS = {
    # ETHEREUM & EVM CHAINS
    'etherscan': {
        'url': 'https://api.etherscan.io/api',
        'free_tier': '5 calls/second, no daily limit',
        'api_key_required': True,
        'features': ['transactions', 'balance', 'token transfers', 'contract ABI'],
        'rate_limit': '5/sec',
        'reliability': 0.95,
        'cost': '$0'
    },
    'blockscout_eth': {
        'url': 'https://eth.blockscout.com/api',
        'free_tier': 'No API key needed, generous limits',
        'api_key_required': False,
        'features': ['transactions', 'tokens', 'internal txs'],
        'rate_limit': '50/sec',
        'reliability': 0.85,
        'cost': '$0'
    },
    'bscscan': {
        'url': 'https://api.bscscan.com/api',
        'free_tier': '5 calls/second',
        'api_key_required': True,
        'features': ['transactions', 'BEP-20 tokens'],
        'rate_limit': '5/sec',
        'reliability': 0.90,
        'cost': '$0'
    },
    'polygonscan': {
        'url': 'https://api.polygonscan.com/api',
        'free_tier': '5 calls/second',
        'api_key_required': True,
        'features': ['transactions', 'ERC-20 tokens'],
        'rate_limit': '5/sec',
        'reliability': 0.88,
        'cost': '$0'
    },
    'arbiscan': {
        'url': 'https://api.arbiscan.io/api',
        'free_tier': '5 calls/second',
        'api_key_required': True,
        'features': ['Arbitrum transactions'],
        'rate_limit': '5/sec',
        'reliability': 0.87,
        'cost': '$0'
    },
    'optimistic_etherscan': {
        'url': 'https://api-optimistic.etherscan.io/api',
        'free_tier': '5 calls/second',
        'api_key_required': True,
        'features': ['Optimism transactions'],
        'rate_limit': '5/sec',
        'reliability': 0.87,
        'cost': '$0'
    },
    'basescan': {
        'url': 'https://api.basescan.org/api',
        'free_tier': '5 calls/second',
        'api_key_required': True,
        'features': ['Base chain transactions'],
        'rate_limit': '5/sec',
        'reliability': 0.85,
        'cost': '$0'
    },
    
    # SOLANA
    'solana_public_rpc': {
        'url': 'https://api.mainnet-beta.solana.com',
        'free_tier': 'Unlimited (rate limited)',
        'api_key_required': False,
        'features': ['transactions', 'accounts', 'program data'],
        'rate_limit': 'Variable',
        'reliability': 0.90,
        'cost': '$0'
    },
    'helius': {
        'url': 'https://mainnet.helius-rpc.com',
        'free_tier': '100,000 requests/day',
        'api_key_required': True,
        'features': ['enhanced transactions', 'NFT APIs'],
        'rate_limit': '100K/day',
        'reliability': 0.95,
        'cost': '$0'
    },
    'quicknode_solana': {
        'url': 'https://api.quicknode.com',
        'free_tier': 'Free tier available',
        'api_key_required': True,
        'features': ['full RPC'],
        'rate_limit': 'Limited',
        'reliability': 0.92,
        'cost': '$0'
    },
    
    # TRON
    'trongrid': {
        'url': 'https://api.trongrid.io',
        'free_tier': '10 QPS, no daily limit',
        'api_key_required': True,
        'features': ['transactions', 'TRC-20 tokens', 'TRC-721'],
        'rate_limit': '10/sec',
        'reliability': 0.88,
        'cost': '$0'
    },
    'tronscan_public': {
        'url': 'https://apilist.tronscanapi.com/api',
        'free_tier': 'Public endpoints',
        'api_key_required': False,
        'features': ['basic queries'],
        'rate_limit': 'Unknown',
        'reliability': 0.80,
        'cost': '$0'
    },
    
    # BITCOIN
    'blockchain_info': {
        'url': 'https://blockchain.info/api',
        'free_tier': 'Unlimited',
        'api_key_required': False,
        'features': ['blocks', 'transactions', 'charts'],
        'rate_limit': 'None',
        'reliability': 0.90,
        'cost': '$0'
    },
    'blockchair_btc': {
        'url': 'https://api.blockchair.com/bitcoin',
        'free_tier': '1440 requests/day',
        'api_key_required': False,
        'features': ['rich list', 'transactions', 'blocks'],
        'rate_limit': '1440/day',
        'reliability': 0.92,
        'cost': '$0'
    },
    'mempool_space': {
        'url': 'https://mempool.space/api',
        'free_tier': 'Open source, unlimited',
        'api_key_required': False,
        'features': ['mempool data', 'transactions', 'fees'],
        'rate_limit': 'None',
        'reliability': 0.90,
        'cost': '$0'
    },
    
    # OTHER CHAINS
    'snowtrace_avalanche': {
        'url': 'https://api.snowtrace.io/api',
        'free_tier': '5 calls/second',
        'api_key_required': True,
        'features': ['Avalanche C-Chain'],
        'rate_limit': '5/sec',
        'reliability': 0.85,
        'cost': '$0'
    },
    'ftmscan': {
        'url': 'https://api.ftmscan.com/api',
        'free_tier': '5 calls/second',
        'api_key_required': True,
        'features': ['Fantom transactions'],
        'rate_limit': '5/sec',
        'reliability': 0.82,
        'cost': '$0'
    },
    'celoscan': {
        'url': 'https://api.celoscan.io/api',
        'free_tier': '5 calls/second',
        'api_key_required': True,
        'features': ['Celo transactions'],
        'rate_limit': '5/sec',
        'reliability': 0.80,
        'cost': '$0'
    },
    'moonscan': {
        'url': 'https://api-moonbeam.moonscan.io/api',
        'free_tier': '5 calls/second',
        'api_key_required': True,
        'features': ['Moonbeam transactions'],
        'rate_limit': '5/sec',
        'reliability': 0.78,
        'cost': '$0'
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# FREE DATA AGGREGATORS
# ═══════════════════════════════════════════════════════════════════════════════

FREE_AGGREGATORS = {
    'defillama': {
        'url': 'https://defillama.com/api',
        'description': 'DeFi protocol data, TVL, yields',
        'cost': 'Free',
        'use_case': 'Identify DeFi interactions'
    },
    'coingecko': {
        'url': 'https://api.coingecko.com/api/v3',
        'description': 'Crypto prices, market data',
        'free_tier': '10-30 calls/minute',
        'cost': 'Free tier generous',
        'use_case': 'USD value calculations'
    },
    'coinmarketcap': {
        'url': 'https://pro-api.coinmarketcap.com',
        'description': 'Market data, exchange info',
        'free_tier': '10K calls/month',
        'cost': 'Free tier available',
        'use_case': 'Token metadata'
    },
    'dune_analytics': {
        'url': 'https://dune.com/browse/dashboards',
        'description': 'Community queries, dashboards',
        'cost': 'Free with signup',
        'use_case': 'Pre-built scam tracking queries'
    },
    'nansen_portfolio': {
        'url': 'https://portfolio.nansen.ai',
        'description': 'Wallet labeling (limited free)',
        'cost': 'Free for basic',
        'use_case': 'Smart money tracking'
    },
    'zerion': {
        'url': 'https://zerion.io',
        'description': 'Portfolio tracking',
        'cost': 'Free',
        'use_case': 'Token holding visualization'
    },
    'zapper': {
        'url': 'https://zapper.fi/api',
        'description': 'DeFi position tracking',
        'cost': 'Free tier',
        'use_case': 'DeFi protocol interactions'
    },
    'debank': {
        'url': 'https://api.debank.com',
        'description': 'Multi-chain portfolio',
        'cost': 'Free for basic',
        'use_case': 'Cross-chain token balances'
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# FREE INTELLIGENCE & OSINT SOURCES
# ═══════════════════════════════════════════════════════════════════════════════

FREE_INTELLIGENCE = {
    'government_sanctions': {
        'ofac': {
            'url': 'https://www.treasury.gov/ofac/downloads',
            'data': 'SDN list, crypto addresses',
            'format': 'XML, CSV, TXT',
            'update_frequency': 'Daily',
            'cost': 'Free'
        },
        'un_consolidated': {
            'url': 'https://www.un.org/securitycouncil/content/un-sc-consolidated-list',
            'data': 'UN sanctions',
            'format': 'XML, PDF',
            'update_frequency': 'As needed',
            'cost': 'Free'
        },
        'eu_sanctions': {
            'url': 'https://data.europa.eu/data/datasets/consolidated-list-of-persons-groups-and-entities-subject-to-eu-financial-sanctions',
            'data': 'EU sanctions',
            'format': 'XML',
            'update_frequency': 'Daily',
            'cost': 'Free'
        },
        'hmt_uk': {
            'url': 'https://www.gov.uk/government/collections/financial-sanctions-consolidated-list-of-targets',
            'data': 'UK sanctions',
            'format': 'CSV, XML',
            'update_frequency': 'Daily',
            'cost': 'Free'
        },
        'dfat_australia': {
            'url': 'https://www.dfat.gov.au/international-relations/security/sanctions/consolidated-list',
            'data': 'Australian sanctions',
            'format': 'XML',
            'cost': 'Free'
        }
    },
    
    'scam_databases': {
        'chainabuse': {
            'url': 'https://www.chainabuse.com',
            'api': 'Available',
            'data': 'Community-reported scams',
            'cost': 'Free tier'
        },
        'bitcoinabuse': {
            'url': 'https://www.bitcoinabuse.com/api',
            'api': 'Free with limits',
            'data': 'Reported addresses',
            'cost': 'Free'
        },
        'scamalert': {
            'url': 'https://scamalert.com',
            'data': 'Scam reports',
            'cost': 'Free'
        },
        'cryptoscamdb': {
            'url': 'https://cryptoscamdb.org',
            'data': 'Scam domains, addresses',
            'cost': 'Free'
        },
        'wallet_alert': {
            'url': 'https://wallet-alert.com',
            'data': 'Risk scores',
            'cost': 'Free tier'
        }
    },
    
    'security_research': {
        'slowmist_hacked': {
            'url': 'https://hacked.slowmist.io',
            'data': 'Hack incidents, stolen funds',
            'cost': 'Free'
        },
        'rekt_news': {
            'url': 'https://rekt.news',
            'data': 'Hack post-mortems',
            'cost': 'Free'
        },
        'forta_network': {
            'url': 'https://forta.org',
            'data': 'Threat detection bots',
            'cost': 'Free alerts'
        },
        'blocksec': {
            'url': 'https://blocksec.com',
            'data': 'Security incidents',
            'cost': 'Free reports'
        }
    },
    
    'social_osint': {
        'twitter_lists': {
            'scam_hunters': ['@zachxbt', '@PeckShieldAlert', '@CertiKAlert'],
            'description': 'Real-time scam alerts',
            'cost': 'Free'
        },
        'reddit': {
            'subreddits': ['r/CryptoScams', 'r/Scams', 'r/ethdev'],
            'cost': 'Free'
        },
        'telegram_channels': {
            'scam_alerts': ['@PeckShieldAlert', '@CertiKCommunity'],
            'cost': 'Free'
        }
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# FREE GRAPH/VISUALIZATION TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

FREE_VISUALIZATION = {
    'd3_js': {
        'name': 'D3.js',
        'url': 'https://d3js.org',
        'type': 'JavaScript library',
        'cost': 'Free (Open Source)',
        'use_case': 'Custom network graphs',
        'learning_curve': 'Steep',
        'power': 'High'
    },
    'cytoscape_js': {
        'name': 'Cytoscape.js',
        'url': 'https://js.cytoscape.org',
        'type': 'JavaScript library',
        'cost': 'Free (MIT License)',
        'use_case': 'Network theory visualization',
        'learning_curve': 'Medium',
        'power': 'High'
    },
    'vis_js': {
        'name': 'Vis.js',
        'url': 'https://visjs.org',
        'type': 'JavaScript library',
        'cost': 'Free (Apache 2.0)',
        'use_case': 'Interactive network graphs',
        'learning_curve': 'Low',
        'power': 'Medium'
    },
    'sigma_js': {
        'name': 'Sigma.js',
        'url': 'https://www.sigmajs.org',
        'type': 'JavaScript library',
        'cost': 'Free (MIT License)',
        'use_case': 'Large graph rendering',
        'learning_curve': 'Medium',
        'power': 'Very High'
    },
    'chart_js': {
        'name': 'Chart.js',
        'url': 'https://www.chartjs.org',
        'type': 'JavaScript library',
        'cost': 'Free (MIT License)',
        'use_case': 'Charts and graphs',
        'learning_curve': 'Low',
        'power': 'Medium'
    },
    'plotly_js': {
        'name': 'Plotly.js',
        'url': 'https://plotly.com/javascript',
        'type': 'JavaScript library',
        'cost': 'Free (Open Source)',
        'use_case': 'Scientific visualization',
        'learning_curve': 'Medium',
        'power': 'High'
    },
    'graphviz': {
        'name': 'Graphviz',
        'url': 'https://graphviz.org',
        'type': 'Command-line + libraries',
        'cost': 'Free (EPL)',
        'use_case': 'Graph layout algorithms',
        'learning_curve': 'Medium',
        'power': 'High'
    },
    'gephi': {
        'name': 'Gephi',
        'url': 'https://gephi.org',
        'type': 'Desktop application',
        'cost': 'Free (Open Source)',
        'use_case': 'Large network analysis',
        'learning_curve': 'Medium',
        'power': 'Very High'
    },
    'networkx': {
        'name': 'NetworkX',
        'url': 'https://networkx.org',
        'type': 'Python library',
        'cost': 'Free (BSD)',
        'use_case': 'Graph algorithms, analysis',
        'learning_curve': 'Low',
        'power': 'High'
    },
    'bokeh': {
        'name': 'Bokeh',
        'url': 'https://bokeh.org',
        'type': 'Python library',
        'cost': 'Free (BSD)',
        'use_case': 'Interactive web plots',
        'learning_curve': 'Medium',
        'power': 'High'
    },
    'apache_echarts': {
        'name': 'Apache ECharts',
        'url': 'https://echarts.apache.org',
        'type': 'JavaScript library',
        'cost': 'Free (Apache 2.0)',
        'use_case': 'Business charts, graphs',
        'learning_curve': 'Low',
        'power': 'High'
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# COST-OPTIMIZATION STRATEGY
# ═══════════════════════════════════════════════════════════════════════════════

COST_OPTIMIZATION = {
    'api_rotation': {
        'strategy': 'Rotate through multiple free API keys',
        'implementation': 'Create multiple accounts, rotate requests',
        'chains_affected': ['Ethereum', 'BSC', 'Polygon'],
        'cost_savings': '80-90%'
    },
    'cache_aggressively': {
        'strategy': 'Cache all blockchain data',
        'ttl': {
            'balances': '1 hour',
            'transactions': '24 hours',
            'token_holders': '6 hours',
            'labels': '7 days'
        },
        'cost_savings': '60-70%'
    },
    'batch_requests': {
        'strategy': 'Batch multiple queries',
        'implementation': 'Use multicall contracts where possible',
        'cost_savings': '50-70%'
    },
    'use_public_rpc': {
        'strategy': 'Use public RPC endpoints when possible',
        'chains': ['Solana', 'Ethereum (limited)'],
        'cost_savings': '100% for those calls'
    },
    'rate_limit_respect': {
        'strategy': 'Stay well under rate limits',
        'benefit': 'Avoid throttling, consistent performance',
        'implementation': 'Exponential backoff, jitter'
    }
}

# Recommended stack for minimal cost
RECOMMENDED_FREE_STACK = {
    'primary_explorer': {
        'ethereum': 'Etherscan (free tier)',
        'solana': 'Helius (100K/day free)',
        'tron': 'TronGrid (free tier)',
        'bsc': 'BscScan (free tier)',
        'polygon': 'PolygonScan (free tier)'
    },
    'fallback_explorer': {
        'ethereum': 'Blockscout (no key needed)',
        'solana': 'Public RPC',
        'others': 'Native chain RPC'
    },
    'visualization': {
        'web': 'Cytoscape.js (free, powerful)',
        'backend': 'NetworkX (Python)',
        'charts': 'Chart.js (simple) or Plotly.js (advanced)'
    },
    'intelligence': {
        'sanctions': 'OFAC/UN downloads (free)',
        'scams': 'Chainabuse + BitcoinAbuse APIs',
        'news': 'RSS feeds + Twitter API v2 (free tier)'
    },
    'estimated_monthly_cost': '$0 - $50',
    'estimated_capacity': '10,000 addresses/day'
}


def get_free_sources_by_chain(chain: str) -> List[Dict]:
    """Get all free data sources for a specific chain"""
    sources = []
    
    for name, config in FREE_EXPLORER_APIS.items():
        if chain.lower() in name or chain.lower() in str(config.get('features', [])).lower():
            sources.append({
                'name': name,
                'cost': config['cost'],
                'rate_limit': config['rate_limit'],
                'api_key': 'Required' if config['api_key_required'] else 'Not needed'
            })
    
    return sources


if __name__ == "__main__":
    print("FREE DATA SOURCES FOR MUNCHMAPS")
    print("=" * 60)
    
    print("\n🆓 FREE EXPLORER APIs:")
    print(f"  Total: {len(FREE_EXPLORER_APIS)} sources")
    
    no_key_required = sum(1 for s in FREE_EXPLORER_APIS.values() if not s['api_key_required'])
    print(f"  No API key needed: {no_key_required}")
    
    print("\n📊 FREE VISUALIZATION:")
    print(f"  Recommended: Sigma.js or Cytoscape.js")
    print(f"  Both free, production-ready")
    
    print("\n💰 COST OPTIMIZATION:")
    for strategy, details in COST_OPTIMIZATION.items():
        savings = details.get('cost_savings', 'Unknown')
        print(f"  • {strategy}: {savings} savings")
    
    print("\n🎯 RECOMMENDED STACK:")
    print(f"  Monthly cost: {RECOMMENDED_FREE_STACK['estimated_monthly_cost']}")
    print(f"  Daily capacity: {RECOMMENDED_FREE_STACK['estimated_capacity']}")
