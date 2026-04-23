/**
 * Revenue Dashboard
 * Subscription tracking, crypto payments, financial reports
 */
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { db } from '../../services/supabase';
import {
  TrendingUp,
  TrendingDown,
  CreditCard,
  Bitcoin,
  Calendar,
  Download,
  Activity,
  Crown,
  Star,
  Shield,
} from 'lucide-react';

const CRYPTO_OPTIONS = [
  { id: 'ETH', name: 'Ethereum', icon: 'Ξ', color: '#627EEA' },
  { id: 'BTC', name: 'Bitcoin', icon: '₿', color: '#F7931A' },
  { id: 'USDC', name: 'USD Coin', icon: 'U', color: '#2775CA' },
  { id: 'USDT', name: 'Tether', icon: 'T', color: '#26A17B' },
];

const TIERS = ['FREE', 'BASIC', 'PRO', 'ELITE', 'ENTERPRISE'];

export default function RevenueDashboard() {
  const [dateRange, setDateRange] = useState('30d');
  const [activeTab, setActiveTab] = useState<'overview' | 'subscriptions' | 'payments' | 'reports'>('overview');

  // Fetch users for subscription data
  const { data: users, isLoading: _usersLoading } = useQuery({
    queryKey: ['revenue-users'],
    queryFn: async () => {
      const { data, error } = await db.users.getAll();
      if (error) throw error;
      return data || [];
    },
  });

  // Fetch payments data
  const { data: payments, isLoading: _paymentsLoading } = useQuery({
    queryKey: ['revenue-payments'],
    queryFn: async () => {
      const { data, error } = await db.payments.getAll();
      if (error) throw error;
      return data || [];
    },
  });

  // Fetch revenue stats
  const { data: revenueStats } = useQuery({
    queryKey: ['revenue-stats'],
    queryFn: async () => {
      const { data, error } = await db.payments.getStats();
      if (error) throw error;
      return data;
    },
  });

  // Calculate stats from real data
  const stats = {
    totalRevenue: revenueStats?.total_revenue_eth || 0,
    mrr: revenueStats?.mrr_eth || 0,
    subscriptions: {
      free: users?.filter((u: any) => u.tier === 'FREE' || !u.tier).length || 0,
      basic: users?.filter((u: any) => u.tier === 'BASIC').length || 0,
      pro: users?.filter((u: any) => u.tier === 'PRO').length || 0,
      elite: users?.filter((u: any) => u.tier === 'ELITE').length || 0,
      enterprise: users?.filter((u: any) => u.tier === 'ENTERPRISE').length || 0,
    },
    conversions: {
      freeToPaid: revenueStats?.free_to_paid_conversions || 0,
      upgrades: revenueStats?.upgrades || 0,
      downgrades: revenueStats?.downgrades || 0,
      churn: revenueStats?.churn_rate || 0,
    },
  };

  const totalPaidUsers = stats.subscriptions.basic + stats.subscriptions.pro + stats.subscriptions.elite + stats.subscriptions.enterprise;
  const totalUsers = stats.subscriptions.free + totalPaidUsers;
  const conversionRate = totalUsers > 0 ? ((totalPaidUsers / totalUsers) * 100).toFixed(1) : '0';

  // Recent payments from database (limit to last 10)
  const recentPayments = payments?.slice(0, 10).map((p: any) => ({
    id: p.id,
    user: p.user_email || p.user_id?.slice(0, 8) + '...',
    amount: p.amount,
    currency: p.currency || 'ETH',
    type: p.payment_type || 'Subscription',
    status: p.status || 'confirmed',
    date: new Date(p.created_at).toLocaleDateString(),
  })) || [];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'bg-green-500/20 text-green-400';
      case 'pending':
        return 'bg-yellow-500/20 text-yellow-400';
      case 'failed':
        return 'bg-red-500/20 text-red-400';
      default:
        return 'bg-gray-500/20 text-gray-400';
    }
  };

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="flex gap-2">
        {['overview', 'subscriptions', 'payments', 'reports'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as any)}
            className={`px-4 py-2 rounded-lg font-medium capitalize ${
              activeTab === tab
                ? 'bg-neon-green/20 text-neon-green border border-neon-green/50'
                : 'bg-crypto-card text-gray-400 border border-crypto-border'
            }`}
          >
            {tab.replace('_', ' ')}
          </button>
        ))}
      </div>

      {/* OVERVIEW TAB */}
      {activeTab === 'overview' && (
        <>
          {/* Main Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <RevenueCard
              title="Total Revenue (ETH)"
              value="12.45"
              change="+15.3%"
              up={true}
              icon={Bitcoin}
              color="orange"
            />
            <RevenueCard
              title="Monthly Recurring"
              value="3.2 ETH"
              change="+8.1%"
              up={true}
              icon={Calendar}
              color="blue"
            />
            <RevenueCard
              title="Paid Subscribers"
              value={totalPaidUsers}
              change={`${conversionRate}% conv.`}
              up={true}
              icon={Crown}
              color="purple"
            />
            <RevenueCard
              title="Avg Revenue/User"
              value="0.03 ETH"
              change="-2.4%"
              up={false}
              icon={Activity}
              color="cyan"
            />
          </div>

          {/* Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Revenue by Tier */}
            <div className="crypto-card">
              <h3 className="text-lg font-semibold text-white mb-4">Subscribers by Tier</h3>
              <div className="space-y-3">
                {TIERS.map((tier) => {
                  const count = stats.subscriptions[tier.toLowerCase() as keyof typeof stats.subscriptions] || 0;
                  const percentage = totalUsers > 0 ? (count / totalUsers) * 100 : 0;
                  return (
                    <div key={tier} className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-300">{tier}</span>
                        <span className="text-white">{count} users ({percentage.toFixed(1)}%)</span>
                      </div>
                      <div className="h-2 bg-crypto-dark rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            tier === 'ENTERPRISE' ? 'bg-purple-500' :
                            tier === 'ELITE' ? 'bg-yellow-500' :
                            tier === 'PRO' ? 'bg-blue-500' :
                            tier === 'BASIC' ? 'bg-green-500' :
                            'bg-gray-500'
                          }`}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Revenue Streams */}
            <div className="crypto-card">
              <h3 className="text-lg font-semibold text-white mb-4">Revenue Streams</h3>
              <div className="space-y-3">
                <RevenueStreamRow
                  name="Subscriptions"
                  amount="8.5 ETH"
                  percentage={68}
                  color="blue"
                  icon={CreditCard}
                />
                <RevenueStreamRow
                  name="Rug Pull Rehab"
                  amount="2.3 ETH"
                  percentage={18}
                  color="green"
                  icon={Shield}
                />
                <RevenueStreamRow
                  name="Snitch Rewards"
                  amount="1.2 ETH"
                  percentage={10}
                  color="yellow"
                  icon={Star}
                />
                <RevenueStreamRow
                  name="Premium Alerts"
                  amount="0.45 ETH"
                  percentage={4}
                  color="purple"
                  icon={Crown}
                />
              </div>
            </div>
          </div>

          {/* Recent Payments */}
          <div className="crypto-card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Recent Payments</h3>
              <button className="btn-secondary text-sm">View All</button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-crypto-border text-gray-400">
                    <th className="text-left p-3">User</th>
                    <th className="text-left p-3">Type</th>
                    <th className="text-left p-3">Amount</th>
                    <th className="text-left p-3">Status</th>
                    <th className="text-left p-3">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {recentPayments.map((payment) => (
                    <tr key={payment.id} className="border-b border-crypto-border">
                      <td className="p-3 text-gray-300">{payment.user}</td>
                      <td className="p-3 text-gray-300">{payment.type}</td>
                      <td className="p-3">
                        <span className="text-neon-green font-medium">
                          {payment.amount} {payment.currency}
                        </span>
                      </td>
                      <td className="p-3">
                        <span className={`px-2 py-1 rounded text-xs ${getStatusColor(payment.status)}`}>
                          {payment.status}
                        </span>
                      </td>
                      <td className="p-3 text-gray-400">{payment.date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {/* SUBSCRIPTIONS TAB */}
      {activeTab === 'subscriptions' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {TIERS.map((tier) => (
              <div key={tier} className="crypto-card text-center">
                <h4 className="text-gray-400 text-sm mb-2">{tier}</h4>
                <p className="text-3xl font-bold text-white">
                  {stats.subscriptions[tier.toLowerCase() as keyof typeof stats.subscriptions] || 0}
                </p>
                <p className="text-xs text-gray-500 mt-1">subscribers</p>
              </div>
            ))}
          </div>

          <div className="crypto-card">
            <h3 className="text-lg font-semibold text-white mb-4">Tier Configuration</h3>
            <div className="space-y-4">
              <TierConfigRow
                tier="BASIC"
                price="0.05 ETH/mo"
                features={['5 scans/day', 'Basic alerts', 'Email support']}
                subscribers={stats.subscriptions.basic}
              />
              <TierConfigRow
                tier="PRO"
                price="0.1 ETH/mo"
                features={['Unlimited scans', 'Priority alerts', 'API access', 'Discord access']}
                subscribers={stats.subscriptions.pro}
              />
              <TierConfigRow
                tier="ELITE"
                price="0.25 ETH/mo"
                features={['Everything in PRO', 'Custom investigations', 'Direct analyst access', 'White-glove support']}
                subscribers={stats.subscriptions.elite}
              />
              <TierConfigRow
                tier="ENTERPRISE"
                price="Custom"
                features={['Dedicated resources', 'SLA guarantees', 'Custom integrations', 'Priority everything']}
                subscribers={stats.subscriptions.enterprise}
              />
            </div>
          </div>
        </div>
      )}

      {/* PAYMENTS TAB */}
      {activeTab === 'payments' && (
        <div className="space-y-6">
          {/* Crypto Balances */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {CRYPTO_OPTIONS.map((crypto) => (
              <div key={crypto.id} className="crypto-card">
                <div className="flex items-center gap-2 mb-2">
                  <span
                    className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold"
                    style={{ backgroundColor: crypto.color }}
                  >
                    {crypto.icon}
                  </span>
                  <span className="text-gray-400">{crypto.name}</span>
                </div>
                <p className="text-2xl font-bold text-white">
                  {crypto.id === 'ETH' ? '12.45' : crypto.id === 'BTC' ? '0.85' : '5,240'}
                </p>
                <p className="text-xs text-gray-500">{crypto.id}</p>
              </div>
            ))}
          </div>

          {/* Payment Processing */}
          <div className="crypto-card">
            <h3 className="text-lg font-semibold text-white mb-4">Payment Processing</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-crypto-dark rounded p-4">
                <p className="text-gray-400 text-sm mb-1">Pending Confirmations</p>
                <p className="text-2xl font-bold text-yellow-400">3</p>
              </div>
              <div className="bg-crypto-dark rounded p-4">
                <p className="text-gray-400 text-sm mb-1">Failed Payments</p>
                <p className="text-2xl font-bold text-red-400">1</p>
              </div>
              <div className="bg-crypto-dark rounded p-4">
                <p className="text-gray-400 text-sm mb-1">Avg Confirmation Time</p>
                <p className="text-2xl font-bold text-green-400">2.3 min</p>
              </div>
            </div>
          </div>

          {/* Wallet Addresses */}
          <div className="crypto-card">
            <h3 className="text-lg font-semibold text-white mb-4">Receiving Wallets</h3>
            <div className="space-y-3">
              <WalletRow currency="ETH" address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb" />
              <WalletRow currency="BTC" address="bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh" />
              <WalletRow currency="USDC" address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb" />
            </div>
          </div>
        </div>
      )}

      {/* REPORTS TAB */}
      {activeTab === 'reports' && (
        <div className="space-y-6">
          <div className="flex gap-4">
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="bg-crypto-card border border-crypto-border rounded-lg px-3 py-2 text-white"
            >
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
              <option value="1y">Last Year</option>
            </select>
            <button className="btn-secondary flex items-center gap-2">
              <Download className="w-4 h-4" />
              Export CSV
            </button>
            <button className="btn-secondary flex items-center gap-2">
              <Download className="w-4 h-4" />
              Export PDF
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="crypto-card">
              <h3 className="text-lg font-semibold text-white mb-4">Monthly Revenue</h3>
              <div className="space-y-2">
                {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'].map((month) => (
                  <div key={month} className="flex items-center gap-3">
                    <span className="text-gray-400 w-8">{month}</span>
                    <div className="flex-1 h-6 bg-crypto-dark rounded overflow-hidden">
                      <div
                        className="h-full bg-neon-green/50 rounded"
                        style={{ width: `${Math.random() * 80 + 20}%` }}
                      />
                    </div>
                    <span className="text-white text-sm">{(Math.random() * 5 + 1).toFixed(2)} ETH</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="crypto-card">
              <h3 className="text-lg font-semibold text-white mb-4">Key Metrics</h3>
              <div className="space-y-4">
                <MetricRow label="Customer Acquisition Cost" value="0.02 ETH" change="-5%" />
                <MetricRow label="Lifetime Value" value="0.15 ETH" change="+12%" />
                <MetricRow label="Churn Rate" value="3.2%" change="-0.5%" />
                <MetricRow label="Net Revenue Retention" value="118%" change="+8%" />
                <MetricRow label="Free-to-Paid Conversion" value={`${conversionRate}%`} change="+2.3%" />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function RevenueCard({ title, value, change, up, icon: Icon, color }: any) {
  const colors: any = {
    orange: 'text-orange-400 bg-orange-500/20',
    blue: 'text-blue-400 bg-blue-500/20',
    purple: 'text-purple-400 bg-purple-500/20',
    cyan: 'text-cyan-400 bg-cyan-500/20',
  };

  return (
    <div className="crypto-card p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-gray-400 text-sm">{title}</span>
        <div className={`p-2 rounded ${colors[color]}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
      <div className={`flex items-center gap-1 text-sm ${up ? 'text-green-400' : 'text-red-400'}`}>
        {up ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
        {change}
      </div>
    </div>
  );
}

function RevenueStreamRow({ name, amount, percentage, color, icon: Icon }: any) {
  const colors: any = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    purple: 'bg-purple-500',
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon className="w-4 h-4 text-gray-400" />
          <span className="text-gray-300">{name}</span>
        </div>
        <span className="text-white font-medium">{amount}</span>
      </div>
      <div className="h-2 bg-crypto-dark rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${colors[color]}`} style={{ width: `${percentage}%` }} />
      </div>
    </div>
  );
}

function TierConfigRow({ tier, price, features, subscribers }: any) {
  const colors: any = {
    BASIC: 'border-green-500/30',
    PRO: 'border-blue-500/30',
    ELITE: 'border-yellow-500/30',
    ENTERPRISE: 'border-purple-500/30',
  };

  return (
    <div className={`p-4 bg-crypto-dark rounded-lg border ${colors[tier] || 'border-crypto-border'}`}>
      <div className="flex items-center justify-between mb-3">
        <div>
          <h4 className="text-white font-semibold">{tier}</h4>
          <p className="text-neon-green font-medium">{price}</p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-white">{subscribers}</p>
          <p className="text-xs text-gray-500">subscribers</p>
        </div>
      </div>
      <div className="flex flex-wrap gap-2">
        {features.map((f: string) => (
          <span key={f} className="text-xs px-2 py-1 bg-crypto-card rounded text-gray-400">{f}</span>
        ))}
      </div>
    </div>
  );
}

function WalletRow({ currency, address }: any) {
  return (
    <div className="flex items-center justify-between p-3 bg-crypto-dark rounded">
      <div className="flex items-center gap-3">
        <span className="text-gray-400 font-medium w-16">{currency}</span>
        <code className="text-neon-green text-sm">{address}</code>
      </div>
      <button className="btn-secondary text-xs py-1">Copy</button>
    </div>
  );
}

function MetricRow({ label, value, change }: any) {
  const isPositive = change.startsWith('+');
  return (
    <div className="flex items-center justify-between p-3 bg-crypto-dark rounded">
      <span className="text-gray-400">{label}</span>
      <div className="flex items-center gap-3">
        <span className="text-white font-medium">{value}</span>
        <span className={`text-sm ${isPositive ? 'text-green-400' : 'text-red-400'}`}>{change}</span>
      </div>
    </div>
  );
}
