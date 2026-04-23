import React, { useState } from 'react';
import {
  Eye,
  Database,
  TrendingUp,
  TrendingDown,
  Flame,
  Coins,
  Droplets,
  PieChart,
  BarChart3,
  ArrowRightLeft,
  Clock,
  CheckCircle,
  AlertTriangle,
  Lock,
  Globe,
  Users,
  Wallet,
  FileText,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  ExternalLink
} from 'lucide-react';

interface TokenMetric {
  label: string;
  value: string;
  change: string;
  positive: boolean;
  icon: React.ReactNode;
}

interface Transaction {
  id: string;
  type: 'buyback' | 'burn' | 'tax_to_lp' | 'revenue' | 'expense';
  amount: string;
  usdValue: string;
  timestamp: string;
  txHash: string;
  description: string;
  verified: boolean;
}

const TransparencyDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'supply' | 'transactions' | 'governance'>('overview');
  const [expandedTx, setExpandedTx] = useState<string | null>(null);
  const [timeframe, setTimeframe] = useState<'24h' | '7d' | '30d' | 'all'>('7d');

  const metrics: TokenMetric[] = [
    { label: 'Total Supply', value: '100,000,000 CRM', change: 'Fixed', positive: true, icon: <Database className="w-5 h-5" /> },
    { label: 'Circulating Supply', value: '65,420,000 CRM', change: '+2.3% this month', positive: true, icon: <Coins className="w-5 h-5" /> },
    { label: 'Tokens Burned', value: '12,580,000 CRM', change: '+450,000 this week', positive: true, icon: <Flame className="w-5 h-5 text-orange-400" /> },
    { label: 'Treasury Holdings', value: '22,000,000 CRM', change: '22% of supply', positive: true, icon: <Lock className="w-5 h-5" /> },
    { label: 'Liquidity Pool', value: '$2,450,000', change: '+$125,000 this month', positive: true, icon: <Droplets className="w-5 h-5 text-blue-400" /> },
    { label: 'Market Cap', value: '$8,200,000', change: '+15.4% (7d)', positive: true, icon: <BarChart3 className="w-5 h-5" /> },
  ];

  const transactions: Transaction[] = [
    {
      id: 'tx1',
      type: 'burn',
      amount: '250,000 CRM',
      usdValue: '$75,000',
      timestamp: '2026-04-14 08:30:00 UTC',
      txHash: '0x742d...8f3a',
      description: 'Scheduled weekly token burn from revenue',
      verified: true
    },
    {
      id: 'tx2',
      type: 'buyback',
      amount: '180,000 CRM',
      usdValue: '$54,000',
      timestamp: '2026-04-13 14:22:00 UTC',
      txHash: '0x91ab...2e4c',
      description: 'Market buyback from Q1 profits',
      verified: true
    },
    {
      id: 'tx3',
      type: 'tax_to_lp',
      amount: '85,000 CRM',
      usdValue: '$25,500',
      timestamp: '2026-04-13 00:00:00 UTC',
      txHash: '0x3f9c...7b1d',
      description: '1% transaction tax → Liquidity Pool',
      verified: true
    },
    {
      id: 'tx4',
      type: 'revenue',
      amount: '420 ETH',
      usdValue: '$1,260,000',
      timestamp: '2026-04-12 23:45:00 UTC',
      txHash: '0x8a2e...9f5b',
      description: 'Monthly subscription revenue collected',
      verified: true
    },
    {
      id: 'tx5',
      type: 'expense',
      amount: '15 ETH',
      usdValue: '$45,000',
      timestamp: '2026-04-12 16:00:00 UTC',
      txHash: '0x7d3f...1a2b',
      description: 'Server infrastructure payment',
      verified: true
    }
  ];

  const getTxIcon = (type: string) => {
    switch (type) {
      case 'burn': return <Flame className="w-5 h-5 text-orange-400" />;
      case 'buyback': return <TrendingUp className="w-5 h-5 text-green-400" />;
      case 'tax_to_lp': return <Droplets className="w-5 h-5 text-blue-400" />;
      case 'revenue': return <Coins className="w-5 h-5 text-[#7c3aed]" />;
      case 'expense': return <TrendingDown className="w-5 h-5 text-red-400" />;
      default: return <ArrowRightLeft className="w-5 h-5 text-gray-400" />;
    }
  };

  const getTxColor = (type: string) => {
    switch (type) {
      case 'burn': return 'bg-orange-500/10 border-orange-500/30 text-orange-400';
      case 'buyback': return 'bg-green-500/10 border-green-500/30 text-green-400';
      case 'tax_to_lp': return 'bg-blue-500/10 border-blue-500/30 text-blue-400';
      case 'revenue': return 'bg-[#7c3aed]/10 border-[#7c3aed]/30 text-[#7c3aed]';
      case 'expense': return 'bg-red-500/10 border-red-500/30 text-red-400';
      default: return 'bg-gray-800 border-gray-700';
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0812] text-gray-100 font-mono selection:bg-[#7c3aed]/30">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#0f0c1d] via-[#1a1525] to-[#0f0c1d] border-b border-[#7c3aed]/30">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Eye className="w-8 h-8 text-[#7c3aed]" />
              <div>
                <h1 className="text-xl font-bold tracking-wider">
                  TRANSPARENCY <span className="text-[#7c3aed]">PORTAL</span>
                </h1>
                <p className="text-xs text-gray-500 tracking-[0.2em]">REAL-TIME TREASURY & TOKEN METRICS</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 border border-green-500/30 rounded">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span className="text-xs text-green-400">On-Chain Verified</span>
              </div>
              <div className="text-right">
                <div className="text-xs text-gray-500">Last Update</div>
                <div className="text-sm">{new Date().toLocaleTimeString()}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-[1600px] mx-auto p-6 space-y-6">
        {/* Key Metrics */}
        <div className="grid grid-cols-3 gap-4">
          {metrics.map((metric, idx) => (
            <div key={idx} className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="p-2 bg-[#7c3aed]/10 rounded-lg text-[#7c3aed]">
                  {metric.icon}
                </div>
                <span className={`text-xs ${metric.positive ? 'text-green-400' : 'text-gray-400'}`}>
                  {metric.change}
                </span>
              </div>
              <div className="text-2xl font-bold">{metric.value}</div>
              <div className="text-xs text-gray-500 mt-1">{metric.label}</div>
            </div>
          ))}
        </div>

        {/* Navigation */}
        <div className="flex items-center gap-1 border-b border-gray-800">
          {[
            { id: 'overview', label: 'OVERVIEW', icon: <PieChart className="w-4 h-4" /> },
            { id: 'supply', label: 'SUPPLY FLOW', icon: <Database className="w-4 h-4" /> },
            { id: 'transactions', label: 'TRANSACTIONS', icon: <ArrowRightLeft className="w-4 h-4" /> },
            { id: 'governance', label: 'GOVERNANCE', icon: <Users className="w-4 h-4" /> },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold tracking-wider transition-all border-b-2 ${
                activeTab === tab.id
                  ? 'text-[#7c3aed] border-[#7c3aed]'
                  : 'text-gray-500 border-transparent hover:text-gray-300'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="space-y-6">
          {activeTab === 'overview' && (
            <>
              {/* Revenue Allocation */}
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                <h2 className="text-lg font-bold mb-6 flex items-center gap-2">
                  <PieChart className="w-5 h-5 text-[#7c3aed]" />
                  Revenue Allocation
                </h2>
                <div className="grid grid-cols-5 gap-4">
                  {[
                    { label: 'Treasury', percentage: 50, amount: '$62,500/mo', color: 'bg-[#7c3aed]' },
                    { label: 'Staking Rewards', percentage: 30, amount: '$37,500/mo', color: 'bg-green-500' },
                    { label: 'Development', percentage: 15, amount: '$18,750/mo', color: 'bg-blue-500' },
                    { label: 'Legal/Compliance', percentage: 3, amount: '$3,750/mo', color: 'bg-yellow-500' },
                    { label: 'Buyback & Burn', percentage: 2, amount: '$2,500/mo', color: 'bg-orange-500' },
                  ].map((item) => (
                    <div key={item.label} className="text-center">
                      <div className="text-3xl font-bold mb-1">{item.percentage}%</div>
                      <div className="h-2 bg-gray-800 rounded-full overflow-hidden mb-2">
                        <div className={`h-full ${item.color} rounded-full`} style={{ width: `${item.percentage}%` }} />
                      </div>
                      <div className="text-sm font-semibold">{item.label}</div>
                      <div className="text-xs text-gray-500">{item.amount}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Monthly Stats */}
              <div className="grid grid-cols-2 gap-6">
                <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                  <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">Buyback & Burn (30 Days)</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Tokens Burned</span>
                      <span className="text-xl font-bold text-orange-400">1,250,000 CRM</span>
                    </div>
                    <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                      <div className="h-full bg-orange-500 rounded-full" style={{ width: '45%' }} />
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Buyback Spend</span>
                      <span className="text-xl font-bold text-green-400">$375,000</span>
                    </div>
                    <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                      <div className="h-full bg-green-500 rounded-full" style={{ width: '75%' }} />
                    </div>
                    <div className="p-3 bg-orange-500/10 border border-orange-500/30 rounded-lg">
                      <div className="text-sm text-orange-400">
                        <Flame className="w-4 h-4 inline mr-2" />
                        1.25% of total supply burned this month
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                  <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">Transaction Tax (1%)</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Tax Collected (30d)</span>
                      <span className="text-xl font-bold text-blue-400">340,000 CRM</span>
                    </div>
                    <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                      <div className="h-full bg-blue-500 rounded-full" style={{ width: '60%' }} />
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Added to LP</span>
                      <span className="text-xl font-bold text-[#7c3aed]">$102,000</span>
                    </div>
                    <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                      <div className="h-full bg-[#7c3aed] rounded-full" style={{ width: '80%' }} />
                    </div>
                    <div className="p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                      <div className="text-sm text-blue-400">
                        <Droplets className="w-4 h-4 inline mr-2" />
                        Liquidity pool depth increased 12% this month
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}

          {activeTab === 'supply' && (
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <h2 className="text-lg font-bold mb-6">Supply Flow Visualization</h2>
              <div className="h-96 bg-[#0a0812] rounded-lg border border-gray-800 flex items-center justify-center">
                <div className="text-center text-gray-500">
                  <Database className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p className="text-lg mb-2">Token Flow Diagram</p>
                  <p className="text-sm">Interactive supply flow chart showing:</p>
                  <ul className="text-sm mt-2 space-y-1">
                    <li>• Initial mint → Treasury allocation</li>
                    <li>• Circulating supply movement</li>
                    <li>→ Buyback → Burn mechanism</li>
                    <li>→ Tax collection → LP injection</li>
                    <li>→ Staking rewards distribution</li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'transactions' && (
            <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-bold">Recent Treasury Transactions</h2>
                <div className="flex items-center gap-2">
                  {['24h', '7d', '30d', 'all'].map((tf) => (
                    <button
                      key={tf}
                      onClick={() => setTimeframe(tf as any)}
                      className={`px-3 py-1 rounded text-xs ${
                        timeframe === tf
                          ? 'bg-[#7c3aed] text-white'
                          : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                      }`}
                    >
                      {tf.toUpperCase()}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-3">
                {transactions.map((tx) => (
                  <div
                    key={tx.id}
                    className="bg-[#0a0812] rounded-lg border border-gray-800 overflow-hidden"
                  >
                    <div
                      className="p-4 cursor-pointer"
                      onClick={() => setExpandedTx(expandedTx === tx.id ? null : tx.id)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className={`p-2 rounded-lg ${getTxColor(tx.type)}`}>
                            {getTxIcon(tx.type)}
                          </div>
                          <div>
                            <div className="font-semibold flex items-center gap-2">
                              {tx.type.replace('_', ' ').toUpperCase()}
                              {tx.verified && <CheckCircle className="w-4 h-4 text-green-400" />}
                            </div>
                            <div className="text-xs text-gray-500">{tx.description}</div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-semibold">{tx.amount}</div>
                          <div className="text-xs text-gray-500">{tx.usdValue}</div>
                        </div>
                      </div>
                    </div>

                    {expandedTx === tx.id && (
                      <div className="px-4 pb-4 border-t border-gray-800 pt-3">
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="text-gray-500">Transaction Hash:</span>
                            <div className="font-mono text-[#7c3aed]">{tx.txHash}</div>
                          </div>
                          <div>
                            <span className="text-gray-500">Timestamp:</span>
                            <div>{tx.timestamp}</div>
                          </div>
                          <div>
                            <span className="text-gray-500">Status:</span>
                            <div className="flex items-center gap-1 text-green-400">
                              <CheckCircle className="w-4 h-4" />
                              Verified on-chain
                            </div>
                          </div>
                          <div>
                            <span className="text-gray-500">View on Explorer:</span>
                            <div>
                              <a href="#" className="text-[#7c3aed] hover:underline flex items-center gap-1">
                                Etherscan <ExternalLink className="w-3 h-3" />
                              </a>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'governance' && (
            <div className="grid grid-cols-2 gap-6">
              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <Users className="w-5 h-5 text-[#7c3aed]" />
                  DAO Proposals
                </h3>
                <div className="space-y-3">
                  {[
                    { title: 'Increase buyback allocation to 5%', status: 'active', votes: '67% FOR', time: '2 days left' },
                    { title: 'Add Base chain liquidity pair', status: 'passed', votes: '82% FOR', time: 'Executed 3d ago' },
                    { title: 'Reduce staking lock period', status: 'rejected', votes: '34% FOR', time: 'Closed 1w ago' },
                  ].map((proposal, idx) => (
                    <div key={idx} className="p-3 bg-[#0a0812] rounded-lg border border-gray-800">
                      <div className="font-semibold text-sm">{proposal.title}</div>
                      <div className="flex items-center justify-between mt-2 text-xs">
                        <span className={`px-2 py-0.5 rounded ${
                          proposal.status === 'active' ? 'bg-yellow-500/20 text-yellow-400' :
                          proposal.status === 'passed' ? 'bg-green-500/20 text-green-400' :
                          'bg-red-500/20 text-red-400'
                        }`}>
                          {proposal.status.toUpperCase()}
                        </span>
                        <span className="text-gray-500">{proposal.votes} • {proposal.time}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <Wallet className="w-5 h-5 text-green-400" />
                  Staking Rewards
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Current APY</span>
                    <span className="text-3xl font-bold text-green-400">18.5%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Total Staked</span>
                    <span className="text-xl font-bold">28,450,000 CRM</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Staking Participants</span>
                    <span className="text-xl font-bold">4,230</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Rewards Distributed (30d)</span>
                    <span className="text-xl font-bold text-[#7c3aed]">$37,500</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Audit & Verification Footer */}
        <div className="bg-gradient-to-br from-[#1a1525] to-[#0f0c1d] border border-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-[#7c3aed]" />
                <span className="text-sm">Audited by CertiK</span>
              </div>
              <div className="flex items-center gap-2">
                <Lock className="w-5 h-5 text-green-400" />
                <span className="text-sm">Multi-sig Treasury (3/5)</span>
              </div>
              <div className="flex items-center gap-2">
                <Globe className="w-5 h-5 text-blue-400" />
                <span className="text-sm">Real-time on-chain data</span>
              </div>
            </div>
            <button className="flex items-center gap-2 px-4 py-2 bg-[#7c3aed]/10 border border-[#7c3aed]/30 rounded-lg text-[#7c3aed] hover:bg-[#7c3aed]/20 transition-all">
              <ExternalLink className="w-4 h-4" />
              View Full Audit
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TransparencyDashboard;
