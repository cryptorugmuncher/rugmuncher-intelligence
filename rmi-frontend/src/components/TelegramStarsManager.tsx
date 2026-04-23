import { useState } from 'react';
import { Star, MessageSquare, Wallet, ArrowRightLeft, TrendingUp, Gift, ShoppingCart, Users, CreditCard, CheckCircle2, Clock, AlertCircle, ExternalLink, BarChart3, Download, Plus, Settings, Receipt, Zap, Bot, Shield, ChevronDown, Filter, RefreshCw } from 'lucide-react';
import { useAppStore } from '../store/appStore';

interface StarsTransaction {
  id: string;
  type: 'incoming' | 'outgoing' | 'withdrawal';
  amount: number;
  userId: string;
  userName: string;
  product: string;
  status: 'completed' | 'pending' | 'failed';
  timestamp: string;
  telegramPaymentId?: string;
  convertedTo?: 'usdc' | 'eth' | 'crm';
  conversionRate?: number;
}

interface StarsProduct {
  id: string;
  name: string;
  description: string;
  priceStars: number;
  priceUsd: number;
  category: 'subscription' | 'digital_goods' | 'premium_feature' | 'donation';
  status: 'active' | 'paused';
  totalSales: number;
  revenueStars: number;
  telegramBotEnabled: boolean;
}

interface StarsBalance {
  available: number;
  pending: number;
  withheld: number;
  totalEarned: number;
  totalWithdrawn: number;
  conversionRate: number; // Stars to USD
}

const mockTransactions: StarsTransaction[] = [
  {
    id: '1',
    type: 'incoming',
    amount: 500,
    userId: '123456789',
    userName: '@crypto_whale',
    product: 'Daily Intelligence Briefing - Monthly',
    status: 'completed',
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    telegramPaymentId: 'TG_PAY_001'
  },
  {
    id: '2',
    type: 'incoming',
    amount: 2500,
    userId: '987654321',
    userName: '@defi_trader',
    product: 'Rug Pull Rehab - Initial Consultation',
    status: 'completed',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    telegramPaymentId: 'TG_PAY_002',
    convertedTo: 'usdc',
    conversionRate: 0.013
  },
  {
    id: '3',
    type: 'incoming',
    amount: 1000,
    userId: '456789123',
    userName: '@nft_collector',
    product: 'MunchMaps API Access - Starter',
    status: 'completed',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString(),
    telegramPaymentId: 'TG_PAY_003'
  },
  {
    id: '4',
    type: 'withdrawal',
    amount: 5000,
    userId: 'SYSTEM',
    userName: 'Treasury Withdrawal',
    product: 'Converted to USDC',
    status: 'completed',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    convertedTo: 'usdc',
    conversionRate: 0.013
  },
  {
    id: '5',
    type: 'incoming',
    amount: 100,
    userId: '789123456',
    userName: '@anon_user',
    product: 'Support Donation',
    status: 'pending',
    timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString()
  }
];

const mockProducts: StarsProduct[] = [
  {
    id: '1',
    name: 'Daily Intelligence Briefing',
    description: 'Monthly subscription to curated crypto security news',
    priceStars: 500,
    priceUsd: 6.50,
    category: 'subscription',
    status: 'active',
    totalSales: 234,
    revenueStars: 117000,
    telegramBotEnabled: true
  },
  {
    id: '2',
    name: 'Rug Pull Rehab Consultation',
    description: 'One-on-one session with recovery specialist',
    priceStars: 2500,
    priceUsd: 32.50,
    category: 'premium_feature',
    status: 'active',
    totalSales: 45,
    revenueStars: 112500,
    telegramBotEnabled: true
  },
  {
    id: '3',
    name: 'MunchMaps API - Starter',
    description: '10,000 API calls per month',
    priceStars: 1000,
    priceUsd: 13.00,
    category: 'subscription',
    status: 'active',
    totalSales: 89,
    revenueStars: 89000,
    telegramBotEnabled: true
  },
  {
    id: '4',
    name: 'Wallet Analysis Report',
    description: 'Comprehensive wallet security analysis',
    priceStars: 2000,
    priceUsd: 26.00,
    category: 'digital_goods',
    status: 'active',
    totalSales: 67,
    revenueStars: 134000,
    telegramBotEnabled: true
  },
  {
    id: '5',
    name: 'Support the Mission',
    description: 'Optional donation to support development',
    priceStars: 100,
    priceUsd: 1.30,
    category: 'donation',
    status: 'active',
    totalSales: 456,
    revenueStars: 45600,
    telegramBotEnabled: true
  }
];

const starsBalance: StarsBalance = {
  available: 25000,
  pending: 3500,
  withheld: 0,
  totalEarned: 523456,
  totalWithdrawn: 498456,
  conversionRate: 0.013
};

export default function TelegramStarsManager() {
  const { theme } = useAppStore();
  const darkMode = theme === 'dark';

  const [activeTab, setActiveTab] = useState<'overview' | 'transactions' | 'products' | 'withdrawal'>('overview');
  const [transactions] = useState<StarsTransaction[]>(mockTransactions);
  const [products] = useState<StarsProduct[]>(mockProducts);
  const [filterType, setFilterType] = useState<string>('all');
  const [withdrawalAmount, setWithdrawalAmount] = useState('');

  const stats = {
    availableUsd: starsBalance.available * starsBalance.conversionRate,
    totalRevenue: starsBalance.totalEarned * starsBalance.conversionRate,
    monthlyGrowth: 23.5,
    activeProducts: products.filter(p => p.status === 'active').length
  };

  const filteredTransactions = filterType === 'all'
    ? transactions
    : transactions.filter(t => t.type === filterType);

  const formatTimeAgo = (timestamp: string) => {
    const diff = Date.now() - new Date(timestamp).getTime();
    const minutes = Math.floor(diff / 60000);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
        <div className="flex items-center gap-3 mb-2">
          <Star className="w-8 h-8 text-yellow-400 fill-yellow-400" />
          <h1 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
            TELEGRAM STARS CENTER
          </h1>
          <span className="px-2 py-1 bg-yellow-500/10 text-yellow-400 text-xs font-mono rounded">
            TON PAYMENTS
          </span>
        </div>
        <p className={`${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
          Manage Telegram Stars payments for Telegram-based products only. Stars are Telegram's native currency for bot and mini app payments within the Telegram ecosystem.
        </p>

        {/* Important Notice */}
        <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg flex items-start gap-2">
          <Bot className="w-5 h-5 text-blue-400 mt-0.5" />
          <p className="text-sm text-blue-400">
            <strong>Telegram-Only:</strong> Stars can only be used for purchases made through Telegram bots and mini apps. For web-based products, use Payment Center (Stripe/Crypto).
          </p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="flex items-center gap-2 mb-1">
            <Star className="w-4 h-4 text-yellow-400" />
            <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Available</span>
          </div>
          <p className="text-2xl font-bold text-yellow-400">{starsBalance.available.toLocaleString()}</p>
          <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>≈ ${stats.availableUsd.toFixed(2)} USD</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="flex items-center gap-2 mb-1">
            <Clock className="w-4 h-4 text-blue-400" />
            <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Pending</span>
          </div>
          <p className="text-2xl font-bold text-blue-400">{starsBalance.pending.toLocaleString()}</p>
          <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>Clearing in ~14 days</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp className="w-4 h-4 text-green-400" />
            <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Total Earned</span>
          </div>
          <p className="text-2xl font-bold text-green-400">{(starsBalance.totalEarned / 1000).toFixed(1)}K</p>
          <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>≈ ${stats.totalRevenue.toFixed(0)} USD</p>
        </div>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="flex items-center gap-2 mb-1">
            <ShoppingCart className="w-4 h-4 text-purple-400" />
            <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Products</span>
          </div>
          <p className="text-2xl font-bold text-purple-400">{stats.activeProducts}</p>
          <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>Active listings</p>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex flex-wrap gap-2">
        {[
          { id: 'overview', label: 'Overview', icon: Star },
          { id: 'transactions', label: 'Transactions', icon: Receipt },
          { id: 'products', label: 'Products', icon: ShoppingCart },
          { id: 'withdrawal', label: 'Withdraw', icon: ArrowRightLeft }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
              activeTab === tab.id
                ? 'bg-yellow-500 text-black'
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
          <div className="lg:col-span-2 space-y-4">
            <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Recent Stars Transactions
              </h3>
              <div className="space-y-3">
                {transactions.slice(0, 5).map(tx => (
                  <div key={tx.id} className={`p-3 rounded-lg ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'} flex items-center justify-between`}>
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded ${tx.type === 'incoming' ? 'bg-green-500/20' : 'bg-blue-500/20'}`}>
                        {tx.type === 'incoming' ? <Star className="w-4 h-4 text-green-400" /> : <ArrowRightLeft className="w-4 h-4 text-blue-400" />}
                      </div>
                      <div>
                        <p className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>{tx.product}</p>
                        <p className="text-sm text-slate-500">{tx.userName} • {formatTimeAgo(tx.timestamp)}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`font-bold ${tx.type === 'incoming' ? 'text-green-400' : 'text-blue-400'}`}>
                        {tx.type === 'incoming' ? '+' : '-'}{tx.amount.toLocaleString()} ⭐
                      </p>
                      <span className={`text-xs px-2 py-0.5 rounded ${
                        tx.status === 'completed' ? 'bg-green-500/10 text-green-400' :
                        tx.status === 'pending' ? 'bg-yellow-500/10 text-yellow-400' :
                        'bg-red-500/10 text-red-400'
                      }`}>
                        {tx.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Top Selling Products
              </h3>
              <div className="grid sm:grid-cols-2 gap-4">
                {products.slice(0, 4).map(product => (
                  <div key={product.id} className={`p-4 rounded-lg ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                    <div className="flex items-center justify-between mb-2">
                      <h4 className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>{product.name}</h4>
                      <span className="text-yellow-400 font-bold">{product.priceStars} ⭐</span>
                    </div>
                    <p className="text-sm text-slate-500 mb-2">{product.description.slice(0, 40)}...</p>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-green-400">{product.totalSales} sales</span>
                      <span className="text-slate-400">${product.priceUsd}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Quick Actions
              </h3>
              <div className="space-y-2">
                <button
                  onClick={() => setActiveTab('withdrawal')}
                  className="w-full py-2 bg-yellow-500 hover:bg-yellow-600 text-black rounded-lg flex items-center justify-center gap-2 font-medium"
                >
                  <ArrowRightLeft className="w-4 h-4" />
                  Withdraw Stars
                </button>
                <button
                  onClick={() => setActiveTab('products')}
                  className="w-full py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg flex items-center justify-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  New Product
                </button>
                <button className="w-full py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg flex items-center justify-center gap-2">
                  <Bot className="w-4 h-4" />
                  Bot Settings
                </button>
              </div>
            </div>

            <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Exchange Rate
              </h3>
              <div className="text-center">
                <p className="text-3xl font-bold text-yellow-400">1000 ⭐</p>
                <p className="text-lg text-slate-400">≈ $13.00 USD</p>
                <p className="text-sm text-slate-500 mt-2">Rate: 1 Star = ${starsBalance.conversionRate}</p>
              </div>
            </div>

            <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <MessageSquare className="w-5 h-5 text-white" />
                <span className="text-white font-medium">Telegram Integration</span>
              </div>
              <p className="text-blue-200 text-sm">Bot is active and processing Stars payments in real-time.</p>
            </div>
          </div>
        </div>
      )}

      {/* Transactions Tab */}
      {activeTab === 'transactions' && (
        <div className={`rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
          <div className="p-4 border-b border-slate-700/50">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                All Stars Transactions
              </h3>
              <div className="flex gap-2">
                <select
                  value={filterType}
                  onChange={e => setFilterType(e.target.value)}
                  className={`px-3 py-2 rounded-lg border ${darkMode ? 'bg-slate-900 border-slate-700 text-white' : 'bg-white border-slate-300'}`}
                >
                  <option value="all">All Types</option>
                  <option value="incoming">Incoming</option>
                  <option value="outgoing">Outgoing</option>
                  <option value="withdrawal">Withdrawals</option>
                </select>
                <button className="flex items-center gap-2 px-3 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600">
                  <Download className="w-4 h-4" />
                  Export
                </button>
              </div>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className={`${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                <tr>
                  <th className="text-left p-4 text-sm font-medium text-slate-400">Transaction</th>
                  <th className="text-left p-4 text-sm font-medium text-slate-400">User</th>
                  <th className="text-right p-4 text-sm font-medium text-slate-400">Amount</th>
                  <th className="text-center p-4 text-sm font-medium text-slate-400">Status</th>
                  <th className="text-right p-4 text-sm font-medium text-slate-400">Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/30">
                {filteredTransactions.map(tx => (
                  <tr key={tx.id} className="hover:bg-slate-700/10">
                    <td className="p-4">
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded ${tx.type === 'incoming' ? 'bg-green-500/20' : 'bg-blue-500/20'}`}>
                          {tx.type === 'incoming' ? <Star className="w-4 h-4 text-green-400" /> : <ArrowRightLeft className="w-4 h-4 text-blue-400" />}
                        </div>
                        <div>
                          <p className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>{tx.product}</p>
                          {tx.convertedTo && (
                            <p className="text-xs text-slate-500">Converted to {tx.convertedTo.toUpperCase()}</p>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <span className={`${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>{tx.userName}</span>
                    </td>
                    <td className="p-4 text-right">
                      <span className={`font-bold ${tx.type === 'incoming' ? 'text-green-400' : 'text-blue-400'}`}>
                        {tx.type === 'incoming' ? '+' : '-'}{tx.amount.toLocaleString()} ⭐
                      </span>
                    </td>
                    <td className="p-4 text-center">
                      <span className={`px-2 py-1 rounded text-xs ${
                        tx.status === 'completed' ? 'bg-green-500/10 text-green-400' :
                        tx.status === 'pending' ? 'bg-yellow-500/10 text-yellow-400' :
                        'bg-red-500/10 text-red-400'
                      }`}>
                        {tx.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                        {formatTimeAgo(tx.timestamp)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Products Tab */}
      {activeTab === 'products' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              Stars Products & Pricing
            </h3>
            <button className="flex items-center gap-2 px-4 py-2 bg-yellow-500 text-black rounded-lg hover:bg-yellow-600 font-medium">
              <Plus className="w-4 h-4" />
              Add Product
            </button>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {products.map(product => (
              <div key={product.id} className={`p-6 rounded-lg ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h4 className={`font-semibold text-lg ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                      {product.name}
                    </h4>
                    <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                      {product.description}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-yellow-400">{product.priceStars} ⭐</p>
                    <p className="text-sm text-slate-500">≈ ${product.priceUsd}</p>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div className="text-center p-2 rounded bg-slate-900/30">
                    <p className="font-bold text-white">{product.totalSales}</p>
                    <p className="text-xs text-slate-500">Sales</p>
                  </div>
                  <div className="text-center p-2 rounded bg-slate-900/30">
                    <p className="font-bold text-green-400">{(product.revenueStars / 1000).toFixed(1)}K</p>
                    <p className="text-xs text-slate-500">Revenue</p>
                  </div>
                  <div className="text-center p-2 rounded bg-slate-900/30">
                    <p className="font-bold text-blue-400">{product.category}</p>
                    <p className="text-xs text-slate-500">Type</p>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-slate-700/30">
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${product.status === 'active' ? 'bg-green-400' : 'bg-slate-400'}`} />
                    <span className="text-sm text-slate-400">{product.status}</span>
                    {product.telegramBotEnabled && (
                      <span className="text-xs px-2 py-0.5 bg-blue-500/10 text-blue-400 rounded">
                        BOT ENABLED
                      </span>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <button className="px-3 py-1.5 text-sm bg-slate-700 text-white rounded hover:bg-slate-600">
                      Edit
                    </button>
                    <button className="px-3 py-1.5 text-sm bg-slate-700 text-white rounded hover:bg-slate-600">
                      <ExternalLink className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Withdrawal Tab */}
      {activeTab === 'withdrawal' && (
        <div className="grid md:grid-cols-2 gap-6">
          <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
            <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              Withdraw Stars
            </h3>
            <p className={`text-sm mb-6 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
              Convert your Stars to cryptocurrency or fiat. Withdrawals typically process within 24-48 hours.
            </p>

            <div className="space-y-4">
              <div>
                <label className={`block text-sm mb-2 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                  Amount to Withdraw (Stars)
                </label>
                <input
                  type="number"
                  value={withdrawalAmount}
                  onChange={(e) => setWithdrawalAmount(e.target.value)}
                  placeholder={`Max: ${starsBalance.available.toLocaleString()}`}
                  max={starsBalance.available}
                  className={`w-full px-4 py-3 rounded-lg border ${darkMode ? 'bg-slate-900 border-slate-700 text-white' : 'bg-white border-slate-300'}`}
                />
                <p className="text-sm text-slate-500 mt-1">
                  ≈ ${(parseInt(withdrawalAmount || '0') * starsBalance.conversionRate).toFixed(2)} USD
                </p>
              </div>

              <div>
                <label className={`block text-sm mb-2 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                  Withdrawal Method
                </label>
                <div className="space-y-2">
                  <button className="w-full p-3 rounded-lg border border-green-500/30 bg-green-500/10 flex items-center gap-3">
                    <Wallet className="w-5 h-5 text-green-400" />
                    <div className="text-left">
                      <p className="font-medium text-white">USDC (Base/Ethereum)</p>
                      <p className="text-sm text-slate-400">Conversion rate: 1 ⭐ = ${starsBalance.conversionRate}</p>
                    </div>
                    <CheckCircle2 className="w-5 h-5 text-green-400 ml-auto" />
                  </button>
                  <button className="w-full p-3 rounded-lg border border-slate-700 bg-slate-900/30 flex items-center gap-3 opacity-50">
                    <CreditCard className="w-5 h-5 text-slate-400" />
                    <div className="text-left">
                      <p className="font-medium text-slate-400">Bank Transfer</p>
                      <p className="text-sm text-slate-500">Coming soon</p>
                    </div>
                  </button>
                </div>
              </div>

              <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
                <div className="flex items-start gap-2">
                  <AlertCircle className="w-5 h-5 text-yellow-400 mt-0.5" />
                  <div>
                    <p className="text-sm text-yellow-400 font-medium">Withdrawal Information</p>
                    <ul className="text-sm text-slate-400 mt-1 space-y-1">
                      <li>• Minimum withdrawal: 1000 Stars</li>
                      <li>• Processing time: 24-48 hours</li>
                      <li>• Gas fees deducted from amount</li>
                      <li>• Must use whitelisted wallet</li>
                    </ul>
                  </div>
                </div>
              </div>

              <button className="w-full py-3 bg-yellow-500 hover:bg-yellow-600 text-black rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed" disabled={!withdrawalAmount || parseInt(withdrawalAmount) < 1000}>
                Request Withdrawal
              </button>
            </div>
          </div>

          <div className="space-y-4">
            <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Balance Breakdown
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 rounded bg-slate-900/30">
                  <span className="text-slate-400">Available</span>
                  <span className="font-bold text-white">{starsBalance.available.toLocaleString()} ⭐</span>
                </div>
                <div className="flex justify-between items-center p-3 rounded bg-slate-900/30">
                  <span className="text-slate-400">Pending Clearance</span>
                  <span className="font-bold text-blue-400">{starsBalance.pending.toLocaleString()} ⭐</span>
                </div>
                <div className="flex justify-between items-center p-3 rounded bg-slate-900/30">
                  <span className="text-slate-400">Withheld</span>
                  <span className="font-bold text-red-400">{starsBalance.withheld.toLocaleString()} ⭐</span>
                </div>
                <div className="border-t border-slate-700 pt-3 flex justify-between items-center">
                  <span className="font-medium text-white">Total Balance</span>
                  <span className="font-bold text-yellow-400">
                    {(starsBalance.available + starsBalance.pending).toLocaleString()} ⭐
                  </span>
                </div>
              </div>
            </div>

            <div className={`rounded-lg p-6 ${darkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-slate-200'}`}>
              <h3 className={`font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Withdrawal History
              </h3>
              <div className="space-y-3">
                <div className="p-3 rounded bg-slate-900/30">
                  <div className="flex justify-between">
                    <span className="text-sm text-white">5,000 ⭐ → USDC</span>
                    <span className="text-xs text-green-400">Completed</span>
                  </div>
                  <p className="text-xs text-slate-500">Apr 13, 2026 • $65.00</p>
                </div>
                <div className="p-3 rounded bg-slate-900/30">
                  <div className="flex justify-between">
                    <span className="text-sm text-white">10,000 ⭐ → USDC</span>
                    <span className="text-xs text-green-400">Completed</span>
                  </div>
                  <p className="text-xs text-slate-500">Mar 28, 2026 • $130.00</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
