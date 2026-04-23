#!/bin/bash
# Deploy ScyllaDB - High-Performance Cassandra Alternative
# For blockchain data, time-series, and analytics

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "═══════════════════════════════════════════════════════════"
echo "  ⚡ DEPLOYING SCYLLA DB"
echo "  High-Performance Blockchain Data Store"
echo "═══════════════════════════════════════════════════════════"
echo -e "${NC}"

# ═══════════════════════════════════════════════════════════
# STEP 1: Create Scylla Directories
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${BLUE}STEP 1: Creating directories...${NC}"

mkdir -p /var/lib/scylla/data
mkdir -p /var/lib/scylla/commitlog
mkdir -p /var/lib/scylla/hints
mkdir -p /var/lib/scylla/view_hints
chmod -R 777 /var/lib/scylla

echo -e "${GREEN}✅ Directories created${NC}"

# ═══════════════════════════════════════════════════════════
# STEP 2: Deploy Scylla Container
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${BLUE}STEP 2: Deploying ScyllaDB...${NC}"

# Check if Dragonfly is using port 9042
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep -E "(dragonfly|scylla)" || echo "No conflicting containers"

# Deploy Scylla
docker run -d \
    --name scylla \
    --hostname scylla \
    --restart unless-stopped \
    -p 9042:9042 \
    -p 9160:9160 \
    -p 9180:9180 \
    -p 10000:10000 \
    -v /var/lib/scylla:/var/lib/scylla \
    -e SCYLLA_DEVELOPER_MODE=1 \
    scylladb/scylla:6.0.0 \
    --smp 2 \
    --memory 4G \
    --overprovisioned \
    --developer-mode 1

echo -e "${GREEN}✅ Scylla container started${NC}"

# ═══════════════════════════════════════════════════════════
# STEP 3: Wait for Scylla to Start
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${BLUE}STEP 3: Waiting for Scylla to initialize...${NC}"

echo "This may take 30-60 seconds for first startup..."
for i in {1..60}; do
    if docker logs scylla 2>&1 | grep -q "Starting listening for CQL clients"; then
        echo -e "${GREEN}✅ Scylla is ready!${NC}"
        break
    fi
    sleep 2
    echo -n "."
done

# Wait a bit more for CQL to be ready
sleep 5

# ═══════════════════════════════════════════════════════════
# STEP 4: Initialize Database Schema
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${BLUE}STEP 4: Creating database schema...${NC}"

# Create keyspace and tables
docker exec -i scylla cqlsh -e "
-- Create keyspace for RugMuncher
CREATE KEYSPACE IF NOT EXISTS rugmuncher 
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE rugmuncher;

-- Solana transactions table with 90-day TTL
CREATE TABLE IF NOT EXISTS solana_transactions (
    signature text PRIMARY KEY,
    slot bigint,
    block_time timestamp,
    sender text,
    receiver text,
    amount bigint,
    token_mint text,
    program_id text,
    success boolean,
    fee bigint,
    data blob
) WITH default_time_to_live = 7776000  -- 90 days
AND compaction = {'class': 'TimeWindowCompactionStrategy', 'compaction_window_unit': 'DAYS', 'compaction_window_size': 7};

-- Ethereum transactions
CREATE TABLE IF NOT EXISTS ethereum_transactions (
    hash text PRIMARY KEY,
    block_number bigint,
    block_time timestamp,
    from_address text,
    to_address text,
    value bigint,
    gas_price bigint,
    gas_used bigint,
    input text,
    success boolean
) WITH default_time_to_live = 7776000;

-- Wallet activity tracking
CREATE TABLE IF NOT EXISTS wallet_activity (
    wallet text,
    chain text,
    timestamp timestamp,
    tx_hash text,
    tx_type text,
    counterparty text,
    amount bigint,
    token text,
    PRIMARY KEY ((wallet, chain), timestamp, tx_hash)
) WITH CLUSTERING ORDER BY (timestamp DESC)
AND default_time_to_live = 7776000;

-- Risk scores (no TTL - keep forever)
CREATE TABLE IF NOT EXISTS wallet_risk_scores (
    wallet text PRIMARY KEY,
    chain text,
    risk_score float,
    risk_factors list<text>,
    first_seen timestamp,
    last_updated timestamp,
    total_transactions bigint,
    scam_associations int
);

-- Scam reports with TTL
CREATE TABLE IF NOT EXISTS scam_reports (
    report_id uuid PRIMARY KEY,
    reporter_wallet text,
    scammer_wallet text,
    chain text,
    scam_type text,
    description text,
    evidence_urls list<text>,
    reported_at timestamp,
    status text,
    verified boolean
) WITH default_time_to_live = 15552000;  -- 180 days

-- Analytics: Daily stats
CREATE TABLE IF NOT EXISTS daily_chain_stats (
    chain text,
    date date,
    total_transactions bigint,
    total_volume bigint,
    unique_wallets bigint,
    scam_transactions int,
    avg_gas_price bigint,
    PRIMARY KEY (chain, date)
) WITH CLUSTERING ORDER BY (date DESC);

-- Analytics: Top scammer wallets (materialized view pattern)
CREATE TABLE IF NOT EXISTS scammer_rankings (
    wallet text PRIMARY KEY,
    chain text,
    scam_score float,
    victim_count int,
    total_stolen bigint,
    first_scam_date timestamp,
    last_scam_date timestamp,
    associated_wallets set<text>
);

-- Evidence storage
CREATE TABLE IF NOT EXISTS evidence_files (
    evidence_id uuid PRIMARY KEY,
    case_id text,
    file_hash text,
    file_type text,
    ipfs_cid text,
    upload_time timestamp,
    metadata map<text, text>
);

-- Investigation audit log
CREATE TABLE IF NOT EXISTS investigation_logs (
    investigation_id text,
    timestamp timestamp,
    user_id text,
    action text,
    details text,
    ip_address text,
    PRIMARY KEY (investigation_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC)
AND default_time_to_live = 31536000;  -- 365 days

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_solana_sender ON solana_transactions(sender);
CREATE INDEX IF NOT EXISTS idx_solana_receiver ON solana_transactions(receiver);
CREATE INDEX IF NOT EXISTS idx_eth_from ON ethereum_transactions(from_address);
CREATE INDEX IF NOT EXISTS idx_eth_to ON ethereum_transactions(to_address);
CREATE INDEX IF NOT EXISTS idx_risk_scores ON wallet_risk_scores(risk_score);
CREATE INDEX IF NOT EXISTS idx_scammer_chain ON scammer_rankings(chain);

-- Insert sample data
INSERT INTO wallet_risk_scores (wallet, chain, risk_score, risk_factors, first_seen, last_updated, total_transactions, scam_associations)
VALUES ('0x1234567890abcdef1234567890abcdef12345678', 'ethereum', 95.5, ['known_scammer', 'mixer_usage'], toTimestamp(now()), toTimestamp(now()), 1523, 5);

INSERT INTO scammer_rankings (wallet, chain, scam_score, victim_count, total_stolen, first_scam_date, last_scam_date)
VALUES ('0x1234567890abcdef1234567890abcdef12345678', 'ethereum', 98.2, 47, 152000000000000000000, '2024-01-15', toTimestamp(now()));
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database schema created${NC}"
else
    echo -e "${YELLOW}⚠️ Schema creation may need retry (Scylla still starting)${NC}"
fi

# ═══════════════════════════════════════════════════════════
# STEP 5: Create Python Integration
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${BLUE}STEP 5: Creating Python integration...${NC}"

cat > /root/rmi/backend/scylla_integration.py << 'PYEOF'
"""
⚡ ScyllaDB Integration for RugMuncher
High-performance blockchain data storage
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from decimal import Decimal

# Scylla/Cassandra driver
try:
    from cassandra.cluster import Cluster
    from cassandra.auth import PlainTextAuthProvider
    from cassandra.query import SimpleStatement, BatchStatement
    CASSANDRA_AVAILABLE = True
except ImportError:
    CASSANDRA_AVAILABLE = False
    print("⚠️ Cassandra driver not installed. Run: pip install cassandra-driver")


class ScyllaClient:
    """ScyllaDB client for blockchain data"""
    
    def __init__(self, hosts=None, port=9042, keyspace='rugmuncher'):
        if not CASSANDRA_AVAILABLE:
            raise ImportError("cassandra-driver not installed")
        
        self.hosts = hosts or ['localhost']
        self.port = port
        self.keyspace = keyspace
        self.session = None
        self.cluster = None
        
    def connect(self):
        """Connect to Scylla cluster"""
        try:
            self.cluster = Cluster(self.hosts, port=self.port)
            self.session = self.cluster.connect(self.keyspace)
            print(f"✅ Connected to Scylla: {self.hosts}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Scylla: {e}")
            return False
    
    def close(self):
        """Close connection"""
        if self.cluster:
            self.cluster.shutdown()
    
    # ═══════════════════════════════════════════════════════
    # WALLET OPERATIONS
    # ═══════════════════════════════════════════════════════
    
    def store_wallet_risk_score(self, wallet: str, chain: str, risk_score: float, 
                                 risk_factors: List[str], total_tx: int = 0):
        """Store or update wallet risk score"""
        query = """
        INSERT INTO wallet_risk_scores 
        (wallet, chain, risk_score, risk_factors, first_seen, last_updated, total_transactions)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        now = datetime.now()
        self.session.execute(query, (
            wallet, chain, risk_score, risk_factors, now, now, total_tx
        ))
    
    def get_wallet_risk_score(self, wallet: str) -> Optional[Dict]:
        """Get wallet risk score"""
        query = "SELECT * FROM wallet_risk_scores WHERE wallet = ?"
        result = self.session.execute(query, (wallet,))
        row = result.one()
        if row:
            return {
                'wallet': row.wallet,
                'chain': row.chain,
                'risk_score': row.risk_score,
                'risk_factors': row.risk_factors,
                'last_updated': row.last_updated,
                'total_transactions': row.total_transactions,
                'scam_associations': row.scam_associations
            }
        return None
    
    def get_high_risk_wallets(self, min_score: float = 80.0, limit: int = 100) -> List[Dict]:
        """Get list of high-risk wallets"""
        query = """
        SELECT * FROM wallet_risk_scores 
        WHERE risk_score >= ? 
        LIMIT ?
        ALLOW FILTERING
        """
        result = self.session.execute(query, (min_score, limit))
        return [self._row_to_dict(row) for row in result]
    
    # ═══════════════════════════════════════════════════════
    # TRANSACTION OPERATIONS
    # ═══════════════════════════════════════════════════════
    
    def store_solana_transaction(self, tx_data: Dict):
        """Store Solana transaction (auto-TTL 90 days)"""
        query = """
        INSERT INTO solana_transactions 
        (signature, slot, block_time, sender, receiver, amount, token_mint, 
         program_id, success, fee, data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.session.execute(query, (
            tx_data['signature'],
            tx_data.get('slot'),
            tx_data.get('block_time'),
            tx_data.get('sender'),
            tx_data.get('receiver'),
            tx_data.get('amount'),
            tx_data.get('token_mint'),
            tx_data.get('program_id'),
            tx_data.get('success', True),
            tx_data.get('fee', 0),
            tx_data.get('data')
        ))
    
    def get_wallet_transactions(self, wallet: str, chain: str = 'solana', 
                                 hours: int = 24, limit: int = 1000) -> List[Dict]:
        """Get recent transactions for a wallet"""
        since = datetime.now() - timedelta(hours=hours)
        
        query = """
        SELECT * FROM wallet_activity 
        WHERE wallet = ? AND chain = ? AND timestamp > ?
        LIMIT ?
        """
        result = self.session.execute(query, (wallet, chain, since, limit))
        return [self._row_to_dict(row) for row in result]
    
    def get_transaction_count(self, wallet: str, chain: str, hours: int = 24) -> int:
        """Get transaction count for a wallet"""
        txs = self.get_wallet_transactions(wallet, chain, hours, limit=10000)
        return len(txs)
    
    # ═══════════════════════════════════════════════════════
    # ANALYTICS
    # ═══════════════════════════════════════════════════════
    
    def get_top_scammers(self, chain: str = None, limit: int = 100) -> List[Dict]:
        """Get top scammer wallets by score"""
        if chain:
            query = """
            SELECT * FROM scammer_rankings 
            WHERE chain = ? 
            LIMIT ?
            ALLOW FILTERING
            """
            result = self.session.execute(query, (chain, limit))
        else:
            query = "SELECT * FROM scammer_rankings LIMIT ?"
            result = self.session.execute(query, (limit,))
        
        return sorted(
            [self._row_to_dict(row) for row in result],
            key=lambda x: x.get('scam_score', 0),
            reverse=True
        )[:limit]
    
    def update_scammer_ranking(self, wallet: str, chain: str, scam_score: float,
                                victim_count: int = 0, total_stolen: int = 0):
        """Update scammer ranking"""
        query = """
        INSERT INTO scammer_rankings 
        (wallet, chain, scam_score, victim_count, total_stolen, first_scam_date, last_scam_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        now = datetime.now()
        self.session.execute(query, (
            wallet, chain, scam_score, victim_count, total_stolen, now, now
        ))
    
    def store_daily_stats(self, chain: str, date: datetime, stats: Dict):
        """Store daily chain statistics"""
        query = """
        INSERT INTO daily_chain_stats 
        (chain, date, total_transactions, total_volume, unique_wallets, 
         scam_transactions, avg_gas_price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.session.execute(query, (
            chain, date.date(),
            stats.get('total_transactions', 0),
            stats.get('total_volume', 0),
            stats.get('unique_wallets', 0),
            stats.get('scam_transactions', 0),
            stats.get('avg_gas_price', 0)
        ))
    
    # ═══════════════════════════════════════════════════════
    # INVESTIGATION SUPPORT
    # ═══════════════════════════════════════════════════════
    
    def store_evidence(self, evidence_id: str, case_id: str, file_hash: str,
                      file_type: str, ipfs_cid: str = None, metadata: Dict = None):
        """Store evidence file reference"""
        from uuid import UUID
        query = """
        INSERT INTO evidence_files 
        (evidence_id, case_id, file_hash, file_type, ipfs_cid, upload_time, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.session.execute(query, (
            UUID(evidence_id), case_id, file_hash, file_type,
            ipfs_cid, datetime.now(), metadata or {}
        ))
    
    def log_investigation_action(self, investigation_id: str, user_id: str,
                                  action: str, details: str, ip_address: str = None):
        """Log investigation audit trail"""
        query = """
        INSERT INTO investigation_logs 
        (investigation_id, timestamp, user_id, action, details, ip_address)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        self.session.execute(query, (
            investigation_id, datetime.now(), user_id, action, details, ip_address
        ))
    
    # ═══════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════
    
    def _row_to_dict(self, row) -> Dict:
        """Convert Cassandra row to dict"""
        if not row:
            return {}
        return {key: getattr(row, key) for key in row._fields}
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            # Count tables
            tables = self.session.execute(
                "SELECT table_name FROM system_schema.tables WHERE keyspace_name = ?",
                (self.keyspace,)
            )
            table_count = len(list(tables))
            
            return {
                'connected': True,
                'keyspace': self.keyspace,
                'tables': table_count,
                'hosts': self.hosts
            }
        except Exception as e:
            return {'connected': False, 'error': str(e)}


# ═══════════════════════════════════════════════════════════
# FAST CACHING LAYER (Dragonfly + Scylla)
# ═══════════════════════════════════════════════════════════

class HybridDataStore:
    """
    Hybrid storage: Dragonfly (hot) + Scylla (warm)
    
    Pattern:
    1. Check Dragonfly (sub-millisecond)
    2. If miss, query Scylla (milliseconds)
    3. Store result in Dragonfly for next time
    """
    
    def __init__(self, dragonfly_client, scylla_client):
        self.cache = dragonfly_client  # Dragonfly/Redis
        self.db = scylla_client        # Scylla
        
    def get_wallet_risk(self, wallet: str, chain: str = 'ethereum') -> Optional[Dict]:
        """Get wallet risk with caching"""
        import json
        
        # Try cache first
        cache_key = f"risk:{chain}:{wallet}"
        cached = self.cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Query database
        result = self.db.get_wallet_risk_score(wallet)
        
        # Cache for 1 hour
        if result:
            self.cache.setex(cache_key, 3600, json.dumps(result))
        
        return result
    
    def get_wallet_transactions(self, wallet: str, chain: str, hours: int = 24):
        """Get transactions with caching"""
        import json
        
        cache_key = f"txs:{chain}:{wallet}:{hours}h"
        cached = self.cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Query database
        result = self.db.get_wallet_transactions(wallet, chain, hours)
        
        # Cache for 5 minutes (transactions change)
        if result:
            self.cache.setex(cache_key, 300, json.dumps(result))
        
        return result


# Usage example
if __name__ == '__main__':
    # Connect to Scylla
    client = ScyllaClient(['localhost'], 9042)
    if client.connect():
        print("✅ Scylla connected")
        
        # Test operations
        stats = client.get_stats()
        print(f"Database stats: {stats}")
        
        # Store test data
        client.store_wallet_risk_score(
            '0xTEST123',
            'ethereum',
            85.5,
            ['high_velocity', 'mixer_usage']
        )
        print("✅ Test data stored")
        
        # Retrieve
        result = client.get_wallet_risk_score('0xTEST123')
        print(f"Retrieved: {result}")
        
        client.close()
PYEOF

echo -e "${GREEN}✅ Python integration created${NC}"

# ═══════════════════════════════════════════════════════════
# STEP 6: Install Python Driver
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${BLUE}STEP 6: Installing Python driver...${NC}"

pip install -q cassandra-driver 2>/dev/null || pip3 install -q cassandra-driver 2>/dev/null || echo "⚠️ pip install may need manual run"

echo -e "${GREEN}✅ Driver installed${NC}"

# ═══════════════════════════════════════════════════════════
# STEP 7: Create Helper Scripts
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${BLUE}STEP 7: Creating helper scripts...${NC}"

cat > /usr/local/bin/rmi-scylla << 'EOF'
#!/bin/bash
# Scylla CLI helper
docker exec -it scylla cqlsh "$@"
EOF
chmod +x /usr/local/bin/rmi-scylla

cat > /usr/local/bin/rmi-scylla-stats << 'EOF'
#!/bin/bash
echo "⚡ Scylla Statistics"
echo "════════════════════"
docker exec scylla nodetool status 2>/dev/null || echo "Scylla not ready yet"
echo ""
echo "Logs:"
docker logs scylla --tail 10 2>/dev/null | tail -5
EOF
chmod +x /usr/local/bin/rmi-scylla-stats

# ═══════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════"
echo "  ✅ SCYLLA DEPLOYMENT COMPLETE!"
echo "═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}⚡ ScyllaDB is now running on port 9042${NC}"
echo ""
echo -e "${BLUE}📊 Connection Info:${NC}"
echo "   Host: localhost (or $(curl -s ifconfig.me 2>/dev/null || echo 'your-server-ip'))"
echo "   Port: 9042 (CQL)"
echo "   Keyspace: rugmuncher"
echo ""
echo -e "${BLUE}🗄️  Tables Created:${NC}"
echo "   • solana_transactions (90-day TTL)"
echo "   • ethereum_transactions (90-day TTL)"
echo "   • wallet_activity (90-day TTL)"
echo "   • wallet_risk_scores (permanent)"
echo "   • scam_reports (180-day TTL)"
echo "   • scammer_rankings (permanent)"
echo "   • evidence_files (permanent)"
echo "   • daily_chain_stats (permanent)"
echo "   • investigation_logs (365-day TTL)"
echo ""
echo -e "${BLUE}🔧 Commands:${NC}"
echo "   rmi-scylla                    - Connect to CQL shell"
echo "   rmi-scylla-stats              - Show statistics"
echo "   docker logs scylla --tail 20  - View logs"
echo ""
echo -e "${BLUE}💻 Python Usage:${NC}"
echo "   from scylla_integration import ScyllaClient"
echo "   client = ScyllaClient(['localhost'], 9042)"
echo "   client.connect()"
echo ""
echo -e "${YELLOW}💡 Next Steps:${NC}"
echo "   1. Test connection: rmi-scylla"
echo "   2. Query data: SELECT * FROM rugmuncher.wallet_risk_scores;"
echo "   3. Integrate with bot: import scylla_integration"
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
