/**
 * Wallet Clustering Component
 * Advanced wallet relationship analysis and cluster detection
 * ELITE+ tier feature
 */
import { useState, useMemo } from 'react';
import { useWalletClusters, useClusterAnalysis } from '../hooks/useAnalytics';
import { useAppStore } from '../store/appStore';
import {
  Network,
  Users,
  AlertTriangle,
  Brain,
  Search,
  Filter,
  Download,
  Target,
  Activity,
  Zap,
  Wallet,
  ExternalLink,
  Copy,
  Check,
  Lock,
  XCircle,
  Play,
  RefreshCw,
  Layers,
  Maximize2,
} from 'lucide-react';

// Mock cluster data for development (will be replaced with API)
const MOCK_CLUSTERS = [
  {
    id: 'cluster_001',
    name: 'Rug Pull Syndicate Alpha',
    type: 'scam_network',
    severity: 'CRITICAL',
    wallet_count: 47,
    total_volume_eth: 2847.5,
    created_at: '2024-03-15T10:00:00Z',
    updated_at: '2024-04-13T08:30:00Z',
    confidence_score: 94,
    tags: ['rug_pull', 'wash_trading', 'layered_transfers'],
    central_wallets: ['0x7a2...9f3b', '0x9c4...2d8a'],
    related_clusters: ['cluster_003', 'cluster_007'],
    status: 'active',
    description: 'Sophisticated multi-chain rug pull operation using 47 connected wallets for token manipulation and exit liquidity extraction.',
  },
  {
    id: 'cluster_002',
    name: 'Ponzi Scheme Network Beta',
    type: 'ponzi_scheme',
    severity: 'HIGH',
    wallet_count: 23,
    total_volume_eth: 892.3,
    created_at: '2024-02-28T14:20:00Z',
    updated_at: '2024-04-12T16:45:00Z',
    confidence_score: 87,
    tags: ['ponzi', 'pyramid', 'referral_fraud'],
    central_wallets: ['0x3f8...7e2c'],
    related_clusters: [],
    status: 'monitoring',
    description: 'Classic ponzi structure with early investors receiving funds from later deposits. Pyramid-style referral system.',
  },
  {
    id: 'cluster_003',
    name: 'Mixer/Laundering Ring',
    type: 'money_laundering',
    severity: 'HIGH',
    wallet_count: 156,
    total_volume_eth: 5234.8,
    created_at: '2024-01-10T09:00:00Z',
    updated_at: '2024-04-13T12:00:00Z',
    confidence_score: 91,
    tags: ['tornado_cash', 'layering', 'peel_chain'],
    central_wallets: ['0x2a9...4f7d', '0x8b1...6c3e', '0x4d2...8a9f'],
    related_clusters: ['cluster_001'],
    status: 'active',
    description: 'Complex laundering operation using Tornado Cash and peel chain techniques across 156 wallets.',
  },
  {
    id: 'cluster_004',
    name: 'Pump & Dump Coordination',
    type: 'market_manipulation',
    severity: 'MEDIUM',
    wallet_count: 12,
    total_volume_eth: 456.2,
    created_at: '2024-03-20T11:30:00Z',
    updated_at: '2024-04-10T09:15:00Z',
    confidence_score: 76,
    tags: ['pump_dump', 'wash_trading', 'social_manipulation'],
    central_wallets: ['0x1e5...9b4a'],
    related_clusters: [],
    status: 'investigating',
    description: 'Coordinated token pump and dump scheme with synchronized buying and social media manipulation.',
  },
  {
    id: 'cluster_005',
    name: 'Insider Trading Ring',
    type: 'insider_trading',
    severity: 'CRITICAL',
    wallet_count: 8,
    total_volume_eth: 1234.6,
    created_at: '2024-03-01T08:00:00Z',
    updated_at: '2024-04-13T14:20:00Z',
    confidence_score: 89,
    tags: ['insider_info', 'front_running', 'mev_extraction'],
    central_wallets: ['0x6c3...2f8e'],
    related_clusters: [],
    status: 'active',
    description: 'Small tight-knit group with advanced knowledge of major announcements and MEV extraction.',
  },
];

const CLUSTER_TYPES = [
  { id: 'all', label: 'All Types', icon: Network },
  { id: 'scam_network', label: 'Scam Networks', icon: AlertTriangle },
  { id: 'ponzi_scheme', label: 'Ponzi Schemes', icon: Users },
  { id: 'money_laundering', label: 'Money Laundering', icon: Layers },
  { id: 'market_manipulation', label: 'Market Manipulation', icon: Activity },
  { id: 'insider_trading', label: 'Insider Trading', icon: Lock },
];

const SEVERITY_COLORS = {
  CRITICAL: 'text-red-400 bg-red-500/20 border-red-500/30',
  HIGH: 'text-orange-400 bg-orange-500/20 border-orange-500/30',
  MEDIUM: 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30',
  LOW: 'text-green-400 bg-green-500/20 border-green-500/30',
};

const STATUS_COLORS = {
  active: 'text-red-400 bg-red-500/10',
  monitoring: 'text-yellow-400 bg-yellow-500/10',
  investigating: 'text-blue-400 bg-blue-500/10',
  resolved: 'text-green-400 bg-green-500/10',
};

// Mock cluster details for selected cluster
const MOCK_CLUSTER_DETAILS = {
  nodes: [
    { id: '0x7a2...9f3b', type: 'central', risk_score: 98, tx_count: 3421, volume: 892.4 },
    { id: '0x9c4...2d8a', type: 'central', risk_score: 96, tx_count: 2893, volume: 756.2 },
    { id: '0x3f1...8d5c', type: 'layer_1', risk_score: 87, tx_count: 1234, volume: 234.5 },
    { id: '0x2e8...7a3b', type: 'layer_1', risk_score: 85, tx_count: 987, volume: 198.3 },
    { id: '0x5b9...4f2e', type: 'layer_2', risk_score: 72, tx_count: 456, volume: 89.2 },
    { id: '0x1d7...6c8a', type: 'exit', risk_score: 45, tx_count: 234, volume: 45.6 },
  ],
  connections: [
    { from: '0x7a2...9f3b', to: '0x3f1...8d5c', strength: 0.8, tx_count: 156 },
    { from: '0x7a2...9f3b', to: '0x2e8...7a3b', strength: 0.7, tx_count: 134 },
    { from: '0x9c4...2d8a', to: '0x3f1...8d5c', strength: 0.6, tx_count: 98 },
    { from: '0x3f1...8d5c', to: '0x5b9...4f2e', strength: 0.5, tx_count: 67 },
    { from: '0x2e8...7a3b', to: '0x5b9...4f2e', strength: 0.4, tx_count: 45 },
    { from: '0x5b9...4f2e', to: '0x1d7...6c8a', strength: 0.3, tx_count: 23 },
  ],
  patterns: [
    { type: 'Circular Trading', confidence: 94, description: 'Funds circulate between cluster wallets before exit' },
    { type: 'Layered Transfers', confidence: 91, description: 'Multi-hop obfuscation through intermediate wallets' },
    { type: 'Wash Trading', confidence: 87, description: 'Artificial volume creation for price manipulation' },
    { type: 'Timing Coordination', confidence: 83, description: 'Synchronized transactions within 2-minute windows' },
  ],
  timeline: [
    { date: '2024-03-15', event: 'Cluster formation detected', type: 'formation' },
    { date: '2024-03-20', event: 'First token launch (RUG1)', type: 'token_launch' },
    { date: '2024-03-25', event: 'Liquidity drain #1: 450 ETH', type: 'liquidity_drain' },
    { date: '2024-04-01', event: 'Second token launch (SCAM2)', type: 'token_launch' },
    { date: '2024-04-05', event: 'Liquidity drain #2: 892 ETH', type: 'liquidity_drain' },
    { date: '2024-04-13', event: 'Active monitoring continues', type: 'monitoring' },
  ],
};

export default function WalletClustering() {
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [selectedCluster, setSelectedCluster] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [showAIFinder, setShowAIFinder] = useState(false);
  const [walletInput, setWalletInput] = useState('');
  const [copiedAddress, setCopiedAddress] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'network' | 'timeline'>('overview');

  const user = useAppStore((state) => state.user);
  const userTier = user?.tier || 'FREE';
  const hasClusterAccess = ['ELITE', 'ENTERPRISE'].includes(userTier);

  // Query hooks (using mock data for now)
  const { data: clusters, isLoading } = useWalletClusters();
  const clusterAnalysis = useClusterAnalysis();

  // Filter clusters
  const filteredClusters = useMemo(() => {
    const data = (clusters as any[]) || MOCK_CLUSTERS;
    return data.filter((cluster) => {
      const matchesSearch = 
        cluster.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        cluster.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        cluster.tags.some((t: string) => t.toLowerCase().includes(searchQuery.toLowerCase()));
      const matchesType = typeFilter === 'all' || cluster.type === typeFilter;
      const matchesSeverity = severityFilter === 'all' || cluster.severity === severityFilter;
      return matchesSearch && matchesType && matchesSeverity;
    });
  }, [clusters, searchQuery, typeFilter, severityFilter]);

  const selectedClusterData = useMemo(() => {
    if (!selectedCluster) return null;
    return MOCK_CLUSTERS.find(c => c.id === selectedCluster) || null;
  }, [selectedCluster]);

  const handleFindCluster = async () => {
    if (!walletInput.trim()) return;
    try {
      await clusterAnalysis.mutateAsync({ address: walletInput });
    } catch (e) {
      // Error handled by mutation
    }
  };

  const copyAddress = (address: string) => {
    navigator.clipboard.writeText(address);
    setCopiedAddress(address);
    setTimeout(() => setCopiedAddress(null), 2000);
  };

  // Tier restriction UI
  if (!hasClusterAccess) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Network className="w-6 h-6 text-neon-green" />
            Wallet Clustering
          </h1>
          <p className="text-gray-400 mt-1">
            Advanced wallet relationship analysis and scam network detection
          </p>
        </div>

        <div className="crypto-card p-12 text-center">
          <Lock className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-white mb-2">ELITE Feature</h2>
          <p className="text-gray-400 mb-6 max-w-md mx-auto">
            Wallet clustering and network analysis requires an ELITE or ENTERPRISE subscription. 
            Upgrade to unlock advanced scam network detection.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="btn-primary">
              Upgrade to ELITE
            </button>
            <button className="btn-secondary">
              View Pricing
            </button>
          </div>
          <div className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-2xl mx-auto text-left">
            <div className="p-4 bg-crypto-dark/50 rounded-lg">
              <Network className="w-5 h-5 text-neon-green mb-2" />
              <p className="text-sm text-white font-medium">Network Graphs</p>
              <p className="text-xs text-gray-500">Visualize wallet relationships</p>
            </div>
            <div className="p-4 bg-crypto-dark/50 rounded-lg">
              <Brain className="w-5 h-5 text-neon-green mb-2" />
              <p className="text-sm text-white font-medium">AI Clustering</p>
              <p className="text-xs text-gray-500">ML-powered pattern detection</p>
            </div>
            <div className="p-4 bg-crypto-dark/50 rounded-lg">
              <Target className="w-5 h-5 text-neon-green mb-2" />
              <p className="text-sm text-white font-medium">Syndicate Tracking</p>
              <p className="text-xs text-gray-500">Follow organized crime groups</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Network className="w-6 h-6 text-neon-green" />
            Wallet Clustering
          </h1>
          <p className="text-gray-400 mt-1">
            Detect and analyze connected wallet networks, scam syndicates, and coordinated attacks
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowAIFinder(!showAIFinder)}
            className="btn-primary flex items-center gap-2"
          >
            <Brain className="w-4 h-4" />
            AI Cluster Finder
          </button>
          <button className="btn-secondary flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export
          </button>
        </div>
      </div>

      {/* AI Cluster Finder */}
      {showAIFinder && (
        <div className="crypto-card border-neon-green/30">
          <div className="flex items-center gap-2 mb-4">
            <Brain className="w-5 h-5 text-neon-green" />
            <h3 className="font-semibold text-white">AI-Powered Cluster Detection</h3>
          </div>
          <p className="text-sm text-gray-400 mb-4">
            Enter a wallet address to discover related wallets, transaction patterns, and potential cluster affiliations.
          </p>
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Wallet className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={walletInput}
                onChange={(e) => setWalletInput(e.target.value)}
                placeholder="Enter wallet address to analyze (0x...)"
                className="w-full bg-crypto-dark border border-crypto-border rounded-lg pl-10 pr-4 py-3
                         text-white placeholder-gray-500 focus:border-neon-green focus:outline-none font-mono"
              />
            </div>
            <button
              onClick={handleFindCluster}
              disabled={clusterAnalysis.isPending || !walletInput}
              className="btn-primary flex items-center gap-2 px-6"
            >
              {clusterAnalysis.isPending ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Play className="w-4 h-4" />
              )}
              Analyze
            </button>
          </div>
          {clusterAnalysis.data && (
            <div className="mt-4 p-4 bg-neon-green/10 rounded-lg border border-neon-green/20">
              <h4 className="font-medium text-neon-green mb-2">Analysis Results</h4>
              <p className="text-sm text-gray-300">{clusterAnalysis.data.analysis}</p>
            </div>
          )}
        </div>
      )}

      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="crypto-card">
          <p className="text-gray-400 text-sm">Active Clusters</p>
          <p className="text-2xl font-bold text-white">{MOCK_CLUSTERS.filter(c => c.status === 'active').length}</p>
          <p className="text-xs text-red-400 mt-1">{MOCK_CLUSTERS.filter(c => c.severity === 'CRITICAL').length} Critical</p>
        </div>
        <div className="crypto-card">
          <p className="text-gray-400 text-sm">Wallets Tracked</p>
          <p className="text-2xl font-bold text-white">
            {MOCK_CLUSTERS.reduce((acc, c) => acc + c.wallet_count, 0)}
          </p>
          <p className="text-xs text-neon-green mt-1">Across {MOCK_CLUSTERS.length} networks</p>
        </div>
        <div className="crypto-card">
          <p className="text-gray-400 text-sm">Total Volume</p>
          <p className="text-2xl font-bold text-white">
            {MOCK_CLUSTERS.reduce((acc, c) => acc + c.total_volume_eth, 0).toFixed(1)} ETH
          </p>
          <p className="text-xs text-yellow-400 mt-1">High value targets</p>
        </div>
        <div className="crypto-card">
          <p className="text-gray-400 text-sm">AI Confidence</p>
          <p className="text-2xl font-bold text-white">
            {Math.round(MOCK_CLUSTERS.reduce((acc, c) => acc + c.confidence_score, 0) / MOCK_CLUSTERS.length)}%
          </p>
          <p className="text-xs text-neon-green mt-1">Avg detection rate</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[250px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search clusters by name, ID, or tags..."
            className="w-full bg-crypto-card border border-crypto-border rounded-lg pl-10 pr-4 py-2.5
                     text-white placeholder-gray-500 focus:border-neon-green focus:outline-none"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="bg-crypto-card border border-crypto-border rounded-lg px-3 py-2.5
                     text-white focus:border-neon-green focus:outline-none"
          >
            {CLUSTER_TYPES.map(type => (
              <option key={type.id} value={type.id}>{type.label}</option>
            ))}
          </select>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-crypto-card border border-crypto-border rounded-lg px-3 py-2.5
                     text-white focus:border-neon-green focus:outline-none"
          >
            <option value="all">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>
        <div className="flex bg-crypto-card rounded-lg p-1 border border-crypto-border">
          <button
            onClick={() => setViewMode('grid')}
            className={`px-3 py-1.5 rounded text-sm transition-colors ${
              viewMode === 'grid' ? 'bg-neon-green/20 text-neon-green' : 'text-gray-400 hover:text-white'
            }`}
          >
            Grid
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`px-3 py-1.5 rounded text-sm transition-colors ${
              viewMode === 'list' ? 'bg-neon-green/20 text-neon-green' : 'text-gray-400 hover:text-white'
            }`}
          >
            List
          </button>
        </div>
      </div>

      {/* Cluster Detail Modal */}
      {selectedCluster && selectedClusterData && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="crypto-card w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-crypto-border">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h2 className="text-xl font-bold text-white">{selectedClusterData.name}</h2>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${SEVERITY_COLORS[selectedClusterData.severity as keyof typeof SEVERITY_COLORS]}`}>
                    {selectedClusterData.severity}
                  </span>
                </div>
                <p className="text-sm text-gray-400">{selectedClusterData.id}</p>
              </div>
              <button
                onClick={() => setSelectedCluster(null)}
                className="p-2 text-gray-400 hover:text-white transition-colors"
              >
                <XCircle className="w-6 h-6" />
              </button>
            </div>

            {/* Modal Tabs */}
            <div className="flex border-b border-crypto-border px-6">
              {(['overview', 'network', 'timeline'] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === tab
                      ? 'text-neon-green border-neon-green'
                      : 'text-gray-400 border-transparent hover:text-white'
                  }`}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>

            {/* Modal Content */}
            <div className="p-6 overflow-y-auto flex-1">
              {activeTab === 'overview' && (
                <div className="space-y-6">
                  <p className="text-gray-300">{selectedClusterData.description}</p>
                  
                  {/* Cluster Stats */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="p-4 bg-crypto-dark rounded-lg">
                      <p className="text-sm text-gray-400">Wallets</p>
                      <p className="text-xl font-bold text-white">{selectedClusterData.wallet_count}</p>
                    </div>
                    <div className="p-4 bg-crypto-dark rounded-lg">
                      <p className="text-sm text-gray-400">Volume</p>
                      <p className="text-xl font-bold text-white">{selectedClusterData.total_volume_eth} ETH</p>
                    </div>
                    <div className="p-4 bg-crypto-dark rounded-lg">
                      <p className="text-sm text-gray-400">AI Confidence</p>
                      <p className="text-xl font-bold text-neon-green">{selectedClusterData.confidence_score}%</p>
                    </div>
                    <div className="p-4 bg-crypto-dark rounded-lg">
                      <p className="text-sm text-gray-400">Status</p>
                      <p className="text-xl font-bold text-white capitalize">{selectedClusterData.status}</p>
                    </div>
                  </div>

                  {/* Tags */}
                  <div>
                    <h4 className="text-sm font-medium text-gray-400 mb-2">Tags</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedClusterData.tags.map((tag) => (
                        <span
                          key={tag}
                          className="px-3 py-1 bg-crypto-dark rounded-full text-xs text-gray-300 border border-crypto-border"
                        >
                          {tag.replace('_', ' ')}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Central Wallets */}
                  <div>
                    <h4 className="text-sm font-medium text-gray-400 mb-2">Central Wallets</h4>
                    <div className="space-y-2">
                      {selectedClusterData.central_wallets.map((wallet) => (
                        <div key={wallet} className="flex items-center justify-between p-3 bg-crypto-dark rounded-lg">
                          <code className="text-neon-green font-mono text-sm">{wallet}</code>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => copyAddress(wallet)}
                              className="p-1.5 text-gray-400 hover:text-white transition-colors"
                            >
                              {copiedAddress === wallet ? <Check className="w-4 h-4 text-neon-green" /> : <Copy className="w-4 h-4" />}
                            </button>
                            <a
                              href={`https://etherscan.io/address/${wallet}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="p-1.5 text-gray-400 hover:text-neon-blue transition-colors"
                            >
                              <ExternalLink className="w-4 h-4" />
                            </a>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Detected Patterns */}
                  <div>
                    <h4 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
                      <Zap className="w-4 h-4" />
                      Detected Patterns
                    </h4>
                    <div className="space-y-3">
                      {MOCK_CLUSTER_DETAILS.patterns.map((pattern, idx) => (
                        <div key={idx} className="p-4 bg-crypto-dark rounded-lg border border-crypto-border">
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-medium text-white">{pattern.type}</span>
                            <span className="text-xs text-neon-green">{pattern.confidence}% confidence</span>
                          </div>
                          <p className="text-sm text-gray-400">{pattern.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'network' && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-white">Network Visualization</h3>
                    <button className="text-sm text-neon-green hover:text-neon-green/80 flex items-center gap-1">
                      <Maximize2 className="w-4 h-4" />
                      Full Screen
                    </button>
                  </div>
                  <div className="aspect-video bg-crypto-dark rounded-lg border border-crypto-border relative overflow-hidden">
                    {/* Simplified Network Graph Visualization */}
                    <svg className="w-full h-full" viewBox="0 0 800 450">
                      {/* Connection lines */}
                      {MOCK_CLUSTER_DETAILS.connections.map((conn, idx) => {
                        const fromNode = MOCK_CLUSTER_DETAILS.nodes.find(n => n.id === conn.from);
                        const toNode = MOCK_CLUSTER_DETAILS.nodes.find(n => n.id === conn.to);
                        if (!fromNode || !toNode) return null;
                        
                        const fromIdx = MOCK_CLUSTER_DETAILS.nodes.indexOf(fromNode);
                        const toIdx = MOCK_CLUSTER_DETAILS.nodes.indexOf(toNode);
                        
                        // Position nodes in a circular layout
                        const fromAngle = (fromIdx / MOCK_CLUSTER_DETAILS.nodes.length) * 2 * Math.PI - Math.PI / 2;
                        const toAngle = (toIdx / MOCK_CLUSTER_DETAILS.nodes.length) * 2 * Math.PI - Math.PI / 2;
                        
                        const centerX = 400;
                        const centerY = 225;
                        const radius = 150;
                        
                        const x1 = centerX + Math.cos(fromAngle) * radius;
                        const y1 = centerY + Math.sin(fromAngle) * radius;
                        const x2 = centerX + Math.cos(toAngle) * radius;
                        const y2 = centerY + Math.sin(toAngle) * radius;
                        
                        return (
                          <line
                            key={idx}
                            x1={x1}
                            y1={y1}
                            x2={x2}
                            y2={y2}
                            stroke="#8b5cf6"
                            strokeWidth={conn.strength * 3}
                            strokeOpacity={0.4}
                          />
                        );
                      })}
                      
                      {/* Nodes */}
                      {MOCK_CLUSTER_DETAILS.nodes.map((node, idx) => {
                        const angle = (idx / MOCK_CLUSTER_DETAILS.nodes.length) * 2 * Math.PI - Math.PI / 2;
                        const centerX = 400;
                        const centerY = 225;
                        const radius = 150;
                        
                        const x = centerX + Math.cos(angle) * radius;
                        const y = centerY + Math.sin(angle) * radius;
                        
                        const nodeColor = node.type === 'central' ? '#ef4444' : 
                                         node.type === 'exit' ? '#22c55e' : '#8b5cf6';
                        const nodeSize = node.type === 'central' ? 24 : 16;
                        
                        return (
                          <g key={node.id}>
                            <circle
                              cx={x}
                              cy={y}
                              r={nodeSize}
                              fill={nodeColor}
                              fillOpacity={0.8}
                              stroke={nodeColor}
                              strokeWidth={2}
                            />
                            <text
                              x={x}
                              y={y + nodeSize + 20}
                              textAnchor="middle"
                              fill="#9ca3af"
                              fontSize="12"
                              fontFamily="monospace"
                            >
                              {node.id}
                            </text>
                            <text
                              x={x}
                              y={y + nodeSize + 35}
                              textAnchor="middle"
                              fill="#6b7280"
                              fontSize="10"
                            >
                              Risk: {node.risk_score}
                            </text>
                          </g>
                        );
                      })}
                    </svg>
                    
                    {/* Legend */}
                    <div className="absolute bottom-4 left-4 bg-crypto-card/90 p-3 rounded-lg border border-crypto-border">
                      <p className="text-xs font-medium text-gray-400 mb-2">Node Types</p>
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="w-3 h-3 rounded-full bg-red-500"></span>
                          <span className="text-xs text-gray-300">Central Hub</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="w-3 h-3 rounded-full bg-purple-500"></span>
                          <span className="text-xs text-gray-300">Layer Wallet</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="w-3 h-3 rounded-full bg-green-500"></span>
                          <span className="text-xs text-gray-300">Exit Point</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'timeline' && (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-white">Cluster Activity Timeline</h3>
                  <div className="relative">
                    {/* Timeline line */}
                    <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-crypto-border"></div>
                    
                    <div className="space-y-6">
                      {MOCK_CLUSTER_DETAILS.timeline.map((event, idx) => (
                        <div key={idx} className="relative pl-10">
                          {/* Timeline dot */}
                          <div className={`absolute left-2 top-1 w-4 h-4 rounded-full border-2 ${
                            event.type === 'liquidity_drain' ? 'bg-red-500 border-red-500' :
                            event.type === 'token_launch' ? 'bg-yellow-500 border-yellow-500' :
                            event.type === 'formation' ? 'bg-neon-green border-neon-green' :
                            'bg-blue-500 border-blue-500'
                          }`}></div>
                          
                          <div className="p-4 bg-crypto-dark rounded-lg border border-crypto-border">
                            <div className="flex items-center justify-between mb-1">
                              <span className="font-medium text-white">{event.event}</span>
                              <span className="text-xs text-gray-500">{event.date}</span>
                            </div>
                            <span className={`text-xs px-2 py-0.5 rounded ${
                              event.type === 'liquidity_drain' ? 'bg-red-500/20 text-red-400' :
                              event.type === 'token_launch' ? 'bg-yellow-500/20 text-yellow-400' :
                              event.type === 'formation' ? 'bg-neon-green/20 text-neon-green' :
                              'bg-blue-500/20 text-blue-400'
                            }`}>
                              {event.type.replace('_', ' ')}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Clusters Grid/List */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-pulse text-neon-green">Loading clusters...</div>
        </div>
      ) : filteredClusters.length === 0 ? (
        <div className="text-center py-12">
          <Network className="w-12 h-12 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">
            {searchQuery ? 'No clusters match your search' : 'No clusters detected yet. Use AI Finder to analyze wallets.'}
          </p>
        </div>
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredClusters.map((cluster) => (
            <div
              key={cluster.id}
              onClick={() => setSelectedCluster(cluster.id)}
              className="crypto-card cursor-pointer hover:border-neon-green/50 transition-colors group"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  {cluster.type === 'scam_network' && <AlertTriangle className="w-5 h-5 text-red-400" />}
                  {cluster.type === 'ponzi_scheme' && <Users className="w-5 h-5 text-orange-400" />}
                  {cluster.type === 'money_laundering' && <Layers className="w-5 h-5 text-yellow-400" />}
                  {cluster.type === 'market_manipulation' && <Activity className="w-5 h-5 text-purple-400" />}
                  {cluster.type === 'insider_trading' && <Lock className="w-5 h-5 text-blue-400" />}
                </div>
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${SEVERITY_COLORS[cluster.severity as keyof typeof SEVERITY_COLORS]}`}>
                  {cluster.severity}
                </span>
              </div>
              
              <h3 className="font-semibold text-white mb-1 group-hover:text-neon-green transition-colors">
                {cluster.name}
              </h3>
              <p className="text-xs text-gray-500 mb-3">{cluster.id}</p>
              
              <p className="text-sm text-gray-400 mb-4 line-clamp-2">{cluster.description}</p>
              
              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-1 text-gray-400">
                  <Wallet className="w-4 h-4" />
                  <span>{cluster.wallet_count}</span>
                </div>
                <div className="flex items-center gap-1 text-gray-400">
                  <Activity className="w-4 h-4" />
                  <span>{cluster.total_volume_eth} ETH</span>
                </div>
                <div className="flex items-center gap-1 text-neon-green">
                  <Brain className="w-4 h-4" />
                  <span>{cluster.confidence_score}%</span>
                </div>
              </div>
              
              <div className="mt-4 pt-3 border-t border-crypto-border flex items-center justify-between">
                <div className="flex gap-1">
                  {cluster.tags.slice(0, 2).map((tag: string) => (
                    <span key={tag} className="text-[10px] px-2 py-0.5 bg-crypto-dark rounded text-gray-400">
                      {tag.replace('_', ' ')}
                    </span>
                  ))}
                  {cluster.tags.length > 2 && (
                    <span className="text-[10px] px-2 py-0.5 bg-crypto-dark rounded text-gray-400">
                      +{cluster.tags.length - 2}
                    </span>
                  )}
                </div>
                <span className={`text-xs px-2 py-0.5 rounded ${STATUS_COLORS[cluster.status as keyof typeof STATUS_COLORS]}`}>
                  {cluster.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="crypto-card overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-crypto-border">
                <th className="text-left p-4 text-gray-400 font-medium">Cluster</th>
                <th className="text-left p-4 text-gray-400 font-medium">Type</th>
                <th className="text-left p-4 text-gray-400 font-medium">Severity</th>
                <th className="text-left p-4 text-gray-400 font-medium">Wallets</th>
                <th className="text-left p-4 text-gray-400 font-medium">Volume</th>
                <th className="text-left p-4 text-gray-400 font-medium">AI Confidence</th>
                <th className="text-left p-4 text-gray-400 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {filteredClusters.map((cluster) => (
                <tr
                  key={cluster.id}
                  onClick={() => setSelectedCluster(cluster.id)}
                  className="border-b border-crypto-border hover:bg-crypto-dark/50 cursor-pointer transition-colors"
                >
                  <td className="p-4">
                    <div>
                      <p className="font-medium text-white">{cluster.name}</p>
                      <p className="text-xs text-gray-500">{cluster.id}</p>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className="text-sm text-gray-300 capitalize">{cluster.type.replace('_', ' ')}</span>
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-xs ${SEVERITY_COLORS[cluster.severity as keyof typeof SEVERITY_COLORS]}`}>
                      {cluster.severity}
                    </span>
                  </td>
                  <td className="p-4 text-gray-300">{cluster.wallet_count}</td>
                  <td className="p-4 text-gray-300">{cluster.total_volume_eth} ETH</td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 bg-crypto-dark rounded-full overflow-hidden">
                        <div
                          className="h-full bg-neon-green rounded-full"
                          style={{ width: `${cluster.confidence_score}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-neon-green">{cluster.confidence_score}%</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-xs ${STATUS_COLORS[cluster.status as keyof typeof STATUS_COLORS]}`}>
                      {cluster.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
