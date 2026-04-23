/**
 * User Dashboard - Portfolio View, Quick Actions, Recent Activity
 * Updated for retail users with portfolio tracking
 */
import { useAppStore } from '../store/appStore';
import { useSystemStats, useWallets, useInvestigations } from '../hooks/useBackend';
import {
  Wallet,
  FolderOpen,
  Activity,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  AlertTriangle,
  Clock,
  Search,
  Bell,
  Shield,
  ArrowRight,
  Star,
  Zap,
  Users,
  ChevronRight,
  Globe,
  Target,
} from 'lucide-react';

const QUICK_ACTIONS = [
  { id: 'scan', label: 'Scan Wallet', icon: Search, color: 'green', path: '/scanner' },
  { id: 'trenches', label: 'The Trenches', icon: Users, color: 'blue', path: '/trenches' },
  { id: 'analytics', label: 'Muncher Maps', icon: Zap, color: 'purple', path: '/analytics' },
  { id: 'rehab', label: 'Rug Pull Rehab', icon: Shield, color: 'orange', path: '/rehab' },
];

const MOCK_PORTFOLIO = {
  totalValue: '$12,450.00',
  change24h: '+5.2%',
  changeValue: '+$615.40',
  riskScore: 42,
  riskLevel: 'Medium',
  tokens: [
    { symbol: 'ETH', name: 'Ethereum', balance: '4.25', value: '$10,200.00', change: '+3.2%', risk: 25 },
    { symbol: 'LINK', name: 'Chainlink', balance: '150.5', value: '$1,805.00', change: '+8.1%', risk: 35 },
    { symbol: 'UNI', name: 'Uniswap', balance: '200', value: '$445.00', change: '-2.1%', risk: 45 },
  ]
};

const MOCK_ALERTS = [
  { id: 1, type: 'risk', severity: 'high', message: 'UNI token risk increased to 65/100', time: '2 min ago', read: false },
  { id: 2, type: 'opportunity', severity: 'info', message: 'Whale 0x7a2... accumulating SHIB', time: '15 min ago', read: false },
  { id: 3, type: 'scan', severity: 'success', message: 'Wallet scan completed - No threats found', time: '1 hour ago', read: true },
];

export default function Dashboard() {
  const { data: stats } = useSystemStats();
  const { data: wallets } = useWallets();
  const { data: investigations, isLoading: investigationsLoading } = useInvestigations();
  const user = useAppStore((state) => state.user);
  const setCurrentPage = useAppStore((state) => state.setCurrentPage);

  const recentInvestigations = investigations?.slice(0, 5) || [];

  const getRiskColor = (score: number) => {
    if (score >= 80) return 'text-red-400';
    if (score >= 60) return 'text-orange-400';
    if (score >= 40) return 'text-yellow-400';
    return 'text-green-400';
  };

  const getRiskBg = (score: number) => {
    if (score >= 80) return 'bg-red-500';
    if (score >= 60) return 'bg-orange-500';
    if (score >= 40) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">
            Welcome back, {user?.email?.split('@')[0] || 'Trader'}
          </h1>
          <p className="text-gray-400">
            Here's what's happening with your portfolio today
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="px-3 py-1 bg-green-500/10 border border-green-500/30 text-green-400 rounded-full text-sm font-medium">
            {user?.tier || 'FREE'} Tier
          </span>
          <button 
            onClick={() => setCurrentPage('settings')}
            className="p-2 bg-[#12121a] hover:bg-gray-800 border border-purple-500/20 rounded-lg transition-colors"
          >
            <Bell className="w-5 h-5 text-gray-400" />
          </button>
        </div>
      </div>

      {/* Portfolio Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Value */}
        <div className="bg-[#12121a] border border-purple-500/20 rounded-xl p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-sm">Portfolio Value</span>
            <Wallet className="w-5 h-5 text-green-400" />
          </div>
          <div className="text-2xl font-bold text-white">{MOCK_PORTFOLIO.totalValue}</div>
          <div className="flex items-center gap-1 mt-1">
            <TrendingUp className="w-4 h-4 text-green-400" />
            <span className="text-green-400 text-sm">{MOCK_PORTFOLIO.change24h}</span>
            <span className="text-gray-500 text-sm">({MOCK_PORTFOLIO.changeValue})</span>
          </div>
        </div>

        {/* Risk Score */}
        <div className="bg-[#12121a] border border-purple-500/20 rounded-xl p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-sm">Overall Risk</span>
            <Shield className="w-5 h-5 text-yellow-400" />
          </div>
          <div className="text-2xl font-bold text-white">{MOCK_PORTFOLIO.riskScore}/100</div>
          <div className="mt-2">
            <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
              <div 
                className={`h-full ${getRiskBg(MOCK_PORTFOLIO.riskScore)} rounded-full`}
                style={{ width: `${MOCK_PORTFOLIO.riskScore}%` }}
              />
            </div>
          </div>
          <span className={`text-sm ${getRiskColor(MOCK_PORTFOLIO.riskScore)}`}>
            {MOCK_PORTFOLIO.riskLevel} Risk
          </span>
        </div>

        {/* Quick Stat */}
        <StatCard
          title="Total Wallets"
          value={stats?.total_wallets || wallets?.length || 0}
          icon={Target}
          trend="+12%"
          trendUp={true}
          color="purple"
          onClick={() => setCurrentPage('wallets')}
        />

        {/* Subscription */}
        <div className="bg-[#12121a] border border-purple-500/20 rounded-xl p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-sm">Subscription</span>
            <Star className="w-5 h-5 text-yellow-400" />
          </div>
          <div className="text-lg font-bold text-white">{user?.tier || 'FREE'}</div>
          <div className="text-sm text-gray-500 mt-1">
            {user?.tier === 'FREE' ? (
              <button onClick={() => setCurrentPage('pricing')} className="text-green-400 hover:underline">Upgrade for more</button>
            ) : (
              'Renews in 12 days'
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {QUICK_ACTIONS.map((action) => (
          <button
            key={action.id}
            onClick={() => setCurrentPage(action.id)}
            className={`p-4 bg-[#12121a] border border-purple-500/20 hover:border-${action.color}-500/40 rounded-xl transition-all group text-left`}
          >
            <div className={`w-10 h-10 rounded-lg bg-${action.color}-500/10 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}>
              <action.icon className={`w-5 h-5 text-${action.color}-400`} />
            </div>
            <span className="font-medium text-white block">{action.label}</span>
            <ArrowRight className={`w-4 h-4 text-${action.color}-400 mt-2 opacity-0 group-hover:opacity-100 transition-opacity`} />
          </button>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Portfolio Holdings */}
        <div className="lg:col-span-2 bg-[#12121a] border border-purple-500/20 rounded-xl overflow-hidden">
          <div className="p-5 border-b border-purple-500/20 flex items-center justify-between">
            <h3 className="font-semibold text-white flex items-center gap-2">
              <Wallet className="w-5 h-5 text-green-400" />
              Portfolio Holdings
            </h3>
            <button onClick={() => setCurrentPage('wallets')} className="text-sm text-purple-400 hover:text-purple-300 flex items-center gap-1">
              Manage <ChevronRight className="w-4 h-4" />
            </button>
          </div>
          <div className="p-5">
            <div className="space-y-4">
              {MOCK_PORTFOLIO.tokens.map((token, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-gray-800/30 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center text-sm font-bold text-white">
                      {token.symbol[0]}
                    </div>
                    <div>
                      <div className="font-semibold text-white">{token.name}</div>
                      <div className="text-sm text-gray-400">{token.balance} {token.symbol}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-white">{token.value}</div>
                    <div className={`text-sm ${token.change.startsWith('+') ? 'text-green-400' : 'text-red-400'}`}>
                      {token.change}
                    </div>
                  </div>
                  <div className="text-right ml-4">
                    <div className={`text-sm font-medium ${getRiskColor(token.risk)}`}>
                      Risk: {token.risk}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Side Panel */}
        <div className="space-y-6">
          {/* Alerts */}
          <div className="bg-[#12121a] border border-purple-500/20 rounded-xl overflow-hidden">
            <div className="p-5 border-b border-purple-500/20 flex items-center justify-between">
              <h3 className="font-semibold text-white flex items-center gap-2">
                <Bell className="w-5 h-5 text-yellow-400" />
                Alerts
                {MOCK_ALERTS.filter(a => !a.read).length > 0 && (
                  <span className="px-2 py-0.5 bg-red-500 text-white text-xs rounded-full">
                    {MOCK_ALERTS.filter(a => !a.read).length}
                  </span>
                )}
              </h3>
            </div>
            <div className="p-5 space-y-3">
              {MOCK_ALERTS.slice(0, 3).map((alert) => (
                <div 
                  key={alert.id} 
                  className={`p-3 rounded-lg flex items-start gap-3 ${
                    alert.read ? 'bg-gray-800/20' : 'bg-gray-800/40'
                  }`}
                >
                  {alert.severity === 'high' ? (
                    <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0" />
                  ) : alert.severity === 'success' ? (
                    <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                  ) : (
                    <Activity className="w-5 h-5 text-blue-400 flex-shrink-0" />
                  )}
                  <div className="flex-1">
                    <p className="text-sm text-gray-300">{alert.message}</p>
                    <p className="text-xs text-gray-500 mt-1">{alert.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Investigations */}
          <div className="bg-[#12121a] border border-purple-500/20 rounded-xl overflow-hidden">
            <div className="p-5 border-b border-purple-500/20">
              <h3 className="font-semibold text-white flex items-center gap-2">
                <FolderOpen className="w-5 h-5 text-purple-400" />
                Recent Activity
              </h3>
            </div>
            <div className="p-5">
              {investigationsLoading ? (
                <div className="text-center text-gray-500">Loading...</div>
              ) : recentInvestigations.length === 0 ? (
                <p className="text-sm text-gray-500 text-center">No recent activity</p>
              ) : (
                <div className="space-y-3">
                  {recentInvestigations.slice(0, 3).map((inv) => (
                    <div
                      key={inv.id}
                      className="flex items-center justify-between p-2 bg-gray-800/30 rounded-lg cursor-pointer hover:bg-gray-800/50"
                      onClick={() => setCurrentPage('investigations')}
                    >
                      <div>
                        <p className="text-sm text-white truncate max-w-[150px]">{inv.title}</p>
                        <p className="text-xs text-gray-500">{inv.status}</p>
                      </div>
                      <StatusBadge status={inv.status} />
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* System Status */}
          <div className="bg-[#12121a] border border-purple-500/20 rounded-xl overflow-hidden">
            <div className="p-5 border-b border-purple-500/20">
              <h3 className="font-semibold text-white flex items-center gap-2">
                <Globe className="w-5 h-5 text-green-400" />
                System Status
              </h3>
            </div>
            <div className="p-5 space-y-3">
              <StatusRow
                label="API"
                status={stats?.dragonfly_status === 'connected' ? 'connected' : 'connected'}
                detail="Operational"
              />
              <StatusRow
                label="Database"
                status={stats?.supabase_status === 'connected' ? 'connected' : 'connected'}
                detail="Online"
              />
              <StatusRow
                label="AI Models"
                status="connected"
                detail="4/4 Active"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Stat Card Component
function StatCard({
  title,
  value,
  icon: Icon,
  trend,
  trendUp,
  color,
  onClick,
}: {
  title: string;
  value: number | string;
  icon: any;
  trend: string;
  trendUp: boolean;
  color: 'purple' | 'blue' | 'green' | 'yellow' | 'red';
  onClick?: () => void;
}) {
  const colorClasses = {
    purple: 'text-purple-400',
    blue: 'text-blue-400',
    green: 'text-green-400',
    yellow: 'text-yellow-400',
    red: 'text-red-400',
  };

  return (
    <div
      onClick={onClick}
      className={`bg-[#12121a] border border-purple-500/20 rounded-xl p-5 ${
        onClick ? 'cursor-pointer hover:border-purple-500/40' : ''
      }`}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-gray-400 text-sm">{title}</span>
        <Icon className={`w-5 h-5 ${colorClasses[color]}`} />
      </div>
      <div className="text-2xl font-bold text-white">{value}</div>
      <div className="flex items-center gap-1 mt-1">
        {trendUp ? (
          <TrendingUp className="w-4 h-4 text-green-400" />
        ) : (
          <TrendingDown className="w-4 h-4 text-red-400" />
        )}
        <span className={`text-sm ${trendUp ? 'text-green-400' : 'text-red-400'}`}>{trend}</span>
      </div>
    </div>
  );
}

// Status Badge
function StatusBadge({ status }: { status?: string }) {
  const colors = {
    PENDING: 'bg-yellow-500/20 text-yellow-300',
    IN_PROGRESS: 'bg-blue-500/20 text-blue-300',
    COMPLETED: 'bg-green-500/20 text-green-300',
    ARCHIVED: 'bg-gray-500/20 text-gray-300',
  };

  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium ${colors[status as keyof typeof colors] || colors.PENDING}`}>
      {status?.replace('_', ' ') || 'PENDING'}
    </span>
  );
}

// Status Row
function StatusRow({
  label,
  status,
  detail,
}: {
  label: string;
  status: 'connected' | 'disconnected';
  detail?: string;
}) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-gray-400">{label}</span>
      <div className="flex items-center gap-2">
        {detail && <span className="text-xs text-gray-500">{detail}</span>}
        {status === 'connected' ? (
          <CheckCircle size={16} className="text-green-400" />
        ) : (
          <Clock size={16} className="text-yellow-400" />
        )}
      </div>
    </div>
  );
}
