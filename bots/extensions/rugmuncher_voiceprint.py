#!/usr/bin/env python3
"""
👤 DEV VOICEPRINT - Cross-Chain Identity Matcher
Fingerprint and track devs across multiple chains and wallets
Unmask serial scammers regardless of how many aliases they use
"""

import os
import json
import asyncio
import aiohttp
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict
import sqlite3
import numpy as np

@dataclass
class DevFingerprint:
    """Behavioral fingerprint of a developer"""
    # Gas preferences
    avg_gas_price: float
    gas_price_std: float
    preferred_gas_levels: List[str]  # low, medium, high
    
    # Timing patterns
    active_hours_distribution: List[float]  # 24-hour distribution
    avg_time_between_txs: float
    timezone_estimate: str
    
    # Code style
    contract_bytecode_hash: str
    function_signature_hashes: List[str]
    compiler_preferences: List[str]
    optimization_runs: int
    
    # Funding patterns
    funding_sources: List[str]  # CEX, DEX, mixers
    funding_amounts_pattern: List[float]
    
    # Social patterns
    launch_timing_pattern: str  # "3am_utc", "weekend", "random"
    
    def to_dict(self) -> Dict:
        return {
            'avg_gas_price': self.avg_gas_price,
            'gas_price_std': self.gas_price_std,
            'preferred_gas_levels': self.preferred_gas_levels,
            'active_hours_distribution': self.active_hours_distribution,
            'avg_time_between_txs': self.avg_time_between_txs,
            'timezone_estimate': self.timezone_estimate,
            'contract_bytecode_hash': self.contract_bytecode_hash,
            'function_signature_hashes': self.function_signature_hashes,
            'compiler_preferences': self.compiler_preferences,
            'optimization_runs': self.optimization_runs,
            'funding_sources': self.funding_sources,
            'funding_amounts_pattern': self.funding_amounts_pattern,
            'launch_timing_pattern': self.launch_timing_pattern
        }

@dataclass
class DevIdentity:
    """Matched identity across chains"""
    identity_id: str  # Unique hash of fingerprint
    primary_wallets: List[str]
    known_aliases: List[str]
    fingerprints: Dict[str, DevFingerprint]  # chain -> fingerprint
    total_rugs: int
    total_victims_usd: float
    first_seen: datetime
    last_active: datetime
    chains_active: List[str]
    risk_level: str
    
    def to_dict(self) -> Dict:
        return {
            'identity_id': self.identity_id,
            'primary_wallets': self.primary_wallets,
            'known_aliases': self.known_aliases,
            'fingerprints': {k: v.to_dict() for k, v in self.fingerprints.items()},
            'total_rugs': self.total_rugs,
            'total_victims_usd': self.total_victims_usd,
            'first_seen': self.first_seen.isoformat(),
            'last_active': self.last_active.isoformat(),
            'chains_active': self.chains_active,
            'risk_level': self.risk_level
        }

class VoiceprintDatabase:
    """Database for dev fingerprints and identities"""
    
    def __init__(self, db_path: str = '/root/rugmuncher_voiceprints.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_tables()
    
    def _init_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dev_fingerprints (
                wallet TEXT PRIMARY KEY,
                chain TEXT,
                fingerprint TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dev_identities (
                identity_id TEXT PRIMARY KEY,
                data TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wallet_links (
                wallet TEXT,
                identity_id TEXT,
                match_confidence REAL,
                PRIMARY KEY (wallet, identity_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rug_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                identity_id TEXT,
                contract TEXT,
                chain TEXT,
                stolen_usd REAL,
                rugged_at TIMESTAMP,
                victims_count INTEGER
            )
        ''')
        
        self.conn.commit()
    
    def save_fingerprint(self, wallet: str, chain: str, fingerprint: Dict):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO dev_fingerprints (wallet, chain, fingerprint)
            VALUES (?, ?, ?)
        ''', (wallet.lower(), chain, json.dumps(fingerprint)))
        self.conn.commit()
    
    def get_fingerprint(self, wallet: str) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT fingerprint FROM dev_fingerprints WHERE wallet = ?', (wallet.lower(),))
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return None
    
    def save_identity(self, identity: DevIdentity):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO dev_identities (identity_id, data, updated_at)
            VALUES (?, ?, ?)
        ''', (identity.identity_id, json.dumps(identity.to_dict()), datetime.now()))
        
        # Update wallet links
        for wallet in identity.primary_wallets:
            cursor.execute('''
                INSERT OR REPLACE INTO wallet_links (wallet, identity_id, match_confidence)
                VALUES (?, ?, ?)
            ''', (wallet.lower(), identity.identity_id, 95.0))
        
        self.conn.commit()
    
    def get_identity_by_wallet(self, wallet: str) -> Optional[DevIdentity]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT i.data FROM dev_identities i
            JOIN wallet_links wl ON i.identity_id = wl.identity_id
            WHERE wl.wallet = ?
        ''', (wallet.lower(),))
        
        row = cursor.fetchone()
        if row:
            data = json.loads(row[0])
            return self._dict_to_identity(data)
        return None
    
    def get_all_fingerprints(self) -> List[Tuple[str, str, Dict]]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT wallet, chain, fingerprint FROM dev_fingerprints')
        return [(row[0], row[1], json.loads(row[2])) for row in cursor.fetchall()]
    
    def add_rug(self, identity_id: str, contract: str, chain: str, 
                stolen_usd: float, victims: int):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO rug_history (identity_id, contract, chain, stolen_usd, rugged_at, victims_count)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (identity_id, contract, chain, stolen_usd, datetime.now(), victims))
        self.conn.commit()
    
    def get_rug_history(self, identity_id: str) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT contract, chain, stolen_usd, rugged_at, victims_count
            FROM rug_history WHERE identity_id = ?
            ORDER BY rugged_at DESC
        ''', (identity_id,))
        
        columns = ['contract', 'chain', 'stolen_usd', 'rugged_at', 'victims_count']
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def _dict_to_identity(self, data: Dict) -> DevIdentity:
        return DevIdentity(
            identity_id=data['identity_id'],
            primary_wallets=data['primary_wallets'],
            known_aliases=data['known_aliases'],
            fingerprints={k: DevFingerprint(**v) for k, v in data['fingerprints'].items()},
            total_rugs=data['total_rugs'],
            total_victims_usd=data['total_victims_usd'],
            first_seen=datetime.fromisoformat(data['first_seen']),
            last_active=datetime.fromisoformat(data['last_active']),
            chains_active=data['chains_active'],
            risk_level=data['risk_level']
        )

class DevVoiceprintAnalyzer:
    """
    Analyze and fingerprint developer behavior
    """
    
    def __init__(self):
        self.db = VoiceprintDatabase()
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Similarity thresholds
        self.GAS_SIMILARITY_THRESHOLD = 0.85
        self.TIMING_SIMILARITY_THRESHOLD = 0.80
        self.CODE_SIMILARITY_THRESHOLD = 0.90
    
    async def start(self):
        self.session = aiohttp.ClientSession()
    
    async def stop(self):
        if self.session:
            await self.session.close()
    
    async def fingerprint_wallet(self, wallet: str, chain: str) -> DevFingerprint:
        """
        Create behavioral fingerprint from wallet activity
        """
        # Check cache
        cached = self.db.get_fingerprint(wallet)
        if cached:
            return DevFingerprint(**cached)
        
        api_key = os.getenv('BSCSCAN_KEY' if chain == 'bsc' else 'ETHERSCAN_KEY', '')
        base = 'api.bscscan.com' if chain == 'bsc' else 'api.etherscan.io'
        
        # Fetch transaction history
        txs = await self._fetch_transactions(wallet, base, api_key)
        
        # Analyze gas patterns
        gas_prices = [int(tx.get('gasPrice', '0'), 16) / 1e9 if isinstance(tx.get('gasPrice'), str) and tx.get('gasPrice').startswith('0x') else float(tx.get('gasPrice', 0)) / 1e9 for tx in txs if tx.get('gasPrice')]
        avg_gas = sum(gas_prices) / len(gas_prices) if gas_prices else 20
        gas_std = np.std(gas_prices) if len(gas_prices) > 1 else 0
        
        # Determine preferred gas levels
        gas_levels = []
        for price in gas_prices:
            if price < 10:
                gas_levels.append('low')
            elif price < 50:
                gas_levels.append('medium')
            else:
                gas_levels.append('high')
        
        preferred_levels = list(set(gas_levels))
        
        # Analyze timing patterns
        hours = [datetime.fromtimestamp(int(tx['timeStamp'])).hour for tx in txs]
        hour_dist = [hours.count(h) / len(hours) if hours else 0 for h in range(24)]
        
        # Estimate timezone
        peak_hour = hour_dist.index(max(hour_dist)) if hour_dist else 12
        if 0 <= peak_hour <= 6:
            timezone = 'UTC-5 to UTC-8 (Americas Night)'
        elif 6 <= peak_hour <= 12:
            timezone = 'UTC+0 to UTC+4 (Europe)'
        else:
            timezone = 'UTC+8 to UTC+12 (Asia)'
        
        # Time between transactions
        timestamps = sorted([int(tx['timeStamp']) for tx in txs])
        if len(timestamps) > 1:
            intervals = [(timestamps[i] - timestamps[i-1]) / 3600 for i in range(1, len(timestamps))]
            avg_interval = sum(intervals) / len(intervals)
        else:
            avg_interval = 24
        
        # Get contract code fingerprint
        contract_data = await self._get_contract_data(wallet, base, api_key)
        
        fingerprint = DevFingerprint(
            avg_gas_price=avg_gas,
            gas_price_std=gas_std,
            preferred_gas_levels=preferred_levels,
            active_hours_distribution=hour_dist,
            avg_time_between_txs=avg_interval,
            timezone_estimate=timezone,
            contract_bytecode_hash=contract_data.get('bytecode_hash', ''),
            function_signature_hashes=contract_data.get('function_sigs', []),
            compiler_preferences=contract_data.get('compilers', []),
            optimization_runs=contract_data.get('optimization', 200),
            funding_sources=[],  # Would require deeper analysis
            funding_amounts_pattern=[],
            launch_timing_pattern=self._classify_launch_timing(hours)
        )
        
        # Cache fingerprint
        self.db.save_fingerprint(wallet, chain, fingerprint.to_dict())
        
        return fingerprint
    
    async def _fetch_transactions(self, wallet: str, base: str, api_key: str) -> List[Dict]:
        """Fetch transaction history"""
        try:
            url = f"https://{base}/api?module=account&action=txlist&address={wallet}&page=1&offset=100&sort=desc&apikey={api_key}"
            async with self.session.get(url, timeout=10) as r:
                data = await r.json()
                if data.get('status') == '1':
                    return data.get('result', [])
        except Exception as e:
            print(f"[Voiceprint] Error fetching txs: {e}")
        return []
    
    async def _get_contract_data(self, wallet: str, base: str, api_key: str) -> Dict:
        """Get contract deployment data"""
        try:
            url = f"https://{base}/api?module=contract&action=getsourcecode&address={wallet}&apikey={api_key}"
            async with self.session.get(url, timeout=10) as r:
                data = await r.json()
                if data.get('status') == '1' and data.get('result'):
                    result = data['result'][0]
                    return {
                        'bytecode_hash': hashlib.sha256(result.get('SourceCode', '').encode()).hexdigest()[:16],
                        'function_sigs': [],  # Would parse ABI
                        'compilers': [result.get('CompilerVersion', 'Unknown')],
                        'optimization': 200 if result.get('OptimizationUsed') == '1' else 0
                    }
        except Exception as e:
            print(f"[Voiceprint] Error fetching contract: {e}")
        
        return {'bytecode_hash': '', 'function_sigs': [], 'compilers': [], 'optimization': 0}
    
    def _classify_launch_timing(self, hours: List[int]) -> str:
        """Classify launch timing pattern"""
        if not hours:
            return 'unknown'
        
        avg_hour = sum(hours) / len(hours)
        
        if 0 <= avg_hour <= 5:
            return '3am_utc'
        elif 5 <= avg_hour <= 9:
            return 'early_morning'
        elif avg_hour >= 22 or avg_hour <= 2:
            return 'late_night'
        else:
            return 'business_hours'
    
    def calculate_similarity(self, fp1: DevFingerprint, fp2: DevFingerprint) -> float:
        """
        Calculate similarity score between two fingerprints
        Returns 0-1 where 1 = identical
        """
        scores = []
        
        # Gas pattern similarity
        gas_diff = abs(fp1.avg_gas_price - fp2.avg_gas_price) / max(fp1.avg_gas_price, 1)
        gas_sim = max(0, 1 - gas_diff)
        scores.append(gas_sim)
        
        # Timing similarity (correlation of hour distributions)
        if fp1.active_hours_distribution and fp2.active_hours_distribution:
            timing_sim = np.corrcoef(fp1.active_hours_distribution, fp2.active_hours_distribution)[0, 1]
            if not np.isnan(timing_sim):
                scores.append(max(0, timing_sim))
        
        # Code similarity
        if fp1.contract_bytecode_hash and fp2.contract_bytecode_hash:
            code_sim = 1.0 if fp1.contract_bytecode_hash == fp2.contract_bytecode_hash else 0.0
            scores.append(code_sim)
        
        # Launch timing
        if fp1.launch_timing_pattern == fp2.launch_timing_pattern:
            scores.append(1.0)
        else:
            scores.append(0.3)
        
        return sum(scores) / len(scores) if scores else 0
    
    async def match_identity(self, wallet: str, chain: str) -> Optional[Tuple[DevIdentity, float]]:
        """
        Match wallet to known identity
        Returns matched identity and confidence score
        """
        # First check if wallet already linked
        existing = self.db.get_identity_by_wallet(wallet)
        if existing:
            return existing, 95.0
        
        # Generate fingerprint
        fingerprint = await self.fingerprint_wallet(wallet, chain)
        
        # Compare against all known fingerprints
        all_fps = self.db.get_all_fingerprints()
        
        best_match = None
        best_score = 0
        
        for known_wallet, known_chain, known_fp_data in all_fps:
            if known_wallet == wallet:
                continue
            
            known_fp = DevFingerprint(**known_fp_data)
            similarity = self.calculate_similarity(fingerprint, known_fp)
            
            # Check if similarity exceeds threshold
            if similarity > 0.85 and similarity > best_score:
                identity = self.db.get_identity_by_wallet(known_wallet)
                if identity:
                    best_match = identity
                    best_score = similarity
        
        if best_match:
            return best_match, best_score * 100
        
        return None, 0
    
    async def analyze_dev(self, wallet: str, chain: str) -> Dict:
        """
        Full analysis including cross-chain identity matching
        """
        # Get or create fingerprint
        fingerprint = await self.fingerprint_wallet(wallet, chain)
        
        # Try to match to known identity
        matched_identity, confidence = await self.match_identity(wallet, chain)
        
        if matched_identity:
            # Add this wallet to existing identity
            if wallet not in matched_identity.primary_wallets:
                matched_identity.primary_wallets.append(wallet)
                matched_identity.chains_active.append(chain)
                matched_identity.last_active = datetime.now()
                self.db.save_identity(matched_identity)
            
            rug_history = self.db.get_rug_history(matched_identity.identity_id)
            
            return {
                'wallet': wallet,
                'chain': chain,
                'identity_matched': True,
                'identity_id': matched_identity.identity_id,
                'match_confidence': confidence,
                'known_aliases': matched_identity.known_aliases,
                'total_rugs': matched_identity.total_rugs,
                'total_stolen': matched_identity.total_victims_usd,
                'cross_chains': matched_identity.chains_active,
                'rug_history': rug_history,
                'risk_level': matched_identity.risk_level,
                'fingerprint': fingerprint.to_dict()
            }
        else:
            # Create new identity
            identity_id = hashlib.sha256(f"{wallet}:{chain}:{datetime.now()}".encode()).hexdigest()[:16]
            
            new_identity = DevIdentity(
                identity_id=identity_id,
                primary_wallets=[wallet],
                known_aliases=[wallet[:12]],
                fingerprints={chain: fingerprint},
                total_rugs=0,
                total_victims_usd=0,
                first_seen=datetime.now(),
                last_active=datetime.now(),
                chains_active=[chain],
                risk_level='UNKNOWN'
            )
            
            self.db.save_identity(new_identity)
            
            return {
                'wallet': wallet,
                'chain': chain,
                'identity_matched': False,
                'identity_id': identity_id,
                'match_confidence': 0,
                'known_aliases': [],
                'total_rugs': 0,
                'total_stolen': 0,
                'cross_chains': [chain],
                'rug_history': [],
                'risk_level': 'UNKNOWN',
                'fingerprint': fingerprint.to_dict()
            }
    
    def format_voiceprint_report(self, analysis: Dict) -> str:
        """Format voiceprint analysis for display"""
        
        if analysis['identity_matched']:
            status_emoji = "💀" if analysis['total_rugs'] >= 3 else "🚨" if analysis['total_rugs'] >= 1 else "⚠️"
            matched_text = f"""
<b>🎯 IDENTITY MATCHED!</b>
<b>Confidence:</b> {analysis['match_confidence']:.1f}%
<b>Known Aliases:</b> {', '.join(analysis['known_aliases'])}
"""
        else:
            status_emoji = "🆕"
            matched_text = "<b>🆕 New Identity</b>\nNo prior matches found\n"
        
        text = f"""
{status_emoji} <b>DEV VOICEPRINT ANALYSIS</b> {status_emoji}

<b>Wallet:</b> <code>{analysis['wallet'][:16]}...</code>
<b>Chain:</b> {analysis['chain'].upper()}
<b>Identity ID:</b> <code>{analysis['identity_id']}</code>

{matched_text}
"""
        
        if analysis['total_rugs'] > 0:
            text += f"""
╔════════════════════════════════════════════════╗
║  💀 <b>SERIAL SCAMMER DETECTED</b> 💀
╚════════════════════════════════════════════════╝

<b>Total Rugs:</b> {analysis['total_rugs']}
<b>Total Stolen:</b> ${analysis['total_stolen']:,.0f}
<b>Active Chains:</b> {', '.join(analysis['cross_chains'])}
"""
        
        if analysis['rug_history']:
            text += """
<b>📜 RUG HISTORY:</b>
"""
            for rug in analysis['rug_history'][:5]:
                text += f"• {rug['chain'].upper()}: ${rug['stolen_usd']:,.0f} - {rug['contract'][:12]}...\n"
        
        # Fingerprint details
        fp = analysis['fingerprint']
        text += f"""
<b>🧬 BEHAVIORAL FINGERPRINT:</b>
• Avg Gas Price: {fp['avg_gas_price']:.1f} Gwei
• Timezone: {fp['timezone_estimate']}
• Launch Pattern: {fp['launch_timing_pattern']}
• Code Signature: {fp['contract_bytecode_hash'][:8]}...
"""
        
        return text

# ═══════════════════════════════════════════════════════════
# USAGE
# ═══════════════════════════════════════════════════════════

async def main():
    analyzer = DevVoiceprintAnalyzer()
    await analyzer.start()
    
    try:
        analysis = await analyzer.analyze_dev(
            '0x1234567890abcdef1234567890abcdef12345678',
            'bsc'
        )
        print(analyzer.format_voiceprint_report(analysis))
    finally:
        await analyzer.stop()

if __name__ == "__main__":
    asyncio.run(main())
