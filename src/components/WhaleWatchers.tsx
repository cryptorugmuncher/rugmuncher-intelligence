import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Eye, Fish, TrendingUp, TrendingDown, Wallet, ArrowRightLeft, 
  Zap, Activity, BarChart3, Search, Filter, ChevronDown, ChevronUp,
  AlertTriangle, Radio, Clock, DollarSign, Target, Flame,
  Waves, Anchor, Compass, ExternalLink, Copy, Check
} from 'lucide-react';
import api from '../services/api';

// ═══════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════

interface WhaleMove {
  id: string;
  wallet: string;
  walletLabel?: string;
  type: 'BUY' | 'SELL' | 'TRANSFER' | 'SWAP' | 'STAKE' | 'UNSTAKE';
  tokenIn: string;
  tokenOut?: string;
  amount: string;
  usdValue: number;
  chain: string;
  timestamp: string;
  txHash: string;
  significance: 'MAJOR' | 'SIGNIFICANT' | 'NOTABLE' | 'ROUTINE';
  relatedWallets?: string[];
  pattern?: string;
}

interface WhaleProfile {
  address: string;
  label?: string;
  totalVolume30d: number;
  tradeCount30d: number;
  winRate: number;
  avgTradeSize: number;
  favoriteTokens: string[];
  lastActive: string;
  riskScore: number; // 0-100
  classification: 'SMART_MONEY' | 'MARKET_MAKER' | 'INSTITUTIONAL' | 'UNKNOWN' | 'SUSPECT';
}

interface TokenFlow {
  token: string;
  symbol: string;
  inflow24h: number;
  outflow24h: number;
  netFlow: number;
  whaleHolders: number;
  priceChange24h: number;
}

// ═══════════════════════════════════════════════════════════
// DEMO DATA - Will be replaced with real API calls
// ═══════════════════════════════════════════════════════════

const DEMO_MOVES: WhaleMove[] = [
  {
    id: 'ww-001',
    wallet: '8eVZa7bEBnd6MA6JJkNdABRN4S3LbVLRnCZNJAUeuwQj',
    walletLabel: 'CRM Whale #9',
    type: 'SELL',
    tokenIn: 'CRM',
    amount: '2,450,000',
    usdValue: 18450,
    chain: 'Solana',
    timestamp: new Date(Date.now() - 1000 * 60 * 12).toISOString(),
    txHash: '5xK...8mP2',
    significance: 'MAJOR',
    pattern: 'Coordinated dump following contest results'
  },
  {
    id: 'ww-002',
    wallet: 'DojAziGhp...',
    walletLabel: 'SOSANA Settlement Layer',
    type: 'TRANSFER',
    tokenIn: 'PBTC',
    tokenOut: 'SOL',
    amount: '850,000',
    usdValue: 7200,
    chain: 'Solana',
    timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    txHash: '7nQ...3vK9',
    significance: 'SIGNIFICANT',
    pattern: 'Insider reward distribution'
  },
  {
    id: 'ww-003',
    wallet: 'AFXigaYu...',
    walletLabel: 'SOSANA Seeding Arm',
    type: 'TRANSFER',
    tokenIn: 'SOSANA',
    amount: '1,200,000',
    usdValue: 3400,
    chain: 'Solana',
    timestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
    txHash: '2mR...9wL4',
    significance: 'NOTABLE',
    pattern: 'Mass airdrop infrastructure'
  },
  {
    id: 'ww-004',
    wallet: 'HnKLp3vR...',
    walletLabel: 'Smart Money Whale',
    type: 'BUY',
    tokenIn: 'BONK',
    amount: '15,000,000,000',
    usdValue: 28500,
    chain: 'Solana',
    timestamp: new Date(Date.now() - 1000 * 60 * 8).toISOString(),
    txHash: '9pT...2xM7',
    significance: 'MAJOR',
    pattern: 'Accumulation before major announcement'
  },
  {
    id: 'ww-005',
    wallet: 'JmQw5tYx...',
    walletLabel: 'Market Maker Alpha',
    type: 'SWAP',
    tokenIn: 'USDC',
    tokenOut: 'WIF',
    amount: '50,000',
    usdValue: 50000,
    chain: 'Solana',
    timestamp: new Date(Date.now() - 1000 * 60 * 22).toISOString(),
    txHash: '4vB...6nK1',
    significance: 'MAJOR',
    pattern: 'Large position entry'
  },
  {
    id: 'ww-006',
    wallet: 'KpRs7uZx...',
    walletLabel: 'VC Wallet',
    type: 'SELL',
    tokenIn: 'JUP',
    amount: '125,000',
    usdValue: 42000,
    chain: 'Solana',
    timestamp: new Date(Date.now() - 1000 * 60 * 35).toISOString(),
    txHash: '1cD...8fH3',
    significance: 'SIGNIFICANT',
    pattern: 'VC unlock distribution'
  },
  {
    id: 'ww-007',
    wallet: 'LmTu9vBy...',
    walletLabel: 'DeFi Whale',
    type: 'STAKE',
    tokenIn: 'SOL',
    amount: '8,500',
    usdValue: 1275000,
    chain: 'Solana',
    timestamp: new Date(Date.now() - 1000 * 60 * 55).toISOString(),
    txHash: '6gE...4jI8',
    significance: 'MAJOR',
    pattern: 'Institutional staking'
  },
  {
    id: 'ww-008',
    wallet: 'NwVx1wDa...',
    walletLabel: 'Meme Lord',
    type: 'BUY',
    tokenIn: 'POPCAT',
    amount: '3,200,000',
    usdValue: 15600,
    chain: 'Solana',
    timestamp: new Date(Date.now() - 1000 * 60 * 67).toISOString(),
    txHash: '3hF...5kL2',
    significance: 'NOTABLE',
    pattern: 'Social momentum play'
  },
];

const DEMO_PROFILES: WhaleProfile[] = [
  {
    address: 'HnKLp3vR...',
    label: 'Smart Money Whale',
    totalVolume30d: 2840000,
    tradeCount30d: 47,
    winRate: 72,
    avgTradeSize: 60400,
    favoriteTokens: ['BONK', 'WIF', 'JUP'],
    lastActive: '12 min ago',
    riskScore: 35,
    classification: 'SMART_MONEY'
  },
  {
    address: 'JmQw5tYx...',
    label: 'Market Maker Alpha',
    totalVolume30d: 15200000,
    tradeCount30d: 312,
    winRate: 58,
    avgTradeSize: 48700,
    favoriteTokens: ['SOL', 'USDC', 'WIF'],
    lastActive: '22 min ago',
    riskScore: 25,
    classification: 'MARKET_MAKER'
  },
  {
    address: '8eVZa7bE...',
    label: 'CRM Whale #9',
    totalVolume30d: 450000,
    tradeCount30d: 12,
    winRate: 33,
    avgTradeSize: 37500,
    favoriteTokens: ['CRM', 'PBTC', 'SOSANA'],
    lastActive: '12 min ago',
    riskScore: 92,
    classification: 'SUSPECT'
  },
  {
    address: 'LmTu9vBy...',
    label: 'DeFi Whale',
    totalVolume30d: 42000000,
    tradeCount30d: 89,
    winRate: 81,
    avgTradeSize: 472000,
    favoriteTokens: ['SOL', 'mSOL', 'JitoSOL'],
    lastActive: '55 min ago',
    riskScore: 15,
    classification: 'INSTITUTIONAL'
  },
];

const DEMO_FLOWS: TokenFlow[] = [
  { token: 'BONK', symbol: 'BONK', inflow24h: 2840000, outflow24h: 1200000, netFlow: 1640000, whaleHolders: 1247, priceChange24h: 12.4 },
  { token: 'WIF', symbol: 'WIF', inflow24h: 5200000, outflow24h: 3100000, netFlow: 2100000, whaleHolders: 892, priceChange24h: 8.7 },
  { token: 'JUP', symbol: 'JUP', inflow24h: 1800000, outflow24h: 4200000, netFlow: -2400000, whaleHolders: 634, priceChange24h: -5.2 },
  { token: 'SOL', symbol: 'SOL', inflow24h: 15200000, outflow24h: 8900000, netFlow: 6300000, whaleHolders: 2104, priceChange24h: 3.1 },
  { token: 'POPCAT', symbol: 'POPCAT', inflow24h: 890000, outflow24h: 450000, netFlow: 440000, whaleHolders: 567, priceChange24h: 15.3 },
  { token: 'CRM', symbol: 'CRM', inflow24h: 120000, outflow24h: 450000, netFlow: -330000, whaleHolders: 89, priceChange24h: -18.5 },
];

// ═══════════════════════════════════════════════════════════
// HELPERS
// ═══════════════════════════════════════════════════════════

function formatTimeAgo(isoString: string): string {
  const diff = Date.now() - new Date(isoString).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'Just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

function formatUSD(val: number): string {
  if (val >= 1_000_000) return `$${(val / 1_000_000).toFixed(2)}M`;
  if (val >= 1_000) return `$${(val / 1_000).toFixed(1)}K`;
  return `$${val.toFixed(0)}`;
}

const SignificanceBadge: React.FC<{ level: string }> = ({ level }) => {
  const colors: Record<string, string> = {
    MAJOR: 'bg-red-600/20 text-red-400 border border-red-500/30',
    SIGNIFICANT: 'bg-orange-600/20 text-orange-400 border border-orange-500/30',
    NOTABLE: 'bg-amber-600/20 text-amber-400 border border-amber-500/30',
    ROUTINE: 'bg-slate-600/20 text-slate-400 border border-slate-500/30',
  };
  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase ${colors[level] || colors.ROUTINE}`}>
      {level}
    </span>
  );
};

const TypeBadge: React.FC<{ type: string }> = ({ type }) => {
  const colors: Record<string, string> = {
    BUY: 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30',
    SELL: 'bg-red-600/20 text-red-400 border border-red-500/30',
    TRANSFER: 'bg-blue-600/20 text-blue-400 border border-blue-500/30',
    SWAP: 'bg-purple-600/20 text-purple-400 border border-purple-500/30',
    STAKE: 'bg-cyan-600/20 text-cyan-400 border border-cyan-500/30',
    UNSTAKE: 'bg-amber-600/20 text-amber-400 border border-amber-500/30',
  };
  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase ${colors[type] || colors.TRANSFER}`}>
      {type}
    </span>
  );
};

const ClassificationBadge: React.FC<{ type: string }> = ({ type }) => {
  const colors: Record<string, string> = {
    SMART_MONEY: 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30',
    MARKET_MAKER: 'bg-blue-600/20 text-blue-400 border border-blue-500/30',
    INSTITUTIONAL: 'bg-purple-600/20 text-purple-400 border border-purple-500/30',
    UNKNOWN: 'bg-slate-600/20 text-slate-400 border border-slate-500/30',
    SUSPECT: 'bg-red-600/20 text-red-400 border border-red-500/30',
  };
  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase ${colors[type] || colors.UNKNOWN}`}>
      {type.replace('_', ' ')}
    </span>
  );
};

// ═══════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════

export default function WhaleWatchers() {
  const [activeTab, setActiveTab] = useState<'feed' | 'profiles' | 'flows'>('feed');
  const [moves, setMoves] = useState<WhaleMove[]>(DEMO_MOVES);
  const [filterType, setFilterType] = useState<string>('ALL');
  const [filterSig, setFilterSig] = useState<string>('ALL');
  const [searchWallet, setSearchWallet] = useState('');
  const [copiedTx, setCopiedTx] = useState<string | null>(null);
  const [livePulse, setLivePulse] = useState(false);

  // Simulated live updates
  useEffect(() => {
    const interval = setInterval(() => {
      setLivePulse(p => !p);
      // Occasionally add a new random move
      if (Math.random() > 0.7) {
        const types: WhaleMove['type'][] = ['BUY', 'SELL', 'TRANSFER', 'SWAP'];
        const tokens = ['BONK', 'WIF', 'JUP', 'SOL', 'POPCAT', 'PEPE', 'SHIB'];
        const newMove: WhaleMove = {
          id: `ww-${Date.now()}`,
          wallet: `0x${Math.random().toString(36).substring(2, 8)}...`,
          type: types[Math.floor(Math.random() * types.length)],
          tokenIn: tokens[Math.floor(Math.random() * tokens.length)],
          amount: (Math.random() * 5000000).toFixed(0),
          usdValue: Math.random() * 50000 + 1000,
          chain: 'Solana',
          timestamp: new Date().toISOString(),
          txHash: `${Math.random().toString(36).substring(2, 5)}...${Math.random().toString(36).substring(2, 5)}`,
          significance: Math.random() > 0.7 ? 'MAJOR' : Math.random() > 0.5 ? 'SIGNIFICANT' : 'NOTABLE',
          pattern: 'Live detected movement'
        };
        setMoves(prev => [newMove, ...prev].slice(0, 50));
      }
    }, 8000);
    return () => clearInterval(interval);
  }, []);

  const filteredMoves = moves.filter(m => {
    if (filterType !== 'ALL' && m.type !== filterType) return false;
    if (filterSig !== 'ALL' && m.significance !== filterSig) return false;
    if (searchWallet && !m.wallet.toLowerCase().includes(searchWallet.toLowerCase()) && !m.walletLabel?.toLowerCase().includes(searchWallet.toLowerCase())) return false;
    return true;
  });

  const tabs = [
    { id: 'feed' as const, label: 'Live Feed', icon: Radio },
    { id: 'profiles' as const, label: 'Whale Profiles', icon: Fish },
    { id: 'flows' as const, label: 'Token Flows', icon: Waves },
  ];

  const copyTx = (hash: string) => {
    navigator.clipboard.writeText(hash);
    setCopiedTx(hash);
    setTimeout(() => setCopiedTx(null), 2000);
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-200">
      {/* HERO */}
      <div className="relative overflow-hidden border-b border-cyan-900/20">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(6,182,212,0.06),transparent_70%)]" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10 relative">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded bg-cyan-950/60 border border-cyan-800/40 flex items-center justify-center">
              <Eye className="w-5 h-5 text-cyan-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">Whale Watchers</h1>
              <p className="text-xs text-cyan-400/70 font-mono tracking-wider uppercase">Big Movements. Early Signals.</p>
            </div>
            <div className="ml-auto flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${livePulse ? 'bg-emerald-400' : 'bg-emerald-600'} transition-colors`} />
              <span className="text-[10px] text-emerald-400/70 font-mono uppercase tracking-wider">Live</span>
            </div>
          </div>

          <div className="flex gap-4 mt-5">
            <div className="bg-cyan-950/20 border border-cyan-900/30 rounded px-4 py-2.5">
              <div className="text-[10px] text-cyan-400/60 uppercase tracking-wider">24h Volume</div>
              <div className="text-lg font-bold text-cyan-300">$284.2M</div>
            </div>
            <div className="bg-cyan-950/20 border border-cyan-900/30 rounded px-4 py-2.5">
              <div className="text-[10px] text-cyan-400/60 uppercase tracking-wider">Whale Wallets</div>
              <div className="text-lg font-bold text-cyan-300">2,847</div>
            </div>
            <div className="bg-cyan-950/20 border border-cyan-900/30 rounded px-4 py-2.5">
              <div className="text-[10px] text-cyan-400/60 uppercase tracking-wider">Major Moves</div>
              <div className="text-lg font-bold text-cyan-300">{moves.filter(m => m.significance === 'MAJOR').length}</div>
            </div>
            <div className="bg-cyan-950/20 border border-cyan-900/30 rounded px-4 py-2.5">
              <div className="text-[10px] text-cyan-400/60 uppercase tracking-wider">Smart Money Score</div>
              <div className="text-lg font-bold text-emerald-400">+12.4%</div>
            </div>
          </div>
        </div>
      </div>

      {/* TABS */}
      <div className="border-b border-slate-800/60 bg-[#0d0d14]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex gap-1 overflow-x-auto py-1">
            {tabs.map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2.5 text-xs font-medium rounded-t transition-all whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'text-cyan-400 border-b-2 border-cyan-500 bg-cyan-950/20'
                      : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800/30'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* CONTENT */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2 }}
          >
            {activeTab === 'feed' && (
              <FeedTab
                moves={filteredMoves}
                filterType={filterType}
                setFilterType={setFilterType}
                filterSig={filterSig}
                setFilterSig={setFilterSig}
                searchWallet={searchWallet}
                setSearchWallet={setSearchWallet}
                copyTx={copyTx}
                copiedTx={copiedTx}
              />
            )}
            {activeTab === 'profiles' && <ProfilesTab profiles={DEMO_PROFILES} />}
            {activeTab === 'flows' && <FlowsTab flows={DEMO_FLOWS} />}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// FEED TAB
// ═══════════════════════════════════════════════════════════

function FeedTab({
  moves, filterType, setFilterType, filterSig, setFilterSig,
  searchWallet, setSearchWallet, copyTx, copiedTx
}: {
  moves: WhaleMove[];
  filterType: string; setFilterType: (v: string) => void;
  filterSig: string; setFilterSig: (v: string) => void;
  searchWallet: string; setSearchWallet: (v: string) => void;
  copyTx: (h: string) => void;
  copiedTx: string | null;
}) {
  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500" />
          <input
            type="text"
            value={searchWallet}
            onChange={e => setSearchWallet(e.target.value)}
            placeholder="Search wallet or label..."
            className="w-full bg-slate-900/60 border border-slate-700/50 rounded pl-8 pr-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-600/50"
          />
        </div>
        <select
          value={filterType}
          onChange={e => setFilterType(e.target.value)}
          className="bg-slate-900/60 border border-slate-700/50 rounded px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-cyan-600/50"
        >
          <option value="ALL">All Types</option>
          <option value="BUY">Buy</option>
          <option value="SELL">Sell</option>
          <option value="TRANSFER">Transfer</option>
          <option value="SWAP">Swap</option>
          <option value="STAKE">Stake</option>
        </select>
        <select
          value={filterSig}
          onChange={e => setFilterSig(e.target.value)}
          className="bg-slate-900/60 border border-slate-700/50 rounded px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-cyan-600/50"
        >
          <option value="ALL">All Significance</option>
          <option value="MAJOR">Major</option>
          <option value="SIGNIFICANT">Significant</option>
          <option value="NOTABLE">Notable</option>
        </select>
      </div>

      {/* Moves Feed */}
      <div className="space-y-2">
        {moves.map((move, i) => (
          <motion.div
            key={move.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: Math.min(i * 0.03, 0.3) }}
            className={`bg-slate-900/40 border rounded-lg p-3.5 transition-colors ${
              move.significance === 'MAJOR' ? 'border-red-800/20 hover:border-red-700/30' : 'border-slate-800/50 hover:border-slate-700/50'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3 flex-1 min-w-0">
                <div className={`w-8 h-8 rounded flex items-center justify-center flex-shrink-0 ${
                  move.type === 'BUY' ? 'bg-emerald-950/40' :
                  move.type === 'SELL' ? 'bg-red-950/40' :
                  move.type === 'STAKE' ? 'bg-cyan-950/40' :
                  'bg-blue-950/40'
                }`}>
                  {move.type === 'BUY' ? <TrendingUp className="w-4 h-4 text-emerald-400" /> :
                   move.type === 'SELL' ? <TrendingDown className="w-4 h-4 text-red-400" /> :
                   move.type === 'SWAP' ? <ArrowRightLeft className="w-4 h-4 text-purple-400" /> :
                   move.type === 'STAKE' ? <Anchor className="w-4 h-4 text-cyan-400" /> :
                   <Wallet className="w-4 h-4 text-blue-400" />}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <TypeBadge type={move.type} />
                    <SignificanceBadge level={move.significance} />
                    <span className="text-[10px] text-slate-500 font-mono">{formatTimeAgo(move.timestamp)}</span>
                  </div>
                  <div className="flex items-center gap-2 mt-1.5 text-xs">
                    <span className="text-slate-400 truncate max-w-[180px]">
                      {move.walletLabel || move.wallet}
                    </span>
                    <span className="text-slate-600">|</span>
                    <span className="text-white font-bold">{move.amount} {move.tokenIn}</span>
                    {move.tokenOut && (
                      <>
                        <ArrowRightLeft className="w-3 h-3 text-slate-500" />
                        <span className="text-white font-bold">{move.tokenOut}</span>
                      </>
                    )}
                    <span className="text-cyan-400 font-mono">{formatUSD(move.usdValue)}</span>
                  </div>
                  {move.pattern && (
                    <div className="flex items-center gap-1.5 mt-1">
                      <Compass className="w-3 h-3 text-amber-500/60" />
                      <span className="text-[10px] text-amber-400/70">{move.pattern}</span>
                    </div>
                  )}
                </div>
              </div>
              <button
                onClick={() => copyTx(move.txHash)}
                className="flex items-center gap-1 text-[10px] text-slate-500 hover:text-cyan-400 transition-colors ml-2 flex-shrink-0"
              >
                {copiedTx === move.txHash ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                <span className="font-mono">{move.txHash}</span>
              </button>
            </div>
          </motion.div>
        ))}
        {moves.length === 0 && (
          <div className="text-center py-12 text-slate-500">
            <Fish className="w-8 h-8 mx-auto mb-2 opacity-40" />
            <p className="text-sm">No whale movements match your filters</p>
          </div>
        )}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// PROFILES TAB
// ═══════════════════════════════════════════════════════════

function ProfilesTab({ profiles }: { profiles: WhaleProfile[] }) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      {profiles.map((profile, i) => (
        <motion.div
          key={profile.address}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.08 }}
          className="bg-slate-900/40 border border-slate-800/50 rounded-lg p-4 hover:border-slate-700/50 transition-colors"
        >
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-cyan-950/40 border border-cyan-800/30 flex items-center justify-center">
                <Fish className="w-4 h-4 text-cyan-400/70" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-white">{profile.label || profile.address}</h4>
                <p className="text-[10px] text-slate-500 font-mono">{profile.address}</p>
              </div>
            </div>
            <ClassificationBadge type={profile.classification} />
          </div>

          <div className="grid grid-cols-3 gap-2 mb-3">
            <div className="bg-slate-800/30 rounded p-2 text-center">
              <div className="text-xs font-bold text-white">{formatUSD(profile.totalVolume30d)}</div>
              <div className="text-[9px] text-slate-500">30d Vol</div>
            </div>
            <div className="bg-slate-800/30 rounded p-2 text-center">
              <div className="text-xs font-bold text-white">{profile.tradeCount30d}</div>
              <div className="text-[9px] text-slate-500">Trades</div>
            </div>
            <div className="bg-slate-800/30 rounded p-2 text-center">
              <div className={`text-xs font-bold ${profile.winRate >= 60 ? 'text-emerald-400' : profile.winRate >= 40 ? 'text-amber-400' : 'text-red-400'}`}>
                {profile.winRate}%
              </div>
              <div className="text-[9px] text-slate-500">Win Rate</div>
            </div>
          </div>

          <div className="flex items-center gap-2 text-[11px] mb-2">
            <DollarSign className="w-3 h-3 text-slate-500" />
            <span className="text-slate-400">Avg trade:</span>
            <span className="text-white font-mono">{formatUSD(profile.avgTradeSize)}</span>
          </div>

          <div className="flex items-center gap-2 text-[11px] mb-2">
            <Clock className="w-3 h-3 text-slate-500" />
            <span className="text-slate-400">Last active:</span>
            <span className="text-slate-200">{profile.lastActive}</span>
          </div>

          <div className="flex items-center gap-2 mb-2">
            <span className="text-[10px] text-slate-500">Risk Score:</span>
            <div className="flex-1 h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${
                  profile.riskScore >= 70 ? 'bg-red-500' :
                  profile.riskScore >= 40 ? 'bg-amber-500' :
                  'bg-emerald-500'
                }`}
                style={{ width: `${profile.riskScore}%` }}
              />
            </div>
            <span className={`text-[10px] font-bold ${
              profile.riskScore >= 70 ? 'text-red-400' :
              profile.riskScore >= 40 ? 'text-amber-400' :
              'text-emerald-400'
            }`}>{profile.riskScore}</span>
          </div>

          <div className="flex flex-wrap gap-1">
            {profile.favoriteTokens.map(token => (
              <span key={token} className="px-1.5 py-0.5 rounded bg-slate-800/50 text-[10px] text-slate-400">
                {token}
              </span>
            ))}
          </div>
        </motion.div>
      ))}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// FLOWS TAB
// ═══════════════════════════════════════════════════════════

function FlowsTab({ flows }: { flows: TokenFlow[] }) {
  return (
    <div className="space-y-4">
      <div className="grid gap-3">
        {flows.map((flow, i) => (
          <motion.div
            key={flow.token}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="bg-slate-900/40 border border-slate-800/50 rounded-lg p-4"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded bg-slate-800/50 flex items-center justify-center">
                  <span className="text-xs font-bold text-white">{flow.symbol.slice(0, 2)}</span>
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white">{flow.symbol}</h4>
                  <span className="text-[10px] text-slate-500">{flow.whaleHolders} whale holders</span>
                </div>
              </div>
              <div className={`text-sm font-bold font-mono ${flow.priceChange24h >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {flow.priceChange24h >= 0 ? '+' : ''}{flow.priceChange24h}%
              </div>
            </div>

            {/* Net Flow Bar */}
            <div className="mb-2">
              <div className="flex items-center justify-between text-[10px] mb-1">
                <span className="text-emerald-400">In: {formatUSD(flow.inflow24h)}</span>
                <span className="text-red-400">Out: {formatUSD(flow.outflow24h)}</span>
              </div>
              <div className="h-2 bg-slate-800 rounded-full overflow-hidden flex">
                <div 
                  className="bg-emerald-500/60 transition-all"
                  style={{ width: `${Math.max(5, (flow.inflow24h / (flow.inflow24h + flow.outflow24h)) * 100)}%` }}
                />
                <div 
                  className="bg-red-500/60 transition-all"
                  style={{ width: `${Math.max(5, (flow.outflow24h / (flow.inflow24h + flow.outflow24h)) * 100)}%` }}
                />
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-[10px] text-slate-500">Net Flow:</span>
              <span className={`text-xs font-bold font-mono ${flow.netFlow >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {flow.netFlow >= 0 ? '+' : ''}{formatUSD(Math.abs(flow.netFlow))}
              </span>
              {flow.netFlow > 1000000 && (
                <span className="flex items-center gap-1 text-[10px] text-amber-400">
                  <Flame className="w-3 h-3" /> High accumulation
                </span>
              )}
              {flow.netFlow < -1000000 && (
                <span className="flex items-center gap-1 text-[10px] text-red-400">
                  <AlertTriangle className="w-3 h-3" /> Distribution warning
                </span>
              )}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
