import { useState } from 'react';
import { Vault, Coins, TrendingUp, TrendingDown, ArrowRightLeft, Wallet, PieChart, BarChart3, ExternalLink, RefreshCw, Plus, AlertTriangle, CheckCircle2, Clock, Shield, Lock, Unlock, History, Target, Zap } from 'lucide-react';
import { useAppStore } from '../store/appStore';

interface TreasuryAsset {
  id: string;
  token: string;
  symbol: string;
  chain: string;
  balance: number;
  priceUsd: number;
  valueUsd: number;
  allocation: number; // percentage of total
  change24h: number;
  type: 'native' | 'stablecoin' | 'governance' | 'investment' | 'yield';
  wallet: string;
  acquiredAt: string;
  costBasis?: number;
  unrealizedPnl?: number;
  tags: string[];
}

interface TreasuryTransaction {
  id: string;
  type: 'inflow' | 'outflow' | 'swap' | 'yield' | 'expense';
  asset: string;
  amount: number;
  valueUsd: number;
  timestamp: string;
  description: string;
  txHash: string;
  counterparty?: string;
  category: 'operations' | 'marketing' | 'development' | 'investment' | 'revenue' | 'grant';
}

const mockAssets: TreasuryAsset[] = [
  {
    id: '1',
    token: 'Ethereum',
    symbol: 'ETH',
    chain: 'Ethereum',
    balance: 45.5,
    priceUsd: 3250.00,
    valueUsd: 147875.00,
    allocation: 35.2,
    change24h: 2.3,
    type: 'native',
    wallet: '0x742d35Cc6634C0532925a3b8D4B9db96590f6C7E',
    acquiredAt: '2026-01-15',
    costBasis: 2800.00,
    unrealizedPnl: 20475.00,
    tags: ['primary', 'operational']
  },
  {
    id: '2',
    token: 'USD Coin',
    symbol: 'USDC',
    chain: 'Base',
    balance: 125000.00,
    priceUsd: 1.00,
    valueUsd: 125000.00,
    allocation: 29.7,
    change24h: 0.01,
    type: 'stablecoin',
    wallet: '0x742d35Cc6634C0532925a3b8D4B9db96590f6C7E',
    acquiredAt: '2026-03-01',
    tags: ['stable', 'operational']
  },
  {
    id: '3',
    token: 'Arbitrum',
    symbol: 'ARB',
    chain: 'Arbitrum',
    balance: 25000.00,
    priceUsd: 0.85,
    valueUsd: 21250.00,
    allocation: 5.1,
    change24h: -1.2,
    type: 'governance',
    wallet: '0x742d35Cc6634C0532925a3b8D4B9db96590f6C7E',
    acquiredAt: '2026-02-10',
    costBasis: 1.20,
    unrealizedPnl: -8750.00,
    tags: ['dao', 'voting']
  },
  {
    id: '4',
    token: 'Wrapped Bitcoin',
    symbol: 'WBTC',
    chain: 'Ethereum',
    balance: 0.75,
    priceUsd: 87500.00,
    valueUsd: 65625.00,
    allocation: 15.6,
    change24h: 1.8,
    type: 'investment',
    wallet: '0x742d35Cc6634C0532925a3b8D4B9db96590f6C7E',
    acquiredAt: '2026-01-20',
    costBasis: 80000.00,
    unrealizedPnl: 5625.00,
    tags: ['bitcoin', 'hedge']
  },
  {
    id: '5',
    token: 'Rug Munch Intel',
    symbol: 'CRM',
    chain: 'Ethereum',
    balance: 2500000.00,
    priceUsd: 0.015,
    valueUsd: 37500.00,
    allocation: 8.9,
    change24h: 5.2,
    type: 'governance',
    wallet: '0x742d35Cc6634C0532925a3b8D4B9db96590f6C7E',
    acquiredAt: '2025-11-01',
    costBasis: 0.001,
    unrealizedPnl: 35000.00,
    tags: ['treasury', 'v2-reserve']
  },
  {
    id: '6',
    token: 'Aave USDC',
    symbol: 'aUSDC',
    chain: 'Ethereum',
    balance: 50000.00,
    priceUsd: 1.02,
    valueUsd: 51000.00,
    allocation: 5.5,
    change24h: 0.05,
    type: 'yield',
    wallet: '0x742d35Cc6634C0532925a3b8D4B9db96590f6C7E',
    acquiredAt: '2026-03-15',
    tags: ['yield', 'aave', 'earning']
  }
];

const mockTransactions: TreasuryTransaction[] = [
  {
    id: '1',
    type: 'expense',
    asset: 'USDC',
    amount: 5000.00,
    valueUsd: 5000.00,
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    description: 'Server infrastructure payment - AWS',
    txHash: '0xabc123...',
    category: 'operations'
  },
  {
    id: '2',
    type: 'yield',
    asset: 'aUSDC',
    amount: 125.50,
    valueUsd: 128.01,
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
    description: 'Aave yield accrual',
    txHash: '0xdef456...',
    category: 'revenue'
  },
  {
    id: '3',
    type: 'inflow',
    asset: 'ETH',
    amount: 2.5,
    valueUsd: 8125.00,
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 72).toISOString(),
    description: 'Base Ecosystem Grant - First Tranche',
    txHash: '0xghi789...',
    counterparty: 'Base Ecosystem Fund',
    category: 'grant'
  },
  {
    id: '4',
    type: 'expense',
    asset: 'USDC',
    amount: 8500.00,
    valueUsd: 8500.00,
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 96).toISOString(),
    description: 'Smart contract audit - CertiK',
    txHash: '0xjkl012...',
    category: 'development'
  },
  {
    id: '5',
    type: 'swap',
    asset: 'ETH',
    amount: 5.0,
    valueUsd: 16250.00,
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 120).toISOString(),
    description: 'Converted ETH to USDC for operational runway',
    txHash: '0xmno345...',
    category: 'operations'
  }
];

const chainIcons: Record<string, string> = {
  'Ethereum': '🔷',
  'Base': '🔵',
  'Arbitrum': '🔶',
  'Polygon': '💜',
  'BSC': '🟡',
  'Solana': '🟪'
};

export default function ProjectTreasury() {
  const { theme } = useAppStore();
  const darkMode = theme === 'dark';

  const [assets] = useState<TreasuryAsset[]>(mockAssets);
  const [transactions] = useState<TreasuryTransaction[]>(mockTransactions);
  const [activeTab, setActiveTab] = useState<'overview' | 'holdings' | 'transactions' | 'allocations' | 'yield'>('overview');
  const [filterType, setFilterType] = useState<string>('all');

  const totalValue = assets.reduce((acc, asset) => acc + asset.valueUsd, 0);
  const totalChange24h = assets.reduce((acc, asset) => acc + (asset.valueUsd * asset.change24h / 100), 0);
  const totalChangePercent = (totalChange24h / totalValue) * 100;
  const totalUnrealizedPnl = assets.reduce((acc, asset) => acc + (asset.unrealizedPnl || 0), 0);

  // Calculate allocation by type
  const allocationByType = assets.reduce((acc, asset) => {
    acc[asset.type] = (acc[asset.type] || 0) + asset.valueUsd;
    return acc;
  }, {} as Record<string, number>);

  const filteredAssets = filterType === 'all'
    ? assets
    : assets.filter(a => a.type === filterType);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const formatTimeAgo = (timestamp: string) => {
    const diff = Date.now() - new Date(timestamp).getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
        <div className="flex items-center gap-3 mb-2">
          <Vault className="w-8 h-8 text-purple-500" />
          <h1 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
            PROJECT TREASURY
          </h1>
          <span className="px-2 py-1 bg-purple-500/10 text-purple-400 text-xs font-mono rounded">
            TREASURY CONTROL
          </span>
          <Shield className="w-5 h-5 text-green-400 ml-2" />
        </div>
        <p className={`${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
          Comprehensive view of all project token holdings across wallets and chains. Multi-sig protected.
        </p>
      </div>

      {/* Treasury Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Total Treasury Value</p>
          <p className="text-2xl font-bold text-white">{formatCurrency(totalValue)}</p>
          <div className={`flex items-center gap-1 text-sm ${totalChangePercent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {totalChangePercent >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
            {totalChangePercent >= 0 ? '+' : ''}{totalChangePercent.toFixed(2)}% (24h)
          </div>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Unrealized P&L</p>
          <p className={`text-2xl font-bold ${totalUnrealizedPnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {totalUnrealizedPnl >= 0 ? '+' : ''}{formatCurrency(totalUnrealizedPnl)}
          </p>
          <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>Since acquisition</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Asset Count</p>
          <p className="text-2xl font-bold text-purple-400">{assets.length}</p>
          <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>Across {Object.keys(chainIcons).length} chains</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Est. Monthly Yield</p>
          <p className="text-2xl font-bold text-green-400">{formatCurrency(2100)}</p>
          <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>From aUSDC, staked positions</p>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex flex-wrap gap-2">
        {[
          { id: 'overview', label: 'Treasury Overview', icon: Vault },
          { id: 'holdings', label: 'All Holdings', icon: Wallet },
          { id: 'transactions', label: 'Transaction Log', icon: History },
          { id: 'allocations', label: 'Allocation Strategy', icon: PieChart },
          { id: 'yield', label: 'Yield Management', icon: TrendingUp }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
              activeTab === tab.id
                ? 'bg-purple-600 text-white'
                : darkMode
                ? 'bg-slate-800 text-slate-400 hover:text-white'
                : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-200'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Main Holdings */}
          <div className="lg:col-span-2 space-y-4">
            <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Top Holdings
              </h3>
              <div className="space-y-3">
                {assets.slice(0, 5).map(asset => (
                  <div key={asset.id} className="flex items-center justify-between p-3 rounded-lg bg-slate-900/30">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{chainIcons[asset.chain]}</span>
                      <div>
                        <p className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                          {asset.token} ({asset.symbol})
                        </p>
                        <p className="text-sm text-slate-500">{asset.balance.toLocaleString()} tokens</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-white">{formatCurrency(asset.valueUsd)}</p>
                      <p className={`text-sm ${asset.change24h >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {asset.change24h >= 0 ? '+' : ''}{asset.change24h}% (24h)
                      </p>
                    </div>
                  </div>
                ))}
              </div>
              <button
                onClick={() => setActiveTab('holdings')}
                className="w-full mt-4 py-2 text-center text-purple-400 hover:text-purple-300 text-sm"
              >
                View All Holdings →
              </button>
            </div>

            {/* Recent Transactions */}
            <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Recent Treasury Activity
              </h3>
              <div className="space-y-3">
                {transactions.slice(0, 4).map(tx => (
                  <div key={tx.id} className="flex items-center justify-between p-3 rounded-lg bg-slate-900/30">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded ${
                        tx.type === 'inflow' ? 'bg-green-500/20' :
                        tx.type === 'outflow' || tx.type === 'expense' ? 'bg-red-500/20' :
                        'bg-blue-500/20'
                      }`}>
                        {tx.type === 'inflow' ? <TrendingUp className="w-4 h-4 text-green-400" /> :
                         tx.type === 'outflow' || tx.type === 'expense' ? <TrendingDown className="w-4 h-4 text-red-400" /> :
                         <ArrowRightLeft className="w-4 h-4 text-blue-400" />}
                      </div>
                      <div>
                        <p className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                          {tx.description}
                        </p>
                        <p className="text-sm text-slate-500">{formatTimeAgo(tx.timestamp)}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`font-medium ${
                        tx.type === 'inflow' || tx.type === 'yield' ? 'text-green-400' :
                        tx.type === 'outflow' || tx.type === 'expense' ? 'text-red-400' :
                        'text-blue-400'
                      }`}>
                        {tx.type === 'inflow' || tx.type === 'yield' ? '+' : '-'}{formatCurrency(tx.valueUsd)}
                      </p>
                      <p className="text-xs text-slate-500">{tx.category}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-4">
            {/* Quick Actions */}
            <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Treasury Actions
              </h3>
              <div className="space-y-2">
                <button className="w-full py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg flex items-center justify-center gap-2">
                  <ArrowRightLeft className="w-4 h-4" />
                  Rebalance Portfolio
                </button>
                <button className="w-full py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg flex items-center justify-center gap-2">
                  <Target className="w-4 h-4" />
                  Set Allocation Targets
                </button>
                <button className="w-full py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg flex items-center justify-center gap-2">
                  <ExternalLink className="w-4 h-4" />
                  View Multi-sig
                </button>
              </div>
            </div>

            {/* Allocation Summary */}
            <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                By Asset Type
              </h3>
              <div className="space-y-3">
                {Object.entries(allocationByType).map(([type, value]) => {
                  const percentage = ((value / totalValue) * 100).toFixed(1);
                  const colors: Record<string, string> = {
                    native: 'bg-blue-500',
                    stablecoin: 'bg-green-500',
                    governance: 'bg-purple-500',
                    investment: 'bg-yellow-500',
                    yield: 'bg-orange-500'
                  };
                  return (
                    <div key={type}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className={`capitalize ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                          {type}
                        </span>
                        <span className="text-slate-400">{percentage}%</span>
                      </div>
                      <div className={`h-2 rounded-full ${darkMode ? 'bg-slate-700' : 'bg-slate-200'}`}>
                        <div className={`h-full rounded-full ${colors[type] || 'bg-slate-500'}`} style={{ width: `${percentage}%` }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Alerts */}
            <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Treasury Alerts
              </h3>
              <div className="space-y-2">
                <div className="flex items-center gap-2 p-2 rounded bg-yellow-500/10 text-yellow-400 text-sm">
                  <AlertTriangle className="w-4 h-4" />
                  <span>ARB position down 25% from cost</span>
                </div>
                <div className="flex items-center gap-2 p-2 rounded bg-green-500/10 text-green-400 text-sm">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Base Grant received</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Holdings Tab */}
      {activeTab === 'holdings' && (
        <div className={`rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="p-4 border-b border-slate-700/50">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                All Treasury Holdings
              </h3>
              <select
                value={filterType}
                onChange={e => setFilterType(e.target.value)}
                className={`px-3 py-2 rounded-lg border ${darkMode ? 'bg-slate-900 border-slate-700 text-white' : 'bg-white border-slate-300'}`}
              >
                <option value="all">All Types</option>
                <option value="native">Native Tokens</option>
                <option value="stablecoin">Stablecoins</option>
                <option value="governance">Governance</option>
                <option value="investment">Investments</option>
                <option value="yield">Yield-bearing</option>
              </select>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className={`${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                <tr>
                  <th className="text-left p-4 text-sm font-medium text-slate-400">Asset</th>
                  <th className="text-left p-4 text-sm font-medium text-slate-400">Chain</th>
                  <th className="text-right p-4 text-sm font-medium text-slate-400">Balance</th>
                  <th className="text-right p-4 text-sm font-medium text-slate-400">Price</th>
                  <th className="text-right p-4 text-sm font-medium text-slate-400">Value</th>
                  <th className="text-right p-4 text-sm font-medium text-slate-400">Allocation</th>
                  <th className="text-right p-4 text-sm font-medium text-slate-400">24h Change</th>
                  <th className="text-right p-4 text-sm font-medium text-slate-400">P&L</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/30">
                {filteredAssets.map(asset => (
                  <tr key={asset.id} className="hover:bg-slate-700/10">
                    <td className="p-4">
                      <div className="flex items-center gap-3">
                        <span className="text-xl">{chainIcons[asset.chain]}</span>
                        <div>
                          <p className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>{asset.token}</p>
                          <p className="text-sm text-slate-500">{asset.symbol}</p>
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>{asset.chain}</span>
                    </td>
                    <td className="p-4 text-right">
                      <span className={`${darkMode ? 'text-white' : 'text-slate-900'}`}>
                        {asset.balance.toLocaleString()}
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      <span className={`${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                        ${asset.priceUsd.toFixed(2)}
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      <span className="font-medium text-white">{formatCurrency(asset.valueUsd)}</span>
                    </td>
                    <td className="p-4 text-right">
                      <span className={`${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                        {asset.allocation.toFixed(1)}%
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      <span className={asset.change24h >= 0 ? 'text-green-400' : 'text-red-400'}>
                        {asset.change24h >= 0 ? '+' : ''}{asset.change24h}%
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      {asset.unrealizedPnl !== undefined ? (
                        <span className={asset.unrealizedPnl >= 0 ? 'text-green-400' : 'text-red-400'}>
                          {asset.unrealizedPnl >= 0 ? '+' : ''}{formatCurrency(asset.unrealizedPnl)}
                        </span>
                      ) : (
                        <span className="text-slate-500">-</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Transactions Tab */}
      {activeTab === 'transactions' && (
        <div className={`rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="p-4 border-b border-slate-700/50">
            <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              Treasury Transaction Log
            </h3>
          </div>
          <div className="divide-y divide-slate-700/30">
            {transactions.map(tx => (
              <div key={tx.id} className="p-4 hover:bg-slate-700/10">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <div className={`p-2 rounded ${
                      tx.type === 'inflow' ? 'bg-green-500/20' :
                      tx.type === 'outflow' || tx.type === 'expense' ? 'bg-red-500/20' :
                      'bg-blue-500/20'
                    }`}>
                      {tx.type === 'inflow' ? <TrendingUp className="w-5 h-5 text-green-400" /> :
                       tx.type === 'outflow' || tx.type === 'expense' ? <TrendingDown className="w-5 h-5 text-red-400" /> :
                       tx.type === 'yield' ? <Zap className="w-5 h-5 text-yellow-400" /> :
                       <ArrowRightLeft className="w-5 h-5 text-blue-400" />}
                    </div>
                    <div>
                      <p className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>{tx.description}</p>
                      <div className="flex items-center gap-3 mt-1 text-sm">
                        <span className={`px-2 py-0.5 rounded text-xs ${
                          tx.type === 'inflow' ? 'bg-green-500/10 text-green-400' :
                          tx.type === 'outflow' || tx.type === 'expense' ? 'bg-red-500/10 text-red-400' :
                          'bg-blue-500/10 text-blue-400'
                        }`}>
                          {tx.type.toUpperCase()}
                        </span>
                        <span className={darkMode ? 'text-slate-500' : 'text-slate-500'}>{tx.category}</span>
                        <span className={darkMode ? 'text-slate-500' : 'text-slate-500'}>{formatTimeAgo(tx.timestamp)}</span>
                        {tx.counterparty && (
                          <span className="text-purple-400">From: {tx.counterparty}</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`font-semibold ${
                      tx.type === 'inflow' || tx.type === 'yield' ? 'text-green-400' :
                      tx.type === 'outflow' || tx.type === 'expense' ? 'text-red-400' :
                      'text-blue-400'
                    }`}>
                      {tx.type === 'inflow' || tx.type === 'yield' ? '+' : '-'}{formatCurrency(tx.valueUsd)}
                    </p>
                    <p className="text-sm text-slate-500">{tx.amount} {tx.asset}</p>
                    <a href={`https://etherscan.io/tx/${tx.txHash}`} target="_blank" rel="noopener noreferrer" className="text-xs text-purple-400 hover:text-purple-300">
                      View Tx
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Other tabs placeholder */}
      {(activeTab === 'allocations' || activeTab === 'yield') && (
        <div className={`p-12 text-center rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <BarChart3 className="w-12 h-12 text-slate-500 mx-auto mb-4" />
          <p className={`text-lg font-medium ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
            {activeTab === 'allocations' ? 'Allocation Strategy' : 'Yield Management'} Dashboard
          </p>
          <p className={`text-sm ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>
            Advanced portfolio optimization tools coming soon
          </p>
        </div>
      )}
    </div>
  );
}
