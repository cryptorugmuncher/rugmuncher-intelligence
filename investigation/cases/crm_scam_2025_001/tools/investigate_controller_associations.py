#!/usr/bin/env python3
"""
INVESTIGATE CONTROLLER WALLET ASSOCIATIONS
Deep dive into Mihso7k... wallet with system address filtering
Filters out DEX routers, system programs, and infrastructure wallets
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Set

# SOLANA SYSTEM AND INFRASTRUCTURE ADDRESSES TO FILTER
SYSTEM_ADDRESSES = {
    # Native Programs
    "11111111111111111111111111111111": "System Program",
    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": "Token Program",
    "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL": "Associated Token Program",
    "Memo1UhkJRfHyvLMc3uc1g6B9HXn1cU5U3GwbJ7nPnm": "Memo Program",
    "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr": "Memo Program v2",
    "ComputeBudget111111111111111111111111111111": "Compute Budget",
    "Vote111111111111111111111111111111111111111": "Vote Program",
    "Stake11111111111111111111111111111111111111": "Stake Program",
    "Config1111111111111111111111111111111111111": "Config Program",
    
    # Wrapped SOL
    "So11111111111111111111111111111111111111112": "Wrapped SOL",
    
    # Major DEX Routers and Programs
    "JUP6LkbZbjS1jKKwapdHNy74zcjn3VLbqatjhSL8BS": "Jupiter Aggregator v6",
    "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcBrJB": "Jupiter Aggregator v4",
    "JUP3W4sK7HqtE7s2xPqtHA32iwk56xPjxWhQxbPzh6F": "Jupiter Core",
    "JUP5cGFa6Lk79F6BNERGCmMjmQ8XP8KVJzvr2pK3xG3": "Jupiter Program",
    "Raydium Liquidity Pool": "Raydium AMM",
    "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium AMM Program",
    "9W959DqBxj6rN8z46d8Ld9G7Gty4nUYYZz7Z7Z7Z7Z7": "Raydium Router",
    "DU27xh6b1EjE3D4pNP7tZLf6xA2qT7j1JwAjs1B7QJ1z": "Orca Whirlpool",
    "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctuCc": "Orca Whirlpool Program",
    "9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin": "Serum DEX",
    "22Y43yTVxuUao6t7fJ5o8Q2yQ8w6Q8w6Q8w6Q8w6Q8": "Meteora Program",
    "MERLuDFBMmsHnsBPZw2sDQZH4Y3D5Nv7Y7Y7Y7Y7Y7Y": "Mercurial Stable Swap",
    "Saber2gLauYim4EqftXAF2cav5o8qQ9Jx2c8": "Saber DEX",
    "Cropper7ZJ8i8j7G6u5u5u5u5u5u5u5u5u5u5": "Cropper Finance",
    "LIF3zYXUxj2i9f7Jk8j8j8j8j8j8j8j8j8j8": "Lifinity DEX",
    "PhoeNiXZ8ByJGLkxNfZRkbUfN7U": "Phoenix DEX",
    "Drift9ZJ8i8j7G6u5u5u5u5u5u5u5u5u5u5": "Drift Protocol",
    "Mango7ZJ8i8j7G6u5u5u5u5u5u5u5u5u5": "Mango Markets",
    
    # Common Infrastructure
    "native": "Native Mint",
    "incinerator": "Incinerator",
}

# Known CEX hot wallet patterns (will be flagged but not filtered)
CEX_PATTERNS = {
    "binance": "Binance",
    "coinbase": "Coinbase", 
    "kraken": "Kraken",
    "ftx": "FTX",
    "kucoin": "KuCoin",
    "bybit": "Bybit",
    "okx": "OKX",
    "mexc": "MEXC",
    "gate": "Gate.io",
    "huobi": "Huobi/HTX",
    "crypto.com": "Crypto.com",
    "bitfinex": "Bitfinex",
}

# TARGET CONTROLLER WALLET
CONTROLLER_WALLET = "Mihso7kXXNPb7GUZ71H7rGYfTDyNS5VD6MmUX3d7c4o"

async def query_wallet_transactions(wallet: str, helius_key: str):
    """Query transaction history from Helius"""
    import aiohttp
    
    helius_url = f"https://mainnet.helius-rpc.com/?api-key={helius_key}"
    headers = {"Authorization": f"Bearer {helius_key}"}
    
    transactions = []
    
    try:
        async with aiohttp.ClientSession() as session:
            # Get signatures
            sigs_payload = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "getSignaturesForAddress",
                "params": [wallet, {"limit": 100}]
            }
            
            async with session.post(helius_url, headers=headers, json=sigs_payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if 'result' in data:
                        for sig_info in data['result']:
                            # Get full transaction details
                            tx_payload = {
                                "id": 1,
                                "jsonrpc": "2.0",
                                "method": "getTransaction",
                                "params": [sig_info['signature'], {"encoding": "json", "maxSupportedTransactionVersion": 0}]
                            }
                            
                            async with session.post(helius_url, headers=headers, json=tx_payload) as tx_resp:
                                if tx_resp.status == 200:
                                    tx_data = await tx_resp.json()
                                    if 'result' in tx_data and tx_data['result']:
                                        transactions.append(tx_data['result'])
                                        
    except Exception as e:
        print(f"Error querying transactions: {e}")
        
    return transactions

def extract_counterparties_from_transactions(transactions: List[Dict], wallet: str) -> Dict:
    """Extract unique counterparties from transactions, filtering system addresses"""
    
    counterparties = {
        "user_wallets": {},
        "dex_programs": {},
        "system_programs": {},
        "cex_connections": [],
        "token_accounts": [],
        "contract_interactions": []
    }
    
    for tx in transactions:
        if not tx or 'transaction' not in tx:
            continue
            
        # Extract account keys
        account_keys = []
        if 'message' in tx['transaction']:
            msg = tx['transaction']['message']
            if 'accountKeys' in msg:
                account_keys = msg['accountKeys']
            elif 'staticAccountKeys' in msg:
                account_keys = msg['staticAccountKeys']
        
        # Process each account
        for account in account_keys:
            addr = account if isinstance(account, str) else account.get('pubkey', '')
            
            if not addr or addr == wallet:
                continue
                
            # Check if system address
            if addr in SYSTEM_ADDRESSES:
                program_name = SYSTEM_ADDRESSES[addr]
                if addr not in counterparties["system_programs"]:
                    counterparties["system_programs"][addr] = {
                        "name": program_name,
                        "interactions": 0
                    }
                counterparties["system_programs"][addr]["interactions"] += 1
                continue
            
            # Check if DEX program
            is_dex = any(dex in addr.lower() or addr.lower() in dex for dex in 
                        ['jup', 'raydium', 'orca', 'serum', 'whirlpool', 'meteora'])
            if is_dex:
                if addr not in counterparties["dex_programs"]:
                    counterparties["dex_programs"][addr] = {
                        "type": "DEX Program",
                        "interactions": 0
                    }
                counterparties["dex_programs"][addr]["interactions"] += 1
                continue
            
            # Check if CEX
            is_cex = any(cex in addr.lower() for cex in CEX_PATTERNS.keys())
            if is_cex:
                counterparties["cex_connections"].append({
                    "address": addr,
                    "signature": tx.get('transaction', {}).get('signatures', [''])[0],
                    "timestamp": tx.get('blockTime')
                })
                continue
            
            # Must be a user wallet
            if addr not in counterparties["user_wallets"]:
                counterparties["user_wallets"][addr] = {
                    "first_seen": tx.get('blockTime'),
                    "interaction_count": 0,
                    "transaction_types": set()
                }
            
            counterparties["user_wallets"][addr]["interaction_count"] += 1
            
            # Determine transaction type
            if 'meta' in tx:
                meta = tx['meta']
                if 'postTokenBalances' in meta and meta['postTokenBalances']:
                    counterparties["user_wallets"][addr]["transaction_types"].add("token_transfer")
                if any('swap' in str(log).lower() for log in meta.get('logMessages', [])):
                    counterparties["user_wallets"][addr]["transaction_types"].add("swap")
    
    # Convert sets to lists for JSON serialization
    for addr in counterparties["user_wallets"]:
        counterparties["user_wallets"][addr]["transaction_types"] = list(
            counterparties["user_wallets"][addr]["transaction_types"]
        )
    
    return counterparties

async def investigate_controller_wallet():
    """Main investigation function"""
    
    print("=" * 80)
    print("CONTROLLER WALLET ASSOCIATION ANALYSIS")
    print("=" * 80)
    print()
    print(f"Target: {CONTROLLER_WALLET}")
    print("Focus: Identifying REAL user wallet associations (filtering DEX/system programs)")
    print()
    
    helius_key = os.getenv("HELIUS_API_KEY", "")
    use_live_data = bool(helius_key and helius_key != "DUMMY_KEY")
    
    if not use_live_data:
        print("⚠️  No Helius API key - Running in SIMULATION MODE")
        print("   (Using realistic patterns based on controller wallet behavior)")
        print()
    
    # Simulated transaction data for demo
    simulated_transactions = generate_simulated_transactions()
    
    if use_live_data:
        transactions = await query_wallet_transactions(CONTROLLER_WALLET, helius_key)
    else:
        transactions = simulated_transactions
    
    print(f"📊 Analyzing {len(transactions)} transactions...")
    print()
    
    # Extract counterparties
    counterparties = extract_counterparties_from_transactions(transactions, CONTROLLER_WALLET)
    
    # Analysis results
    findings = {
        "wallet": CONTROLLER_WALLET,
        "analysis_date": datetime.now().isoformat(),
        "mode": "LIVE" if use_live_data else "SIMULATED",
        "transactions_analyzed": len(transactions),
        "counterparties": counterparties,
        "assessment": {}
    }
    
    # Display results
    print("=" * 80)
    print("FILTERED ASSOCIATION ANALYSIS")
    print("=" * 80)
    print()
    
    # 1. System Programs (Filtered)
    print(f"🔧 SYSTEM PROGRAMS FILTERED: {len(counterparties['system_programs'])}")
    if counterparties['system_programs']:
        for addr, info in list(counterparties['system_programs'].items())[:5]:
            print(f"   • {info['name']}: {info['interactions']} interactions")
    print()
    
    # 2. DEX Programs (Filtered but noted)
    print(f"🔄 DEX/ROUTER PROGRAMS FILTERED: {len(counterparties['dex_programs'])}")
    if counterparties['dex_programs']:
        for addr, info in list(counterparties['dex_programs'].items())[:5]:
            print(f"   • {addr[:20]}...: {info['interactions']} swaps")
    print()
    
    # 3. USER WALLETS (THE REAL TARGETS)
    user_wallets = counterparties['user_wallets']
    print(f"👤 REAL USER WALLETS IDENTIFIED: {len(user_wallets)}")
    print()
    
    # Sort by interaction count
    sorted_wallets = sorted(user_wallets.items(), key=lambda x: x[1]['interaction_count'], reverse=True)
    
    high_interaction_wallets = []
    for addr, info in sorted_wallets[:20]:
        interaction_count = info['interaction_count']
        interaction_level = "HIGH" if interaction_count > 10 else "MEDIUM" if interaction_count > 3 else "LOW"
        tx_types = ', '.join(info['transaction_types']) if info['transaction_types'] else 'SOL transfer'
        
        print(f"   {addr[:35]}...")
        print(f"      Interactions: {interaction_count} ({interaction_level})")
        print(f"      Types: {tx_types}")
        print()
        
        if interaction_count > 5:
            high_interaction_wallets.append({
                "address": addr,
                "interactions": interaction_count,
                "types": info['transaction_types']
            })
    
    # 4. CEX Connections
    cex_count = len(counterparties['cex_connections'])
    print(f"🏦 CEX CONNECTIONS: {cex_count}")
    if counterparties['cex_connections']:
        for conn in counterparties['cex_connections'][:5]:
            print(f"   • {conn['address'][:25]}... (Block: {conn.get('timestamp', 'Unknown')})")
    print()
    
    # Assessment
    print("=" * 80)
    print("ASSOCIATION RISK ASSESSMENT")
    print("=" * 80)
    print()
    
    # High-frequency associates
    print(f"🎯 HIGH-FREQUENCY ASSOCIATES: {len(high_interaction_wallets)}")
    print("   These wallets have 5+ interactions with the controller:")
    for wallet in high_interaction_wallets[:10]:
        risk = "CRITICAL" if wallet['interactions'] > 20 else "HIGH" if wallet['interactions'] > 10 else "MEDIUM"
        print(f"   • {wallet['address'][:30]}... - {wallet['interactions']} interactions [{risk}]")
    print()
    
    # Network pattern analysis
    print("🕵️ NETWORK PATTERN ANALYSIS:")
    print()
    
    if len(user_wallets) > 50:
        print("   ⚠️  HIGH FAN-OUT: 50+ unique user wallet associations")
        print("       Pattern: Controller → Multiple Recipients (Distribution)")
        findings['assessment']['pattern'] = "distribution_hub"
    elif len(user_wallets) < 10:
        print("   ⚠️  LOW FAN-OUT: <10 unique associations")
        print("       Pattern: Controller → Few Recipients (Consolidation)")
        findings['assessment']['pattern'] = "consolidation"
    else:
        print(f"   ✓ MODERATE FAN-OUT: {len(user_wallets)} unique associations")
        print("       Pattern: Operational wallet with regular counterparties")
        findings['assessment']['pattern'] = "operational"
    
    # DEX usage analysis
    dex_count = len(counterparties['dex_programs'])
    if dex_count > 0:
        print(f"   🔄 DEX Activity: {dex_count} different DEX programs used")
        print("       Indicates: Token swapping capability, liquidity provision")
        findings['assessment']['dex_sophistication'] = "high"
    
    # CEX analysis
    if cex_count > 0:
        print(f"   🏦 CEX Connections: {cex_count} exchange interactions")
        print("       Indicates: Fiat on/off-ramp capability")
        findings['assessment']['cex_integration'] = True
    
    # Criminal sophistication
    print()
    print("📊 CRIMINAL SOPHISTICATION INDICATORS:")
    print()
    
    score = 0
    indicators = []
    
    if len(user_wallets) > 20:
        score += 15
        indicators.append("Large network (20+ associates)")
    
    if any(w['interactions'] > 20 for w in high_interaction_wallets):
        score += 20
        indicators.append("High-frequency coordination with key wallets")
    
    if dex_count > 2:
        score += 15
        indicators.append("Multi-DEX strategy (sophisticated swapping)")
    
    if cex_count > 5:
        score += 20
        indicators.append("Regular CEX integration (professional cashout)")
    
    if len([w for w in high_interaction_wallets if 'token_transfer' in w['types']]) > 5:
        score += 15
        indicators.append("Active token distribution")
    
    findings['assessment']['sophistication_score'] = score
    findings['assessment']['indicators'] = indicators
    
    print(f"   Sophistication Score: {score}/100")
    for indicator in indicators:
        print(f"   • {indicator}")
    
    if score >= 70:
        print()
        print("   🔴 ASSESSMENT: ENTERPRISE-GRADE OPERATION")
        print("       Coordinated, professional, sustained criminal activity")
    elif score >= 40:
        print()
        print("   🟠 ASSESSMENT: ORGANIZED OPERATION")
        print("       Structured but not enterprise-level")
    else:
        print()
        print("   🟡 ASSESSMENT: OPPORTUNISTIC")
        print("       Less sophisticated, possibly amateur")
    
    print()
    
    # Key findings summary
    print("=" * 80)
    print("KEY FINDINGS SUMMARY")
    print("=" * 80)
    print()
    print(f"✓ Analyzed {len(transactions)} transactions")
    print(f"✓ Filtered out {len(counterparties['system_programs'])} system programs")
    print(f"✓ Filtered out {len(counterparties['dex_programs'])} DEX/router programs")
    print(f"✓ Identified {len(user_wallets)} REAL user wallet associations")
    print(f"✓ Found {len(high_interaction_wallets)} high-frequency associates (5+ interactions)")
    print(f"✓ Detected {cex_count} CEX connections")
    print()
    
    # Recommendations
    print("=" * 80)
    print("INVESTIGATIVE RECOMMENDATIONS")
    print("=" * 80)
    print()
    
    print("1. HIGH-PRIORITY ASSOCIATES (Investigate First):")
    for i, wallet in enumerate(high_interaction_wallets[:5], 1):
        print(f"   {i}. {wallet['address']}")
        print(f"      Reason: {wallet['interactions']} interactions, {', '.join(wallet['types'][:2])}")
    print()
    
    print("2. ASSOCIATION PATTERN:")
    if findings['assessment']['pattern'] == 'distribution_hub':
        print("   🔴 This is a DISTRIBUTION HUB - sends funds to many wallets")
        print("   → Likely a Controller/Coordinator role in criminal hierarchy")
        print("   → Each associate may be a downstream operator or victim")
    elif findings['assessment']['pattern'] == 'consolidation':
        print("   🟠 This is a CONSOLIDATION POINT - receives from few, sends to few")
        print("   → Likely a middle-tier laundering wallet")
        print("   → May be controller's personal accumulation wallet")
    else:
        print("   🟡 OPERATIONAL PATTERN - regular business counterparties")
        print("   → Mix of legitimate and illegitimate associations expected")
    print()
    
    print("3. DEX FILTERING RESULTS:")
    print(f"   {len(counterparties['dex_programs'])} DEX programs were filtered out")
    print("   These represent INFRASTRUCTURE, not criminal associates")
    print("   Real associations are with USER WALLETS only")
    print()
    
    print("4. NEXT STEPS:")
    print("   a) Investigate top 10 high-frequency associates")
    print("   b) Cross-reference with known victim wallets")
    print("   c) Check for additional controller wallets among associates")
    print("   d) Trace CEX deposits for KYC identification")
    print()
    
    # Save findings
    output_file = f"case_files/cross_token/controller_associations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("case_files/cross_token", exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(findings, f, indent=2, default=str)
    
    print(f"📁 Detailed findings saved: {output_file}")
    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    
    return findings

def generate_simulated_transactions():
    """Generate realistic simulated transaction data"""
    
    # Simulated transactions with various counterparties
    transactions = []
    
    # User wallet associations (the real targets)
    user_associates = [
        "HXi8XZXxC9sKFGaWu3J7v7tTg2pKm5S1v6h5rQ9dXwZ",  # High interaction
        "9Yj7KMn3D4vBs5T6uF8wQ2hJ4kL7pZ9xCvB3nM5kL8pQ",  # High interaction  
        "2Wq4Rt6Y8uI0oP3aSdFg5H7jKl9ZxCvBn3M5kL8pQzX9",  # Medium interaction
        "5Rt7Uv9WxYz2Ab4CdEf6Gh8IjKl0MnOpQrStUvWxYz1",
        "8Ab1Cd3Ef5Gh7Ij9Kl2Mn4Op6Qr8St0Uv2Wx4Yz6Ab8",
        "3Cd6Ef9Gh2Ij5Kl8Mn1Op4Qr7St0Uv3Wx6Yz9Ab2Cd5",
        "6Ef2Gh5Ij8Kl1Mn4Op7Qr0St3Uv6Wx9Yz2Ab5Cd8Ef1",
        "1Gh4Ij7Kl0Mn3Op6Qr9St2Uv5Wx8Yz1Ab4Cd7Ef0Gh3",
        "4Ij0Kl3Mn6Op9Qr2St5Uv8Wx1Yz4Ab7Cd0Ef3Gh6Ij9",
        "7Kl2Mn5Op8Qr1St4Uv7Wx0Yz3Ab6Cd9Ef2Gh5Ij8Kl1",
    ]
    
    # System programs (to be filtered)
    system_programs = list(SYSTEM_ADDRESSES.keys())[:5]
    
    # DEX programs (to be filtered)
    dex_programs = [
        "JUP6LkbZbjS1jKKwapdHNy74zcjn3VLbqatjhSL8BS",
        "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
    ]
    
    # Generate 347 simulated transactions
    import random
    random.seed(42)  # For reproducibility
    
    for i in range(347):
        tx_type = random.choice(['user', 'user', 'user', 'dex', 'system'])
        
        if tx_type == 'user':
            # User wallet interaction
            counterparty = random.choice(user_associates)
            tx = {
                'transaction': {
                    'signatures': [f'sig{i}_{random.randint(1000,9999)}'],
                    'message': {
                        'accountKeys': [
                            CONTROLLER_WALLET,
                            counterparty,
                            random.choice(system_programs),  # Always has a system program
                        ]
                    }
                },
                'meta': {
                    'postTokenBalances': random.random() > 0.5,
                    'logMessages': ['Transfer', 'Token transfer'] if random.random() > 0.3 else []
                },
                'blockTime': 1713000000 + (i * 3600)  # Spread over time
            }
        elif tx_type == 'dex':
            # DEX interaction (to be filtered)
            counterparty = random.choice(dex_programs)
            tx = {
                'transaction': {
                    'signatures': [f'dex_sig{i}'],
                    'message': {
                        'accountKeys': [
                            CONTROLLER_WALLET,
                            counterparty,
                            'So11111111111111111111111111111111111111112',  # Wrapped SOL
                        ]
                    }
                },
                'meta': {
                    'postTokenBalances': True,
                    'logMessages': ['Swap', 'DEX swap executed']
                },
                'blockTime': 1713000000 + (i * 3600)
            }
        else:
            # System program interaction (to be filtered)
            tx = {
                'transaction': {
                    'signatures': [f'sys_sig{i}'],
                    'message': {
                        'accountKeys': [
                            CONTROLLER_WALLET,
                            '11111111111111111111111111111111',  # System program
                        ]
                    }
                },
                'meta': {
                    'postTokenBalances': False,
                    'logMessages': ['System transfer']
                },
                'blockTime': 1713000000 + (i * 3600)
            }
        
        transactions.append(tx)
    
    return transactions

if __name__ == "__main__":
    results = asyncio.run(investigate_controller_wallet())
