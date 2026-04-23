# MunchMaps V2 - Quick Start Guide

## Installation & Setup

```bash
# API Keys Required (Free Tiers)
# - Etherscan: https://etherscan.io/apis
# - Helius (Solana): https://helius.xyz
# - TronGrid: https://www.trongrid.io
# - BscScan: https://bscscan.com/apis
# - PolygonScan: https://polygonscan.com/apis
```

## Basic Usage

```python
import asyncio
from munchmaps_v2_full import MunchMapsV2Full

# Initialize
api_keys = {
    'ethereum': 'YOUR_ETHERSCAN_API_KEY',
    'solana': 'YOUR_HELIUS_API_KEY', 
    'tron': 'YOUR_TRONGRID_API_KEY',
    'bsc': 'YOUR_BSCSCAN_API_KEY',
    'polygon': 'YOUR_POLYGONSCAN_API_KEY'
}

engine = MunchMapsV2Full(api_keys)

# Run investigation
addresses = [
    '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',  # Ethereum
    'TNP2uM4bE7Xv9F8G7H6J5K4L3M2N1B0V9',         # Tron (pig butcherer)
]

async def main():
    report = await engine.analyze_investigation(
        investigation_name="Case_001",
        addresses=addresses
    )
    
    # Export results
    engine.export_report(report, 'case_001_report.json')
    
    # Access key findings
    print(f"Critical Wallets: {report['executive_summary']['critical_risk_wallets']}")
    print(f"Pig Butcherers: {report['pig_butcherer_analysis']['pig_butcher_operators_detected']}")
    
    # Access cross-chain connections
    for conn in report['cross_chain_analysis']['relationships']:
        print(f"{conn['wallet1']} <-> {conn['wallet2']} ({conn['type']})")

asyncio.run(main())
```

## Investigation Report Structure

```python
report = {
    'metadata': {
        'investigation_name': str,
        'duration_seconds': float,
        'chains_covered': int,
        'addresses_analyzed': int
    },
    'executive_summary': {
        'overall_risk': 'CRITICAL|HIGH|MEDIUM|LOW',
        'classified_suspicious': int,
        'critical_risk_wallets': int,
        'pig_butcher_operators_detected': int
    },
    'wallet_classifications': {
        'individual': {
            'address': [{
                'wallet_type': str,
                'confidence': float,
                'risk_level': str,
                'indicators': [str]
            }]
        },
        'coordinated_groups': [{
            'type': str,
            'wallets': [str],
            'count': int
        }]
    },
    'pig_butcherer_analysis': {
        'operators_detected': int,
        'high_confidence_operators': [dict],
        'tron_analysis': dict
    },
    'cross_chain_analysis': {
        'relationships': [dict],
        'bridges_detected': [dict]
    },
    'chain_specific_analysis': {
        'ethereum': { ... },
        'solana': { ... },
        'tron': { ... },
        # ... per chain
    }
}
```

## Wallet Types Detected

| Type | Risk | Description |
|------|------|-------------|
| PIG_BUTCHER_OPERATOR | CRITICAL | Lures victims, extracts large funds |
| BOT_FARM_COORDINATOR | CRITICAL | Creates/manages bot networks |
| RUG_PULL_DEPLOYER | CRITICAL | Creates tokens then drains liquidity |
| MARKET_MANIPULATOR | CRITICAL | Wash trading, spoofing |
| SANCTIONS_EVADER | CRITICAL | Associated with sanctioned entities |
| BOT_FARM_WALLET | HIGH | Individual bot in network |
| SYBIL_ATTACKER | HIGH | Multiple fake identities |
| MIXER_USER | HIGH | Uses tumblers/mixers |
| PUMP_AND_DUMP_OPERATOR | HIGH | Coordinates P&D schemes |
| LAUNDERING_LAYER | HIGH | Intermediate in ML chain |

## Tron Pig Butcherer Detection

Tron is CRITICAL for big money operations:

```python
# Tron addresses start with 'T'
tron_addresses = [
    'TMuA6Yqf6TqUfthPfAWzHkC3fTqJNAipqZ',  # Binance hot wallet
    'TNP2uM4bE7Xv9F8G7H6J5K4L3M2N1B0V9',  # Suspect
]

# The system will automatically:
# 1. Detect large round USDT transfers
# 2. Identify rapid succession patterns
# 3. Track CEX cashouts
# 4. Calculate risk scores
```

## Chain Reliability

```python
# Check data quality
for addr, data in report['data_reliability']['per_address'].items():
    print(f"{addr}: {data['reliability_score']}")
    if data['validation']['warnings']:
        print(f"  Warnings: {data['validation']['warnings']}")
```

## Export Options

```python
# JSON export
engine.export_report(report, 'investigation.json')

# Access network data for visualization
network_data = report['chain_specific_analysis']['ethereum']['network_data']
nodes = network_data['nodes']
edges = network_data['edges']
```

## Tips

1. **Start with Tron** for pig butcherer cases - most big money moves there
2. **Check reliability scores** - low scores mean incomplete data
3. **Review coordinated groups** - bot farms often work together
4. **Cross-chain analysis** - scammers use multiple chains
5. **Export early and often** - save progress

## Free API Limits

| Chain | API | Free Tier |
|-------|-----|-----------|
| Ethereum | Etherscan | 5 calls/sec |
| Solana | Helius | 100k/day |
| Tron | TronGrid | 10 QPS |
| BSC | BscScan | 5 calls/sec |
| Polygon | PolygonScan | 5 calls/sec |

## Support

All modules are in `/root/rmi/munchmaps/v2_advanced/`

Run tests:
```bash
cd /root/rmi/munchmaps/v2_advanced
python3 munchmaps_v2_full.py
```
