# Munch Maps V2 Design Specification
## Guided by "Advanced Architectures for Visualizing Cryptographic Threat Actor Networks"

**Document Version:** 1.0  
**Date:** 2026-04-13  
**Source Research:** Advanced Architectures for Visualizing Cryptographic Threat Actor Networks

---

## EXECUTIVE SUMMARY

The research paper identifies critical architectural limitations in current blockchain visualization tools (Bubblemaps, Arkham, Nansen) and proposes a 100x improvement framework. This document translates those academic specifications into concrete Munch Maps V2 design requirements.

**Current Market Limitation:** Tools truncate at 150-200 wallets, hiding Sybil networks  
**Munch Maps V2 Target:** 1,000,000+ nodes at 60 FPS with multi-dimensional forensic context

---

## 1. CORE DESIGN PRINCIPLES (From Research)

### 1.1 The 100x Improvement Framework

| Aspect | Current Tools (Bubblemaps/Nansen) | Munch Maps V2 Target |
|--------|-----------------------------------|---------------------|
| **Node Capacity** | 150-200 (truncated) | 1,000,000+ |
| **Rendering** | SVG/HTML5 Canvas | WebGL/WebGPU |
| **Layout Engine** | CPU-bound (D3.js) | GPU-accelerated (Cosmos.gl) |
| **Chain Support** | Single-chain isolation | Cross-chain unified graph |
| **Data Depth** | On-chain only | OSINT + Network-layer + Temporal |
| **Frame Rate** | 15-30 FPS (degrades) | 60 FPS (stable) |

### 1.2 The "Sybil Blind Spot" Problem

**Current Tool Failure:**
- Scammers create 10,000+ micro-wallets via seed phrase derivation
- Each holds fractional amounts (below top-150 threshold)
- Coordinated dumps happen OFF the visible map
- Result: "Clean" bubble map while massive botnet drains liquidity

**Munch Maps Solution:**
- Render ALL wallets (not just top holders)
- Cluster micro-wallets into entity groups
- Visual bounding boxes around Sybil networks
- Real-time coordination detection

---

## 2. DATA ONTOLOGY & SCHEMA DESIGN

### 2.1 Unified Vertex (Node) Schema

```typescript
interface WalletVertex {
  id: string;                    // Address
  type: 'EOA' | 'CONTRACT';
  chain: 'ETH' | 'BSC' | 'SOL' | 'BASE' | 'ARB' | etc.;
  
  // On-chain Metrics
  balance: Record<string, number>; // Token balances
  riskScore: number;             // 0-100 calculated
  clusterId: string | null;      // Entity clustering
  
  // Temporal Data
  firstSeen: number;             // Unix timestamp
  lastActive: number;
  transactionCount: number;
  
  // Network Layer (RPC Deanonymization)
  ipMetadata?: {
    ipHash: string;              // Hashed IP
    geoLocation: [lat, lng];
    asn: string;
    rpcEndpoint: string;
    tcpTimestamp: number;
  };
  
  // OSINT Linkage
  identities?: {
    telegram?: string;
    twitter?: string;
    emailHash?: string;
    datingProfiles?: string[];
    waasProvider?: 'privy' | 'alchemy' | 'circle';
    kycStatus?: 'verified' | 'suspicious' | 'unknown';
  };
  
  // Behavioral Fingerprints
  gasProfile: {
    avgMaxFee: number;
    avgPriorityFee: number;
    feeVariance: number;         // Consistency = bot indicator
    last9Digits: number;         // Manual config fingerprint
  };
  noncePattern: 'sequential' | 'batched' | 'irregular';
}

interface ContractVertex {
  id: string;                    // Contract address
  chain: string;
  creator: string;               // Deployer wallet
  creationTimestamp: number;
  bytecodeHash: string;
  
  // Risk Analysis
  opcodeVector: number[];        // NLP-embedded opcodes
  isProxy: boolean;
  honeypotScore: number;         // ML classification
  ponziProbability: number;      // XGBoost prediction
  
  // Interaction Metrics
  txIn: number;
  txOut: number;
  uniqueInteractors: number;
  
  // Labels
  labels: string[];              // 'dex', 'mixer', 'token', etc.
}

interface IdentityVertex {
  id: string;                    // Social handle or email hash
  type: 'TELEGRAM' | 'TWITTER' | 'EMAIL' | 'DATING';
  
  // Reputation
  trustScore: number;
  scamReports: number;
  verifiedSince?: number;
  
  // Web2 Metadata
  accountAge: number;            // Days since creation
  followerCount: number;
  profileImages: string[];       // For face recognition matching
}
```

### 2.2 Unified Edge (Relationship) Schema

```typescript
interface TransferEdge {
  id: string;
  from: string;                  // Source wallet
  to: string;                    // Dest wallet
  
  // Transaction Data
  txHash: string;
  value: number;
  assetId: string;              // Token address or native
  timestamp: number;
  
  // Gas Fingerprinting
  maxFeePerGas: string;
  maxPriorityFeePerGas: string;
  gasUsed: number;
  
  // Temporal Proximity (for IP correlation)
  rpcQueryTime?: number;         // When seen in mempool
  blockTime: number;
  tcpPacketTimestamp?: number;   // Network layer
}

interface CrossChainEdge {
  id: string;
  from: string;                  // Source wallet (Chain A)
  to: string;                    // Dest wallet (Chain B)
  
  // Bridge Data
  sourceChain: string;
  destChain: string;
  bridgeProtocol: 'thorchain' | 'synapse' | 'celer' | 'custom';
  
  // Matching Confidence
  explicitMatch: boolean;        // Direct bridge log
  implicitMatchScore: number;      // 0-1 via temporal/value analysis
  slippageDelta: number;
  timeWindow: number;            // Seconds between deposit/withdrawal
  
  // ABCTracer Methodology
  depositTx: string;
  withdrawalTx: string;
  valueEquivalence: number;      // After slippage adjustment
}

interface ControlEdge {
  from: string;                  // Identity (Telegram/Twitter)
  to: string;                    // Wallet
  
  confidenceScore: number;       // 0-1 certainty
  evidence: string[];            // Links, screenshots
  sourceApi: string;             // OSINT provider
  authProvider?: string;         // WaaS provider if applicable
}

interface NetworkEdge {
  from: string;                  // IP/Network node
  to: string;                    // Transaction
  
  rpcEndpoint: string;
  tcpTimestamp: number;
  latencyMs: number;
  userAgent?: string;
}
```

### 2.3 Graph Database Schema (TigerGraph GSQL)

```sql
// Vertex Types
CREATE VERTEX Wallet (PRIMARY_ID address STRING, chain STRING, 
                      risk_score FLOAT, cluster_id STRING)
CREATE VERTEX Contract (PRIMARY_ID address STRING, chain STRING,
                        bytecode_hash STRING, creator STRING)
CREATE VERTEX Identity (PRIMARY_ID handle STRING, type STRING,
                        trust_score FLOAT)
CREATE VERTEX NetworkNode (PRIMARY_ID ip_hash STRING, 
                           geo_location STRING, asn STRING)

// Edge Types
CREATE DIRECTED EDGE TRANSFERRED_TO (FROM Wallet, TO Wallet, 
    amount FLOAT, asset_id STRING, timestamp UINT, tx_hash STRING,
    max_fee STRING, priority_fee STRING)

CREATE DIRECTED EDGE BRIDGED_ASSET (FROM Wallet, TO Wallet,
    source_chain STRING, dest_chain STRING, bridge_protocol STRING,
    match_score FLOAT, slippage FLOAT)

CREATE DIRECTED EDGE CONTROLS (FROM Identity, TO Wallet,
    confidence FLOAT, source_api STRING)

CREATE DIRECTED EDGE BROADCASTED (FROM NetworkNode, TO Wallet,
    rpc_endpoint STRING, tcp_timestamp UINT, latency_ms UINT)

CREATE UNDIRECTED EDGE CLUSTERED_WITH (FROM Wallet, TO Wallet,
    heuristic_type STRING, confidence FLOAT)
```

---

## 3. VISUALIZATION LAYER ARCHITECTURE

### 3.1 Rendering Stack

```
┌─────────────────────────────────────────────┐
│          REACT UI LAYER                     │
│  - Controls, panels, overlays                │
│  - State management (Zustand/Redux)         │
└──────────────────┬──────────────────────────┘
                   │ Apache Arrow (zero-copy)
                   ▼
┌─────────────────────────────────────────────┐
│        CLIENT-SIDE PROCESSING               │
│  DuckDB Wasm - SQL filtering                │
│  - "Show only >$10k transfers"              │
│  - "Filter cross-chain only"               │
│  - Instant response, no server round-trip   │
└──────────────────┬──────────────────────────┘
                   │ WebGL buffers
                   ▼
┌─────────────────────────────────────────────┐
│     GPU-ACCELERATED LAYOUT ENGINE         │
│  Cosmos.gl / force-graph                    │
│  - Many-Body repulsion (GPU)                │
│  - Spring forces                              │
│  - 1M+ nodes @ 60 FPS                        │
└──────────────────┬──────────────────────────┘
                   │ WebGL draw calls
                   ▼
┌─────────────────────────────────────────────┐
│      WEBGL RENDERER (Deck.gl/Cosmograph)    │
│  - Instanced rendering (1 draw call/100k)     │
│  - GPU picking (hover/click detection)        │
│  - Temporal animation shaders                 │
└─────────────────────────────────────────────┘
```

### 3.2 Visual Encoding System

#### Node (Bubble) Encodings

| Attribute | Visual Channel | Purpose |
|-----------|---------------|---------|
| **Risk Score** | Color (Green→Red gradient) | Immediate threat assessment |
| **Entity Cluster** | Shape + Halo | Group Sybil networks visually |
| **Balance** | Size (area) | Capital concentration |
| **Chain** | Border pattern | Cross-chain identification |
| **Age** | Opacity | New vs established wallets |
| **Activity** | Pulse animation | Recent transaction heat |

#### Edge Encodings

| Attribute | Visual Channel | Purpose |
|-----------|---------------|---------|
| **Value** | Thickness | Capital flow magnitude |
| **Time** | Opacity fade | Temporal decay (older = fainter) |
| **Cross-chain** | Dashed + gradient | Bridge transactions |
| **Risk** | Red pulse | Suspicious path highlighting |
| **Volume** | Animation speed | Transaction frequency |

### 3.3 Multi-Layer Visualization Modes

#### Mode 1: Macro View (Galactic)
- Zoom: 100% token ecosystem
- Nodes: 100,000-1,000,000
- Cluster bounding boxes visible
- Animated time-slider shows token lifecycle
- Use case: "Where are the Sybil armies?"

#### Mode 2: Entity View (Cluster)
- Zoom: Single cluster focus
- Nodes: 50-500 related wallets
- Network topology clear
- Control relationships visible
- Use case: "Who controls this cluster?"

#### Mode 3: Transaction View (Micro)
- Zoom: Individual wallet
- Nodes: Direct neighbors
- Full transaction history
- Temporal sequence animation
- Use case: "Trace this specific flow"

#### Mode 4: Cross-Chain View
- Multi-chain parallel display
- Bridge connections highlighted
- Time-synchronized across chains
- Use case: "Follow the chain-hop"

---

## 4. HEURISTIC ENGINE (Backend)

### 4.1 Clustering Algorithms

#### 4.1.1 Gas-Funding Tree Detection
```python
class GasFundingHeuristic:
    """
    Identify Sybil networks by tracing gas token dispersal.
    Single parent → many children with identical amounts = cluster
    """
    def detect_clusters(self, parent_wallet: str) -> List[Cluster]:
        # Find all wallets funded by parent within time window
        children = self.trace_outflows(
            from_wallet=parent_wallet,
            value_range=(0.049, 0.051),  # ~0.05 ETH with tolerance
            time_window_hours=24
        )
        
        # Filter: Must have similar gas fee patterns
        fingerprint_match = self.compare_gas_fingerprints(children)
        
        return Cluster(
            wallets=children,
            confidence=len(children) * 0.01,  # More wallets = higher confidence
            type='GAS_FUNDED_SYBIL'
        )
```

#### 4.1.2 Co-Spending (UTXO) Heuristic
```python
class CoSpendingHeuristic:
    """
    UTXO chains: Multiple inputs = same owner
    Account chains: Trace to common funding source
    """
    def apply(self, transaction: Tx) -> List[ClusterUpdate]:
        if self.is_utxo_chain(transaction.chain):
            # All input addresses belong to same entity
            return self.cluster_addresses(transaction.inputs)
        else:
            # Account model: Check for shared gas funding
            return self.trace_gas_trees(transaction)
```

#### 4.1.3 Change Address Heuristic
```python
class ChangeAddressHeuristic:
    """
    Identify change outputs by:
    - First-time appearance on chain
    - Self-change (output address in inputs)
    - Round numbers (payment) vs odd (change)
    """
    def identify_change(self, tx: Tx) -> Optional[str]:
        for output in tx.outputs:
            if self.is_first_appearance(output.address):
                return output.address
            if output.address in tx.input_addresses:
                return output.address
        return None
```

### 4.2 Smart Contract Classification

```python
class ContractClassifier:
    """
    XGBoost/LGBM classifier using:
    - Opcode frequency vector
    - Lifetime metrics
    - Tx in/out ratios
    - Hidden delegate calls
    """
    features = [
        'lifetime_seconds',
        'tx_in_count', 'tx_out_count',
        'balance_delta',
        'suicide_opcode_count',
        'delegatecall_count',
        'transfer_restriction_score'
    ]
    
    def classify(self, contract: Contract) -> RiskScore:
        opcode_vector = self.vectorize_opcodes(contract.bytecode)
        feature_vector = self.extract_features(contract)
        
        # XGBoost prediction
        ponzi_prob = self.xgb_model.predict(feature_vector)
        honeypot_prob = self.lgbm_model.predict(opcode_vector)
        
        return RiskScore(
            ponzi=ponzi_prob,
            honeypot=honeypot_prob,
            overall=max(ponzi_prob, honeypot_prob)
        )
```

### 4.3 Edge-Temporal Graph Neural Network

```python
class EdgeTemporalGNN:
    """
    Spatiotemporal edge encoding for fraud detection.
    Distinguishes programmatic dumps from organic trading.
    """
    def encode_edge(self, edge: TransferEdge) -> Embedding:
        # Temporal features
        time_encoding = self.temporal_encode(edge.timestamp)
        frequency_encoding = self.frequency_decompose(edge)
        
        # Spatiotemporal synthesis
        edge_embedding = self.gnn_layer(
            neighbor_embeddings=edge.neighbors,
            temporal_features=time_encoding,
            edge_attributes=edge.value,
            proximity_weight=self.temporal_proximity(edge)
        )
        
        return edge_embedding
```

---

## 5. DATA PIPELINE ARCHITECTURE

### 5.1 Real-Time Ingestion

```
┌──────────────────────────────────────────────────────┐
│           BLOCKCHAIN NODES (Erigon/Geth)            │
│  - Archive nodes for full history                    │
│  - Mempool monitoring for pre-confirmation           │
│  - debug_traceTransaction for internal calls         │
└──────────────────────┬───────────────────────────────┘
                       │ Kafka Streams
                       ▼
┌──────────────────────────────────────────────────────┐
│         APACHE FLINK (Real-time Processing)         │
│  - Gas fingerprinting                                  │
│  - Co-spending detection                               │
│  - Mempool anomaly detection                           │
│  Latency: <2 seconds from block to Kafka              │
└──────────────────────┬───────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│        TIGERGRAPH (Graph Database)                   │
│  - Native parallel processing                         │
│  - 10+ hop traversals in milliseconds                │
│  - 2x-10x compression ratio                          │
└──────────────────────┬───────────────────────────────┘
                       │ GraphQL API
                       ▼
┌──────────────────────────────────────────────────────┐
│         REACT + WEBGL FRONTEND                       │
│  - Apache Arrow zero-copy transfer                   │
│  - DuckDB Wasm client-side filtering                 │
│  - Cosmos.gl GPU layout                              │
└──────────────────────────────────────────────────────┘
```

### 5.2 Batch Processing (Nightly)

```
┌──────────────────────────────────────────────────────┐
│        APACHE SPARK (Heavy Computation)             │
│  - ABCTracer cross-chain analysis                    │
│  - GNN training and inference                        │
│  - XGBoost model updates                             │
│  - Entity resolution across chains                   │
└──────────────────────┬───────────────────────────────┘
                       │ Update TigerGraph
                       ▼
┌──────────────────────────────────────────────────────┐
│        MODEL SERVING                                 │
│  - SynapTrack scoring API                            │
│  - Real-time risk evaluation                         │
│  - 98% accuracy on cross-chain tracing               │
└──────────────────────────────────────────────────────┘
```

---

## 6. UI/UX DESIGN SPECIFICATIONS

### 6.1 Main Interface Layout

```
┌─────────────────────────────────────────────────────────────┐
│  NAVBAR                                                     │
│  [Logo] [Search: 0x...] [Risk Alert: 3] [Profile] [Settings] │
├──────────┬──────────────────────────────────────┬───────────┤
│          │                                      │           │
│ SIDEBAR  │         MAIN CANVAS                  │ INSPECTOR │
│          │         (WebGL Viewport)             │ PANEL     │
│ Layers:  │                                      │           │
│ ☑ Wallets│    ┌─────┐     ┌──────────────┐    │ Selected: │
│ ☑ Clusters    │     │     │              │    │ 0x123...  │
│ ☑ Bridges│    │  ●──┼─────┼──▶ ●         │    │           │
│ ☑ Identities  │     │     │              │    │ Risk: 85  │
│          │    └─────┘     └──────────────┘    │ Chain: ETH│
│ Filters: │                                      │           │
│ Value >  │   [Zoom] [Pan] [Time Slider]         │ [Analyze] │
│ $10k     │                                      │ [Export]  │
│          │   Time: ▓▓▓▓░░░░░░░░░░░░  Jan-Mar   │           │
│ Time:    │   [Play] [Speed: 2x]                 │ Related:  │
│ 24h      │                                      │ 3 clusters│
│ 7d       │                                      │           │
│ 30d      │                                      │           │
│ Custom   │                                      │           │
│          │                                      │           │
├──────────┴──────────────────────────────────────┴───────────┤
│  STATUS BAR                                                  │
│  Nodes: 1,247,832 | Edges: 4,582,109 | FPS: 60 | Latency: 23ms│
└──────────────────────────────────────────────────────────────┘
```

### 6.2 Color System (Dark Theme)

```css
:root {
  /* Background Layers */
  --bg-universe: #050508;        /* Deep space black */
  --bg-void: #0a0a0f;            /* Main canvas */
  --bg-panel: #12121a;           /* UI panels */
  
  /* Risk Gradient (Node Colors) */
  --risk-none: #00ff9d;          /* Safe: Neon green */
  --risk-low: #88ff00;           /* Low: Lime */
  --risk-medium: #ffcc00;        /* Medium: Yellow */
  --risk-high: #ff6600;          /* High: Orange */
  --risk-critical: #ff0044;     /* Critical: Red */
  
  /* Chain Identification (Borders) */
  --chain-eth: #627eea;         /* Ethereum blue */
  --chain-bsc: #f3ba2f;         /* BSC yellow */
  --chain-sol: #9945ff;         /* Solana purple */
  --chain-base: #0052ff;        /* Base blue */
  
  /* Activity States */
  --pulse-active: rgba(0, 255, 157, 0.6);
  --pulse-suspicious: rgba(255, 0, 68, 0.6);
  
  /* Cluster Bounding */
  --cluster-halo: rgba(0, 212, 255, 0.3);
}
```

### 6.3 Interaction Patterns

#### Hover State
- Node expands 20%
- Ring appears showing: Address (truncated), Balance, Risk Score
- Incoming/outgoing edge highlight
- Tooltip with quick actions (View, Flag, Add to Case)

#### Click State
- Node locks to center
- Inspector panel slides in
- Neighbor nodes pulse
- Path tracing initiates (showing flows)

#### Drag (Time Slider)
- Graph animates through time
- Edges appear/disappear based on timestamp
- Accumulated risk scores update
- Play/Pause controls for replay

#### Zoom Levels
- **0.1x-0.5x:** Galaxy view (all clusters, no individual nodes)
- **0.5x-2x:** Cluster view (entity groups visible)
- **2x-5x:** Wallet view (individual addresses)
- **5x-10x:** Transaction view (specific flows)

---

## 7. IMPLEMENTATION PHASES

### Phase 1: Data Infrastructure (Weeks 1-4)
1. Deploy Erigon archive nodes (ETH, BSC, BASE)
2. Set up Kafka ingestion pipeline
3. Deploy TigerGraph cluster
4. Implement base vertex/edge schema
5. Historical data backfill (6 months)

### Phase 2: Heuristic Engine (Weeks 5-8)
1. Implement gas-funding tree detection
2. Build co-spending heuristics
3. Deploy XGBoost contract classifier
4. Train GNN on historical scam data
5. Build ABCTracer cross-chain module

### Phase 3: Visualization Core (Weeks 9-12)
1. Implement Cosmos.gl integration
2. Build Apache Arrow data pipeline
3. Integrate DuckDB Wasm
4. Create WebGL instanced renderer
5. Implement multi-layer view modes

### Phase 4: OSINT Integration (Weeks 13-16)
1. Telegram/Twitter scrapers
2. WaaS provider APIs (Privy, Alchemy)
3. RPC deanonymization capture
4. Dating site search integration
5. IP geolocation enrichment

### Phase 5: UI/UX Polish (Weeks 17-20)
1. Design system implementation
2. Animation and transition polish
3. Mobile responsiveness
4. Performance optimization
5. User testing and iteration

---

## 8. PERFORMANCE TARGETS

| Metric | Target | Current Tools |
|--------|--------|---------------|
| Max Nodes Rendered | 1,000,000 | ~200 |
| Frame Rate (stable) | 60 FPS | ~15-30 FPS |
| Initial Load Time | <3 seconds | ~10 seconds |
| Query Latency (10 hops) | <500ms | N/A (fails) |
| Cross-chain Trace | <2 seconds | Not supported |
| Cluster Detection | Real-time | Batch only |

---

## 9. COMPETITIVE DIFFERENTIATION

### vs. Bubblemaps
- **They show:** Top 150 wallets
- **We show:** Complete ecosystem (1M+ nodes)
- **They miss:** Sybil networks, micro-wallets
- **We detect:** All coordination patterns

### vs. Arkham
- **They track:** Labelled entities only
- **We track:** All addresses + inferred entities
- **They miss:** Cross-chain flows
- **We visualize:** Unified multi-chain graph

### vs. Nansen
- **They analyze:** Smart money labels
- **We analyze:** Complete forensic topology
- **They miss:** OSINT linkages
- **We integrate:** Social, network, temporal data

---

## 10. RISK & MITIGATION

| Risk | Mitigation |
|------|-----------|
| **Performance at scale** | GPU acceleration, aggressive LOD |
| **False positive clustering** | Confidence scores, manual review queue |
| **IP deanonymization ethics** | Hashing, court-order access only |
| **Data storage costs** | TigerGraph compression, tiered storage |
| **Real-time ingestion lag** | Kafka partitioning, horizontal scaling |

---

## APPENDIX: Research Citations

1. **"Track and Trace: Automatically Uncovering Cross-chain Transactions"** - ABCTracer methodology (91.75% F1 score)
2. **"Ghost Clusters: Evaluating Attribution of Illicit Services"** - USENIX Security
3. **"Gas fees on the Ethereum blockchain"** - Frontiers in Blockchain
4. **"Clustering Ethereum Addresses"** - ETH Zürich
5. **"Time Tells All: Deanonymization of Blockchain RPC Users"** - arXiv (95% success rate)
6. **"Edge-Temporal Encoding for Financial Transaction Graphs"** - ResearchGate (+8.7% F1 improvement)

---

*End of Specification*
*This document translates academic research into actionable Munch Maps V2 requirements*
