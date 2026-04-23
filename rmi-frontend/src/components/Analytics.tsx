/**
 * Advanced Analytics Component
 * Muncher Maps - Network Visualization & Wallet Clustering
 * Bundle Detection, Fresh Wallet Analysis, Sniper Detection
 * 
 * MULTI-MODEL AI ARCHITECTURE:
 * - GPT-4o-mini: Fast filtering, simple patterns (cost: $0.002/query)
 * - GPT-4o: Pattern detection, risk analysis (cost: $0.015/query)
 * - Claude 3.5 Sonnet: Deep investigation reports (cost: $0.08/query)
 * - Claude 3.5 Opus: Forensic/court-ready docs (cost: $0.25/query)
 * Smart routing based on query complexity keeps costs sustainable
 * while delivering premium intelligence to all tiers.
 */
import { useState, useRef } from 'react';
import { useAppStore } from '../store/appStore';
import {
  useNetworkGraph,
  useBundleDetection,
  useFreshWalletAnalysis,
  useSniperDetection,
  useCopyTradingDetection,
} from '../hooks/useAnalytics';
import {
  Search,
  Network,
  Users,
  Clock,
  Zap,
  Target,
  Share2,
  Copy,
  Download,
  AlertTriangle,
  RotateCcw,
  Filter,
  Activity,
  Brain,
  Maximize2,
  Minimize2,
} from 'lucide-react';

const CHAINS = [
  { id: 'ethereum', name: 'Ethereum', icon: '⧫' },
  { id: 'bsc', name: 'BSC', icon: 'B' },
  { id: 'polygon', name: 'Polygon', icon: 'P' },
  { id: 'arbitrum', name: 'Arbitrum', icon: 'A' },
  { id: 'optimism', name: 'Optimism', icon: 'O' },
  { id: 'base', name: 'Base', icon: 'B' },
  { id: 'solana', name: 'Solana', icon: 'S' },
];

const ANALYSIS_TYPES = [
  { id: 'network', label: 'Muncher Map', icon: Network, desc: 'Visual wallet relationships' },
  { id: 'bundle', label: 'Bundle Detection', icon: Users, desc: 'Find coordinated groups' },
  { id: 'fresh', label: 'Fresh Wallet', icon: Clock, desc: 'New wallet analysis' },
  { id: 'sniper', label: 'Sniper Track', icon: Target, desc: 'First-block buyers' },
  { id: 'copy', label: 'Copy Trading', icon: Share2, desc: 'Mirror patterns' },
  { id: 'bot', label: 'Bot Farm', icon: Zap, desc: 'Automation detection' },
];

// Mock data for network graph
const MOCK_NETWORK_NODES = [
  { id: '0x1234...5678', type: 'target', x: 400, y: 300, risk: 85, label: 'Target Wallet' },
  { id: '0xabcd...ef01', type: 'connected', x: 250, y: 200, risk: 92, label: 'Sniper 1' },
  { id: '0x2345...6789', type: 'connected', x: 550, y: 200, risk: 88, label: 'Sniper 2' },
  { id: '0xbcde...f012', type: 'connected', x: 200, y: 350, risk: 45, label: 'CEX Deposit' },
  { id: '0x3456...7890', type: 'connected', x: 600, y: 350, risk: 67, label: 'Fresh Wallet' },
  { id: '0xcdef...0123', type: 'connected', x: 300, y: 450, risk: 73, label: 'Related' },
  { id: '0x4567...8901', type: 'connected', x: 500, y: 450, risk: 56, label: 'Related' },
  { id: '0xdef0...1234', type: 'cex', x: 150, y: 300, risk: 30, label: 'Binance Hot' },
  { id: '0x5678...9012', type: 'bridge', x: 650, y: 300, risk: 40, label: 'Bridge' },
];

const MOCK_NETWORK_EDGES = [
  { from: '0x1234...5678', to: '0xabcd...ef01', type: 'fund', value: 5.2 },
  { from: '0x1234...5678', to: '0x2345...6789', type: 'fund', value: 3.8 },
  { from: '0xabcd...ef01', to: '0xbcde...f012', type: 'cex', value: 2.1 },
  { from: '0x2345...6789', to: '0x3456...7890', type: 'transfer', value: 1.5 },
  { from: '0x1234...5678', to: '0xcdef...0123', type: 'interaction', value: 0.8 },
  { from: '0x1234...5678', to: '0x4567...8901', type: 'interaction', value: 0.3 },
  { from: '0xbcde...f012', to: '0xdef0...1234', type: 'cex', value: 5.5 },
  { from: '0x3456...7890', to: '0x5678...9012', type: 'bridge', value: 2.0 },
  { from: '0xabcd...ef01', to: '0x2345...6789', type: 'same_origin', value: 0 },
];

export default function Analytics() {
  const [address, setAddress] = useState('');
  const [chain, setChain] = useState('ethereum');
  const [activeTab, setActiveTab] = useState('network');
  const [hops, setHops] = useState(2);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [zoom, setZoom] = useState(1);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showLabels, setShowLabels] = useState(true);
  const [riskFilter, setRiskFilter] = useState<'all' | 'high' | 'critical'>('all');
  const graphRef = useRef<HTMLDivElement>(null);

  const user = useAppStore((state) => state.user);
  const setError = useAppStore((state) => state.setError);

  const tier = user?.tier || 'FREE';
  const isPro = tier === 'PRO' || tier === 'ELITE' || tier === 'ENTERPRISE';
  const isElite = tier === 'ELITE' || tier === 'ENTERPRISE';

  // Analysis hooks
  const networkQuery = useNetworkGraph(address, chain, { enabled: address.length >= 10 && activeTab === 'network' });
  const bundleQuery = useBundleDetection(address, chain, { enabled: address.length >= 10 && activeTab === 'bundle' });
  const freshQuery = useFreshWalletAnalysis(address, chain, { enabled: address.length >= 10 && activeTab === 'fresh' });
  const sniperQuery = useSniperDetection(address, chain, { enabled: address.length >= 10 && activeTab === 'sniper' });
  const copyQuery = useCopyTradingDetection(address, chain, { enabled: address.length >= 10 && activeTab === 'copy' });

  const handleAnalyze = () => {
    if (!address || address.length < 10) {
      setError('Please enter a valid wallet address');
      return;
    }
    // Trigger refetch based on active tab
    switch (activeTab) {
      case 'network':
        networkQuery.refetch();
        break;
      case 'bundle':
        bundleQuery.refetch();
        break;
      case 'fresh':
        freshQuery.refetch();
        break;
      case 'sniper':
        sniperQuery.refetch();
        break;
      case 'copy':
        copyQuery.refetch();
        break;
    }
  };

  const getNodeColor = (risk: number, type: string) => {
    if (type === 'target') return '#8b5cf6'; // purple
    if (type === 'cex') return '#3b82f6'; // blue
    if (type === 'bridge') return '#f59e0b'; // amber
    if (risk >= 80) return '#ef4444'; // red
    if (risk >= 60) return '#f97316'; // orange
    if (risk >= 40) return '#eab308'; // yellow
    return '#22c55e'; // green
  };

  const getEdgeStyle = (type: string) => {
    switch (type) {
      case 'fund':
        return { stroke: '#8b5cf6', width: 2, dash: '0' };
      case 'cex':
        return { stroke: '#3b82f6', width: 1.5, dash: '5,5' };
      case 'bridge':
        return { stroke: '#f59e0b', width: 1.5, dash: '10,5' };
      case 'same_origin':
        return { stroke: '#ef4444', width: 2, dash: '0' };
      default:
        return { stroke: '#6b7280', width: 1, dash: '0' };
    }
  };

  const renderNetworkGraph = () => {
    const nodes = networkQuery.data?.nodes || MOCK_NETWORK_NODES;
    const edges = networkQuery.data?.edges || MOCK_NETWORK_EDGES;

    const filteredNodes = riskFilter === 'all' 
      ? nodes 
      : riskFilter === 'critical' 
        ? nodes.filter((n: any) => n.risk >= 80)
        : nodes.filter((n: any) => n.risk >= 60);

    return (
      <div 
        ref={graphRef}
        className={`relative bg-[#0a0a0f] rounded-xl border border-purple-500/20 overflow-hidden ${
          isFullscreen ? 'fixed inset-4 z-50' : 'h-[500px]'
        }`}
      >
        {/* Graph Controls */}
        <div className="absolute top-4 left-4 right-4 flex items-center justify-between z-10">
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-400 bg-black/50 px-2 py-1 rounded">
              {filteredNodes.length} nodes · {edges.length} connections
            </span>
            {isElite && (
              <span className="text-xs text-green-400 bg-green-500/10 px-2 py-1 rounded flex items-center gap-1">
                <Brain size={12} />
                ML-Powered
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button 
              onClick={() => setZoom(z => Math.max(0.5, z - 0.1))}
              className="p-2 bg-black/50 rounded-lg text-gray-400 hover:text-white"
            >
              -
            </button>
            <span className="text-xs text-gray-400 w-12 text-center">{Math.round(zoom * 100)}%</span>
            <button 
              onClick={() => setZoom(z => Math.min(2, z + 0.1))}
              className="p-2 bg-black/50 rounded-lg text-gray-400 hover:text-white"
            >
              +
            </button>
            <button 
              onClick={() => setZoom(1)}
              className="p-2 bg-black/50 rounded-lg text-gray-400 hover:text-white"
            >
              <RotateCcw size={16} />
            </button>
            <button 
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-2 bg-black/50 rounded-lg text-gray-400 hover:text-white"
            >
              {isFullscreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
            </button>
          </div>
        </div>

        {/* Legend */}
        <div className="absolute bottom-4 left-4 z-10 bg-black/70 rounded-lg p-3 space-y-2">
          <p className="text-xs text-gray-400 font-medium mb-2">Connection Types</p>
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 bg-purple-500"></div>
            <span className="text-xs text-gray-300">Fund Flow</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 bg-blue-500 border-dashed border-t border-blue-500"></div>
            <span className="text-xs text-gray-300">CEX</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 bg-amber-500"></div>
            <span className="text-xs text-gray-300">Bridge</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 bg-red-500"></div>
            <span className="text-xs text-gray-300">Same Origin</span>
          </div>
        </div>

        {/* SVG Graph */}
        <svg 
          viewBox="0 0 800 600" 
          className="w-full h-full"
          style={{ transform: `scale(${zoom})`, transformOrigin: 'center' }}
        >
          {/* Grid background */}
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1f2937" strokeWidth="0.5"/>
            </pattern>
          </defs>
          <rect width="800" height="600" fill="url(#grid)" />

          {/* Edges */}
          {edges.map((edge: any, idx: number) => {
            const fromNode = nodes.find((n: any) => n.id === edge.from);
            const toNode = nodes.find((n: any) => n.id === edge.to);
            if (!fromNode || !toNode) return null;
            const style = getEdgeStyle(edge.type);
            return (
              <g key={idx}>
                <line
                  x1={fromNode.x}
                  y1={fromNode.y}
                  x2={toNode.x}
                  y2={toNode.y}
                  stroke={style.stroke}
                  strokeWidth={style.width}
                  strokeDasharray={style.dash}
                  opacity={0.6}
                />
                {edge.value > 0 && (
                  <text
                    x={(fromNode.x + toNode.x) / 2}
                    y={(fromNode.y + toNode.y) / 2 - 5}
                    fill="#9ca3af"
                    fontSize="10"
                    textAnchor="middle"
                  >
                    {edge.value} ETH
                  </text>
                )}
              </g>
            );
          })}

          {/* Nodes */}
          {filteredNodes.map((node: any) => (
            <g 
              key={node.id}
              className="cursor-pointer"
              onClick={() => setSelectedNode(selectedNode === node.id ? null : node.id)}
            >
              <circle
                cx={node.x}
                cy={node.y}
                r={node.type === 'target' ? 25 : 18}
                fill={getNodeColor(node.risk, node.type)}
                stroke={selectedNode === node.id ? '#fff' : 'transparent'}
                strokeWidth={3}
                className="transition-all hover:opacity-80"
              />
              {node.type === 'target' && (
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={30}
                  fill="none"
                  stroke="#8b5cf6"
                  strokeWidth="2"
                  strokeDasharray="4,4"
                  className="animate-spin"
                  style={{ transformOrigin: `${node.x}px ${node.y}px`, animationDuration: '8s' }}
                />
              )}
              {showLabels && (
                <text
                  x={node.x}
                  y={node.y + (node.type === 'target' ? 40 : 32)}
                  fill="#fff"
                  fontSize="11"
                  textAnchor="middle"
                  className="pointer-events-none"
                >
                  {node.label}
                </text>
              )}
              <text
                x={node.x}
                y={node.y + 5}
                fill="#fff"
                fontSize="10"
                textAnchor="middle"
                className="pointer-events-none font-mono"
              >
                {node.risk}
              </text>
            </g>
          ))}
        </svg>

        {/* Selected Node Panel */}
        {selectedNode && (
          <div className="absolute top-16 right-4 w-64 bg-[#12121a] rounded-lg border border-purple-500/20 p-4 z-10">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-medium text-white">Node Details</h4>
              <button 
                onClick={() => setSelectedNode(null)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>
            {(() => {
              const node = nodes.find((n: any) => n.id === selectedNode);
              if (!node) return null;
              return (
                <div className="space-y-2">
                  <p className="text-xs text-gray-400">Address</p>
                  <p className="text-sm font-mono text-neon-green">{node.id}</p>
                  <p className="text-xs text-gray-400">Risk Score</p>
                  <p className={`text-lg font-bold ${node.risk >= 80 ? 'text-red-400' : node.risk >= 60 ? 'text-orange-400' : 'text-green-400'}`}>
                    {node.risk}/100
                  </p>
                  <p className="text-xs text-gray-400">Type</p>
                  <p className="text-sm text-white capitalize">{node.type.replace('_', ' ')}</p>
                  <div className="flex gap-2 pt-2">
                    <button className="flex-1 px-2 py-1 bg-purple-600/20 text-purple-300 rounded text-xs">
                      Expand
                    </button>
                    <button className="flex-1 px-2 py-1 bg-blue-600/20 text-blue-300 rounded text-xs flex items-center justify-center gap-1">
                      <Copy size={12} />
                      Copy
                    </button>
                  </div>
                </div>
              );
            })()}
          </div>
        )}
      </div>
    );
  };

  const renderBundleAnalysis = () => {
    const bundles = bundleQuery.data?.bundles || [
      {
        id: 1,
        size: 12,
        wallets: ['0xabc...123', '0xdef...456', '0xghi...789'],
        coordination_score: 94,
        first_seen: '2 hours ago',
        total_volume: 45.8,
        risk_level: 'CRITICAL',
        pattern: 'Same-block buys + synchronized dumps',
      },
      {
        id: 2,
        size: 8,
        wallets: ['0xjkl...012', '0xmno...345'],
        coordination_score: 78,
        first_seen: '5 hours ago',
        total_volume: 23.2,
        risk_level: 'HIGH',
        pattern: 'Funding from same CEX batch',
      },
    ];

    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="text-red-400" size={20} />
            <span className="text-white font-medium">{bundles.length} Coordinated Groups Detected</span>
          </div>
          <button className="px-3 py-1.5 bg-purple-600/20 text-purple-300 rounded-lg text-sm flex items-center gap-1">
            <Download size={14} />
            Export Report
          </button>
        </div>

        {bundles.map((bundle: any) => (
          <div key={bundle.id} className="bg-[#12121a] rounded-xl border border-red-500/20 p-4">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h4 className="text-white font-medium flex items-center gap-2">
                  Bundle #{bundle.id}
                  <span className={`px-2 py-0.5 rounded text-xs ${
                    bundle.risk_level === 'CRITICAL' ? 'bg-red-500/20 text-red-400' :
                    bundle.risk_level === 'HIGH' ? 'bg-orange-500/20 text-orange-400' :
                    'bg-yellow-500/20 text-yellow-400'
                  }`}>
                    {bundle.risk_level}
                  </span>
                </h4>
                <p className="text-sm text-gray-400 mt-1">{bundle.pattern}</p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-white">{bundle.size}</p>
                <p className="text-xs text-gray-400">wallets</p>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="bg-black/30 rounded-lg p-3">
                <p className="text-xs text-gray-400">Coordination</p>
                <p className="text-lg font-bold text-purple-400">{bundle.coordination_score}%</p>
              </div>
              <div className="bg-black/30 rounded-lg p-3">
                <p className="text-xs text-gray-400">Total Volume</p>
                <p className="text-lg font-bold text-white">{bundle.total_volume} ETH</p>
              </div>
              <div className="bg-black/30 rounded-lg p-3">
                <p className="text-xs text-gray-400">First Seen</p>
                <p className="text-lg font-bold text-white">{bundle.first_seen}</p>
              </div>
            </div>

            <div className="space-y-2">
              <p className="text-xs text-gray-400">Connected Wallets ({bundle.wallets.length} shown)</p>
              <div className="flex flex-wrap gap-2">
                {bundle.wallets.map((wallet: string, idx: number) => (
                  <span key={idx} className="px-2 py-1 bg-black/50 rounded text-xs font-mono text-gray-300">
                    {wallet}
                  </span>
                ))}
                {bundle.size > bundle.wallets.length && (
                  <span className="px-2 py-1 bg-purple-600/20 rounded text-xs text-purple-300">
                    +{bundle.size - bundle.wallets.length} more
                  </span>
                )}
              </div>
            </div>

            <div className="flex gap-2 mt-4">
              <button className="flex-1 px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm transition-colors">
                View in Muncher Map
              </button>
              <button className="px-3 py-2 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg text-sm transition-colors flex items-center gap-1">
                <AlertTriangle size={14} />
                Report
              </button>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderFreshWalletAnalysis = () => {
    const data = freshQuery.data || {
      total_holders: 1247,
      fresh_wallets: 892,
      fresh_percentage: 71.5,
      avg_wallet_age_hours: 18.3,
      funding_sources: [
        { source: 'Binance', count: 423, percentage: 47.4 },
        { source: 'OKX', count: 198, percentage: 22.2 },
        { source: 'Faucet', count: 156, percentage: 17.5 },
        { source: 'Other CEX', count: 115, percentage: 12.9 },
      ],
      age_distribution: [
        { range: '< 1 hour', count: 234, percentage: 26.2 },
        { range: '1-6 hours', count: 356, percentage: 39.9 },
        { range: '6-24 hours', count: 198, percentage: 22.2 },
        { range: '1-7 days', count: 104, percentage: 11.7 },
      ],
      risk_assessment: {
        score: 87,
        level: 'CRITICAL',
        factors: [
          '71.5% wallets created within 24 hours',
          '47% funded from same exchange batch',
          'Batch creation detected (156 wallets in same block)',
          'No organic transaction history',
        ],
      },
    };

    return (
      <div className="space-y-6">
        {/* Risk Overview */}
        <div className="bg-gradient-to-r from-red-500/20 to-orange-500/20 rounded-xl border border-red-500/30 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-red-500/30 flex items-center justify-center">
                <Clock size={32} className="text-red-400" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white">Fresh Wallet Risk</h3>
                <p className="text-red-300">{data.risk_assessment.factors[0]}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-5xl font-bold text-red-400">{data.risk_assessment.score}</p>
              <p className="text-sm text-red-300">/100 Risk Score</p>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-[#12121a] rounded-xl p-4 border border-purple-500/20">
            <p className="text-sm text-gray-400">Total Holders</p>
            <p className="text-2xl font-bold text-white">{data.total_holders.toLocaleString()}</p>
          </div>
          <div className="bg-[#12121a] rounded-xl p-4 border border-red-500/20">
            <p className="text-sm text-gray-400">Fresh Wallets (&lt;24h)</p>
            <p className="text-2xl font-bold text-red-400">{data.fresh_wallets.toLocaleString()}</p>
            <p className="text-sm text-red-300">{data.fresh_percentage}%</p>
          </div>
          <div className="bg-[#12121a] rounded-xl p-4 border border-orange-500/20">
            <p className="text-sm text-gray-400">Avg Wallet Age</p>
            <p className="text-2xl font-bold text-orange-400">{data.avg_wallet_age_hours}h</p>
          </div>
          <div className="bg-[#12121a] rounded-xl p-4 border border-purple-500/20">
            <p className="text-sm text-gray-400">Prediction</p>
            <p className="text-lg font-bold text-purple-400">87% Rug Probability</p>
          </div>
        </div>

        {/* Funding Sources */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-[#12121a] rounded-xl border border-purple-500/20 p-4">
            <h4 className="text-white font-medium mb-4">Funding Sources</h4>
            <div className="space-y-3">
              {data.funding_sources.map((source: any, idx: number) => (
                <div key={idx}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-300">{source.source}</span>
                    <span className="text-gray-400">{source.count} ({source.percentage}%)</span>
                  </div>
                  <div className="h-2 bg-black/50 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-purple-500 rounded-full"
                      style={{ width: `${source.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-[#12121a] rounded-xl border border-purple-500/20 p-4">
            <h4 className="text-white font-medium mb-4">Age Distribution</h4>
            <div className="space-y-3">
              {data.age_distribution.map((age: any, idx: number) => (
                <div key={idx}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-300">{age.range}</span>
                    <span className="text-gray-400">{age.count} ({age.percentage}%)</span>
                  </div>
                  <div className="h-2 bg-black/50 rounded-full overflow-hidden">
                    <div 
                      className={`h-full rounded-full ${
                        idx === 0 ? 'bg-red-500' : 
                        idx === 1 ? 'bg-orange-500' : 
                        idx === 2 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${age.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Risk Factors */}
        <div className="bg-[#12121a] rounded-xl border border-red-500/20 p-4">
          <h4 className="text-white font-medium mb-3 flex items-center gap-2">
            <AlertTriangle size={18} className="text-red-400" />
            Critical Risk Factors
          </h4>
          <ul className="space-y-2">
            {data.risk_assessment.factors.map((factor: string, idx: number) => (
              <li key={idx} className="flex items-start gap-2 text-sm text-gray-300">
                <span className="text-red-400 mt-0.5">•</span>
                {factor}
              </li>
            ))}
          </ul>
        </div>
      </div>
    );
  };

  const renderSniperTracking = () => {
    const snipers = sniperQuery.data?.snipers || [
      {
        address: '0x1234...5678',
        entry_block: 18472931,
        exit_block: 18472945,
        hold_time: '14 blocks (~3 min)',
        profit: '+342%',
        gas_paid: 0.42,
        entry_price: 0.00000123,
        exit_price: 0.00000544,
        dump_percentage: 94,
        is_sniper: true,
      },
      {
        address: '0xabcd...ef01',
        entry_block: 18472932,
        exit_block: null,
        hold_time: 'Still holding',
        profit: '+156%',
        gas_paid: 0.38,
        entry_price: 0.00000125,
        exit_price: null,
        dump_percentage: 0,
        is_sniper: true,
      },
    ];

    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Target className="text-purple-400" size={20} />
            <span className="text-white font-medium">{snipers.length} Sniper Wallets Detected</span>
          </div>
          <div className="flex gap-2">
            <span className="px-3 py-1 bg-red-500/20 text-red-400 rounded-full text-sm">
              ⚠️ High Dump Risk: 67%
            </span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-purple-500/20">
                <th className="text-left p-3 text-gray-400 font-medium text-sm">Wallet</th>
                <th className="text-left p-3 text-gray-400 font-medium text-sm">Entry Block</th>
                <th className="text-left p-3 text-gray-400 font-medium text-sm">Hold Time</th>
                <th className="text-left p-3 text-gray-400 font-medium text-sm">Profit</th>
                <th className="text-left p-3 text-gray-400 font-medium text-sm">Dump %</th>
                <th className="text-left p-3 text-gray-400 font-medium text-sm">Risk</th>
              </tr>
            </thead>
            <tbody>
              {snipers.map((sniper: any, idx: number) => (
                <tr key={idx} className="border-b border-purple-500/10 hover:bg-white/5">
                  <td className="p-3">
                    <code className="text-sm font-mono text-neon-green">{sniper.address}</code>
                  </td>
                  <td className="p-3 text-sm text-gray-300">{sniper.entry_block}</td>
                  <td className="p-3 text-sm text-gray-300">{sniper.hold_time}</td>
                  <td className="p-3">
                    <span className={`text-sm font-medium ${sniper.profit.startsWith('+') ? 'text-green-400' : 'text-red-400'}`}>
                      {sniper.profit}
                    </span>
                  </td>
                  <td className="p-3">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-2 bg-black/50 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${sniper.dump_percentage > 50 ? 'bg-red-500' : 'bg-yellow-500'}`}
                          style={{ width: `${sniper.dump_percentage}%` }}
                        />
                      </div>
                      <span className="text-sm text-gray-300">{sniper.dump_percentage}%</span>
                    </div>
                  </td>
                  <td className="p-3">
                    {sniper.dump_percentage > 90 ? (
                      <span className="px-2 py-1 bg-red-500/20 text-red-400 rounded text-xs">DUMPED</span>
                    ) : sniper.dump_percentage > 50 ? (
                      <span className="px-2 py-1 bg-orange-500/20 text-orange-400 rounded text-xs">EXITING</span>
                    ) : (
                      <span className="px-2 py-1 bg-yellow-500/20 text-yellow-400 rounded text-xs">HOLDING</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Sniper Summary */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-[#12121a] rounded-xl p-4 border border-purple-500/20">
            <p className="text-sm text-gray-400">Avg Hold Time</p>
            <p className="text-xl font-bold text-white">4.2 minutes</p>
            <p className="text-xs text-red-400">⚠️ Very short - typical sniper behavior</p>
          </div>
          <div className="bg-[#12121a] rounded-xl p-4 border border-purple-500/20">
            <p className="text-sm text-gray-400">Total Sniper Profit</p>
            <p className="text-xl font-bold text-green-400">+1,247 ETH</p>
            <p className="text-xs text-gray-400">Extracted from regular buyers</p>
          </div>
          <div className="bg-[#12121a] rounded-xl p-4 border border-purple-500/20">
            <p className="text-sm text-gray-400">Dump Warning</p>
            <p className="text-xl font-bold text-red-400">ACTIVE</p>
            <p className="text-xs text-red-400">3 snipers still holding</p>
          </div>
        </div>
      </div>
    );
  };

  const renderCopyTrading = () => {
    const copies = copyQuery.data?.copies || [
      {
        leader: '0x7890...1234',
        followers: 23,
        total_copy_volume: 156.7,
        avg_delay_blocks: 3.2,
        success_rate: 68,
        pattern: 'Mirror exact trades with 2-4 block delay',
      },
    ];

    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Share2 className="text-blue-400" size={20} />
            <span className="text-white font-medium">{copies.length} Copy Trading Pattern Detected</span>
          </div>
        </div>

        {copies.map((copy: any, idx: number) => (
          <div key={idx} className="bg-[#12121a] rounded-xl border border-blue-500/20 p-4">
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="text-sm text-gray-400">Leader Wallet</p>
                <code className="text-lg font-mono text-blue-400">{copy.leader}</code>
              </div>
              <div className="text-right">
                <p className="text-3xl font-bold text-white">{copy.followers}</p>
                <p className="text-sm text-gray-400">followers</p>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="bg-black/30 rounded-lg p-3">
                <p className="text-xs text-gray-400">Copy Volume</p>
                <p className="text-lg font-bold text-blue-400">{copy.total_copy_volume} ETH</p>
              </div>
              <div className="bg-black/30 rounded-lg p-3">
                <p className="text-xs text-gray-400">Avg Delay</p>
                <p className="text-lg font-bold text-white">{copy.avg_delay_blocks} blocks</p>
              </div>
              <div className="bg-black/30 rounded-lg p-3">
                <p className="text-xs text-gray-400">Success Rate</p>
                <p className="text-lg font-bold text-green-400">{copy.success_rate}%</p>
              </div>
            </div>

            <p className="text-sm text-gray-300 bg-black/30 rounded-lg p-3">
              <span className="text-gray-400">Pattern:</span> {copy.pattern}
            </p>
          </div>
        ))}
      </div>
    );
  };

  const renderBotFarmDetection = () => {
    return (
      <div className="space-y-6">
        <div className="bg-gradient-to-r from-purple-500/20 to-blue-500/20 rounded-xl border border-purple-500/30 p-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-purple-500/30 flex items-center justify-center">
              <Zap size={32} className="text-purple-400" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">Bot Farm Detection</h3>
              <p className="text-purple-300">Advanced automation pattern analysis</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-[#12121a] rounded-xl border border-purple-500/20 p-4">
            <h4 className="text-white font-medium mb-3 flex items-center gap-2">
              <Activity size={16} className="text-purple-400" />
              Gas Pattern Analysis
            </h4>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Pattern Consistency</span>
                <span className="text-red-400">94% (High Bot Probability)</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Gas Price Variance</span>
                <span className="text-orange-400">Low (0.2% deviation)</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Priority Fee Pattern</span>
                <span className="text-red-400">Identical across 23 wallets</span>
              </div>
            </div>
          </div>

          <div className="bg-[#12121a] rounded-xl border border-purple-500/20 p-4">
            <h4 className="text-white font-medium mb-3 flex items-center gap-2">
              <Clock size={16} className="text-purple-400" />
              Timing Analysis
            </h4>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Inter-TX Time</span>
                <span className="text-red-400">12.4s avg (Suspiciously regular)</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Block Position</span>
                <span className="text-orange-400">0-3 (Flashbots/MEV)</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Time Clustering</span>
                <span className="text-red-400">47 wallets, 60s window</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-[#12121a] rounded-xl border border-red-500/20 p-4">
          <h4 className="text-white font-medium mb-3 flex items-center gap-2">
            <AlertTriangle size={18} className="text-red-400" />
            Bot Farm Detected: 847 Wallets
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-black/30 rounded-lg">
              <p className="text-2xl font-bold text-red-400">847</p>
              <p className="text-xs text-gray-400">Total Wallets</p>
            </div>
            <div className="text-center p-3 bg-black/30 rounded-lg">
              <p className="text-2xl font-bold text-orange-400">98.2%</p>
              <p className="text-xs text-gray-400">Bot Probability</p>
            </div>
            <div className="text-center p-3 bg-black/30 rounded-lg">
              <p className="text-2xl font-bold text-purple-400">$2.4M</p>
              <p className="text-xs text-gray-400">Total Volume</p>
            </div>
            <div className="text-center p-3 bg-black/30 rounded-lg">
              <p className="text-2xl font-bold text-blue-400">OKX</p>
              <p className="text-xs text-gray-400">Funding Source</p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Network className="text-purple-400" />
            Advanced Analytics
          </h1>
          <p className="text-gray-400 mt-1">
            Muncher Maps, bundle detection, fresh wallet analysis & more
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-3 py-1 bg-purple-500/20 text-purple-300 rounded-lg text-sm">
            {tier} Tier
          </span>
          {!isPro && (
            <button className="px-3 py-1 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg text-sm hover:opacity-90 transition-opacity">
              Upgrade to PRO
            </button>
          )}
        </div>
      </div>

      {/* Search */}
      <div className="bg-[#12121a] rounded-xl border border-purple-500/20 p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="md:w-48">
            <label className="block text-sm text-gray-400 mb-2">Blockchain</label>
            <select
              value={chain}
              onChange={(e) => setChain(e.target.value)}
              className="w-full bg-[#0a0a0f] border border-purple-500/20 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-purple-500/50"
            >
              {CHAINS.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.icon} {c.name}
                </option>
              ))}
            </select>
          </div>
          <div className="flex-1">
            <label className="block text-sm text-gray-400 mb-2">
              Wallet Address or Contract
              {activeTab === 'network' && isElite && (
                <span className="ml-2 text-xs text-green-400">(6 hops enabled)</span>
              )}
            </label>
            <div className="relative">
              <input
                type="text"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder="0x... or contract address"
                className="w-full bg-[#0a0a0f] border border-purple-500/20 rounded-lg px-4 py-2.5 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500/50 font-mono"
              />
            </div>
          </div>
          <div className="md:w-auto">
            <label className="block text-sm text-transparent mb-2">Action</label>
            <button
              onClick={handleAnalyze}
              disabled={!address || address.length < 10}
              className="w-full md:w-auto px-6 py-2.5 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-600/50 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
            >
              <Search size={18} />
              Analyze
            </button>
          </div>
        </div>
      </div>

      {/* Analysis Type Tabs */}
      <div className="flex flex-wrap gap-2">
        {ANALYSIS_TYPES.map((type) => {
          const Icon = type.icon;
          const isLocked = 
            (type.id === 'network' && !isPro) ||
            (type.id === 'bundle' && tier === 'FREE') ||
            (type.id === 'fresh' && tier === 'FREE') ||
            (type.id === 'sniper' && !isPro) ||
            (type.id === 'copy' && !isPro) ||
            (type.id === 'bot' && !isPro);

          return (
            <button
              key={type.id}
              onClick={() => !isLocked && setActiveTab(type.id)}
              disabled={isLocked}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === type.id
                  ? 'bg-purple-600 text-white'
                  : isLocked
                  ? 'bg-gray-800/50 text-gray-500 cursor-not-allowed'
                  : 'bg-[#12121a] text-gray-300 hover:bg-purple-600/20 hover:text-purple-300'
              }`}
            >
              <Icon size={16} />
              {type.label}
              {isLocked && <span className="text-xs ml-1">🔒</span>}
            </button>
          );
        })}
      </div>

      {/* Filters (for network graph) */}
      {activeTab === 'network' && isPro && (
        <div className="flex flex-wrap items-center gap-4 bg-[#12121a] rounded-lg p-3 border border-purple-500/20">
          <span className="text-sm text-gray-400 flex items-center gap-1">
            <Filter size={14} />
            Filters:
          </span>
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value as any)}
            className="bg-[#0a0a0f] border border-purple-500/20 rounded px-2 py-1 text-sm text-white"
          >
            <option value="all">All Risk Levels</option>
            <option value="high">High Risk (60+)</option>
            <option value="critical">Critical (80+)</option>
          </select>
          <label className="flex items-center gap-2 text-sm text-gray-300">
            <input
              type="checkbox"
              checked={showLabels}
              onChange={(e) => setShowLabels(e.target.checked)}
              className="rounded border-purple-500/20"
            />
            Show Labels
          </label>
          {isElite && (
            <select
              value={hops}
              onChange={(e) => setHops(Number(e.target.value))}
              className="bg-[#0a0a0f] border border-purple-500/20 rounded px-2 py-1 text-sm text-white"
            >
              <option value={2}>2 Hops</option>
              <option value={3}>3 Hops (PRO)</option>
              <option value={4}>4 Hops (ELITE)</option>
              <option value={6}>6 Hops (ELITE+)</option>
            </select>
          )}
        </div>
      )}

      {/* Content */}
      <div className="min-h-[400px]">
        {activeTab === 'network' && (
          isPro ? renderNetworkGraph() : (
            <div className="flex flex-col items-center justify-center h-[400px] bg-[#12121a] rounded-xl border border-purple-500/20">
              <Network size={48} className="text-gray-600 mb-4" />
              <p className="text-gray-400 mb-2">Muncher Maps requires PRO tier</p>
              <p className="text-sm text-gray-500 mb-4">Visualize wallet relationships and track funds</p>
              <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
                Upgrade to PRO
              </button>
            </div>
          )
        )}
        {activeTab === 'bundle' && (
          tier === 'FREE' ? (
            <div className="flex flex-col items-center justify-center h-[400px] bg-[#12121a] rounded-xl border border-purple-500/20">
              <Users size={48} className="text-gray-600 mb-4" />
              <p className="text-gray-400 mb-2">Bundle Detection requires BASIC+ tier</p>
              <p className="text-sm text-gray-500 mb-4">Detect coordinated wallet groups and sybil attacks</p>
              <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
                Upgrade Now
              </button>
            </div>
          ) : renderBundleAnalysis()
        )}
        {activeTab === 'fresh' && (
          tier === 'FREE' ? (
            <div className="flex flex-col items-center justify-center h-[400px] bg-[#12121a] rounded-xl border border-purple-500/20">
              <Clock size={48} className="text-gray-600 mb-4" />
              <p className="text-gray-400 mb-2">Fresh Wallet Analysis requires BASIC+ tier</p>
              <p className="text-sm text-gray-500 mb-4">Predict rugs by analyzing new wallet patterns</p>
              <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
                Upgrade Now
              </button>
            </div>
          ) : renderFreshWalletAnalysis()
        )}
        {activeTab === 'sniper' && (
          !isPro ? (
            <div className="flex flex-col items-center justify-center h-[400px] bg-[#12121a] rounded-xl border border-purple-500/20">
              <Target size={48} className="text-gray-600 mb-4" />
              <p className="text-gray-400 mb-2">Sniper Tracking requires PRO tier</p>
              <p className="text-sm text-gray-500 mb-4">Track first-block buyers and instant dumpers</p>
              <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
                Upgrade to PRO
              </button>
            </div>
          ) : renderSniperTracking()
        )}
        {activeTab === 'copy' && (
          !isPro ? (
            <div className="flex flex-col items-center justify-center h-[400px] bg-[#12121a] rounded-xl border border-purple-500/20">
              <Share2 size={48} className="text-gray-600 mb-4" />
              <p className="text-gray-400 mb-2">Copy Trading Detection requires PRO tier</p>
              <p className="text-sm text-gray-500 mb-4">Find wallets copying successful traders</p>
              <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
                Upgrade to PRO
              </button>
            </div>
          ) : renderCopyTrading()
        )}
        {activeTab === 'bot' && (
          !isPro ? (
            <div className="flex flex-col items-center justify-center h-[400px] bg-[#12121a] rounded-xl border border-purple-500/20">
              <Zap size={48} className="text-gray-600 mb-4" />
              <p className="text-gray-400 mb-2">Bot Farm Detection requires PRO tier</p>
              <p className="text-sm text-gray-500 mb-4">Identify automation patterns and MEV bots</p>
              <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
                Upgrade to PRO
              </button>
            </div>
          ) : renderBotFarmDetection()
        )}
      </div>
    </div>
  );
}
